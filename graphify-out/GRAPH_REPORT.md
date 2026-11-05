# Graph Report - drop-shipping-  (2026-11-05)

## Corpus Check
- 181 files · ~150,382 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .csv 15, (none) 4, .example 1)

## Summary
- 1683 nodes · 2761 edges · 135 communities (115 shown, 20 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a7e797f`
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
- jsonld
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
- classify.py
- 20 — Source pilots: what each source actually discovered
- 22. Shopify store benchmarks for estimating revenue from traffic
- store_intel.py
- 0007 — Deterministic harness first, intelligence layer on top
- 32c. Trustpilot and Google Ads Transparency: legal automation routes
- __init__.py
- test_cj.py
- 32a. Meta Ad Library API: official route for brand ad monitoring
- 0009 — Step 1: find the best online stores and reconstruct what they do
- Step 1 flow: how we find the best online stores and what they do
- Plan: find top-performing Shopify stores to take inspiration from
- Estimating sales and profit: how we think about it
- 26. Calibration set widening: Shopify-hosted stores that publish revenue
- test_snapshots.py
- stores.py
- Tool shortlist from the owner (2026-11-05)
- argparse
- snapshot_job.py
- 27 — Can we pre-filter brands and retailers before fetching a store's feed?
- llm.py
- Plan: read a store's hidden supply fingerprints and estimate its source
- test_trends_llm.py
- 25 — Audit of four public Shopify data repos
- __init__.py
- test_stores.py
- run_batch
- argparse
- 0012-temporal-storage.md
- fit_shop_age
- Best online stores: what they sell and how they get traffic — 2026-11-04
- webmeta.py
- __init__.py
- json
- fixture
- test_shopify_detect.py
- Data pipeline: feeding the team authentic evidence
- Autopilot: the store pipeline runs 24/7 on scripts
- min_price
- 29. Proof-of-performance pilot (10 Shopify stores)
- csv
- Inputs
- 0013 — Automating ad and review checks: official routes only
- Opportunity (parked): stores that try hard but underperform
- summarize_feed
- 30 — Proof of performance for the top 50 candidate stores
- 31 — What the top-performing Shopify stores have in common
- 0014 — Crawl4AI for review counts on store pages
- 33a Fingerprints: AliExpress import and fulfilment apps (Shopify)
- glm-worker.md
- time
- 2. Per-niche price bands and representative products
- store_export.py
- 33c. Supply fingerprints: print-on-demand apps, themes and marketing kits, tracking apps and carriers
- 28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy
- 33b. Supply fingerprints: US/EU suppliers, dropship apps and 3PL apps
- latest_good
- second_opinion
- Findings
- failing_open
- margin.py
- test_webmeta.py
- Session state: where the project stands
- products
- deep_targets
- keyword_hits
- meta_summary

## God Nodes (most connected - your core abstractions)
1. `record_run()` - 43 edges
2. `chat()` - 42 edges
3. `column_types` - 24 edges
4. `Inputs` - 21 edges
5. `CJClient` - 21 edges
6. `feed_signals()` - 21 edges
7. `rebuild()` - 19 edges
8. `compact()` - 18 edges
9. `evaluate()` - 16 edges
10. `supply_estimate()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Method` --references--> `_shop_hits()`  [INFERRED]
  docs/research/28-discovery-miss-rate.md → scout/stores.py
- `1. Landed-cost ceiling table [data: scout.margin output]` --references--> `evaluate()`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py
- `How to get good results` --references--> `record_run()`  [INFERRED]
  .claude/skills/free-llm/SKILL.md → scout/store.py
- `Rules every scheduled job follows` --references--> `record_run()`  [INFERRED]
  docs/plan/autopilot.md → scout/store.py
- `What "best" means here` --references--> `business_model()`  [INFERRED]
  docs/decisions/0009-best-store-discovery.md → scout/stores.py

## Import Cycles
- None detected.

## Communities (135 total, 20 thin omitted)

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
Nodes (19): Shared rules for every AI team member, 2. What makes it "authentic", _checked_path(), main(), query(), rebuild(), record_run(), _runs() (+11 more)

### Community 23 - "steps"
Cohesion: 0.08
Nodes (23): concurrency, cancel-in-progress, group, SKIP, jobs, test, name, on (+15 more)

### Community 25 - "3. Candidate cards"
Cohesion: 0.10
Nodes (19): 0001 — Candidate niches (Stage B), 1. Decision, 2. Evidence table, 2a. Margin constraint behind the price targets, 2b. Rubric scores (`docs/plan/ai-team.md` §5), 2c. Sources for the shared premises, 3.1 `tcg-supplies`: trading-card storage and display, 3.2 `hobby-modeling-tools`: miniature and scale-model tools (+11 more)

### Community 26 - "jsonld"
Cohesion: 0.50
Nodes (3): aggregate_rating(), jsonld(), test_jsonld_same_as_and_rating()

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
Cohesion: 0.06
Nodes (48): _clamp(), _country(), feed_signals(), fingerprint_host(), fingerprint_many(), one(), main(), _merge_page() (+40 more)

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

### Community 63 - "classify.py"
Cohesion: 0.09
Nodes (23): 0006 — DuckDB warehouse: deterministic core, LLM on top, Choice, Intelligence layer (next), Layers, Out of scope for this slice, Rules that make it deterministic, Why now, _append() (+15 more)

### Community 64 - "20 — Source pilots: what each source actually discovered"
Cohesion: 0.33
Nodes (5): 20 — Source pilots: what each source actually discovered, Fixes for the next round, Manual steps that remain valuable (owner, about 20–30 minutes each), Scorecard, What worked, what didn't

### Community 65 - "22. Shopify store benchmarks for estimating revenue from traffic"
Cohesion: 0.14
Nodes (13): 1. Conversion rate (Shopify), 22. Shopify store benchmarks for estimating revenue from traffic, 2. Average order value (AOV), 3. Units per order, 4. Traffic channel mix (paid vs organic vs email), 5. Ad spend share of revenue (blended CAC / MER), 6. Return rates by category, How we would use these (+5 more)

### Community 66 - "store_intel.py"
Cohesion: 0.16
Nodes (20): _numbers(), append_cache(), _clean(), gaps(), grounded(), walk(), load_cache(), _ls() (+12 more)

### Community 67 - "0007 — Deterministic harness first, intelligence layer on top"
Cohesion: 0.33
Nodes (5): 0007 — Deterministic harness first, intelligence layer on top, How to run, New in this decision, Open: where history lives, The split

### Community 68 - "32c. Trustpilot and Google Ads Transparency: legal automation routes"
Cohesion: 0.13
Nodes (14): 32c. Trustpilot and Google Ads Transparency: legal automation routes, Express permission, Gaps, Notes on the public Business Units API, Part 1: Trustpilot, Part 2: Google Ads Transparency, Pilot status, Recommendation (Google) (+6 more)

### Community 69 - "__init__.py"
Cohesion: 0.12
Nodes (19): dropship_confidence(), extract_policy_signals(), _fetch_policies_async(), main(), PolicySignals, profile_many(), one(), run() (+11 more)

### Community 70 - "test_cj.py"
Cohesion: 0.15
Nodes (16): client(), FakeResp, FakeSession, test_a_non_json_response_is_a_clear_error(), test_a_second_auth_failure_is_not_retried_forever(), test_detail_ignores_junk_variants_and_images(), test_detail_normalizes_images_and_variants(), test_detail_parses_live_string_numbers_and_json_list_fields() (+8 more)

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

### Community 79 - "stores.py"
Cohesion: 0.18
Nodes (14): classify_product(), _deep_one(), _light_one(), load_rules(), main(), _meta_one(), _parallel(), _quantile() (+6 more)

### Community 80 - "Tool shortlist from the owner (2026-11-05)"
Cohesion: 0.29
Nodes (6): For the outreach test (after R1, owner approval), Held back, with the reason, Later (UI and content), Not relevant to this project, Tool shortlist from the owner (2026-11-05), Use now or next (fits the current pipeline)

### Community 81 - "argparse"
Cohesion: 0.07
Nodes (31): 1. Project in four lines, 2. Read first (in this order, about 30 minutes), 3. Ground rules (from `CLAUDE.md`, restated because they matter most), 4. How to work, 5. Part 1: independent review (DONE, merged as PR #1; read `docs/reviews/2026-11-agent2-project-review.md`), 6. Part 2: build the shortlist engine (stage E of `docs/plan/ai-team.md`), 7. When you finish, Brief for the second agent: independent review, then build the shortlist engine (+23 more)

### Community 82 - "snapshot_job.py"
Cohesion: 0.09
Nodes (30): diff_runs(), feed_status(), fetch_feed(), _intkeys(), main(), review_app(), review_sample(), run() (+22 more)

### Community 83 - "27 — Can we pre-filter brands and retailers before fetching a store's feed?"
Cohesion: 0.29
Nodes (6): 27 — Can we pre-filter brands and retailers before fetching a store's feed?, Answer, Pilot results, Untested ideas (hypotheses), What a filter would cost, What we do instead

### Community 84 - "llm.py"
Cohesion: 0.10
Nodes (19): _cache_get(), cache_key(), _cache_put(), chat(), _extract_text(), is_or_free(), _key(), list_free() (+11 more)

### Community 85 - "Plan: read a store's hidden supply fingerprints and estimate its source"
Cohesion: 0.22
Nodes (8): Exit criteria, Goal, P0 result (2026-11-05), P1 result (2026-11-05), Phases (small first), Plan: read a store's hidden supply fingerprints and estimate its source, Team and workstreams, The traces a store leaves (indicator catalogue, first draft)

### Community 86 - "test_trends_llm.py"
Cohesion: 0.10
Nodes (20): _inline_images(), _read_image(), _reply(), test_all_empty_replies_raise(), test_data_urls_are_left_alone(), test_empty_or_malformed_replies_fall_through_to_the_next_model(), test_empty_series_reports_no_data(), test_explicit_models_override_the_task_list() (+12 more)

### Community 87 - "25 — Audit of four public Shopify data repos"
Cohesion: 0.40
Nodes (4): 25 — Audit of four public Shopify data repos, Summary, What each one taught us, What we reuse and what we build

### Community 88 - "__init__.py"
Cohesion: 0.15
Nodes (14): best_count(), is_blocked(), main(), product_url(), _render(), go(), review_app(), review_counts() (+6 more)

### Community 89 - "test_stores.py"
Cohesion: 0.22
Nodes (12): business_model(), category_spread(), homepage_signals(), _m(), test_app_developer_with_dropship_code_is_not_a_dropshipper(), test_business_model_rules(), test_dominant_vendor_or_few_labels_means_brand(), test_general_store_pattern_is_separate_from_brand() (+4 more)

### Community 90 - "run_batch"
Cohesion: 0.33
Nodes (7): run_batch(), _read(), test_batch_records_errors_without_stopping(), test_batch_rejects_duplicate_ids(), test_batch_resumes_and_retries_errors(), test_batch_writes_one_result_per_id(), _write()

### Community 91 - "argparse"
Cohesion: 0.16
Nodes (8): main(), sweep(), git_ident(), main(), main(), parse(), sample(), seen()

### Community 93 - "fit_shop_age"
Cohesion: 0.40
Nodes (3): fit_shop_age(), shop_started_by(), test_shop_age_curve_is_monotone_lower_envelope()

### Community 94 - "Best online stores: what they sell and how they get traffic — 2026-11-04"
Cohesion: 0.25
Nodes (7): Best online stores: what they sell and how they get traffic — 2026-11-04, Business model of every screened US store, Categories the best stores win with, Funnel, How they get traffic, Niche shortlist for step 2 (sourcing), Who is moving: rank history of the copyable stores

### Community 95 - "webmeta.py"
Cohesion: 0.23
Nodes (7): discover(), dns(), is_shopify(), _tranco_list(), txt_signals(), test_shopify_detection_by_ip_range_or_cname(), test_txt_signals_reveal_platforms()

### Community 96 - "__init__.py"
Cohesion: 0.27
Nodes (3): med(), main(), median()

### Community 97 - "json"
Cohesion: 0.27
Nodes (6): _git_sha(), flatten(), main(), write_csv(), main(), parse_cell()

### Community 98 - "fixture"
Cohesion: 0.25
Nodes (4): _no_llm_cache(), lake(), _isolated_free_usage(), no_keys()

### Community 99 - "test_shopify_detect.py"
Cohesion: 0.11
Nodes (19): is_blocked(), is_shopify(), probe(), _robots_allows(), shopify_evidence(), _Resp, _Sess, test_blocked() (+11 more)

### Community 100 - "Data pipeline: feeding the team authentic evidence"
Cohesion: 0.29
Nodes (6): 1. Architecture, 3. Datasets, 4. How agents use it, 5. Automation, 6. Build order, Data pipeline: feeding the team authentic evidence

### Community 101 - "Autopilot: the store pipeline runs 24/7 on scripts"
Cohesion: 0.29
Nodes (6): Autopilot: the store pipeline runs 24/7 on scripts, Build order, Jobs and cadence, Operating model, Rules every scheduled job follows, Where it runs (owner decision needed)

### Community 102 - "min_price"
Cohesion: 0.15
Nodes (11): Commands, Free models: GLM Flash + OpenRouter free lane, How to get good results, Limits (tested), Never, min_price(), _price_floor(), test_min_price_matches_the_documented_ceilings() (+3 more)

### Community 106 - "29. Proof-of-performance pilot (10 Shopify stores)"
Cohesion: 0.20
Nodes (9): 29. Proof-of-performance pilot (10 Shopify stores), Grade counts, Method, Open items, Recommendation for the 300-store sweep, Result in one line, Sources: useful and useless, Terms concerns (+1 more)

### Community 107 - "csv"
Cohesion: 0.19
Nodes (9): load_cache(), main(), parse_verdict(), screen(), url_hash(), analyze(), _fetch(), main() (+1 more)

### Community 108 - "Inputs"
Cohesion: 0.30
Nodes (12): compute(), Inputs, test_duty_reduces_net_one_for_one(), test_hand_calculated_case(), test_higher_cost_lowers_net(), test_impossible_inputs_are_rejected(), test_min_price_is_the_lowest_passing_price(), test_net_is_contribution_minus_reserves() (+4 more)

### Community 109 - "0013 — Automating ad and review checks: official routes only"
Cohesion: 0.33
Nodes (5): 0013 — Automating ad and review checks: official routes only, Decision, Owner steps (in order of value per effort), Rule applied, What the official routes give

### Community 110 - "Opportunity (parked): stores that try hard but underperform"
Cohesion: 0.22
Nodes (8): How we would quantify "potential", Open questions for the owner, Opportunity (parked): stores that try hard but underperform, Problems visible from public pages (no checkout, no login), Review of the owner's "Shopify Audit & Competitor Spy SaaS" blueprint (2026-11-05), Rules if this becomes a phase, The idea in one line, What the autopilot keeps now (cheap, and the only action taken)

### Community 111 - "summarize_feed"
Cohesion: 0.15
Nodes (14): dropship_traces(), _norm(), product_category(), _product_text(), summarize_feed(), vendor_is_shop(), _p(), test_added_categories() (+6 more)

### Community 112 - "30 — Proof of performance for the top 50 candidate stores"
Cohesion: 0.25
Nodes (7): 30 — Proof of performance for the top 50 candidate stores, How the 50 were chosen, Model lesson, Next, Result: independent proof grade, Sources that worked and failed, What this tells us

### Community 113 - "31 — What the top-performing Shopify stores have in common"
Cohesion: 0.29
Nodes (6): 31 — What the top-performing Shopify stores have in common, Gaps, Patterns, What a small zero-inventory store can borrow, What needs scale or rights (do not plan on it), Who they are

### Community 115 - "0014 — Crawl4AI for review counts on store pages"
Cohesion: 0.33
Nodes (5): 0014 — Crawl4AI for review counts on store pages, Candidates, Pilot (small first), Scope: what Crawl4AI may and may not fetch, Settings that keep us inside our rules

### Community 116 - "33a Fingerprints: AliExpress import and fulfilment apps (Shopify)"
Cohesion: 0.40
Nodes (4): 33a Fingerprints: AliExpress import and fulfilment apps (Shopify), Fingerprint table, Method and gaps, Sources

### Community 117 - "glm-worker.md"
Cohesion: 0.50
Nodes (3): How you work, Report (short), Rules

### Community 118 - "time"
Cohesion: 0.47
Nodes (5): or_free_used(), _ok_post(), test_chat_many_spread_sends_a_share_to_openrouter_free(), test_glm_calls_do_not_use_the_openrouter_allowance(), test_openrouter_free_calls_are_counted_and_capped()

### Community 119 - "2. Per-niche price bands and representative products"
Cohesion: 0.13
Nodes (14): 13 - Sales: landed-cost ceilings and niche economics, 1. Landed-cost ceiling table [data: scout.margin output], 2. Per-niche price bands and representative products, 3. Ranked summary, 4. Gaps and next steps, auto-detailing-tools, coin-supplies, collectibles-display (+6 more)

### Community 120 - "store_export.py"
Cohesion: 0.18
Nodes (5): main(), niche_score(), rows(), table(), main()

### Community 121 - "33c. Supply fingerprints: print-on-demand apps, themes and marketing kits, tracking apps and carriers"
Cohesion: 0.40
Nodes (4): 33c. Supply fingerprints: print-on-demand apps, themes and marketing kits, tracking apps and carriers, Notes, Sources, Table: traces by tool or carrier

### Community 122 - "28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy"
Cohesion: 0.18
Nodes (11): Update: phase Niche Finder R1 (2026-11-04, later), 28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy, Advisor reading (2026-11-04), Caveats `[unverified]`, Implied miss rate, Method, Question, Recommendation (+3 more)

### Community 123 - "33b. Supply fingerprints: US/EU suppliers, dropship apps and 3PL apps"
Cohesion: 0.50
Nodes (3): 33b. Supply fingerprints: US/EU suppliers, dropship apps and 3PL apps, Sources, Table: traces by app

### Community 124 - "latest_good"
Cohesion: 0.20
Nodes (8): Business-model rules: validation record (R1 exit criterion), Error classes (carry into the rules and the report), Pipeline bugs found by testing small, Result and the change made, Rounds, latest_good(), relabel(), test_failed_refresh_never_replaces_a_good_profile()

### Community 125 - "second_opinion"
Cohesion: 0.25
Nodes (5): LLMError, second_opinion(), test_second_opinion_agreement(), test_second_opinion_disagreement_and_failure(), boom()

### Community 126 - "Findings"
Cohesion: 0.29
Nodes (6): Findings, Independent project review — 2026-11-03, Primary-source verification, retrieved 2026-11-03, Questions for the review pull request, Top 10 actions, Validation and limits

### Community 128 - "margin.py"
Cohesion: 0.27
Nodes (6): _check(), _compute_raw(), evaluate(), main(), _rounded(), test_pass_decision_uses_unrounded_margins()

### Community 129 - "test_webmeta.py"
Cohesion: 0.15
Nodes (10): parse_sitemap(), social_links(), summarize_products(), traffic_tags(), test_web_pixel_settings_identify_platforms(), test_bad_xml_is_empty_not_a_crash(), test_parse_sitemap_index_and_urlset(), test_social_links_skip_share_buttons() (+2 more)

### Community 130 - "Session state: where the project stands"
Cohesion: 0.22
Nodes (8): Facts that change plans, Owner tasks outstanding, Repo, Review panel result (2026-11-04) — read before starting, Session state: where the project stands, Traps in a fresh container, Update: data vault and approved re-scope (2026-11-04, late), What exists

### Community 131 - "products"
Cohesion: 0.39
Nodes (8): Next tasks, in order (focus from 2026-11-04: reconstruct and recreate store success), footprint(), _latest(), main(), products(), resolve_a(), _session(), sitemaps()

### Community 132 - "deep_targets"
Cohesion: 0.29
Nodes (4): deep_targets(), _done(), us_store(), test_us_store_needs_dollars_and_us_reach()

## Knowledge Gaps
- **6 isolated node(s):** `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 905 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `record_run()` connect `record_run` to `__init__.py`, `json`, `products`, `__init__.py`, `Autopilot: the store pipeline runs 24/7 on scripts`, `min_price`, `test_fingerprints.py`, `csv`, `stores.py`, `argparse`, `snapshot_job.py`, `__init__.py`, `28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy`, `latest_good`, `webmeta.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `record_run()` (e.g. with `Shared rules for every AI team member` and `How to get good results`) actually correct?**
  _`record_run()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `hooks` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `6. Part 2: build the shortlist engine (stage E of `docs/plan/ai-team.md`)` connect `argparse` to `margin.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `chat()` (e.g. with `main()` and `main()`) actually correct?**
  _`chat()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.13666666666666666 - nodes in this community are weakly interconnected._