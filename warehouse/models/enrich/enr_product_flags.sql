-- One row per product x fired rule. Rules live in seeds (rules.*), versioned in git.
with p as (
    select p.pid, lower(p.title) as t, c.level1, c.level2, c.level3
    from {{ ref('stg_cj_products') }} p
    left join {{ ref('stg_cj_categories') }} c using (category_id)
)
select p.pid, r.rule_id, r.action, r.reason, 'category_rule' as method
from p
join {{ ref('rule_category') }} r
  on p.level1 = r.level1
 and (coalesce(r.level2, '') = '' or p.level2 = r.level2)
 and (coalesce(r.level3, '') = '' or p.level3 = r.level3)
union all
select p.pid, r.rule_id, r.action, r.reason, 'title_rule' as method
from p
join {{ ref('rule_title') }} r on regexp_matches(p.t, r.pattern)
union all
select p.pid, 'cat_unmapped' as rule_id, 'review' as action,
       'CJ category id not in the category tree' as reason, 'category_rule' as method
from p
where p.level1 is null
