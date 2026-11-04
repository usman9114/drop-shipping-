-- One row per CJ product in the latest US-warehouse listing run.
select
    pid,
    trim(name)                         as title,
    sku,
    price_low                          as cost_low,
    price_high                         as cost_high,
    warehouse_inventory                as us_stock,
    verified_inventory,
    category_id,
    listed_num,
    run_id
from {{ lake('cj_products', {
    'pid': 'VARCHAR', 'name': 'VARCHAR', 'sku': 'VARCHAR',
    'price_low': 'DOUBLE', 'price_high': 'DOUBLE',
    'warehouse_inventory': 'BIGINT', 'verified_inventory': 'BIGINT',
    'category_id': 'VARCHAR', 'listed_num': 'BIGINT'}) }}
where pid is not null
qualify row_number() over (partition by pid order by listed_num desc nulls last) = 1
