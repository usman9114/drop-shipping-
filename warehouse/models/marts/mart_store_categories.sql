-- What categories the best stores win with, and how they get traffic.
-- Aggregate only (no domains): safe to commit.
with p as (select * from {{ ref('mart_store_profile') }} where top_category is not null),
cats as (
    select top_category as category,
        count(*)                                                    as stores,
        count(*) filter (where business_model = 'brand')            as brands,
        count(*) filter (where business_model = 'general')          as general_stores,
        count(*) filter (where business_model = 'retailer')         as retailers,
        count(*) filter (where business_model = 'reseller')         as resellers,
        count(*) filter (where business_model = 'dropship')         as dropshippers,
        count(*) filter (where business_model = 'pod')              as pod,
        count(*) filter (where business_model = 'unclear')          as unclear,
        count(*) filter (where best_score >= 0.7)                   as top30_stores,
        median(tranco_rank)::bigint                                 as median_rank,
        min(tranco_rank)                                            as best_rank,
        round(median(price_median), 2)                              as median_entry_price,
        round(median(price_p25), 2)                                 as median_price_p25,
        median(published_products)::bigint                          as median_catalogue,
        round(median(added_90d), 1)                                 as median_added_90d,
        round(avg((rank_growth_log > 0)::int) filter (where rank_growth_log is not null), 2)
                                                                    as share_rank_rising,
        round(avg(list_contains(paid_ads, 'meta_pixel')::int), 2)   as share_meta_pixel,
        round(avg(list_contains(paid_ads, 'tiktok_pixel')::int), 2) as share_tiktok_pixel,
        round(avg(list_contains(paid_ads, 'google_ads')::int), 2)   as share_google_ads,
        round(avg(list_contains(retention, 'klaviyo_email')::int), 2) as share_klaviyo,
        round(avg(list_contains(retention, 'sms_marketing')::int), 2) as share_sms,
        round(avg((len(partners) > 0)::int), 2)                     as share_affiliate_influencer,
        round(avg(list_contains(conversion, 'reviews_app')::int), 2) as share_reviews_app,
        round(avg(discount_share), 2)                               as avg_discount_share,
        round(sum(1.0 / tranco_rank) * 1e5, 2)                      as traffic_weight
    from p
    group by top_category
)
select *,
    -- Demand that zero inventory can copy: resellers, dropshippers and unclear stores.
    resellers + dropshippers + general_stores + pod + unclear as transferable_stores
from cats
order by traffic_weight desc
