"""Load a vault export (see scripts/vault_export.py) back into the private lake.

    python scripts/vault_restore.py data/private/vault_download/

Each CSV becomes one new lake run of its dataset (source "vault_restore"), with
JSON-encoded cells turned back into lists and dicts and numbers back into numbers.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scout import store  # noqa: E402


def parse_cell(v: str):
    if v == "":
        return None
    if v[0] in "[{":
        try:
            return json.loads(v)
        except ValueError:
            return v
    if v in ("True", "False"):
        return v == "True"
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


def main(argv: list[str]) -> int:
    folder = Path(argv[1])
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    by_ds: dict[str, list[dict]] = {}
    for f in manifest["files"]:
        if f.get("restore_to"):  # a private working file, copied back as-is
            dst = Path(f["restore_to"])
            if not dst.resolve().is_relative_to(Path("data/private").resolve()):
                print(
                    f"skip {f['file']}: restore_to outside data/private",
                    file=sys.stderr,
                )
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((folder / f["file"]).read_bytes())
            print(f"{f['file']} -> {dst}", file=sys.stderr)
            continue
        if not f["file"].endswith(".csv"):
            continue
        with (folder / f["file"]).open(newline="", encoding="utf-8") as fh:
            rows = [
                {k: parse_cell(v) for k, v in r.items() if k != "run_id"}
                for r in csv.DictReader(fh)
            ]
        by_ds.setdefault(f["dataset"], []).extend(rows)
    for ds, rows in by_ds.items():
        run = store.record_run(
            ds,
            rows,
            source="vault_restore",
            trust="data",
            params={"exported_at": manifest["exported_at"]},
            note="restored from the owner's Claude storage vault",
        )
        print(f"{ds}: {len(rows)} rows -> run {run}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
