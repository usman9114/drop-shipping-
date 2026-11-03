# Data pipeline: feeding the team authentic evidence

> 2026-11-03, orchestrator. **Problem:** agents reasoning over web articles make educated guesses. **Fix:** a store of our own pulled data, with provenance, that every agent queries and every decision cites.

## 1. Architecture

```
 SOURCES (ingesters)            LAKE (truth, in git)                 STORE (derived)          CONSUMERS
 ───────────────────            ────────────────────                 ───────────────          ─────────
 Google Trends   ✅ ─┐
 CJ catalog/stock 🔑 ─┤    data/lake/<dataset>/<date>/<run>.jsonl.gz    data/store/scout.db     agents: python -m scout.store query
 eBay Browse API  🔑 ─┼──▶ + data/lake/_runs.jsonl  ──rebuild──▶  (SQLite, gitignored)  ─▶ reports / scoring views
 Terapeak CSV  (manual)─┤    (append-only; provenance per run)                                decisions cite run_ids
 Shopify/IG insights 🔑─┘
 Agent outputs (margin, compliance verdicts) ─▶ dataset `evaluations`
```

✅ = built · 🔑 = needs keys (code next) · manual = owner exports

## 2. What makes it "authentic"

| Property | How |
|---|---|
| Provenance | Every run records source, trust level, params, `fetched_at`, git SHA, row count and a sha256 of the rows (`scout.store.record_run`) |
| Immutability | Runs are append-only files. A re-pull is a new run, never an edit. `rebuild` verifies every hash. |
| Time series | Repeated pulls (daily or weekly) give real price, stock and competition history, which no blog has |
| Honesty | Trust levels are `data`, `primary`, `secondary`, `estimate` or `mock`. Mock rows can't pass for real ones. |
| Traceability | Decision memos cite `run_id`s, so anyone can rebuild the exact numbers behind a decision |

## 3. Datasets

| Dataset | Source | Cadence | Status |
|---|---|---|---|
| `trend_points` | Google Trends (pytrends) | weekly | ✅ backfilled: 48 keywords × 262 weeks (12,576 points) |
| `supplier_offers` | CJ API: product, variant, US-warehouse stock, cost, shipping, images | daily for the shortlist, weekly for the niche catalog | 🔑 `CJ_API_KEY` |
| `market_listings`, `market_query_stats` | eBay Browse API: active listings, price distribution, competition | daily for the shortlist | 🔑 `EBAY_CLIENT_ID/SECRET`. Must also check the Akamai 403 from this environment. |
| `sold_observations` | Terapeak (Seller Hub UI) CSV exports: sold counts, sell-through | weekly, manual | needs an eBay seller account |
| `evaluations` | agent outputs: margin runs, compliance verdicts, scores | per decision | ready |
| `shop_*` (later) | Shopify Admin API orders, Instagram insights | daily | channel 2 |

## 4. How agents use it

- `python -m scout.store tables`, then `query "SELECT ..."` (read-only).
- Canned views come next: `v_candidate_latest` (latest CJ offer + eBay price stats + margin pass/fail) and `v_price_history`.
- Rule (added to `_team-rules.md`): **numbers in decisions come from the store and cite `run_id`.** Web research explains; it doesn't decide.

## 5. Automation

- Ingesters are plain CLIs, so they can run on a schedule: a cloud **Routine** (a fresh session daily) runs the ingesters, commits the new lake files and pushes.
- This needs the API keys in the environment settings.
- Free LLM work (tagging the CJ catalog, image QA) runs inside ingestion through `scout.llm`, with Z.ai GLM Flash first and OpenRouter free models as fallback.

## 6. Build order

1. ✅ Lake + store + Trends ingester.
2. 🔑 CJ ingester as a **dlt REST source** (no custom client; see decision 0003): auth, product search in the niche, US-warehouse variants, stock, cost, shipping quote. Starts with a one-day spike.
3. 🔑 eBay ingester as a **dlt REST source** (OAuth client-credentials helper, no SDK): Browse search per product query, recording the listing count and price distribution.
4. Scoring view that joins CJ and eBay data with `scout.margin`, giving the product shortlist (stage E).
5. Terapeak CSV importer.
6. Scheduled **GitHub Actions** workflow (needs the branch merged to the default branch, plus secrets).

> Visual of this pipeline and the build-vs-reuse plan: private artifact "Dropship Data Model" (https://claude.ai/artifact/VRe8aSLrYV2g9bc8mwzG5K). Tooling choices: `docs/decisions/0003-build-vs-reuse.md`.
