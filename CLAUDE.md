# CLAUDE.md

## Project

Proof-of-concept to test whether **eBay (and similar marketplace) dropshipping** is feasible. The idea: pick products with proven demand, make better listings (CJ product images with AI-enhanced surroundings; accurate, structured descriptions), and fulfil through CJ Dropshipping (zero inventory).

- Current phase: **Phase 0, release R1 "Niche Finder"**: find the best online stores and what they do, ending in a niche shortlist (not a single product). Goal, deliverables, exit criteria and scope: `docs/plan/phase-niche-finder-r1.md`; flow: `docs/plan/step1-flow.md`. Sourcing, listings and the live eBay test are later phases. Verdict, thesis and phased plan with kill criteria: `docs/research/00-summary.md`.
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
- **Model roles (owner, 2026-11-04).** Workers are Z.ai GLM (free, first) and Claude **Haiku** and **Sonnet** via OpenRouter (`scout/llm.py` routes: bulk/vision → GLM then Haiku; reasoning/code → GLM then Sonnet). **Phase one is free only**: paid Claude routes are skipped unless `SCOUT_ALLOW_PAID=1`; free OpenRouter models are the fallback. **Opus is the advisor**: plans, reviews and decides; it does not do bulk work. Subagents use `model: haiku` or `sonnet`.
- **Research workflow.** Plan and synthesize on the large model. Fan web searches out to Haiku subagents (`model: haiku`), one topic per agent, in parallel. Save each report to `docs/research/NN-topic.md` and update `00-summary.md`.

## How we think (standing principles, owner 2026-11-04)

Apply these to every task, not only when asked.

1. **One phase at a time.** Every phase has a written goal, deliverables, measurable exit criteria and an out-of-scope list in `docs/plan/`. Work outside the current phase waits. Early phases produce a shortlist of niches, not "the best product"; picking products is a later phase.
2. **Label what we know.** Tag every number `[data]` (observed), `[proxy]` (indirect signal) or `[unknown]`. Never present a proxy as sales, profit or margin. Public records do not show revenue, ad spend, orders or supplier cost; say so and name the gap in every story and report. Paid revenue estimators are modelled guesses and need the owner's approval.
3. **Demand evidence is not eBay demand.** A Shopify store's success shows demand and method. A brand's success does not transfer to zero inventory. Only our own live test measures eBay.
4. **Explain every ranking.** A score documents its inputs, weights and why, keeps the weights in one place, and says what would change the order. If the owner asks "how do you rank", the answer is already in the docs.
5. **Validate before relying.** Rules and classifiers (business model, categories, filters) get a hand-checked sample and an independent second opinion, with an accuracy figure, before their output feeds a decision. Each error we find becomes a test.
6. **Terms before automation, including "wrap an API around it".** Read the site's terms first. If they forbid automated access, do not scrape, drive a browser against it, or get around a bot check; use the official API (owner buys access) or manual reading. Precedent: myip.ms (terms III(e)), decision 0009.
7. **Free first, spend only on request.** Phase one runs on free models; paid Claude routes need `SCOUT_ALLOW_PAID=1`. Stop and ask before spending money, creating accounts, installing unreviewed third-party code, or sending anything outside the repo. A third-party skill or tool is read first, pinned to a commit and installed by an owner-approved script; confirm a named tool exists before installing anything with that name.
8. **Long jobs are resumable and auditable.** Scans run in batches that record their own counts and can restart; progress is watched, not guessed.
9. **Report plainly.** When asked for status, say what is done, what is running now and what is next, in simple steps with numbers. Say what failed or was blocked. Lead with the answer.
10. **Small first.** Any new method, rule, crawl or model prompt runs on a small sample (about 10 to 30 items) before it runs at scale; scale only after the sample passes. Testing small found two bugs and a weak rule on this project before they touched thousands of stores.
11. **Parallel by default, within limits.** Independent work runs in parallel: model calls through `scout.llm.chat_many` (GLM Flash is free; **8 workers** is the tested limit, 16 gets HTTP errors; `spread=0.15` adds the OpenRouter free lane, whose 1,000 calls a day are counted in `data/private/llm_usage.json` and capped at 900), research in background subagents, jobs as resumable batches. Do not wait on one slow serial call. Use the fast `bulk` route for classification; `reasoning` makes GLM think for a minute per call.
12. **Keep decisions in the repo.** Terms read, method chosen and owner decisions go in `docs/decisions/` or `docs/plan/` the same day, so a fresh container can resume from `docs/handoff/session-state.md`.
13. **Autopilot: scripts run it, free models assist, Claude designs** (owner 2026-11-05). The store pipeline runs 24/7 on scheduled scripts; the only AI in the runtime loop is GLM and the OpenRouter free lane via `scout.llm` (cached, budgeted). Build every job idempotent, resumable, rule-versioned and observable; save evidence (counts, shapes, ids), not content, so rule changes re-score without refetching. A finding made in a session becomes a rule, test or prompt in the repo the same day. Design: `docs/plan/autopilot.md`.
14. **Hand off, don't compact** (owner 2026-11-05). Before a session's context gets long (after a big phase, or when background work has finished), stop starting new work: update `docs/handoff/session-state.md` (done, running, next, traps, open owner decisions), commit and push it, then start a fresh session with a short handover prompt that points to `CLAUDE.md` and that file (`create_session`, or give the prompt to the owner). Never rely on automatic compaction to carry context; anything not in the repo is lost. Don't hand off while a background agent this session started is still running: wait for it, or record what it was doing and where its output goes.

## Context: graphify knowledge graph

Project context lives in the graphify knowledge graph (`graphify-out/`). Use it before re-reading files. It is rebuilt by git hooks after each commit, checkout and merge (`graphify hook install`, run by `make setup`). After editing docs or code, run `graphify update .`. For a full semantic rebuild including the research docs, run the `/graphify .` skill (vendored in `.claude/skills/graphify/`).

## Commands

```bash
make setup      # pip install pre-commit graphifyy detect-secrets; install all hooks
make lint       # pre-commit run --all-files
make graph      # graphify update . (refresh knowledge graph)
python -m scout.store tables|runs|query "SQL"|rebuild   # evidence store (docs/plan/data-pipeline.md)
python -m scout.llm --task code "..."                  # free models: Z.ai GLM Flash -> OpenRouter
python -m scout.llm --batch in.jsonl --out out.jsonl   # bulk via GLM + OpenRouter free lane, resumable (skill: free-llm)
python -m scout.llm --usage | --second-opinion "..."    # lane usage today; two-model check
make pipeline | make wh-snapshot | make intel          # warehouse flow and intelligence layer (decision 0007)
python -m scout.webmeta discover|sitemaps|products|scan  # internet-metadata harness (decisions 0008, 0009)
make niches                                             # R1: scan, profile, score, shortlist, supply check (~3 h)
python -m scout.stores meta|deep|ranks                  # store profiler; python -m scout.store_intel --top 40
```

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
