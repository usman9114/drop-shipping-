# 0012 — Where the forward-only time series live

> 2026-11-04. Status: **decided by the owner: option D, the owner's Claude storage, for now.** Only the weekly feed snapshots and review counts cannot be rebuilt (`docs/plan/temporal-system.md`). The container's `data/private/` is lost on restart, so without durable storage each restart resets the series.

| Option | What it means | Pros | Cons |
|---|---|---|---|
| **A. Private data repo (recommended)** | Owner creates an empty private GitHub repo; the session is given push access (`add_repo` with push); a sync script commits the compressed lake after each run | Free, versioned, restorable in one clone; keeps store lists out of this public repo | One owner step (create repo); store lists sit in a private repo under the stores' unknown terms (acceptable for private working copies under our terms gate) |
| B. Aggregates only in this public repo | Commit per-category weekly totals; store-level rows stay local | No new repo | Loses store-level history: no per-store review velocity or price changes, which is the point |
| C. Nothing durable | Rebuild what we can; accept that snapshots restart after each container reset | Zero setup | The series never accumulates; review velocity and price history are impossible |

Recommendation: A. Rules stay as in decision 0009: robots.txt respected, no personal data, raw store data never in the public repo, nothing sent outside the owner's own repos.

## Owner decision (2026-11-04): D. The owner's Claude storage

"Drop data in my Claude storage for now." The data lives as files in a **private artifact titled "Store Data Vault"** in the owner's claude.ai account (readable only by the owner). A fresh session finds it with the Artifact tool's `list` action (title "Store Data Vault"); the link itself is not written into this public repo.

- **Export:** `python scripts/vault_export.py` writes plain CSV and a `manifest.json` (rows, bytes, sha256 per file) under `data/private/vault/<stamp>/`; each file stays under the 20 MiB asset limit and splits into parts if needed. The session uploads each file to the vault artifact's asset store.
- **Restore:** read each file from the vault into one folder, then `python scripts/vault_restore.py <folder>`; JSON cells and numbers come back typed (round trip tested on a scratch lake).
- **Not stored:** rank history, which rebuilds from Tranco's archive in about 10 minutes; the manifest lists its 26 dates.
- **First export:** 2026-11-04, 8 files, 15 MB (30,372 scan hits, 30,245 store-fact rows, 8,718 light screens, 296 deep profiles, 10,498 snapshot rows).
- **Limits:** a manual step per export (upload) until it is scheduled; the vault holds store-level data under the stores' unread terms, which our terms gate allows only as a private working copy; option A (a private data repo) remains the better long-term home.
