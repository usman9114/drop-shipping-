-- Phase 1 candidate pool (docs/plan/top-stores-inspiration-plan.md): US-relevant
-- Shopify stores of ANY business model, ranked by a performance proxy. Private.
-- proxy = 0.60 traffic + 0.25 rank growth + 0.15 release rhythm, each a percentile
-- among eligible stores. A proxy only: rank is popularity, not sales.
with u as (
    select u.*, t.rank_now, t.growth_old_to_recent, t.slope_90d, t.emerged, t.breakout,
           t.fading, t.first_seen, t.rank_volatility
    from {{ ref('mart_store_universe') }} u
    left join {{ ref('mart_store_rank_trend') }} t using (domain)
    where coalesce(u.top_category, 'other') not in ('books_media', 'non_product', 'adult_vape_flagged')
      and u.products_sampled >= 10
),
scored as (
    select *,
        1 - percent_rank() over (order by tranco_rank)                          as pct_traffic,
        percent_rank() over (order by coalesce(growth_old_to_recent, 0))        as pct_growth,
        -- capped at 250: light screens read one page, deep profiles up to 1,000 products
        percent_rank() over (order by least(coalesce(added_90d, 0), 250))       as pct_rhythm
    from u
)
select *,
    round(0.60 * pct_traffic + 0.25 * pct_growth + 0.15 * pct_rhythm, 4) as performance_proxy,
    row_number() over (order by 0.60 * pct_traffic + 0.25 * pct_growth + 0.15 * pct_rhythm desc,
                       tranco_rank) as pool_rank
from scored
qualify pool_rank <= 300
