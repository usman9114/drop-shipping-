# 23. Estimating units sold from public signals on Shopify stores

Status: research pass, 2026-11-04. Market: US. Author: market-researcher (Haiku).
Scope: how to turn public review and availability signals into an estimate of units sold, without breaching a site's terms. This report does not measure sales. Every output is a proxy.

Labels used: **[primary]** official or first-party source; **[secondary]** a summary or vendor blog quoting a source; **[unverified]** a claim seen only in a search snippet or an unreadable page; **[estimate]** our arithmetic on the inputs.

## Summary

- The core formula is units ≈ reviews ÷ review rate. The review rate is the unknown. Public vendor figures put it at roughly 2.5% to 25% depending on whether buyers are prompted. That gives a multiplier of about 4x to 40x on review counts. The spread is the main error, not the arithmetic.
- No primary study measures the review rate for Shopify stores. The best figures are vendor benchmarks with different denominators. Treat them as rules of thumb.
- Review-count growth over time (from schema.org `ratingCount` or `reviewCount`) gives a velocity proxy, with a lag between order and review.
- Sold-out flips (`available` true to false) are weak evidence. They show a variant was not purchasable at one moment, not that demand exists.
- Sorted "best sellers" URLs are disallowed by Shopify's default robots.txt. The unsorted collection page is allowed by the same file. Whether that default order is sales-based depends on each merchant's setting [unverified].
- Shopify's FY2025 10-K gives platform-wide GMV ($378.4B, 2025) and says there are "millions of merchants". It gives no per-store distribution. GMV per store cannot be derived from public data.
- Public signals give a number for the platform and a wide band for a store. They are a screen, not a sales count.

## 1. Review rate (reviews per order)

| Source | Value | Definition (denominator) | Date | Type | URL |
|---|---|---|---|---|---|
| Judge.me help: "review collection benchmark" | No number on the page. Badge: above average / average / below average vs other Judge.me stores. Pool median recomputed monthly. | RCR = orders with a request that got ≥1 review ÷ orders with a request. Example on page: 14 of 200 = 7%. | Page shows "August 21, 2026" (only date) | [primary] (vendor) | https://judge.me/help/en/articles/16119278-understanding-the-review-collection-benchmark |
| Judge.me blog "benchmarking review collection rate" | Not read (HTTP 403). | — | — | — | https://judge.me/blog/benchmarking-review-collection-rate |
| Judge.me search snippet: typical store 3.7% RCR; top 10% ~10% | 3.7% typical, ~10% top 10% | Same as above | Not dated | [unverified] (snippet only, not in the help page we read) | https://judge.me/blog/benchmarking-review-collection-rate |
| Okendo support article "reviews metrics optimizations" | "benchmark review rate of 2.5-5% for merchants"; top 10% of merchants "22% review rate" | Review rate = reviews collected ÷ orders placed. Okendo notes a delay between order and request, so month-to-month swings distort the rate. Alt: emails sent ÷ orders. | Article dated March 21, 2024. No time window or sample given. | [primary] (vendor), no sample | https://support.okendo.io/en/articles/9069711-reviews-metrics-optimizations |
| Growave blog "what percent of customers leave reviews" | "roughly 10% of customers leave product reviews" and "roughly 10% of purchasers will leave a review without targeted prompts" | Reviews received ÷ orders in the same period, × 100, excluding returns and refunds. Counts unique reviews tied to orders. | Published Sep 2, 2025; last updated Jun 24, 2026. No studies cited. | [secondary] vendor (conflicted) | https://www.growave.io/blog/what-percent-of-customers-leave-reviews |
| Growave search snippets (other Growave pages) | Unprompted 5–10%; baseline 5–12%; with post-purchase email, 12–25%; prompted/incentivized campaigns "about 20–40%" for engaged buyers | Mixed definitions across pages | Not dated in snippets | [secondary] vendor, [unverified] for the ranges | https://www.growave.io/blog/what-percentage-of-customers-write-reviews-on-a-website |
| Stamped blog (search snippet) | Review response rate 6.5% vs typical 1–3%; follow-up emails: 2.2% with one email, 4.1% with four | Not stated in snippet | Not dated | [unverified] (snippet; page not read) | https://website.stamped.io/blog/best-ways-to-optimize-your-review-request-emails/ |
| BrightLocal survey, via usecarly.com summary | 78% of consumers asked to review in past 12 months; 83% of those asked did; 65% of all consumers wrote a review after being asked | Share of consumers asked, not share of purchasers | Not dated in summary | [secondary] of [secondary]; [unverified]. Not checked against BrightLocal | https://www.usecarly.com/blog/online-review-statistics/ |
| Bazaarvoice resources page | None. Only a Forrester ROI study (400% over 3 years). | — | — | [primary] page, no rate found | https://www.bazaarvoice.com/resources/ |
| Trustpilot "Write a Review Week" (search snippet) | No purchaser review rate. Motivation: 56% after very positive, 38% after negative experience. | Survey of 1,064 US adults (per snippet) | 2025 | [unverified] | https://uk.trustpilot.com/blog/reviews-matter/write-a-review-week |
| Loox, Yotpo | Not found in any result. | — | — | — | — |
| Academic | Not found for purchaser review rate. | — | — | — | — |

Reading the table:
- Vendors use three different denominators: orders with a request (Judge.me), all orders placed (Okendo, Growave), and emails sent (Okendo alternate). A rate on one denominator is not comparable to another. Only Judge.me's RCR can be checked on its own terms, and its benchmark numbers are not on the page we read.
- No vendor states a sample size or time window for its benchmark. Okendo's 2.5–5% is the only one with a range and a stated source type, and it is undated as to data period.
- The Growave ~10% baseline is repeated across its own articles. It cites no study, so it is one vendor's view.

Range we would use, with its status: **unprompted ~5–10% [secondary, vendor]; prompted ~2.5–25% [secondary/primary vendor mix, undated]**. Treat the whole range as a hypothesis until a pilot calibrates it.

## 2. Units from review counts (the conversion)

- Formula: units_est ≈ reviews_cumulative ÷ r, where r is the share of orders that produce a review.
- Multiplier = 1/r. At r = 5% the multiplier is 20x. At r = 10% it is 10x. At r = 25% it is 4x. Across the vendor range (2.5%–25%) it spans 4x to 40x.
- Etsy third-party guides use multipliers of "3–5x" and "10–20x" (search snippets [unverified]). These match r ≈ 20–33% and r ≈ 5–10%. The two guides therefore disagree by roughly 3x to 4x.
- Calibration option: compare reviews with a known count. Etsy shows a public lifetime sales counter that is official but only for Etsy shops. No Shopify equivalent was found [not found].
- Lag: reviews follow orders by days to weeks (Okendo states the delay). Velocity over short windows is therefore biased low and noisy.
- Mix: a store with many old products accumulates reviews from products sold long ago. Store-level totals need a per-product split.

Error band: **roughly 4x to 40x around the reviews count, before any product-level or time-lag correction**. Any single-store unit figure from this method is a [proxy] with that band.

## 3. Review-count velocity from schema.org JSON-LD snapshots

- schema.org definitions [primary]: `AggregateRating` = "The average rating based on multiple ratings or reviews." `ratingCount` = "The count of total number of ratings." `reviewCount` = "The count of total number of reviews." An item can have more ratings than reviews. Source: https://schema.org/AggregateRating
- Method: take weekly snapshots of each product page's JSON-LD `aggregateRating` (ratingCount or reviewCount), take the difference over time, and divide by r to get units per period.
- Caveats:
  - Which field an app writes into JSON-LD is app-specific. Some apps write both, some only one. [unverified]: we have not checked how Judge.me, Loox, Yotpo, Okendo or Stamped populate it.
  - Some apps cache or round the displayed count. [unverified].
  - A ratings-only increase (no written review) breaks the reviewCount link, so use reviewCount where present.
  - Growth in reviewCount in a week = reviews received in that week, which is a lagged signal of orders from earlier weeks.
- Velocity estimate: Δ reviewCount per week ÷ r ≈ units per week [estimate]. Error band as in section 2, plus lag error.
- Terms: reading a public product page is fetching a public page. Shopify's and each store's terms were not read in this pass. Under the terms gate, record terms before any snapshot run, and do not retain review text.

## 4. Amazon "bought in past month" and Etsy "sold" as analogues (not usable for us)

| Platform signal | What we know | Source | Status |
|---|---|---|---|
| Amazon "X+ bought in past month" | Shown as floor buckets (search snippet lists 50+, 100+, 200+, 300+). Rounded down, so "50+" can be 50–99. Products below ~50/month may show nothing. Sellers have reported under-counts. Amazon's own definition not retrieved (amazon.com help page returned HTTP 503). | Secondary: pmg.com (Mar 28, 2023), analyzer.tools knowledge base, seller-forum post | [secondary] / [unverified] for bucket values |
| Amazon Sales Trend FAQ | Named in a seller-forum post; not retrieved. | https://sellercentral-europe.amazon.com/seller-forums/discussions/t/7d835e85-2312-4ca6-83ec-382cb8b75f03 | [unverified] |
| Etsy "X+ Sold" badge and shop lifetime counter | Official Etsy display; the counter is a minimum on listings. Third-party "sold" estimates use reviews × multiplier and disagree by ~3–4x. No official Etsy method found. | Vendor guides (insightagent.app, sellertoolshq.com, alura.io) | [secondary] |
| eBay "sold" | Not retrieved. We may not use eBay API data for stats (decision 0004). | CLAUDE.md | not used |

Use only as a directional comparison. Our markets are Shopify storefronts, not these platforms.

## 5. Sold-out flips (variant availability)

- Shopify's Storefront API `Product` object exposes `availableForSale` ("Indicates if at least one product variant is available for sale.") and `encodedVariantAvailability` [primary, https://shopify.dev/docs/api/storefront/2025-10/objects/Product]. These are Storefront API fields, not the public feed.
- The public `/products.json` endpoint is the path a monitor would use. Per an Apify listing (secondary, [unverified]): unauthenticated, up to 250 products per page, each variant has a boolean `available` and no stock count. Drafts do not appear; some stores disable or password-protect it. No Shopify primary doc for `/products.json` was found.
- Interpretation: `available` true→false means the variant could not be bought at that moment. It can come from stock-out, a paused variant, or a settings change. A false value does not prove zero stock [secondary, Apify listing]. A restock returns it to true.
- So a flip is a demand signal only in combination with a restock pattern or review growth. Alone it is weak.
- Data cost is low (one request per store per interval). Terms: not read for each store; record before running.

## 6. Within-store ranking from "best sellers" collections

- Shopify default robots.txt [primary, Shopify Help: https://help.shopify.com/en/manual/promoting-marketing/seo/editing-robots-txt]:
  - `Allow: /` (product, collection, page, blog, policy pages are crawlable).
  - `Disallow: /collections/*sort_by*` (sorted collection pages are not crawlable).
  - `Disallow: /collections/*+*` (filtered collection pages).
  - The default list shown on that page has no search rule. Older custom templates had `Disallow: /search`.
  - The page says editing robots.txt.liquid is an "unsupported customization" and can cause loss of traffic.
- A store's live file confirms this pattern. Aventon's robots.txt has `Disallow: /collections/*sort_by*`, `Disallow: /*/collections/*sort_by*`, and `Disallow: /search` [primary live file, fetched; https://www.aventon.com/robots.txt]. This is one store, not a sample.
- No rule specific to "best-selling" was found. The `sort_by` wildcard would cover `?sort_by=best-selling` by pattern. That reading is ours [estimate].
- Remains allowed: the unsorted collection page `/collections/<handle>` (crawlable under `Allow: /`). Whether its default order is sales-based depends on the merchant's theme and sort setting. [unverified] for the default.
- Ranking value: the position of a product on an unsorted "best sellers" page is a merchant-curated order, not a sales rank. It is a weak within-store signal. We found no source that says how merchants set it.
- Terms: the page is crawlable under the robots file. The Shopify terms of service were not read. Automated access to pages still requires the terms gate.

## 7. Shopify published figures (sanity check for store distribution)

| Figure | Value | Date | Source | Status |
|---|---|---|---|---|
| Platform GMV | $378.4 billion, up 29% vs 2024 | FY ending Dec 31, 2025 | Shopify Form 10-K FY2025, Business Overview: "our platform facilitated gross merchandise volume ("GMV") of $378.4 billion, representing an increase of 29%" | [primary] (SEC filing, read directly) https://www.sec.gov/Archives/edgar/data/1594805/000159480526000007/shop-20251231.htm |
| Merchant count | "millions of merchants from more than 175 countries" (no exact number) | As of Dec 31, 2025 | Same 10-K | [primary] |
| Concentration | No single merchant >5% of total revenue in any reporting period | Through FY2025 | Same 10-K | [primary] |
| GMV note | "GMV does not represent revenue earned by us." | FY2025 | Same 10-K | [primary] |
| Exact merchant count | Last exact figure 2.06 million (Dec 2021), per Search Engine Land | Dec 2021 | https://searchengineland.com/guide/shopify-stats | [secondary] |
| Current merchant estimate | ~5.5 to 5.7 million | 2026 | Countly, DemandSage (Built With data) | [unverified] third-party estimates |
| Q1 2026 GMV | Over $100 billion (press release, 8-K) | Q1 2026 | https://www.sec.gov/Archives/edgar/data/0001594805/000159480526000018/exhibit991pressreleaseq120.htm | [primary] for the wording seen in snippet; the exact figure was not read |
| Per-store GMV distribution | Not found | — | — | not found |

Use: GMV ÷ merchants gives a platform mean of about $69k per merchant if the 5.5M estimate were right [estimate, [unverified] denominator]. A mean is not a distribution. Long-tail shares are unknown. Do not use this as a per-store figure.

## 8. Academic and industry papers on sales from public signals

| Paper | What it does | Relevant numbers | Status | URL |
|---|---|---|---|---|
| Chevalier & Goolsbee (2003), "Measuring Prices and Price Competition Online: Amazon and Barnes and Noble," Quantitative Marketing and Economics 1(2) | Turns public Amazon/BN sales ranks into quantity proxies (~20,000 books). Calibrated with cheap purchase experiments. | Secondary (Postrel article): "sales approximately double every time the rank is cut in half" [unverified rule of thumb, not the paper's own wording]. Experiment: six copies bought, rank moved to 2,854. | NBER WP 9085 (2002); DOI 10.1023/A:1024634613982 | https://www.nber.org/papers/w9085 |
| Chevalier & Mayzlin (2006), "The Effect of Word of Mouth on Sales: Online Book Reviews," J. Marketing Research 43(3) 345–354 | Review valence and volume vs relative book sales at Amazon and BN | ~1,087 books in three two-day windows (2003–2004), per secondary summary [secondary]. Negative reviews move sales more than positive ones. Effects are relative across sites, not total market. | JSTOR stable/30162409 | https://wordofmouth.org/blog/word-of-mouth-research-the-effects-of-online-reviews-on-book-sales/ |
| Archak, Ghose & Ipeirotis (NET Institute WP 07-36; later Management Science) | Amazon, 242 products, 15 months; text of reviews predicts sales better than numeric signals alone | Per search snippet [secondary] | — | not fetched |
| arXiv 1704.02993, "Characterizing Product Lifecycle in Online Marketing" | Closest match: approximates online sales from review data for 1.09M Amazon products | Method not retrieved (PDF fetch returned binary). Intro only [secondary] | Method unverified | https://arxiv.org/pdf/1704.02993 |
| Tmall snack study (GEE model of review aspect tags) | Review tags relate to same-period sales volume; some tags nowcast next period | Per snippet [unverified] | — | not fetched |

Conclusion from the literature: the mapping from reviews to sales is a modelled, product-specific relationship. Published work either uses sales data as ground truth (Amazon/BN ranks, calibration) or does not validate a units estimate. We found no paper that validates a Shopify review-count multiplier.

## Table: signals and how to use them

| signal | what it measures | how to turn it into units | error band | data cost | terms risk |
|---|---|---|---|---|---|
| Review count (cumulative, per store) | Reviews received; a lagged, partial record of past orders | units ≈ reviews ÷ r, r from vendor benchmarks (2.5%–25%) | ~4x to 40x (r uncertainty dominates); lag adds more | Low: one page or app-JSON read per store per interval | Medium: store and app terms not read; do not retain review text |
| Review count velocity (weekly Δ reviewCount in JSON-LD) | Recent review inflow | Δ reviews per week ÷ r | Same as above, plus week-level noise and lag; app-dependent field | Low (weekly snapshots) | Medium: as above; record terms |
| Aggregate rating (average stars) | Quality signal, not volume | Not a units input | Not applicable | Low | Low |
| Vendor review-rate benchmarks (Okendo, Judge.me, Growave) | The r in the formula | Use as prior for r, with sensitivity range | Vendor-published; no sample or window; denominators differ | None (published) | Low (public content) |
| Sold-out flips (variant available true→false) | Momentary non-purchasability | Count of flips × restock timing; no units | Not a units count; false ≠ zero stock | Low: `/products.json` if reachable | Medium: feed not documented by Shopify; check each store's terms |
| "Best sellers" collection order | Merchant-curated order | Rank only; no units | Unknown ordering logic | Low: unsorted collection page | Low for the unsorted page; `sort_by` URLs disallowed by default robots.txt, so do not fetch them |
| Amazon "bought in past month" / Etsy "sold" | Analogue platform counters | Not for Shopify; calibration reference only | Floor buckets (50–99 etc.); under-count reports | Not used | Not applicable (not our platform) |
| Shopify GMV (10-K) | Platform total, not per store | Mean per merchant only with an uncertain denominator | No distribution | None (SEC) | Low |
| Chevalier & Goolsbee rank-to-quantity | Rank-to-sales mapping on Amazon/BN books (2003) | Rank → quantity via a fitted curve (needs calibration per category) | Not stated in our sources; old data, different platform | None | Not applicable |

## Not found

- Primary study of the review-to-purchase rate for Shopify stores: not found.
- Loox and Yotpo published review-rate benchmarks: not found.
- Judge.me typical/top-10% numbers on a primary page: not confirmed (snippet only).
- Stamped's own page (blog fetch not read): not confirmed.
- Shopify's own documentation for public `/products.json`: not found.
- Amazon's definition of "bought in past month": not retrieved (503).
- Per-store GMV or order distribution for Shopify: not found.
- Any validated multiplier from reviews to units for Shopify: not found.

## Notes on method

- Pilot not run in this pass. Per the source-evaluation standard, these are hypotheses until we pilot them on a sample (for example, 20 stores: read `/products.json` and product JSON-LD, record the fields present and the flip count over two weeks, and check whether reviewCount moves).
- Terms gate: for any store we read, record the terms (date, `max_retention`, license link) before ingestion. Review text is not stored.

## Sources

1. Judge.me, "Understanding the review collection benchmark" (help article; page shows Aug 21, 2026): https://judge.me/help/en/articles/16119278-understanding-the-review-collection-benchmark
2. Judge.me, "Benchmarking review collection rate" (blog; HTTP 403, not read; snippet only): https://judge.me/blog/benchmarking-review-collection-rate
3. Okendo support, "Reviews metrics optimizations" (dated Mar 21, 2024): https://support.okendo.io/en/articles/9069711-reviews-metrics-optimizations
4. Growave, "What percent of customers leave reviews" (published Sep 2, 2025; updated Jun 24, 2026): https://www.growave.io/blog/what-percent-of-customers-leave-reviews
5. Growave, "What percentage of customers write reviews on a website" (search snippets): https://www.growave.io/blog/what-percentage-of-customers-write-reviews-on-a-website
6. Stamped, blog on review request emails (snippet only): https://website.stamped.io/blog/best-ways-to-optimize-your-review-request-emails/
7. usecarly.com, online review statistics (secondary summary of BrightLocal): https://www.usecarly.com/blog/online-review-statistics/
8. Bazaarvoice resources page (no rate found): https://www.bazaarvoice.com/resources/
9. Trustpilot, "Write a Review Week" (UK; snippet only): https://uk.trustpilot.com/blog/reviews-matter/write-a-review-week
10. schema.org, AggregateRating: https://schema.org/AggregateRating
11. Shopify Help, "Editing robots.txt" (default rules): https://help.shopify.com/en/manual/promoting-marketing/seo/editing-robots-txt
12. Aventon live robots.txt (example of store rules): https://www.aventon.com/robots.txt
13. Shopify.dev, Storefront API Product object (availableForSale, encodedVariantAvailability): https://shopify.dev/docs/api/storefront/2025-10/objects/Product
14. Apify, Shopify Products Scraper listing (secondary description of /products.json; [unverified]): https://apify.com/dami_studio/shopify-products-scraper?fpr=wcqem0
15. Amazon "bought in past month" explainers (secondary): https://www.pmg.com/insights-and-news/amazon-serp-bought-in-last-tags ; https://www.analyzer.tools/knowledge-base/bought-in-past-month-sales/
16. Amazon Seller Forums thread on the metric: https://sellercentral-europe.amazon.com/seller-forums/discussions/t/7d835e85-2312-4ca6-83ec-382cb8b75f03
17. Etsy third-party sold-estimate guides (secondary, [unverified] multipliers): https://www.insightagent.app/guides/how-to-see-how-many-items-sold-on-etsy ; https://sellertoolshq.com/guides/etsy-shop-revenue-estimator/
18. Shopify Inc., Form 10-K FY2025 (GMV $378.4B; "millions of merchants"; 5% concentration): https://www.sec.gov/Archives/edgar/data/1594805/000159480526000007/shop-20251231.htm
19. Shopify Inc., Form 8-K exhibit 99.1 Q1 2026 press release: https://www.sec.gov/Archives/edgar/data/0001594805/000159480526000018/exhibit991pressreleaseq120.htm
20. Search Engine Land, Shopify statistics (last exact merchant count 2.06M, Dec 2021; [secondary]): https://searchengineland.com/guide/shopify-stats
21. Countly, "How many Shopify merchants are there in 2026" ([unverified] estimate): https://countly.net/how-many-shopify-merchants-are-there-in-2026-global-by-count
22. Chevalier & Goolsbee (2003), NBER WP 9085: https://www.nber.org/papers/w9085 ; DOI: https://www.doi.org/10.1023/A:1024634613982
23. Chevalier & Mayzlin (2006), "The Effect of Word of Mouth on Sales" (summary and citation): https://wordofmouth.org/blog/word-of-mouth-research-the-effects-of-online-reviews-on-book-sales/
24. Archak, Ghose & Ipeirotis, NET Institute WP 07-36 (snippet only): search result, no URL fetched
25. arXiv 1704.02993, "Characterizing Product Lifecycle in Online Marketing" (intro only): https://arxiv.org/pdf/1704.02993

## How we would use these

1. Treat review count ÷ r as a range (roughly 4x to 40x reviews), never a point estimate, and label it [proxy].
2. Calibrate r with a pilot: pick 20 stores with a known count (for example, a store that publishes its order count), and see which vendor benchmark fits.
3. Use weekly reviewCount deltas from JSON-LD as a velocity screen for niche ranking, not as units. Record the app and field per store.
4. Use sold-out flips and unsorted collection order as tie-breakers only. Do not fetch sorted `sort_by` URLs.
5. Record terms for each store and for Shopify before any snapshot job runs. Keep counts, not review text.
