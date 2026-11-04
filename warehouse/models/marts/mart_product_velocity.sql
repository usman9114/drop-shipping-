-- Change over time per product, from repeated catalogue pulls (make wh-snapshot).
-- A fall in CJ US stock is the closest thing to a sales meter we have: every
-- store selling the item ships from the same US stock. A rise in listed_num means
-- more stores are adopting it. Restocks break the stock signal, so drawdown only
-- sums falls, and restocks are counted. Rates need at least half a day of history.
with s as (
    select *,
        lag(us_stock)   over w as prev_stock,
        lag(listed_num) over w as prev_listed
    from {{ ref('core_fact_product_snapshot') }}
    window w as (partition by pid order by snapshot_at)
),
agg as (
    select
        pid,
        count(*)                                                    as snapshots,
        min(snapshot_at)                                            as first_at,
        max(snapshot_at)                                            as last_at,
        date_diff('minute', min(snapshot_at), max(snapshot_at)) / 1440.0 as span_days,
        coalesce(sum(greatest(prev_stock - us_stock, 0)), 0)       as stock_drawdown,
        count(*) filter (where us_stock > prev_stock)               as restocks,
        arg_max(listed_num, snapshot_at) - arg_min(listed_num, snapshot_at) as listed_gain
    from s
    group by pid
)
select
    pid, snapshots, first_at, last_at,
    round(span_days, 3)                                              as span_days,
    stock_drawdown, restocks, listed_gain,
    case when span_days >= 0.5 then round(stock_drawdown / span_days, 2) end as units_per_day,
    case when span_days >= 0.5 then round(listed_gain / span_days, 2) end   as listings_per_day
from agg
