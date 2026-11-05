# Session state: where the project stands

> Rewritten 2026-11-05 for a hand-off (CLAUDE.md principle 14). Read `CLAUDE.md` first (binding rules, principles 1 to 14). This file says what is done, what is running, what is next, and the traps. No secrets.

## Repo

- GitHub: https://github.com/usman9114/drop-shipping- (**public**). Working branch: `research/feasibility-poc`. No open PRs.
- Private data lives in `data/private/` (gitignored; survived the last worker restart but not a new container) and in the owner's private artifact "Store Data Vault" (decision 0012; restore with `scripts/vault_restore.py`).

## Where we are (2026-11-05)

Phase R1 re-scoped by the owner to **finding real dropshippers and their supply source** (not brands). Done today:

| Work | Result | Where |
|---|---|---|
| Policy-page dropship profiler | 105 dropship-labelled stores profiled; shipping text is a weak signal (promo banners) | `scout/dropship_profile.py`, run `20261105T104753Z-deacb2` |
| **Supply fingerprints** (owner's "street smart" idea after spotting `aliorders.fireapps.io`) | 105 stores: AliExpress 65, CJ 24, POD 2, no trace 14 | `scout/fingerprints.py`, `docs/plan/supply-fingerprints-plan.md` (P0, P1, P2 results) |
| App-trace catalogue | vendors rarely document storefront traces; catalogue must come from observation | `docs/research/33a/33b/33c` |
| **Validation (W3)** | 67 stores hand-checked: named source right 28/31 (90%); dropship-or-not 89%; strong rules 100% precision; several weak signals below 80% | `docs/research/35-fingerprint-validation.md`, truth CSV `data/private/research/fingerprint-truth.csv` |
| Bug fixed | DSers SKU rule matched brand SKUs (tommyjohn.com); also in the business-model classifier | `scout/stores.py` `DSERS_SKU`, tests |
| Free-model harness | `scout.llm --batch` (resumable), `--second-opinion`, `--usage`, answer cache; skill `free-llm`; agent `glm-worker` | `.claude/skills/free-llm/SKILL.md` |
| Autopilot design (owner: pipeline runs 24/7 on scripts, only GLM/OpenRouter at runtime) | rule versions, SKU shapes, cached answers built; jobs, gaps, hosting options written | `docs/plan/autopilot.md`, principle 13 |
| Parked ideas | underperforming-store leads and the owner's audit-SaaS blueprint reviewed; owner's tool shortlist mapped | `docs/plan/opportunity-store-rescue.md`, `docs/plan/tool-shortlist.md` |

Nothing is running in the background at hand-off.

Later on 2026-11-05 (after the first hand-off):

- **W3 changes applied** by the follow-up session (commit `8145d71`, `RULE_VERSION` 2026-11-05.3); see that commit and doc 35 for accuracy before/after.
- **Decision 0015:** ZenRows and ScrapingBee adopted as a paid fallback fetch tier (`scout/unblock.py`: plain first, escalate only on a block, daily credit cap 1,000). Keys `ZENROWS_API_KEY`, `SCRAPINGBEE_API_KEY` not set yet (owner step). CLAUDE.md principle 6 amended.
- **Crawl4AI stealth is ON** by default in `scout/reviews.py` (owner decision; `SCOUT_CRAWL_STEALTH=0` turns it off). Crawl4AI is not installed in a fresh container (`pip install -r requirements-crawl.txt`). The session permission check blocked a curl_cffi impersonation test; the owner was told a permission rule is needed for such runs.
- Owner's tool list mapped in `docs/plan/tool-shortlist.md` (Supabase, GitHub Actions, PageSpeed API, Empire Flippers as revenue ground truth, outreach stack).
- **Hosting decided: GitHub Actions** (decision 0016); storage Supabase free tier recommended, owner to create the account and add Actions secrets. Logs are public: jobs print counts only.
- **UI/UX:** design-only brief in `docs/plan/ui-ux-brief.md`. Step 1 done (store card, side panel, lead inbox card; prototype + data contract in `docs/design/ui-v0-store-card-and-leads.md`); waiting for owner feedback.


## Next, in order

1. **Done 2026-11-05 (later session):** W3 changes applied, `RULE_VERSION` 2026-11-05.3, 18 `test_w3_*` tests (`docs/research/35` "Applied"). Accuracy after is **not measured**: the truth CSV and fingerprint rows were never exported to the vault and were lost with the container. Re-score needs the truth set rebuilt (67 stores, about an hour by hand from public data) or a vault that has it. `vault_export.py` now includes both; export after every labelling job.
2. Add effort/budget apps from the owner's list as signatures (Klaviyo, Gorgias, Recharge, Skio, Nosto, Elevar, Littledata, Judge.me, Yotpo), observed on live stores first (small sample).
3. Re-run fingerprints on the 105, then (after the sample passes) on all 11,415 screened stores (about 2 hours at 8 concurrent).
4. Re-fetch and relabel the business-model classifier with the corrected DSers rule (saved counts used the old rule).
5. Autopilot build order (`docs/plan/autopilot.md`): incremental discovery, job queues, heartbeats, `make autopilot-daily`.

## Owner decisions open

1. **Hosting and storage for the 24/7 pipeline:** recommended Supabase (Postgres) + GitHub Actions or cron on a small box (`docs/plan/autopilot.md`, `docs/plan/tool-shortlist.md`).
2. Put the **two-week outreach test** (underperforming stores, kill rule: fewer than 2 interested replies from 20) in the plan as the phase after R1? Service (agency) or product (SaaS)?
3. Free Google API key for PageSpeed / Chrome UX Report.
4. Older, still open: CJ supply option A/B/C (fact 6 below), eBay production keys, Terapeak session, key rotation, Meta Ad Library manual check of the top 20.

## Facts that change plans

1. **eBay API License 9.6 (seller arbitrage):** no automated ordering from CJ, no posting tracking for CJ-sourced orders, no repricing or stock sync from CJ prices through the eBay API. Order forwarding and tracking upload are **manual**.
2. **eBay API License 8.1.4, 9.5, 9.7, 9.10:** no storing eBay data, no statistics or average selling prices, no price modelling, no ML on it without written permission. eBay market evidence comes from manual Terapeak reading and, later, our own account's data.
3. **CJ API data terms are unconfirmed.** Raw CJ output goes only to `data/private/` (gitignored). Commit derived results only (product id plus our computed metrics).
4. **CJ may disable API access after 30 days with no transaction** [unverified reading]. The key was created around 2026-11-04. Place the first test order within about a month.
5. Google Trends via pytrends is terms-unclear. Do not add pulls; licensed providers (SerpApi, DataForSEO) are the route. Raw points were removed from git.
6. **2026-11-04 live CJ run: `tcg-supplies` fails kill criterion K1** (0 relevant US-warehouse SKUs across 24 types), and both backups fail the same bar. CJ's US warehouse holds only 3,964 products, mostly furniture, women's clothing, beauty and jewelry. Real US→US shipping is ~$5.2–6.0 per light parcel. See `docs/shortlists/2026-11-04-cj-supply-check.md`. **Owner decision pending** between options A (supply-first on CJ US, recommended), B (tcg shipped from China), C (other US supplier).
7. eBay keys in the environment are **sandbox** keys (production returns 401).

## Traps in a fresh container

- **Vault lag:** the vault holds only what `vault_export.py` covered at the last export (2026-11-04). Fingerprint runs and `data/private/research/` from 2026-11-05 were lost. Run `python scripts/vault_export.py` and upload after every scan or labelling job.
- **Stale local branch:** a fresh clone may hold an old pre-rewrite `research/feasibility-poc` (ahead/behind origin by about 50). Origin is canonical: `git reset --hard origin/research/feasibility-poc` after checking `git log origin/...`.
- **Git identity defaults to an AI name.** The commit-msg hook then rejects every commit. Set `git config user.name` and `user.email` to match the repo owner's existing commits (`git log --format='%an <%ae>' | sort -u`).
- Git hooks are not cloned. Run `make setup`, then `pip install -r requirements.txt -r requirements-dev.txt`.
- `.env` is gitignored and disappears with the container. Keys must come from environment settings. Expected variable names: `CJ_API_KEY`, `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `ZAI_API_KEY`, `OPENROUTER_API_KEY`. Report names only, never values.
- The graphify post-commit hook rebuilds the graph in the background. A commit made during the rebuild can fail with "files were modified by this hook". Wait a few seconds and retry. After committing, stage `graphify-out` and commit again if the tree is dirty.
- OpenRouter credit (€10) bought by the owner on 2026-11-04. See `docs/plan/operating-plan.md` §2 for how it is used.
- OpenRouter key works (credit registered, `is_free_tier: false`). It was pasted in chat on 2026-11-04 and used from a gitignored `.env` for the day; **owner will rotate it**, then add the new one to "Crypto" as `OPENROUTER_API_KEY`.
- Keys live in the cloud environment **"Crypto"** (the one this project's sessions use; "Default" also has them). As of 2026-11-04 `OPENROUTER_API_KEY` is not visible in the container; check the variable name.
- Z.ai and OpenRouter keys were pasted into an earlier chat. The owner was asked to rotate them.
- Every commit triggers a background graphify rebuild that dirties `graphify-out/`; commit it as "Refresh knowledge graph".
- Subagents can hit the Claude 5-hour usage limit; resume them with SendMessage after the reset instead of starting a new one.

## History

Earlier states (2026-11-04: CJ supply check, review panel, niche finder R1, top-stores re-scope, data vault) are in git history of this file and in `docs/plan/` and `docs/decisions/`.
