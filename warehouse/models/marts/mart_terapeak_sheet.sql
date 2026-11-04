-- The owner's Terapeak worklist: one row per search phrase with viable CJ
-- supply, ranked so the first ~40 rows are the best use of a 2-hour session.
-- Rank: no review flags first, then a usable main image, then more CJ
-- products behind the phrase, then the lowest price floor.
with c as (
    select *,
        coalesce(search_phrase, product_type, 'unclassified') as phrase
    from {{ ref('mart_supply_candidates') }}
    where is_viable
),
g as (
    select
        phrase                                              as search_phrase,
        min(coalesce(product_type, 'unclassified'))         as product_type,
        count(*)                                            as cj_products,
        string_agg(pid, ';' order by min_price)             as pids,
        round(min(min_price), 2)                            as price_floor_best,
        round(median(min_price), 2)                         as price_floor_median,
        string_agg(distinct review_rules, ';')              as review_flags,
        bool_and(coalesce(needs_image_review, false))       as all_need_image_review,
        bool_or(review_rules is null)                       as has_unflagged_product
    from c
    group by phrase
)
select
    row_number() over (
        order by has_unflagged_product desc, all_need_image_review, cj_products desc,
                 price_floor_best, search_phrase
    ) as priority,
    *
from g
order by priority
