-- Products worth a detail/stock/freight pull: not excluded by any rule, cheap
-- enough before freight, enough US stock. Thresholds are dbt vars.
select pid
from {{ ref('core_dim_product') }}
where not is_excluded
  and cost_low <= {{ var('max_cost_prefilter') }}
  and us_stock >= {{ var('min_us_stock') }}
order by pid
