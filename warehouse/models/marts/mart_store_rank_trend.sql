-- Temporal features per Shopify store from its Tranco rank history (26 list dates,
-- about 2 years, plus today's scan). Absence from a list means rank above 1,000,000.
-- Private (domains). Lower rank number = more traffic, so "improving" = falling rank.
with today as (
    select domain, tranco_rank,
           (select max(list_date) from {{ ref('stg_web_ranks') }}) + interval 7 day as list_date
    from {{ ref('stg_web_scan') }}
),
hist as (
    select domain, list_date, tranco_rank from {{ ref('stg_web_ranks') }}
    union all
    select domain, list_date::date, tranco_rank from today
),
dates as (select count(distinct list_date) as n_dates, min(list_date) as first_date,
                 max(list_date) as last_date from hist),
agg as (
    select domain,
        count(*)                                           as dates_present,
        min(list_date)                                     as first_seen,
        max(list_date)                                     as last_seen,
        min(tranco_rank)                                   as best_rank,
        max(tranco_rank)                                   as worst_rank,
        round(stddev_samp(ln(tranco_rank)), 3)             as rank_volatility,
        -- change in ln(rank) per 90 days; negative = traffic rising
        round(regr_slope(ln(tranco_rank), epoch(list_date) / 86400.0) * 90, 3) as slope_90d,
        arg_max(tranco_rank, list_date)                    as rank_now,
        arg_min(tranco_rank, list_date)                    as rank_first
    from hist
    group by domain
),
ref as (
    select h.domain,
        median(h.tranco_rank) filter (where h.list_date <= d.last_date - interval 270 day) as rank_old_median,
        median(h.tranco_rank) filter (where h.list_date >= d.last_date - interval 90 day)  as rank_recent_median
    from hist h cross join dates d
    group by h.domain
)
select a.*, r.rank_old_median, r.rank_recent_median,
    d.n_dates,
    round(ln(r.rank_old_median / r.rank_recent_median), 3)              as growth_old_to_recent,
    -- emerged: absent from every list older than 270 days, present on 3+ recent lists
    -- and solidly inside the top 500k (stores hovering near the 1M cutoff are noise)
    (a.first_seen > d.last_date - interval 270 day
        and a.dates_present >= 3
        and r.rank_recent_median <= 500000)                              as emerged,
    -- breakout: rank at least 2x better than the older level, or emerged
    ((r.rank_old_median / r.rank_recent_median >= 2
        and r.rank_recent_median <= 500000)
        or (a.first_seen > d.last_date - interval 270 day
            and a.dates_present >= 3
            and r.rank_recent_median <= 500000))                         as breakout,
    -- fading: rank at least 2x worse
    (r.rank_recent_median / r.rank_old_median >= 2)                      as fading
from agg a
join ref r using (domain)
cross join dates d
