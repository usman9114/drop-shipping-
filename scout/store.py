"""Evidence store: append-only lake (source of truth) + derived SQLite for queries.

Lake layout (gitignored: raw data stays private until its source terms are
recorded; moved under data/private/ on 2026-11-04, set SCOUT_LAKE to override):
    data/private/lake/<dataset>/<YYYY-MM-DD>/<run_id>.jsonl.gz
    data/private/lake/_runs.jsonl    one line per ingestion run (provenance)

The DuckDB warehouse (warehouse/, dbt) reads the lake directly.

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
import os
import re
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

LAKE = Path(os.environ.get("SCOUT_LAKE", "data/private/lake"))
RUNS = LAKE / "_runs.jsonl"
DB = Path("data/store/scout.db")
_DATASET = re.compile(r"^[a-z][a-z0-9_]{0,62}$")
_COLUMN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")
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
    if not _DATASET.match(dataset):
        raise ValueError(f"invalid dataset name: {dataset!r}")
    for row in rows:
        bad = [k for k in row if not _COLUMN.match(str(k))]
        if bad:
            raise ValueError(f"invalid column name(s): {bad}")
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    body = "\n".join(json.dumps({**r, "run_id": run_id}, sort_keys=True) for r in rows)
    path = LAKE / dataset / now.strftime("%Y-%m-%d") / f"{run_id}.jsonl.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temporary name, then rename: readers (the warehouse globs every
    # file in the lake) never see a half-written run, even if the process dies.
    tmp = path.with_name(path.name + ".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8") as fh:
        fh.write(body + "\n")
    os.replace(tmp, path)
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


def _checked_path(run: dict) -> Path:
    """A run's file must live inside the lake, with a safe dataset name."""
    if not _DATASET.match(str(run.get("dataset", ""))):
        raise ValueError(f"invalid dataset name in run log: {run.get('dataset')!r}")
    path = Path(run["path"]).resolve()
    if not path.is_relative_to(LAKE.resolve()):
        raise ValueError(f"run {run.get('run_id')} points outside the lake")
    return path


def rebuild() -> dict:
    """Recreate the SQLite DB from the lake, atomically.

    The new database is built beside the old one and swapped in only when
    complete. A run whose checksum does not match is quarantined: it is listed
    in `runs` with verified=0 and its rows are NOT loaded. Returns rows loaded
    per table."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    tmp = DB.with_name(DB.name + ".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    counts: dict[str, int] = {}
    cols_by_table: dict[str, list[str]] = {}
    try:
        con.execute(
            "CREATE TABLE runs (run_id TEXT PRIMARY KEY, dataset TEXT, source TEXT,"
            " trust TEXT, params TEXT, fetched_at TEXT, git_sha TEXT, rows INT,"
            " sha256 TEXT, path TEXT, note TEXT, verified INT)"
        )
        for run in _runs():
            path = _checked_path(run)
            with gzip.open(path, "rt", encoding="utf-8") as fh:
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
            if not ok:
                print(
                    f"WARNING: run {run['run_id']} failed its checksum; rows quarantined",
                    file=sys.stderr,
                )
                continue
            rows = [json.loads(line) for line in body.splitlines() if line]
            if not rows:
                continue
            table = run["dataset"]
            new_cols = list(dict.fromkeys(c for r in rows for c in r))
            bad = [c for c in new_cols if not _COLUMN.match(str(c))]
            if bad:
                raise ValueError(f"invalid column name(s) in {run['run_id']}: {bad}")
            if table not in cols_by_table:
                cols_by_table[table] = new_cols
                defs = ",".join(f'"{c}"' for c in new_cols)
                con.execute(f'CREATE TABLE "{table}" ({defs})')
            cols = cols_by_table[table]
            for c in new_cols:
                if c not in cols:
                    con.execute(f'ALTER TABLE "{table}" ADD COLUMN "{c}"')
                    cols.append(c)
            quoted = ",".join(f'"{c}"' for c in cols)
            marks = ",".join("?" for _ in cols)
            con.executemany(
                f'INSERT INTO "{table}" ({quoted}) VALUES ({marks})',
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
    except BaseException:
        con.close()
        tmp.unlink(missing_ok=True)
        raise
    con.close()
    os.replace(tmp, DB)
    return counts


def query(sql: str) -> list[tuple]:
    """Read-only SQL. Rebuilds first when the lake is newer than the database."""
    stale = RUNS.exists() and DB.exists() and RUNS.stat().st_mtime >= DB.stat().st_mtime
    if not DB.exists() or stale:
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
