"""Store stories: a grounded "how they did it" per top store, plus the
committed aggregate report (categories, traffic stack, niche shortlist).

Deterministic first, like scout.intel: one evidence pack per store from
`mart.mart_store_profile`, a fixed template, and optionally a free model that
rewrites the pack as prose. Every number in model text must appear in the pack
or the template is used. Gaps are named in every story.

Store-level output names real domains, so it stays private:
    data/private/reports/<date>-store-stories.md
The committed report holds aggregates only (no domains):
    docs/reports/<date>-best-stores.md

Usage:
    python -m scout.store_intel --top 40            # stories + report, model text
    python -m scout.store_intel --top 40 --no-llm   # template only, offline
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

from scout.intel import _numbers

DB = Path("data/private/warehouse.duckdb")
CACHE = Path("data/private/llm_store_story_cache.csv")
PROMPT_VERSION = "store-story-v2"
FIELDS = ["pack_sha256", "narrative", "model", "prompt_version"]

PACK_KEYS = [
    "tranco_rank",
    "rank_earliest",
    "rank_earliest_date",
    "rank_growth_log",
    "country",
    "currency",
    "ships_to_count",
    "published_products",
    "existed_by",
    "oldest_created",
    "newest_created",
    "added_30d",
    "added_90d",
    "added_365d",
    "products_sampled",
    "price_p25",
    "price_median",
    "price_p75",
    "discount_share",
    "top_category",
    "top_category_share",
    "top_types",
    "business_model",
    "business_model_why",
    "paid_ads",
    "retention",
    "partners",
    "conversion",
    "social_networks",
    "dns_signals",
    "sample_review_count",
    "installments",
    "best_score",
]

# What public records cannot show. Named in every story.
STANDING_GAPS = [
    "revenue and order volume",
    "ad spend and which ads run",
    "traffic split by channel",
    "supplier and product cost (margin)",
]

SYSTEM = (
    "You are a careful e-commerce analyst. You reconstruct how an online store "
    "grew, using only the evidence you are given, and you name what is unknown."
)
PROMPT = """Evidence about one Shopify store, from public machine records (Tranco
traffic rank, DNS, the store's own /meta.json and /products.json feed, homepage
tags). Field meanings:
- tranco_rank: popularity rank among all websites now (lower = more traffic);
  rank_earliest on rank_earliest_date is the same rank earlier
- existed_by: the store existed by this date (from its sequential shop id); say
  "existed by", never "founded" or "since": the real start may be earlier
- added_30d / added_90d / added_365d: products created in those windows, among
  products_sampled newest products
- price_*: entry price per product in the store currency; discount_share: share
  of products shown with a crossed-out compare-at price
- business_model: brand (sells its own goods), retailer (10+ brands, big retailer
  or portfolio owner), reseller (5 to 9 brands), dropship
  (supplier import traces), pod (print on demand), unclear
- paid_ads / retention / partners / conversion: marketing code found on the homepage
- dns_signals: platforms the domain verified with (meta_business = Meta business account)

Evidence (JSON):
{pack}

Write 4 to 6 plain sentences: what the store sells and at what price, how long
it has existed and how often it adds products, how it gets and keeps traffic,
whether a zero-inventory seller could copy this (brands cannot be copied), and
what is unknown. Use only numbers that appear in the evidence. No store name,
no invented facts, no lists, no markdown."""


def _clean(v):
    if isinstance(v, float):
        return round(v, 3)
    if isinstance(v, (list, tuple)):
        return list(v)
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


def pack(row: dict) -> dict:
    p = {k: _clean(row.get(k)) for k in PACK_KEYS}
    p["gaps"] = gaps(p)
    return p


def gaps(p: dict) -> list[str]:
    g = list(STANDING_GAPS)
    if p.get("rank_earliest") is None:
        g.append("rank history (store not in the earlier Tranco lists)")
    if (p.get("published_products") or 0) > (p.get("products_sampled") or 0):
        g.append("older catalogue beyond the sampled pages")
    if not p.get("paid_ads"):
        g.append("ad pixels (none visible; may load after consent or server-side)")
    if p.get("sample_review_count") is None:
        g.append("review counts (no structured rating on the sampled product)")
    return g


def pack_hash(p: dict) -> str:
    blob = json.dumps(p, sort_keys=True, default=str) + PROMPT_VERSION
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def grounded(text: str, p: dict) -> bool:
    allowed: set[float] = set()

    def walk(v):
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, (int, float)):
            allowed.add(round(float(v), 2))
            if isinstance(v, float) and 0 <= v <= 1:
                allowed.add(round(v * 100, 2))  # shares written as percent
                allowed.add(round(v * 100))
        elif isinstance(v, str):
            allowed.update(round(x, 2) for x in _numbers(v))
        elif isinstance(v, list):
            for x in v:
                walk(x)

    for v in p.values():
        walk(v)
    allowed |= {30.0, 90.0, 365.0}
    return all(round(n, 2) in allowed for n in _numbers(text))


def _ls(v) -> str:
    return ", ".join(str(x).replace("_", " ") for x in v) if v else "none found"


def template(p: dict) -> str:
    cur = p.get("currency") or ""
    parts = [
        f"Sells mainly {str(p.get('top_category') or 'unclassified').replace('_', ' ')} "
        f"({_pct(p.get('top_category_share'))} of sampled products), "
        f"{p.get('published_products')} published products, entry prices "
        f"{p.get('price_p25')} to {p.get('price_p75')} {cur} (median {p.get('price_median')}).",
    ]
    if p.get("rank_earliest"):
        parts.append(
            f"Tranco rank {p.get('tranco_rank')} now against {p.get('rank_earliest')} on "
            f"{p.get('rank_earliest_date')}."
        )
    else:
        parts.append(f"Tranco rank {p.get('tranco_rank')}; no earlier rank on record.")
    parts.append(
        f"Existed by {p.get('existed_by')}; added {p.get('added_30d')} products in 30 days, "
        f"{p.get('added_90d')} in 90 and {p.get('added_365d')} in 365."
    )
    parts.append(
        f"Traffic: ads {_ls(p.get('paid_ads'))}; retention {_ls(p.get('retention'))}; "
        f"partners {_ls(p.get('partners'))}; social {_ls(p.get('social_networks'))}."
    )
    model = p.get("business_model")
    why = "; ".join(p.get("business_model_why") or [])
    copy = (
        "not copyable with zero inventory"
        if model in ("brand", "retailer")
        else "method copyable"
    )
    parts.append(f"Model: {model} ({why}), {copy}.")
    parts.append("Unknown: " + "; ".join(p["gaps"]) + ".")
    return " ".join(parts)


def _pct(x) -> str:
    return "–" if x is None else f"{round(x * 100)}%"


def load_cache(path: Path = CACHE) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["pack_sha256"]: r for r in csv.DictReader(fh)}


def append_cache(rows: list[dict], path: Path = CACHE) -> None:
    if not rows:
        return
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)


def narrate(p: dict, cache: dict, chat=None) -> tuple[str, str, dict | None]:
    key = pack_hash(p)
    if key in cache:
        return cache[key]["narrative"], "cache", None
    if chat is None:
        return template(p), "template", None
    try:
        out = chat(
            PROMPT.format(pack=json.dumps(p, sort_keys=True, default=str)),
            task="bulk",
            system=SYSTEM,
            max_tokens=700,
        )
    except Exception as exc:
        print(f"  model failed: {exc}"[:200], file=sys.stderr)
        return template(p), "template", None
    text = " ".join(out["text"].split())
    if not grounded(text, p):
        return template(p), "template (model text rejected)", None
    row = {
        "pack_sha256": key,
        "narrative": text,
        "model": out["model"],
        "prompt_version": PROMPT_VERSION,
    }
    return text, "llm", row


def _rows(con, sql: str) -> list[dict]:
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]


def render_private(items, built: str) -> str:
    lines = [
        f"# Store stories (private) — {built}",
        "",
        "> `python -m scout.store_intel`. Evidence from `mart.mart_store_profile`. "
        "Private: names real stores. Do not commit.",
        "",
        "| # | Store | Rank | Then | Score | Model | Category | Entry price | Added 90d | Ads | Retention |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, (row, p, _, _) in enumerate(items, 1):
        lines.append(
            f"| {i} | {row['domain']} | {p['tranco_rank']} | {p.get('rank_earliest') or '–'} | "
            f"{p['best_score']} | {p['business_model']} | {p.get('top_category')} | "
            f"{p.get('price_median')} {p.get('currency') or ''} | {p.get('added_90d')} | "
            f"{_ls(p.get('paid_ads'))} | {_ls(p.get('retention'))} |"
        )
    lines.append("")
    for i, (row, _p, text, method) in enumerate(items, 1):
        lines += [
            f"## {i}. {row['domain']}",
            "",
            text,
            "",
            f"*Narrative: {method}.*",
            "",
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Grounded store stories")
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--transferable-only", action="store_true")
    a = ap.parse_args(argv)
    import duckdb

    con = duckdb.connect(a.db, read_only=True)
    where = "where transferable_model" if a.transferable_only else ""
    rows = _rows(
        con,
        f"select * from mart.mart_store_profile {where} "
        f"order by best_score desc, tranco_rank limit {int(a.top)}",
    )
    con.close()
    chat = None
    if not a.no_llm:
        from scout.llm import chat as llm_chat

        chat = llm_chat
    cache = load_cache()
    items, new = [], []
    for r in rows:
        p = pack(r)
        text, method, crow = narrate(p, cache, chat)
        items.append((r, p, text, method))
        if crow:
            new.append(crow)
            cache[crow["pack_sha256"]] = crow
    append_cache(new)
    today = date.today().isoformat()
    out = Path(f"data/private/reports/{today}-store-stories.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_private(items, today) + "\n", encoding="utf-8")
    methods: dict[str, int] = {}
    for *_, m in items:
        methods[m] = methods.get(m, 0) + 1
    print(f"wrote {out}: {len(items)} stores, narratives {methods}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
