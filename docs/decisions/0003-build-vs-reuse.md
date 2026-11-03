# 0003 — Build vs reuse: workflow, data loading, connectors, LLM routing

> Status: **proposed**, awaiting owner sign-off. Date: 2026-11-03. Rule in force: `CLAUDE.md` "Reuse before build".
> Evidence: market-researcher (Haiku) run, 2026-11-03. Stars come from GitHub pages. Release dates come from PyPI where available. The n8n license text itself was not retrieved (docs URL 404), so license claims for n8n are **[secondary]**.
> Visual: private artifact "Dropship Data Model" (https://claude.ai/artifact/VRe8aSLrYV2g9bc8mwzG5K).

## Decision

**We do not adopt n8n for the research phase.** The pipeline is a handful of Python ingesters that need a clock and retries. Reuse choices below replace most of what we would otherwise write.

| Job | Reuse choice | Why | Caveats |
|---|---|---|---|
| Run ingesters on a schedule | **GitHub Actions** scheduled workflow | In the repo, free tier, 5-minute minimum interval [GitHub docs] | Schedules run **only from the default branch** (ours is still empty, so work must be merged first). Runs can be delayed or dropped. Keys must be stored as GitHub secrets. |
| Load API data into tables | **dlt** (Apache-2.0, v1.32.0 Oct 2026, 6.1k stars) with **DuckDB** (MIT, v2.0.0) | Declarative REST sources, incremental loads, official REST-to-DuckDB tutorial, verified Shopify source for channel 2 | Replaces `scout/store.py` ingestion. Our provenance fields (trust level, params, sha256) may not map to dlt's load metadata. Settle that in a one-day spike on the CJ source. |
| CJ catalog, stock, cost, orders | **CJ's own API and official MCP server** (`CJ-dropshipping/api-mcp`, vendor-run, 4 stars, no releases) | Agents can browse the catalog interactively. Scheduled pulls use the REST API. | Vendor MCP is young. Premium tiers may apply [promotional, unverified]. Tokens expire. |
| Order forwarding to eBay or Shopify | **CJ's native store connections** | Zero order code from us | Whether eBay uses the native connection rather than the API is [unverified] (doc 06 §5). |
| eBay Browse API | **dlt REST source** with its OAuth client-credentials helper | No maintained SDK exists: `ebay-rest` is archived, `ebaysdk` last released 2020. The community MCP (193 stars, unofficial) handles our credentials and needs a security review first. | We write a small source definition, not a client library. |
| LLM routing (Z.ai + OpenRouter) | **LiteLLM** (MIT core, 62.6k stars, v1.106.6 Oct 2026), `zai/` prefix supported | Covers both providers, with router fallbacks. OpenRouter's own `models` fallback covers OpenRouter only. | Spike first: Z.ai "thinking off" and image inputs must pass through. Fallbacks config [unverified, not fetched]. |
| Google Trends | Keep **pytrends** while it works. Apply for the **official Trends API alpha**. | pytrends was archived Apr 2025 (last release 2023) but still returned data today. `trendspy` (MIT) was last released Dec 2024. | Official API is gated. The wrapper stays thin so the library can be swapped. |
| Looking at the data | **Streamlit** on DuckDB, when there is data worth a dashboard | Python only, reads DuckDB directly | Skip Metabase and Grafana for now. |
| Shopify and Instagram flows with sign-off | **Decide when channel 2 starts**: n8n, Activepieces (MIT) or Windmill (AGPL, code-first) | Visual flows a non-engineer can edit, which suits a human-approval step | n8n uses the Sustainable Use License (source-available, free to self-host for own use) and cloud starts around €20/month. No eBay or CJ nodes found, so HTTP calls would be needed. |

## Home-grown audit (flagged to the team)

| Piece | Status | Plan |
|---|---|---|
| `scout/store.py` | **HOME-GROWN**, written before the rule | Replace ingestion with dlt + DuckDB if the spike keeps our provenance. The lake files are plain JSONL, so nothing is locked in. |
| `scout/llm.py` | **HOME-GROWN**, about 250 lines | Replace with LiteLLM after the spike. |
| `scout/trends.py` | Thin wrapper over an archived library | Keep the interface, swap the library when needed. |
| `scout/margin.py`, niche rubric, compliance cards | **Ours by nature** (business logic) | Keep. |

## What this does not settle

- Whether dlt's load metadata can carry `trust`, `params` and `sha256`. If it cannot, we keep a thin provenance layer, and that layer is the only home-grown part left.
- Whether LiteLLM passes through Z.ai's `thinking` parameter and base64 images.
- Repo release dates were missing for GitHub-only projects. Re-check before adopting any of them.

## Next actions

| Action | Owner |
|---|---|
| Approve or amend this plan | owner |
| Add the API keys as GitHub secrets (the default branch is already `research/feasibility-poc`, so no merge is needed; corrected 2026-11-03) | owner |
| One-day spike: dlt REST source for CJ (needs `CJ_API_KEY`) | data-analyst |
| One-day spike: LiteLLM with Z.ai and OpenRouter | glm-coder, reviewed by sales-lead or main session |
| Apply for the Google Trends API alpha | owner |
| Security review of the community eBay MCP, only if we want to use it | compliance-officer |
