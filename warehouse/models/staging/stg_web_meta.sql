-- Shopify /meta.json per store (latest answer per domain).
select *
from {{ lake('web_meta', {
    'domain': 'VARCHAR', 'tranco_rank': 'BIGINT', 'meta_allowed': 'BOOLEAN',
    'feed_allowed': 'BOOLEAN', 'status': 'BIGINT', 'shop_id': 'BIGINT',
    'shop_name': 'VARCHAR', 'country': 'VARCHAR', 'province': 'VARCHAR',
    'currency': 'VARCHAR', 'ships_to_count': 'BIGINT', 'ships_to_us': 'BOOLEAN',
    'published_products': 'BIGINT', 'published_collections': 'BIGINT',
    'installments': 'BOOLEAN', 'final_host': 'VARCHAR', 'error': 'VARCHAR'},
    all_runs=true) }}
qualify row_number() over (partition by domain order by (shop_id is not null) desc, run_id desc) = 1
