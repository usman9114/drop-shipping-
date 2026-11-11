# 0018 — UI stack: private artifact first, Next.js on Supabase when a second user appears

> 2026-11-11. Owner: "start working on UI". Brief: `docs/plan/ui-ux-brief.md`; design and data contract: `docs/design/ui-v0-store-card-and-leads.md`. This note is the stack recommendation the brief asks for ("reuse before build").

## What the first version must do

One user (the owner) studies stores and niches on real data, sees where dropshippers source, watches the autopilot, and marks stores Shortlist / Watch / Skip. Store names are private (CLAUDE.md terms gate), so the page must not be public and the data must not be in git.

## Candidates

| Candidate | License / cost | Maintenance signal | Fit for version 1 |
|---|---|---|---|
| **Private claude.ai artifact** (one HTML page + a data file published beside it) | included in the owner's plan, no hosting, no account | hosted by Anthropic; already holds the Store Data Vault (decision 0012) | private by default, opens on phone and desktop, no auth to build. Limits: data is a snapshot refreshed by a session, decisions are saved in the browser only |
| Next.js + React + Tailwind + shadcn/ui + Tremor on Supabase (owner's shortlist) | MIT / Apache; Vercel hobby and Supabase free tier | all very active | the right production stack, but needs hosting, login, row-level security and Postgres tables that do not exist yet (0016: "Postgres tables come later, when the UI needs them") |
| Evidence.dev over DuckDB | MIT, free | active | good for reports, weak for cards, panels and decisions |
| Streamlit over DuckDB | Apache-2.0, free | active | fast to write, but needs a host and a login in front of private data |

## Decision

1. **Version 1: private artifact "Store Scout"**, fed by `scripts/ui_export.py`, which writes one JSON file from the warehouse (`data/private/ui/store-scout.json`, gitignored). The page (`ui/store-scout.html`, committed, holds no data) reads that file. The JSON's shape is the data contract in code: when the production app comes, it reads the same fields from Postgres.
2. **Version 2, when a second user or daily freshness is needed: Next.js + shadcn/ui + Tremor on Supabase** (the owner's shortlist), with Supabase Auth and row-level security. Trigger: the owner wants to share it with a client or agency, or wants decisions synced across devices. It needs a phase of its own (principle 1) and the owner's approval for a Vercel account.

`HOMEGROWN`: only `scripts/ui_export.py` and the page itself (domain presentation). No framework is added; the page is plain HTML, CSS and JavaScript.

## Rules the page follows (from the brief)

- Every number carries a chip: DATA, PROXY or UNKNOWN. No proxy is shown as sales or revenue; the gaps (revenue, orders, ad spend, margin) are listed on every store panel.
- Card first, evidence one click away, raw fields two clicks away.
- Every score opens its inputs and weights. The weights are exported by `ui_export.py` from one place (`SCORE_WEIGHTS`), not typed into the page.
- Every screen ends in a decision. Decisions are the only thing the UI writes; in version 1 they live in the browser and can be copied out as text.
- Store names appear only in the private data file. Nothing store-level is committed.

## Known limits of version 1

- Snapshot, not live: refreshed by running `python scripts/ui_export.py` and republishing the data file.
- Decisions are per browser; a "Copy decisions" button exports them. A `ui_decisions` table arrives with version 2.
- The lead inbox stays design-only: its flags are not collected yet (`docs/plan/opportunity-store-rescue.md`), and outreach is not an approved phase.
