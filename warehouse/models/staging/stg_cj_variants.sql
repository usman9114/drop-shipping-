-- Variants from `offers` pulls; offers are pulled in batches, so keep the
-- latest run per product rather than the latest run overall.
select *
from {{ lake('cj_variants', {
    'pid': 'VARCHAR', 'vid': 'VARCHAR', 'variant_sku': 'VARCHAR', 'variant_name': 'VARCHAR',
    'cost': 'DOUBLE', 'weight_g': 'DOUBLE',
    'length_mm': 'DOUBLE', 'width_mm': 'DOUBLE', 'height_mm': 'DOUBLE',
    'product_weight_g': 'DOUBLE', 'packing_weight_g': 'DOUBLE', 'materials': 'VARCHAR',
    'suggested_price_low': 'DOUBLE', 'suggested_price_high': 'DOUBLE',
    'image_count': 'BIGINT'}, all_runs=true) }}
qualify run_id = max(run_id) over (partition by pid)
