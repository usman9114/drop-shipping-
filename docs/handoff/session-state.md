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

## Review panel result (2026-11-04) — read before starting

`docs/reviews/2026-11-04-idea-panel.md` (2–3 of 4 free models answered per idea; weak sample):
- **Drop or split:** look-alike discovery (I06), traffic footprint (I07), the warehouse (I11), the intelligence layer (I10), CJ listing count (I05), and studying Shopify stores for an eBay-first test (I08, split or drop).
- **Keep or modify:** live micro-test (I13), jewelry only with changes (I12), supplier-image listings (I03), free LLMs (I14).
- **Shared message:** stop building analysis tooling; list 3–5 margin-viable, compliance-clean CJ US products on eBay and measure real sales.
- **Wrong reasons to ignore:** "Shopify feeds break eBay's API terms" and "this collects personal data" are both untrue.
- **Orchestrator's recommendation:** do both, in this order. First a small live test (3–5 products from the less crowded types: cleaning tools, pet grooming tools, hand tools; CJ test orders also keep the CJ API active). Then use the store-story work for the **Shopify channel** it actually fits.
- **Owner decision (2026-11-04): focus on choosing the product niche and on how successful businesses did it** (store discovery, store stories, recreation plan). The live test comes later. Keep the panel's caution in view: Shopify success is evidence of demand and method, not proof of eBay demand.

## Next tasks, in order (focus from 2026-11-04: reconstruct and recreate store success)

**Focus:** pick successful stores, rebuild the story of how they did it end to end (what they sell, from whom, at what price and margin, since when, how they get traffic), mark the gaps, then turn the story into a recreation plan inside our constraints. Method: `CLAUDE.md` source evaluation standard; decisions 0007 (harness + intelligence layer) and 0008 (internet-metadata harness).

1. **Set up and rebuild local data** (container is ephemeral): git identity, `make setup`, `pip install -r requirements.txt -r requirements-dev.txt tranco`, `make test`, then `make pipeline` (about 25 minutes, mostly CJ offers).
2. **Discover stores** with `python -m scout.webmeta discover --max-dns 1200`, then `sitemaps`, `products` and `footprint` for the Shopify stores found. Improve first:
   - a tighter keyword list (drop noisy words such as "craft" and "mop")
   - a US filter (TLD, storefront currency or shipping country)
3. **Build the store story** as warehouse models plus the intelligence layer:
   - stage the `web_*` lake datasets
   - match each store's products to CJ US products by type and price, to estimate their margin at CJ cost
   - combine with DNS platform signals, traffic tags (ads, email and SMS, affiliates), social links, catalogue size, release rhythm, price band and Tranco rank
   - `scout.intel` writes a grounded "how they did it" story per store (every number from the evidence, gaps named), then a **recreation plan**: product mix, price points and channels we would copy within C1 to C8, with eBay first
4. **Review panel:** `python -m scout.review_panel` fills any missing reviews (cached). Read `docs/reviews/<date>-idea-panel.md`, especially I06 to I08 (does studying Shopify stores serve an eBay-first test?). Act on drop consensus or split votes.
5. **Velocity:** `make wh-snapshot` once a day. History needs durable storage; the owner's choice is still open (private data repo recommended, decision 0007).
6. Stop and ask before spending money, creating accounts, or sending anything outside the repo.

**State at handoff:**
- Warehouse built with 48 of 48 models and tests passing.
- First what-sells report in template mode. Jewelry tops supply but every item is flagged for metal content; press-on nails and cleaning tools are far less crowded (median 57 and 96 stores against 423 to 786).
- Metadata pilot: 4,510 keyword domains; 17 Shopify stores profiled; DNS and `/products.json` are the strongest traces.
- Shopify sitemaps' `lastmod` is always today, so it is useless for timing.
- The panel and a 1,200-domain discovery were still running when this session ended. Their local results do not carry over; rerun them.

## Owner tasks outstanding

Choose option A/B/C (supply check §4); CJ and eBay seller account setup (eBay developer approval pending; current eBay keys are sandbox), Terapeak session, rotate leaked keys, add the 5 env vars to the cloud environment, ask CJ about customer returns and the return address, decide public versus private repo and the commit email, answer the Shopify questions (wife's Instagram details, beauty route, sequencing).
