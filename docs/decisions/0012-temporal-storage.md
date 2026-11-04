# 0012 — Where the forward-only time series live

> 2026-11-04. Status: **owner decision pending.** Only the weekly feed snapshots and review counts cannot be rebuilt (`docs/plan/temporal-system.md`). The container's `data/private/` is lost on restart, so without durable storage each restart resets the series.

| Option | What it means | Pros | Cons |
|---|---|---|---|
| **A. Private data repo (recommended)** | Owner creates an empty private GitHub repo; the session is given push access (`add_repo` with push); a sync script commits the compressed lake after each run | Free, versioned, restorable in one clone; keeps store lists out of this public repo | One owner step (create repo); store lists sit in a private repo under the stores' unknown terms (acceptable for private working copies under our terms gate) |
| B. Aggregates only in this public repo | Commit per-category weekly totals; store-level rows stay local | No new repo | Loses store-level history: no per-store review velocity or price changes, which is the point |
| C. Nothing durable | Rebuild what we can; accept that snapshots restart after each container reset | Zero setup | The series never accumulates; review velocity and price history are impossible |

Recommendation: A. Rules stay as in decision 0009: robots.txt respected, no personal data, raw store data never in the public repo, nothing sent outside the owner's own repos.
