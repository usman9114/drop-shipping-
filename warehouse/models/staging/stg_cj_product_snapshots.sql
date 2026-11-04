-- Every catalogue run, not just the latest: the time series behind velocity.
-- run_id starts with the UTC fetch time (YYYYMMDDTHHMMSSZ, see scout.store).
select
    pid,
    strptime(substr(run_id, 1, 16), '%Y%m%dT%H%M%SZ')  as snapshot_at,
    price_low                                          as cost_low,
    warehouse_inventory                                as us_stock,
    listed_num,
    run_id
from {{ lake('cj_products', {
    'pid': 'VARCHAR', 'price_low': 'DOUBLE',
    'warehouse_inventory': 'BIGINT', 'listed_num': 'BIGINT'}, all_runs=true) }}
where pid is not null
qualify row_number() over (partition by pid, run_id order by listed_num desc nulls last) = 1
