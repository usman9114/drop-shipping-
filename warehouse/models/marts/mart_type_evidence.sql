-- One row per product type: everything the intelligence layer may cite.
-- Supply and margin (CJ + scout.margin), popularity (listed_num), velocity
-- (repeated pulls), eBay demand (owner's Terapeak readings), why-tags (rules).
with c as (
    select c.*, p.listed_num
    from {{ ref('mart_supply_candidates') }} c
    left join {{ ref('stg_cj_products') }} p using (pid)
    where c.product_type is not null
),
v as (select * from {{ ref('mart_product_velocity') }}),
t as (
    select product_type,
        sum(sold_count_90d)                 as ebay_sold_90d,
        round(median(avg_sold_price), 2)    as ebay_avg_price,
        sum(active_listings)                as ebay_active_listings,
        round(median(sell_through_pct), 1)  as ebay_sell_through_pct,
        count(*)                            as ebay_searches
    from {{ ref('stg_terapeak_observations') }}
    group by product_type
)
select
    c.product_type,
    count(*)                                                     as cj_products,
    count(*) filter (where c.is_viable)                          as viable_products,
    round(median(c.min_price) filter (where c.is_viable), 2)     as median_price_floor,
    round(min(c.min_price) filter (where c.is_viable), 2)        as best_price_floor,
    cast(round(median(c.listed_num)) as bigint)                  as median_listed,
    count(*) filter (where c.listed_num >= 500)                  as popular_products,
    count(*) filter (where c.review_rules is not null)           as flagged_products,
    round(median(v.units_per_day), 2)                            as median_units_per_day,
    round(sum(v.units_per_day), 2)                               as total_units_per_day,
    round(max(v.span_days), 2)                                   as velocity_span_days,
    any_value(t.ebay_sold_90d)                                   as ebay_sold_90d,
    any_value(t.ebay_avg_price)                                  as ebay_avg_price,
    any_value(t.ebay_active_listings)                            as ebay_active_listings,
    any_value(t.ebay_sell_through_pct)                           as ebay_sell_through_pct,
    any_value(w.why_tags)                                        as why_tags
from c
left join v using (pid)
left join t on t.product_type = c.product_type
left join {{ ref('rule_why') }} w on w.product_type = c.product_type
group by c.product_type
