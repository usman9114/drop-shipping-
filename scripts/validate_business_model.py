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
from scout.llm import chat  # noqa: E402

LABELS = ["brand", "reseller", "dropship", "pod"]
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
- reseller: retails many other brands' goods
- dropship: imports marketplace/supplier goods under generic or rotating vendor names (AliExpress-style images, supplier SKUs)
- pod: print on demand
Evidence (JSON):
{ev}

Reply with exactly one line: LABEL | short reason. LABEL is one of brand, reseller, dropship, pod."""


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
        r"\s*\**\s*(brand|reseller|dropship|pod)\b[^|]*\|?\s*(.*)", text.strip(), re.I
    )
    return (m.group(1).lower(), m.group(2).strip()) if m else (None, text.strip()[:120])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()
    rows = {
        r["domain"]: r for r in stores._all_rows("web_store_deep") if not r.get("error")
    }
    rows = [r for r in rows.values() if r.get("products_sampled")]
    picks = sample(rows, a.n)
    out, errors = [], 0
    for i, r in enumerate(picks, 1):
        print(f"{i}/{len(picks)} {r['domain']}", file=sys.stderr, flush=True)
        ev = {k: r.get(k) for k in FIELDS}
        try:
            res = chat(
                PROMPT.format(ev=json.dumps(ev, default=str)),
                task="reasoning",
                max_tokens=400,
            )
            model_label, why = parse(res["text"])
            engine = res["model"]
        except Exception as exc:
            model_label, why, engine = None, type(exc).__name__, ""
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
