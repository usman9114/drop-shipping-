# Local setup: run the project on your own machine

> Written 2026-11-21 for the move from cloud sessions to a local machine. Read `CLAUDE.md` first, then `docs/handoff/session-state.md`. No secrets in this file: key names only.

## 1. Prerequisites

- Python **3.12** (CI uses 3.12; 3.13 also passed the tests), `git`, `make`.
- Windows: use WSL (Ubuntu). The Makefile and hooks assume a POSIX shell.
- Optional: Claude Code CLI, for working in the repo with `CLAUDE.md` and the project agents and skills.

## 2. Clone and install

```bash
git clone https://github.com/usman9114/drop-shipping-.git
cd drop-shipping-
git checkout main                 # default branch since 2026-11-21

python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt -r requirements-autopilot.txt
make setup                        # pre-commit, commit-msg and graphify hooks

# make setup rewrites two tracked files; keep the repo versions:
git checkout -- .claude/settings.json CLAUDE.md && rm -f .claude/settings.json.graphify-bak
```

Optional, only for review counts (Crawl4AI, decision 0014): `pip install -r requirements-crawl.txt && playwright install chromium`.

**Git identity:** the commit-msg hook rejects AI names and emails. Set yours to match the existing commits: `git log --format='%an <%ae>' | sort -u`, then `git config user.name ...` and `git config user.email ...`.

## 3. Keys (`.env`)

```bash
cp .env.example .env              # .env is gitignored
```

| Variable | Needed for | Where to get it |
|---|---|---|
| `ZAI_API_KEY` | every free-model call (GLM Flash first) | z.ai console |
| `OPENROUTER_API_KEY` | free lane and fallback | openrouter.ai keys |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | pulling and pushing the data lake | Supabase project, Settings, API keys: the **`sb_secret_`** key |
| `CJ_API_KEY` | CJ supply check | CJ Dropshipping, API settings |
| `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET` | not needed for R1 (sandbox only) | eBay developer account |
| `ZENROWS_API_KEY`, `SCRAPINGBEE_API_KEY` | optional paid unblock tier | only if the owner turns it on |

Rules: put comments on their own lines (the loader in `scout/llm.py` does not strip trailing comments). The real environment wins over `.env`. Never paste keys into chat, an issue or a commit.

## 4. Check that it works (about 2 minutes)

```bash
python -m pytest -q                         # expect 354 passed
python -m scout.llm --usage                 # lane usage today
python -m scout.llm --task bulk "Reply with the word ok"   # one free call
python -m scout.lake_sync status            # expect remote=75 (or more)
make lake-pull                              # data/private from Supabase
python -c "from scout import fingerprints as f; print(len(f.backlog(10**6)))"   # expect about 0
python -m scout.autopilot daily --only build   # warehouse build from the lake
make ui-data                                # data/private/ui/store-scout.json
```

If `lake_sync status` prints `skipped=true reason=no-supabase-secrets`, the two Supabase keys are missing or empty in `.env`.

## 5. Everyday commands

| Goal | Command |
|---|---|
| Full daily run (discover new stores, meta, light, fingerprints, build, report) | `make autopilot-daily`, then `make lake-push` |
| Health check | `make autopilot-health` |
| Fingerprint a backlog | `python -m scout.fingerprints --backlog 300 --batch 300 && make lake-push` |
| Free-model batch | `python -m scout.llm --batch in.jsonl --out out.jsonl` (8 workers is the tested limit) |
| Query the evidence store | `python -m scout.store tables`, `python -m scout.store query "SQL"` |
| Refresh the knowledge graph | `graphify update .` (the git hooks also do it after each commit) |
| Lint and tests | `make lint`, `make test` |

Push the lake after every long job: `make lake-push`. Supabase is the only copy of `data/private/` outside your machine.

## 6. Local and GitHub Actions together

The autopilot workflow (`.github/workflows/autopilot.yml`) also runs on a schedule. Two writers are safe: lake sync merges append-only run files and never replaces one (tests in `tests/test_lake_sync.py`). Until the Actions secrets are set, the cloud runs keep nothing and the health job fails with `no-heartbeat`; either add the four secrets or disable the workflow in the Actions tab.

## 7. Traps

- Every commit starts a background graphify rebuild that dirties `graphify-out/`. Commit it as "Refresh knowledge graph". A commit made during the rebuild can fail; wait a few seconds.
- Never `--no-verify`. Fix what pre-commit reports.
- `detect-secrets` false positive: `detect-secrets scan --baseline .secrets.baseline`.
- Raw store domains, CJ output and eBay data stay in `data/private/` (gitignored). Commit aggregates only.
