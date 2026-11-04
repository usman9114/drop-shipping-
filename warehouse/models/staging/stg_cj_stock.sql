select pid, country, total, cj, factory, run_id
from {{ lake('cj_stock', {
    'pid': 'VARCHAR', 'country': 'VARCHAR', 'total': 'BIGINT', 'cj': 'BIGINT', 'factory': 'BIGINT'},
    all_runs=true) }}
qualify run_id = max(run_id) over (partition by pid)
