# Estimating sales and profit: how we think about it

> 2026-11-04. Owner request: "how do we get a good estimation of their profit and sales". Standing rule: label every number `[data]`, `[proxy]`, `[estimate]` or `[unknown]` (`CLAUDE.md`, principle 2). Public records never show a store's revenue, ad spend, orders or margin, so we estimate with ranges and prove the method on stores whose revenue is public.

## The three questions

| Question | Evidence to seek |
|---|---|
| **Are people buying?** | Disclosed sales, explicit sold counters, recent verified-purchase reviews, sustained activity across several independent stores |
| **Could we profit?** | Our supplier quotes, shipping, fees, expected returns, acquisition-cost limits |
| **Can we reproduce the offer?** | Product quality, delivery promise, differentiation, access to customers |

The key move: **we do not need a competitor's profit.** We need to know whether people buy this product (Q1) and whether *we* would profit selling it with *our* costs (Q2). A competitor's margin is unobservable and mostly irrelevant; our own margin is computable.

## Q1: are people buying? Signals, strongest first

| # | Signal | How it becomes units or revenue | Label | Data cost | Error band |
|---|---|---|---|---|---|
| A | **Disclosed sales** (public filings, a store's own published totals, sold counters on listings) | read directly; treat on-page "N sold" widgets as suspect unless they match other signals | [data] | low | small |
| B | **Review velocity**: weekly snapshots of the public review count (already read from the product page's structured data) | new reviews per week ÷ review rate (share of buyers who review; published range to be sourced, doc 23) | [estimate] | low, needs 3+ weeks | about 3x until the review rate is sourced |
| C | **Sold-out flips and restocks** in the product feed (variant `available` true → false) | demand pressure, not units | [proxy] | low | ordinal only |
| D | **Top-down revenue**: visits × conversion × order value | visits from a Tranco-rank curve calibrated on known stores; conversion and order value from sourced benchmarks (doc 22); order value from the store's price band | [estimate] | low | wide; measured on the calibration set |
| E | **Cross-store consensus**: the same product type rising across several independent stores (rank trend, release rhythm) | confidence, not size | [proxy] | already built | n/a |

**Evidence grade per niche:** A = three or more independent signals agree; B = two; C = one. A niche with grade C is not recommended however large its estimate.

Every estimate is a **low / base / high range** with its method named; no single revenue figure is published as a fact.

## Q2: could we profit? Our own numbers

Per product, from `scout.margin` (already built): our listing price minus CJ cost and US shipping quote, marketplace fee, payment fee, expected returns (8%) and an ad rate (5% to 7%), giving **profit per unit and the maximum we can pay to acquire a customer**. Inputs come from our supplier quotes in the sourcing phase; in R1 the supply sanity check gives only a price-to-cost ratio. Paid-traffic stores (Meta, TikTok) have a customer-acquisition cost that eBay search does not, so a niche that wins on social ads on Shopify may or may not work through eBay search.

## Q3: can we reproduce the offer? A checklist, not a number

| Part | What we look at | Source |
|---|---|---|
| Product quality | rating and review count on the sampled product | store page [proxy] |
| Delivery promise | the store's shipping reach (`ships_to_count`) against CJ US-warehouse delivery times | meta + CJ quote |
| Differentiation | price against CJ cost; whether the image set is ours to license | CJ listing, rules |
| Access to customers | which channels the store uses (paid social, email, SMS, affiliate) and which of those we can use | homepage tags |

## Calibrating the estimator (so we know how wrong it is)

1. Find 10 or more stores on Shopify whose revenue is public (filings, press); research doc 24 collects them with sources.
2. Run method D on those stores. Report predicted against actual and the error band.
3. Rule: if the typical error is worse than 3x, method D is used **only to rank** stores, never to state a level.
4. Where both B and D exist for a store, compare them; a big gap flags a bad input.

## Build order (small first: 20 stores, then 200, then the full list)

1. **Start the review-count time series now** (weekly snapshot of the top profiled stores) because it needs weeks to mean anything.
2. `scout/estimate.py`: pure, tested functions for B and D with ranges; test on the calibration set.
3. Add estimate columns (low/base/high, grade) to the store marts and to the stories' evidence pack, so every story number stays grounded.
4. Q2 with real supplier quotes in the sourcing phase.

## What we will not do

Scrape ad libraries or any site whose terms forbid it; use eBay API data for statistics; buy a paid estimator (StoreLeads, Similarweb) without the owner's approval; present an estimate as revenue. A paid estimator, if approved, is used on about 10 stores to compare against our range, not as our source.

## Research feeding this plan (written by the research agents)

- `docs/research/22-shopify-conversion-aov-benchmarks.md`: conversion, order value, ad share, returns
- `docs/research/23-reviews-and-sales-velocity.md`: review rate, sold-out flips, best-seller ordering
- `docs/research/24-traffic-calibration-and-public-revenue.md`: rank to visits, calibration set, paid estimators
