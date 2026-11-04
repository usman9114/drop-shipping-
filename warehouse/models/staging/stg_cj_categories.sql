select category_id, level1, level2, level3, run_id
from {{ lake('cj_categories', {
    'category_id': 'VARCHAR', 'level1': 'VARCHAR', 'level2': 'VARCHAR', 'level3': 'VARCHAR'}) }}
where category_id is not null
qualify row_number() over (partition by category_id order by level3) = 1
