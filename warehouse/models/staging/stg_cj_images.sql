select pid, position, url, sha256(url) as image_sha256, run_id
from {{ lake('cj_images', {'pid': 'VARCHAR', 'position': 'BIGINT', 'url': 'VARCHAR'},
             all_runs=true) }}
qualify run_id = max(run_id) over (partition by pid)
