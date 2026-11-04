-- Tranco rank of scanned stores on earlier list dates.
select domain, list_date::date as list_date, list_id, tranco_rank
from {{ lake('web_ranks', {'domain': 'VARCHAR', 'list_date': 'VARCHAR',
                          'list_id': 'VARCHAR', 'tranco_rank': 'BIGINT'}, all_runs=true) }}
qualify row_number() over (partition by domain, list_date order by run_id desc) = 1
