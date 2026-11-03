# 0004 — Postgres warehouse, hosting, and what the source terms allow

> Status: **proposed**, awaiting owner sign-off. Date: 2026-11-03. Supersedes the storage rows of decision 0003 (DuckDB, `scout/store.py`).
> **Parked 2026-11-03:** the owner chose to run lean without a database for now. Phase 0 keeps the existing JSONL lake in git plus a disposable SQLite file (`scout/store.py`, flagged home-grown). This design and the VPS runbook stay as the target. **Revisit when:** a scheduled daily ingest exists, there are three or more live sources, or the lake passes about 50 MB. **Rule meanwhile:** anything with a retention limit in its terms must never be committed to git, because deleting a file does not remove it from history.
> Inputs: `docs/research/15` (hosting and tools), `16` (trend sources), `17` (free feeds and storage terms). Design: `docs/plan/warehouse.md`.
> Research, not legal advice.

## 1. Decision

| Area | Choice | Notes |
|---|---|---|
| Database | **PostgreSQL**, layered schemas `meta / raw / stg / enrich / core / mart` | Owner's direction. Replaces DuckDB and SQLite. |
| Hosting | **Postgres in Docker on the owner's VPS**, reached by CI through a restricted SSH tunnel (no database port exposed). Ephemeral Postgres **service container** in CI for tests. | Owner choice 2026-11-03. Runbook: `docs/runbooks/vps-postgres.md`. No storage cap, always on. We own security, patching and backups. |
| Fallback | Neon Free (1 GB per its docs, scales to zero, 6 h of history), then Aiven Free | `pg_dump` loads into either, so moving is cheap. |
| Migrations | **dbmate** (MIT, plain SQL) | Atlas if declarative diffs are wanted later. |
| Transforms and tests | **dbt Core 1.x + dbt-postgres** (Apache-2.0) with dbt tests, plus **pgTAP** for DDL and constraints | Stay off dbt v2/Fusion until licensing and the Postgres adapter are clear. |
| Ingestion | **dlt** (Postgres destination), one-day spike on the CJ source first | Open question from 0003 stands: can load metadata carry trust, params, sha256? |
| Scheduling | **GitHub Actions** cron. No pg_cron. | Default-branch only. Free private plan includes $12/month of compute (about 2,000 Linux minutes). |
| Partitioning and retention | **Native declarative partitioning** (built into Postgres) with a small SQL retention function in a migration | No extension needed. Revisit pg_partman only if it becomes painful. |
| Backups | Nightly encrypted `pg_dump` of `meta` and `core` copied off the server, plus a weekly CI restore test | Tool choice recorded before it is written (runbook §8). |

## 2. New rule: terms gate

No source is enabled until its terms page has been read and `meta.source` records `terms_reviewed_on`, `max_retention` (null means *do not store*) and the license link. The retention job enforces `max_retention`. This is now in `CLAUDE.md`.

## 3. What the terms change (the important part)

### eBay data cannot simply be stored and analysed

Verified clauses (`docs/research/17` §A): statistics and "average selling price" need eBay's **written permission** (8.1.4), using eBay content to "suggest or model prices" is restricted (9.5), storage is allowed only for permitted purposes and no clause permits internal research (9.7), displayed listings must be at most 6 hours old (8.1.3), and no ML training (9.10). Marketplace Insights (sold data) is a Restricted API.

**So the earlier plan is withdrawn:** ingesting Browse API listings into the warehouse, keeping daily price statistics, and using them to set prices. That would likely breach the agreement without permission.

| Option | Effect | Recommendation |
|---|---|---|
| A. Ask eBay for written permission describing our internal research use | Could unlock Browse data. Slow and uncertain. | **Do in parallel.** The owner sends it (eBay developer support). |
| B. Use **Terapeak** manually in Seller Hub (eBay's own research tool for sellers) | Competition and sold-price evidence, no API terms involved. Terapeak's own terms not checked. | **Use now**, for the owner's research. Record conclusions in decision notes, not raw eBay data in the warehouse. |
| C. Query the Browse API transiently and store nothing | Still hits 8.1.4 (statistics) and 9.5 (price modeling) | **Avoid** for pricing. |
| D. Build demand and price evidence from **non-eBay** sources | YouTube, licensed search-interest providers, Instagram hashtags, Keepa for Amazon price proxies, CJ costs, compliance feeds | **Primary route until permission arrives.** |
| E. **First-party data** from our own eBay account (impressions, sales, returns via the Sell APIs, covering our own listings) | The strongest and least restricted evidence. Covered by our own account's terms [check the Sell API clauses before storing]. | The Phase 2 micro-test becomes the main source of truth for eBay performance. |

The warehouse is built so `eBay listings` is a **disabled source** with a TTL job ready (6 hours for listings, 24 hours for other content, delete on delisting). It is switched on only if permission arrives.

**Effect on feasibility:** pricing and sell-through for the first product choices will rest on manual Terapeak reading and Amazon proxies, not on automated eBay data. That is weaker evidence than the plan assumed. It is a real constraint on this idea and should be treated as such.

### Google Trends

Google's terms (effective 2026-07-30) bar automated access that ignores machine-readable rules. `pytrends` is unofficial automated access. I recommended keeping it earlier; the new evidence says that is not safe.

- **Stop adding pytrends pulls.**
- Use **SerpApi** (free 250 searches/month, then $25 per 1,000 [fetched]) or **DataForSEO** ($0.0027 per standard task [fetched]), which are licensed providers.
- The 12,576 points already loaded stay as internal research evidence, flagged `pytrends, terms unclear`, and are not redistributed.
- The owner also applies for the official API alpha.

### Other sources

- **TikTok:** manual reading only (no API for commercial use). **Instagram hashtags:** official, 30 unique hashtags per 7 days, needs App Review. **Reddit, WIPO, Marketplace Insights:** exclude.
- **First ingests (free and safe):** CPSC recalls, openFDA, Google Product Taxonomy, USITC HTS, Federal Register, eBay Taxonomy (category IDs and aspects only), CJ catalog for our own account, YouTube Data API, SerpApi/DataForSEO.

## 4. Home-grown audit update

| Piece | Status |
|---|---|
| `scout/store.py`, `data/lake` | Superseded by Postgres `raw`. One-off loader for the existing Trends points. |
| `scout/trends.py` (pytrends) | **Retire** in favour of a SerpApi or DataForSEO ingester. |
| `scout/llm.py` | Unchanged from 0003 (LiteLLM spike pending). |
| `scout/margin.py` | Ours by nature. Its price inputs can no longer come from eBay API data. |

## 5. Owner actions

| Action | Why |
|---|---|
| Provision the VPS and follow the runbook; add the GitHub secrets it lists | Needed before any scheduled job |
| Email eBay developer support for written permission (internal research, statistics, price guidance) | Option A above |
| Decide the Trends route: SerpApi free tier now | Stop pytrends |
| Create the Neon project and add `DATABASE_URL` as a secret; merge the branch to the default branch | Needed before any scheduled job |
| Apply for the Google Trends alpha | Official route |
| Review this decision, especially §3 | Changes the evidence strategy |

## 6. What this does not settle

- Neon's storage cap conflict (1 GB vs 0.5 GB) and its extension list were not verified.
- Whether derived aggregates of eBay data fall under 8.1.4 is unclear and needs counsel or eBay's answer.
- CJ's data-use terms were not located.
- Postgres service-container syntax and SSL setup were not verified against live docs.
