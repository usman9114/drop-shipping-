-- Deep profile per store: product-feed aggregates, homepage tags, DNS. Latest per domain.
select *
from {{ lake('web_store_deep', {
    'domain': 'VARCHAR', 'tranco_rank': 'BIGINT',
    'products_sampled': 'BIGINT', 'oldest_created': 'DATE', 'newest_created': 'DATE',
    'added_30d': 'BIGINT', 'added_90d': 'BIGINT', 'added_365d': 'BIGINT',
    'created_by_month': 'JSON',
    'price_p25': 'DOUBLE', 'price_median': 'DOUBLE', 'price_p75': 'DOUBLE',
    'discount_share': 'DOUBLE', 'variants_per_product': 'DOUBLE',
    'available_variant_share': 'DOUBLE',
    'vendors': 'BIGINT', 'top_vendor_share': 'DOUBLE', 'own_vendor_share': 'DOUBLE',
    'category_counts': 'JSON', 'top_category': 'VARCHAR', 'top_category_share': 'DOUBLE',
    'top_types': 'VARCHAR[]',
    'ae_image_share': 'DOUBLE', 'dropship_sku_share': 'DOUBLE',
    'dropship_vendor_share': 'DOUBLE', 'pod_share': 'DOUBLE',
    'traffic_tags': 'VARCHAR[]', 'social_networks': 'VARCHAR[]',
    'sample_review_count': 'BIGINT', 'sample_rating': 'DOUBLE',
    'dns_signals': 'VARCHAR[]', 'mx': 'VARCHAR[]',
    'business_model': 'VARCHAR', 'business_model_why': 'VARCHAR[]',
    'feed_allowed': 'BOOLEAN', 'feed_status': 'BIGINT', 'error': 'VARCHAR'},
    all_runs=true) }}
-- a failed refresh (error set) must not replace a good profile
qualify row_number() over (partition by domain order by (error is null) desc, run_id desc) = 1
