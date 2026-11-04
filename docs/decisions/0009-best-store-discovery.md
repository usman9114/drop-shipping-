# 0009 — Step 1: find the best online stores and reconstruct what they do

> Status: **accepted for step 1**, 2026-11-04. Owner decision: step 1 is finding the best stores and understanding exactly what they do, with no CJ or supplier work; step 2 is sourcing for what step 1 finds. Builds on decision 0008. Code: `scout/webmeta.py` (`scan`), `scout/stores.py`, `scout/store_intel.py`, `scripts/store_export.py`, `warehouse/models/staging/stg_web_*`, `warehouse/models/marts/mart_store_*`. Run: `make stores`.

## The myip.ms idea, from open data

myip.ms lists the sites on Shopify's IP addresses ranked by popularity. Its pages sit behind a bot check and its terms could not be read (pilot A, doc 20), so it is **not automated**; the owner is checking its terms in a browser. The same list comes from open records:

| Step | Record | Channel | Pace and rules |
|---|---|---|---|
| Popularity | Tranco top 1M (research ranking, 30-day aggregate) | `tranco` package, cached list | one download per list date |
| Platform | apex DNS A record in Shopify's storefront range 23.227.38.0/24 | Google Public DNS JSON API | 100 queries/s against Google's documented 1,500/s per IP; 50k-domain tranches, resumable |
| Store facts | the store's own `/meta.json` | storefront | robots.txt read per store, 1 s between requests to one store |
| Catalogue, rhythm, price, vendors | the store's own `/products.json` (up to 4 pages + the last page) | storefront | same; aggregates only, no titles or text kept |
| Traffic stack | homepage code: ad pixels, Shopify web-pixel settings, email/SMS, affiliate, review, BNPL apps; social links | storefront | same |
| Domain platforms | DNS TXT (verification tokens), MX | Google Public DNS | same pace |
| Rank growth | Tranco lists 90 and 365 days back | `tranco` package | — |

No keyword filter: every domain in the top 1M is checked.

## What "best" means here

`mart.mart_store_profile.best_score` = percentile among profiled stores of: **traffic rank 45%**, **rank growth 20%** (ln(rank 365 or 90 days ago / rank now)), **release rhythm 20%** (products created in the last 90 days), **marketing stack 15%** (count of ad, retention, partner and conversion tools plus DNS platform verifications). Weights are our judgment and sit in one SQL line.

**Business model** (`scout.stores.business_model`, tested) separates stores whose success does not transfer to zero inventory:

| Model | Rule (first match) |
|---|---|
| dropship | ≥ 20% of products carry supplier-import traces (AliExpress image ids, DSers/CJ SKU patterns, supplier vendor names) or a dropshipping app on the homepage |
| pod | ≥ 30% print-on-demand vendors |
| brand | the shop's own name is the vendor on ≥ 60% of products, or 1–2 vendors hold ≥ 80% |
| reseller | ≥ 5 vendors and the largest < 50% |
| unclear | anything else |

Brands are kept as **demand evidence** (what sells, at what price, how they market) but not as models to copy.

## Store start date

Shopify shop ids are sequential. For each store, the oldest product date is an upper bound on its start; the running minimum of that date over all stores with a higher id gives `existed_by`, a monotone id → date curve. It says when a store existed **by**, not the exact launch.

## Rules kept

- Store domains, store-level stories and raw rows stay in `data/private/` (gitignored). Committed: aggregates with a 3-store floor on any published label.
- No personal data: `/meta.json` city and description are dropped; no WHOIS, no emails, no names.
- robots.txt is obeyed for every URL; one fixed User-Agent naming the project.
- Copy the method, never the content: no titles, descriptions or images are stored.

## Source terms (terms gate)

| Source | Terms read 2026-11-04 | Retention | Use |
|---|---|---|---|
| Tranco | No licence published for the list ([tranco-list.eu](https://tranco-list.eu/)); upstream lists include Cloudflare Radar under CC BY-NC 4.0 and CrUX under CC BY-SA 4.0; API 1 query/s | **unknown → private working copy only** | Rankings not redistributed; only aggregates published |
| Google Public DNS | Google APIs Terms of Service ([terms](https://developers.google.com/speed/public-dns/terms)); 1,500 qps per IP default limit ([docs](https://developers.google.com/speed/public-dns/docs/isp)) | DNS answers kept privately | Within the limit |
| Shopify storefront `/meta.json`, `/products.json`, homepage | Public storefront endpoints; robots.txt obeyed. Individual stores' terms of service **not read** | **unknown → private only** | Aggregates only published |

## HOMEGROWN

`scout/stores.py` and `scout/store_intel.py` are home-grown: no maintained tool profiles Shopify stores from public records under these privacy and terms rules. Store-intelligence SaaS products (StoreLeads, BuiltWith, Koala Inspector and similar) do the same job for a fee; they are the paid alternative if this proves useful (not bought; owner approval needed).

## Results

See `docs/reports/2026-11-04-best-stores.md` (aggregates) and the private `data/private/reports/2026-11-04-store-stories.md`.
