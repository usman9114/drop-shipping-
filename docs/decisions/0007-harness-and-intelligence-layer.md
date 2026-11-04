# 0007 — Deterministic harness first, intelligence layer on top

> Status: **accepted** (owner, 2026-11-04: "instead of agents, make deterministic scripts automate this flow; let scripts pull data in an organised manner, then the intelligence layer kicks in"). Extends decision 0006 (DuckDB warehouse). Code: `warehouse/`, `scout/intel.py`, `make pipeline`.

> **2026-11-04: Terapeak dropped** (owner: if it cannot be automated, it is out). Automated replacements are listed in decision 0008.

## The split

| Layer | What runs | Deterministic? | Where |
|---|---|---|---|
| Collect | CJ catalogue, offers (detail, stock, freight), categories | Yes. Same inputs give the same runs; every run is append-only with provenance | `scout/ingest_cj.py` → `data/private/lake` |
| Collect (manual) | Owner's Terapeak readings | Yes (CSV) | `data/observations/*.csv` |
| Transform and test | staging → enrich → core → marts, with dbt tests | Yes | `warehouse/models` |
| Rules | product types, exclusions, **why-tags** | Yes (versioned seeds) | `warehouse/seeds/rule_*.csv` |
| Intelligence | Narrative per product type from an evidence pack | **Model**, but cached and checked | `scout/intel.py` → `docs/reports/` |

Agents stay for one-off research (new sources, terms checks). Anything repeated becomes a script.

## New in this decision

1. **History (velocity).** `stg_cj_product_snapshots` reads *every* catalogue run, not only the latest. `mart_product_velocity` gives, per product: stock drawdown (sum of falls in CJ US stock, ignoring restocks), restock count, growth in the number of stores listing it, and rates per day once at least half a day of history exists. CJ's US stock is shared by every store selling the item, so its fall is the nearest thing to a sales meter we have. **This is a hypothesis to validate against eBay sold counts:** restocks, CJ's own sales channels and stock moves can all distort it.
2. **eBay demand intake.** `stg_terapeak_observations` reads the owner's filled Terapeak sheets and joins them by product type. These are the owner's own notes from eBay's seller tool, not API data (decision 0004).
3. **Why-tags.** `rule_why` maps each product type to reasons it sells: repeat purchase, video demo, giftable, problem solver, seasonal Q4, collectible, routine care. Impulse price (median floor ≤ $25) is computed, not tagged. Tags are judgments, labelled as such in reports, and changed by editing the seed.
4. **Evidence mart.** `mart_type_evidence`: one row per product type with supply, margin, popularity, velocity, eBay demand, flags and tags. The intelligence layer reads **only** this table.
5. **Intelligence layer.** `scout.intel` builds one evidence pack per type. A free model writes 3–5 sentences from the pack. Guards:
   - **Cache:** keyed by sha256 of the pack plus the prompt version, in `warehouse/seeds/llm_story_cache.csv`. Same data gives the same report with no model call.
   - **Grounding:** any number in the narrative that is not in the pack rejects the text, and a fixed template is used.
   - **Labels:** each narrative is marked cache, llm, template, or template (model text rejected).
   - The model never decides compliance or pass/fail; those come from rules and `scout.margin`.

## How to run

```bash
make pipeline      # wh-load, wh-catalogue, wh-offers, wh-build, wh-export, intel
make wh-snapshot   # catalogue only; run daily so velocity accumulates
make intel         # report only, from the current warehouse
```

## Open: where history lives

Velocity needs snapshots across days. The lake sits in `data/private/` inside an ephemeral container, and raw CJ data may not be committed to this public repo (terms gate). Options for the owner:

| Option | Effort | Notes |
|---|---|---|
| **Private GitHub repo for data** (recommended) | Owner creates it and gives this project access; a daily GitHub Actions job runs `make wh-snapshot` and commits the new lake files there | Free, durable, versioned, private |
| The VPS from decision 0004 | Owner provisions it | When Postgres comes back |
| Keep a session alive and snapshot by hand | None | Fragile; loses history when the container is recycled |

`HOMEGROWN`: `scout/intel.py` (about 250 lines, tested). There is no maintained tool that writes grounded narratives from a fixed evidence table under our cache and terms rules; it is glue around our own free-model client.
