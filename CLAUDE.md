# CLAUDE.md

## Project

Proof-of-concept to test whether **eBay (and similar marketplace) dropshipping** is feasible. The idea: pick products with proven demand, make better listings (CJ product images with AI-enhanced surroundings; accurate, structured descriptions), and fulfil through CJ Dropshipping (zero inventory).

- Current phase: **research done → Phase 0 (desk feasibility tool)**. See `docs/research/00-summary.md` for the verdict, thesis and phased plan with kill criteria.
- Research reports: `docs/research/01..06-*.md` (eBay policy, unit economics, suppliers, tooling/APIs, legal/platforms, image sourcing). Every claim carries a source URL; `[unverified]` marks secondary-only claims. Keep that convention when adding research.

## Hard rules

- **No AI attribution in git.** Never add `Co-Authored-By: Claude`, `Claude-Session:`, "Generated with Claude Code" or any AI name or email to commit messages, PR bodies or authorship. Commits are authored by the repo owner. The `no-ai-attribution` commit-msg hook enforces this; never bypass it with `--no-verify`.
- **Pre-commit must pass.** Run `make setup` once per clone (installs pre-commit + commit-msg hooks and graphify git hooks). Fix the failures; don't skip hooks.
- **No secrets in the repo.** eBay, CJ and LLM API keys go in `.env` (gitignored). `detect-secrets` scans every commit; if a finding is a false positive, update `.secrets.baseline` with `detect-secrets scan --baseline .secrets.baseline`.
- **Zero inventory.** The business never holds, buys or prepays stock. Every order is purchased from the supplier after the customer pays and shipped by the supplier straight to the buyer. Don't design features that assume we have stock or our own product photos. Images must be supplier-licensed and only enhanced, never fabricated.
- **Images = CJ's own product images** (from the CJ API `bigImage` / `productImageSet` / `variantImage`). AI may change only the surroundings: background, lighting, upscaling, lifestyle scene. The product pixels stay untouched. No text, badges, borders or watermarks (eBay picture policy). Never use Google Images or competitors' photos, even as AI references. Keep the CJ source URL with every generated image. CJ's paid photo service comes later, if the PoC works.
- **Reuse before build.** No home-grown solutions when a maintained tool exists. Before writing any module (ingester, scheduler, LLM router, connector, dashboard), search for an existing library, SDK, MCP server or hosted service, and record the choice in `docs/decisions/` (candidates, license/cost, maintenance signal, why chosen). Write our own only when nothing fits, and then say so to the owner and the team: mark the note `HOMEGROWN` with the reason. Domain logic (margin model, scoring rubric, compliance rules) is ours by nature.
- **Terms gate.** No data source is ingested until its terms have been read and recorded (date, `max_retention`, license link) in `meta.source`. Unknown terms mean *do not retain or publish*: a gitignored working copy under `data/private/` is allowed for operation, but nothing is committed, kept as a dataset, or shared until the terms are recorded. eBay API content is not stored, analysed for statistics, or used to model prices without eBay's written permission (decision 0004). Never use the eBay API to order from CJ, post tracking for CJ-sourced orders, or reprice or stock-sync from CJ prices (License 9.6): those steps are manual. No automated access that a site's terms prohibit (this includes Google Trends via unofficial libraries).
- **Stay policy-compliant in code we build.** No scraping that breaches marketplace terms, no copying competitors' images or text, no sourcing from retail marketplaces (AliExpress, Amazon, Walmart) for eBay orders. See `docs/research/01` and `05`.
- **Source evaluation standard: show what a source helped us discover, never just list tools.** For any research question: (1) define the evidence needed; (2) list the traces the subject leaves (hosting, technology, ads, search results, product feeds, archives, certificates, reviews); (3) find sources that expose those traces, including tools built for other purposes (reverse-IP directories, certificate logs, web archives); (4) test each on a small sample and record relevant leads found, freshness, unique discoveries, cost and effort, and whether the terms allow it; (5) recommend sources by those results. A source without a pilot result is a hypothesis, not a recommendation.
- **Research workflow.** Plan and synthesize on the large model. Fan web searches out to Haiku subagents (`model: haiku`), one topic per agent, in parallel. Save each report to `docs/research/NN-topic.md` and update `00-summary.md`.

## Context: graphify knowledge graph

Project context lives in the graphify knowledge graph (`graphify-out/`). Use it before re-reading files. It is rebuilt by git hooks after each commit, checkout and merge (`graphify hook install`, run by `make setup`). After editing docs or code, run `graphify update .`. For a full semantic rebuild including the research docs, run the `/graphify .` skill (vendored in `.claude/skills/graphify/`).

## Commands

```bash
make setup      # pip install pre-commit graphifyy detect-secrets; install all hooks
make lint       # pre-commit run --all-files
make graph      # graphify update . (refresh knowledge graph)
python -m scout.store tables|runs|query "SQL"|rebuild   # evidence store (docs/plan/data-pipeline.md)
python -m scout.llm --task code "..."                  # free models: Z.ai GLM Flash -> OpenRouter
```

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
