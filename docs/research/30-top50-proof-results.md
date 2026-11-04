# 30 — Proof of performance for the top 50 candidate stores

> 2026-11-04. Phase 2 of `docs/plan/top-stores-inspiration-plan.md` (revised after the pilot, doc 29). Five Haiku research agents, 10 stores each, in parallel. Store-level evidence with URLs stays in `data/private/research/top50-batch-*.md`; this file holds aggregates only.

## How the 50 were chosen

From the 300-store pool (`mart_candidate_pool`), stores with **own-evidence grade A** (4 or more of: traffic inside the top 150,000, rank up 35% or more, about 2 years steady in the top 1M, 20+ products added in 90 days, active ads or ads plus email/SMS), big multi-brand retailers excluded: **25 established** stores (strongest traffic) and **25 risers** (fastest rank growth).

## Result: independent proof grade

| Slice | A | B | C | D |
|---|---|---|---|---|
| Established (25) | 2 | 10 | 6 | 7 |
| Risers (25) | 0 | 2 | 2 | 21 |

A = 3+ independent signals including one hard signal (filing, disclosed revenue, funding, acquisition, named major retailer, employee count); B = 2; C = 1; D = none. Every number had to come from a fetched page with a date.

## What this tells us

1. **Established stores are the study set.** 18 of 25 have at least one independent sign of performance: listing filings with revenue growth, funding rounds, named retail partners, design awards. Their methods are worth studying even where they are brands we would not copy.
2. **Fast risers are mostly unverifiable.** 21 of 25 have no independent proof, and 7 of 20 researched in two batches could not be tied to a real business. A sudden rank jump often means a short-lived or anonymous store. Risers stay on the watchlist (temporal system) and are not used as inspiration until they show proof.
3. **The first identity rule was too strict.** Requiring a legal company name on the store's own pages failed several well-known brands (a listed spice company, a decades-old outdoor apparel brand, a known backpack brand). Corrected rule: a brand with contact details, tied to a named company by its own pages or one independent source. Those stores are being re-graded.
4. **Category labels are wrong in a few cases** (a coin dealer labelled hobby, a B2B electronics supplier labelled apparel, a general store labelled home décor). The keyword rules are a first cut; dossiers use the researchers' description.
5. **Safety:** one store's pages showed a pop-up asking for an email and password ("quick verification"), a phishing pattern. It is excluded and nothing was entered.
6. **Search snippets mislead.** As in the pilot, several snippet facts did not match the fetched pages; only fetched, dated numbers count.

## Sources that worked and failed

Worked: trade press (retail and tech outlets), stock-exchange listing documents as reported by press, funding news, official award winner pages, company profile sites, Wikipedia with citations. Failed or blocked: several paywalled or bot-protected sites (403), a stock exchange PDF (404). Not used by rule: Trustpilot (terms forbid collection), Meta Ad Library and TikTok Creative Center (owner checks manually).

## Next

Re-grade the 7 strict-rule cases; write dossiers for the established B and A stores (who they are, what they sell, price, offer, traffic stack, what to borrow); pattern report across them; owner's manual ad check for the final top 20.
