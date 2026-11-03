# Graph Report - drop-shipping-  (2026-11-03)

## Corpus Check
- 33 files · ~26,366 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: .csv 4, (none) 3, .example 1)

## Summary
- 259 nodes · 267 edges · 30 communities (20 shown, 10 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6d46f430`
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
- _team-rules.md
- 3. Candidate cards
- 2. Per-niche price bands and representative products
- 12 — Compliance risk cards for the 8 candidate niches
- aggregate_candidates.py
- check_no_ai_attribution.py

## God Nodes (most connected - your core abstractions)
1. `12 — Compliance risk cards for the 8 candidate niches` - 13 edges
2. `2. Per-niche price bands and representative products` - 11 edges
3. `02 — Unit economics, success rates, saturation, tariffs` - 10 edges
4. `hooks` - 9 edges
5. `11 - Google Trends check of Stage B candidates (US)` - 9 edges
6. `3. Candidate cards` - 9 edges
7. `00 — Research summary and PoC plan` - 8 edges
8. `06 — Image sourcing under zero inventory` - 8 edges
9. `01 — eBay dropshipping policy, enforcement, fees` - 8 edges
10. `0001 — Candidate niches (Stage B)` - 8 edges

## Surprising Connections (you probably didn't know these)
- `1. Landed-cost ceiling table [data: scout.margin output]` --references--> `evaluate()`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py
- `2. Per-niche price bands and representative products` --references--> `Inputs`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py
- `2. Per-niche price bands and representative products` --references--> `evaluate()`  [INFERRED]
  docs/research/13-sales-niche-economics.md → scout/margin.py

## Import Cycles
- None detected.

## Communities (30 total, 10 thin omitted)

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
Cohesion: 0.12
Nodes (12): chat(), list_free(), LLMError, main(), _post(), compute(), evaluate(), Inputs (+4 more)

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

### Community 25 - "3. Candidate cards"
Cohesion: 0.10
Nodes (19): 0001 — Candidate niches (Stage B), 1. Decision, 2. Evidence table, 2a. Margin constraint behind the price targets, 2b. Rubric scores (`docs/plan/ai-team.md` §5), 2c. Sources for the shared premises, 3.1 `tcg-supplies`: trading-card storage and display, 3.2 `hobby-modeling-tools`: miniature and scale-model tools (+11 more)

### Community 26 - "2. Per-niche price bands and representative products"
Cohesion: 0.13
Nodes (14): 13 - Sales: landed-cost ceilings and niche economics, 1. Landed-cost ceiling table [data: scout.margin output], 2. Per-niche price bands and representative products, 3. Ranked summary, 4. Gaps and next steps, auto-detailing-tools, coin-supplies, collectibles-display (+6 more)

### Community 27 - "12 — Compliance risk cards for the 8 candidate niches"
Cohesion: 0.10
Nodes (19): 0.1 Checks that apply to every niche, 0.2 Wording rules that apply to every niche (eBay IP policy), 0.3 SKU-level gate (before any listing in any niche), 0.4 Design-patent / Schedule A finding (checked for this card set), 0.5 Prop 65 finding (checked for this card set), 0.6 "Graded card" / "PSA" wording finding, 0. Shared rules, 12 — Compliance risk cards for the 8 candidate niches (+11 more)

## Knowledge Gaps
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `2. Per-niche price bands and representative products` connect `2. Per-niche price bands and representative products` to `llm.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `2. Per-niche price bands and representative products` (e.g. with `evaluate()` and `Inputs`) actually correct?**
  _`2. Per-niche price bands and representative products` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `hooks` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `evaluate()` connect `llm.py` to `2. Per-niche price bands and representative products`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12473118279569892 - nodes in this community are weakly interconnected._
- **Why does `Inputs` connect `llm.py` to `2. Per-niche price bands and representative products`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Should `3. Candidate cards` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._