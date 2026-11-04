-- Every screened US store (light or deep), one row each, with its business model.
-- Deep profiles win over light ones. Private (domains). Aggregates come from
-- mart_niche_copyable.
with light as (
    select domain, tranco_rank, business_model, top_category, top_category_share,
           price_p25, price_median, price_p75, discount_share, added_90d, added_365d,
           products_sampled, vendors, 'light' as depth
    from {{ ref('stg_web_store_light') }}
    where products_sampled > 0 and business_model is not null
),
deep as (
    select domain, tranco_rank, business_model, top_category, top_category_share,
           price_p25, price_median, price_p75, discount_share, added_90d, added_365d,
           products_sampled, vendors, 'deep' as depth
    from {{ ref('stg_web_store_deep') }}
    where products_sampled > 0 and business_model is not null
),
u as (
    select * from deep
    union all
    select * from light where domain not in (select domain from deep)
),
meta as (select domain, published_products, shop_id from {{ ref('stg_web_meta') }}),
growth as (
    select s.domain, ln(r.rank_earliest::double / s.tranco_rank) as rank_growth_log
    from (select domain, min(tranco_rank) as tranco_rank from {{ ref('stg_web_scan') }} group by domain) s
    join (select domain, arg_min(tranco_rank, list_date) as rank_earliest
          from {{ ref('stg_web_ranks') }} group by domain) r using (domain)
)
select u.*, m.published_products, g.rank_growth_log,
       business_model in ('dropship', 'general', 'reseller', 'pod', 'unclear') as copyable
from u
left join meta m using (domain)
left join growth g using (domain)
