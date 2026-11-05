# Autopilot: the store pipeline runs 24/7 on scripts

> 2026-11-05. Owner: "This pipeline will run 24/7, getting new stores and updating their data on autopilot, with minimal AI support: only GLM and OpenRouter. Most of the work must be reproducible with scripts; you guide the scripts from your experience."

## Operating model

| Who | Does what | When |
|---|---|---|
| **Scripts** (`scout/*`, `make` targets) | all fetching, parsing, rules, scoring, storage, reports | always, on a schedule |
| **Free models** (GLM Flash, OpenRouter free lane, via `scout.llm`) | only the fuzzy residue that rules cannot decide (vendor names, unclear categories, page summaries), cached by input | inside scheduled jobs, within the daily budget |
| **Claude** (this session or a later one) | design and fix scripts, review run logs and drift alerts, change rules with tests | on demand, never in the runtime loop |
| **Owner** | approvals, spending, manual sources the terms forbid us to automate | as needed |

A finding made by Claude in a session becomes a rule, test or prompt in the repo the same day, so the autopilot repeats it without Claude.

## Rules every scheduled job follows

1. **Idempotent and resumable.** Re-running a job does not duplicate data; a killed job restarts from its last batch (`store.record_run` per batch, batch state in the lake).
2. **Deterministic first.** Regexes, lookups and weights decide everything they can. The free models get only what is left, with the prompt and model recorded.
3. **Reproducible model calls.** `scout.llm` caches every successful answer by input (`data/private/llm_cache.jsonl`); a rerun reads the cache and spends no calls. Changing the prompt text forces fresh answers.
4. **Versioned rules.** Every row carries the `rule_version` that produced it (`scout.fingerprints.RULE_VERSION`). A rule change re-scores old rows, from saved evidence where possible (SKU shapes, counts), refetching only what saved evidence cannot answer.
5. **Evidence saved, content not.** Store counts, shares, shapes, ids and app names, never page text or images, so rules can be re-run without refetching and without holding content.
6. **Polite by construction.** robots.txt per URL, one honest User-Agent, pause per host, back off and record on 403/429/430, never retry around a block, no stealth.
7. **Budgets enforced in code.** OpenRouter free calls are capped at 900 a day in `data/private/llm_usage.json`; GLM at 8 workers; paid routes off unless `SCOUT_ALLOW_PAID=1`.
8. **Health is observable.** Each job writes a heartbeat (last start, last success, counts, errors). Alerts fire on: a job missing its window, error rate above 10%, a signal's fire rate changing more than 2x week on week (a rule or site change), disk above 80%.
9. **Small first still applies.** A new rule or prompt runs on a 10 to 30 item sample in a session, then ships; the autopilot only runs reviewed code.

## Jobs and cadence

| Job | Cadence | Built? | Gap |
|---|---|---|---|
| Tranco list download and rank history | daily | yes (`scout.stores ranks`) | none |
| **New-store discovery**: domains new to the list -> DNS -> Shopify check -> `/meta.json` | daily | yes (2026-11-05): `scout.webmeta scan-new` diffs against the last incremental run's list; `stores meta/light --new-first` | none |
| Light profile of new Shopify stores (feed aggregates, business model) | daily, new stores first | yes (`scout.stores light/deep`) | none |
| **Supply fingerprints** (`scout.fingerprints`) | daily for new stores; re-score on `RULE_VERSION` change; full refresh monthly | yes: new-store queue `--queue N` (2026-11-05) | re-score-from-shapes job, monthly refresh |
| Fuzzy labels by free models (vendor names, unclear stores) | daily batch, cached | runner yes (`scout.llm --batch`) | the prompts, after W3 validation |
| Feed snapshots and review counts, watchlist | weekly | yes (`scout.snapshot_job`) | watchlist definition |
| Warehouse build and reports (aggregates committed, store lists private) | daily after the jobs | yes (`make stores-build`, `stores-report`) | none |
| Health check and alerts | after each daily run, and every 6 h | yes (`scout.autopilot health`, decision 0017) | alerts are a failed workflow run (GitHub e-mail); no chat/phone channel |

## Where it runs

**Decided 2026-11-05: GitHub Actions + Supabase Storage free tier** (decision 0016); built in decision 0017: `.github/workflows/autopilot.yml`, `scout/autopilot.py` (job table, heartbeat, health), `scout/lake_sync.py` (bucket sync), `scout/quiet.py` (public-log guard). The options below are kept for the record.

### Options considered

This cloud container is reset when idle and the current data vault (decision 0012, option D) needs a Claude session to sync, so **neither can host a 24/7 loop**. Options, scheduler reused not built (CLAUDE.md "reuse before build"):

| Option | Scheduler | Storage | Cost | Notes |
|---|---|---|---|---|
| **A. Small always-on Linux box** (VPS or a home machine) | cron or systemd timers, `flock` per job | local disk + nightly push to a private data repo | VPS about $5 to $6 a month; home machine free | simplest; full control; recommended |
| B. GitHub Actions in a private repo | Actions `schedule` | the private repo | free tier 2,000 min/month, likely exceeded by daily crawls | 6 h job limit; runner IPs shared |
| C. Orchestrator (Prefect, Dagster) on option A | its scheduler and UI | as A | free self-hosted | worth it only once there are many dependent jobs |

Recommendation: **A with cron or systemd timers now**, a private data repo for durable storage (0012 option A), and C later if the job graph grows. Needs the owner's approval because it may spend money and creates an account or repo.

## Build order

1. Rule version, SKU shapes and the model-answer cache (done 2026-11-05).
2. Incremental discovery ("new since last list") and a work queue per job (done 2026-11-05).
3. Heartbeats, alert script and a `make autopilot-daily` entry point that runs the daily jobs in order (done 2026-11-05).
4. Host and storage per the owner's decision: GitHub Actions workflow and Supabase sync (done 2026-11-05; waits for the owner's account and secrets).
5. W3 validation results become weights and free-model prompts in code.
