# Graph Report - drop-shipping-  (2026-11-04)

## Corpus Check
- 60 files · ~51,885 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: .csv 6, (none) 4, .example 1)

## Summary
- 604 nodes · 773 edges · 51 communities (42 shown, 9 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `909b258a`
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
- llm.py
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
- store.py
- steps
- 3. Candidate cards
- 2. Per-niche price bands and representative products
- 12 — Compliance risk cards for the 8 candidate niches
- 3. Primary niche: `tcg-supplies`
- Warehouse design: Postgres as the source of truth
- Multichannel plan: one pipeline, eBay + Shopify/Instagram
- claude-glm.sh
- db
- CJClient
- glm-coder.md
- 0003 — Build vs reuse: workflow, data loading, connectors, LLM routing
- data-engineer.md
- 0004 — Postgres warehouse, hosting, and what the source terms allow
- 15 — Postgres hosting, GitHub Actions limits, warehouse tooling
- 16 — Trend and demand sources (US): what we can legitimately ingest
- 17 — Free feeds, and what each API lets us store
- Runbook: Postgres on a VPS, reached by CI through an SSH tunnel
- Data pipeline: feeding the team authentic evidence
- Runbook: Terapeak research session (manual, about 90 minutes)
- test_cj.py
- aggregate_candidates.py
- 18 — CJ Dropshipping API cheat sheet
- 0005-cj-client.md
- Independent project review — 2026-11-03
- 2. Per-niche price bands and representative products
- Session state: where the project stands

## God Nodes (most connected - your core abstractions)
1. `record_run()` - 21 edges
2. `rebuild()` - 19 edges
3. `Inputs` - 18 edges
4. `chat()` - 15 edges
5. `evaluate()` - 14 edges
6. `Warehouse design: Postgres as the source of truth` - 13 edges
7. `12 — Compliance risk cards for the 8 candidate niches` - 13 edges
8. `Runbook: Postgres on a VPS, reached by CI through an SSH tunnel` - 13 edges
9. `compute()` - 12 edges
10. `db` - 11 edges

## Surprising Connections (you probably didn't know these)
- `1. Landed-cost ceiling table [data: scout.margin output]` --references--> `evaluate()`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py
- `Findings` --references--> `_inline_images()`  [INFERRED]
  docs/reviews/2026-11-agent2-project-review.md → scout/llm.py
- `2. Per-niche price bands and representative products` --references--> `Inputs`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py
- `6. Part 2: build the shortlist engine (stage E of `docs/plan/ai-team.md`)` --references--> `evaluate()`  [INFERRED]
  docs/handoff/agent2-review-and-shortlist.md → scout/margin.py
- `2. Per-niche price bands and representative products` --references--> `evaluate()`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py

## Import Cycles
- None detected.

## Communities (51 total, 9 thin omitted)

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
Cohesion: 0.29
Nodes (5): Commands, Context: graphify knowledge graph, graphify, Hard rules, Project

### Community 8 - "llm.py"
Cohesion: 0.07
Nodes (29): chat(), _extract_text(), _inline_images(), _key(), list_free(), LLMError, _load_dotenv(), main() (+21 more)

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

### Community 22 - "store.py"
Cohesion: 0.11
Nodes (21): Shared rules for every AI team member, 2. What makes it "authentic", _checked_path(), _git_sha(), main(), query(), rebuild(), record_run() (+13 more)

### Community 23 - "steps"
Cohesion: 0.08
Nodes (23): concurrency, cancel-in-progress, group, SKIP, jobs, test, name, on (+15 more)

### Community 25 - "3. Candidate cards"
Cohesion: 0.10
Nodes (19): 0001 — Candidate niches (Stage B), 1. Decision, 2. Evidence table, 2a. Margin constraint behind the price targets, 2b. Rubric scores (`docs/plan/ai-team.md` §5), 2c. Sources for the shared premises, 3.1 `tcg-supplies`: trading-card storage and display, 3.2 `hobby-modeling-tools`: miniature and scale-model tools (+11 more)

### Community 26 - "2. Per-niche price bands and representative products"
Cohesion: 0.17
Nodes (18): Findings, _check(), compute(), _compute_raw(), evaluate(), Inputs, main(), _rounded() (+10 more)

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

### Community 33 - "CJClient"
Cohesion: 0.11
Nodes (16): 1. Project in four lines, 2. Read first (in this order, about 30 minutes), 3. Ground rules (from `CLAUDE.md`, restated because they matter most), 4. How to work, 5. Part 1: independent review (DONE, merged as PR #1; read `docs/reviews/2026-11-agent2-project-review.md`), 6. Part 2: build the shortlist engine (stage E of `docs/plan/ai-team.md`), 7. When you finish, Brief for the second agent: independent review, then build the shortlist engine (+8 more)

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

### Community 42 - "Data pipeline: feeding the team authentic evidence"
Cohesion: 0.29
Nodes (6): 1. Architecture, 3. Datasets, 4. How agents use it, 5. Automation, 6. Build order, Data pipeline: feeding the team authentic evidence

### Community 43 - "Runbook: Terapeak research session (manual, about 90 minutes)"
Cohesion: 0.29
Nodes (6): For each product type, Rules, Runbook: Terapeak research session (manual, about 90 minutes), What I do with it, What you need, Which products

### Community 44 - "test_cj.py"
Cohesion: 0.08
Nodes (18): parse_price(), private_path(), git_ident(), main(), client(), FakeResp, FakeSession, test_a_non_json_response_is_a_clear_error() (+10 more)

### Community 46 - "18 — CJ Dropshipping API cheat sheet"
Cohesion: 0.22
Nodes (8): 18 — CJ Dropshipping API cheat sheet, Endpoints, Limits and errors, Minimal call sequence, Official MCP server, Sources, Terms, Unknowns that need a live key

### Community 48 - "Independent project review — 2026-11-03"
Cohesion: 0.33
Nodes (5): Independent project review — 2026-11-03, Primary-source verification, retrieved 2026-11-03, Questions for the review pull request, Top 10 actions, Validation and limits

### Community 49 - "2. Per-niche price bands and representative products"
Cohesion: 0.13
Nodes (14): 13 - Sales: landed-cost ceilings and niche economics, 1. Landed-cost ceiling table [data: scout.margin output], 2. Per-niche price bands and representative products, 3. Ranked summary, 4. Gaps and next steps, auto-detailing-tools, coin-supplies, collectibles-display (+6 more)

### Community 50 - "Session state: where the project stands"
Cohesion: 0.25
Nodes (7): Facts that change plans, Next tasks, in order, Owner tasks outstanding, Repo, Session state: where the project stands, Traps in a fresh container, What exists

## Knowledge Gaps
- **6 isolated node(s):** `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `API_TIMEOUT_MS`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 399 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `evaluate()` connect `2. Per-niche price bands and representative products` to `CJClient`, `2. Per-niche price bands and representative products`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `record_run()` (e.g. with `Shared rules for every AI team member` and `2. What makes it "authentic"`) actually correct?**
  _`record_run()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `API_TIMEOUT_MS` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `hooks` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `Findings` connect `2. Per-niche price bands and representative products` to `llm.py`, `Independent project review — 2026-11-03`, `store.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `rebuild()` (e.g. with `2. What makes it "authentic"` and `Findings`) actually correct?**
  _`rebuild()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06578947368421052 - nodes in this community are weakly interconnected._