# 0006 — DuckDB warehouse: deterministic core, LLM on top

> Status: **accepted**, 2026-11-04 (owner: "yes duckdb for now"). Un-parks a thin slice of `docs/plan/warehouse.md`; Postgres on the VPS stays the target (decision 0004). Code: `warehouse/` (dbt project), `scout/ingest_cj.py`, `scout/classify.py`, `scripts/wh_export.py`, `make wh-*`.

## Why now

The live CJ run (supply check, 2026-11-04) showed the niche-first hunt fails on supply. The new hunt is supply-first: score what CJ's US warehouse actually ships, then check demand by hand in Terapeak. The owner wants that scoring to be deterministic and owned by us, with LLMs as an assistant on top, not the engine.

## Choice

| Need | Candidates | License / cost | Maintenance signal | Chosen |
|---|---|---|---|---|
| Engine | **DuckDB**, SQLite, Postgres (VPS) | MIT, free | Very active; v2.0 | **DuckDB**: one file, no server, reads gzipped JSONL directly. Postgres when a scheduled daily load exists (warehouse.md revisit trigger). |
| Transforms + tests | **dbt-core + dbt-duckdb**, SQLMesh, plain SQL scripts | Apache-2.0, free | dbt-core 1.12, dbt-duckdb 1.11 (both current) | **dbt**: already the target in warehouse.md; same models port to Postgres. |
| Raw landing | **`scout/store.py` lake** (existing), dlt | ours / Apache-2.0 | n/a / active | **Existing lake**: immutable gzipped JSONL runs with run_id, sha256 and a provenance log already exist and are tested. dlt is deferred: four endpoints and a lake that DuckDB reads natively do not need it. Revisit with Postgres. |
| Margin floor | `scout.margin` (ours) | ours | tested | Domain logic, ours by nature. Called from a dbt Python model so the formula lives in one place. |
| Product typing | Rules dictionary (seed), free LLM fallback | free | n/a | **Rules first** (79% of the first pool), then a cached LLM label. |

`HOMEGROWN` (thin): `scout/ingest_cj.py` (glue between our CJ client and our lake) and `scout/classify.py` (cache filler). Both are under 200 lines, tested, and replaceable.

## Rules that make it deterministic

1. **Rules are data.** Category and title rules (`warehouse/seeds/rule_*.csv`) and the product-type dictionary are versioned CSV seeds, each with an action (exclude / review) and a reason. Every rule hit is a row in `enrich.enr_product_flags`, so every exclusion can be traced to its rule.
2. **The LLM never runs inside the build.** `scout.classify` labels only what the rules missed and appends `(sha256 of title, label, model, prompt version)` to a committed seed. A rebuild reads the cache, so the same lake gives the same marts. Titles are not stored in the cache.
3. **LLM labels never decide compliance.** They only name product types. Exclusions come from rules and the compliance officer.
4. **Raw stays private.** Lake and DuckDB file live in `data/private/` (gitignored, terms gate). Committed outputs are ids, our labels and our computed numbers (`scripts/wh_export.py`).
5. **Rebuild per session.** The cloud container is ephemeral; `make wh-load wh-catalogue wh-offers wh-build` rebuilds everything in about 25 minutes, mostly the CJ offers pull. History over time waits for Postgres.

## Layers

`stg` (typed, latest run, column contracts) → `rules` (seeds) → `enrich` (flags, product type) → `core` (`core_dim_product`, `core_fact_offer`) → `mart` (`mart_prefilter`, `mart_supply_candidates`, `mart_terapeak_sheet`). dbt tests run on every build.

## Intelligence layer (next)

Reads marts only: names and explains product-type groups, drafts listings from verified specs, answers questions with read-only SQL. Not built in this slice.

## Out of scope for this slice

Postgres, VPS, scheduled loads, SCD2 history, dashboards, eBay data (decision 0004).
