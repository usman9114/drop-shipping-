# 0017 — Lake sync to Supabase Storage, autopilot runner and health check

> 2026-11-05. Implements decision 0016 (GitHub Actions + Supabase free tier). Code: `scout/lake_sync.py`, `scout/autopilot.py`, `scout/quiet.py`, `.github/workflows/autopilot.yml`. Plan: `docs/plan/autopilot.md`.

## 1. Lake sync client (CLAUDE.md "reuse before build")

| Candidate | License / cost | Maintenance signal | Fit |
|---|---|---|---|
| **supabase-py** (`supabase` 2.34.0 on PyPI) | MIT, free | Supabase's official Python SDK, same-day releases with the platform | pulls in auth, realtime, postgrest and httpx; we need only storage |
| **storage3** (2.34.0) | MIT, free | the storage part of the same monorepo, released with it | the right size; would be the first choice |
| rclone / AWS CLI over Supabase's S3 protocol | MIT / Apache, free | very mature | needs separate S3 access keys (another secret for the owner to make), no merge of line files |
| **`requests` against the Storage REST API** | already a dependency | REST API documented by Supabase | 4 calls: get, upload, upsert, missing-object check |

**Chosen: `requests` + the REST API. `HOMEGROWN` (thin, about 90 lines for the client).** Reason: installing storage3 is an unreviewed third-party install, which needs the owner's approval (CLAUDE.md principle 7; the session's permission check also blocked it). The client is four HTTP calls; the logic around them (what to sync, immutable run files, merging the run log, manifest written last) is ours by nature and would be needed with storage3 too. **Switch path:** if the owner approves storage3, swap `SupabaseStorage` for `storage3.SyncStorageClient(...).from_("lake")`; the `get/put` interface is the only seam.

How it stays correct:

- **Immutable run files** (`lake/<dataset>/<date>/<run_id>.jsonl.gz`) are uploaded once with `x-upsert: false` and never replaced; a changed run file is reported as a conflict, not uploaded.
- **Line files** (`lake/_runs.jsonl`, `llm_cache.jsonl`) are merged as a union (by `run_id` for the run log) on pull and before every push, so two writers never drop each other's runs.
- **Manifest last.** `_manifest.json` (path, sha256, size, updated_at) is uploaded after every file it lists. A push that dies leaves the old manifest; readers trust only the manifest. Downloads are checked against its sha256 and renamed into place.
- **No secrets, no-op.** Without `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` every command prints `skipped=true reason=no-supabase-secrets` and exits 0.
- Not synced: `tranco/` (583 MB, re-downloaded), `dbt/`, `vault/`, temp files. Per-file cap 50 MB (free plan limit).

## 2. Public logs (the repo is public)

GitHub Actions logs of a public repo are public. Rule, enforced in code:

- The workflow runs only `pip install`, `python -m scout.lake_sync ...` and `python -m scout.autopilot ...`.
- Those two modules print only through `scout.quiet.say()`, which accepts numbers, booleans and short lowercase tokens with no dot, slash, `@` or space. A domain, URL, path or exception message cannot pass. Exceptions become their class name.
- Each child job's output (which can name stores) is captured into `data/private/autopilot/logs/<date>/<job>.log`, synced to the private bucket, never printed, never uploaded as an artifact.
- `tests/test_autopilot.py` checks this: `say()` refuses domain-like values; the two modules contain no `print()` or `sys.stdout/stderr`; the workflow has no `upload-artifact`, no shell tracing and no other step commands; a job that prints a domain and crashes with a URL leaves no trace in stdout or stderr.

## 3. Daily jobs, heartbeat, health

`python -m scout.autopilot daily` runs the job table in `scout/autopilot.py` (`JOBS`, the one place for caps and timeouts):

| Job | Command | Cap per day |
|---|---|---|
| ranks | `scout.stores ranks --days-back 1` | all known Shopify hits |
| discover-new | `scout.webmeta scan-new` | 100,000 lookups (live sample 2026-11-05: 6,853 domains new to the list in a day `[data]`) |
| meta | `scout.stores meta --new-first` | 500 stores |
| light | `scout.stores light --new-first` | 300 stores |
| fingerprints | `scout.fingerprints --queue 200` | 200 new stores not scored at the current `RULE_VERSION` |
| seed | empty placeholder run for a build dataset with no files yet (fresh bucket) | — |
| build | `make stores-build` | — |
| report | `make stores-report` (private stories to `data/private/reports/`; the committed-style aggregate report is written in the runner and discarded, Actions does not commit) | — |

Resumable: each job skips work already in the lake; the runner records which jobs finished today (`lake/_autopilot/daily-<date>.json`) and a rerun starts at the first unfinished one. Budget 330 minutes, under the 6 h job limit.

Heartbeat `lake/_autopilot/heartbeat.json` per job: last start, last success, status, exit, seconds, runs, rows and error rows added. One row per job per run goes to the lake dataset `autopilot_jobs`.

Health (`python -m scout.autopilot health`, autopilot.md rule 8) alerts on: no heartbeat; the daily run older than 30 h; a job with no success in 30 h; error rows above 10% of a job's rows (at least 20 rows); a fingerprint signal whose fire rate changed more than 2x between the last two 7-day windows (at least 30 rows each, signal in at least 5% of either week); disk above 80%. An alert makes the step fail, so GitHub e-mails the owner (free alert channel). A separate 6-hourly workflow job pulls only the heartbeat and checks it, so a missed daily run is noticed.

## Known limits

- Scheduled workflows in a public repo are switched off by GitHub after 60 days without repository activity `[unverified]`; the health job is in the same workflow, so it stops too. GitHub e-mails a warning first. Any commit keeps it on.
- The incremental diff is against the list of the last incremental run. When a day has more than 100,000 new entries, the rest are not looked up later (recorded as `truncated` in the run params).
- New stores are queued for fingerprints; the 11,415 older screened stores are not (that full run waits for the owner/session decision in `docs/handoff/session-state.md`).
- The lake starts empty in Supabase: seed it once from the vault (`scripts/vault_restore.py`, then `python -m scout.lake_sync push`) or let it grow from new stores only.

## Small-first run (2026-11-05, scratch lake, this container)

All 8 jobs ran end to end on an empty lake: ranks ok (0 rows, no hits yet); discover-new 6,853 domains new to the list, 167 Shopify `[data]` in 73 s; meta 167 stores (3 fetch errors); light 73 US stores; fingerprints 158 stores, 0 errors, 168 s; seed, build and report ok after two fixes the run found (dbt fails on a dataset with no files: `seed` job; the report crashed when the lake has no full-scan tranche: guarded). Health: 0 alerts after the run, and it flagged the failed report job correctly before the fix. Public output was counts only.

## Live check against the owner's project (2026-11-05)

Key saved as a network secret on the "Crypto" environment (proxy injects it as the `apikey` header; the session runs with `SUPABASE_SERVICE_KEY=proxy-injected`). The client now sends `Authorization: Bearer` only for legacy JWT keys; new `sb_secret_` keys go in `apikey` only. Result: reads answer HTTP 200, but bucket creation was refused with "new row violates row-level security policy" and the bucket list is empty: the saved key is the **publishable** key, not the secret key. Blocked until the secret key replaces it and the private bucket `lake` exists.
