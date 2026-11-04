# 0011 — Weekly store snapshots: reuse and build

> 2026-11-04. Needed for review velocity and release rhythm over time (`docs/plan/estimating-sales-and-profit.md`). Audit of candidates: `docs/research/25-similar-repos-audit.md`.

## Candidates

| Candidate | Licence | Maintenance | Verdict |
|---|---|---|---|
| vladevr/shopify-price-monitor | MIT | commit 2026-09-22, 0 stars | Not used as code: false removals from truncated feeds, ignores Retry-After and robots.txt, impersonates a browser and rotates proxies |
| sarrarmohcin/Shopify-price-monitor | MIT | commit 2026-10-29, 0 stars | Not used as code: no robots.txt check, HTTP-date Retry-After unsupported; its "abort the store before saving" idea is kept |
| ShopIntelligence, Shopify-Scout | none | 1 star each | Not used: no licence |
| `urllib3.util.Retry`, `urllib.robotparser`, `requests` | MIT / PSF | maintained | **Used** for retries, Retry-After and robots.txt |

## Decision

Build the snapshot change model and completeness gate ourselves (`scout/snapshots.py`, `scout/snapshot_job.py`): the logic is specific to our rules, and no maintained, licensed tool handles partial feeds safely. **HOMEGROWN**, domain logic only; transport (retries, Retry-After, robots) uses maintained libraries. `scout.snapshots.parse_retry_after` and `next_delay` stay for one purpose urllib3 does not cover: **skip a store whose Retry-After is longer than the job's budget** instead of holding a worker.

## Rules in the job

1. Robots.txt first; identifying User-Agent; one pause between requests to a store.
2. A store is **complete** only if every page returned and the product count is plausible against `/meta.json`; otherwise the diff for it is **partial or failed** and reports no removals (and no new products if the earlier snapshot was partial).
3. A 403 or 430 stops the store for the run and marks it `blocked`. No proxies, no browser impersonation.
4. "Removed" means "absent from the public feed"; an unpublished product is not proven gone.
5. Only ids, dates, prices and availability are stored (`snapshots.compact`); private lake only (terms of each store not yet recorded).
6. Availability flips are a demand proxy, never units sold.
