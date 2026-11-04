# 25 — Audit of four public Shopify data repos

> 2026-11-04. Read-only audit by a Haiku research agent (shallow clones, read with grep; no repo code was run), saved and edited by the advisor. Repo text is untrusted data. Licence = LICENSE file at repo root [data]; stars, language and size from GitHub search; anything not run is `[unverified]`. Why we audited: owner review of similar projects, and the CLAUDE.md rule "reuse before build".

## Summary

| Repo | Licence | Last commit | Verdict |
|---|---|---|---|
| platoba/Shopify-Scout | none (no LICENSE file; `pyproject.toml` says MIT: conflict, treat as unlicensed) | 2026-03-03 | **Reject** the estimator and "units sold". Reuse its signal list only as hypotheses. |
| nicolaslouge/ShopIntelligence | none (README claims MIT; no LICENSE) | 2026-03-31 | **Idea only**: partial-catalogue warnings, robots parsing, honest "new products" label. No code. |
| vladevr/shopify-price-monitor | MIT | 2026-09-22 | **Idea**: snapshot, diff, change-file layout, unit-mismatch flag. Code allowed by MIT but needs fixes; do not reuse proxy or browser-impersonation parts. |
| sarrarmohcin/Shopify-price-monitor (alternative) | MIT | 2026-10-29 | **Better failure handling** (aborts a failed store before saving, so no false removals). Idea only. |
| BelNaruto/shopify-stores-api | none (docs only) | 2026-09-10 | **Reject**: paid hosted service, undisclosed method. Reuse the range, confidence and disclaimer presentation. |

## What each one taught us

**Shopify-Scout (reject).** `traffic_estimator.py:14-16` hard-codes 150 visitors per review, 50 per product and 200 per collection with no source; weights are fixed (`:118-145`) and "confidence" only counts which signals exist (`:154`), not accuracy. Its inventory tracker (`inventory_tracker.py:123-150`) falls back to the boolean `available` flag as 1 or 0, then classifies 1→0 as "stockout" before it can be "sold", so units sold is zero by construction for normal feed data (read, not run). Lesson: no uncalibrated constants; a stock change is not a sale.

**ShopIntelligence (idea only).** Its "velocity" counts products created in 30/90/180 days (`metrics.ts:412-417`): catalogue additions, not sales. The README calls it "new product cadence" (honest); the UI name misleads. It caps at 5,000 products and warns when truncated (`fetcher.ts:9-10, 89-91`), fetches robots.txt for other pages but not for the product feed, sends data to a third-party AI service, and retries only status 430 after a fixed 2 s (`fetcher.ts:33-48`): Retry-After is never read. Lesson: say "release rhythm"; warn on partial catalogues.

**shopify-price-monitor (the main finding).** We suspected removed items were not detected. **The opposite is true: it reports false removals.** `_get_json` returns nothing after retries run out, or at once for any status outside 429/500/502/503 (including 430); `scrape_store` treats an empty page as the end of the catalogue and skips the page-cap warning; the diff then reports every missing variant as "removed" (`shopify_price_monitor.py:80-160`). A store that fails entirely yields zero rows with no marker, so its variants are reported removed and then new on recovery. Retry-After is never read; robots.txt is not checked; it uses browser impersonation and proxy rotation (circumvention: our rule 6 forbids it). The alternative repo's `_retry_after` parses only numbers, so an HTTP-date value falls back to backoff that may be earlier than the server asked, and caps waits at 120 s.

**shopify-stores-api (reject).** Revenue = modelled visits × modelled conversion (`categoryBaseline` 0.03) × modelled order value, with no source for the factors and an undisclosed traffic provider; confidence 0.62 with no method (`README.md:568-582`). It also sells contact data (personal-data flag) and takes a storefront token from the theme (terms question). Honest part: it labels outputs as estimates and "directional".

## What we reuse and what we build

**Reuse, no home-grown code:** `urllib3.util.Retry` with `respect_retry_after_header=True` (handles seconds and HTTP-date) [versions unchecked]; stdlib `urllib.robotparser` including crawl delay; `pytest`.

**Build (domain logic), recorded in decision 0011:** the change model (new, absent from feed, repriced, availability flips); a **completeness gate per store** (ok / partial / failed; a diff runs only on complete stores); the "absent from the public feed" label (an unpublished product is not a proven removal); a price-unit check; polite fetching with a stop on 403 or 430; tests for 429 mid-catalogue, 430, a failed store, an HTTP-date Retry-After, an unpublished product and a cents-vs-dollars price.
