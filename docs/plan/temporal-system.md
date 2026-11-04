# Temporal system: tracking stores over time

> 2026-11-04. Owner request: "lets build a temporal system". Single snapshots tell us who is big; change over time tells us who is growing, what they add, what they reprice, and whether demand is real. Decision on storage: `docs/decisions/0012-temporal-storage.md`.

## What is reconstructible and what is forward-only

| Data | Source | Can we rebuild it later? | Needs durable storage? |
|---|---|---|---|
| **Rank history** (26 Tranco list dates, 2 years, 30,365 stores) | Tranco's archive of daily lists | **Yes**, in about 10 minutes | No |
| Store facts, light and deep profiles | each store's own pages | Yes, about 1.5 hours | Nice to have |
| **Feed snapshots** (new, absent, repriced, availability flips) | each store's `/products.json`, one point per week | **No**: yesterday's feed is gone | **Yes** |
| **Review counts** (review velocity) | product-page structured data | **No** | **Yes** |

Only the forward-only series need durable storage. The container loses `data/private/` on restart, which is the one blocker for the weekly series.

## Layers

| Layer | What | Status |
|---|---|---|
| Clock | daily Tranco rank; weekly feed snapshot and review counts for a watchlist; monthly profile refresh and relabel | cadence defined, scheduling waits on storage |
| Capture | `scout.stores ranks` (backfill any dates), `scout.snapshot_job run` (feed + reviews), `scout.stores light/deep` | built and tested |
| Change model | `scout.snapshots.diff` (new, absent-from-feed, repriced, availability flips, completeness gate), `snapshot_job diff` (adds review delta) | built and tested |
| Series marts | `mart_store_rank_trend` (slope, volatility, first seen, emerged, breakout, fading) | **built today** |
| Reports | weekly "movers": counts of rising, emerging and fading stores per category (aggregates only); store-level lists stay private | next |

## What the rank history already shows (26 dates, 2 years)

Of 30,365 Shopify stores: **1,120 emerged** in the last 9 months (absent from every older list, present on 3+ recent lists, inside the top 500k), **1,286 rose** at least 2x against their older level, and **1,087 are fading** at least 2x. Copyable stores rise at about the same rate as the rest (4.6% against 4.2%), so "copyable" does not mean "stagnant". An early version flagged 51% of stores as emerged because stores hovering at the 1M cutoff drop in and out of the list; the rule now requires a solid presence.

## Feature definitions (so the numbers are explainable)

- **Rank now / first seen / best / worst**: from the lists we hold; absence means rank above 1,000,000.
- **slope_90d**: change in ln(rank) per 90 days; negative = traffic rising.
- **rank_volatility**: standard deviation of ln(rank); high = unstable, treat with care.
- **growth_old_to_recent**: ln of (median rank 270+ days ago ÷ median rank in the last 90 days).
- **emerged**, **breakout**, **fading**: thresholds above; all flagged `[proxy]` (rank is popularity, not visits).
- Limits: Tranco is a 30-day average of five sources, so it lags real changes by weeks; list dates are sparse (weekly for 12 weeks, then monthly).

## Cadence and cost

| Job | Cadence | Cost |
|---|---|---|
| Rank list (all stores) | daily or weekly | one download, seconds |
| Feed snapshot + review sample, watchlist of about 300 stores | weekly | about 20 minutes at 4 workers |
| Light screen of new US stores | monthly | about 40 minutes |
| Deep profile refresh | monthly | about 1 hour for 300 stores |
| Business-model relabel | on rule change | seconds |

## Build order

1. Rank history marts (done); show movers in the report.
2. **Persistence** (owner decision 0012) so weekly series survive container restarts.
3. Watchlist: the strongest copyable stores plus the strongest brands in niches we shortlist.
4. Weekly scheduled run (Routine) that snapshots, syncs and reports.
5. Alerts: a store that breaks out, goes out of stock across its catalogue, or reprices broadly.
