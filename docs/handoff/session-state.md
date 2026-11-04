# Session state: where the project stands

> Written 2026-11-04 so a fresh session can resume. Read `CLAUDE.md` first (binding rules). This file says what is done, what is next, and the traps. It contains no secrets.

## Repo

- GitHub: https://github.com/usman9114/drop-shipping- (**public**). Default branch and working branch: `research/feasibility-poc`.
- Second agent: branch `agent2/review-and-shortlist` is merged (PR #1). For its Part 2 it uses a new branch `agent2/shortlist-engine` (not created yet; no open PRs). Brief: `docs/handoff/agent2-review-and-shortlist.md`. Its paths: `scout/shortlist.py`, `scout/rules.py`, `rules/`, matching tests and docs.
- CI: `.github/workflows/ci.yml` (pytest + pre-commit, no secrets). Last known state: green, 64 tests.

## What exists

| Area | Where |
|---|---|
| Verdict and phased plan | `docs/research/00-summary.md` |
| Niche decision: **trading-card supplies** (backups: vinyl-record care, hobby/modelling tools) | `docs/decisions/0002-niche-selection.md` (24 product types in §3.3) |
| Source terms and what we may store; Postgres **parked** | `docs/decisions/0004-*.md`, `docs/research/17-*.md` |
| CJ client decision (thin, home-grown) and API cheat sheet | `docs/decisions/0005-cj-client.md`, `docs/research/18-cj-api-cheatsheet.md` |
| Independent review of the project | `docs/reviews/2026-11-agent2-project-review.md` |
| Team roles | `.claude/agents/*.md`, `docs/plan/ai-team.md` |
| Code | `scout/margin.py` (decision engine), `scout/cj.py`, `scout/store.py`, `scout/llm.py`, `scout/trends.py`; tests in `tests/` |
| Operating plan (calendar, model routing, €10 use, SaaS option, anti-trap rules) | `docs/plan/operating-plan.md` |
| Manual eBay research kit | `docs/runbooks/terapeak-session.md`, `data/observations/terapeak-prefilled.csv` |

## Facts that change plans

1. **eBay API License 9.6 (seller arbitrage):** no automated ordering from CJ, no posting tracking for CJ-sourced orders, no repricing or stock sync from CJ prices through the eBay API. Order forwarding and tracking upload are **manual**.
2. **eBay API License 8.1.4, 9.5, 9.7, 9.10:** no storing eBay data, no statistics or average selling prices, no price modelling, no ML on it without written permission. eBay market evidence comes from manual Terapeak reading and, later, our own account's data.
3. **CJ API data terms are unconfirmed.** Raw CJ output goes only to `data/private/` (gitignored). Commit derived results only (product id plus our computed metrics).
4. **CJ may disable API access after 30 days with no transaction** [unverified reading]. The key was created around 2026-11-04. Place the first test order within about a month.
5. Google Trends via pytrends is terms-unclear. Do not add pulls; licensed providers (SerpApi, DataForSEO) are the route. Raw points were removed from git.
6. **2026-11-04 live CJ run: `tcg-supplies` fails kill criterion K1** (0 relevant US-warehouse SKUs across 24 types), and both backups fail the same bar. CJ's US warehouse holds only 3,964 products, mostly furniture, women's clothing, beauty and jewelry. Real US→US shipping is ~$5.2–6.0 per light parcel. See `docs/shortlists/2026-11-04-cj-supply-check.md`. **Owner decision pending** between options A (supply-first on CJ US, recommended), B (tcg shipped from China), C (other US supplier).
7. eBay keys in the environment are **sandbox** keys (production returns 401).

## Traps in a fresh container

- **Git identity defaults to an AI name.** The commit-msg hook then rejects every commit. Set `git config user.name` and `user.email` to match the repo owner's existing commits (`git log --format='%an <%ae>' | sort -u`).
- Git hooks are not cloned. Run `make setup`, then `pip install -r requirements.txt -r requirements-dev.txt`.
- `.env` is gitignored and disappears with the container. Keys must come from environment settings. Expected variable names: `CJ_API_KEY`, `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `ZAI_API_KEY`, `OPENROUTER_API_KEY`. Report names only, never values.
- The graphify post-commit hook rebuilds the graph in the background. A commit made during the rebuild can fail with "files were modified by this hook". Wait a few seconds and retry. After committing, stage `graphify-out` and commit again if the tree is dirty.
- OpenRouter credit (€10) bought by the owner on 2026-11-04. See `docs/plan/operating-plan.md` §2 for how it is used.
- OpenRouter key works (credit registered, `is_free_tier: false`). It was pasted in chat on 2026-11-04 and used from a gitignored `.env` for the day; **owner will rotate it**, then add the new one to "Crypto" as `OPENROUTER_API_KEY`.
- Keys live in the cloud environment **"Crypto"** (the one this project's sessions use; "Default" also has them). As of 2026-11-04 `OPENROUTER_API_KEY` is not visible in the container; check the variable name.
- Z.ai and OpenRouter keys were pasted into an earlier chat. The owner was asked to rotate them.

## Next tasks, in order

Calendar: `docs/plan/operating-plan.md` §3. **Approach changed 2026-11-04: supply-first** (owner agreed): score what CJ's US warehouse ships in a DuckDB warehouse (decision 0006), then the owner checks demand by hand in Terapeak (no API exists; automation banned by eBay's User Agreement).

Done 2026-11-04: warehouse slice (`warehouse/`, `make wh-*`), CJ catalogue (3,964) → rules → 268 pre-filtered → offers (cost, US stock, real freight: median $4.80) → **252 pass margin at ≤ $45** (`docs/shortlists/supply-candidates-2026-11-04.csv`). Free GLM wrote product types for the 21% the rules missed and one eBay search phrase per product (both cached as hash → label seeds). Terapeak worklist: `data/observations/terapeak-sheet-2026-11-04.csv` (245 phrases, ranked).

1. **Image screen** (`make wh-images`, main image per viable product) was running at session end; re-run to finish (cache skips done images), then `make wh-build wh-export`. Z.ai's free vision model stalled after 27 images (no reply for 14 min); OpenRouter's `nemotron-3.5-super-vl:free` does ~9 s/image, so run it as `ZAI_API_KEY= make wh-images`. Follow-up: give `scout.llm` a per-call timeout well under 180 s for vision.
2. **Owner fills the Terapeak sheet** (top ~40 rows first, runbook `docs/runbooks/terapeak-session.md`). Most CJ US items are cheap; if singles sell below `price_floor_best`, record the 2- or 3-pack price in `notes`.
3. Load the filled sheet into the warehouse (new seed or `read_csv` source + `mart_shortlist`: avg sold ≥ floor, sell-through ≥ ~50%, ≥ ~20 sold in 90 days), then compliance review and test orders before ~2026-12-01.
4. Stop and ask before spending money, creating accounts, or sending anything outside the repo.

Rebuild in a fresh container: `make wh-load wh-catalogue wh-offers` (~25 min), `python -m scout.ingest_cj images --from-file data/private/candidates.txt`, `make wh-build`. LLM caches are committed, so no model calls are repeated.

## Owner tasks outstanding

Choose option A/B/C (supply check §4); CJ and eBay seller account setup (eBay developer approval pending; current eBay keys are sandbox), Terapeak session, rotate leaked keys, add the 5 env vars to the cloud environment, ask CJ about customer returns and the return address, decide public versus private repo and the commit email, answer the Shopify questions (wife's Instagram details, beauty route, sequencing).
