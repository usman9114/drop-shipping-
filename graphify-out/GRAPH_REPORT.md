# Graph Report - drop-shipping-  (2026-11-05)

## Corpus Check
- 196 files · ~165,033 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .csv 15, (none) 4, .example 1)

## Summary
- 1995 nodes · 3433 edges · 152 communities (135 shown, 17 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d4a7ee92`
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
- chat_many
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
- pathlib
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
- test_fingerprints.py
- 32b. TikTok ads: official routes to see other advertisers' ads
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
- feed_signals
- Idea review panel — 2026-11-04
- supply_estimate
- classify.py
- 20 — Source pilots: what each source actually discovered
- 22. Shopify store benchmarks for estimating revenue from traffic
- test_cj.py
- 0007 — Deterministic harness first, intelligence layer on top
- 32c. Trustpilot and Google Ads Transparency: legal automation routes
- __init__.py
- time
- 32a. Meta Ad Library API: official route for brand ad monitoring
- 0009 — Step 1: find the best online stores and reconstruct what they do
- Step 1 flow: how we find the best online stores and what they do
- Plan: find top-performing Shopify stores to take inspiration from
- Estimating sales and profit: how we think about it
- 26. Calibration set widening: Shopify-hosted stores that publish revenue
- test_snapshots.py
- 35. Fingerprint validation (W3): how far can we trust each indicator?
- argparse
- Tool shortlist from the owner (2026-11-05)
- CJClient
- snapshot_job.py
- 27 — Can we pre-filter brands and retailers before fetching a store's feed?
- llm.py
- Plan: read a store's hidden supply fingerprints and estimate its source
- test_trends_llm.py
- 25 — Audit of four public Shopify data repos
- lake_sync.py
- 2. Per-niche price bands and representative products
- run_batch
- re
- 0012-temporal-storage.md
- fit_shop_age
- Best online stores: what they sell and how they get traffic — 2026-11-04
- webmeta.py
- __init__.py
- json
- min_price
- test_shopify_detect.py
- Data pipeline: feeding the team authentic evidence
- Autopilot: the store pipeline runs 24/7 on scripts
- unblock.py
- _shop_hits
- 2. Per-niche price bands and representative products
- cj.py
- 29. Proof-of-performance pilot (10 Shopify stores)
- csv
- pytest
- 0013 — Automating ad and review checks: official routes only
- Opportunity (parked): stores that try hard but underperform
- __init__.py
- 30 — Proof of performance for the top 50 candidate stores
- 31 — What the top-performing Shopify stores have in common
- test_autopilot_discovery.py
- 0014 — Crawl4AI for review counts on store pages
- 33a Fingerprints: AliExpress import and fulfilment apps (Shopify)
- glm-worker.md
- test_trends_llm.py
- 0006 — DuckDB warehouse: deterministic core, LLM on top
- Findings
- 33c. Supply fingerprints: print-on-demand apps, themes and marketing kits, tracking apps and carriers
- or_free_used
- 33b. Supply fingerprints: US/EU suppliers, dropship apps and 3PL apps
- test_autopilot.py
- second_opinion
- failing_open
- UI/UX brief (design phase, no production build yet)
- autopilot.py
- sys
- Session state: where the project stands
- steps
- 0016 — Autopilot runs on GitHub Actions; storage on Supabase (free tier)
- stores.py
- quiet.py
- datetime
- mode
- test_warehouse_helpers.py
- autopilot.yml
- Brief for the second agent: independent review, then build the shortlist engine
- health
- cj_sweep.py
- pathlib
- env
- _checked_path
- fingerprint_host
- check_no_ai_attribution.py
- exc_token
- daily
- conftest.py
- Shared rules for every AI team member
- test_dsers_sku_rejects_brand_style_skus

## God Nodes (most connected - your core abstractions)
1. `record_run()` - 47 edges
2. `chat()` - 42 edges
3. `supply_estimate()` - 30 edges
4. `feed_signals()` - 29 edges
5. `column_types` - 24 edges
6. `CJClient` - 21 edges
7. `Inputs` - 21 edges
8. `fetch()` - 21 edges
9. `prod()` - 20 edges
10. `push()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Next, in order` --references--> `daily()`  [INFERRED]
  docs/handoff/session-state.md → scout/autopilot.py
- `Where we are (2026-11-05)` --references--> `daily()`  [INFERRED]
  docs/handoff/session-state.md → scout/autopilot.py
- `Rules that make it deterministic` --references--> `classify()`  [INFERRED]
  docs/decisions/0006-duckdb-warehouse.md → scout/classify.py
- `Proposed WEIGHTS and rule changes (applied 2026-11-05 in `RULE_VERSION` 2026-11-05.3, see below)` --references--> `supply_estimate()`  [INFERRED]
  docs/research/35-fingerprint-validation.md → scout/fingerprints.py
- `1. Landed-cost ceiling table [data: scout.margin output]` --references--> `evaluate()`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py

## Import Cycles
- 2-file cycle: `scout/stores.py -> scout/webmeta.py -> scout/stores.py`

## Communities (152 total, 17 thin omitted)

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

### Community 7 - "chat_many"
Cohesion: 0.15
Nodes (10): Commands, Context: graphify knowledge graph, graphify, Hard rules, How we think (standing principles, owner 2026-11-04), Project, chat_many(), one() (+2 more)

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
Cohesion: 0.14
Nodes (18): _git_sha(), main(), query(), rebuild(), record_run(), _runs(), lake(), test_a_failed_rebuild_leaves_the_old_database_intact() (+10 more)

### Community 23 - "steps"
Cohesion: 0.08
Nodes (23): concurrency, cancel-in-progress, group, SKIP, jobs, test, name, on (+15 more)

### Community 25 - "3. Candidate cards"
Cohesion: 0.10
Nodes (19): 0001 — Candidate niches (Stage B), 1. Decision, 2. Evidence table, 2a. Margin constraint behind the price targets, 2b. Rubric scores (`docs/plan/ai-team.md` §5), 2c. Sources for the shared premises, 3.1 `tcg-supplies`: trading-card storage and display, 3.2 `hobby-modeling-tools`: miniature and scale-model tools (+11 more)

### Community 26 - "pathlib"
Cohesion: 0.27
Nodes (5): main(), niche_score(), rows(), table(), main()

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

### Community 43 - "test_fingerprints.py"
Cohesion: 0.13
Nodes (19): page_signals(), _feed(), test_aliorders_means_aliexpress(), test_aliorders_script_fires(), test_app_embed_handles(), test_asyncload_hosts_hostnames_only(), test_brand_like_feed_is_quiet(), test_no_asyncload_no_hosts() (+11 more)

### Community 44 - "32b. TikTok ads: official routes to see other advertisers' ads"
Cohesion: 0.18
Nodes (10): 1. Commercial Content API [primary unless tagged], 2. Ad Library website, 32b. TikTok ads: official routes to see other advertisers' ads, 3. Creative Center, 4. Coverage for our 17 brands, Notes, Recommendation (evidence-limited), Short answer (+2 more)

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
Cohesion: 0.13
Nodes (21): append_cache(), _cell(), grounded(), load_cache(), load_evidence(), main(), narrate(), pack() (+13 more)

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

### Community 60 - "feed_signals"
Cohesion: 0.14
Nodes (22): _country(), feed_signals(), _share(), _tags(), prod(), test_ae_image_and_o1cn(), test_boilerplate_and_cjk_counts_only(), test_bulk_burst_and_grams_and_ratio() (+14 more)

### Community 61 - "Idea review panel — 2026-11-04"
Cohesion: 0.12
Nodes (15): I01 — Core thesis, I02 — Supply-first product selection, I03 — Better listings from supplier images, I04 — CJ stock drawdown as a sales meter, I05 — CJ listing count as a popularity signal, I06 — Look-alike discovery from internet metadata, I07 — Traffic footprint of look-alike stores, I08 — Study Shopify stores although our channel is eBay (+7 more)

### Community 62 - "supply_estimate"
Cohesion: 0.14
Nodes (14): _clamp(), _noisy_or(), supply_estimate(), test_cj_sku_means_cj(), test_cjk_alone_does_not_pick_a_source(), test_contested_source_lowers_confidence(), test_generic_only_no_longer_claims_dropship(), test_no_evidence_is_unknown() (+6 more)

### Community 63 - "classify.py"
Cohesion: 0.26
Nodes (10): _append(), classify(), load_cache(), main(), parse_labels(), phrases(), title_hash(), test_classify_caches_by_title_hash_not_title() (+2 more)

### Community 64 - "20 — Source pilots: what each source actually discovered"
Cohesion: 0.33
Nodes (5): 20 — Source pilots: what each source actually discovered, Fixes for the next round, Manual steps that remain valuable (owner, about 20–30 minutes each), Scorecard, What worked, what didn't

### Community 65 - "22. Shopify store benchmarks for estimating revenue from traffic"
Cohesion: 0.14
Nodes (13): 1. Conversion rate (Shopify), 22. Shopify store benchmarks for estimating revenue from traffic, 2. Average order value (AOV), 3. Units per order, 4. Traffic channel mix (paid vs organic vs email), 5. Ad spend share of revenue (blended CAC / MER), 6. Return rates by category, How we would use these (+5 more)

### Community 66 - "test_cj.py"
Cohesion: 0.16
Nodes (16): client(), FakeResp, FakeSession, test_a_non_json_response_is_a_clear_error(), test_a_second_auth_failure_is_not_retried_forever(), test_detail_ignores_junk_variants_and_images(), test_detail_normalizes_images_and_variants(), test_detail_parses_live_string_numbers_and_json_list_fields() (+8 more)

### Community 67 - "0007 — Deterministic harness first, intelligence layer on top"
Cohesion: 0.33
Nodes (5): 0007 — Deterministic harness first, intelligence layer on top, How to run, New in this decision, Open: where history lives, The split

### Community 68 - "32c. Trustpilot and Google Ads Transparency: legal automation routes"
Cohesion: 0.13
Nodes (14): 32c. Trustpilot and Google Ads Transparency: legal automation routes, Express permission, Gaps, Notes on the public Business Units API, Part 1: Trustpilot, Part 2: Google Ads Transparency, Pilot status, Recommendation (Google) (+6 more)

### Community 69 - "__init__.py"
Cohesion: 0.16
Nodes (16): dropship_confidence(), extract_policy_signals(), _fetch_policies_async(), PolicySignals, one(), test_boilerplate_refund_detected(), test_confidence_high_when_product_label_dropship_and_slow_ship(), test_confidence_low_when_brand_and_fast_ship() (+8 more)

### Community 70 - "time"
Cohesion: 0.10
Nodes (25): Business-model rules: validation record (R1 exit criterion), Error classes (carry into the rules and the report), Pipeline bugs found by testing small, Result and the change made, Rounds, business_model(), category_spread(), dropship_traces() (+17 more)

### Community 71 - "32a. Meta Ad Library API: official route for brand ad monitoring"
Cohesion: 0.25
Nodes (7): 1. Summary table, 2. Access steps (all [unverified] until the owner reads the official page), 32a. Meta Ad Library API: official route for brand ad monitoring, 3. Report, CSV and Meta Content Library, 4. Practical coverage for us (plain statement), 5. Recommendation (limited to the evidence), Sources

### Community 72 - "0009 — Step 1: find the best online stores and reconstruct what they do"
Cohesion: 0.20
Nodes (9): 0009 — Step 1: find the best online stores and reconstruct what they do, HOMEGROWN, myip.ms terms (read 2026-11-04), Results, Rules kept, Source terms (terms gate), Store start date, The myip.ms idea, from open data (+1 more)

### Community 73 - "Step 1 flow: how we find the best online stores and what they do"
Cohesion: 0.33
Nodes (5): Diagram, How it works, step by step, Rules that apply throughout, Step 1 flow: how we find the best online stores and what they do, What this cannot tell us

### Community 74 - "Plan: find top-performing Shopify stores to take inspiration from"
Cohesion: 0.15
Nodes (12): Is the current approach good? An honest verdict, Owner tasks, Phase 2 result (2026-11-04), Phases 3 and 4 result (2026-11-04), Phases (small first: a 10-store pilot before every sweep), Plan: find top-performing Shopify stores to take inspiration from, Revision after the Phase 2 pilot (2026-11-04), Risks (+4 more)

### Community 75 - "Estimating sales and profit: how we think about it"
Cohesion: 0.17
Nodes (11): Build order (small first: 20 stores, then 200, then the full list), Calibrating the estimator (so we know how wrong it is), Estimating sales and profit: how we think about it, Lessons from similar open-source projects (owner review, 2026-11-04), Q1: are people buying? Signals, strongest first, Q2: could we profit? Our own numbers, Q3: can we reproduce the offer? A checklist, not a number, Research feeding this plan (written by the research agents) (+3 more)

### Community 76 - "26. Calibration set widening: Shopify-hosted stores that publish revenue"
Cohesion: 0.25
Nodes (7): 26. Calibration set widening: Shopify-hosted stores that publish revenue, Checked and not found, Method and limits (read first), Sources, Summary, Table: entries found, Tranco check

### Community 77 - "test_snapshots.py"
Cohesion: 0.05
Nodes (61): 0011 — Weekly store snapshots: reuse and build, Candidates, Decision, Rules in the job, Build order, Cadence and cost, Feature definitions (so the numbers are explainable), Layers (+53 more)

### Community 78 - "35. Fingerprint validation (W3): how far can we trust each indicator?"
Cohesion: 0.14
Nodes (12): 35. Fingerprint validation (W3): how far can we trust each indicator?, Accuracy before/after, Applied (2026-11-05, `RULE_VERSION` 2026-11-05.3), Free-model second opinion `[proxy]`, Method and limits, Per-indicator precision `[data]` (sample, `unclear` excluded), Proposed WEIGHTS and rule changes (applied 2026-11-05 in `RULE_VERSION` 2026-11-05.3, see below), Signatures and rules worth adding (from 33a, 33b, 33c plus what we saw) (+4 more)

### Community 79 - "argparse"
Cohesion: 0.13
Nodes (14): main(), profile_many(), run(), fingerprint_many(), main(), queue(), run(), run() (+6 more)

### Community 80 - "Tool shortlist from the owner (2026-11-05)"
Cohesion: 0.29
Nodes (6): Adopted after owner decision (2026-11-05), For the outreach test (after R1, owner approval), Later (UI and content), Not relevant to this project, Tool shortlist from the owner (2026-11-05), Use now or next (fits the current pipeline)

### Community 81 - "CJClient"
Cohesion: 0.19
Nodes (10): CJClient, CJError, _default_session(), main(), catalogue(), image_rows(), images(), main() (+2 more)

### Community 82 - "snapshot_job.py"
Cohesion: 0.17
Nodes (20): feed_status(), fetch_feed(), job(), _prod_row(), prods(), Resp, rp(), Session (+12 more)

### Community 83 - "27 — Can we pre-filter brands and retailers before fetching a store's feed?"
Cohesion: 0.29
Nodes (6): 27 — Can we pre-filter brands and retailers before fetching a store's feed?, Answer, Pilot results, Untested ideas (hypotheses), What a filter would cost, What we do instead

### Community 84 - "llm.py"
Cohesion: 0.16
Nodes (12): _cache_get(), _cache_put(), is_or_free(), _key(), list_free(), main(), _or_free_take(), paid_allowed() (+4 more)

### Community 85 - "Plan: read a store's hidden supply fingerprints and estimate its source"
Cohesion: 0.20
Nodes (9): Exit criteria, Goal, P0 result (2026-11-05), P1 result (2026-11-05), P2 result (2026-11-05), Phases (small first), Plan: read a store's hidden supply fingerprints and estimate its source, Team and workstreams (+1 more)

### Community 86 - "test_trends_llm.py"
Cohesion: 0.14
Nodes (12): cache_key(), chat(), _extract_text(), _post(), test_chat_without_any_key_fails_clearly(), test_explicit_models_override_the_task_list(), fake_post(), test_only_providers_with_keys_are_tried() (+4 more)

### Community 87 - "25 — Audit of four public Shopify data repos"
Cohesion: 0.40
Nodes (4): 25 — Audit of four public Shopify data repos, Summary, What each one taught us, What we reuse and what we build

### Community 88 - "lake_sync.py"
Cohesion: 0.08
Nodes (37): 0017 — Lake sync to Supabase Storage, autopilot runner and health check, 1. Lake sync client (CLAUDE.md "reuse before build"), 2. Public logs (the repo is public), 3. Daily jobs, heartbeat, health, Known limits, Exists, kind(), local_files() (+29 more)

### Community 89 - "2. Per-niche price bands and representative products"
Cohesion: 0.13
Nodes (14): 13 - Sales: landed-cost ceilings and niche economics, 1. Landed-cost ceiling table [data: scout.margin output], 2. Per-niche price bands and representative products, 3. Ranked summary, 4. Gaps and next steps, auto-detailing-tools, coin-supplies, collectibles-display (+6 more)

### Community 90 - "run_batch"
Cohesion: 0.26
Nodes (8): run_batch(), _read(), test_batch_records_errors_without_stopping(), test_batch_rejects_duplicate_ids(), test_batch_resumes_and_retries_errors(), test_batch_writes_one_result_per_id(), test_chat_cache_hit_skips_the_call(), _write()

### Community 91 - "re"
Cohesion: 0.36
Nodes (4): main(), parse(), sample(), seen()

### Community 93 - "fit_shop_age"
Cohesion: 0.40
Nodes (3): fit_shop_age(), shop_started_by(), test_shop_age_curve_is_monotone_lower_envelope()

### Community 94 - "Best online stores: what they sell and how they get traffic — 2026-11-04"
Cohesion: 0.25
Nodes (7): Best online stores: what they sell and how they get traffic — 2026-11-04, Business model of every screened US store, Categories the best stores win with, Funnel, How they get traffic, Niche shortlist for step 2 (sourcing), Who is moving: rank history of the copyable stores

### Community 95 - "webmeta.py"
Cohesion: 0.08
Nodes (31): homepage_signals(), aggregate_rating(), discover(), dns(), footprint(), is_shopify(), jsonld(), keyword_hits() (+23 more)

### Community 97 - "json"
Cohesion: 0.18
Nodes (9): analyze(), _fetch(), main(), flatten(), main(), write_csv(), main(), parse_cell() (+1 more)

### Community 98 - "min_price"
Cohesion: 0.12
Nodes (12): Commands, Free models: GLM Flash + OpenRouter free lane, How to get good results, Limits (tested), Never, _check(), min_price(), _price_floor() (+4 more)

### Community 99 - "test_shopify_detect.py"
Cohesion: 0.09
Nodes (26): 28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy, Advisor reading (2026-11-04), Caveats `[unverified]`, Implied miss rate, Method, Recommendation, Results `[data]`, is_blocked() (+18 more)

### Community 100 - "Data pipeline: feeding the team authentic evidence"
Cohesion: 0.25
Nodes (7): 1. Architecture, 2. What makes it "authentic", 3. Datasets, 4. How agents use it, 5. Automation, 6. Build order, Data pipeline: feeding the team authentic evidence

### Community 101 - "Autopilot: the store pipeline runs 24/7 on scripts"
Cohesion: 0.25
Nodes (7): Autopilot: the store pipeline runs 24/7 on scripts, Build order, Jobs and cadence, Operating model, Options considered, Rules every scheduled job follows, Where it runs

### Community 102 - "unblock.py"
Cohesion: 0.09
Nodes (32): 0015 — ZenRows and ScrapingBee as a paid fallback tier, How they are used, Owner steps, Scope, What is adopted, _load_dotenv(), _budget_left(), _cost() (+24 more)

### Community 103 - "_shop_hits"
Cohesion: 0.17
Nodes (9): Question, run_ranks(), _shop_hits(), scan(), scan_tranche(), _shop_hit_domains(), tranches_done(), _tranco_list() (+1 more)

### Community 104 - "2. Per-niche price bands and representative products"
Cohesion: 0.10
Nodes (29): Data contract: lead inbox card, Data contract: store card and side panel, Design rules applied, Flow 1: study a store, Flow 2: review a lead (parked idea, design only), Information architecture (all five views, first cut), Next (after owner feedback), Open owner questions from this step (+21 more)

### Community 105 - "cj.py"
Cohesion: 0.14
Nodes (12): 6. Part 2: build the shortlist engine (stage E of `docs/plan/ai-team.md`), _dicts(), _json_list(), normalize_detail(), normalize_freight(), normalize_listing(), normalize_stock(), _num() (+4 more)

### Community 106 - "29. Proof-of-performance pilot (10 Shopify stores)"
Cohesion: 0.20
Nodes (9): 29. Proof-of-performance pilot (10 Shopify stores), Grade counts, Method, Open items, Recommendation for the 300-store sweep, Result in one line, Sources: useful and useless, Terms concerns (+1 more)

### Community 107 - "csv"
Cohesion: 0.23
Nodes (7): load_cache(), main(), parse_verdict(), screen(), url_hash(), test_image_verdict_needs_all_checks_and_marks_clean(), test_screen_skips_failures_and_yields_hash_keyed_rows()

### Community 108 - "pytest"
Cohesion: 0.20
Nodes (17): compute(), _compute_raw(), evaluate(), Inputs, main(), _rounded(), test_duty_reduces_net_one_for_one(), test_hand_calculated_case() (+9 more)

### Community 109 - "0013 — Automating ad and review checks: official routes only"
Cohesion: 0.33
Nodes (5): 0013 — Automating ad and review checks: official routes only, Decision, Owner steps (in order of value per effort), Rule applied, What the official routes give

### Community 110 - "Opportunity (parked): stores that try hard but underperform"
Cohesion: 0.22
Nodes (8): How we would quantify "potential", Open questions for the owner, Opportunity (parked): stores that try hard but underperform, Problems visible from public pages (no checkout, no login), Review of the owner's "Shopify Audit & Competitor Spy SaaS" blueprint (2026-11-05), Rules if this becomes a phase, The idea in one line, What the autopilot keeps now (cheap, and the only action taken)

### Community 111 - "__init__.py"
Cohesion: 0.14
Nodes (13): best_count(), is_blocked(), main(), product_url(), _render(), go(), review_app(), review_counts() (+5 more)

### Community 112 - "30 — Proof of performance for the top 50 candidate stores"
Cohesion: 0.25
Nodes (7): 30 — Proof of performance for the top 50 candidate stores, How the 50 were chosen, Model lesson, Next, Result: independent proof grade, Sources that worked and failed, What this tells us

### Community 113 - "31 — What the top-performing Shopify stores have in common"
Cohesion: 0.29
Nodes (6): 31 — What the top-performing Shopify stores have in common, Gaps, Patterns, What a small zero-inventory store can borrow, What needs scale or rights (do not plan on it), Who they are

### Community 114 - "test_autopilot_discovery.py"
Cohesion: 0.15
Nodes (11): _last_new_run(), new_entries(), scan_new(), FakeList, lake(), _lists(), _resolver(), test_new_entries_are_the_diff_best_rank_first() (+3 more)

### Community 115 - "0014 — Crawl4AI for review counts on store pages"
Cohesion: 0.33
Nodes (5): 0014 — Crawl4AI for review counts on store pages, Candidates, Pilot (small first), Scope: what Crawl4AI may and may not fetch, Settings that keep us inside our rules

### Community 116 - "33a Fingerprints: AliExpress import and fulfilment apps (Shopify)"
Cohesion: 0.40
Nodes (4): 33a Fingerprints: AliExpress import and fulfilment apps (Shopify), Fingerprint table, Method and gaps, Sources

### Community 117 - "glm-worker.md"
Cohesion: 0.50
Nodes (3): How you work, Report (short), Rules

### Community 118 - "test_trends_llm.py"
Cohesion: 0.13
Nodes (14): _inline_images(), _read_image(), _isolated_free_usage(), no_keys(), _reply(), test_all_empty_replies_raise(), test_data_urls_are_left_alone(), test_empty_or_malformed_replies_fall_through_to_the_next_model() (+6 more)

### Community 119 - "0006 — DuckDB warehouse: deterministic core, LLM on top"
Cohesion: 0.25
Nodes (7): 0006 — DuckDB warehouse: deterministic core, LLM on top, Choice, Intelligence layer (next), Layers, Out of scope for this slice, Rules that make it deterministic, Why now

### Community 120 - "Findings"
Cohesion: 0.29
Nodes (6): Findings, Independent project review — 2026-11-03, Primary-source verification, retrieved 2026-11-03, Questions for the review pull request, Top 10 actions, Validation and limits

### Community 121 - "33c. Supply fingerprints: print-on-demand apps, themes and marketing kits, tracking apps and carriers"
Cohesion: 0.40
Nodes (4): 33c. Supply fingerprints: print-on-demand apps, themes and marketing kits, tracking apps and carriers, Notes, Sources, Table: traces by tool or carrier

### Community 122 - "or_free_used"
Cohesion: 0.47
Nodes (5): or_free_used(), _ok_post(), test_chat_many_spread_sends_a_share_to_openrouter_free(), test_glm_calls_do_not_use_the_openrouter_allowance(), test_openrouter_free_calls_are_counted_and_capped()

### Community 123 - "33b. Supply fingerprints: US/EU suppliers, dropship apps and 3PL apps"
Cohesion: 0.50
Nodes (3): 33b. Supply fingerprints: US/EU suppliers, dropship apps and 3PL apps, Sources, Table: traces by app

### Community 124 - "test_autopilot.py"
Cohesion: 0.15
Nodes (9): lake(), _ok_runner(), run(), _rows(), test_a_leaky_job_does_not_reach_the_public_log(), test_a_rerun_the_same_day_resumes_at_the_failed_job(), test_daily_runs_in_order_counts_rows_and_captures_output(), test_dry_run_runs_nothing() (+1 more)

### Community 125 - "second_opinion"
Cohesion: 0.25
Nodes (5): LLMError, second_opinion(), test_second_opinion_agreement(), test_second_opinion_disagreement_and_failure(), boom()

### Community 127 - "UI/UX brief (design phase, no production build yet)"
Cohesion: 0.25
Nodes (7): Deliverables of the design session, Out of scope, Principles, Progress, UI/UX brief (design phase, no production build yet), Views to design, Who uses it

### Community 128 - "autopilot.py"
Cohesion: 0.28
Nodes (10): daily(), main(), _now(), _read_json(), _run_ids(), run_job(), _safe_token(), _tail_to() (+2 more)

### Community 129 - "sys"
Cohesion: 0.18
Nodes (7): diff_runs(), _intkeys(), main(), review_app(), review_sample(), _runs_by_date(), snapshot_store()

### Community 130 - "Session state: where the project stands"
Cohesion: 0.22
Nodes (8): Facts that change plans, History, Next, in order, Owner decisions open, Repo, Session state: where the project stands, Traps in a fresh container, Where we are (2026-11-05)

### Community 131 - "steps"
Cohesion: 0.21
Nodes (12): steps, steps, continue-on-error, id, if, name, run, uses (+4 more)

### Community 132 - "0016 — Autopilot runs on GitHub Actions; storage on Supabase (free tier)"
Cohesion: 0.40
Nodes (4): 0016 — Autopilot runs on GitHub Actions; storage on Supabase (free tier), Owner steps, Scheduler: GitHub Actions (decided), Storage: Supabase free tier (recommended, owner to create the account)

### Community 133 - "stores.py"
Cohesion: 0.11
Nodes (22): classify_product(), _deep_one(), _light_one(), load_rules(), main(), _meta_one(), meta_summary(), _new_first() (+14 more)

### Community 134 - "quiet.py"
Cohesion: 0.20
Nodes (6): LeakError, line(), _ok(), test_entry_points_print_only_through_say(), test_say_accepts_counts_and_tokens(), test_say_refuses_anything_that_could_name_a_store()

### Community 135 - "datetime"
Cohesion: 0.24
Nodes (7): drift(), health(), _week_rates(), _heartbeat(), test_error_rate_above_ten_percent_alerts(), test_healthy_heartbeat_has_no_alerts(), test_missing_heartbeat_and_stale_jobs_alert()

### Community 136 - "mode"
Cohesion: 0.18
Nodes (11): mode, default, description, options, required, type, on, schedule (+3 more)

### Community 137 - "test_warehouse_helpers.py"
Cohesion: 0.22
Nodes (5): flatten_categories(), FakeCJ, test_flatten_categories_keeps_three_levels(), test_offers_lands_variants_stock_and_freight_for_cheapest_variant(), test_parse_labels_keeps_only_valid_entries()

### Community 138 - "autopilot.yml"
Cohesion: 0.22
Nodes (8): env, PYTHONUNBUFFERED, SCOUT_ALLOW_PAID, SCOUT_CRAWL_STEALTH, jobs, name, permissions, contents

### Community 139 - "Brief for the second agent: independent review, then build the shortlist engine"
Cohesion: 0.25
Nodes (7): 1. Project in four lines, 2. Read first (in this order, about 30 minutes), 3. Ground rules (from `CLAUDE.md`, restated because they matter most), 4. How to work, 5. Part 1: independent review (DONE, merged as PR #1; read `docs/reviews/2026-11-agent2-project-review.md`), 7. When you finish, Brief for the second agent: independent review, then build the shortlist engine

### Community 140 - "health"
Cohesion: 0.29
Nodes (8): cancel-in-progress, group, concurrency, concurrency, if, runs-on, timeout-minutes, health

### Community 141 - "cj_sweep.py"
Cohesion: 0.32
Nodes (4): private_path(), main(), sweep(), test_raw_output_must_stay_under_data_private()

### Community 143 - "env"
Cohesion: 0.40
Nodes (6): env, OPENROUTER_API_KEY, SUPABASE_SERVICE_KEY, SUPABASE_URL, ZAI_API_KEY, env

### Community 144 - "_checked_path"
Cohesion: 0.33
Nodes (3): _added(), _fingerprint_signal_rows(), _checked_path()

### Community 145 - "fingerprint_host"
Cohesion: 0.40
Nodes (3): fingerprint_host(), one(), _merge_page()

### Community 148 - "daily"
Cohesion: 0.50
Nodes (4): if, runs-on, timeout-minutes, daily

## Knowledge Gaps
- **6 isolated node(s):** `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `API_TIMEOUT_MS`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1031 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `record_run()` connect `record_run` to `autopilot.py`, `json`, `min_price`, `Data pipeline: feeding the team authentic evidence`, `Autopilot: the store pipeline runs 24/7 on scripts`, `stores.py`, `_shop_hits`, `pathlib`, `argparse`, `__init__.py`, `CJClient`, `test_autopilot_discovery.py`, `Shared rules for every AI team member`, `test_autopilot.py`, `webmeta.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `record_run()` (e.g. with `Shared rules for every AI team member` and `How to get good results`) actually correct?**
  _`record_run()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `API_TIMEOUT_MS` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `hooks` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `evaluate()` connect `pytest` to `2. Per-niche price bands and representative products`, `cj.py`, `min_price`, `Findings`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `chat()` (e.g. with `main()` and `main()`) actually correct?**
  _`chat()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.13666666666666666 - nodes in this community are weakly interconnected._