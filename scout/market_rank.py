"""Rank the best Shopify stores of one market (first use: Pakistan, owner 2026-11-22).

    python -m scout.market_rank --market pk --top 40          # table to stdout
    python -m scout.market_rank --market pk --csv out.csv     # every store (private)

Inputs, all [data] from public machine records already in the lake:
    web_scan / web_meta    current Tranco rank, currency, country, product count
    web_store_light        one feed page: release rhythm (products added in 90 days),
                           entry-price band, top category
    web_ranks              Tranco rank 90 and 365 days ago (rank growth)

Score (weights live only in WEIGHTS below; each input is a percentile among the
market's stores, so the score says "better than X% of this market's stores"):
    traffic  0.55  1 - percentile of current Tranco rank (lower rank = more visits) [proxy]
    growth   0.25  percentile of ln(earliest rank / current rank); no history = 0
    rhythm   0.20  percentile of products added in the last 90 days

Why these weights: the US score (warehouse mart_store_profile) is 0.45 traffic,
0.20 growth, 0.20 rhythm, 0.15 marketing stack. The stack needs a homepage
fetch (deep profile), which most stores here lack, so its 0.15 is spread over
the other three in proportion (0.45/0.85 ~ 0.53 -> 0.55, 0.20/0.85 ~ 0.235).

What would change the order: a store with fast rank growth climbs past a
slightly busier, flat one; a store that stopped adding products drops. Tranco
rank is traffic popularity, not sales: no revenue, orders or margin are known.
Business model is shown but NOT scored: the rules were tuned on US stores and
mislabel Pakistani brands (sample 2026-11-22), see docs/decisions/0019.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys

from scout import stores

WEIGHTS = {"traffic": 0.55, "growth": 0.25, "rhythm": 0.20}


def percentile(values: list[float]) -> list[float]:
    """percent_rank like DuckDB: (rank - 1) / (n - 1), ties share the lowest rank."""
    n = len(values)
    if n < 2:
        return [0.0] * n
    order = sorted(values)
    first = {}
    for i, v in enumerate(order):
        first.setdefault(v, i)
    return [first[v] / (n - 1) for v in values]


def growth_log(current: int | None, earliest: int | None) -> float | None:
    if not current or not earliest:
        return None
    return round(math.log(earliest / current), 3)


def score(rows: list[dict]) -> list[dict]:
    """Add pct_* and best_score to each row (needs tranco_rank, rank_growth_log,
    added_90d); return rows best first."""
    if not rows:
        return []
    traffic = [1 - p for p in percentile([r["tranco_rank"] for r in rows])]
    growth = percentile([r.get("rank_growth_log") or 0 for r in rows])
    rhythm = percentile([r.get("added_90d") or 0 for r in rows])
    for r, t, g, h in zip(rows, traffic, growth, rhythm):
        r["pct_traffic"], r["pct_growth"], r["pct_rhythm"] = (
            round(t, 3),
            round(g, 3),
            round(h, 3),
        )
        r["best_score"] = round(
            WEIGHTS["traffic"] * t + WEIGHTS["growth"] * g + WEIGHTS["rhythm"] * h,
            4,
        )
    return sorted(rows, key=lambda r: (-r["best_score"], r["tranco_rank"]))


def market_rows(market: str) -> list[dict]:
    metas = stores.latest_good(stores._all_rows("web_meta"))
    light = stores.latest_good(stores._all_rows("web_store_light"))
    current: dict[str, int] = {}
    for r in stores._all_rows("web_scan"):
        d = r["domain"]
        current[d] = min(current.get(d, 10**9), r["tranco_rank"])
    earliest: dict[str, tuple[str, int]] = {}
    for r in stores._all_rows("web_ranks"):
        d, dt = r["domain"], r["list_date"]
        if d not in earliest or dt < earliest[d][0]:
            earliest[d] = (dt, r["tranco_rank"])
    out = []
    for d, m in metas.items():
        if not m.get("shop_id") or not stores.in_market(m, market):
            continue
        lt = light.get(d, {})
        rank = current.get(d) or m.get("tranco_rank")
        e = earliest.get(d)
        out.append(
            {
                "domain": d,
                "shop_name": m.get("shop_name"),
                "country": m.get("country"),
                "currency": m.get("currency"),
                "tranco_rank": rank,
                "rank_earliest": e[1] if e else None,
                "rank_earliest_date": e[0] if e else None,
                "rank_growth_log": growth_log(rank, e[1] if e else None),
                "published_products": m.get("published_products"),
                "profiled": bool(lt.get("products_sampled")),
                "added_90d": lt.get("added_90d"),
                "price_median": lt.get("price_median"),
                "top_category": lt.get("top_category"),
                "business_model_unvalidated": lt.get("business_model"),
            }
        )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--market", choices=sorted(stores.MARKETS), default="pk")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--csv", help="write every ranked store here (keep it private)")
    a = ap.parse_args(argv)
    ranked = score(market_rows(a.market))
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(ranked[0]))
            w.writeheader()
            w.writerows(ranked)
    cols = (
        "best_score tranco_rank rank_growth_log added_90d price_median "
        "top_category domain"
    ).split()
    print("\t".join(["#"] + cols))
    for i, r in enumerate(ranked[: a.top], 1):
        print("\t".join([str(i)] + [str(r.get(c, "")) for c in cols]))
    print(
        f"{len(ranked)} stores, {sum(r['profiled'] for r in ranked)} profiled, "
        f"{sum(r['rank_earliest'] is not None for r in ranked)} with rank history",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
