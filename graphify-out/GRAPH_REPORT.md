# Graph Report - drop-shipping-  (2026-11-03)

## Corpus Check
- 10 files · ~6,029 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .example 1)

## Summary
- 86 nodes · 80 edges · 10 communities (9 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- 00 — Research summary and PoC plan
- 02 — Unit economics, success rates, saturation, tariffs
- 01 — eBay dropshipping policy, enforcement, fees
- 04 — Tooling, APIs and AI listing pipeline
- 05 — Legal/IP/compliance risks and other platforms
- 03 — Suppliers and their APIs
- hooks
- CLAUDE.md
- .pre-commit-config.yaml
- check_no_ai_attribution.py

## God Nodes (most connected - your core abstractions)
1. `02 — Unit economics, success rates, saturation, tariffs` - 10 edges
2. `hooks` - 8 edges
3. `01 — eBay dropshipping policy, enforcement, fees` - 8 edges
4. `04 — Tooling, APIs and AI listing pipeline` - 8 edges
5. `05 — Legal/IP/compliance risks and other platforms` - 8 edges
6. `00 — Research summary and PoC plan` - 7 edges
7. `03 — Suppliers and their APIs` - 7 edges
8. `repos` - 4 edges
9. `PoC plan (feasibility before money)` - 4 edges
10. `git_ident()` - 3 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (10 total, 1 thin omitted)

### Community 0 - "00 — Research summary and PoC plan"
Cohesion: 0.18
Nodes (10): 00 — Research summary and PoC plan, Confidence, Open questions to resolve before building, Phase 0: desk feasibility, $0, ~1–2 weeks of build, Phase 1: listing quality, ~$100–200, Phase 2: live micro-test, ~$300–500 working capital, 60 days, PoC plan (feasibility before money), The thesis to test (+2 more)

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
Cohesion: 0.25
Nodes (8): always_run, args, entry, id, language, name, stages, hooks

### Community 7 - "CLAUDE.md"
Cohesion: 0.29
Nodes (5): Commands, Context: graphify knowledge graph, graphify, Hard rules, Project

### Community 8 - ".pre-commit-config.yaml"
Cohesion: 0.29
Nodes (6): default_install_hook_types, default_stages, exclude, repos, repo, rev

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `hooks` connect `hooks` to `.pre-commit-config.yaml`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `repos` connect `.pre-commit-config.yaml` to `hooks`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._