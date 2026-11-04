# Best online stores: what they sell and how they get traffic — 2026-11-04

> Step 1 (owner, 2026-11-04). Built by `make stores` (decision 0009): Tranco top 1M → DNS (Shopify IP range) → each store's own `/meta.json`, `/products.json` and homepage, robots.txt respected → `mart.mart_store_profile` → this export. **Aggregates only**: store domains stay in `data/private/`. Numbers are [data] from public machine records; business model and category are our rules (`scout/stores.py`, `warehouse/seeds/store_category_rules.csv`).

## Funnel

Scanned 1000000 Tranco domains (ranks 1–1000000, 20 tranches); 896910 resolved; **30365 on Shopify**.

| shopify_domains | meta_tried | meta_answered | us_stores | deep_tried | profiled |
|---|---|---|---|---|---|
| 30365 | 21842 | 21470 | 9440 | 266 | 258 |

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
| US | 8199 |
| GB | 1727 |
| IN | 1599 |
| DE | 1006 |
| AU | 814 |
| CA | 727 |
| HK | 681 |
| FR | 627 |
| NL | 574 |
| IT | 537 |

## Business model of every screened US store

3919 US stores screened (one page of each store's own feed); **184 are copyable** (dropship, general store, reseller, print on demand, unclear). Brand = sells its own goods (its success does not transfer to zero inventory); retailer = 10+ brands or a portfolio owner (not copyable at our scale); general = one name over many unrelated categories with permanent discounts, the dropshipper shape (a hypothesis, validated separately).

| business_model | stores | median_rank | deep |
|---|---|---|---|
| brand | 2921 | 269134 | 203 |
| retailer | 814 | 276752 | 48 |
| general | 76 | 264191 | 2 |
| reseller | 74 | 285279 | 4 |
| dropship | 23 | 239276 | 1 |
| pod | 11 | 259521 | 2 |

Deep-profiled stores only (best traffic first; `top30` = best_score ≥ 0.7):

| business_model | stores | median_rank | median_score | top30 |
|---|---|---|---|---|
| brand | 202 | 53975 | 0.49 | 16 |
| retailer | 47 | 56789 | 0.51 | 6 |
| reseller | 4 | 39634 | 0.61 | 0 |
| general | 2 | 67050 | 0.48 | 0 |
| pod | 2 | 53371 | 0.45 | 0 |
| dropship | 1 | 13916 | 0.77 | 1 |

## Categories the best stores win with

Over every screened US store, by the store's main category. `copyable_*` columns use copyable stores only. `copyable_traffic_weight` = Σ 1/rank ×10⁵ over copyable stores.

| category | stores | copyable_stores | brands | retailers | copyable_median_rank | copyable_median_entry_price | copyable_median_added_90d | copyable_share_rank_rising | copyable_traffic_weight | niche_score | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apparel | 790 | 42 | 588 | 160 | 278787 | 41.29 | 114.0 | 0.42 | 21.24 | 29.311 |  |
| home_decor | 151 | 16 | 110 | 25 | 217388 | 48.5 | 105.0 | 0.53 | 8.11 | 12.53 |  |
| jewelry_watches | 171 | 8 | 130 | 33 | 210754 | 43.49 | 54.0 | 0.33 | 8.43 | 10.495 |  |
| bags_accessories | 203 | 9 | 153 | 41 | 202180 | 42.83 | 24.0 | 0.22 | 4.19 | 3.922 |  |
| outdoor_camping | 55 | 5 | 34 | 16 | 333998 | 39.95 | 28.0 | 0.6 | 1.86 | 2.933 |  |
| phone_electronics | 191 | 7 | 154 | 30 | 369892 | 49.99 | 8.0 | 0.71 | 1.98 | 1.286 | FCC and lithium shipping rules |
| furniture | 68 | 5 | 47 | 16 | 312152 | 289.1 | 235.0 | 0.8 | 2.26 | 1.234 | freight-heavy |
| fitness_sports | 49 | 6 | 30 | 13 | 303368 | 141.48 | 24.5 | 0.4 | 2.19 | 1.038 |  |
| kitchen_dining | 84 | 5 | 65 | 14 | 290079 | 29.98 | 7.0 | 0.25 | 1.67 | 0.918 |  |
| bikes_moto_auto | 166 | 5 | 110 | 51 | 212423 | 38.49 | 9.0 | 0.0 | 2.36 | 0.661 | heavy or fitment-specific |
| other | 441 | 29 | 354 | 58 | 270122 | 79.95 | 24.0 | 0.75 | 15.33 | 0.0 | unclassified |
| food_beverage | 182 | 4 | 133 | 45 | 172702 | 16.5 | 50.5 | 0.67 | 3.09 | 0.0 | perishable, FDA food rules |
| pet | 67 | 4 | 48 | 15 | 294848 | 22.47 | 11.5 | 1.0 | 1.71 | 0.0 |  |
| swim_lingerie | 59 | 4 | 48 | 7 | 291676 | 40.29 | 108.5 | 0.0 | 1.64 | 0.0 |  |
| toys_games | 82 | 4 | 44 | 34 | 278234 | 33.5 | 163.0 | 1.0 | 3.49 | 0.0 | CPSIA if for children |
| smart_home_security | 42 | 4 | 33 | 5 | 254899 | 139.99 | 6.0 | 0.75 | 8.34 | 0.0 |  |
| skincare | 102 | 3 | 83 | 16 | 336133 | 45.0 | 99.0 | 0.67 | 1.21 | 0.0 |  |
| hobby_crafts_art | 84 | 3 | 56 | 25 | 250838 | 24.95 | 250.0 | 0.67 | 2.12 | 0.0 |  |
| bedding_bath | 50 | 2 | 41 | 7 | 286810 | 164.0 | 2.5 | 0.5 | 0.7 | 0.0 |  |
| personal_care | 24 | 2 | 18 | 4 | 302036 | 35.0 | 34.5 | 0.0 | 0.68 | 0.0 |  |
| baby_kids | 55 | 2 | 47 | 6 | 218533 | 30.19 | 0.0 | 1.0 | 0.92 | 0.0 | CPSIA testing and certificates |
| nails | 25 | 2 | 21 | 2 | 300728 | 14.47 | 117.0 | 0.0 | 0.69 | 0.0 |  |
| footwear | 106 | 2 | 90 | 14 | 419808 | 129.0 | 82.0 | 0.5 | 0.52 | 0.0 |  |
| beauty_cosmetics | 58 | 2 | 50 | 6 | 294964 | 193.27 | 70.5 | 0.0 | 0.75 | 0.0 |  |
| maker_3d_laser | 26 | 1 | 22 | 3 | 240178 | 2377.5 | 3.0 | 1.0 | 0.42 | 0.0 |  |
| office_paper | 23 | 1 | 22 | 0 | 561861 | 59.5 | 65.0 | 1.0 | 0.18 | 0.0 |  |
| music_instruments | 34 | 1 | 19 | 14 | 208408 | 4.99 | 250.0 | 1.0 | 0.48 | 0.0 | heavy, brand-led |
| party_seasonal | 36 | 1 | 25 | 10 | 351574 | 26.99 | 1.0 | 0.0 | 0.28 | 0.0 |  |
| cleaning_household | 24 | 1 | 17 | 6 | 290188 | 49.95 | 7.0 | 1.0 | 0.34 | 0.0 |  |
| health_supplements | 110 | 1 | 94 | 15 | 292912 | 79.48 | 14.0 | 1.0 | 0.34 | 0.0 | FDA/FTC claims, eBay restrictions |
| haircare | 56 | 1 | 49 | 6 | 244847 | 69.99 | 16.0 | 1.0 | 0.41 | 0.0 |  |
| garden_tools | 95 | 1 | 66 | 28 | 358162 | 42.99 | 5.0 | 1.0 | 0.28 | 0.0 |  |
| books_media | 117 | 1 | 59 | 57 | 248779 | 9.0 | 241.0 | 1.0 | 0.4 | 0.0 | publisher supply, thin margins |
| fragrance | 47 | 0 | 27 | 20 | – | – | – | – | – | 0.0 |  |
| audio_pro | 25 | 0 | 17 | 8 | – | – | – | – | – | 0.0 |  |
| adult_vape_flagged | 16 | 0 | 12 | 4 | – | – | – | – | – | 0.0 | restricted on eBay |

## How they get traffic

Homepage code (share of deep-profiled stores, and of the top 30%; deep profiles favour the highest-traffic stores, so this describes the strongest stores, not the copyable ones):

| tag | share_all | share_top30 |
|---|---|---|
| shopify_web_pixels | 0.94 | 0.87 |
| meta_pixel | 0.5 | 0.74 |
| klaviyo_email | 0.59 | 0.7 |
| google_ads | 0.67 | 0.65 |
| reviews_app | 0.64 | 0.65 |
| bnpl | 0.39 | 0.57 |
| tiktok_pixel | 0.35 | 0.48 |
| chat_support | 0.34 | 0.35 |
| microsoft_ads | 0.23 | 0.35 |
| sms_marketing | 0.19 | 0.3 |
| google_analytics | 0.23 | 0.22 |
| affiliate_program | 0.19 | 0.22 |
| influencer_app | 0.1 | 0.17 |
| upsell_app | 0.24 | 0.09 |
| loyalty_program | 0.14 | 0.09 |
| subscriptions | 0.09 | 0.09 |
| pinterest_tag | 0.05 | 0.09 |
| reddit_pixel | 0.04 | 0.04 |
| pod_app | 0.05 | 0.0 |
| amazon_link | 0.02 | 0.0 |
| snap_pixel | 0.01 | 0.0 |
| dropship_app | 0.0 | 0.0 |

DNS verification and email records:

| sig | share |
|---|---|
| google_search_console | 0.91 |
| klaviyo | 0.59 |
| microsoft | 0.45 |
| apple | 0.4 |
| meta_business | 0.4 |
| google_workspace | 0.36 |
| microsoft_365 | 0.31 |
| mailgun | 0.17 |
| shopify_email | 0.17 |
| sendgrid | 0.14 |
| mailchimp | 0.07 |
| pinterest | 0.05 |
| zoho | 0.04 |
| tiktok | 0.02 |

Per category (share of deep-profiled stores with each channel; `deep_stores` is the sample size, read small samples with care):

| category | share_meta_pixel | share_tiktok_pixel | share_google_ads | share_klaviyo | share_sms | share_affiliate_influencer | share_reviews_app | avg_discount_share |
|---|---|---|---|---|---|---|---|---|
| apparel | 0.54 | 0.41 | 0.66 | 0.63 | 0.23 | 0.2 | 0.7 | 0.28 |
| home_decor | 0.73 | 0.55 | 0.82 | 0.82 | 0.0 | 0.09 | 0.91 | 0.29 |
| jewelry_watches | 0.57 | 0.43 | 0.71 | 0.64 | 0.14 | 0.5 | 0.79 | 0.28 |
| bags_accessories | 0.5 | 0.4 | 0.55 | 0.5 | 0.15 | 0.25 | 0.4 | 0.32 |
| outdoor_camping | 0.75 | 0.25 | 1.0 | 0.5 | 0.0 | 0.5 | 0.75 | 0.24 |
| phone_electronics | 0.33 | 0.33 | 0.58 | 0.5 | 0.25 | 0.33 | 0.58 | 0.25 |
| furniture | 0.5 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 1.0 | 0.1 |
| fitness_sports | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 0.06 |
| kitchen_dining | 0.8 | 0.4 | 0.8 | 0.6 | 0.2 | 0.2 | 0.6 | 0.07 |
| bikes_moto_auto | 0.5 | 0.5 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.12 |
| other | 0.39 | 0.14 | 0.71 | 0.39 | 0.07 | 0.29 | 0.46 | 0.21 |
| food_beverage | 0.5 | 0.33 | 0.5 | 0.33 | 0.0 | 0.17 | 0.17 | 0.25 |
| pet | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.19 |
| swim_lingerie | 0.5 | 0.5 | 0.5 | 0.0 | 1.0 | 0.5 | 0.5 | 0.43 |
| toys_games | 0.5 | 0.17 | 0.83 | 0.83 | 0.0 | 0.17 | 0.67 | 0.33 |
| smart_home_security | 0.89 | 0.33 | 1.0 | 0.78 | 0.0 | 0.33 | 0.44 | 0.31 |
| skincare | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.75 | 0.3 |
| hobby_crafts_art | 1.0 | 0.33 | 0.33 | 0.67 | 0.0 | 0.0 | 0.67 | 0.33 |
| bedding_bath | 0.2 | 0.4 | 0.6 | 0.4 | 0.4 | 0.2 | 0.8 | 0.24 |
| personal_care | 0.5 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 0.5 | 0.33 |
| baby_kids | 0.5 | 0.25 | 0.75 | 0.75 | 0.25 | 0.25 | 0.5 | 0.17 |
| nails | 1.0 | 0.5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.2 |
| footwear | 0.3 | 0.5 | 0.3 | 0.5 | 0.5 | 0.2 | 0.9 | 0.33 |
| beauty_cosmetics | 0.33 | 0.33 | 0.56 | 0.67 | 0.33 | 0.22 | 0.78 | 0.19 |
| maker_3d_laser | 0.67 | 0.33 | 1.0 | 1.0 | 0.0 | 0.67 | 0.67 | 0.19 |
| office_paper | 0.0 | 0.0 | 0.33 | 1.0 | 0.0 | 0.0 | 0.33 | 0.01 |
| music_instruments | 0.0 | 0.33 | 0.33 | 0.33 | 0.0 | 0.0 | 1.0 | 0.02 |
| party_seasonal | 0.67 | 0.33 | 0.67 | 0.33 | 0.67 | 0.0 | 1.0 | 0.22 |
| cleaning_household | 0.0 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 | 0.43 |
| health_supplements | 0.4 | 0.4 | 0.8 | 0.8 | 0.2 | 0.8 | 0.6 | 0.55 |
| haircare | 0.5 | 1.0 | 1.0 | 1.0 | 0.5 | 1.0 | 1.0 | 0.18 |
| garden_tools | 0.29 | 0.43 | 0.43 | 0.57 | 0.29 | 0.29 | 0.86 | 0.09 |
| books_media | 0.67 | 0.11 | 0.78 | 0.44 | 0.22 | 0.11 | 0.33 | 0.07 |
| fragrance | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 | 0.46 |
| audio_pro | 0.67 | 0.33 | 0.67 | 0.67 | 0.0 | 0.33 | 0.67 | 0.15 |
| adult_vape_flagged | – | – | – | – | – | – | – | – |

## Niche shortlist for step 2 (sourcing)

Score = copyable_traffic_weight × (0.5 + rising share) × (0.5 + rhythm) × price fit (entry price 12–80) × review discount; needs at least 5 copyable stores. Excluded: non_product (not a physical product), food_beverage (perishable, FDA food rules), health_supplements (FDA/FTC claims, eBay restrictions), adult_vape_flagged (restricted on eBay), baby_kids (CPSIA testing and certificates), books_media (publisher supply, thin margins), other (unclassified). File: `docs/shortlists/2026-11-04-niche-candidates.csv`.

| category | niche_score | copyable_stores | copyable_median_entry_price | copyable_median_added_90d | copyable_share_rank_rising | note | example_types |
|---|---|---|---|---|---|---|---|
| apparel | 29.311 | 42 | 41.29 | 114.0 | 0.42 |  |  |
| home_decor | 12.53 | 16 | 48.5 | 105.0 | 0.53 |  |  |
| jewelry_watches | 10.495 | 8 | 43.49 | 54.0 | 0.33 |  |  |
| bags_accessories | 3.922 | 9 | 42.83 | 24.0 | 0.22 |  |  |
| outdoor_camping | 2.933 | 5 | 39.95 | 28.0 | 0.6 |  |  |
| phone_electronics | 1.286 | 7 | 49.99 | 8.0 | 0.71 | FCC and lithium shipping rules |  |
| furniture | 1.234 | 5 | 289.1 | 235.0 | 0.8 | freight-heavy |  |
| fitness_sports | 1.038 | 6 | 141.48 | 24.5 | 0.4 |  |  |
