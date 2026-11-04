-- The owner's manual Terapeak readings (data/observations/*.csv), one row per
-- filled search. Unfilled rows and old template rows are dropped. These are the
-- owner's own notes from eBay's seller tool, not eBay API data (decision 0004).
with raw as (
    select *
    from read_csv('{{ env_var("SCOUT_OBS", "../data/observations") }}/*.csv',
                  union_by_name = true, all_varchar = true, filename = true)
)
select
    lower(trim(search_phrase))                       as search_phrase,
    lower(trim(product_type))                        as product_type,
    try_cast(date as date)                           as observed_on,
    try_cast(sold_count_90d as integer)              as sold_count_90d,
    try_cast(avg_sold_price as double)               as avg_sold_price,
    try_cast(active_listings as integer)             as active_listings,
    try_cast(sell_through_pct as double)             as sell_through_pct,
    try_cast(sellers_with_20plus_sales as integer)   as sellers_with_20plus_sales,
    filename                                         as source_file
from raw
where try_cast(sold_count_90d as integer) is not null
