# Phase: Niche Finder, release R1

> 2026-11-04. Defines the goal of the current phase, what ships in release R1, and how we know it is done. It sits inside Phase 0 of `docs/research/00-summary.md` (desk feasibility, $0). Method and terms: `docs/decisions/0009-best-store-discovery.md`. Flow: `docs/plan/step1-flow.md`. Owner decision (2026-11-04): step 1 is finding the best stores and what they do, with no supplier work beyond a sanity check; sourcing is the next phase.

## Goal

R1 finds a **shortlist of niches**, not the single best product. Picking products is the sourcing phase.

**Produce an evidence-backed, reproducible shortlist of niches for a US zero-inventory seller, found by studying the best online stores and what they do, and ready to hand to sourcing.**

One command (`make niches`) reproduces it from open data. One decision pack tells the owner which niches to source first, with the evidence and the gaps.

## What R1 contains

| # | Deliverable | Where | Committed? |
|---|---|---|---|
| 1 | Shopify store list from the full Tranco top 1M, with scan coverage per batch | `data/private/lake` | no (private) |
| 2 | Store profiles: catalogue, release rhythm, price band, vendors, categories, marketing stack, business model, rank growth | `mart.mart_store_profile` | no (private) |
| 3 | Ranked "best stores" report: categories won, traffic stack, brand vs copyable | `docs/reports/<date>-best-stores.md` | yes, aggregates only |
| 4 | "How they did it" stories for the top stores, every number grounded, gaps named | `data/private/reports/` | no (names stores) |
| 5 | Niche shortlist with scores and exclusions | `docs/shortlists/<date>-niche-candidates.csv` | yes |
| 6 | Supply sanity check per shortlisted niche (CJ matches, price-to-cost) | `docs/shortlists/<date>-supply-sanity.csv` | yes |
| 7 | Compliance screen of the shortlist (veto) | `docs/reviews/<date>-niche-compliance.md` | yes |
| 8 | Decision pack: ranked niches, evidence, risks, recommended first niche | `docs/decisions/0010-niche-finder-r1.md` | yes |
| 9 | Validation record: classifier accuracy and known error rates | in the decision pack | yes |
| 10 | Git tag `niche-finder-r1` on the release commit | repo | yes |

## Exit criteria (R1 is done when all hold)

**Coverage**
- Full top-1M scan finished, every batch recorded, resolve rate reported.
- At least 600 US dollar-priced stores deep-profiled, at least 90% answered without error.
- Rank history attached for stores that appear on the 90- and 365-day Tranco lists.

**Quality** (we measured errors early, so each gets a gate)
- **Business model:** hand-check 30 stores spread across brand, reseller, dropship and unclear. At least 85% agreement. A free model (GLM, then a free OpenRouter model) gives an independent second opinion on the same 30. Disagreements are fixed in the rules and listed.
- **Categories:** "other" (unclassified) below 15% of profiled stores, after rule fixes.
- **Stories:** top 40 stores written; share that passed the numbers check reported; any template fallback labelled.
- **US filter:** zero non-USD stores in the profiled set (test already in place).

**Shortlist**
- At least 5 niche candidates, each with at least 5 copyable stores (reseller, dropship, print on demand or unclear), no excluded category, and an entry price in the 12–80 USD band.
- Every candidate carries: score, store count, median entry price, release rhythm, rank trend, traffic stack, and what is unknown.

**Supply and compliance**
- Supply sanity run for every candidate. A candidate passes if CJ returns at least 20 matching products with US-warehouse stock for at least 2 of its 3 phrases, and median store price is at least 2.5 times median CJ cost.
- Compliance officer reviews the passing candidates; any veto removes that niche.
- At least 3 niches survive, ranked, with one recommended for sourcing.

**Reproducibility and hygiene**
- `make niches` runs from a clean clone plus the environment variables.
- `make test` and `pre-commit run --all-files` pass; no raw store data, domains or personal data in git; no AI attribution in commits.

## Out of scope for R1

- Sourcing, supplier orders, listing creation, images, eBay listings (next phases).
- Any use of the eBay API for data, any CJ ordering or repricing (License 9.6, decision 0004).
- myip.ms in any automated form (terms forbid it; API only if the owner buys access).
- Estimating revenue, ad spend or margin of a store (not observable; named as gaps).
- Non-Shopify platforms (WooCommerce, BigCommerce, marketplaces) and non-US markets.

## What I still fix before calling R1 final

Known weaknesses found while building, with the fix and the gate that proves it:

| Weakness | Fix | Proof |
|---|---|---|
| Stores that point only `www.` at Shopify are missed by the apex DNS check | Add a `www` CNAME check for a sample of non-hits and report the miss rate | miss rate stated in the report |
| Review counts found on only 18 of 110 stores | Treat as a stated gap, drop review counts from the score | gap listed in every story |
| Product feed sample is the newest 1,000 products | Report sample size; add last page for the oldest | `products_sampled` in each profile |
| Brand vs dropship rules were wrong in 11 cases once | Hand-check plus Haiku second opinion (above) | accuracy figure |
| "Existed by" is an upper bound, not a launch date | Always word it as "existed by" | story check |
| Shopify success shows demand and method, not eBay demand | Carry as a risk on every niche; the live micro-test (later phase) measures eBay | risk row in decision pack |

## Stages and who does the work

Owner rules: **phase one uses free models only** (GLM, then free OpenRouter models; Haiku and Sonnet stay off unless `SCOUT_ALLOW_PAID=1`, which needs the owner's say-so). Opus advises and reviews.

| Stage | Work | Runs on | Output |
|---|---|---|---|
| S1 Discover | Finish the 1M scan (about 1 h 40 m left at 8 of 20 batches), `/meta.json` for all hits | scripts, no model | store list, coverage |
| S2 Profile | Deep profile of top 600+ US stores; rank history | scripts | `mart_store_profile` |
| S3 Validate | 30-store hand check; free-model second opinion; fix rules; rerun | free models + owner spot check | accuracy figure, rule fixes |
| S4 Score and story | Rerun marts; stories for top 40 | GLM, then free OpenRouter models | report, stories |
| S5 Shortlist | Niche scoring, exclusions, k-floor | SQL and `store_export.py` | shortlist CSV |
| S6 Sanity | CJ search per niche | existing CJ key, no cost | sanity CSV |
| S7 Compliance | Policy, IP, safety screen | `compliance-officer` agent (Sonnet) | review file, vetoes |
| S8 Release | Decision pack, `make niches`, tag, graph refresh | Opus reviews; scripts | R1 tag |

**Model spend for R1: 0 USD.** Free models only; the OpenRouter credit stays untouched so the higher free-tier daily limit stays unlocked. Paid Haiku/Sonnet are for a later phase.

## After R1 (not part of this phase)

1. **Sourcing phase:** for the top niche, match real CJ products, landed cost and delivery time (CJ US warehouse is thin; the earlier supply check failed for card supplies).
2. **Listing-quality phase:** supplier-licensed images, accurate descriptions.
3. **Live micro-test:** 3–5 margin-viable products on eBay, measure real sales. This is the first step that sees eBay demand.

## Decisions needed from the owner

1. **Approve R1 scope** as above (Shopify-only discovery, US, free models only).
2. **myip.ms API:** pay for access or skip? Default: skip, the Tranco scan covers it.
3. **archify skill:** allow the install script (diagram skill), or skip? Default: skip; Mermaid images are enough.
