# 32c. Trustpilot and Google Ads Transparency: legal automation routes

Researched 2026-11-05. Scope: only routes whose terms allow automated access. Third-party scrapers (Apify actors etc.) are out of scope. Label key: [primary] = official page fetched today; [secondary] = non-official; [unverified] = not confirmed on an official page.

## Summary table

| Source | Legal automated route? | Access | Cost | Fields we need | Verdict |
|---|---|---|---|---|---|
| Trustpilot website (scraping) | No. Consumer Terms s.4 [primary] [1] | n/a | n/a | n/a | Do not automate |
| Trustpilot Data Solutions: Display API | Yes, by contract | Contact sales ("Get in touch") [2][3] | Not published; quote-based [unverified] | TrustScore, review count (`numberOfReviews.total`) [4] | Only legal automated route; internal-use terms to be confirmed in writing |
| Trustpilot Data Solutions: Insights API | Yes, by contract | Contact sales [3] | Not published [unverified] | Display fields + full reviews + categories [2] | Overkill for rating and count |
| Trustpilot public Business Units API (api.trustpilot.com) | Exists [secondary]; key eligibility unconfirmed | Reported to need a Trustpilot Business account with API add-on [secondary, Apify listing, 5] | Unknown [unverified] | TrustScore, review count | Treat as unavailable to non-customers until Trustpilot confirms |
| Trustpilot Product Reviews / Consumer APIs | Not relevant | Listed in nav [6]; for Trustpilot-for-Business customers and partners | n/a | Reviews of own products; consumer actions | Not for looking up other companies |
| Google Ads Transparency Center website | No API [secondary] | n/a | n/a | n/a | Manual viewing only |
| Google BigQuery dataset `bigquery-public-data.google_ads_transparency_center` | Yes (official) | Google account + GCP project, free sandbox [7][8] | Free tier (see notes) | Advertiser, creative ID, format, first/last shown by region, impression bounds | Official, but EEA + Turkey only; US not covered |
| Google political ads dataset `google_political_ads` | Yes (official) | Same | Same | Election ads only | Useless for Shopify brands |

## Part 1: Trustpilot

### What the official pages say

- Developer portal lists: Business Units API and Business Units API (public), Consumer API, Consumer Profile API, Product Reviews API, Private Products API, Service Reviews API, Data Solutions API, Deletions API, etc. Three tracks: Trustpilot for Business, Integration partners, Data Solutions ("Access Trustpilot's global database of business profiles and consumer reviews"). The page does not state eligibility, pricing or limits. [primary] [6]
- Data Solutions API "provides access to Trustpilot's data for all Business Units (domains)". Host `https://datasolutions.trustpilot.com/v1/`, header `apikey`. Steps: find the Business Unit ID from a domain, then fetch details. Endpoints: `GET /business-units?domain=...`, `GET /business-units/{id}`, `GET /business-units/{id}/reviews/latest` (up to five), `GET /business-units/{id}/reviews` (Insights only). [primary] [4]
- Fields: `numberOfReviews.total` and `numberOfReviews.usedForTrustScoreCalculation`; TrustScore ranges 1.0 to 5.0. [secondary summary of the official docs, search result 2026-11-05] [4]. Lookup is by domain, so our brand list (domains) maps directly. 100 results per page on searches. [primary] [4]
- Access: "register your interest on the Data Solutions waitlist"; a team member then sets up the account; your partner manager creates the first admin; keys are generated in the Data Solutions web app ("Create new key"); one active key per organization; the key is shown once. [primary] [2]
- Plans: Display API (business unit search and lookup, business details, latest reviews, web app) and Insights API (Display + full service reviews + categories). [primary] [2]
- The marketing page says Display API embeds "ratings, review counts, and sentiment scores"; Insights API gives "raw Trustpilot reviews and business data" for "market research, and competitive intelligence"; access is via "Get in touch". [primary] [3]
- Cost: no price published on any official page seen. Datarade says Trustpilot has not published pricing. [secondary] Assume enterprise quote. [unverified]
- Rate limits: "Trustpilot recommends that you don't exceed 833 calls per 5 minutes or 10K calls per hour." [primary] [9] This is a recommendation; hard limits [unverified]. 300 brands is a trivial load.
- Storage rules: cached TrustScores must be refreshed every 24 hours (Content Refresh Guidelines); Business Unit IDs can be cached indefinitely. [primary] [10] If you store consumer or review data you must call the Deletions API "every 28 days". [primary] [4]

### Terms: can we look up OTHER companies' TrustScore and review counts and keep them privately?

- Data Report terms (Data Solutions schedule): "End Companies will use the Trustpilot Content solely for their internal business purposes"; sharing a Data Report or its content with a third party is forbidden "unless expressly permitted in this Schedule or the Order Form". [primary] [11] So internal analysis is the contemplated use; publishing or redistributing is not. This schedule is for Data Reports; whether the same wording governs the API order form is [unverified]; the signed Order Form controls.
- Retention: the schedule is silent on storage; the 24-hour refresh rule applies to content "you display". Whether a private historical time series (our tracking use) is permitted is [unverified]. Ask in writing.
- Partner agreement: "Trustpilot Content" includes reviews, star ratings and TrustScores; unauthorized use can be enjoined; APIs are "as is" and can change without notice. [primary] [12]
- Our rule (CLAUDE.md Terms gate): no ingestion until terms are recorded in `meta.source`. Record date, max_retention (unknown until written reply), licence link.

### Express permission

- Consumer Terms s.4: "You must not access, search or collect content from our platform by any means (automated or otherwise)" "except as provided on our platform or specifically approved by us"; and no "text mining, data mining or web scraping of our platform for any purpose without our express permission". [primary] [1]
- No dedicated permission form or process is published on the pages seen. The only documented "approved by us" routes are the Data Solutions products via "Get in touch". [primary] [3] A written request to Trustpilot sales or legal is the process. [inference]
- Consequence: use of the public website for rating and count lookups, even manual-by-script, is outside s.4. Manual reading by a person on the profile page is "as provided on our platform"; scripted collection is not.

### Notes on the public Business Units API
Search shows an older `api.trustpilot.com/v1/business-units/find` with `apikey` auth [secondary, 5]. The official page returned HTTP 503 when fetched, so we could not confirm who can obtain a key. An Apify listing states a Business account with the API add-on is needed [secondary]. Not confirmed; do not plan on it.

### Recommendation (Trustpilot)
- Legal automation route: Data Solutions Display API (contract). Nothing else is confirmed.
- Stays manual: all rating/count reads from trustpilot.com until a contract exists. At 17 brands, a monthly person-read of the profile page, typed into a sheet, is within "as provided on our platform" [inference, not legal advice].
- Owner steps: (1) Use "Get in touch" on https://br.business.trustpilot.com/datasolutions and pick Display API. (2) Ask in writing: price; whether internal, private, time-series storage of TrustScore and review count for ~300 third-party domains is allowed; max retention; whether a non-reviewed-company buyer is eligible. (3) Record the answer in `docs/decisions/` and `meta.source`. (4) Cost: unknown; get the quote before any commitment (CLAUDE.md: stop and ask before spending). Do not use paid wrappers or scrapers.

## Part 2: Google Ads Transparency

### What exists officially

- Google's Cloud blog describes only the political dataset: `bigquery-public-data.google_political_ads`, table `creative_stats`, election ads only, verified advertisers, from 2018, 7-year retention, 35+ countries, fields include advertiser name/ID, date_range_start/end, impressions as ranges. [primary] [13] Not useful for Shopify brands.
- Commercial dataset: `google_ads_transparency_center` (Cloud Marketplace listing: "Google Ads Transparency Center"). Per Google's download README: [primary] [14]
  - Two datasets, free to download and also queryable in BigQuery: `creative_stats` (EEA and Turkey) and `removed_creative_stats` (EEA only).
  - Impression data since 2023-03-01; earlier first-shown dates are reported as 2023-03-01.
  - `creative_stats` fields: advertiser ID and names, creative ID, ad format, location, verification status, topic, Ad Grants flag, payer, audience selection.
  - Region stats: region code, first and last shown dates, lower/upper bounds of times shown.
  - Terms: Google Terms of Service plus Google Ads Transparency Center Additional Terms (adstransparency.google.com/terms). No separate open licence named. I did not read the Additional Terms text: [unverified] whether internal competitor analysis is allowed.
- Marketplace listing summary (via search snippet, page itself not fetchable: header overflow): within BigQuery's free monthly tier; needs a Google account and a GCP project. [secondary snippet] [7] BigQuery sandbox needs no credit card; billing beyond the free tier follows standard pricing. [primary] [13]
- Coverage gap: the website is global, the dataset is EEA + Turkey only. A forum reply states public datasets "may not have all of the data" that the site shows. [secondary] [8] So a US-only Shopify brand running US ads will mostly be absent. Brands advertising in the EU would appear.
- A single blog claims EU political ad history was removed around 2025-09-28. [unverified, one secondary source]
- No official Ads Transparency Center API for the website: only vendor statements. [secondary] The Google Ads Policy help page I tried returned 404, so "no API" is [unverified] from Google.

### Pilot status
No pilot query was run (no GCP project available in this run). Per CLAUDE.md, the dataset is a hypothesis until a small pilot (10 to 30 known brands: match by advertiser name/domain, report hits, freshness) is done.

### Recommendation (Google)
- Legal automation route: BigQuery public dataset `google_ads_transparency_center`, only for the share of brands that advertise in the EEA/Turkey. Free tier.
- Stays manual: US ad viewing. Look up each brand by hand at adstransparency.google.com (viewing by a person); do not script the site (no official API; scraper terms [unverified]).
- Owner steps: (1) Create a Google account and a GCP project with the BigQuery sandbox (no card), or approve us using one; stop and ask before enabling billing. (2) Read https://adstransparency.google.com/terms and record date, retention and link in `meta.source`. (3) Run a 20-brand pilot query on `creative_stats` (advertiser name match, format, first/last shown by region); record hit rate. (4) If hit rate for our brands is low, drop it and keep manual US checks. Cost: $0 within the free tier (1 TB query/month standard BigQuery free tier [unverified on this run; confirm on the pricing page]).

## Gaps
- Trustpilot pricing, rate hard limits, key eligibility of the public API, and internal-storage rights: unconfirmed.
- Google Additional Terms and the Marketplace listing text: not read directly.
- Neither source reveals ad spend or revenue; ratings are a [proxy] for customer satisfaction and review counts a [proxy] for order volume, not sales.

## Sources
1. https://corporate.trustpilot.com/legal/for-reviewers/terms-of-use-for-consumers (s.4; fetched 2026-11-05)
2. https://developers.trustpilot.com/data-solutions-get-started
3. https://br.business.trustpilot.com/datasolutions
4. https://developers.trustpilot.com/data-solutions-how-to
5. https://apify.com/nabeelbaghoor/customer-reviews-trustscore-api (vendor, conflicted); https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)/ (503 on fetch)
6. https://developers.trustpilot.com/
7. https://console.cloud.google.com/marketplace/details/bigquery-public-data/google-ads-transparency-center (snippet only)
8. https://discuss.google.dev/gc/Data-Analytics/Querying-public-google-ads-transparency-center-table-doesn-t/m-p/856073
9. https://developers.trustpilot.com/rate-limiting
10. https://developers.trustpilot.com/ds-caching-best-practices/
11. https://it.legal.trustpilot.com/for-businesses/data-report-specific-terms
12. https://corporate.trustpilot.com/legal/for-partners/master-partner-agreement-trustpilot-a-s
13. https://cloud.google.com/blog/topics/developers-practitioners/how-get-started-political-ads-transparency-report-dataset
14. https://storage.googleapis.com/ads-transparency-center/api-data/README.txt
