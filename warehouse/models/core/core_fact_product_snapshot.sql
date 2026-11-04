-- One row per product per catalogue run (append-only history).
select pid, snapshot_at, cost_low, us_stock, listed_num, run_id
from {{ ref('stg_cj_product_snapshots') }}
