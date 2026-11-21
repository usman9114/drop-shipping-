# Session state: where the project stands

> Rewritten 2026-11-21 as a clean start (CLAUDE.md principle 14). The project moves from cloud sessions to the owner's machine: setup in `docs/runbooks/local-setup.md`. Read `CLAUDE.md` first (binding rules, principles 1 to 14). Earlier versions of this file are in git history.

## Repo

- GitHub: https://github.com/usman9114/drop-shipping- (**public**). Default branch **`main`** (created by the owner 2026-11-21). `research/feasibility-poc` is the old working branch and is behind `main`. No open PRs.
- Private data: `data/private/` (gitignored) and its only off-machine copy, the private Supabase bucket `lake` (75 files, decision 0017). Restore with `make lake-pull`. The older artifact "Store Data Vault" (decision 0012) is stale since 2026-11-04; Supabase replaces it.

## What the project is and where it stands

Proof of concept: eBay dropshipping with CJ Dropshipping as the zero-inventory supplier. **Phase 0, release R1 "Niche Finder"**: find successful online stores, learn what they sell and where they get it, and end with a ranked niche shortlist (goal and exit criteria: `docs/plan/phase-niche-finder-r1.md`). Products, listings and the live eBay test are later phases.

### Done so far `[data]` unless marked

| Area | Result | Where |
|---|---|---|
| Research | eBay policy, unit economics, suppliers, APIs, legal, images, plus app-trace and validation studies | `docs/research/00-summary.md` and 01 to 35 |
| Decisions | 0001 to 0018 (warehouse, store discovery, unblock APIs, autopilot on Actions, Supabase lake, UI stack) | `docs/decisions/` |
| Store discovery | Tranco top 1M → 30,372 Shopify stores; 30,245 `/meta.json` answers; 11,141 US stores screened; 437 deep-profiled; rank history 642,423 rows over 28 list dates | `scout/webmeta.py`, `scout/stores.py` |
| Business model | of the screened US stores: 8,152 brand, 2,390 retailer, **535 copyable** (dropship, general, reseller, print on demand, unclear) `[proxy: our rules]` | `docs/reports/2026-11-11-best-stores.md` |
| Supply fingerprints | **11,532 stores** checked for supply traces (backlog finished 2026-11-17). Sources: AliExpress 287, CJ 29, other dropship apps 566, US supplier 9, mixed 8, print on demand 4, no trace 10,629. Dropship-labelled stores: 62 AliExpress, 19 CJ of 105 | `scout/fingerprints.py` |
| Validation | 67 stores hand-checked on 2026-11-05: named source right 28/31 (90%), dropship-or-not 89% | `docs/research/35-fingerprint-validation.md` |
| Niche shortlist (2026-11-11) | apparel 49.7 (120 copyable stores), home decor 17.8 (39), jewelry and watches 17.2 (26), hobby and crafts 5.7 (10), fitness 5.3 (13), toys 4.9 (12), bags 4.5 (22), pet 4.0 (8) `[proxy: score]` | `docs/shortlists/2026-11-11-niche-candidates.csv` |
| CJ supply (2026-11-04) | first niche `tcg-supplies` **fails kill criterion K1**: 0 relevant US-warehouse SKUs; CJ US warehouse holds only 3,964 products | `docs/shortlists/2026-11-04-cj-supply-check.md` |
| Free models | `scout.llm`: GLM Flash first, OpenRouter free lane, cache, resumable batches, second opinion | `.claude/skills/free-llm/SKILL.md` |
| Autopilot | daily job runner, heartbeat, health alerts, lake sync; GitHub Actions workflow on schedule | `scout/autopilot.py`, `.github/workflows/autopilot.yml` |
| UI | private artifact "Store Scout" https://claude.ai/artifact/8W7nFMj25E5xSbW3ded3Af, **still on 2026-11-11 data** (republish was blocked by a permission check on 2026-11-17) | `ui/store-scout.html`, `make ui-data` |

What public records cannot show: revenue, orders, ad spend, supplier cost, margin. Traffic rank is a proxy for visits, not sales. Store success is demand evidence, not eBay demand.

### 2026-11-21 changes

- `scout/lake_sync.py` now reads `.env` when run as a command, so `make lake-pull` works locally (it was a silent no-op without exported variables). Tests still never read a developer's `.env`.
- `requirements-dev.txt` gains `requests`: CI on `main` failed 14 tests with `ModuleNotFoundError: requests`.
- `.env.example` lists every variable the code reads; `docs/runbooks/local-setup.md` written.

## Running now

Nothing in a session. GitHub Actions autopilot runs on schedule but **keeps nothing**: its four secrets are empty, so lake pull and push log `skipped=true reason=no-supabase-secrets`, and the 6-hourly health job fails with `no-heartbeat`. Not a code bug.

## Next, in order

1. **Owner: local setup** (`docs/runbooks/local-setup.md`), keys in `.env`, run section 4 checks.
2. **Hand-check "brand with a supply trace"**: 173 brand-labelled stores carry an AliExpress trace, 322 a dropship-app trace (retailers 31 and 204). Either the business-model rule misses dropshippers that look like brands, or weak signals fire on brands. Sample about 30, measure, fix the rule, add tests (principles 5, 10).
3. **Rebuild the truth set** (67 stores, about an hour by hand; lost with an old container). Accuracy after rule version 2026-11-05.3 is unmeasured. Keep it in `data/private/research/` and push the lake.
4. **Finish R1 exit criteria**: deep profiles up to 600 or more (now 437); CJ supply sanity for each shortlist niche (`make stores-sanity`, needs `CJ_API_KEY`); compliance officer review; at least 3 niches ranked, one recommended.
5. Republish the Store Scout UI with the new `data/private/ui/store-scout.json` as `data.json`.
6. Autopilot: Actions secrets or disable the workflow; then the re-score-from-shapes job and the monthly fingerprint refresh.

## Owner decisions open

1. **Actions autopilot:** add the four repository secrets (the Supabase one is the `sb_secret_` key) or disable the workflow now that runs are local. <!-- pragma: allowlist secret (names only) -->
2. **CJ supply option** after the K1 fail: A supply-first on CJ US (recommended), B ship tcg from China, C another US supplier.
3. **CJ API clock:** CJ may disable API access after 30 days with no transaction `[unverified]`; the key dates from about 2026-11-04, so about 2026-12-04.
4. Outreach test (underperforming stores, kill rule fewer than 2 interested replies from 20) as the phase after R1? Service or SaaS?
5. Older: free Google API key (PageSpeed, Chrome UX Report), eBay production keys, Terapeak session, Meta Ad Library manual check of the top 20, rotation of keys that were pasted in chat on 2026-11-04.

## Facts that change plans

1. **eBay API License 9.6:** no automated ordering from CJ, no tracking upload for CJ-sourced orders, no repricing or stock sync from CJ prices through the eBay API. Those steps are manual.
2. **eBay API License 8.1.4, 9.5, 9.7, 9.10:** no storing eBay data, no statistics or average prices, no price modelling without written permission (decision 0004).
3. **CJ API data terms are unconfirmed:** raw CJ output stays in `data/private/`; commit derived results only.
4. Google Trends via pytrends is terms-unclear: no pulls.
5. eBay keys so far are sandbox keys (production returns 401).
6. OpenRouter has €10 credit (2026-11-04); paid Claude routes stay off unless `SCOUT_ALLOW_PAID` is 1.

## Traps

- `make setup` rewrites `.claude/settings.json` and `CLAUDE.md`; restore with `git checkout -- .claude/settings.json CLAUDE.md`.
- Git identity must match the owner's existing commits; the commit-msg hook rejects AI names and emails.
- Every commit starts a background graphify rebuild that dirties `graphify-out/`; commit it as "Refresh knowledge graph".
- `.env` loader in `scout/llm.py` does not strip trailing comments: keep comments on their own lines.
- `tranco` is pinned in `requirements-autopilot.txt`, Crawl4AI in `requirements-crawl.txt`.
- Push the lake (`make lake-push`) after every long job; a lost machine loses everything since the last push.
- Cloud sessions only: keys come from the "Crypto" environment and the Supabase key is injected by the proxy; the four Actions secrets are separate.
