-- Every Shopify domain found by the Tranco + DNS scan (all tranches), best rank kept.
select domain, min(tranco_rank) as tranco_rank, any_value(a) as a_records
from {{ lake('web_scan', {'domain': 'VARCHAR', 'tranco_rank': 'BIGINT', 'a': 'VARCHAR'},
             all_runs=true) }}
where domain is not null
  and not regexp_matches(domain, '(^|\.)(shopify|myshopify|shopifycdn|shopifysvc)\.')
group by domain
