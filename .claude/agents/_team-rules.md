# Shared rules for every AI team member

Every agent in `.claude/agents/` reads this file first. It is not an agent itself.

1. **Evidence or it didn't happen.** Every claim that drives a decision cites a source: a URL, a file under `data/evidence/`, or the output of a `scout/` command (with the exact command). Label each claim **[data]** (our own pull), **[primary]** (official source), **[secondary]** or **[estimate]**. Decisions resting only on [secondary]/[estimate] must say so.
2. **Cheapest capable model first.**
   - Bulk work (classification, tagging, first drafts, image QA, scanning catalogs): **free OpenRouter models** via `python -m scout.llm` (see `docs/plan/ai-team.md` §4).
   - Web search: Haiku (`market-researcher`).
   - Execution and analysis: Sonnet.
   - Strategy, synthesis and final calls: Opus (`head-of-marketing`).
   - Never use a paid model for a task a free model passes.
3. **Hard rules from CLAUDE.md apply:**
   - zero inventory
   - CJ images only, product pixels untouched
   - no scraping that breaches marketplace terms
   - no copying competitors
   - no AI attribution in git
4. **Market is US.** Prices in USD, regulations US (CPSC, FCC, FTC, Prop 65).
5. **Write outputs to files, not just chat.**
   - Research: `docs/research/NN-*.md`
   - Decisions: `docs/decisions/NNNN-*.md`
   - Raw data: `data/evidence/<source>/`
   - Keep reports skimmable: tables first, then notes, then sources.
6. **Say what you don't know.** A missing number is reported as missing, never invented. Mocked data must be labeled `MOCK` in the filename and the text.
7. **Use the knowledge graph** before reading lots of files: `graphify query "<question>"`.
