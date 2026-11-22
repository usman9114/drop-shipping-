"""Score the business-model rules against a hand-labelled truth CSV.

    python scripts/check_truth.py data/private/research/pk-business-model-truth.csv

Truth CSV columns: domain, truth, confidence, basis. Rows labelled "unclear" are
left out. Prints every disagreement with the rule's reasons, then the accuracy.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scout import stores  # noqa: E402


def main(argv: list[str]) -> int:
    light = stores.latest_good(stores._all_rows("web_store_light"))
    truth = [
        r
        for r in csv.DictReader(open(argv[1], encoding="utf-8"))
        if r["truth"] != "unclear" and r["domain"] in light
    ]
    ok = 0
    for r in truth:
        got = light[r["domain"]]
        if got["business_model"] == r["truth"]:
            ok += 1
            continue
        print(
            f"WRONG {r['domain']}: truth {r['truth']}, rule {got['business_model']} "
            f"({'; '.join(got.get('business_model_why') or [])}) "
            f"vendors {list((got.get('vendor_names') or {}))[:6]}"
        )
    hi = [r for r in truth if r["confidence"] == "high"]
    hi_ok = sum(light[r["domain"]]["business_model"] == r["truth"] for r in hi)
    print(
        f"accuracy {ok}/{len(truth)} = {ok / len(truth):.0%}; "
        f"high-confidence {hi_ok}/{len(hi)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
