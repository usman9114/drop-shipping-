-- Product type per product. Order: deterministic dictionary (seed
-- product_type_rules, lowest priority number wins) -> cached LLM label (seed
-- llm_product_type_cache, keyed by sha256 of the lower-cased title) -> null.
-- The LLM never runs inside dbt: scout.classify fills the cache offline.
with p as (
    select pid, lower(title) as t, sha256(lower(title)) as title_sha256
    from {{ ref('stg_cj_products') }}
),
dict as (
    select p.pid, r.product_type, r.priority
    from p join {{ ref('product_type_rules') }} r on regexp_matches(p.t, r.pattern)
    qualify row_number() over (partition by p.pid order by r.priority, r.product_type) = 1
)
select
    p.pid,
    p.title_sha256,
    coalesce(d.product_type, l.product_type) as product_type,
    case when d.product_type is not null then 'rule'
         when l.product_type is not null then 'llm:' || l.model || ':' || l.prompt_version
    end as type_method
from p
left join dict d using (pid)
left join {{ ref('llm_product_type_cache') }} l using (title_sha256)
