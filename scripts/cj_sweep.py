"""Count relevant CJ catalogue hits per product type, US warehouse vs global.

Input: a JSON spec of product types, each with search phrases and a title regex
that a hit must match to count as relevant. Raw CJ responses go to
data/private/ only (terms gate). The derived summary (counts and product ids)
is printed as JSON and may be committed.

    python scripts/cj_sweep.py scripts/cj_sweep_tcg.json \
        --raw data/private/cj-sweep-tcg.json > docs/shortlists/cj-sweep-tcg.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scout.cj import CJClient, private_path


def sweep(client, spec: dict, size: int = 50) -> tuple[list[dict], dict]:
    summary, raw = [], {}
    for t in spec["types"]:
        rx = re.compile(t["match"], re.IGNORECASE)
        exclude = re.compile(t["exclude"], re.IGNORECASE) if t.get("exclude") else None
        row = {"id": t["id"], "name": t["name"], "phrases": t["phrases"]}
        for scope, cc in (("us", "US"), ("global", None)):
            seen: dict[str, dict] = {}
            total = 0
            for phrase in t["phrases"]:
                params = {"keyWord": phrase, "page": 1, "size": size}
                if cc:
                    params["countryCode"] = cc
                data = client.call("GET", "/product/listV2", params=params) or {}
                raw[f"{t['id']}|{scope}|{phrase}"] = data
                total += data.get("totalRecords") or 0
                for c in data.get("content") or []:
                    for p in c.get("productList") or []:
                        name = p.get("nameEn") or ""
                        if rx.search(name) and not (exclude and exclude.search(name)):
                            seen[p["id"]] = p
            row[f"{scope}_search_total"] = total
            row[f"{scope}_relevant"] = len(seen)
            row[f"{scope}_relevant_pids"] = sorted(seen)
        summary.append(row)
        print(
            f"{t['id']:>3} {t['name'][:44]:44} US {row['us_relevant']:>3}/"
            f"{row['us_search_total']:<5} ALL {row['global_relevant']:>3}/"
            f"{row['global_search_total']}",
            file=sys.stderr,
        )
    return summary, raw


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec")
    ap.add_argument("--raw", required=True, help="raw output path under data/private/")
    ap.add_argument("--size", type=int, default=50)
    a = ap.parse_args(argv)
    raw_path = private_path(a.raw)
    spec = json.loads(Path(a.spec).read_text())
    summary, raw = sweep(CJClient(), spec, a.size)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(raw, ensure_ascii=False))
    out = {
        "niche": spec["niche"],
        "date": date.today().isoformat(),
        "source": "CJ API product/listV2, page 1, relevance = title regex in spec",
        "us_relevant_total": sum(r["us_relevant"] for r in summary),
        "global_relevant_total": sum(r["global_relevant"] for r in summary),
        "types": summary,
    }
    json.dump(out, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
