"""Intelligence layer: turn warehouse evidence into a "what sells and why" report.

Deterministic first. It reads only `mart.mart_type_evidence` (read-only) and
builds one evidence pack per product type. A free model then writes a short
narrative from that pack and nothing else. Three guards keep it honest:

1. **Cache.** Narratives are stored in `warehouse/seeds/llm_story_cache.csv`,
   keyed by the sha256 of the pack plus the prompt version. Same data, same
   report, no model call.
2. **Grounding check.** Every number in a narrative must appear in its pack.
   If one does not, the narrative is rejected and a fixed template is used.
3. **Labels.** The report marks each narrative as `cache`, `llm`, `template` or
   `template (model text rejected)`.

Usage:
    python -m scout.intel                     # top 15 types, model narratives
    python -m scout.intel --no-llm            # template only, fully offline
    python -m scout.intel --limit 40 --out docs/reports/x.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

DB = Path("data/private/warehouse.duckdb")
CACHE = Path("warehouse/seeds/llm_story_cache.csv")
PROMPT_VERSION = "story-v1"
FIELDS = ["pack_sha256", "product_type", "narrative", "model", "prompt_version"]
IMPULSE_PRICE = 25.0
MIN_VELOCITY_DAYS = 0.5

PACK_KEYS = [
    "product_type",
    "cj_products",
    "viable_products",
    "median_price_floor",
    "best_price_floor",
    "median_listed",
    "popular_products",
    "flagged_products",
    "median_units_per_day",
    "total_units_per_day",
    "velocity_span_days",
    "why_tags",
]

SYSTEM = (
    "You are a careful e-commerce analyst. You explain why a product type sells "
    "and what limits it, using only the evidence you are given."
)
PROMPT = """Evidence for one product type sold by a small US eBay dropshipper
(supplier: CJ Dropshipping US warehouse). Field meanings:
- viable_products: CJ products that pass our margin model at some eBay price
- median_price_floor / best_price_floor: lowest eBay price (USD) that still passes
- median_listed / popular_products: how many dropshipping stores list these items
  (popular = 500+); high means proven appeal AND crowded competition
- flagged_products: items needing compliance review
- units_per_day / velocity_span_days: CJ US stock falling over time (null = not measured yet)
- why_tags: rule-based reasons this kind of product sells
- impulse_price: true when the median price floor is $25 or less

Evidence (JSON):
{pack}

Write 3 to 5 plain sentences: why this type sells (use why_tags), what limits it
(price floor vs impulse buying, crowding, compliance flags), what is not yet
measured, and the single most useful next check. Use only numbers that appear in
the evidence. No product names, no invented facts, no lists, no markdown."""


def pack(row: dict) -> dict:
    """The evidence a narrative may cite, with derived flags."""
    p = {k: row.get(k) for k in PACK_KEYS}
    for k, v in p.items():
        if isinstance(v, float):
            p[k] = round(v, 2)
    floor = p.get("median_price_floor")
    p["impulse_price"] = floor is not None and floor <= IMPULSE_PRICE
    span = p.get("velocity_span_days")
    p["velocity_measured"] = span is not None and span >= MIN_VELOCITY_DAYS
    return p


def pack_hash(p: dict) -> str:
    blob = json.dumps(p, sort_keys=True, default=str) + PROMPT_VERSION
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


_NUM = re.compile(r"(?<![\w.])\$?(\d+(?:,\d{3})*(?:\.\d+)?)%?")


def _numbers(text: str) -> set[float]:
    return {float(m.replace(",", "")) for m in _NUM.findall(text)}


def grounded(text: str, p: dict) -> bool:
    """True when every number in `text` appears in the pack."""
    allowed = set()
    for v in p.values():
        if isinstance(v, bool) or v is None:
            continue
        if isinstance(v, (int, float)):
            allowed.add(round(float(v), 2))
        elif isinstance(v, str):
            allowed |= {round(x, 2) for x in _numbers(v)}
    allowed |= {float(IMPULSE_PRICE), 500.0, 90.0}  # thresholds named in the prompt
    return all(round(n, 2) in allowed for n in _numbers(text))


def template(p: dict) -> str:
    """Deterministic fallback narrative."""
    tags = (p.get("why_tags") or "untagged").replace("|", ", ").replace("_", " ")
    parts = [
        f"{p['product_type']}: {p['viable_products']} of {p['cj_products']} CJ US products "
        f"pass the margin model.",
        f"Reasons it sells (rules): {tags}.",
    ]
    if p.get("median_price_floor") is not None:
        kind = "an impulse price" if p["impulse_price"] else "above impulse range"
        parts.append(f"Median price floor ${p['median_price_floor']} ({kind}).")
    if p.get("median_listed") is not None:
        parts.append(
            f"Median {p['median_listed']} stores list these items; "
            f"{p['popular_products']} are listed by 500+ stores."
        )
    if p.get("flagged_products"):
        parts.append(f"{p['flagged_products']} need compliance review.")
    gaps = []
    if not p["velocity_measured"]:
        gaps.append("stock velocity")
    gaps.append("marketplace demand")
    if gaps:
        parts.append("Not measured yet: " + " and ".join(gaps) + ".")
    return " ".join(parts)


def load_cache(path: Path = CACHE) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["pack_sha256"]: r for r in csv.DictReader(fh)}


def append_cache(rows: list[dict], path: Path = CACHE) -> None:
    if not rows:
        return
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)


def narrate(p: dict, cache: dict, chat=None) -> tuple[str, str, dict | None]:
    """Return (text, method, new_cache_row_or_None)."""
    key = pack_hash(p)
    hit = cache.get(key)
    if hit:
        return hit["narrative"], "cache", None
    if chat is None:
        return template(p), "template", None
    try:
        out = chat(
            PROMPT.format(pack=json.dumps(p, sort_keys=True, default=str)),
            task="bulk",
            system=SYSTEM,
            max_tokens=600,
        )
    except Exception as exc:  # any provider failure falls back to the template
        print(f"  model failed for {p['product_type']}: {exc}"[:200], file=sys.stderr)
        return template(p), "template", None
    text = " ".join(out["text"].split())
    if not grounded(text, p):
        return template(p), "template (model text rejected)", None
    row = {
        "pack_sha256": key,
        "product_type": p["product_type"],
        "narrative": text,
        "model": out["model"],
        "prompt_version": PROMPT_VERSION,
    }
    return text, "llm", row


def _cell(v) -> str:
    return "–" if v is None else str(v)


def render(items: list[tuple[dict, str, str]], built: str) -> str:
    lines = [
        f"# What sells and why — {built}",
        "",
        "> Generated by `python -m scout.intel` from `mart.mart_type_evidence`. Numbers are "
        "[data] from the warehouse. Why-tags are rule-based judgments (`warehouse/seeds/rule_why.csv`). "
        "Narratives are model-written from the numbers only and checked: any number not in the "
        "evidence makes the pipeline fall back to a template. No CJ product text is included.",
        "",
        "| Product type | Viable / CJ | Median floor $ | Median stores listing | Popular | "
        "Flagged | Units/day | Why tags |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p, _, _ in items:
        lines.append(
            f"| {p['product_type']} | {p['viable_products']} / {p['cj_products']} | "
            f"{_cell(p['median_price_floor'])} | {_cell(p['median_listed'])} | "
            f"{_cell(p['popular_products'])} | {_cell(p['flagged_products'])} | "
            f"{_cell(p['median_units_per_day'])} | "
            f"{(p.get('why_tags') or '–').replace('|', ', ')} |"
        )
    lines.append("")
    for p, text, method in items:
        lines += [
            f"## {p['product_type']}",
            "",
            text,
            "",
            f"*Narrative: {method}.*",
            "",
        ]
    return "\n".join(lines)


def load_evidence(db: Path = DB) -> list[dict]:
    import duckdb

    con = duckdb.connect(str(db), read_only=True)
    try:
        cur = con.execute(
            "select * from mart.mart_type_evidence "
            "order by viable_products desc, cj_products desc, product_type"
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="What-sells-and-why report from the warehouse"
    )
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--limit", type=int, default=15, help="product types to cover")
    ap.add_argument("--no-llm", action="store_true", help="template narratives only")
    ap.add_argument(
        "--out", help="report path (default docs/reports/<date>-what-sells.md)"
    )
    a = ap.parse_args(argv)

    rows = [r for r in load_evidence(Path(a.db)) if (r.get("viable_products") or 0) > 0]
    packs = [pack(r) for r in rows[: a.limit]]
    chat = None
    if not a.no_llm:
        from scout.llm import chat as llm_chat

        chat = llm_chat
    cache = load_cache()
    items, new_rows = [], []
    for p in packs:
        text, method, row = narrate(p, cache, chat)
        items.append((p, text, method))
        if row:
            new_rows.append(row)
            cache[row["pack_sha256"]] = row
    append_cache(new_rows)
    today = date.today().isoformat()
    out = Path(a.out or f"docs/reports/{today}-what-sells.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(items, today) + "\n", encoding="utf-8")
    methods = {}
    for _, _, m in items:
        methods[m] = methods.get(m, 0) + 1
    print(
        f"wrote {out}: {len(items)} product types, narratives {methods}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
