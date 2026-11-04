select pid, vid, zip, carrier, price_usd, days_low, days_high, run_id
from {{ lake('cj_freight', {
    'pid': 'VARCHAR', 'vid': 'VARCHAR', 'zip': 'VARCHAR', 'carrier': 'VARCHAR',
    'price_usd': 'DOUBLE', 'days_low': 'BIGINT', 'days_high': 'BIGINT'}, all_runs=true) }}
qualify run_id = max(run_id) over (partition by pid)
