"""Committed aggregate report for step 1 (best online stores). No domains.

Reads the private warehouse and writes:
    docs/reports/<date>-best-stores.md          ranked categories, traffic stack, funnel
    docs/shortlists/<date>-niche-candidates.csv niche shortlist for step 2 (sourcing)

Only counts, shares, medians and our labels leave data/private/. Merchant
product-type labels are included only when at least MIN_STORES stores use them.

    python scripts/store_export.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import duckdb

DB = "data/private/warehouse.duckdb"
MIN_STORES = 3  # k-anonymity floor for any label published
MIN_COPYABLE = 5  # a niche needs this many copyable stores
# Categories a small eBay/Shopify dropshipper should not start with (compliance,
# perishables, licensing, or not a physical product). Our rule, reviewable.
EXCLUDE = {
    "non_product": "not a physical product",
    "food_beverage": "perishable, FDA food rules",
    "health_supplements": "FDA/FTC claims, eBay restrictions",
    "adult_vape_flagged": "restricted on eBay",
    "baby_kids": "CPSIA testing and certificates",
    "books_media": "publisher supply, thin margins",
    "other": "unclassified",
}
REVIEW = {
    "phone_electronics": "FCC and lithium shipping rules",
    "bikes_moto_auto": "heavy or fitment-specific",
    "furniture": "freight-heavy",
    "toys_games": "CPSIA if for children",
    "music_instruments": "heavy, brand-led",
}
IMPULSE = (12.0, 80.0)  # entry-price band that suits a new seller


def rows(con, sql):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]


def table(rs, cols, headers=None) -> list[str]:
    headers = headers or cols
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(cols)]
    for r in rs:
        out.append(
            "| "
            + " | ".join("–" if r.get(c) is None else str(r.get(c)) for c in cols)
            + " |"
        )
    return out


def niche_score(c: dict) -> float:
    """Deterministic: traffic of copyable stores x momentum x rhythm x price fit.

    Uses only copyable stores (resellers, dropshippers, general stores, print on
    demand, unclear): a brand's success does not transfer to zero inventory."""
    if c["category"] in EXCLUDE or (c.get("copyable_stores") or 0) < MIN_COPYABLE:
        return 0.0
    price = c.get("copyable_median_entry_price") or 0
    fit = 1.0 if IMPULSE[0] <= price <= IMPULSE[1] else 0.4
    rising = c.get("copyable_share_rank_rising") or 0.0
    rhythm = min((c.get("copyable_median_added_90d") or 0) / 30.0, 1.0)
    review = 0.7 if c["category"] in REVIEW else 1.0
    return round(
        (c.get("copyable_traffic_weight") or 0)
        * (0.5 + rising)
        * (0.5 + rhythm)
        * fit
        * review,
        3,
    )


def main() -> int:
    today = date.today().isoformat()
    con = duckdb.connect(DB, read_only=True)
    tr = rows(
        con,
        """select count(*) tranches, sum(looked_up) looked_up, sum(resolved) resolved,
                             sum(shopify) shopify, min(rank_from) rank_from, max(rank_to) rank_to
                      from stg.stg_web_scan_tranches""",
    )[0]
    funnel = rows(
        con,
        """
        select (select count(*) from stg.stg_web_scan) shopify_domains,
               (select count(*) from stg.stg_web_meta) meta_tried,
               (select count(*) from stg.stg_web_meta where shop_id is not null) meta_answered,
               (select count(*) from stg.stg_web_meta where country = 'US' or currency = 'USD') us_stores,
               (select count(*) from stg.stg_web_store_deep) deep_tried,
               (select count(*) from mart.mart_store_profile) profiled""",
    )[0]
    bands = rows(
        con,
        """
        select case when tranco_rank <= 10000 then '1-10k' when tranco_rank <= 100000 then '10k-100k'
                    when tranco_rank <= 300000 then '100k-300k' else '300k-1M' end band,
               count(*) shopify_stores
        from stg.stg_web_scan group by 1 order by min(tranco_rank)""",
    )
    countries = rows(
        con,
        """select coalesce(country,'?') country, count(*) stores
                             from stg.stg_web_meta where shop_id is not null
                             group by 1 order by 2 desc limit 10""",
    )
    models = rows(
        con,
        """
        select business_model, count(*) stores, median(tranco_rank)::bigint median_rank,
               round(median(best_score), 2) median_score,
               count(*) filter (where best_score >= 0.7) top30
        from mart.mart_store_profile group by 1 order by 2 desc""",
    )
    stack = rows(
        con,
        """
        with t as (select unnest(traffic_tags) tag, best_score >= 0.7 top from mart.mart_store_profile),
             n as (select count(*) n_all, count(*) filter (where best_score >= 0.7) n_top
                   from mart.mart_store_profile)
        select tag, round(count(*) / any_value(n_all), 2) share_all,
               round(count(*) filter (where top) / nullif(any_value(n_top), 0), 2) share_top30
        from t, n group by tag order by share_top30 desc nulls last, share_all desc""",
    )
    dns = rows(
        con,
        """
        with t as (select unnest(dns_signals) sig from mart.mart_store_profile),
             n as (select count(*) n from mart.mart_store_profile)
        select sig, round(count(*) / any_value(n), 2) share from t, n group by sig order by 2 desc""",
    )
    universe = rows(
        con,
        """select business_model, count(*) stores, median(tranco_rank)::bigint median_rank,
                  count(*) filter (where depth = 'deep') deep
           from mart.mart_store_universe group by 1 order by 2 desc""",
    )
    uni = rows(
        con,
        """select count(*) screened, count(*) filter (where copyable) copyable
           from mart.mart_store_universe""",
    )[0]
    cats = rows(con, "select * from mart.mart_niche_copyable")
    deep_stats = {
        r["category"]: r for r in rows(con, "select * from mart.mart_store_categories")
    }
    for c in cats:  # traffic-stack shares come from the deep-profiled stores only
        d = deep_stats.get(c["category"], {})
        for k in (
            "share_meta_pixel",
            "share_tiktok_pixel",
            "share_google_ads",
            "share_klaviyo",
            "share_sms",
            "share_affiliate_influencer",
            "share_reviews_app",
            "avg_discount_share",
        ):
            c[k] = d.get(k)
        c["deep_stores"] = d.get("stores")
    types = rows(
        con,
        f"""
        with t as (select top_category, unnest(top_types[1:3]) ptype
                   from mart.mart_store_profile where transferable_model)
        select top_category, ptype, count(*) stores from t group by all
        having count(*) >= {MIN_STORES} order by stores desc""",
    )
    con.close()

    for c in cats:
        c["niche_score"] = niche_score(c)
        c["note"] = EXCLUDE.get(c["category"]) or REVIEW.get(c["category"]) or ""
    ranked = sorted(cats, key=lambda c: -c["niche_score"])
    short = [c for c in ranked if c["niche_score"] > 0][:8]
    for c in short:
        c["example_types"] = "; ".join(
            t["ptype"] for t in types if t["top_category"] == c["category"]
        )[:120]

    out = Path(f"docs/shortlists/{today}-niche-candidates.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    import csv

    cols = [
        "category",
        "niche_score",
        "stores",
        "copyable_stores",
        "brands",
        "retailers",
        "copyable_median_rank",
        "copyable_median_entry_price",
        "copyable_median_added_90d",
        "copyable_share_rank_rising",
        "copyable_avg_discount_share",
        "deep_stores",
        "share_meta_pixel",
        "share_tiktok_pixel",
        "share_klaviyo",
        "share_sms",
        "note",
        "example_types",
    ]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n"
        )
        w.writeheader()
        w.writerows(short)

    md = [
        f"# Best online stores: what they sell and how they get traffic — {today}",
        "",
        "> Step 1 (owner, 2026-11-04). Built by `make stores` (decision 0009): Tranco top 1M → "
        "DNS (Shopify IP range) → each store's own `/meta.json`, `/products.json` and homepage, "
        "robots.txt respected → `mart.mart_store_profile` → this export. **Aggregates only**: "
        "store domains stay in `data/private/`. Numbers are [data] from public machine records; "
        "business model and category are our rules (`scout/stores.py`, "
        "`warehouse/seeds/store_category_rules.csv`).",
        "",
        "## Funnel",
        "",
        f"Scanned {tr['looked_up']} Tranco domains (ranks {tr['rank_from'] + 1}–{tr['rank_to']}, "
        f"{tr['tranches']} tranches); {tr['resolved']} resolved; **{funnel['shopify_domains']} on "
        f"Shopify**.",
        "",
        *table([funnel], list(funnel)),
        "",
        "Shopify stores by traffic band:",
        "",
        *table(bands, ["band", "shopify_stores"]),
        "",
        "Store country (from `/meta.json`), top 10:",
        "",
        *table(countries, ["country", "stores"]),
        "",
        "## Business model of every screened US store",
        "",
        f"{uni['screened']} US stores screened (one page of each store's own feed); "
        f"**{uni['copyable']} are copyable** (dropship, general store, reseller, print on demand, "
        "unclear). Brand = sells its own goods (its success does not transfer to zero inventory); "
        "retailer = 10+ brands or a portfolio owner (not copyable at our scale); general = one name "
        "over many unrelated categories with permanent discounts, the dropshipper shape (a "
        "hypothesis, validated separately).",
        "",
        *table(universe, ["business_model", "stores", "median_rank", "deep"]),
        "",
        "Deep-profiled stores only (best traffic first; `top30` = best_score ≥ 0.7):",
        "",
        *table(
            models, ["business_model", "stores", "median_rank", "median_score", "top30"]
        ),
        "",
        "## Categories the best stores win with",
        "",
        "Over every screened US store, by the store's main category. `copyable_*` columns use "
        "copyable stores only. `copyable_traffic_weight` = Σ 1/rank ×10⁵ over copyable stores.",
        "",
        *table(
            ranked,
            [
                "category",
                "stores",
                "copyable_stores",
                "brands",
                "retailers",
                "copyable_median_rank",
                "copyable_median_entry_price",
                "copyable_median_added_90d",
                "copyable_share_rank_rising",
                "copyable_traffic_weight",
                "niche_score",
                "note",
            ],
        ),
        "",
        "## How they get traffic",
        "",
        "Homepage code (share of deep-profiled stores, and of the top 30%; deep profiles favour the highest-traffic stores, so this describes the strongest stores, not the copyable ones):",
        "",
        *table(stack, ["tag", "share_all", "share_top30"]),
        "",
        "DNS verification and email records:",
        "",
        *table(dns, ["sig", "share"]),
        "",
        "Per category (share of deep-profiled stores with each channel; `deep_stores` is the sample size, read small samples with care):",
        "",
        *table(
            ranked,
            [
                "category",
                "share_meta_pixel",
                "share_tiktok_pixel",
                "share_google_ads",
                "share_klaviyo",
                "share_sms",
                "share_affiliate_influencer",
                "share_reviews_app",
                "avg_discount_share",
            ],
        ),
        "",
        "## Niche shortlist for step 2 (sourcing)",
        "",
        f"Score = copyable_traffic_weight × (0.5 + rising share) × (0.5 + rhythm) × "
        f"price fit (entry price {IMPULSE[0]:.0f}–{IMPULSE[1]:.0f}) × review discount; "
        f"needs at least {MIN_COPYABLE} copyable stores. Excluded: "
        + ", ".join(f"{k} ({v})" for k, v in EXCLUDE.items())
        + f". File: `{out}`.",
        "",
        *table(
            short,
            [
                "category",
                "niche_score",
                "copyable_stores",
                "copyable_median_entry_price",
                "copyable_median_added_90d",
                "copyable_share_rank_rising",
                "note",
                "example_types",
            ],
        ),
        "",
    ]
    rep = Path(f"docs/reports/{today}-best-stores.md")
    rep.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {rep} and {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
