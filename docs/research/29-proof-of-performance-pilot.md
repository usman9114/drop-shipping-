# 29. Proof-of-performance pilot (10 Shopify stores)

Date: 2026-11-04. Plan: `docs/plan/top-stores-inspiration-plan.md`, Phase 2. Store-level evidence is private (`data/private/research/`, gitignored). This report names no stores.

## Result in one line

Of 10 stores, 0 reached grade A, 2 reached B, 4 reached C and 4 reached D. Only 3 of 10 had any dated hard signal. The pilot shows that the evidence method works but that independent proof is thin for this pool, so the 300-store sweep needs a changed method before it runs.

## Grade counts

| Grade | Rule | Stores |
|---|---|---|
| A | 3+ signals, at least 1 HARD | 0 |
| B | 2 signals | 2 |
| C | 1 signal | 4 |
| D | none found | 4 |

Signal definitions used in this pilot:
- **HARD**: an acquisition, an employee count, funding or revenue, from a dated source. Own-site claims do not count. Modelled revenue estimates do not count.
- **Customer**: a rating and a review count on an independent review site, with a date.
- **Press**: an independent article with a date (trade, local or consumer press).
- **Social reach** is recorded but not graded (see Method).

A signal counts only if it has a URL and a date. A date inferred from a URL is marked as inferred. Undated items were recorded and excluded.

## Method

1. Identity check: read each store's own site (homepage and About page). Record what it sells and any founding or location claim (self-reported).
2. Search per store, standard mode, one query each for hard growth, customer reviews, press and social. Searches run in parallel within a store.
3. Fetch each source that matters. Numbers are taken from the fetched page, not from search summaries.
4. Grade with the rule above. Record conflicts instead of picking one.

Cost: about 42 calls for 10 stores (22 searches, 20 fetches), about 4 per store. Wall time was not measured. The per-store evidence file holds the URLs and dates.

## Which signal types were findable (10 stores)

| Signal | Stores with a dated, usable item | Notes |
|---|---|---|
| HARD: acquisition | 2 | Both from trade press (one fetched; one snippet-only, source returned 403 on fetch) |
| HARD: employee count | 1 | From a dated 2016 press feature; the newer feature gave no count |
| HARD: funding, revenue (disclosed), Inc/Deloitte lists | 0 | Revenue figures found were modelled estimates or unverified |
| Customer rating + count + date | 3 | One store had 1,848 reviews; another had 60 |
| Review page exists, no rating captured | 3 | Not countable |
| Dated press feature | 2 | |
| Notable retail placement, dated | 0 | Retailer product pages were undated |
| Social follower count from an independent source, tied to the store | 0 | One tracker showed a figure that did not fit the store's review count |
| Founding year or location on own site | 4 | Self-reported only |
| Automated scam or security scores | 2 | Not performance evidence |

Other findings:
- Three of the ten review-site pages were missing a rating or count in our pass.
- Most brand-name searches collided with unrelated companies that share a name.

## Sources: useful and useless

Useful:
- Review-site pages fetched directly. They show the rating, count and newest-review date on one page. This was the most reliable customer signal.
- Dated trade and local press. Acquisition and headcount facts came from these, with dates.
- The store's own About page. Good for "who they are" (founding year, leadership, location), always labelled self-reported. Leadership claims on the own site and in other sources disagreed for one store, so we record both.

Useless or misleading for grading:
- Automated scam and security scanners. They rate sites on risk heuristics, not performance. They gave opposite verdicts on two stores' legitimacy.
- Promotional or affiliate review pages. They repeat ratings from the store's own marketing and are often undated.
- Revenue and employee estimates from paid databases. They are modelled, not disclosed. Not used (plan: paid estimators need owner approval).
- Creator-tracker social reach. The figure was implausible for the store's review count and the identity could not be confirmed.
- Undated listicles and retailer product pages. They confirm a placement exists but not when.
- Search summaries. Three facts in summaries did not match the fetched page (an employee count that the page does not contain; two different review counts for the same review site; a leadership date that conflicts with the store's own page). Summaries are leads only.

## Terms concerns

- Review sites: the pilot read public pages one by one through the fetch tool. It did not scrape or log in. Trustpilot's terms on automated access were NOT read or recorded. The sweep must not start until they are, and the owner should decide whether a manual or licensed route is used.
- Scam, security and creator trackers, paid estimators, the acquisition database and promotional review sites: terms not read. Not ingested. Their results are not retained beyond the private pilot file.
- Meta Ad Library and TikTok Creative Center: not opened (owner's manual task).
- Instagram, Facebook, TikTok and Pinterest: links read from store sites only; no profiles opened, no follower counts scraped.
- Store names and domains are kept out of this report.
- Page-level text from sources was not stored. The private file keeps URLs, dates and short facts.

## Recommendation for the 300-store sweep

Keep:
- Review-site rating, count and date, from fetched pages, once the terms are read and recorded.
- Dated trade and local press, fetched, with the date on the page.
- Acquisition checks against a second dated source.
- The own About page for founding, leadership and location (self-reported label).

Drop:
- Scam and security scores as evidence of performance (keep only as a warning note, if at all).
- Promotional or affiliate review pages.
- Modelled revenue or headcount estimates, unless the owner approves a paid trial.
- Social reach from creator trackers until identity is confirmed.
- Undated items, which are excluded.

Add:
- Identity check before evidence collection: the store's name on its own site plus one independent link (registry, trademark, or address match). Stores that fail go to a "not verifiable" list, not into grades.
- Date extraction for every item (fetch the page; do not rely on search snippets).
- Two sources for any HARD fact before it counts.
- A category check: the pool label is a hint; record when the site sells something else.

Batch size and run plan:
- 10 stores per Haiku agent (as in the plan). About 4 calls per store, so about 40 calls per batch.
- Run up to 5 batches in parallel (50 stores per wave). 300 stores = 30 batches, about 1,260 calls.
- Each batch writes its own private evidence file and a count line (graded, identity failures, undated items), so it can restart.
- Stop rule: if a batch has more than 3 identity failures, halt that wave and fix the identity check before continuing.

Expectation: with this method, most stores will land at C or D. Grade A will be rare. The owner should expect that grade B and C are the realistic range for this pool, and that traffic trend and the owner's manual ad-activity check will carry more of the ranking than grades do.

## Open items

- Trustpilot terms read by the advisor on 2026-11-04: the consumer terms, section 4, forbid accessing, searching or collecting content "by any means (automated or otherwise)" and any data mining or scraping without express permission. **Trustpilot is excluded**; its figures were removed from the private evidence file. Other review sites, scam checkers, creator trackers and paid estimators: terms still unread, so not used.
- Two review-count conflicts (one review site showed two different totals across pages) are unresolved; the grade does not depend on them.
- One HARD signal (an acquisition) is snippet-only; the source returned 403 on fetch. Its grade depends on it.
- Owner's manual step (ad libraries, top 20) not started.
- `docs/research/00-summary.md` not updated; this run was scoped to the two files named in the task.
