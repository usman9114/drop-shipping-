"""Rank the best Shopify stores of one market (first use: Pakistan, owner 2026-11-22).

    python -m scout.market_rank --market pk --top 40          # table to stdout
    python -m scout.market_rank --market pk --csv out.csv     # every store (private)

Inputs, all [data] from public machine records already in the lake:
    crux_origins           Chrome UX Report popularity bucket inside the market
                           (top 1k, 5k, 10k, 50k, 100k, 500k): decision 0020
    web_scan / web_meta    global Tranco rank (stores outside the top 1M have none),
                           currency, country, product count
    web_store_light        one feed page: release rhythm (products added in 90 days),
                           entry-price band, top category
    web_ranks              Tranco rank 90 and 365 days ago (rank growth)

Score, weights only in WEIGHTS below. Only profiled stores are scored (release
rhythm needs the feed page); the rest are listed unscored. Each part is 0 to 1:
    pk_popularity  0.35  CrUX bucket: 1k=1.0, 5k=0.8, 10k=0.6, 50k=0.4, 100k=0.2, 500k=0
                         (popularity among Chrome users in the market) [proxy]
    global_rank    0.20  1 - percentile of the Tranco rank among scored stores that
                         have one; no Tranco rank = 0
    growth         0.25  percentile of ln(earliest rank / current rank); no history = 0
    rhythm         0.20  percentile of products added in the last 90 days

Why these weights: the US score (warehouse mart_store_profile) is 0.45 traffic,
0.20 growth, 0.20 rhythm, 0.15 marketing stack. The stack needs a homepage
fetch, which most stores here lack, so its weight is dropped. The 0.45 traffic
part is split: more for popularity inside Pakistan (0.35) than for the global
list (0.20), because the question is who wins in this market, and the
global list cannot see small stores at all.

What would change the order: a store with fast rank growth climbs past a
slightly busier, flat one; a store that stopped adding products drops; stores
outside the Tranco top 1M can still rank high on Pakistani popularity and rhythm
but never earn growth points. CrUX and Tranco measure visits, not sales: no
revenue, orders or margin are known. Business model is shown, not scored.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys

from scout import stores

WEIGHTS = {"pk_popularity": 0.35, "global_rank": 0.20, "growth": 0.25, "rhythm": 0.20}
BUCKET_SCORE = {1000: 1.0, 5000: 0.8, 10000: 0.6, 50000: 0.4, 100000: 0.2, 500000: 0.0}
NO_TRANCO = 1_000_000  # ranks above this mean "outside the top 1M" (marker 1,000,001)


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
    """Score the profiled rows (needs profiled, tranco_rank or None, crux_bucket or
    None, rank_growth_log, added_90d); return scored rows best first, then the
    unscored ones by Pakistani popularity."""
    scored = [r for r in rows if r.get("profiled")]
    rest = [r for r in rows if not r.get("profiled")]
    for r in rest:
        r["best_score"] = None
    if scored:
        pop = [BUCKET_SCORE.get(r.get("crux_bucket"), 0.0) for r in scored]
        has = [i for i, r in enumerate(scored) if r.get("tranco_rank")]
        glob = [0.0] * len(scored)
        for i, p in zip(has, percentile([scored[i]["tranco_rank"] for i in has])):
            glob[i] = 1 - p
        growth = percentile([r.get("rank_growth_log") or 0 for r in scored])
        rhythm = percentile([r.get("added_90d") or 0 for r in scored])
        for r, a, b, g, h in zip(scored, pop, glob, growth, rhythm):
            r["pct_pk"], r["pct_global"] = round(a, 3), round(b, 3)
            r["pct_growth"], r["pct_rhythm"] = round(g, 3), round(h, 3)
            r["best_score"] = round(
                WEIGHTS["pk_popularity"] * a
                + WEIGHTS["global_rank"] * b
                + WEIGHTS["growth"] * g
                + WEIGHTS["rhythm"] * h,
                4,
            )

    def key(r):
        return (-r["best_score"], r.get("tranco_rank") or NO_TRANCO + 1)

    scored.sort(key=key)
    rest.sort(
        key=lambda r: (
            -BUCKET_SCORE.get(r.get("crux_bucket"), 0.0),
            r.get("tranco_rank") or NO_TRANCO + 1,
        )
    )
    return scored + rest


LIGHT_FIELDS = (
    "added_30d added_90d added_365d price_p25 price_median price_p75 discount_share "
    "top_category top_category_share products_sampled vendors top_vendor_share "
    "oldest_created newest_created business_model business_model_why"
).split()


def market_rows(market: str) -> list[dict]:
    metas = stores.latest_good(stores._all_rows("web_meta"))
    light = stores.latest_good(stores._all_rows("web_store_light"))
    crux: dict[str, int] = {}
    for r in stores._all_rows("crux_origins"):
        if r["country"] == market and r["rank_bucket"] < crux.get(r["domain"], 10**9):
            crux[r["domain"]] = r["rank_bucket"]
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
        rank = rank if rank and rank <= NO_TRANCO else None
        e = earliest.get(d)
        row = {
            "domain": d,
            "shop_name": m.get("shop_name"),
            "country": m.get("country"),
            "currency": m.get("currency"),
            "tranco_rank": rank,
            "crux_bucket": crux.get(d),
            "rank_earliest": e[1] if e else None,
            "rank_earliest_date": e[0] if e else None,
            "rank_growth_log": growth_log(rank, e[1] if e else None),
            "published_products": m.get("published_products"),
            "profiled": bool(lt.get("products_sampled")),
        }
        row.update({k: lt.get(k) for k in LIGHT_FIELDS})
        out.append(row)
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
            w = csv.DictWriter(
                fh, fieldnames=list(ranked[0]), extrasaction="ignore", restval=""
            )
            w.writeheader()
            w.writerows(ranked)
    cols = (
        "best_score crux_bucket tranco_rank rank_growth_log added_90d price_median "
        "top_category domain"
    ).split()
    print("\t".join(["#"] + cols))
    for i, r in enumerate(ranked[: a.top], 1):
        print("\t".join([str(i)] + [str(r.get(c, "")) for c in cols]))
    print(
        f"{len(ranked)} stores, {sum(1 for r in ranked if r['profiled'])} scored, "
        f"{sum(1 for r in ranked if r.get('crux_bucket'))} with a CrUX bucket, "
        f"{sum(1 for r in ranked if r['rank_earliest'] is not None)} with rank history",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
