-- Candidate pool (docs/plan/top-stores-inspiration-plan.md, revised after the pilot):
-- US-relevant Shopify stores of ANY business model in two slices:
--   established = the 150 strongest by traffic level
--   riser       = the 150 fastest risers among the rest (recent rank inside the top 500k)
-- Each store gets an OWN-EVIDENCE grade from signals we hold for it (all [proxy]):
--   traffic    recent rank inside the top 150,000
--   rising     recent rank at least 35% better than 9+ months ago, and not fading
--   steady     present on at least 20 of the rank lists (about 2 years in the top 1M)
--   active     20+ products added in the last 90 days (sample capped at 250)
--   marketing  2+ paid-ad pixels, or ads plus email/SMS (deep-profiled stores only)
-- grade A = 4+ signals, B = 3, C = 2, D = 0 or 1. Private (domains).
with t as (select * from {{ ref('mart_store_rank_trend') }}),
p as (select domain, paid_ads, retention, partners, existed_by from {{ ref('mart_store_profile') }}),
u as (
    select u.*, t.rank_now, t.rank_recent_median, t.growth_old_to_recent, t.dates_present,
           t.n_dates, t.emerged, t.breakout, t.fading, t.first_seen, t.rank_volatility,
           p.paid_ads, p.retention, p.partners, p.existed_by
    from {{ ref('mart_store_universe') }} u
    left join t using (domain)
    left join p using (domain)
    where coalesce(u.top_category, 'other') not in ('books_media', 'non_product', 'adult_vape_flagged')
      and u.products_sampled >= 10
),
signals as (
    select *,
        coalesce(rank_recent_median, tranco_rank) <= 150000                          as s_traffic,
        coalesce(growth_old_to_recent >= ln(1.35) and not fading, false)             as s_rising,
        coalesce(dates_present >= 20, false)                                         as s_steady,
        least(coalesce(added_90d, 0), 250) >= 20                                     as s_active,
        case when paid_ads is null then null
             else len(paid_ads) >= 2 or (len(paid_ads) >= 1 and len(retention) >= 1) end as s_marketing
    from u
),
graded as (
    select *,
        s_traffic::int + s_rising::int + s_steady::int + s_active::int
            + coalesce(s_marketing, false)::int                                      as own_signals,
        s_marketing is not null                                                      as marketing_known
    from signals
),
established as (
    select *, 'established' as slice,
           row_number() over (order by coalesce(rank_recent_median, tranco_rank)) as slice_rank
    from graded
    qualify slice_rank <= 150
),
risers as (
    select *, 'riser' as slice,
           row_number() over (order by growth_old_to_recent desc nulls last, tranco_rank) as slice_rank
    from graded
    where domain not in (select domain from established)
      and coalesce(rank_recent_median, tranco_rank) <= 500000
      and growth_old_to_recent is not null and not coalesce(fading, false)
    qualify slice_rank <= 150
)
select *,
    case when own_signals >= 4 then 'A' when own_signals = 3 then 'B'
         when own_signals = 2 then 'C' else 'D' end as own_grade
from (select * from established union all select * from risers)
