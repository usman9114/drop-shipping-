# 0005 — CJ catalogue client

> Status: **accepted for the Phase 0 spike**, 2026-11-03. Spec: `docs/research/18-cj-api-cheatsheet.md`. Code: `scout/cj.py`. Marked **HOMEGROWN (thin)**.

| Candidate | Fit | Verdict |
|---|---|---|
| CJ official MCP server (`CJ-dropshipping/api-mcp`) | Interactive tools for agents; logs in with account email and password or an MCP token; Node 20+; 4 stars, no releases | Not for CI. Useful later for browsing by hand. |
| dlt REST source | Good for loading into a database | Deferred. The database is parked (decision 0004). |
| Community Python wrappers for CJ | None found in our research | n/a |
| Plain `requests` with urllib3 `Retry` | The documented API is about six calls | **Chosen.** About 200 lines including parsing. |

**Why home-grown:** nothing maintained fits a no-database, CI-only run. It is thin glue over `requests`, with retries from the library, and it is replaceable by a dlt source when the database comes back.

**Guardrails built in:**
- Raw output can only be written under `data/private/` (gitignored), because CJ's data-use terms are unconfirmed (terms gate). Derived shortlists and margin results are committed; raw pulls are not.
- One request per 1.1 seconds, retry on 429 and 5xx, one token refresh on error `1600001`.

**Not verified:** every response shape (see the "Unknowns" list in doc 18). The first live call is the real test.
