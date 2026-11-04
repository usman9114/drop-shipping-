# Best online stores: what they sell and how they get traffic — 2026-11-04

> Step 1 (owner, 2026-11-04). Built by `make stores` (decision 0009): Tranco top 1M → DNS (Shopify IP range) → each store's own `/meta.json`, `/products.json` and homepage, robots.txt respected → `mart.mart_store_profile` → this export. **Aggregates only**: store domains stay in `data/private/`. Numbers are [data] from public machine records; business model and category are our rules (`scout/stores.py`, `warehouse/seeds/store_category_rules.csv`).

## Funnel

Scanned 1000000 Tranco domains (ranks 1–1000000, 20 tranches); 896910 resolved; **30365 on Shopify**.

| shopify_domains | meta_tried | meta_answered | us_stores | deep_tried | profiled |
|---|---|---|---|---|---|
| 30365 | 29084 | 28417 | 11172 | 296 | 288 |

Shopify stores by traffic band:

| band | shopify_stores |
|---|---|
| 1-10k | 10 |
| 10k-100k | 906 |
| 100k-300k | 4085 |
| 300k-1M | 25364 |

Store country (from `/meta.json`), top 10:

| country | stores |
|---|---|
| US | 9671 |
| IN | 2902 |
| GB | 2106 |
| DE | 1205 |
| AU | 992 |
| CA | 905 |
| HK | 848 |
| FR | 826 |
| PK | 810 |
| NL | 755 |

## Business model of every screened US store

8203 US stores screened (one page of each store's own feed); **371 are copyable** (dropship, general store, reseller, print on demand, unclear). Brand = sells its own goods (its success does not transfer to zero inventory); retailer = 10+ brands or a portfolio owner (not copyable at our scale); general = one name over many unrelated categories with permanent discounts, the dropshipper shape (a hypothesis, validated separately).

| business_model | stores | median_rank | deep |
|---|---|---|---|
| brand | 6108 | 410715 | 213 |
| retailer | 1724 | 416192 | 53 |
| general | 146 | 408724 | 7 |
| reseller | 132 | 398686 | 7 |
| dropship | 62 | 487876 | 6 |
| pod | 31 | 477060 | 4 |

Deep-profiled stores only (best traffic first; `top30` = best_score ≥ 0.7):

| business_model | stores | median_rank | median_score | top30 |
|---|---|---|---|---|
| brand | 212 | 55318 | 0.5 | 16 |
| retailer | 52 | 58594 | 0.57 | 7 |
| reseller | 7 | 41431 | 0.55 | 0 |
| general | 7 | 135633 | 0.4 | 0 |
| dropship | 6 | 144094 | 0.31 | 1 |
| pod | 4 | 95010 | 0.38 | 0 |

## Categories the best stores win with

Over every screened US store, by the store's main category. `copyable_*` columns use copyable stores only. `copyable_traffic_weight` = Σ 1/rank ×10⁵ over copyable stores.

| category | stores | copyable_stores | brands | retailers | copyable_median_rank | copyable_median_entry_price | copyable_median_added_90d | copyable_share_rank_rising | copyable_traffic_weight | niche_score | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apparel | 1577 | 81 | 1156 | 340 | 414000 | 39.99 | 78.0 | 0.62 | 26.73 | 44.906 |  |
| jewelry_watches | 405 | 17 | 325 | 63 | 394096 | 53.0 | 29.0 | 0.65 | 10.21 | 17.221 |  |
| home_decor | 325 | 31 | 230 | 64 | 412606 | 39.95 | 92.0 | 0.71 | 9.27 | 16.825 |  |
| toys_games | 190 | 8 | 112 | 70 | 454216 | 32.48 | 65.5 | 0.63 | 4.17 | 4.948 | CPSIA if for children |
| bikes_moto_auto | 395 | 14 | 268 | 113 | 514777 | 44.24 | 32.0 | 0.71 | 3.59 | 4.561 | heavy or fitment-specific |
| hobby_crafts_art | 217 | 8 | 157 | 52 | 486839 | 36.48 | 18.5 | 0.75 | 3.0 | 4.188 |  |
| pet | 122 | 8 | 86 | 28 | 441011 | 33.58 | 107.0 | 0.88 | 1.95 | 4.037 |  |
| bags_accessories | 426 | 17 | 325 | 84 | 521770 | 38.74 | 10.0 | 0.65 | 4.18 | 4.006 |  |
| swim_lingerie | 115 | 8 | 90 | 17 | 498628 | 40.29 | 108.5 | 0.5 | 2.24 | 3.36 |  |
| phone_electronics | 354 | 17 | 274 | 63 | 412517 | 44.49 | 11.0 | 0.59 | 3.98 | 2.632 | FCC and lithium shipping rules |
| smart_home_security | 79 | 6 | 63 | 10 | 269306 | 139.99 | 6.0 | 0.5 | 8.71 | 2.439 |  |
| outdoor_camping | 119 | 9 | 76 | 34 | 344133 | 123.84 | 28.0 | 0.89 | 3.05 | 2.431 |  |
| skincare | 208 | 6 | 172 | 30 | 545556 | 36.7 | 45.5 | 0.67 | 1.26 | 2.211 |  |
| fitness_sports | 111 | 10 | 71 | 30 | 371975 | 89.99 | 37.5 | 0.6 | 3.0 | 1.98 |  |
| kitchen_dining | 166 | 9 | 125 | 32 | 381628 | 29.98 | 10.0 | 0.44 | 2.43 | 1.903 |  |
| garden_tools | 188 | 5 | 127 | 56 | 521067 | 29.99 | 25.0 | 0.6 | 1.04 | 1.525 |  |
| furniture | 192 | 12 | 136 | 44 | 508498 | 490.56 | 132.5 | 0.67 | 2.75 | 1.351 | freight-heavy |
| bedding_bath | 104 | 5 | 82 | 17 | 411862 | 78.0 | 3.0 | 0.8 | 1.3 | 1.014 |  |
| footwear | 230 | 6 | 184 | 40 | 590572 | 110.0 | 10.5 | 0.6 | 1.16 | 0.434 |  |
| other | 1033 | 58 | 834 | 141 | 423276 | 59.0 | 15.5 | 0.53 | 18.24 | 0.0 | unclassified |
| food_beverage | 348 | 10 | 248 | 90 | 442249 | 19.95 | 33.5 | 0.7 | 4.28 | 0.0 | perishable, FDA food rules |
| books_media | 209 | 4 | 107 | 98 | 507518 | 24.99 | 120.5 | 1.0 | 0.97 | 0.0 | publisher supply, thin margins |
| health_supplements | 209 | 3 | 182 | 24 | 514011 | 33.32 | 1.0 | 0.33 | 0.69 | 0.0 | FDA/FTC claims, eBay restrictions |
| baby_kids | 112 | 3 | 91 | 18 | 226934 | 30.95 | 0.0 | 1.0 | 1.07 | 0.0 | CPSIA testing and certificates |
| party_seasonal | 80 | 2 | 59 | 19 | 465108 | 26.24 | 125.5 | 0.5 | 0.46 | 0.0 |  |
| beauty_cosmetics | 105 | 2 | 92 | 11 | 294964 | 193.27 | 70.5 | 0.5 | 0.75 | 0.0 |  |
| nails | 47 | 2 | 41 | 4 | 300728 | 14.47 | 117.0 | 0.0 | 0.69 | 0.0 |  |
| haircare | 109 | 2 | 90 | 17 | 324665 | 64.0 | 10.0 | 0.5 | 0.66 | 0.0 |  |
| personal_care | 40 | 2 | 31 | 7 | 302036 | 35.0 | 34.5 | 0.5 | 0.68 | 0.0 |  |
| music_instruments | 53 | 2 | 26 | 25 | 434983 | 202.0 | 250.0 | 1.0 | 0.63 | 0.0 | heavy, brand-led |
| maker_3d_laser | 52 | 2 | 44 | 6 | 366895 | 1197.24 | 7.0 | 1.0 | 0.62 | 0.0 |  |
| cleaning_household | 49 | 1 | 38 | 10 | 290188 | 49.95 | 7.0 | 0.0 | 0.34 | 0.0 |  |
| office_paper | 41 | 1 | 38 | 2 | 561861 | 59.5 | 65.0 | 1.0 | 0.18 | 0.0 |  |
| audio_pro | 48 | 0 | 33 | 15 | – | – | – | – | – | 0.0 |  |
| adult_vape_flagged | 34 | 0 | 24 | 10 | – | – | – | – | – | 0.0 | restricted on eBay |
| fragrance | 104 | 0 | 64 | 40 | – | – | – | – | – | 0.0 |  |

## Who is moving: rank history of the copyable stores

From 26 Tranco list dates over 2 years (`mart_store_rank_trend`, `[proxy]`: rank is popularity, not visits). **Emerged** = absent from every list older than 9 months, now inside the top 500k; **risers** = rank at least 2x better than their older level; **fading** = at least 2x worse. Categories with fewer than 5 copyable stores are left out.

| category | copyable_stores | emerged | risers | fading | median_volatility |
|---|---|---|---|---|---|
| apparel | 81 | 3 | 2 | 4 | 0.21 |
| jewelry_watches | 17 | 3 | 1 | 1 | 0.25 |
| home_decor | 31 | 2 | 2 | 2 | 0.27 |
| other | 58 | 1 | 2 | 0 | 0.2 |
| phone_electronics | 17 | 0 | 2 | 2 | 0.23 |
| hobby_crafts_art | 8 | 0 | 2 | 0 | 0.21 |
| smart_home_security | 6 | 1 | 0 | 0 | 0.22 |
| pet | 8 | 0 | 1 | 0 | 0.27 |
| toys_games | 8 | 0 | 1 | 1 | 0.32 |
| bags_accessories | 17 | 1 | 0 | 0 | 0.18 |
| furniture | 12 | 1 | 0 | 0 | 0.19 |
| bikes_moto_auto | 14 | 1 | 0 | 0 | 0.17 |
| swim_lingerie | 8 | 1 | 0 | 0 | 0.23 |
| fitness_sports | 10 | 1 | 0 | 0 | 0.22 |
| outdoor_camping | 9 | 0 | 1 | 0 | 0.22 |
| food_beverage | 10 | 1 | 0 | 0 | 0.17 |
| kitchen_dining | 9 | 0 | 0 | 2 | 0.17 |
| bedding_bath | 5 | 0 | 0 | 0 | 0.22 |
| skincare | 6 | 0 | 0 | 0 | 0.18 |
| garden_tools | 5 | 0 | 0 | 0 | 0.21 |
| footwear | 6 | 0 | 0 | 1 | 0.25 |

## How they get traffic

Homepage code (share of deep-profiled stores, and of the top 30%; deep profiles favour the highest-traffic stores, so this describes the strongest stores, not the copyable ones):

| tag | share_all | share_top30 |
|---|---|---|
| shopify_web_pixels | 0.94 | 0.92 |
| google_ads | 0.68 | 0.71 |
| meta_pixel | 0.51 | 0.71 |
| klaviyo_email | 0.57 | 0.67 |
| reviews_app | 0.65 | 0.54 |
| tiktok_pixel | 0.37 | 0.46 |
| bnpl | 0.37 | 0.42 |
| chat_support | 0.34 | 0.38 |
| microsoft_ads | 0.24 | 0.38 |
| sms_marketing | 0.17 | 0.38 |
| google_analytics | 0.22 | 0.29 |
| affiliate_program | 0.19 | 0.17 |
| subscriptions | 0.1 | 0.17 |
| influencer_app | 0.09 | 0.17 |
| upsell_app | 0.24 | 0.13 |
| loyalty_program | 0.14 | 0.08 |
| pinterest_tag | 0.06 | 0.08 |
| reddit_pixel | 0.03 | 0.04 |
| pod_app | 0.06 | 0.0 |
| snap_pixel | 0.01 | 0.0 |
| amazon_link | 0.01 | 0.0 |
| dropship_app | 0.0 | 0.0 |

DNS verification and email records:

| sig | share |
|---|---|
| google_search_console | 0.9 |
| klaviyo | 0.57 |
| microsoft | 0.43 |
| meta_business | 0.39 |
| apple | 0.38 |
| google_workspace | 0.35 |
| microsoft_365 | 0.31 |
| shopify_email | 0.18 |
| mailgun | 0.18 |
| sendgrid | 0.14 |
| mailchimp | 0.07 |
| zoho | 0.05 |
| pinterest | 0.05 |
| tiktok | 0.01 |

Per category (share of deep-profiled stores with each channel; `deep_stores` is the sample size, read small samples with care):

| category | share_meta_pixel | share_tiktok_pixel | share_google_ads | share_klaviyo | share_sms | share_affiliate_influencer | share_reviews_app | avg_discount_share |
|---|---|---|---|---|---|---|---|---|
| apparel | 0.57 | 0.43 | 0.68 | 0.59 | 0.21 | 0.21 | 0.73 | 0.29 |
| jewelry_watches | 0.53 | 0.4 | 0.67 | 0.6 | 0.13 | 0.47 | 0.73 | 0.27 |
| home_decor | 0.73 | 0.67 | 0.87 | 0.73 | 0.0 | 0.13 | 0.87 | 0.36 |
| toys_games | 0.5 | 0.17 | 0.83 | 0.83 | 0.0 | 0.17 | 0.67 | 0.33 |
| bikes_moto_auto | 0.33 | 0.33 | 1.0 | 1.0 | 0.0 | 0.0 | 0.33 | 0.22 |
| hobby_crafts_art | 1.0 | 0.33 | 0.33 | 0.67 | 0.0 | 0.0 | 0.67 | 0.33 |
| pet | 0.33 | 0.67 | 0.67 | 0.33 | 0.0 | 0.0 | 1.0 | 0.41 |
| bags_accessories | 0.54 | 0.33 | 0.58 | 0.5 | 0.13 | 0.25 | 0.5 | 0.34 |
| swim_lingerie | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.25 | 0.5 | 0.46 |
| phone_electronics | 0.33 | 0.33 | 0.58 | 0.5 | 0.25 | 0.33 | 0.58 | 0.25 |
| smart_home_security | 0.89 | 0.33 | 1.0 | 0.78 | 0.0 | 0.33 | 0.44 | 0.31 |
| outdoor_camping | 0.6 | 0.4 | 1.0 | 0.6 | 0.0 | 0.6 | 0.8 | 0.39 |
| skincare | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.75 | 0.3 |
| fitness_sports | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 0.06 |
| kitchen_dining | 0.8 | 0.4 | 0.8 | 0.6 | 0.2 | 0.2 | 0.6 | 0.07 |
| garden_tools | 0.29 | 0.43 | 0.43 | 0.57 | 0.29 | 0.29 | 0.86 | 0.09 |
| furniture | 0.5 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 1.0 | 0.1 |
| bedding_bath | 0.2 | 0.4 | 0.6 | 0.4 | 0.4 | 0.2 | 0.8 | 0.24 |
| footwear | 0.3 | 0.5 | 0.3 | 0.5 | 0.5 | 0.2 | 0.9 | 0.33 |
| other | 0.42 | 0.21 | 0.73 | 0.42 | 0.06 | 0.3 | 0.45 | 0.25 |
| food_beverage | 0.38 | 0.38 | 0.63 | 0.38 | 0.0 | 0.13 | 0.25 | 0.19 |
| books_media | 0.67 | 0.11 | 0.78 | 0.44 | 0.22 | 0.11 | 0.33 | 0.07 |
| health_supplements | 0.4 | 0.4 | 0.8 | 0.8 | 0.2 | 0.8 | 0.6 | 0.55 |
| baby_kids | 0.5 | 0.25 | 0.75 | 0.75 | 0.25 | 0.25 | 0.5 | 0.17 |
| party_seasonal | 0.67 | 0.33 | 0.67 | 0.33 | 0.67 | 0.0 | 1.0 | 0.22 |
| beauty_cosmetics | 0.33 | 0.33 | 0.56 | 0.67 | 0.33 | 0.22 | 0.78 | 0.19 |
| nails | 1.0 | 0.5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.2 |
| haircare | 0.5 | 1.0 | 1.0 | 1.0 | 0.5 | 1.0 | 1.0 | 0.18 |
| personal_care | 0.5 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 0.5 | 0.33 |
| music_instruments | 0.0 | 0.33 | 0.33 | 0.33 | 0.0 | 0.0 | 1.0 | 0.02 |
| maker_3d_laser | 0.67 | 0.33 | 1.0 | 1.0 | 0.0 | 0.67 | 0.67 | 0.19 |
| cleaning_household | 0.0 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 | 0.43 |
| office_paper | 0.0 | 0.0 | 0.33 | 1.0 | 0.0 | 0.0 | 0.33 | 0.01 |
| audio_pro | 0.67 | 0.33 | 0.67 | 0.67 | 0.0 | 0.33 | 0.67 | 0.15 |
| adult_vape_flagged | – | – | – | – | – | – | – | – |
| fragrance | 0.5 | 1.0 | 1.0 | 0.5 | 0.0 | 0.5 | 1.0 | 0.37 |

## Niche shortlist for step 2 (sourcing)

Score = copyable_traffic_weight × (0.5 + rising share) × (0.5 + rhythm) × price fit (entry price 12–80) × review discount; needs at least 5 copyable stores. Excluded: non_product (not a physical product), food_beverage (perishable, FDA food rules), health_supplements (FDA/FTC claims, eBay restrictions), adult_vape_flagged (restricted on eBay), baby_kids (CPSIA testing and certificates), books_media (publisher supply, thin margins), other (unclassified). File: `docs/shortlists/2026-11-04-niche-candidates.csv`.

| category | niche_score | copyable_stores | copyable_median_entry_price | copyable_median_added_90d | copyable_share_rank_rising | note | example_types |
|---|---|---|---|---|---|---|---|
| apparel | 44.906 | 81 | 39.99 | 78.0 | 0.62 |  | t-shirts |
| jewelry_watches | 17.221 | 17 | 53.0 | 29.0 | 0.65 |  |  |
| home_decor | 16.825 | 31 | 39.95 | 92.0 | 0.71 |  |  |
| toys_games | 4.948 | 8 | 32.48 | 65.5 | 0.63 | CPSIA if for children |  |
| bikes_moto_auto | 4.561 | 14 | 44.24 | 32.0 | 0.71 | heavy or fitment-specific |  |
| hobby_crafts_art | 4.188 | 8 | 36.48 | 18.5 | 0.75 |  |  |
| pet | 4.037 | 8 | 33.58 | 107.0 | 0.88 |  |  |
| bags_accessories | 4.006 | 17 | 38.74 | 10.0 | 0.65 |  |  |
