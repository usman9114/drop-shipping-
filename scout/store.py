"""Evidence store: append-only lake (source of truth) + derived SQLite for queries.

Lake layout (committed to git, text, diffable):
    data/lake/<dataset>/<YYYY-MM-DD>/<run_id>.jsonl.gz
    data/lake/_runs.jsonl            one line per ingestion run (provenance)

Every row carries run_id; every run records source, trust level, params,
fetched_at, git sha, row count and a sha256 of the rows. Nothing is edited in
place: a new pull is a new run. MOCK data must use trust="mock".

The SQLite file (data/store/scout.db, gitignored) is rebuilt from the lake:
    python -m scout.store rebuild
    python -m scout.store runs
    python -m scout.store query "SELECT ... "      # read-only
    python -m scout.store tables

Datasets (table = dataset name; columns are the row keys + run_id):
    trend_points        keyword, niche, geo, week, value
    supplier_offers     supplier, product_id, variant_id, sku, title, category,
                        warehouse, cost, ship_cost, ship_days, stock, image_urls, url
    market_listings     marketplace, query, item_id, title, price, shipping,
                        condition, seller, seller_feedback, url
    market_query_stats  marketplace, query, total, price_min, price_p25,
                        price_median, price_p75, price_max, sample_n
    sold_observations   marketplace, query, sold_count, avg_price, window_days,
                        sell_through
    evaluations         subject, kind, result_json, by_agent
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

LAKE = Path("data/lake")
RUNS = LAKE / "_runs.jsonl"
DB = Path("data/store/scout.db")
TRUST = {"data", "primary", "secondary", "estimate", "mock"}


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
    except OSError:
        return ""


def record_run(
    dataset: str,
    rows: list[dict],
    *,
    source: str,
    trust: str,
    params: dict | None = None,
    note: str = "",
) -> str:
    """Write rows to the lake as one immutable run and log its provenance."""
    if trust not in TRUST:
        raise ValueError(f"trust must be one of {sorted(TRUST)}")
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    body = "\n".join(json.dumps({**r, "run_id": run_id}, sort_keys=True) for r in rows)
    path = LAKE / dataset / now.strftime("%Y-%m-%d") / f"{run_id}.jsonl.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write(body + "\n")
    meta = {
        "run_id": run_id,
        "dataset": dataset,
        "source": source,
        "trust": trust,
        "params": params or {},
        "fetched_at": now.isoformat(timespec="seconds"),
        "git_sha": _git_sha(),
        "rows": len(rows),
        "sha256": hashlib.sha256(body.encode()).hexdigest(),
        "path": str(path),
        "note": note,
    }
    RUNS.parent.mkdir(parents=True, exist_ok=True)
    with RUNS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, sort_keys=True) + "\n")
    return run_id


def _runs() -> list[dict]:
    if not RUNS.exists():
        return []
    return [json.loads(line) for line in RUNS.read_text().splitlines() if line.strip()]


def rebuild() -> dict:
    """Recreate the SQLite DB from the lake. Verifies each run's sha256."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute(
        "CREATE TABLE runs (run_id TEXT PRIMARY KEY, dataset TEXT, source TEXT, trust TEXT,"
        " params TEXT, fetched_at TEXT, git_sha TEXT, rows INT, sha256 TEXT, path TEXT,"
        " note TEXT, verified INT)"
    )
    counts: dict[str, int] = {}
    cols_by_table: dict[str, list[str]] = {}
    for run in _runs():
        with gzip.open(run["path"], "rt", encoding="utf-8") as fh:
            body = fh.read().rstrip("\n")
        ok = hashlib.sha256(body.encode()).hexdigest() == run["sha256"]
        con.execute(
            "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                run["run_id"],
                run["dataset"],
                run["source"],
                run["trust"],
                json.dumps(run["params"]),
                run["fetched_at"],
                run["git_sha"],
                run["rows"],
                run["sha256"],
                run["path"],
                run.get("note", ""),
                int(ok),
            ),
        )
        rows = [json.loads(line) for line in body.splitlines() if line]
        if not rows:
            continue
        table = run["dataset"]
        new_cols = list(dict.fromkeys(c for r in rows for c in r))
        if table not in cols_by_table:
            cols_by_table[table] = new_cols
            con.execute(
                f'CREATE TABLE "{table}" ({",".join(f"{chr(34)}{c}{chr(34)}" for c in new_cols)})'
            )
        cols = cols_by_table[table]
        for c in new_cols:
            if c not in cols:
                con.execute(f'ALTER TABLE "{table}" ADD COLUMN "{c}"')
                cols.append(c)
        placeholders = ",".join("?" for _ in cols)
        quoted = ",".join(f'"{c}"' for c in cols)
        con.executemany(
            f'INSERT INTO "{table}" ({quoted}) VALUES ({placeholders})',
            [
                tuple(
                    json.dumps(r.get(c))
                    if isinstance(r.get(c), (list, dict))
                    else r.get(c)
                    for c in cols
                )
                for r in rows
            ],
        )
        counts[table] = counts.get(table, 0) + len(rows)
    con.commit()
    con.close()
    return counts


def query(sql: str) -> list[tuple]:
    if not DB.exists():
        rebuild()
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        cur = con.execute(sql)
        header = tuple(d[0] for d in cur.description or [])
        return [header, *cur.fetchall()]
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evidence store (lake + SQLite)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("rebuild")
    sub.add_parser("runs")
    sub.add_parser("tables")
    q = sub.add_parser("query")
    q.add_argument("sql")
    a = ap.parse_args(argv)

    if a.cmd == "rebuild":
        print(json.dumps(rebuild(), indent=2))
    elif a.cmd == "runs":
        for r in _runs():
            print(
                f"{r['run_id']}  {r['dataset']:20} {r['source']:22} {r['trust']:9} rows={r['rows']}"
            )
    elif a.cmd == "tables":
        for (name,) in query("SELECT name FROM sqlite_master WHERE type='table'")[1:]:
            n = query(f'SELECT COUNT(*) FROM "{name}"')[1][0]
            print(f"{name:22} {n}")
    elif a.cmd == "query":
        for row in query(a.sql):
            print("\t".join("" if v is None else str(v) for v in row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
