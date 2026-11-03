# Warehouse design: Postgres as the source of truth

> Status: **draft for owner review**, 2026-11-03. Supersedes the DuckDB/SQLite store in `docs/plan/data-pipeline.md` and part of decision 0003. Decision 0004 (proposed) records hosting, tool picks and the source-terms findings. This document follows it.
> **Parked 2026-11-03:** the owner chose to run lean without a database for now. Phase 0 keeps the existing JSONL lake in git plus a disposable SQLite file (`scout/store.py`, flagged home-grown). This design and the VPS runbook stay as the target. **Revisit when:** a scheduled daily ingest exists, there are three or more live sources, or the lake passes about 50 MB. **Rule meanwhile:** anything with a retention limit in its terms must never be committed to git, because deleting a file does not remove it from history.
> Owner's direction: boring proven tech, Postgres, systematic ingestion and enrichment, proper warehousing, lean, runs in GitHub CI, retention controlled.

## 1. Principles

1. **Boring tech.** Postgres, plain SQL migrations, dbt-core for transforms and tests, pytest, make, GitHub Actions. No LLM in the ingestion or aggregation path.
2. **Append-only raw, derived everything else.** Raw rows are never updated. Staging, core and marts can be dropped and rebuilt from raw plus the migrations.
3. **Idempotent.** Re-running any job for the same window changes nothing.
4. **Every row traces to a run** (`run_id`), and every run to a source with a stated trust level and terms.
5. **Funnel the scope.** Wide and cheap first, narrow and expensive last. Only shortlisted candidates get daily snapshots.
6. **Size is a requirement.** Every table has a grain, a retention rule and a budget. CI fails when the database exceeds its budget.

## 2. Layers (one schema each)

| Schema | Purpose | Written by | Mutable? | Retention |
|---|---|---|---|---|
| `meta` | source registry, runs, contracts, DQ results, retention policy | migrations, jobs | append | forever (tiny) |
| `raw` | landing tables, one per source: JSONB payload plus run metadata | ingesters only | **append-only** | per source (see §7) |
| `stg` | typed and deduplicated views of raw, one model per source | dbt | rebuilt | none (views) |
| `enrich` | derived attributes with provenance: category mapping, brand flags, compliance flags | dbt and rule jobs | rebuilt | follows core |
| `core` | conformed dimensions and facts at a stated grain | dbt | history kept via SCD2 or snapshots | per table (see §7) |
| `mart` | scorecards, shortlist, margin inputs for agents and dashboards | dbt | rebuilt | none (views/materialized) |

## 3. Core model (grain first)

| Table | Grain | Key | History |
|---|---|---|---|
| `core.dim_source` | one row per source | source_id | none |
| `core.dim_niche`, `dim_keyword` | niche, keyword | natural key | SCD1 |
| `core.dim_product` | CJ product (variant level) | cj_variant_id | **SCD2** (name, category, images, active) |
| `core.dim_candidate` | niche × CJ product × eBay search phrase × Trends keyword | candidate_id | SCD2 on mapping |
| `core.fact_trend_weekly` | keyword × week × geo | (keyword, week, geo) | upsert, tiny |
| `core.fact_supplier_offer_daily` | variant × warehouse × day | (variant, wh, day) | **change-only**: write a row only when cost, shipping, stock or ship days differ from yesterday |
| `core.fact_market_daily` | eBay search phrase × day | (query, day) | stats only: count, min, p25, median, p75, max. No item rows kept long term. |
| `core.fact_social_weekly` | term × platform × week | (term, platform, week) | upsert |
| `core.fact_compliance_flag` | candidate × rule × evidence date | (candidate, rule, date) | append |
| `core.fact_evaluation` | candidate × kind × run | run_id | append (margin results, verdicts, scores) |

Time handling: every fact carries `observed_at` (when the world was true) and `loaded_at` (when we learned it). SCD2 dimensions carry `valid_from`, `valid_to`, `is_current`. This allows "what did we believe on day X" queries without a full bitemporal design.

## 4. Ingestion contract

Every ingester follows the same steps. The skeleton is shared, so a new source is mostly a mapping.

0. **Terms gate.** A source cannot be enabled until its terms page has been read, `meta.source.terms_reviewed_on` is set, and `max_retention` is recorded (null means *do not store*). The retention job enforces `max_retention`. Sources whose terms forbid storing or analytics stay disabled. This is why eBay listing data is off by default (decision 0004).
1. **Register the source** in `meta.source` once: id, owner, access path, trust level, rate limit, cadence, **storage terms** (max age, redistribution) and license link.
2. **Open a run** in `meta.run` with params, a params hash and the window. A unique key on (source, params_hash, window) makes retries safe.
3. **Fetch** with retries, backoff and a hard timeout. Respect rate limits from the registry.
4. **Validate against a schema contract** (required fields, types, ranges). Rows that fail go to `raw.<source>_rejects` with the reason. They do not enter staging.
5. **Land to `raw.<source>`** as JSONB plus `run_id`, `fetched_at` and `payload_sha256`. Duplicates (same hash) are skipped.
6. **Close the run** with control totals: rows fetched, landed, rejected. A mismatch fails the run.

Reuse: dlt supplies steps 3 to 5 (pagination, incremental state, schema handling) and has a Postgres destination. We only add the registry, the run table and the control totals if dlt's load metadata cannot carry them (open question from decision 0003).

## 5. Enrichment (systematic, deterministic first)

Enrichment writes to `enrich.*` only. It never overwrites facts.

| Stage | Method | Examples |
|---|---|---|
| 1. Lookup | Joins against reference data we ingest | eBay category tree and item aspects, Google Product Taxonomy, HTS duty rates |
| 2. Rules | Versioned SQL or regex | banned words (PSA, BGS, brand names), battery or radio keywords, oversize thresholds, price-band checks |
| 3. Reference matching | Fuzzy match against official lists | USPTO trademark owners as a brand blocklist, CPSC recall titles against product names |
| 4. Model-assisted (last resort) | Free LLM for what rules cannot classify | niche or product-type tagging of unmapped titles |

Every enrichment row stores `method`, `rule_or_model_version`, `confidence`, `input_hash` and `run_id`. Stage 4 results are cached by input hash, flagged `method='llm'`, and never feed compliance verdicts without a human or rule confirmation.

## 6. Aggregation strategy

- **Daily snapshots only for the shortlist** (about 20 to 40 candidates), not the whole catalog.
- **Catalog scans are weekly and change-only.**
- **High-volume sources are reduced at ingest**: eBay item lists become per-query daily statistics. Item-level rows expire quickly.
- **Rollup ladder**: raw → daily → weekly → monthly. Each rung is a dbt model with tests, and its inputs are checked for completeness before it runs.
- **Reproducibility**: marts are built from core with no manual steps. A decision memo cites the mart query and the `run_id`s behind it.

## 7. Retention and size budget (starting values)

Soft target **2 GB** on the VPS (CI fails above it; alert at 70% of disk). The 250 MB figure applies if we fall back to a free hosted tier. Real limits and the terms-forced retention come from the research wave.

| Data | Rough volume | Raw kept | Derived kept | Mechanism |
|---|---|---|---|---|
| Search interest | 260 weekly points per keyword; 100 keywords = 26k rows; from a licensed provider (SerpApi or DataForSEO). Existing pytrends points are flagged. | not kept (tiny) | forever | upsert |
| CJ catalog scan | maybe 5k variants per niche, weekly | 30 days | SCD2 forever | monthly partitions, drop expired |
| CJ shortlist offers | 40 candidates × 10 variants × daily, change-only | 90 days | daily facts 1 year | partitions plus retention job |
| eBay listings | **disabled by default** (eBay API License 8.1.3, 8.1.4, 9.5, 9.7). If eBay gives written permission: listings TTL 6 h, other content 24 h, delete on delisting. | none | none until permission | TTL job built, switched off |
| Own-account eBay data (Sell APIs: impressions, orders, returns) | small | per Sell API terms (check first) | forever | upsert, first-party truth |
| Social trends | weekly per term | 90 days | weekly forever | upsert |
| Compliance feeds (CPSC, FDA, USPTO) | incremental deltas | 90 days | current state | upsert |
| Runs, rejects, DQ results | small | 1 year | summary forever | delete job |

Mechanics:
- Declarative **monthly partitions** on every raw table. Retention drops whole partitions, which is instant and does not bloat the table.
- A `meta.retention_policy` table lists table, column, max age. One job reads it, so limits live in data, not code.
- A **size check** runs after every load and fails CI above the budget. It reports the top 10 tables and projected growth.
- Large JSONB payloads are trimmed to the fields we use before landing, once a source's schema is understood. The first runs keep the full payload for debugging.

## 8. Data quality (run on every load)

| Test | Where |
|---|---|
| Not null, unique, accepted values, relationships | dbt tests on stg, core, mart |
| Freshness per source against its cadence | dbt source freshness or a SQL check |
| Row-count anomaly vs trailing 7-day average | SQL check, fails above 3σ or below 50% |
| Price and stock sanity (positive, plausible ranges) | dbt tests |
| Control totals (fetched = landed + rejected) | run close step |
| Reconciliation: rollup totals equal the sum of the inputs | dbt singular tests |
| Contract drift (new or missing source fields) | schema contract, alert, no silent change |

A failed critical test stops marts from being rebuilt, so agents never read half-loaded data. Failures open an issue (GitHub's native notification).

## 9. CI design (lean)

| Workflow | Trigger | Database | Secrets | Does |
|---|---|---|---|---|
| `ci` | pull request, push | **ephemeral Postgres service container** | none | lint, pytest, apply migrations, load fixtures, `dbt build`, DQ tests |
| `ingest` | schedule (daily or weekly per source) and manual | **persistent Postgres** via `DATABASE_URL` | API keys, DB URL | ingest, `dbt build`, DQ, retention, size check, export a compact status file |
| `backfill` | manual only | persistent | same | replay a source over a window |

- Same code in both, switched by `DATABASE_URL`. Tests never touch real data.
- `concurrency` groups prevent overlapping runs. Job timeouts cap cost. Free-tier minutes are the constraint to verify.
- Scheduled workflows only run from the **default branch**, so the working branch has to be merged first.

## 10. Durability

The choice is the owner's. Both use the same code.

| Option | Where the data lives | Pros | Cons |
|---|---|---|---|
| **A. Hosted free Postgres** (fallback: Neon Free, decision 0004) | Neon, Supabase or similar | Real database, persistent, point-in-time recovery may be included, agents can query it | One more account. Free-tier caps, pausing behaviour and extension support must be checked. |
| **C. Postgres on your own VPS** (chosen 2026-11-03) | Docker on a small Linux VPS, reached by CI through a restricted SSH tunnel | No storage cap, always on, extensions available, full control | We own security, patching and backups. Runbook: `docs/runbooks/vps-postgres.md`. |
| **B. All in CI** | Postgres rebuilt each run from compact exports committed to git or a release | No accounts, fully reproducible | Git history grows, rebuild time grows, no ad-hoc agent queries between runs. Fine for the first weeks only. |

Backups: logical dumps of `core` and `meta` (small) on a schedule to a private location. Raw is replayable only within its retention, so `core` and its history are the real truth.

## 11. What this replaces

| Today | Becomes |
|---|---|
| `scout/store.py`, `data/lake` | `raw` landing in Postgres. The 12,576 Trends points load once through a one-off loader. |
| SQLite `scout.db` | Postgres |
| `scout/trends.py` | an ingester on the shared skeleton, library swappable |
| `docs/plan/data-pipeline.md` | links here for the model, keeps the source list |
| `candidates` and `image_assets` tables from the diagram | `core.dim_candidate` and `core.dim_asset` |

## 12. Build order

| Milestone | Deliverable | Needs |
|---|---|---|
| M0 | Decision 0004 (hosting, tools). Source registry filled in with each source's storage terms. | research wave, owner choice |
| M1 | Migrations for `meta`, `raw`, retention policy. CI workflow with Postgres service container and fixtures. | none |
| M2 | Shared ingestion skeleton and the Trends ingester, with the existing data loaded. dbt project with staging, core and DQ tests. | none |
| M3 | CJ ingester and the shortlist daily facts. | `CJ_API_KEY`, hosted DB |
| M4 | eBay market stats, within its storage terms. | eBay keys |
| M5 | Free compliance feeds (CPSC, USPTO and others) and enrichment rules. Mart: candidate scorecard. | none |
| M6 | Scheduled `ingest` workflow, size and freshness checks. | default branch, secrets |
