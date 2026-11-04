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
| Manual eBay research kit | `docs/runbooks/terapeak-session.md`, `data/observations/terapeak-prefilled.csv` |

## Facts that change plans

1. **eBay API License 9.6 (seller arbitrage):** no automated ordering from CJ, no posting tracking for CJ-sourced orders, no repricing or stock sync from CJ prices through the eBay API. Order forwarding and tracking upload are **manual**.
2. **eBay API License 8.1.4, 9.5, 9.7, 9.10:** no storing eBay data, no statistics or average selling prices, no price modelling, no ML on it without written permission. eBay market evidence comes from manual Terapeak reading and, later, our own account's data.
3. **CJ API data terms are unconfirmed.** Raw CJ output goes only to `data/private/` (gitignored). Commit derived results only (product id plus our computed metrics).
4. **CJ may disable API access after 30 days with no transaction** [unverified reading]. The key was created around 2026-11-04. Place the first test order within about a month.
5. Google Trends via pytrends is terms-unclear. Do not add pulls; licensed providers (SerpApi, DataForSEO) are the route. Raw points were removed from git.
6. Only one product type has a modelled pass (25-pack magnetic holders at about $30, **estimated** costs). Everything depends on real CJ costs.

## Traps in a fresh container

- **Git identity defaults to an AI name.** The commit-msg hook then rejects every commit. Set `git config user.name` and `user.email` to match the repo owner's existing commits (`git log --format='%an <%ae>' | sort -u`).
- Git hooks are not cloned. Run `make setup`, then `pip install -r requirements.txt -r requirements-dev.txt`.
- `.env` is gitignored and disappears with the container. Keys must come from environment settings. Expected variable names: `CJ_API_KEY`, `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `ZAI_API_KEY`, `OPENROUTER_API_KEY`. Report names only, never values.
- The graphify post-commit hook rebuilds the graph in the background. A commit made during the rebuild can fail with "files were modified by this hook". Wait a few seconds and retry. After committing, stage `graphify-out` and commit again if the tree is dirty.
- The reminder to buy the $10 OpenRouter credit was bound to the previous session. Re-create it if still needed.
- Z.ai and OpenRouter keys were pasted into an earlier chat. The owner was asked to rotate them.

## Next tasks, in order

1. Set up (above) and run `make test`.
2. With the CJ key present, run `python -m scout.cj search "<phrase>" --country US --pages 1 --out data/private/cj-search.json` for the 24 product types in decision 0002 §3.3. Compare real responses with the "Unknowns" list in doc 18 and fix `scout/cj.py` and its tests where the guesses were wrong. Update doc 18.
3. Pull details and freight for hits, compute margins with `scout.margin`, drop products that break the compliance exclusions (doc 12, decision 0002 §3.6), and write a **derived** shortlist (ids and computed numbers only) under `docs/shortlists/`. If the second agent's shortlist engine has landed, use it instead.
4. If `EBAY_CLIENT_ID` and `EBAY_CLIENT_SECRET` are present, test a client-credentials token only. Use it for category reference data (Taxonomy) at most. Earlier, `api.ebay.com` returned 403 from this sandbox; note whether that persists. Do not store Browse data.
5. Merge in the owner's Terapeak sheet when it exists, re-score the niche, apply the kill criteria in decision 0002 §3.8. If fewer than about 20 products pass, move to the backup niche.
6. Stop and ask before spending money, creating accounts, or sending anything outside the repo.

## Owner tasks outstanding

CJ and eBay seller account setup (eBay developer approval pending), Terapeak session, rotate leaked keys, buy the $10 OpenRouter credit, ask CJ about customer returns and the return address, decide public versus private repo and the commit email, answer the Shopify questions (wife's Instagram details, beauty route, sequencing).
