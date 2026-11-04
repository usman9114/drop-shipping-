"""Export the private lake to plain CSV/JSON files for the owner's Claude storage vault.

The container loses data/private/ on restart (decision 0012). The owner chose to
keep the data in their own Claude storage for now: a private artifact whose asset
store holds these files. Each file is at most 20 MiB (the asset limit). Rank
history is NOT exported: it rebuilds from Tranco's archive in about 10 minutes
(`python -m scout.stores ranks --days-back ...`); the manifest lists the dates.

    python scripts/vault_export.py          # writes data/private/vault/<stamp>/
    python scripts/vault_restore.py <dir>   # loads the files back into the lake

Store-level files name real stores: they go only to the owner's private artifact,
never into git.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scout import store, stores  # noqa: E402

MAX_BYTES = 19 * 1024 * 1024  # stay under the 20 MiB asset cap
# dataset -> (file name, keep only the latest good row per domain?)
DATASETS = {
    "web_scan": ("scan_hits", False),
    "web_meta": ("store_meta", True),
    "web_store_light": ("store_light", True),
    "web_store_deep": ("store_deep", True),
    "web_snapshot_stores": ("snapshot_stores", False),
    "web_snapshot_products": ("snapshot_products", False),
}


def flatten(row: dict) -> dict:
    """Lists and dicts become JSON text so a CSV cell holds them losslessly."""
    return {
        k: json.dumps(v, sort_keys=True) if isinstance(v, (list, dict)) else v
        for k, v in row.items()
    }


def write_csv(path: Path, rows: list[dict]) -> list[Path]:
    """Write rows, splitting into parts when a file would pass the size cap."""
    if not rows:
        return []
    cols = sorted({k for r in rows for k in r})
    parts, part, size, out = [], [], 0, []
    for r in rows:
        line = len(json.dumps(r)) + 16
        if part and size + line > MAX_BYTES:
            parts.append(part)
            part, size = [], 0
        part.append(r)
        size += line
    parts.append(part)
    for i, chunk in enumerate(parts, 1):
        p = (
            path
            if len(parts) == 1
            else path.with_name(f"{path.stem}_part{i}{path.suffix}")
        )
        with p.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(flatten(r) for r in chunk)
        out.append(p)
    return out


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path("data/private/vault") / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for ds, (name, latest) in DATASETS.items():
        rows = stores._all_rows(ds)
        if latest:
            rows = list(stores.latest_good(rows).values())
        for p in write_csv(out_dir / f"{name}.csv", rows):
            files.append(
                {
                    "file": p.name,
                    "dataset": ds,
                    "rows": sum(1 for _ in p.open(encoding="utf-8")) - 1,
                    "bytes": p.stat().st_size,
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                }
            )
    for extra in ("data/private/validation/seen.txt",):
        src = Path(extra)
        if src.exists():
            dst = out_dir / "validation_seen.txt"
            dst.write_bytes(src.read_bytes())
            files.append(
                {
                    "file": dst.name,
                    "dataset": "validation",
                    "bytes": dst.stat().st_size,
                    "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
                }
            )
    ranks = store._runs()
    rank_dates = sorted(
        {
            d
            for r in ranks
            if r["dataset"] == "web_ranks"
            for d in (r.get("params") or {}).get("dates", [])
        }
    )
    manifest = {
        "exported_at": stamp,
        "git_sha": store._git_sha(),
        "files": files,
        "not_exported": {
            "web_ranks": {
                "why": "rebuilds from Tranco's archive in about 10 minutes",
                "list_dates": rank_dates,
                "rebuild": "python -m scout.stores ranks --days-back <days before today for each date>",
            }
        },
        "restore": "download the files into one folder, then: python scripts/vault_restore.py <folder>",
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    total = sum(f["bytes"] for f in files)
    print(f"wrote {out_dir}: {len(files)} files, {total / 1e6:.1f} MB", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
