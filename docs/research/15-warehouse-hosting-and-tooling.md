# 15 — Postgres hosting, GitHub Actions limits, warehouse tooling

> `market-researcher` (Haiku), 2026-11-03. Primary pages where fetched. **Not covered:** Git LFS quota, repo-size guidance, Xata's free tier, data residency, and the Neon/Supabase extension lists (so pg_cron, pg_partman and pgTAP on hosted services are unverified). Release years on GitHub pages were inferred from context [unverified].

## 1. Free hosted Postgres

| Provider | Storage | Compute | Idle rule | Backups on free | Fit for a daily CI job |
|---|---|---|---|---|---|
| **Neon Free** | **1 GB per project** (one FAQ page says 0.5 GB, a conflict) | 100 CU-hours/project/month | scales to zero after 5 min idle, cannot be disabled | 6 h history, 1 manual snapshot, no schedule | **Best fit.** Storage is the binding limit. |
| Supabase Free | 500 MB database | shared CPU, 500 MB RAM | "may pause" on low activity in a 7-day window | none downloadable | Risky on size; pausing depends on activity |
| Aiven Free | 1 GB disk | 1 CPU, 1 GB RAM | powers off when idle (warns first) | included, retention not stated | Usable. 20 connections max, no pooling. |
| CockroachDB | no free tier found, 30-day trial | usage-based | trial clusters deleted after a grace period | n/a | Avoid (not Postgres) |
| Xata | unclear | unclear | n/a | n/a | could not confirm a free tier |

- No free tier checked offers an IP allow-list, so GitHub runner IPs cannot be locked down. Use strong credentials, require TLS, rotate them.
- Backups are thin or absent, so **schedule `pg_dump` to storage we control**.
- Neon egress 5 GB/project/month. Supabase 5 GB (one page says 500 MB).

## 2. GitHub Actions

| Item | Value |
|---|---|
| Public repos | standard runners free, no minute cap |
| Private repos, Free plan | **$12/month of compute included** (a dollar amount); artifacts 500 MB; cache 10 GB/repo |
| Rate, 2-core Linux | $0.006/min, so about 2,000 minutes of Linux per month |
| Scheduled workflows | **default branch only**; minimum interval 5 min; delays under load [unverified] |
| Public repos | schedules auto-disable after 60 days with no repo activity |
| Step timeout | max 360 min |
| Do not | use artifacts or cache as data storage; retention defaults unconfirmed |

Postgres service-container syntax and SSL setup were not verified (the docs page returned 404 on fetch). Standard practice, but check against the live docs when writing the workflow.

## 3. Tooling

| Tool | License | Latest | Notes |
|---|---|---|---|
| **dbt Core 1.x + dbt-postgres** | Apache-2.0 | v1.13 pre-release 2026-10-14 | v1 adapters frozen (no new features) |
| dbt Core 2.0 (dbt-oss) | Apache-2.0 | v2.0.11, 2026-11-03 | v2 adapter for Postgres unconfirmed |
| dbt v2 / Fusion | proprietary | n/a | avoid until licensing is clear |
| SQLMesh | Apache-2.0 | v0.236.4 | Postgres support unconfirmed; owner Fivetran acquired Tobiko (2026-03) |
| **dbmate** | MIT | date not shown, 7.5k stars | plain SQL migrations, Postgres-native |
| Atlas | Apache-2.0 | 8.8k stars | declarative diffs; paid cloud tier |
| Flyway Community | Apache-2.0 repo | 10.2k stars | Postgres support in Community unconfirmed |
| Alembic | MIT | 4.5k stars | Python/SQLAlchemy only |
| **pgTAP** | permissive | 1.3.5 | SQL unit tests for DDL and constraints |
| Soda Core, Great Expectations | OSS cores, commercial cloud | | heavy for 1-3 people |
| pg_partman | not verified | v5.5.0 | needs PostgreSQL 14+; availability on free hosts unverified |
| pg_cron | PostgreSQL License | no dated release | not needed if Actions schedules jobs |

## 4. Pattern check

An ephemeral Postgres service container in CI for tests plus a persistent hosted Postgres for real data is common practice [no citation found, unverified]. Expect:
- cold starts after Neon scales to zero or Aiven powers off: add a connection retry
- Aiven's 20-connection cap: one connection per job step
- transaction-mode poolers break prepared statements and advisory locks [general guidance, unverified]
- SSL: `sslmode=require` against hosted DBs; service containers default to no TLS

## Ranked recommendation (from the agent)

1. **Hosting:** Neon Free. Keep raw retention short, add a scheduled `pg_dump`. Fallback: Aiven Free.
2. **Migrations:** dbmate (or Atlas for declarative diffs).
3. **Transform and tests:** dbt Core 1.x with dbt-postgres, plus pgTAP for DDL and constraints.
4. **Scheduling and retention:** GitHub Actions cron plus partition-drop scripts. Add pg_partman only if native partitions are needed.
5. **Avoid:** CockroachDB, Soda Cloud or GX stacks, dbt v2/Fusion for now, artifacts/cache or LFS as data storage.

## Sources
- Neon: https://neon.com/docs/introduction/free-tier ; https://neon.com/docs/introduction/plans ; https://neon.com/faqs/free-plan-limits-and-quotas
- Supabase: https://supabase.com/docs/guides/platform/org-based-billing ; https://supabase.com/docs/guides/platform/going-into-prod
- Aiven: https://aiven.io/docs/products/postgresql/concepts/pg-free-tier
- CockroachDB: https://www.cockroachlabs.com/pricing/
- GitHub Actions billing: https://docs.github.com/en/billing/concepts/product-billing/github-actions
- Workflow syntax and disabling: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax ; https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows
- dbt licensing: https://docs.getdbt.com/docs/dbt-licensing ; https://github.com/dbt-labs/dbt-adapters ; https://github.com/dbt-labs/dbt-core/releases
- Tools: https://github.com/amacneil/dbmate ; https://github.com/ariga/atlas ; https://github.com/flyway/flyway ; https://github.com/sqlalchemy/alembic ; https://github.com/theory/pgtap ; https://github.com/sodadata/soda-core ; https://github.com/great-expectations/great_expectations ; https://github.com/pgpartman/pg_partman ; https://github.com/citusdata/pg_cron ; https://github.com/SQLMesh/sqlmesh/releases
- Fivetran/Tobiko: https://www.businesswire.com/news/home/20260325552632/en/
