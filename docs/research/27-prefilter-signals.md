# 27 — Can we pre-filter brands and retailers before fetching a store's feed?

> 2026-11-04. Owner question. Pilot per the source evaluation standard: test each cheap signal on stores whose business model we already know, and report what it separated. Ground truth is our own light-screen label (`scout.stores light`), itself about 80% accurate (`docs/reviews/2026-11-04-business-model-validation.md`), so lifts are approximate. No store names here.

## Answer

**No cheap signal separates them.** The only decisive signal is one page of the store's own product feed (vendors, supplier traces, category spread, discounts), which the light screen already reads: about 4 stores per second, so ~9,000 US stores in about 40 minutes. That screen is the pre-filter: it decides who gets the expensive deep profile.

## Pilot results

**Store facts from `/meta.json`** (8,270 US stores, 455 copyable = 5.5%). The copyable share stays near 5% across every band:

| Signal | Bands (stores, copyable share) | Reading |
|---|---|---|
| Published products | ≤50: 9% · ≤200: 5% · ≤500: 5% · ≤1,000: 5% · ≤3,000: 5% · ≤10,000: 5% · >10,000: 6% | flat; only the tiniest catalogues lean copyable |
| Countries shipped to | 0: 19% (31 stores) · 1: 5% · ≤5: 4% · ≤30: 7% · ≤100: 6% · >100: 6% | flat |
| Collections | ≤5: 19% (359 stores) · ≤20: 8% · then 4% to 6% | tiny shops lean copyable, too small a group to filter on |
| Collections per product | 10% at the lowest band, 5% to 6% elsewhere | flat |
| Tranco rank | ≤50k: 10% · 50k to 1M: 5% to 6% | flat |
| Instalment payments offered | 5.1% with, 6.1% without | flat |

**DNS email setup** (1,355 stores, enriched sample, 455 copyable = 34%): copyable share by mail provider: Google 30%, Microsoft 29%, other 41%, budget mail 45%, enterprise filter 41%, no mail record 44%. By verification record: all within 27% to 36% except "no signals" 43% and Zoho 45%. **At most a 1.3x lift: not usable as a filter.**

## What a filter would cost

Any rule from these signals that keeps 90% of copyable stores removes only a small share of brands and retailers, so it saves little and risks dropping real candidates. We do not use one.

## What we do instead

1. **Light screen of every US store** (one feed page): business model, price band, categories, release rhythm.
2. **Deep profile** (homepage tags, DNS, up to 5 feed pages, rank history) for the copyable stores, plus the strongest brands for "what the best stores do".
3. Brands and retailers stay in the report as **demand evidence** (what sells, at what price, how they market) and are **excluded from niche scoring**, which counts copyable stores only.

## Untested ideas (hypotheses)

- A smaller feed page (about 50 products) to cut the screen's bandwidth; vendor shares from 50 products may mislabel large catalogues. Worth testing on 200 stores if speed ever matters.
- A model reading the store's title and tagline to tell a maker from a reseller: slower and noisier than the feed screen; not piloted.
