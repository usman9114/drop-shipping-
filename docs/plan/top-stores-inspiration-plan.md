# Plan: find top-performing Shopify stores to take inspiration from

> 2026-11-04. **Approved by the owner 2026-11-04.** Phase 2 revised after the pilot (see the end). Owner doubt: "all I want is to figure out how I can get top Shopify stores who are performing well so I can take inspiration from them. Is this approach even good?" This plan re-scopes release R1 around that goal. Standing rules (`CLAUDE.md`) apply: free first, small first, label what we know, terms before automation.

## Is the current approach good? An honest verdict

**Good at:** finding popular Shopify stores at scale, for free and repeatably (30,365 found), and reading what each one does: catalogue, prices, release rhythm, marketing tools, rank trend over 2 years.

**Weak at the thing you asked for, "performing well":**

1. **Rank is popularity, not performance.** Tranco ranks how much a domain is visited. It says nothing about sales or profit. A content-heavy or deal-heavy site can outrank a more profitable store.
2. **We miss stores.** We only count a store if its domain points at Shopify's address range. Big stores behind a custom CDN or proxy are invisible. The miss rate is unmeasured.
3. **The top is skewed.** The best-ranked Shopify stores are book retailers, Pakistani and Japanese fashion chains, and smart-home brands. Good to study, but not a clean "winners to learn from" list.
4. **We optimised for the wrong filter.** Most of the effort went into a "copyable by dropshipping" label (about 80% accurate, only about 5% of stores). For **inspiration**, a brand with great marketing is just as valuable. The copyable question belongs to a later sourcing step, not to finding winners.
5. **No proof of performance.** We never check independent evidence that a store is doing well (growth lists, press, customer reviews, ads running).

**Verdict:** keep the discovery engine as a **candidate generator**. Add independent evidence of performance. Drop the dropship-first filtering. Study winners first; decide what is copyable afterwards.

## What "performing well" will mean

A store gets an **evidence grade**, never a revenue figure (`[unknown]` stays unknown):

| Signal | Where it comes from | Strength |
|---|---|---|
| Traffic level and 2-year trend | Tranco history (built) | proxy |
| Hard growth proof | Inc. 5000, Deloitte Fast 500, funding, public filings, disclosed revenue | **hard** |
| Customer proof | review volume and rating on the store, third-party review sites | medium |
| Marketing intensity | ad pixels, email/SMS, affiliate tools (built); ads currently running (owner, manual) | medium |
| Longevity and product activity | "existed by" date, release rhythm (built) | weak |
| Press, awards, partnerships | agent web research | medium |

**Grade A** = three or more independent signals including one hard signal. **B** = two. **C** = one. We study A and B stores.

## Team and work

Model rules: free GLM and OpenRouter free lanes for bulk, Haiku agents for research, Sonnet agents for build, Opus advises. Paid Claude routes stay off.

| Role (agent) | Work | Output |
|---|---|---|
| **Head of marketing** (Opus, advisor) | Owns the definition of "performing", picks the final 50, writes "what to borrow" | `docs/decisions/0010-top-stores.md` |
| **Data engineer** (Sonnet) | Measure and fix discovery gaps: detect Shopify by response headers, not only DNS, on a sample of non-Shopify-IP domains in the top 200k; keep pipelines resumable | miss-rate figure, wider candidate pool |
| **Data analyst** (Sonnet) | Candidate pool of about 300 US-relevant stores (any business model) ranked by traffic, trend and marketing; performance score and grades | `mart_store_performance`, pool CSV (private) |
| **Market researchers** (Haiku, many in parallel, 10 stores each) | Proof of performance per store: growth lists, funding, press, awards, review-site volume, social presence; terms checked before any source | `docs/research/3x-*.md` batches, evidence table |
| **Creative producer** (Sonnet) | Study, not copy: positioning, offer structure, page layout, photography style and copy patterns, in written notes only (no images, no text copied) | one dossier page per top store (private) |
| **Sales lead** (Sonnet) | What the winners charge, offers and bundles, discount habits, upsell patterns; later, unit economics | price and offer patterns table |
| **Compliance officer** (Sonnet) | Terms of every source before ingest; IP and policy limits on "inspiration" (ideas, not content) | veto and notes |
| **GLM coder** (free) | Boilerplate, tests, scripts | reviewed by Opus before commit |
| **Owner** | Manual sources the terms forbid us to automate; approvals | see below |

## Phases (small first: a 10-store pilot before every sweep)

**Phase 1: Is discovery good enough? (about half a day)**
- Data engineer: take 500 non-Shopify-IP domains from the top 200k that look like stores, test for Shopify by headers, report the miss rate. If more than 15% are missed, add header detection for the top 200k.
- Analyst: build the candidate pool of about 300 US-relevant stores (rank, trend, marketing, any model).
- Exit: miss rate known; pool exists.

**Phase 2: Proof of performance (about 1 day)**
- Pilot: researchers grade 10 stores. Check the evidence table makes sense; then sweep the pool in parallel batches.
- Owner (30 minutes): Meta Ad Library and TikTok Creative Center, top 20 stores (their terms forbid automation; manual only).
- Exit: every candidate has a grade; at least 50 are grade A or B.

**Phase 3: Dossiers on the top 50 (about 1 day)**
- Deep profile (marketing stack, catalogue, price, rhythm) for all 50; creative and sales studies; compliance notes.
- Exit: one dossier per store, with what they sell, who they sell to, price, offer, how they get traffic, how long they have run, and **what to borrow**, plus gaps named.

**Phase 4: Patterns and playbook (half a day)**
- Opus synthesises: what the winners have in common by niche and size; which ideas transfer to a small new store; which niches repeat among winners.
- Exit: ranked list of 50, pattern report, niche shortlist, and the **copyable** lane as a side result (about 5% of stores, already built).

**Phase 5: Keep watching (ongoing)**
- Watchlist of the 50 on the temporal system: weekly rank, feed changes, review counts. Needs the storage decision (`docs/decisions/0012-temporal-storage.md`).

## Owner tasks

1. **Approve this re-scope** (or tell me what to change).
2. **Meta Ad Library and TikTok Creative Center** session for the top 20 stores (30 minutes; runbook in `docs/research/20-source-pilots-scorecard.md`).
3. **Storage decision** for weekly snapshots (0012), whenever you are ready.
4. Optional, needs approval: a one-month trial of one paid store-estimate tool on about 10 stores, only to compare against our grades.

## What we stop doing

- Tuning the business-model classifier for accuracy beyond what Phase 4 needs.
- Treating "copyable" as the main filter. It becomes one column.
- Scaling the light screen to every US store before Phase 1 shows what is missing.

## What we keep (already built)

The 1M scan and rank history, store profiler (catalogue, price, rhythm, marketing stack), rank-trend marts, snapshot job, report generator, grounded store stories, and the model lanes.

## Risks

- A store that performs well may show no public proof; grade C and honest.
- Ranks lag by weeks; breakouts are late signals.
- Inspiration can slide into copying: the rule stays "copy the method, never the content" (no copied text, images or product listings).

## Revision after the Phase 2 pilot (2026-11-04)

Pilot (`docs/research/29-proof-of-performance-pilot.md`): 10 stores, **A 0, B 2, C 4, D 4**. Independent proof is rare for mid-size stores; search snippets gave wrong numbers three times; two domains could not be tied to a real company; Trustpilot's terms forbid collection, so it is out.

Changes:

1. **Grade every store first from our own evidence**, which we hold for all of them and which is free: traffic level, 2-year rank trend and stability, release rhythm, marketing intensity (ad pixels, email, SMS, affiliates), longevity ("existed by"), catalogue size. This becomes `performance_grade` in the warehouse, with the inputs shown.
2. **Identity check before any research:** is the domain tied to a real company (legal name on the store's own pages, contact page, about page)? Unresolved identity = do not recommend.
3. **External proof only for the top 50**, not 300: company sites, press, growth lists (Inc. 5000, Deloitte), funding announcements. Every number from a fetched page with a date; snippets are leads, never evidence. Each new source's terms are read before use; sources that forbid collection (Trustpilot) are skipped.
4. **Rebalance the pool:** the growth weight pulled in fast-rising but obscure stores, which rarely have public proof. The pool becomes two slices: the 150 strongest by traffic level (established winners) and the 150 strongest risers.
5. **Owner's manual ad check** (Meta Ad Library, TikTok Creative Center) stays the best independent sign that a store is spending to grow; it covers the final top 20.

## Phase 2 result (2026-11-04)

Top 50 researched (doc 30): established slice A 2, B 10, C 6, D 7; riser slice A 0, B 2, C 2, D 21. **Decision:** the study set is the established stores with at least one independent sign of performance; risers go to the watchlist until they show proof. Identity rule corrected (a brand with contact details, tied to a named company by its own pages or one independent source); strict-rule failures re-graded.
