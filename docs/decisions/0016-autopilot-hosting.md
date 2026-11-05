# 0016 — Autopilot runs on GitHub Actions; storage on Supabase (free tier)

> 2026-11-05. **Owner decision: "run it on GitHub Actions".** Storage: Supabase free tier recommended, waiting for the owner to create the account. Context: `docs/plan/autopilot.md`, decision 0012 (storage), `docs/plan/tool-shortlist.md`.

## Scheduler: GitHub Actions (decided)

- **Cost:** standard GitHub-hosted runners are free for public repositories; this repo is public `[unverified: check GitHub billing page before relying on it]`.
- **Limits to design for:** a job may run at most 6 hours, so long scans run in resumable batches across runs (they already do); scheduled runs can start late at busy times; scheduled workflows in public repos are switched off after 60 days without repository activity `[unverified]`, so the health check must notice a missing run.
- **The public-repo catch:** workflow **logs are public** and uploaded artifacts can be downloaded by others. So jobs must print counts only, never store lists or domains, and must not upload data as workflow artifacts. Data goes to private storage only.
- **Secrets:** API keys (Z.ai, OpenRouter, CJ, ZenRows, ScrapingBee, Supabase) go in the repository's Actions secrets (owner step), never in the workflow file. Secrets are not passed to workflows triggered from forks.

## Storage: Supabase free tier (recommended, owner to create the account)

| Free plan (supabase.com/pricing, read 2026-11-05) | Our need |
|---|---|
| Postgres database 500 MB | store tables and latest rows: well under (the whole lake is 17 MB today) |
| File storage 1 GB | the append-only lake files (17 MB) and the DuckDB warehouse (18 MB) |
| Egress 5 GB a month | a daily download and upload of about 35 MB: about 1 GB a month |
| Projects pause after 1 week of inactivity | daily jobs keep it active |
| No automatic backups | weekly copy to the owner's vault or a private repo |
| Pro plan from $25 a month (8 GB) | only if we outgrow the free tier |

The Tranco lists (583 MB locally) are not stored: they are re-downloaded from Tranco when needed.

**First version:** lake files in a private Supabase Storage bucket (download at job start, upload at job end, atomic per run file). Postgres tables come later, when the UI needs them.

## Owner steps

1. Create a Supabase account and one project; create a private storage bucket `lake`.
2. Add Actions secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `ZAI_API_KEY`, `OPENROUTER_API_KEY`, `CJ_API_KEY`, and later `ZENROWS_API_KEY`, `SCRAPINGBEE_API_KEY`. <!-- pragma: allowlist secret (names only, no values) -->
