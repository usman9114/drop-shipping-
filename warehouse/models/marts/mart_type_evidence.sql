-- One row per product type: everything the intelligence layer may cite.
-- Supply and margin (CJ + scout.margin), popularity (listed_num), velocity
-- (repeated pulls), why-tags (rules). External demand signals join here later.
with c as (
    select c.*, p.listed_num
    from {{ ref('mart_supply_candidates') }} c
    left join {{ ref('stg_cj_products') }} p using (pid)
    where c.product_type is not null
),
v as (select * from {{ ref('mart_product_velocity') }})
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
    any_value(w.why_tags)                                        as why_tags
from c
left join v using (pid)
left join {{ ref('rule_why') }} w on w.product_type = c.product_type
group by c.product_type
