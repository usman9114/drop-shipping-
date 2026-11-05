-- Coverage of the scan: one row per tranche (counts come from the run params).
-- A tranche inside a larger one (a test run) is dropped so nothing is counted twice.
with t as (
select
    run_id,
    (params ->> 'list_id')               as list_id,
    (params ->> 'start')::bigint         as rank_from,
    (params ->> 'end')::bigint           as rank_to,
    (params ->> 'looked_up')::bigint     as looked_up,
    (params ->> 'resolved')::bigint      as resolved,
    (params ->> 'errors')::bigint        as errors,
    (params ->> 'shopify')::bigint       as shopify
from read_json('{{ env_var('SCOUT_LAKE', '../data/private/lake') }}/_runs.jsonl',
               format = 'newline_delimited',
               columns = {'run_id': 'VARCHAR', 'dataset': 'VARCHAR', 'params': 'JSON'})
where dataset = 'web_scan'
  and coalesce(params ->> 'mode', 'full') = 'full'  -- incremental runs (mode new) are not tranches
qualify row_number() over (partition by rank_from, rank_to order by run_id desc) = 1
)
select * from t
where not exists (
    select 1 from t b
    where b.rank_from <= t.rank_from and b.rank_to >= t.rank_to
      and (b.rank_to - b.rank_from) > (t.rank_to - t.rank_from)
)
