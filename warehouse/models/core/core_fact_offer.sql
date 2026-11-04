-- One row per product: the cheapest US-stocked variant, US stock and the
-- cheapest US->US freight quote (fixed zip, see scout.ingest_cj.FREIGHT_ZIP).
with v as (
    select *,
        coalesce(weight_g, packing_weight_g, product_weight_g) as ship_weight_g
    from {{ ref('stg_cj_variants') }}
    where cost is not null
    qualify row_number() over (partition by pid order by cost, vid) = 1
),
stock as (
    select pid, total as us_stock from {{ ref('stg_cj_stock') }} where country = 'US'
),
freight as (
    select pid, carrier, price_usd as ship_usd, days_low, days_high
    from {{ ref('stg_cj_freight') }}
    where price_usd is not null
    qualify row_number() over (partition by pid order by price_usd, carrier) = 1
),
variants as (
    select pid, count(*) as variant_count from {{ ref('stg_cj_variants') }} group by pid
)
select
    v.pid, v.vid, v.cost, v.ship_weight_g,
    v.length_mm, v.width_mm, v.height_mm, v.materials, v.image_count,
    v.suggested_price_low, v.suggested_price_high,
    n.variant_count,
    s.us_stock,
    f.carrier, f.ship_usd, f.days_low, f.days_high,
    v.run_id
from v
left join stock s using (pid)
left join freight f using (pid)
left join variants n using (pid)
