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

## Lessons from similar open-source projects (owner review, 2026-11-04)

| Project | Verdict | What we take |
|---|---|---|
| Shopify-Scout | real code, weak estimation | **Reject its constants.** It assumes 50 visitors per product, 200 per collection and 150 per review with no calibration, and can turn inventory decreases into "units sold". We use no fixed per-item visitor counts and never call a stock drop a sale. |
| ShopIntelligence | inspiration only; no licence found, so no code is copied | Comparisons across stores, and warnings when a catalogue is incomplete. Its "velocity" counts new products, not sales: ours is called **release rhythm** and is never presented as sales. |
| shopify-price-monitor | best reference (MIT) | Snapshots of price and availability and comparisons between them. Needs two fixes we build in: **detect removed items**, and **honour the server's Retry-After** instead of retrying sooner. |
| shopify-stores-api | hosted service, no estimator to audit | Nothing; revenue accuracy unverified. |

Rules that follow: every constant in an estimator cites a source and a range; an incomplete snapshot never reports removals; availability flips are a demand proxy, not units. The audit of the four repos is in `docs/research/25-similar-repos-audit.md`; the snapshot code is `scout/snapshots.py`.

## What we will not do

Scrape ad libraries or any site whose terms forbid it; use eBay API data for statistics; buy a paid estimator (StoreLeads, Similarweb) without the owner's approval; present an estimate as revenue. A paid estimator, if approved, is used on about 10 stores to compare against our range, not as our source.

## What the research found (docs 22 to 24) and what it changes

| Finding | Source quality | Consequence |
|---|---|---|
| Median Shopify conversion is about 1.3% (top 20% 2.7%); fashion and home about 1.0%, beauty about 2.6% | one 2026 benchmark of 438 stores, reached through a mirror, `[unverified]` | use 1.0% / 1.3% / 2.7% as low / base / high |
| Average order value ranges from about $85 to $312 across sources | weak, disagree by 10x | take order value from the store's own price band, not from a benchmark |
| Review rate is only vendor-quoted: 2.5% to 5% typical | vendor blogs, no study | units = reviews ÷ rate carries a 4x to 40x band, so review-based units are `[proxy]` |
| No published rank-to-visits mapping exists (Tranco, CrUX, Cloudflare Radar publish ranks or buckets, not visits) | checked three sources | **a visits figure from rank is an estimate with no calibration** |
| Strict calibration set is 2 stores (BARK, Allbirds), target was 10 | filings | **method D cannot be validated yet** |
| Paid estimators (StoreLeads, Similarweb, Semrush): terms and prices unread or conflicting | unpiloted | none used; needs owner approval |

**Decisions that follow**

1. **R1 states no revenue levels.** Method D (visits × conversion × order value) is used **only to rank** stores until the calibration set reaches 10 stores. Ranking inputs are rank, rank trend, release rhythm and the marketing stack, which we already have.
2. **Review velocity (B) is the primary sales signal for R1**, kept as relative velocity (reviews per week, higher or lower than peers), not units. The unit figure is shown only as a wide band, labelled `[proxy]`.
3. **Widen the calibration set.** Result of the automated attempt (doc 26): the SEC's full-text search blocks automated tools (HTTP 403), so we did not use it; the search found 0 strong and 1 partial entry (a company moving to Shopify, with dollar revenue) and 4 weak vendor case studies with no totals. **Owner task (manual, about 30 minutes):** run the SEC full-text search in a browser for "run on Shopify", "built on Shopify" and "Shopify Plus", and list companies with revenue; UK Companies House for Shopify UK brands is the second route. Until the set reaches 10, method D stays ranking-only (decision 1).
4. **Record which review app and which structured-data field** each store uses (the research could not confirm which field each app fills); snapshot jobs record the review-app name so counts compare like with like.
5. **Shopify's default robots rules disallow sorted collection URLs**, so we never fetch best-seller sort pages. Unsorted collection order and sold-out flips are tie-breakers only.
6. **Owner decision (optional):** approve a trial of one paid estimator on about 10 stores, only to compare against our ranges. Default: no.

## Research feeding this plan (written by the research agents)

- `docs/research/22-shopify-conversion-aov-benchmarks.md`: conversion, order value, ad share, returns
- `docs/research/23-reviews-and-sales-velocity.md`: review rate, sold-out flips, best-seller ordering
- `docs/research/24-traffic-calibration-and-public-revenue.md`: rank to visits, calibration set, paid estimators
