# Best online stores: what they sell and how they get traffic — 2026-11-11

> Step 1 (owner, 2026-11-04). Built by `make stores` (decision 0009): Tranco top 1M → DNS (Shopify IP range) → each store's own `/meta.json`, `/products.json` and homepage, robots.txt respected → `mart.mart_store_profile` → this export. **Aggregates only**: store domains stay in `data/private/`. Numbers are [data] from public machine records; business model and category are our rules (`scout/stores.py`, `warehouse/seeds/store_category_rules.csv`).

## Funnel

No full-scan tranches in this lake (incremental discovery only); **30365 on Shopify**.

| shopify_domains | meta_tried | meta_answered | us_stores | deep_tried | profiled |
|---|---|---|---|---|---|
| 30365 | 30245 | 29852 | 11754 | 437 | 429 |

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
| US | 10187 |
| IN | 3009 |
| GB | 2212 |
| DE | 1264 |
| AU | 1053 |
| CA | 965 |
| HK | 873 |
| FR | 866 |
| PK | 844 |
| NL | 802 |

## Business model of every screened US store

11077 US stores screened (one page of each store's own feed); **535 are copyable** (dropship, general store, reseller, print on demand, unclear). Brand = sells its own goods (its success does not transfer to zero inventory); retailer = 10+ brands or a portfolio owner (not copyable at our scale); general = one name over many unrelated categories with permanent discounts, the dropshipper shape (a hypothesis, validated separately).

| business_model | stores | median_rank | deep |
|---|---|---|---|
| brand | 8152 | 507620 | 302 |
| retailer | 2390 | 519968 | 99 |
| general | 194 | 509957 | 8 |
| reseller | 189 | 533245 | 9 |
| dropship | 105 | 639498 | 6 |
| pod | 47 | 571224 | 5 |

Deep-profiled stores only (best traffic first; `top30` = best_score ≥ 0.7):

| business_model | stores | median_rank | median_score | top30 |
|---|---|---|---|---|
| brand | 302 | 68362 | 0.5 | 24 |
| retailer | 99 | 95866 | 0.5 | 10 |
| reseller | 9 | 95343 | 0.56 | 0 |
| general | 8 | 134595 | 0.49 | 0 |
| dropship | 6 | 144094 | 0.42 | 1 |
| pod | 5 | 127427 | 0.5 | 0 |

## Categories the best stores win with

Over every screened US store, by the store's main category. `copyable_*` columns use copyable stores only. `copyable_traffic_weight` = Σ 1/rank ×10⁵ over copyable stores.

| category | stores | copyable_stores | brands | retailers | copyable_median_rank | copyable_median_entry_price | copyable_median_added_90d | copyable_share_rank_rising | copyable_traffic_weight | niche_score | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apparel | 2085 | 120 | 1511 | 454 | 554628 | 40.3 | 66.0 | 0.54 | 31.89 | 49.748 |  |
| home_decor | 447 | 39 | 320 | 88 | 471242 | 44.99 | 92.0 | 0.67 | 10.12 | 17.761 |  |
| jewelry_watches | 570 | 26 | 447 | 97 | 527460 | 51.0 | 29.0 | 0.54 | 11.3 | 17.236 |  |
| hobby_crafts_art | 308 | 10 | 217 | 81 | 571778 | 28.98 | 29.5 | 0.7 | 3.22 | 5.732 |  |
| fitness_sports | 148 | 13 | 92 | 43 | 410955 | 79.99 | 35.0 | 0.54 | 3.4 | 5.304 |  |
| toys_games | 251 | 12 | 141 | 98 | 564526 | 29.97 | 103.0 | 0.5 | 4.64 | 4.872 | CPSIA if for children |
| bags_accessories | 562 | 22 | 425 | 115 | 584618 | 34.37 | 11.0 | 0.59 | 4.75 | 4.487 |  |
| pet | 169 | 8 | 122 | 39 | 441011 | 33.58 | 107.0 | 0.88 | 1.95 | 4.037 |  |
| smart_home_security | 104 | 10 | 77 | 17 | 559502 | 119.99 | 19.0 | 0.4 | 9.17 | 3.741 |  |
| swim_lingerie | 150 | 9 | 117 | 24 | 550545 | 35.58 | 68.0 | 0.44 | 2.37 | 3.342 |  |
| phone_electronics | 442 | 20 | 334 | 88 | 415180 | 49.47 | 9.5 | 0.5 | 4.33 | 2.475 | FCC and lithium shipping rules |
| outdoor_camping | 160 | 11 | 101 | 48 | 347512 | 199.96 | 28.0 | 0.82 | 3.27 | 2.475 |  |
| kitchen_dining | 232 | 14 | 172 | 46 | 550621 | 32.03 | 8.5 | 0.43 | 3.0 | 2.186 |  |
| skincare | 269 | 11 | 222 | 36 | 690272 | 38.99 | 18.0 | 0.55 | 1.86 | 2.148 |  |
| bikes_moto_auto | 521 | 20 | 346 | 155 | 561264 | 86.75 | 32.0 | 0.6 | 4.28 | 1.977 | heavy or fitment-specific |
| garden_tools | 252 | 7 | 169 | 76 | 554058 | 29.99 | 25.0 | 0.57 | 1.29 | 1.84 |  |
| furniture | 280 | 17 | 200 | 63 | 531030 | 588.0 | 39.0 | 0.71 | 3.34 | 1.697 | freight-heavy |
| bedding_bath | 150 | 10 | 116 | 24 | 753966 | 74.0 | 3.0 | 0.6 | 1.84 | 1.214 |  |
| haircare | 146 | 6 | 117 | 23 | 653935 | 29.99 | 5.5 | 0.5 | 1.73 | 1.182 |  |
| footwear | 299 | 10 | 232 | 57 | 660354 | 97.5 | 69.5 | 0.5 | 1.69 | 1.014 |  |
| beauty_cosmetics | 135 | 5 | 117 | 13 | 920640 | 36.0 | 7.0 | 0.2 | 1.07 | 0.549 |  |
| other | 1458 | 84 | 1171 | 203 | 567918 | 74.0 | 22.0 | 0.5 | 22.13 | 0.0 | unclassified |
| food_beverage | 469 | 12 | 334 | 123 | 491873 | 34.99 | 20.5 | 0.58 | 4.52 | 0.0 | perishable, FDA food rules |
| books_media | 282 | 7 | 150 | 125 | 592408 | 29.99 | 67.0 | 0.71 | 1.32 | 0.0 | publisher supply, thin margins |
| baby_kids | 152 | 5 | 119 | 28 | 671177 | 32.0 | 0.0 | 0.8 | 1.3 | 0.0 | CPSIA testing and certificates |
| party_seasonal | 113 | 4 | 85 | 24 | 743588 | 32.48 | 130.5 | 0.25 | 0.67 | 0.0 |  |
| health_supplements | 274 | 4 | 241 | 29 | 590306 | 36.64 | 0.5 | 0.25 | 0.79 | 0.0 | FDA/FTC claims, eBay restrictions |
| music_instruments | 79 | 4 | 37 | 38 | 683442 | 157.0 | 228.5 | 0.5 | 0.89 | 0.0 | heavy, brand-led |
| cleaning_household | 70 | 3 | 51 | 16 | 909790 | 49.95 | 39.0 | 0.0 | 0.56 | 0.0 |  |
| maker_3d_laser | 73 | 3 | 62 | 8 | 493612 | 17.95 | 11.0 | 0.67 | 0.72 | 0.0 |  |
| audio_pro | 61 | 2 | 40 | 19 | 916704 | 35.98 | 5.0 | 0.5 | 0.22 | 0.0 |  |
| fragrance | 136 | 2 | 83 | 51 | 800628 | 56.5 | 2.0 | 1.0 | 0.25 | 0.0 |  |
| nails | 62 | 2 | 50 | 10 | 300728 | 14.47 | 117.0 | 0.0 | 0.69 | 0.0 |  |
| personal_care | 50 | 2 | 39 | 9 | 302036 | 35.0 | 34.5 | 0.5 | 0.68 | 0.0 |  |
| office_paper | 66 | 1 | 56 | 9 | 561861 | 59.5 | 65.0 | 1.0 | 0.18 | 0.0 |  |
| adult_vape_flagged | 45 | 0 | 32 | 13 | – | – | – | – | – | 0.0 | restricted on eBay |

## Who is moving: rank history of the copyable stores

From 26 Tranco list dates over 2 years (`mart_store_rank_trend`, `[proxy]`: rank is popularity, not visits). **Emerged** = absent from every list older than 9 months, now inside the top 500k; **risers** = rank at least 2x better than their older level; **fading** = at least 2x worse. Categories with fewer than 5 copyable stores are left out.

| category | copyable_stores | emerged | risers | fading | median_volatility |
|---|---|---|---|---|---|
| apparel | 120 | 3 | 3 | 5 | 0.2 |
| home_decor | 39 | 3 | 2 | 4 | 0.26 |
| other | 84 | 2 | 2 | 1 | 0.19 |
| jewelry_watches | 26 | 3 | 1 | 1 | 0.23 |
| baby_kids | 5 | 0 | 2 | 1 | 0.37 |
| pet | 8 | 1 | 1 | 0 | 0.29 |
| furniture | 17 | 1 | 1 | 0 | 0.2 |
| hobby_crafts_art | 10 | 0 | 2 | 0 | 0.21 |
| outdoor_camping | 11 | 0 | 2 | 0 | 0.21 |
| smart_home_security | 10 | 1 | 0 | 0 | 0.19 |
| bags_accessories | 22 | 1 | 0 | 1 | 0.19 |
| haircare | 6 | 0 | 1 | 1 | 0.31 |
| toys_games | 12 | 0 | 1 | 1 | 0.14 |
| swim_lingerie | 9 | 1 | 0 | 0 | 0.24 |
| fitness_sports | 13 | 1 | 0 | 0 | 0.2 |
| skincare | 11 | 0 | 1 | 0 | 0.17 |
| phone_electronics | 20 | 0 | 1 | 3 | 0.18 |
| beauty_cosmetics | 5 | 1 | 0 | 0 | 0.19 |
| food_beverage | 12 | 1 | 0 | 0 | 0.15 |
| books_media | 7 | 0 | 1 | 0 | 0.21 |
| bikes_moto_auto | 20 | 0 | 0 | 0 | 0.17 |
| bedding_bath | 10 | 0 | 0 | 0 | 0.18 |
| kitchen_dining | 14 | 0 | 0 | 2 | 0.18 |
| garden_tools | 7 | 0 | 0 | 0 | 0.21 |
| footwear | 10 | 0 | 0 | 2 | 0.22 |

## How they get traffic

Homepage code (share of deep-profiled stores, and of the top 30%; deep profiles favour the highest-traffic stores, so this describes the strongest stores, not the copyable ones):

| tag | share_all | share_top30 |
|---|---|---|
| shopify_web_pixels | 0.96 | 0.97 |
| google_ads | 0.74 | 0.71 |
| klaviyo_email | 0.55 | 0.69 |
| reviews_app | 0.63 | 0.66 |
| meta_pixel | 0.56 | 0.66 |
| tiktok_pixel | 0.35 | 0.54 |
| bnpl | 0.34 | 0.51 |
| microsoft_ads | 0.22 | 0.4 |
| chat_support | 0.31 | 0.37 |
| affiliate_program | 0.21 | 0.29 |
| sms_marketing | 0.14 | 0.29 |
| google_analytics | 0.24 | 0.26 |
| upsell_app | 0.23 | 0.17 |
| influencer_app | 0.07 | 0.17 |
| loyalty_program | 0.12 | 0.14 |
| subscriptions | 0.09 | 0.14 |
| pinterest_tag | 0.04 | 0.11 |
| pod_app | 0.04 | 0.03 |
| reddit_pixel | 0.03 | 0.03 |
| amazon_link | 0.02 | 0.0 |
| snap_pixel | 0.01 | 0.0 |
| dropship_app | 0.0 | 0.0 |

DNS verification and email records:

| sig | share |
|---|---|
| google_search_console | 0.85 |
| klaviyo | 0.54 |
| google_workspace | 0.34 |
| microsoft | 0.33 |
| meta_business | 0.32 |
| apple | 0.28 |
| microsoft_365 | 0.27 |
| mailgun | 0.16 |
| shopify_email | 0.15 |
| sendgrid | 0.1 |
| mailchimp | 0.06 |
| zoho | 0.05 |
| pinterest | 0.05 |
| tiktok | 0.01 |

Per category (share of deep-profiled stores with each channel; `deep_stores` is the sample size, read small samples with care):

| category | share_meta_pixel | share_tiktok_pixel | share_google_ads | share_klaviyo | share_sms | share_affiliate_influencer | share_reviews_app | avg_discount_share |
|---|---|---|---|---|---|---|---|---|
| apparel | 0.61 | 0.41 | 0.75 | 0.58 | 0.19 | 0.2 | 0.69 | 0.27 |
| home_decor | 0.74 | 0.48 | 0.78 | 0.65 | 0.0 | 0.09 | 0.74 | 0.35 |
| jewelry_watches | 0.65 | 0.43 | 0.74 | 0.52 | 0.09 | 0.39 | 0.61 | 0.26 |
| hobby_crafts_art | 0.73 | 0.27 | 0.73 | 0.64 | 0.09 | 0.36 | 0.73 | 0.46 |
| fitness_sports | 0.67 | 0.0 | 1.0 | 1.0 | 0.0 | 0.33 | 0.67 | 0.18 |
| toys_games | 0.63 | 0.38 | 0.88 | 0.88 | 0.13 | 0.25 | 0.75 | 0.26 |
| bags_accessories | 0.57 | 0.35 | 0.68 | 0.57 | 0.14 | 0.24 | 0.51 | 0.33 |
| pet | 0.4 | 0.6 | 0.8 | 0.6 | 0.0 | 0.0 | 0.8 | 0.33 |
| smart_home_security | 0.89 | 0.33 | 1.0 | 0.78 | 0.0 | 0.33 | 0.44 | 0.31 |
| swim_lingerie | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.25 | 0.5 | 0.46 |
| phone_electronics | 0.55 | 0.4 | 0.7 | 0.5 | 0.15 | 0.3 | 0.6 | 0.25 |
| outdoor_camping | 0.5 | 0.33 | 1.0 | 0.67 | 0.0 | 0.67 | 0.83 | 0.36 |
| kitchen_dining | 0.67 | 0.33 | 0.83 | 0.5 | 0.17 | 0.17 | 0.5 | 0.09 |
| skincare | 0.33 | 0.5 | 0.5 | 0.5 | 0.5 | 0.33 | 0.83 | 0.26 |
| bikes_moto_auto | 0.57 | 0.21 | 0.86 | 0.43 | 0.07 | 0.21 | 0.64 | 0.18 |
| garden_tools | 0.29 | 0.43 | 0.43 | 0.57 | 0.29 | 0.29 | 0.86 | 0.09 |
| furniture | 0.67 | 0.56 | 0.67 | 0.11 | 0.0 | 0.11 | 0.56 | 0.63 |
| bedding_bath | 0.17 | 0.33 | 0.67 | 0.33 | 0.33 | 0.17 | 0.83 | 0.2 |
| haircare | 0.75 | 1.0 | 1.0 | 1.0 | 0.5 | 1.0 | 1.0 | 0.36 |
| footwear | 0.25 | 0.42 | 0.42 | 0.5 | 0.42 | 0.25 | 0.75 | 0.28 |
| beauty_cosmetics | 0.36 | 0.27 | 0.64 | 0.73 | 0.27 | 0.18 | 0.73 | 0.21 |
| other | 0.53 | 0.22 | 0.8 | 0.38 | 0.04 | 0.33 | 0.51 | 0.26 |
| food_beverage | 0.45 | 0.27 | 0.64 | 0.45 | 0.0 | 0.09 | 0.27 | 0.14 |
| books_media | 0.67 | 0.11 | 0.78 | 0.44 | 0.22 | 0.11 | 0.33 | 0.07 |
| baby_kids | 0.6 | 0.2 | 0.8 | 0.6 | 0.2 | 0.4 | 0.6 | 0.28 |
| party_seasonal | 0.75 | 0.25 | 0.75 | 0.25 | 0.5 | 0.0 | 1.0 | 0.16 |
| health_supplements | 0.5 | 0.38 | 0.75 | 0.75 | 0.13 | 0.75 | 0.75 | 0.35 |
| music_instruments | 0.2 | 0.4 | 0.6 | 0.2 | 0.0 | 0.0 | 0.8 | 0.14 |
| cleaning_household | 0.5 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 0.5 | 0.32 |
| maker_3d_laser | 0.67 | 0.33 | 1.0 | 1.0 | 0.0 | 0.67 | 0.67 | 0.19 |
| audio_pro | 0.5 | 0.25 | 0.75 | 0.5 | 0.0 | 0.25 | 0.5 | 0.11 |
| fragrance | 0.67 | 0.67 | 1.0 | 0.33 | 0.0 | 0.33 | 1.0 | 0.31 |
| nails | 1.0 | 0.5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.2 |
| personal_care | 0.5 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 0.5 | 0.33 |
| office_paper | 0.29 | 0.14 | 0.43 | 0.86 | 0.0 | 0.14 | 0.57 | 0.12 |
| adult_vape_flagged | – | – | – | – | – | – | – | – |

## Niche shortlist for step 2 (sourcing)

Score = copyable_traffic_weight × (0.5 + rising share) × (0.5 + rhythm) × price fit (entry price 12–80) × review discount; needs at least 5 copyable stores. Excluded: non_product (not a physical product), food_beverage (perishable, FDA food rules), health_supplements (FDA/FTC claims, eBay restrictions), adult_vape_flagged (restricted on eBay), baby_kids (CPSIA testing and certificates), books_media (publisher supply, thin margins), other (unclassified). File: `docs/shortlists/2026-11-11-niche-candidates.csv`.

| category | niche_score | copyable_stores | copyable_median_entry_price | copyable_median_added_90d | copyable_share_rank_rising | note | example_types |
|---|---|---|---|---|---|---|---|
| apparel | 49.748 | 120 | 40.3 | 66.0 | 0.54 |  | t-shirts |
| home_decor | 17.761 | 39 | 44.99 | 92.0 | 0.67 |  |  |
| jewelry_watches | 17.236 | 26 | 51.0 | 29.0 | 0.54 |  |  |
| hobby_crafts_art | 5.732 | 10 | 28.98 | 29.5 | 0.7 |  |  |
| fitness_sports | 5.304 | 13 | 79.99 | 35.0 | 0.54 |  |  |
| toys_games | 4.872 | 12 | 29.97 | 103.0 | 0.5 | CPSIA if for children |  |
| bags_accessories | 4.487 | 22 | 34.37 | 11.0 | 0.59 |  |  |
| pet | 4.037 | 8 | 33.58 | 107.0 | 0.88 |  |  |
