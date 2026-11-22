# 0020 Chrome UX Report (CrUX): country popularity and store discovery

> 2026-11-22. Pilot run on Pakistan (decision 0019). Owner created the Google Cloud project (display name "eth-test", id `gen-lang-client-0043013737`) and the service account `market-research` with BigQuery Job User. Key stays outside the repo (`~/.config/scout/gcp-sa.json`, path in `.env`).

## Source and terms

- **What:** Google's public BigQuery dataset `chrome-ux-report.country_<cc>.<YYYYMM>`: websites real Chrome users in a country visited that month, with `experimental.popularity.rank` as a rank bucket (1k, 5k, 10k, 50k, 100k, 500k...). No personal data.
- **Terms read 2026-11-22:** "CrUX datasets by Google are licensed under a Creative Commons Attribution 4.0 International License" (https://developer.chrome.com/docs/crux/methodology, license https://creativecommons.org/licenses/by/4.0/). **max_retention:** no limit (CC BY 4.0); attribute "Chrome UX Report, Google" in any published output.
- **Cost:** BigQuery free tier (1 TB of queries a month). One country-month, two columns: **12.6 MB**. `scout.crux` dry-runs every query and stops above 5 GB.
- **Tool (reuse before build):** Google's official `google-cloud-bigquery` client (3.41.0, Apache-2.0, maintained by Google). Our code is the 150-line wrapper `scout/crux.py`.

## Pilot result (Pakistan, table 202610)

| Question | Result |
|---|---|
| Rows | 282,371 Pakistan origins (www folded into the apex) |
| Coverage of our 911 PKR Shopify stores | **909 (100%)** |
| Pakistan popularity of those stores | top 1k: 88, 5k: 400, 10k: 346, 50k: 69, 100k: 3, 500k: 3 |
| Origins never in our Tranco scan | 278,128 |
| Discovery test: 600 unscanned origins (150 per bucket), DNS apex + www vs Shopify IPs | **33 Shopify (5.5%)**: bucket 1k 0.7%, 5k 2.0%, 10k 10.0%, 50k 9.3% |
| Estimated Shopify stores Tranco missed, buckets up to 50k | **about 4,000** `[proxy]` (rate x bucket size; 100k and 500k buckets not sampled) |
| Freshness | monthly; latest table 2026-10 |

**Unique value:** (1) a Pakistan-specific popularity signal (Tranco is global, so a store popular only in Pakistan looks small); (2) discovery of smaller Pakistani stores outside the Tranco top 1M, many of them generic names (`.store`, `.shop`), the copyable shape R1 looks for. Shopify detection is by DNS only; currency (PKR) is not yet confirmed for the 33 hits.

## Decision

1. Adopt CrUX as a **source** for country popularity. In `scout.market_rank`, the CrUX bucket is the better traffic input for a single-country ranking than the global Tranco rank (change pending; weights stay in `WEIGHTS`).
2. **Next (small first, then scale):** DNS-check every unscanned CrUX Pakistan origin in buckets up to 50k (about 47k, DNS only, no store traffic), then `/meta.json` for the hits at 1 worker and 4 s (Shopify throttles our user agent; about 4 h for 4,000 stores), keep the PKR ones, light-profile them.
3. Not yet a recommendation for other countries: piloted on Pakistan only.
