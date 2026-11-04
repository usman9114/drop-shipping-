-- One row per product type with viable CJ supply: what to search in Terapeak
-- and the price a sold listing must reach. Owner fills the blank columns by hand.
select
    coalesce(product_type, 'unclassified')          as product_type,
    coalesce(product_type, 'unclassified')          as search_phrase,
    count(*)                                        as cj_products,
    round(min(cost), 2)                             as cost_min,
    round(max(cost), 2)                             as cost_max,
    round(median(ship_usd), 2)                      as ship_median,
    round(min(min_price), 2)                        as price_floor_best,
    round(median(min_price), 2)                     as price_floor_median,
    string_agg(distinct review_rules, ';')          as review_flags
from {{ ref('mart_supply_candidates') }}
where is_viable
group by 1
order by cj_products desc, price_floor_best
