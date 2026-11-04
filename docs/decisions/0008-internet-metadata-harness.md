# 0008 — Internet-metadata harness: find and profile stores from records the web already publishes

> Status: **accepted for the pilot**, 2026-11-04. Owner direction: "think how internet-generated metadata can be reused for this purpose"; "if Terapeak cannot be automated, we drop it". Code: `scout/webmeta.py` (tested), lake datasets `web_domains`, `web_dns`, `web_sitemaps`, `web_products`. Raw results stay in `data/private/` (store domains are public, but lists of competitors don't belong in a public repo).

## Terapeak is dropped

Terapeak is manual only, so it is out of the pipeline: intake model, runbook, template and pre-filled sheet are removed. eBay sold counts are now a **known gap**. Automated demand signals that replace it are listed at the end.

## The idea

Every store leaves machine records made for other purposes. Read through official, free channels, they replace the gated look-alike sources from pilot 1 (myip.ms, ad libraries):

| Record | What it was made for | What it tells us | Channel |
|---|---|---|---|
| **Tranco top-1M list** | Research ranking of popular sites | The domain has real traffic | `tranco` package (cached list) |
| **DNS A / CNAME** | Routing | Store runs on Shopify (23.227.38.0/24 or `*.myshopify.com`) | Google Public DNS JSON API |
| **DNS TXT** | Domain verification, email authentication | Which platforms the store uses: Meta business account, Google Search Console, Pinterest, TikTok, Klaviyo, email senders | same |
| **DNS MX** | Mail routing | Email provider | same |
| **Sitemaps** | Search-engine crawling | Catalogue size | store's own sitemap, robots.txt respected |
| **`/products.json`** | Shopify storefront feed | Product creation dates (release rhythm), price band, the store's own categories | store's own feed, robots.txt respected, one page, aggregates only |
| Certificate logs | Certificate transparency | Domain launch date | crt.sh (flaky from this sandbox) |

## Pilot result (2026-11-04)

| Step | Sample | Found | Notes |
|---|---|---|---|
| Tranco + keywords | top 1M | **4,510** domains with a product word in the name | Noisy keywords: "craft" (1,142) and "mop" (344) catch unrelated sites. Needs a tighter word list. |
| DNS | top 300 by rank | **17 Shopify stores (6%)**, 0 errors | Meta business account 3, Klaviyo 5, Pinterest 1, Google Search Console 13. Top of the list is big non-store sites; small stores sit deeper. |
| Sitemaps | 17 stores | robots allowed 17/17; catalogue sizes 57 to 3,000+ | **Shopify sets every `lastmod` to today**, so sitemaps give size, not timing. |
| `/products.json` | 17 stores | **16/17 answered** | Release rhythm works: one store added 250 of its newest products within a month, another 3. Price band and categories work. |

**Verdict:** DNS and the product feed are the strongest new traces: automated, free, and they fill real parts of the store story (platform, marketing stack, catalogue, release rhythm, price). Tranco is a good discovery list but needs a tighter keyword filter.

## Gaps and fixes for the next run

- **Country and currency.** Many matches are Indian, Brazilian or French; prices are in local currency. Add a US filter (TLD, currency from the storefront, or shipping country). Unverified which storefront field is most reliable.
- **Launch date.** One page of 250 products is the newest 250, not the store's start. Use certificate first-seen date (crt.sh, flaky here) or page through the feed.
- **Depth.** Run DNS on all 4,510 matches (about 12 minutes at the polite pace) to reach the small stores below rank 100k.
- **Store terms.** robots.txt is respected; individual stores' terms of service were not read. Under the terms gate, results stay private and only aggregates are published.

## Automated demand signals that replace Terapeak

| Signal | Status |
|---|---|
| CJ US stock drawdown and listing growth (`mart_product_velocity`) | Built; needs repeated daily pulls |
| Store release rhythm and catalogue size (this harness) | Built |
| Google Chrome UX Report (traffic tier per store, monthly) | Needs a free Google API key from the owner |
| Licensed Google Trends (SerpApi or DataForSEO) | Needs a key; about $25 per 1,000 searches or $0.0027 per task |
| Keepa `monthlySold` (Amazon) | Paid (about €49/month), optional |
| eBay sold data | Only with eBay's written permission (decision 0004) |

`HOMEGROWN`: `scout/webmeta.py` (about 300 lines, tested). Existing pieces are reused: the `tranco` package, Python's `robotparser`, Google's DNS JSON API. No maintained tool combines these under our privacy and terms rules.
