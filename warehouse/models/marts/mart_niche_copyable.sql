-- Per category: how many screened US stores exist, how many are copyable, and what
-- those copyable stores look like (price, release rhythm, rank trend). Aggregate
-- only (no domains): safe to commit.
select
    top_category as category,
    count(*)                                              as stores,
    count(*) filter (where copyable)                      as copyable_stores,
    count(*) filter (where business_model = 'brand')      as brands,
    count(*) filter (where business_model = 'retailer')   as retailers,
    round(median(price_median) filter (where copyable), 2) as copyable_median_entry_price,
    round(median(added_90d) filter (where copyable), 1)   as copyable_median_added_90d,
    round(avg((rank_growth_log > 0)::int)
          filter (where copyable and rank_growth_log is not null), 2) as copyable_share_rank_rising,
    round(avg(discount_share) filter (where copyable), 2) as copyable_avg_discount_share,
    median(tranco_rank) filter (where copyable)::bigint   as copyable_median_rank,
    round(sum(1.0 / tranco_rank) filter (where copyable) * 1e5, 2) as copyable_traffic_weight
from {{ ref('mart_store_universe') }}
where top_category is not null
group by top_category
order by copyable_stores desc
