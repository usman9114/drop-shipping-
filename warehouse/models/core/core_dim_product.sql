-- Conformed product: listing + category + rule outcome + product type.
with flags as (
    select
        pid,
        bool_or(action = 'exclude')                                           as is_excluded,
        string_agg(case when action = 'exclude' then rule_id end, ',' order by rule_id) as exclude_rules,
        string_agg(case when action = 'review'  then rule_id end, ',' order by rule_id) as review_rules
    from {{ ref('enr_product_flags') }}
    group by pid
)
select
    p.pid, p.title, p.sku, p.cost_low, p.cost_high, p.us_stock, p.listed_num,
    c.level1, c.level2, c.level3,
    t.product_type, t.type_method, t.search_phrase,
    coalesce(f.is_excluded, false) as is_excluded,
    f.exclude_rules, f.review_rules,
    p.run_id
from {{ ref('stg_cj_products') }} p
left join {{ ref('stg_cj_categories') }} c using (category_id)
left join flags f using (pid)
left join {{ ref('enr_product_type') }} t using (pid)
