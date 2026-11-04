# Graph Report - drop-shipping-  (2026-11-04)

## Corpus Check
- 158 files · ~125,054 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .csv 15, (none) 4, .example 1)

## Summary
- 1432 nodes · 2345 edges · 112 communities (94 shown, 18 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 74 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `50db94b9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 00 — Research summary and PoC plan
- 02 — Unit economics, success rates, saturation, tariffs
- 01 — eBay dropshipping policy, enforcement, fees
- 04 — Tooling, APIs and AI listing pipeline
- 05 — Legal/IP/compliance risks and other platforms
- 03 — Suppliers and their APIs
- hooks
- CLAUDE.md
- json
- 11 - Google Trends check of Stage B candidates (US)
- 06 — Image sourcing under zero inventory
- 14 — External source review: "I tried AI dropshipping for 7 days" (YouTube transcript)
- AI team operating plan
- 07 — Data sources and free AI tooling
- 08 — eBay US category demand, 2025–2026
- 09 — CJ Dropshipping US warehouses
- 10 — Category risk ranking (US, zero-inventory eBay dropshipping)
- creative-producer.md
- data-analyst.md
- head-of-marketing.md
- sales-lead.md
- compliance-officer.md
- record_run
- steps
- 3. Candidate cards
- Inputs
- 12 — Compliance risk cards for the 8 candidate niches
- 3. Primary niche: `tcg-supplies`
- Warehouse design: Postgres as the source of truth
- Multichannel plan: one pipeline, eBay + Shopify/Instagram
- claude-glm.sh
- db
- Phase: Niche Finder, release R1
- glm-coder.md
- 0003 — Build vs reuse: workflow, data loading, connectors, LLM routing
- data-engineer.md
- 0004 — Postgres warehouse, hosting, and what the source terms allow
- 15 — Postgres hosting, GitHub Actions limits, warehouse tooling
- 16 — Trend and demand sources (US): what we can legitimately ingest
- 17 — Free feeds, and what each API lets us store
- Runbook: Postgres on a VPS, reached by CI through an SSH tunnel
- Operating plan: from desk research to first sale, without the engineering trap
- store_intel.py
- argparse
- 0008 — Internet-metadata harness: find and profile stores from records the web already publishes
- 18 — CJ Dropshipping API cheat sheet
- 0005-cj-client.md
- 23. Estimating units sold from public signals on Shopify stores
- CJ supply check, 2026-11-04: trading-card supplies fail K1; so do both backups
- 24. Traffic calibration and public revenue for Shopify stores
- Look-alike intelligence: reverse-engineer stores that already succeed
- intel.py
- ideas
- dbt_project.yml
- column_types
- 21 — What sells most, and why (no niche assumed)
- models
- models
- dev
- classify.py
- 20 — Source pilots: what each source actually discovered
- 22. Shopify store benchmarks for estimating revenue from traffic
- cj.py
- 0007 — Deterministic harness first, intelligence layer on top
- test_cj.py
- stores.py
- product_category
- test_webmeta.py
- 0009 — Step 1: find the best online stores and reconstruct what they do
- Step 1 flow: how we find the best online stores and what they do
- Plan: find top-performing Shopify stores to take inspiration from
- Estimating sales and profit: how we think about it
- 26. Calibration set widening: Shopify-hosted stores that publish revenue
- test_snapshots.py
- webmeta.py
- Brief for the second agent: independent review, then build the shortlist engine
- CJClient
- snapshot_job.py
- 27 — Can we pre-filter brands and retailers before fetching a store's feed?
- test_warehouse_helpers.py
- csv
- chat
- 25 — Audit of four public Shopify data repos
- summarize_feed
- test_stores.py
- store_export.py
- Business-model rules: validation record (R1 exit criterion)
- 0012-temporal-storage.md
- fit_shop_age
- Best online stores: what they sell and how they get traffic — 2026-11-04
- 28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy
- footprint
- 0006 — DuckDB warehouse: deterministic core, LLM on top
- CJError
- test_shopify_detect.py
- Temporal system: tracking stores over time
- json
- Session state: where the project stands
- 29. Proof-of-performance pilot (10 Shopify stores)
- private_path
- csv
- 30 — Proof of performance for the top 50 candidate stores
- scan_tranche
- _deep_one

## God Nodes (most connected - your core abstractions)
1. `record_run()` - 38 edges
2. `chat()` - 37 edges
3. `column_types` - 24 edges
4. `Inputs` - 21 edges
5. `CJClient` - 21 edges
6. `rebuild()` - 19 edges
7. `compact()` - 18 edges
8. `evaluate()` - 16 edges
9. `diff()` - 16 edges
10. `_product()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Rules that make it deterministic` --references--> `classify()`  [INFERRED]
  docs/decisions/0006-duckdb-warehouse.md → scout/classify.py
- `How we think (standing principles, owner 2026-11-04)` --references--> `chat_many()`  [INFERRED]
  CLAUDE.md → scout/llm.py
- `Layers` --references--> `diff()`  [INFERRED]
  docs/plan/temporal-system.md → scout/snapshots.py
- `What "best" means here` --references--> `business_model()`  [INFERRED]
  docs/decisions/0009-best-store-discovery.md → scout/stores.py
- `Findings` --references--> `_inline_images()`  [INFERRED]
  docs/reviews/2026-11-agent2-project-review.md → scout/llm.py

## Import Cycles
- None detected.

## Communities (112 total, 18 thin omitted)

### Community 0 - "00 — Research summary and PoC plan"
Cohesion: 0.17
Nodes (11): 00 — Research summary and PoC plan, Confidence, Constraint: zero inventory (owner decision, 2026-11-03), Open questions to resolve before building, Phase 0: desk feasibility, $0, ~1–2 weeks of build, Phase 1: listing quality, ~$100–200 (no stock), Phase 2: live micro-test, ~$300–500 working capital, 60 days, PoC plan (feasibility before money) (+3 more)

### Community 1 - "02 — Unit economics, success rates, saturation, tariffs"
Cohesion: 0.18
Nodes (10): 02 — Unit economics, success rates, saturation, tariffs, 1. Worked example: a $30 eBay sale (AliExpress-sourced), 2. Returns, refunds, item-not-received, 3. Success and failure rates, 4. Saturation and Temu/Shein, 5. Tariffs and de minimis (most reliable section), 6. Where margin may still exist (hypotheses, mostly vendor-sourced), 7. What profitable sellers reportedly do differently (+2 more)

### Community 2 - "01 — eBay dropshipping policy, enforcement, fees"
Cohesion: 0.22
Nodes (8): 01 — eBay dropshipping policy, enforcement, fees, 1. Policy, 2. Seller performance standards (US), 3. New sellers, 4. Fees (US, official fee page), 5. Recent changes affecting dropshippers, 6. Seller sentiment (thin evidence), Sources

### Community 3 - "04 — Tooling, APIs and AI listing pipeline"
Cohesion: 0.22
Nodes (8): 04 — Tooling, APIs and AI listing pipeline, 1. eBay developer APIs, 2. Third-party research tools, 3. Finding winning products programmatically, 4. AI for listings, 5. Cassini / Best Match ranking factors, Sources, Takeaways for the PoC

### Community 4 - "05 — Legal/IP/compliance risks and other platforms"
Cohesion: 0.22
Nodes (8): 05 — Legal/IP/compliance risks and other platforms, 1. Copyright: the "clone the listing" part, 2. Trademark, counterfeits, design patents, 3. Product safety and compliance, 4. Consumer protection, 5. Tax and business setup, 6. Platform comparison, Sources

### Community 5 - "03 — Suppliers and their APIs"
Cohesion: 0.25
Nodes (7): 03 — Suppliers and their APIs, API availability (needed for automation), Blind shipping and branding, Quality control, Sources, Stock/price sync risk on eBay, Supplier comparison

### Community 6 - "hooks"
Cohesion: 0.12
Nodes (15): default_install_hook_types, default_stages, exclude, always_run, args, entry, exclude, id (+7 more)

### Community 7 - "CLAUDE.md"
Cohesion: 0.25
Nodes (6): Commands, Context: graphify knowledge graph, graphify, Hard rules, How we think (standing principles, owner 2026-11-04), Project

### Community 8 - "json"
Cohesion: 0.14
Nodes (16): append_cache(), cache_key(), load_cache(), load_ideas(), main(), parse_review(), render(), review() (+8 more)

### Community 9 - "11 - Google Trends check of Stage B candidates (US)"
Cohesion: 0.20
Nodes (9): 11 - Google Trends check of Stage B candidates (US), Commands (exact), Flags for a Nov/Dec start, Headline finding: the scout's growth numbers are distorted, do not use them as-is, Method limits, Per-keyword table, Per-niche ranking, Suggested next steps (+1 more)

### Community 10 - "06 — Image sourcing under zero inventory"
Cohesion: 0.18
Nodes (10): 06 — Image sourcing under zero inventory, 1. Which suppliers license their images to us, 2. What eBay's picture policy allows (fetched), 3. eBay catalog (ePID) images, 4. Checking quality and delivery without stock, 5. CJ follow-up (2026-11-03): supplier decided, Image source for the PoC: **decided 2026-11-03: CJ's own images + AI enhancement of the surroundings** (row 2 below). Google Images look-alikes were rejected for IP and INAD risk., Pipeline rules derived from this (+2 more)

### Community 11 - "14 — External source review: "I tried AI dropshipping for 7 days" (YouTube transcript)"
Cohesion: 0.29
Nodes (6): 14 — External source review: "I tried AI dropshipping for 7 days" (YouTube transcript), His numbers, checked, Plan impact, Red flags, What's useful to us, What the video did

### Community 12 - "AI team operating plan"
Cohesion: 0.25
Nodes (7): 1. Org chart, 2. Operating rules, 3. Pipeline, 4. Model routing and free models, 5. Niche scoring rubric (0–5 per criterion, weighted), 6. What's blocked on the owner, AI team operating plan

### Community 13 - "07 — Data sources and free AI tooling"
Cohesion: 0.25
Nodes (7): 07 — Data sources and free AI tooling, 1. Google Trends, 2. eBay Browse API, 3. Other free US demand signals, 4. OpenRouter free models (fetched: https://openrouter.ai/docs/limits), 5. Image tools (for Phase 1), Sources

### Community 14 - "08 — eBay US category demand, 2025–2026"
Cohesion: 0.29
Nodes (6): 08 — eBay US category demand, 2025–2026, Candidate categories (eBay's strongest growth areas), Gaps, Macro, Sources, Where eBay beats Amazon and Temu (qualitative)

### Community 15 - "09 — CJ Dropshipping US warehouses"
Cohesion: 0.33
Nodes (5): 09 — CJ Dropshipping US warehouses, Category depth, Facts, Implications, Sources

### Community 16 - "10 — Category risk ranking (US, zero-inventory eBay dropshipping)"
Cohesion: 0.50
Nodes (3): 10 — Category risk ranking (US, zero-inventory eBay dropshipping), Cross-cutting facts, Sources

### Community 22 - "record_run"
Cohesion: 0.05
Nodes (39): Shared rules for every AI team member, 1. Architecture, 2. What makes it "authentic", 3. Datasets, 4. How agents use it, 5. Automation, 6. Build order, Data pipeline: feeding the team authentic evidence (+31 more)

### Community 23 - "steps"
Cohesion: 0.08
Nodes (23): concurrency, cancel-in-progress, group, SKIP, jobs, test, name, on (+15 more)

### Community 25 - "3. Candidate cards"
Cohesion: 0.10
Nodes (19): 0001 — Candidate niches (Stage B), 1. Decision, 2. Evidence table, 2a. Margin constraint behind the price targets, 2b. Rubric scores (`docs/plan/ai-team.md` §5), 2c. Sources for the shared premises, 3.1 `tcg-supplies`: trading-card storage and display, 3.2 `hobby-modeling-tools`: miniature and scale-model tools (+11 more)

### Community 26 - "Inputs"
Cohesion: 0.08
Nodes (38): 13 - Sales: landed-cost ceilings and niche economics, 1. Landed-cost ceiling table [data: scout.margin output], 2. Per-niche price bands and representative products, 3. Ranked summary, 4. Gaps and next steps, auto-detailing-tools, coin-supplies, collectibles-display (+30 more)

### Community 27 - "12 — Compliance risk cards for the 8 candidate niches"
Cohesion: 0.10
Nodes (19): 0.1 Checks that apply to every niche, 0.2 Wording rules that apply to every niche (eBay IP policy), 0.3 SKU-level gate (before any listing in any niche), 0.4 Design-patent / Schedule A finding (checked for this card set), 0.5 Prop 65 finding (checked for this card set), 0.6 "Graded card" / "PSA" wording finding, 0. Shared rules, 12 — Compliance risk cards for the 8 candidate niches (+11 more)

### Community 28 - "3. Primary niche: `tcg-supplies`"
Cohesion: 0.10
Nodes (20): 0002 — Niche selection (Stage D), 1. Decision, 2. Evidence table, 2a. Rescore on the §5 rubric (0–5, 5 = best; Risk and Temu/Amazon inverted), 2b. What changed per criterion, and why, 2c. Sensitivity of the primary pick, 2d. Key evidence behind the decision, 3.1 Target buyer (+12 more)

### Community 29 - "Warehouse design: Postgres as the source of truth"
Cohesion: 0.14
Nodes (13): 10. Durability, 11. What this replaces, 12. Build order, 1. Principles, 2. Layers (one schema each), 3. Core model (grain first), 4. Ingestion contract, 5. Enrichment (systematic, deterministic first) (+5 more)

### Community 30 - "Multichannel plan: one pipeline, eBay + Shopify/Instagram"
Cohesion: 0.25
Nodes (7): 1. Why the channels differ, 2. Shared pipeline (generic `scout` core + channel adapters), 3. What the AI team can and can't do, 4. Beauty and cosmetics: the important caveat, 5. Proposed new team roles, 6. Owner decisions needed, Multichannel plan: one pipeline, eBay + Shopify/Instagram

### Community 31 - "claude-glm.sh"
Cohesion: 0.25
Nodes (7): ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL, ANTHROPIC_DEFAULT_HAIKU_MODEL, ANTHROPIC_DEFAULT_OPUS_MODEL, ANTHROPIC_DEFAULT_SONNET_MODEL, API_TIMEOUT_MS, claude-glm.sh script

### Community 32 - "db"
Cohesion: 0.07
Nodes (28): command, environment, healthcheck, image, logging, ports, restart, secrets (+20 more)

### Community 33 - "Phase: Niche Finder, release R1"
Cohesion: 0.20
Nodes (9): After R1 (not part of this phase), Decisions needed from the owner, Exit criteria (R1 is done when all hold), Goal, Out of scope for R1, Phase: Niche Finder, release R1, Stages and who does the work, What I still fix before calling R1 final (+1 more)

### Community 35 - "0003 — Build vs reuse: workflow, data loading, connectors, LLM routing"
Cohesion: 0.33
Nodes (5): 0003 — Build vs reuse: workflow, data loading, connectors, LLM routing, Decision, Home-grown audit (flagged to the team), Next actions, What this does not settle

### Community 36 - "data-engineer.md"
Cohesion: 0.50
Nodes (3): Every change includes, Principles, Rules

### Community 37 - "0004 — Postgres warehouse, hosting, and what the source terms allow"
Cohesion: 0.18
Nodes (10): 0004 — Postgres warehouse, hosting, and what the source terms allow, 1. Decision, 2. New rule: terms gate, 3. What the terms change (the important part), 4. Home-grown audit update, 5. Owner actions, 6. What this does not settle, eBay data cannot simply be stored and analysed (+2 more)

### Community 38 - "15 — Postgres hosting, GitHub Actions limits, warehouse tooling"
Cohesion: 0.25
Nodes (7): 15 — Postgres hosting, GitHub Actions limits, warehouse tooling, 1. Free hosted Postgres, 2. GitHub Actions, 3. Tooling, 4. Pattern check, Ranked recommendation (from the agent), Sources

### Community 39 - "16 — Trend and demand sources (US): what we can legitimately ingest"
Cohesion: 0.29
Nodes (6): 16 — Trend and demand sources (US): what we can legitimately ingest, Implications for the warehouse, Sources, Sources, ranked by value / cost / legal safety, Storage and use constraints found, Verdict by platform

### Community 40 - "17 — Free feeds, and what each API lets us store"
Cohesion: 0.33
Nodes (5): 17 — Free feeds, and what each API lets us store, A. eBay API License Agreement (verified against https://developer.ebay.com/develop/apis/api-license-agreement), B. Other storage terms, C. Free feeds, ranked, Sources

### Community 41 - "Runbook: Postgres on a VPS, reached by CI through an SSH tunnel"
Cohesion: 0.14
Nodes (13): 0. What you are building, 10. Leaving, 1. Choose the server, 2. Harden the server (one time, as root, from your laptop), 3. Install Docker, 4. Start Postgres, 5. The CI tunnel user (can do nothing except forward one port), 6. GitHub secrets (repository settings, Secrets and variables, Actions) (+5 more)

### Community 42 - "Operating plan: from desk research to first sale, without the engineering trap"
Cohesion: 0.14
Nodes (13): 0. Status today, 1. Guardrails against the engineering trap, 2. Model plan: GLM + OpenRouter, and what the €10 is for, 3. Calendar, 4. Weekly review (every Sunday, 30 min), 5. The SaaS option: keep the door open, don't walk through it yet, 6. Parking lot (not before 20 live listings), 7. Owner actions, in order (+5 more)

### Community 43 - "store_intel.py"
Cohesion: 0.16
Nodes (20): _numbers(), append_cache(), _clean(), gaps(), grounded(), walk(), load_cache(), _ls() (+12 more)

### Community 44 - "argparse"
Cohesion: 0.25
Nodes (6): main(), sweep(), main(), parse(), sample(), seen()

### Community 45 - "0008 — Internet-metadata harness: find and profile stores from records the web already publishes"
Cohesion: 0.25
Nodes (7): 0008 — Internet-metadata harness: find and profile stores from records the web already publishes, Automated demand signals that replace Terapeak, Gaps and fixes for the next run, Pilot result (2026-11-04), Terapeak is dropped, The idea, Wider run (2026-11-04, 1,200 domains)

### Community 46 - "18 — CJ Dropshipping API cheat sheet"
Cohesion: 0.22
Nodes (8): 18 — CJ Dropshipping API cheat sheet, Endpoints, Limits and errors, Live findings (2026-11-04, first key), Minimal call sequence, Official MCP server, Sources, Terms

### Community 48 - "23. Estimating units sold from public signals on Shopify stores"
Cohesion: 0.12
Nodes (15): 1. Review rate (reviews per order), 23. Estimating units sold from public signals on Shopify stores, 2. Units from review counts (the conversion), 3. Review-count velocity from schema.org JSON-LD snapshots, 4. Amazon "bought in past month" and Etsy "sold" as analogues (not usable for us), 5. Sold-out flips (variant availability), 6. Within-store ranking from "best sellers" collections, 7. Shopify published figures (sanity check for store distribution) (+7 more)

### Community 49 - "CJ supply check, 2026-11-04: trading-card supplies fail K1; so do both backups"
Cohesion: 0.29
Nodes (6): 1. Result, 2. What CJ's US warehouse actually holds, 3. Real cost floor, 4. Options (owner decision), 5. Other findings, CJ supply check, 2026-11-04: trading-card supplies fail K1; so do both backups

### Community 50 - "24. Traffic calibration and public revenue for Shopify stores"
Cohesion: 0.13
Nodes (14): 24. Traffic calibration and public revenue for Shopify stores, A1. What each ranking publishes, A2. Any published rank-to-visits mapping, Answer first, B1. Candidates that meet the revenue and Shopify tests (partly), B2. Shopify case-study revenue without a usable fiscal year (vendor-stated), B3. Candidates excluded, B4. What the set can and cannot do (+6 more)

### Community 51 - "Look-alike intelligence: reverse-engineer stores that already succeed"
Cohesion: 0.25
Nodes (7): 1. The idea in one paragraph, 2. Evidence we need, the traces, and candidate sources, 3. Pilot protocol (small sample, measured), 4. The store dossier (what "crack the code" produces), 5. Rules that still apply, 6. Pilot 1 (started 2026-11-04), Look-alike intelligence: reverse-engineer stores that already succeed

### Community 52 - "intel.py"
Cohesion: 0.14
Nodes (16): _cell(), grounded(), narrate(), pack(), pack_hash(), render(), template(), test_cache_hit_never_calls_the_model() (+8 more)

### Community 53 - "ideas"
Cohesion: 0.33
Nodes (5): brief, ideas, description, id, title

### Community 54 - "dbt_project.yml"
Cohesion: 0.06
Nodes (30): config-version, +schema, +schema, flags, send_anonymous_usage_stats, macro-paths, +schema, model-paths (+22 more)

### Community 55 - "column_types"
Cohesion: 0.07
Nodes (29): action, border_or_collage, category, child, clean, image_sha256, level1, level2 (+21 more)

### Community 56 - "21 — What sells most, and why (no niche assumed)"
Cohesion: 0.25
Nodes (7): 1. What US shoppers buy most online (category level), 21 — What sells most, and why (no niche assumed), 2. What CJ's US warehouse can supply, and what dropshippers bet on, 3. Where demand, supply and our constraints overlap, 4. The "why" pattern behind the strongest sellers, 5. Cross-check: margin-viable vs popular [data], 6. Next step (method, not guesses)

### Community 57 - "models"
Cohesion: 0.15
Nodes (12): data_tests, name, max_listing_price, max_weight_g, min_us_stock, in_range, models, columns (+4 more)

### Community 58 - "models"
Cohesion: 0.20
Nodes (9): data_tests, name, accepted_values, in_range, models, columns, description, name (+1 more)

### Community 59 - "dev"
Cohesion: 0.25
Nodes (7): path, threads, type, dev, scout, outputs, target

### Community 63 - "classify.py"
Cohesion: 0.26
Nodes (10): _append(), classify(), load_cache(), main(), parse_labels(), phrases(), title_hash(), test_classify_caches_by_title_hash_not_title() (+2 more)

### Community 64 - "20 — Source pilots: what each source actually discovered"
Cohesion: 0.33
Nodes (5): 20 — Source pilots: what each source actually discovered, Fixes for the next round, Manual steps that remain valuable (owner, about 20–30 minutes each), Scorecard, What worked, what didn't

### Community 65 - "22. Shopify store benchmarks for estimating revenue from traffic"
Cohesion: 0.14
Nodes (13): 1. Conversion rate (Shopify), 22. Shopify store benchmarks for estimating revenue from traffic, 2. Average order value (AOV), 3. Units per order, 4. Traffic channel mix (paid vs organic vs email), 5. Ad spend share of revenue (blended CAC / MER), 6. Return rates by category, How we would use these (+5 more)

### Community 66 - "cj.py"
Cohesion: 0.14
Nodes (12): 6. Part 2: build the shortlist engine (stage E of `docs/plan/ai-team.md`), _dicts(), _json_list(), normalize_detail(), normalize_freight(), normalize_listing(), normalize_stock(), _num() (+4 more)

### Community 67 - "0007 — Deterministic harness first, intelligence layer on top"
Cohesion: 0.33
Nodes (5): 0007 — Deterministic harness first, intelligence layer on top, How to run, New in this decision, Open: where history lives, The split

### Community 68 - "test_cj.py"
Cohesion: 0.16
Nodes (15): client(), FakeResp, FakeSession, test_a_non_json_response_is_a_clear_error(), test_a_second_auth_failure_is_not_retried_forever(), test_detail_ignores_junk_variants_and_images(), test_detail_normalizes_images_and_variants(), test_detail_parses_live_string_numbers_and_json_list_fields() (+7 more)

### Community 69 - "stores.py"
Cohesion: 0.15
Nodes (16): _all_rows(), deep_targets(), _done(), load_rules(), main(), _meta_one(), meta_summary(), _parallel() (+8 more)

### Community 70 - "product_category"
Cohesion: 0.21
Nodes (9): classify_product(), product_category(), _product_text(), _p(), test_added_categories(), test_product_category(), test_summarize_feed_aggregates_without_text(), test_type_wins_over_title_but_falls_back_when_unknown() (+1 more)

### Community 71 - "test_webmeta.py"
Cohesion: 0.20
Nodes (7): parse_sitemap(), summarize_products(), traffic_tags(), test_bad_xml_is_empty_not_a_crash(), test_parse_sitemap_index_and_urlset(), test_summarize_products_keeps_aggregates_only(), test_traffic_tags_detect_paid_and_owned_channels()

### Community 72 - "0009 — Step 1: find the best online stores and reconstruct what they do"
Cohesion: 0.20
Nodes (9): 0009 — Step 1: find the best online stores and reconstruct what they do, HOMEGROWN, myip.ms terms (read 2026-11-04), Results, Rules kept, Source terms (terms gate), Store start date, The myip.ms idea, from open data (+1 more)

### Community 73 - "Step 1 flow: how we find the best online stores and what they do"
Cohesion: 0.33
Nodes (5): Diagram, How it works, step by step, Rules that apply throughout, Step 1 flow: how we find the best online stores and what they do, What this cannot tell us

### Community 74 - "Plan: find top-performing Shopify stores to take inspiration from"
Cohesion: 0.17
Nodes (11): Is the current approach good? An honest verdict, Owner tasks, Phase 2 result (2026-11-04), Phases (small first: a 10-store pilot before every sweep), Plan: find top-performing Shopify stores to take inspiration from, Revision after the Phase 2 pilot (2026-11-04), Risks, Team and work (+3 more)

### Community 75 - "Estimating sales and profit: how we think about it"
Cohesion: 0.17
Nodes (11): Build order (small first: 20 stores, then 200, then the full list), Calibrating the estimator (so we know how wrong it is), Estimating sales and profit: how we think about it, Lessons from similar open-source projects (owner review, 2026-11-04), Q1: are people buying? Signals, strongest first, Q2: could we profit? Our own numbers, Q3: can we reproduce the offer? A checklist, not a number, Research feeding this plan (written by the research agents) (+3 more)

### Community 76 - "26. Calibration set widening: Shopify-hosted stores that publish revenue"
Cohesion: 0.25
Nodes (7): 26. Calibration set widening: Shopify-hosted stores that publish revenue, Checked and not found, Method and limits (read first), Sources, Summary, Table: entries found, Tranco check

### Community 77 - "test_snapshots.py"
Cohesion: 0.06
Nodes (54): 0011 — Weekly store snapshots: reuse and build, Candidates, Decision, Rules in the job, compact(), _date_part(), diff(), _is_int_id() (+46 more)

### Community 79 - "webmeta.py"
Cohesion: 0.18
Nodes (8): discover(), is_shopify(), keyword_hits(), _tranco_list(), txt_signals(), test_keyword_hits_use_the_name_not_the_tld(), test_shopify_detection_by_ip_range_or_cname(), test_txt_signals_reveal_platforms()

### Community 80 - "Brief for the second agent: independent review, then build the shortlist engine"
Cohesion: 0.25
Nodes (7): 1. Project in four lines, 2. Read first (in this order, about 30 minutes), 3. Ground rules (from `CLAUDE.md`, restated because they matter most), 4. How to work, 5. Part 1: independent review (DONE, merged as PR #1; read `docs/reviews/2026-11-agent2-project-review.md`), 7. When you finish, Brief for the second agent: independent review, then build the shortlist engine

### Community 81 - "CJClient"
Cohesion: 0.24
Nodes (9): CJClient, main(), catalogue(), flatten_categories(), image_rows(), images(), main(), offers() (+1 more)

### Community 82 - "snapshot_job.py"
Cohesion: 0.11
Nodes (27): diff_runs(), feed_status(), fetch_feed(), _intkeys(), main(), review_app(), review_sample(), run() (+19 more)

### Community 83 - "27 — Can we pre-filter brands and retailers before fetching a store's feed?"
Cohesion: 0.29
Nodes (6): 27 — Can we pre-filter brands and retailers before fetching a store's feed?, Answer, Pilot results, Untested ideas (hypotheses), What a filter would cost, What we do instead

### Community 84 - "test_warehouse_helpers.py"
Cohesion: 0.20
Nodes (6): FakeCJ, test_flatten_categories_keeps_three_levels(), test_image_rows_dedupe_and_number_positions(), test_image_verdict_needs_all_checks_and_marks_clean(), test_offers_lands_variants_stock_and_freight_for_cheapest_variant(), test_parse_labels_keeps_only_valid_entries()

### Community 85 - "csv"
Cohesion: 0.26
Nodes (6): load_cache(), main(), parse_verdict(), screen(), url_hash(), test_screen_skips_failures_and_yields_hash_keyed_rows()

### Community 86 - "chat"
Cohesion: 0.06
Nodes (42): chat(), chat_many(), one(), order(), _extract_text(), _inline_images(), is_or_free(), is_paid() (+34 more)

### Community 87 - "25 — Audit of four public Shopify data repos"
Cohesion: 0.40
Nodes (4): 25 — Audit of four public Shopify data repos, Summary, What each one taught us, What we reuse and what we build

### Community 88 - "summarize_feed"
Cohesion: 0.17
Nodes (8): dropship_traces(), _light_one(), _norm(), _quantile(), summarize_feed(), vendor_is_shop(), test_dropship_traces(), test_vendor_is_shop()

### Community 89 - "test_stores.py"
Cohesion: 0.19
Nodes (13): business_model(), category_spread(), _m(), test_app_developer_with_dropship_code_is_not_a_dropshipper(), test_business_model_rules(), test_dominant_vendor_or_few_labels_means_brand(), test_general_store_pattern_is_separate_from_brand(), test_homepage_signals_include_marketing_apps() (+5 more)

### Community 90 - "store_export.py"
Cohesion: 0.27
Nodes (5): main(), niche_score(), rows(), table(), main()

### Community 91 - "Business-model rules: validation record (R1 exit criterion)"
Cohesion: 0.25
Nodes (7): Business-model rules: validation record (R1 exit criterion), Error classes (carry into the rules and the report), Pipeline bugs found by testing small, Result and the change made, Rounds, latest_good(), test_failed_refresh_never_replaces_a_good_profile()

### Community 93 - "fit_shop_age"
Cohesion: 0.40
Nodes (3): fit_shop_age(), shop_started_by(), test_shop_age_curve_is_monotone_lower_envelope()

### Community 94 - "Best online stores: what they sell and how they get traffic — 2026-11-04"
Cohesion: 0.25
Nodes (7): Best online stores: what they sell and how they get traffic — 2026-11-04, Business model of every screened US store, Categories the best stores win with, Funnel, How they get traffic, Niche shortlist for step 2 (sourcing), Who is moving: rank history of the copyable stores

### Community 95 - "28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy"
Cohesion: 0.20
Nodes (9): 28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy, Advisor reading (2026-11-04), Caveats `[unverified]`, Implied miss rate, Method, Question, Recommendation, Results `[data]` (+1 more)

### Community 96 - "footprint"
Cohesion: 0.31
Nodes (8): Next tasks, in order (focus from 2026-11-04: reconstruct and recreate store success), footprint(), _latest(), main(), products(), resolve_a(), _session(), sitemaps()

### Community 97 - "0006 — DuckDB warehouse: deterministic core, LLM on top"
Cohesion: 0.25
Nodes (7): 0006 — DuckDB warehouse: deterministic core, LLM on top, Choice, Intelligence layer (next), Layers, Out of scope for this slice, Rules that make it deterministic, Why now

### Community 99 - "test_shopify_detect.py"
Cohesion: 0.11
Nodes (19): is_blocked(), is_shopify(), probe(), _robots_allows(), shopify_evidence(), _Resp, _Sess, test_blocked() (+11 more)

### Community 100 - "Temporal system: tracking stores over time"
Cohesion: 0.25
Nodes (7): Build order, Cadence and cost, Feature definitions (so the numbers are explainable), Layers, Temporal system: tracking stores over time, What is reconstructible and what is forward-only, What the rank history already shows (26 dates, 2 years)

### Community 101 - "json"
Cohesion: 0.16
Nodes (8): analyze(), _fetch(), main(), flatten(), main(), write_csv(), main(), parse_cell()

### Community 102 - "Session state: where the project stands"
Cohesion: 0.22
Nodes (8): Facts that change plans, Owner tasks outstanding, Repo, Review panel result (2026-11-04) — read before starting, Session state: where the project stands, Traps in a fresh container, Update: data vault and approved re-scope (2026-11-04, late), What exists

### Community 106 - "29. Proof-of-performance pilot (10 Shopify stores)"
Cohesion: 0.20
Nodes (9): 29. Proof-of-performance pilot (10 Shopify stores), Grade counts, Method, Open items, Recommendation for the 300-store sweep, Result in one line, Sources: useful and useless, Terms concerns (+1 more)

### Community 109 - "csv"
Cohesion: 0.17
Nodes (8): med(), append_cache(), load_cache(), load_evidence(), main(), main(), median(), test_cache_round_trip()

### Community 112 - "30 — Proof of performance for the top 50 candidate stores"
Cohesion: 0.25
Nodes (7): 30 — Proof of performance for the top 50 candidate stores, How the 50 were chosen, Model lesson, Next, Result: independent proof grade, Sources that worked and failed, What this tells us

### Community 115 - "scan_tranche"
Cohesion: 0.29
Nodes (6): Update: phase Niche Finder R1 (2026-11-04, later), scan(), scan_tranche(), job(), tranches_done(), test_scan_tranche_keeps_only_shopify_and_counts()

### Community 117 - "_deep_one"
Cohesion: 0.28
Nodes (8): _deep_one(), homepage_signals(), aggregate_rating(), dns(), jsonld(), social_links(), test_jsonld_same_as_and_rating(), test_social_links_skip_share_buttons()

## Knowledge Gaps
- **6 isolated node(s):** `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 785 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `record_run()` connect `record_run` to `footprint`, `stores.py`, `json`, `csv`, `webmeta.py`, `CJClient`, `snapshot_job.py`, `scan_tranche`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `record_run()` (e.g. with `Shared rules for every AI team member` and `2. What makes it "authentic"`) actually correct?**
  _`record_run()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `hooks` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `business_model()` connect `test_stores.py` to `stores.py`, `0009 — Step 1: find the best online stores and reconstruct what they do`, `_deep_one`, `summarize_feed`, `Business-model rules: validation record (R1 exit criterion)`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `chat()` (e.g. with `main()` and `main()`) actually correct?**
  _`chat()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.13666666666666666 - nodes in this community are weakly interconnected._