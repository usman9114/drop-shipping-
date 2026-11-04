"""Accuracy check for the business-model rules (R1 exit criterion).

Draws a stratified sample of profiled stores, asks a free model for an
independent label from the same evidence plus the public domain name, and
compares it with `scout.stores.business_model`. Writes the comparison to
data/private/validation/ (names stores, so private) and prints agreement.
Disagreements are then hand-checked by the owner/advisor; fixes go into the
rules with a test.

Free models only (scout.llm skips paid routes unless SCOUT_ALLOW_PAID=1).

    python scripts/validate_business_model.py --n 30
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from pathlib import Path as _P
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(_P(__file__).resolve().parent.parent))

from scout import stores  # noqa: E402
from scout.llm import chat_many  # noqa: E402

LABELS = ["brand", "general", "retailer", "reseller", "dropship", "pod"]
FIELDS = [
    "domain",
    "products_sampled",
    "vendors",
    "top_vendor_share",
    "own_vendor_share",
    "ae_image_share",
    "dropship_sku_share",
    "dropship_vendor_share",
    "pod_share",
    "top_category",
    "top_types",
    "price_median",
    "traffic_tags",
]
PROMPT = """Classify one online store's business model from this evidence.
Labels:
- brand: sells goods it makes or commissions under its own name (own-label, one or two vendors)
- general: one store name over many unrelated categories with permanent discounts (typical dropshipper shape)
- retailer: a large multi-brand retailer, publisher or house-brand portfolio (10+ labels)
- reseller: a smaller shop reselling 5 to 9 other brands' goods
- dropship: imports marketplace/supplier goods under generic or rotating vendor names (AliExpress-style images, supplier SKUs)
- pod: print on demand
Evidence (JSON):
{ev}

Reply with exactly one line: LABEL | short reason. LABEL is one of brand, general, retailer, reseller, dropship, pod."""


SEEN = Path("data/private/validation/seen.txt")


def seen() -> set[str]:
    return set(SEEN.read_text().split()) if SEEN.exists() else set()


def sample(rows: list[dict], n: int, seed: int = 7) -> list[dict]:
    """Spread across the rule labels; rare labels (dropship, pod) are taken whole."""
    rng = random.Random(seed)
    by = defaultdict(list)
    for r in rows:
        by[r.get("business_model")].append(r)
    out = []
    for lab, k in (("dropship", 6), ("pod", 3), ("unclear", 6)):
        pool = by.get(lab, [])
        out += rng.sample(pool, min(k, len(pool)))
    for lab in ("brand", "reseller"):
        pool = by.get(lab, [])
        out += rng.sample(
            pool, min((n - len(out)) // (2 if lab == "brand" else 1), len(pool))
        )
    return out[:n]


def parse(text: str) -> tuple[str | None, str]:
    m = re.match(
        r"\s*\**\s*(brand|general|retailer|reseller|dropship|pod)\b[^|]*\|?\s*(.*)",
        text.strip(),
        re.I,
    )
    return (m.group(1).lower(), m.group(2).strip()) if m else (None, text.strip()[:120])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument(
        "--fresh", action="store_true", help="exclude stores validated before"
    )
    a = ap.parse_args()
    rows = {
        r["domain"]: r for r in stores._all_rows("web_store_deep") if not r.get("error")
    }
    rows = [r for r in rows.values() if r.get("products_sampled")]
    if a.fresh:  # only stores never used to tune the rules: an honest hold-out
        done = seen()
        rows = [r for r in rows if r["domain"] not in done]
    picks = sample(rows, a.n, a.seed)
    prompts = [
        PROMPT.format(ev=json.dumps({k: r.get(k) for k in FIELDS}, default=str))
        for r in picks
    ]
    # GLM Flash is free: 8 parallel calls is the tested sweet spot (16 hits HTTP errors)
    results = chat_many(prompts, workers=8, task="bulk", max_tokens=200)
    out, errors = [], 0
    for r, res in zip(picks, results, strict=True):
        if "text" in res:
            model_label, why = parse(res["text"])
            engine = res["model"]
        else:
            model_label, why, engine = None, res["error"], ""
            errors += 1
        rule = r.get("business_model")
        # unclear is a rule abstention, not a claim: it never counts as agreement
        out.append(
            {
                "domain": r["domain"],
                "rule": rule,
                "model": model_label,
                "agree": rule == model_label,
                "model_reason": why,
                "engine": engine,
                "rule_reason": "; ".join(r.get("business_model_why") or []),
            }
        )
    d = Path("data/private/validation")
    d.mkdir(parents=True, exist_ok=True)
    with SEEN.open("a", encoding="utf-8") as fh:
        fh.write("".join(o["domain"] + "\n" for o in out))
    dst = d / f"{date.today().isoformat()}-business-model.csv"
    with dst.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    decided = [o for o in out if o["model"] and o["rule"] != "unclear"]
    agree = sum(o["agree"] for o in decided)
    print(
        f"sample {len(out)}, model errors {errors}, unclear-by-rule {sum(o['rule']=='unclear' for o in out)}",
        file=sys.stderr,
    )
    if decided:
        print(
            f"agreement on decided stores: {agree}/{len(decided)} = {agree/len(decided):.0%}",
            file=sys.stderr,
        )
    print(
        "confusion (rule -> model):",
        dict(Counter((o["rule"], o["model"]) for o in out)),
        file=sys.stderr,
    )
    print(f"wrote {dst}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
