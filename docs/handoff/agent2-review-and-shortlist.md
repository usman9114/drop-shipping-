# Brief for the second agent: independent review, then build the shortlist engine

> Written 2026-11-03 by the first agent for the repo owner. **This repo is public.** Everything you commit is world-readable and permanent.

## 1. Project in four lines

A proof of concept for **zero-inventory eBay US dropshipping** sourced from **CJ Dropshipping** US warehouses. The idea is to find products with proven demand, make better listings from CJ's own images, and test whether the margins hold. Current phase: Phase 0, a desk feasibility tool. Primary niche (decision 0002): **trading-card supplies**. Spent so far: $0. No API keys exist yet for CJ or eBay.

## 2. Read first (in this order, about 30 minutes)

1. `CLAUDE.md` (hard rules, binding)
2. `docs/research/00-summary.md`, then `docs/decisions/0002-niche-selection.md`
3. `docs/decisions/0004-postgres-warehouse-and-source-terms.md` (note the "Parked" banner) and `0005-cj-client.md`
4. `docs/plan/ai-team.md`, `.claude/agents/_team-rules.md`
5. `docs/research/17-free-feeds-and-storage-terms.md` (eBay API license limits) and `18-cj-api-cheatsheet.md`
6. Code: `scout/margin.py`, `scout/cj.py`, `scout/store.py`, `tests/`

Use `graphify query "<question>"` before reading many files, to save tokens.

## 3. Ground rules (from `CLAUDE.md`, restated because they matter most)

- **Public repo.** Never commit keys, tokens, personal data, raw CJ or eBay data, or anything private. Raw API output lives in `data/private/` (gitignored). When unsure, don't commit; ask.
- **No AI attribution in git.** No `Co-Authored-By`, no "Generated with", no AI names or emails in commits, PR text or authorship. Use the repo owner's git identity (`git log -1 --format='%an <%ae>'` shows it). The commit-msg hook rejects violations. Never use `--no-verify`.
- **Run `make setup` once**, then `make test` and `pre-commit run --all-files` must pass before every push.
- **Reuse before build.** Search for an existing tool first. Record choices in `docs/decisions/`. Home-grown code is flagged `HOMEGROWN` with a reason.
- **Terms gate.** Unknown data terms mean don't store. eBay API content is not stored, analysed for statistics, or used to model prices without eBay's written permission.
- **Zero inventory.** CJ images only, product pixels untouched. No scraping that breaches terms.
- **Evidence labels.** Mark claims `[data]`, `[primary]`, `[secondary]`, `[estimate]` or `[unverified]`. Never invent numbers. Mock data is labeled `MOCK`.
- **Don't change** `CLAUDE.md`, accepted decisions (0001 to 0005), or the behaviour of `scout/cj.py`, `scout/margin.py`, `scout/llm.py`, `scout/store.py`. Propose changes in your review instead.

## 4. How to work

- Clone: `git clone -b agent2/review-and-shortlist https://github.com/usman9114/drop-shipping-.git`
- Work **only on `agent2/review-and-shortlist`**. Keep a rebase on `research/feasibility-poc` (`git fetch && git rebase origin/research/feasibility-poc`) before you start each part. The first agent keeps working on that branch and stays out of the paths you own (below).
- Open **two pull requests into `research/feasibility-poc`**: one for the review, one for the shortlist engine. Do not push to `research/feasibility-poc` directly and never force-push it.
- Small commits with clear messages. If blocked or unsure, write the question in the PR description. Don't guess.

## 5. Part 1: independent review (read-only, then a report)

Deliverable: `docs/reviews/2026-11-agent2-project-review.md`. You may add that file only. Findings go in a table: **severity** (blocker, high, medium, low), **evidence** (`file:line` or URL), **recommended fix**, **effort**. End with the **top 10 actions**.

Review these areas. Challenge the work. Don't be polite about it.

1. **Does the thesis hold?** Check the margin model assumptions (fees applied to item plus tax, return and dispute reserves, ad rate), the niche scoring and the conclusion that few products pass. Find unsupported claims, circular reasoning and stale facts. Verify key claims against **primary sources**: eBay's fee page, the eBay API License Agreement (sections 8.1.3, 8.1.4, 9.5, 9.7, 9.10), CJ's developer docs, CPSC and FTC rules cited.
2. **Legal and policy risk.** eBay's dropshipping policy reading, image rules, brand and grading-company wording (PSA, BGS, Pokémon), magnets in "magnetic card holders", Prop 65, sales tax, FTC shipping-time claims. What is missing?
3. **Code and tests.** Bugs, edge cases, misleading tests, `scout/store.py` and `scout/llm.py` especially. Does CI actually protect anything?
4. **Public-repo hygiene.** Secrets or personal data in history (the first agent found none, so confirm independently), commit-author email exposure, missing README, LICENSE, SECURITY.md, branch protection, secret scanning and push protection, which branch is the default, and whether strategy documents should be public at all. Recommend, don't decide.
5. **Process.** Overlap between agent definitions, documentation sprawl, anything that burns tokens without adding evidence. What would you delete or merge?

## 6. Part 2: build the shortlist engine (stage E of `docs/plan/ai-team.md`)

It is buildable **offline today** and will be used the day the CJ key arrives. You own these paths: `scout/shortlist.py`, `scout/rules.py`, `rules/`, `tests/test_shortlist.py`, `tests/test_rules.py`, `tests/fixtures/`, `docs/runbooks/shortlist.md`, `docs/shortlists/`.

**What it does:** read CJ search and detail results plus Terapeak observations, screen products against compliance rules, compute margins with the existing model, and rank them.

**Inputs**
- CJ results in the shapes produced by `scout/cj.py` (`normalize_listing`, `normalize_detail`), read from `data/private/*.json`. These shapes are **unverified against a live CJ response**, so parse defensively and tolerate missing fields.
- Terapeak observations: `docs/templates/terapeak-observations.csv` columns, files under `data/observations/`.

**Rules as data, not code** (`rules/*.yml` or JSON): each rule has an id, a reason and a pointer to the document that justifies it. Start from `docs/research/12-compliance-niche-cards.md` and decision 0002: banned words (grading companies, game and brand names, "PSA style"), excluded product traits (battery, lithium, wireless, mains power, children's products, liquids, oversize), price floor. Each rule has a unit test.

**Pipeline:** normalize, screen, derive a target sell price (from Terapeak sold prices when present, otherwise an explicit `[estimate]` markup), call `scout.margin.evaluate` (do not reimplement it), rank by margin headroom, and write a report.

**CLI:** `python -m scout.shortlist --cj data/private/cj-search.json --terapeak data/observations/<file>.csv --out docs/shortlists/<date>.md`

**Committed outputs contain only** CJ product id, sku, our computed metrics, flags and verdict. No CJ names, descriptions, images or raw prices (CJ's data terms are unconfirmed).

**Acceptance criteria**
- Deterministic and idempotent. No network access. No new secrets.
- `make test` and `pre-commit run --all-files` green, and CI green on the PR.
- Unit tests per rule, plus a **golden-file test** on a small synthetic fixture. Fixtures are invented, not copied from CJ or eBay.
- Missing or malformed fields produce a flagged row, never a crash.
- `docs/runbooks/shortlist.md` explains how to run it and read the output.
- The PR description lists assumptions, unverified shapes and open questions.

**Out of scope:** live API calls, a database, the eBay API, images, listing copy, the Shopify channel.

## 7. When you finish

Report: what you did, what is unverified, what you would do next, and any decision the owner must make. Keep it short.
