# UI/UX brief (design phase, no production build yet)

> 2026-11-05. Owner: "we don't need to work on UI for now but let's think about it", then "open a new session for UI/UX". Scope: **design and a clickable prototype**, not an app. A production build waits for the hosting and storage decision (`docs/plan/autopilot.md`) and a phase of its own (CLAUDE.md principle 1).

## Who uses it

1. **Owner, now**: decide which niches and stores matter, review leads, watch the autopilot.
2. **Later, maybe**: agencies or clients, if the service or SaaS idea goes ahead (`docs/plan/opportunity-store-rescue.md`). Design so store-level private data can be hidden per audience.

## Principles

- **No spreadsheets.** Progressive disclosure: a card first, the evidence one click away, the raw numbers two clicks away.
- **Every number shows its label**: `[data]`, `[proxy]` or `[unknown]` (CLAUDE.md principle 2). Never show a proxy as sales or profit.
- **Every claim has a "verify" link** to the public page it came from, and the date it was seen.
- **Decisions, not dashboards.** Each screen ends in an action: shortlist, skip, watch, draft a message.
- **Explain every score** (principle 4): a score opens its inputs and weights.

## Views to design

| View | Question it answers | Data that exists today |
|---|---|---|
| **Niche board** | which niches have proven winners and supply? | niche scores, store marts, CJ supply check (`make niches`, `docs/shortlists/`) |
| **Store card and side panel ("Success key")** | what does this store sell, how does it get traffic, where does it source, is it growing? | `web_store_deep/light`, rank history (26 dates), `web_fingerprints` (supply source, apps), `web_reviews`, `scout.store_intel` stories |
| **Supply view** | where do dropshippers source, and can we get the same from CJ? | fingerprints supply estimate, CJ catalogue warehouse |
| **Lead inbox** (parked idea) | which funded stores have a verified, fixable problem? one card per lead: problem, evidence, verify link, draft message, approve or skip | flags listed in `opportunity-store-rescue.md` (partly collected) |
| **Autopilot health** | did the jobs run, what failed, what changed? | run log (`python -m scout.store runs`), usage counters (`scout.llm --usage`, `scout.unblock --usage`); heartbeats not built yet |

## Deliverables of the design session

1. Information architecture and user flows for the five views.
2. Wireframes, then a **clickable prototype** (a private claude.ai artifact) using anonymised or aggregate data; no real store lists in anything shared.
3. A **data contract**: for each card and panel field, the mart or dataset and column it comes from, and the gaps (what we would need to collect).
4. A stack recommendation recorded in `docs/decisions/` (owner's shortlist: Next.js, React, Tailwind, shadcn/ui, Tremor on Supabase; alternatives such as Evidence or Streamlit over DuckDB for an internal-only first version), per "reuse before build".

## Out of scope

Production code, hosting, authentication, a database migration, sending email.

## Progress

- 2026-11-05: step 1 (small first) done: store card + side panel and lead inbox card as a clickable prototype (private artifact, invented data), IA and flows, and the data contract for those two views: `docs/design/ui-v0-store-card-and-leads.md`. Waiting for owner feedback before the other three views and the stack note.
