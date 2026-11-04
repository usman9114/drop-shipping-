"""Quick supply sanity check for the step-1 niche shortlist (before step 2).

For each shortlisted category, a few search phrases (the merchant product
types published in the shortlist, else fixed phrases below) are run against
CJ's product search, once with US-warehouse stock and once without a country
filter. Output per phrase: how many CJ products match (first page, capped at
100) and the median CJ cost against the stores' median entry price.

This is a sanity check, not sourcing: it only says whether supply plausibly
exists at a cost that leaves room. Raw CJ rows go to the private lake (CJ data
terms unconfirmed); only counts and our ratios are committed.

    python scripts/supply_sanity.py docs/shortlists/<date>-niche-candidates.csv
"""

from __future__ import annotations

import csv
import statistics
import sys
from datetime import date
from pathlib import Path

from scout import store
from scout.cj import CJClient

PHRASES = {
    "apparel": ["women dress", "hoodie", "leggings"],
    "jewelry_watches": ["necklace", "earrings", "bracelet"],
    "bags_accessories": ["tote bag", "crossbody bag", "sunglasses"],
    "home_decor": ["wall art", "vase", "throw pillow cover"],
    "kitchen_dining": ["tumbler", "kitchen gadget", "storage container"],
    "beauty_cosmetics": ["makeup brush", "lip gloss", "eyelashes"],
    "footwear": ["women sandals", "slippers", "sneakers"],
    "pet": ["dog harness", "cat toy", "pet bed"],
    "fitness_sports": ["yoga mat", "resistance bands", "gym bag"],
    "outdoor_camping": ["camping lantern", "hammock", "hiking backpack"],
    "swim_lingerie": ["bikini", "bralette", "swimsuit"],
    "hobby_crafts_art": ["crochet kit", "paint brushes", "stickers"],
    "skincare": ["face roller", "facial cleansing brush", "silk pillowcase"],
    "haircare": ["hair clips", "scrunchies", "hair brush"],
    "garden_tools": ["garden tools", "planter", "plant stand"],
    "cleaning_household": ["cleaning brush", "drawer organizer", "laundry basket"],
    "bedding_bath": ["bath towel", "duvet cover", "bath mat"],
    "party_seasonal": ["balloons", "halloween decoration", "party decoration"],
    "smart_home_security": ["smart plug", "door sensor", "security camera"],
    "personal_care": ["massager", "electric toothbrush", "sleep mask"],
    "maker_3d_laser": ["3d printer filament", "engraving tool", "cutting mat"],
    "nails": ["press on nails", "nail art", "nail lamp"],
    "fragrance": ["candle", "essential oil diffuser", "reed diffuser"],
}


def median(xs):
    return round(statistics.median(xs), 2) if xs else None


def main(argv: list[str]) -> int:
    src = (
        Path(argv[1])
        if len(argv) > 1
        else sorted(Path("docs/shortlists").glob("*-niche-candidates.csv"))[-1]
    )
    with src.open(newline="", encoding="utf-8") as fh:
        short = list(csv.DictReader(fh))
    cj = CJClient()
    raw, out = [], []
    for c in short:
        cat = c["category"]
        typed = [
            t.strip() for t in (c.get("example_types") or "").split(";") if t.strip()
        ]
        phrases = (typed[:2] + PHRASES.get(cat, []))[:3]
        store_price = (
            float(c["median_entry_price"]) if c.get("median_entry_price") else None
        )
        for ph in phrases:
            row = {
                "category": cat,
                "phrase": ph,
                "store_median_entry_price": store_price,
            }
            for scope, country in (("us", "US"), ("any", None)):
                try:
                    items = cj.search(keyword=ph, country=country, pages=1, size=100)
                except Exception as exc:  # recorded, not fatal
                    row[f"{scope}_error"] = type(exc).__name__
                    continue
                raw += [{**i, "phrase": ph, "scope": scope} for i in items]
                costs = [i["price_low"] for i in items if i.get("price_low")]
                row[f"cj_{scope}_matches"] = len(items)
                row[f"cj_{scope}_median_cost"] = median(costs)
                if store_price and costs:
                    row[f"{scope}_price_to_cost"] = round(
                        store_price / median(costs), 2
                    )
            out.append(row)
            print(row, file=sys.stderr)
    store.record_run(
        "cj_supply_sanity",
        raw,
        source="cj_api",
        trust="data",
        params={"shortlist": str(src)},
        note="CJ listV2 keyword search for niche shortlist phrases; private",
    )
    today = date.today().isoformat()
    dst = Path(f"docs/shortlists/{today}-supply-sanity.csv")
    cols = [
        "category",
        "phrase",
        "store_median_entry_price",
        "cj_us_matches",
        "cj_us_median_cost",
        "us_price_to_cost",
        "cj_any_matches",
        "cj_any_median_cost",
        "any_price_to_cost",
        "us_error",
        "any_error",
    ]
    with dst.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n"
        )
        w.writeheader()
        w.writerows(out)
    print(f"wrote {dst}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
