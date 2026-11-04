-- One row per profiled Shopify store: the evidence behind "best" and the story.
-- Private (store domains). "Best" = traffic rank, rank growth, release rhythm and
-- marketing stack, each as a percentile among profiled stores, then weighted.
with deep as (select * from {{ ref('stg_web_store_deep') }}),
meta as (select * from {{ ref('stg_web_meta') }}),
scan as (select * from {{ ref('stg_web_scan') }}),
ranks as (
    select domain,
           arg_min(tranco_rank, list_date) as rank_earliest,
           min(list_date)                  as rank_earliest_date,
           count(*)                        as rank_points
    from {{ ref('stg_web_ranks') }}
    group by domain
),
-- Shop ids are sequential: the earliest oldest-product date among stores with an
-- id at least as high bounds when a store existed (lower envelope).
age as (
    select m.domain,
           min(d.oldest_created) over (order by m.shop_id desc
                                       rows between unbounded preceding and current row)
               as existed_by
    from meta m join deep d using (domain)
    where m.shop_id is not null and d.oldest_created is not null
),
base as (
    select
        d.domain,
        coalesce(s.tranco_rank, d.tranco_rank)                as tranco_rank,
        r.rank_earliest,
        r.rank_earliest_date,
        case when r.rank_earliest is not null
             then round(ln(r.rank_earliest::double / coalesce(s.tranco_rank, d.tranco_rank)), 3)
        end                                                   as rank_growth_log,
        m.country, m.province, m.currency, m.ships_to_us, m.ships_to_count,
        m.published_products, m.published_collections, m.installments, m.shop_id,
        least(a.existed_by, d.oldest_created)                 as existed_by,
        d.* exclude (domain, tranco_rank, error, feed_allowed, feed_status),
        list_filter(d.traffic_tags, lambda t: t in (
            'meta_pixel','tiktok_pixel','google_ads','pinterest_tag','snap_pixel',
            'microsoft_ads','reddit_pixel')) as paid_ads,
        list_filter(d.traffic_tags, lambda t: t in (
            'klaviyo_email','sms_marketing','loyalty_program','subscriptions')) as retention,
        list_filter(d.traffic_tags, lambda t: t in (
            'affiliate_program','influencer_app')) as partners,
        list_filter(d.traffic_tags, lambda t: t in (
            'reviews_app','bnpl','upsell_app','chat_support')) as conversion
    from deep d
    left join meta m using (domain)
    left join scan s using (domain)
    left join ranks r using (domain)
    left join age a using (domain)
    where d.products_sampled > 0
      -- US market in dollars (same rule as scout.stores.us_store)
      and m.currency = 'USD' and (m.country = 'US' or m.ships_to_us)
),
scored as (
    select *,
        len(paid_ads) + len(retention) + len(partners) + len(conversion)
            + len(list_filter(dns_signals, lambda x: x in ('meta_business','tiktok','pinterest','klaviyo')))
            as stack_breadth,
        1 - percent_rank() over (order by tranco_rank)                       as pct_traffic,
        percent_rank() over (order by coalesce(rank_growth_log, 0))          as pct_growth,
        percent_rank() over (order by coalesce(added_90d, 0))                as pct_rhythm
    from base
)
select *,
    percent_rank() over (order by stack_breadth) as pct_stack,
    round(0.45 * pct_traffic + 0.20 * pct_growth + 0.20 * pct_rhythm
          + 0.15 * percent_rank() over (order by stack_breadth), 4) as best_score,
    business_model in ('dropship', 'reseller', 'pod', 'unclear') as transferable_model
from scored
