"""Load CJ catalogue data into the evidence lake (raw layer of the warehouse).

Each command writes one immutable run per dataset through scout.store, so every
row carries a run_id and the run log records source, params and a checksum.
The lake lives under data/private/ (gitignored): CJ's data terms are not
confirmed, so raw rows are never committed.

    python -m scout.ingest_cj catalogue            # US-warehouse listing + category tree
    python -m scout.ingest_cj offers PID [PID ...] # detail, stock and freight per product
    python -m scout.ingest_cj offers --from-file data/private/candidates.txt

Datasets:
    cj_products    one row per product in the US-filtered listing
    cj_categories  one row per leaf category (three levels)
    cj_variants    one row per variant of a product pulled with `offers`
    cj_stock       one row per product x warehouse country
    cj_freight     one row per variant x quote (US -> US, zip FREIGHT_ZIP)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scout import store
from scout.cj import CJClient, CJError

SOURCE = "cj_api_v2"
FREIGHT_ZIP = "10001"  # one fixed zip so quotes compare; East-coast worst-ish case


def flatten_categories(tree) -> list[dict]:
    rows = []
    for one in tree or []:
        for two in one.get("categoryFirstList") or []:
            for three in two.get("categorySecondList") or []:
                rows.append(
                    {
                        "category_id": three.get("categoryId"),
                        "level1": one.get("categoryFirstName"),
                        "level2": two.get("categorySecondName"),
                        "level3": three.get("categoryName"),
                    }
                )
    return rows


def catalogue(client: CJClient, country: str = "US", pages: int = 60) -> dict:
    products = client.search(None, country=country, pages=pages, size=100)
    run_p = store.record_run(
        "cj_products",
        products,
        source=SOURCE,
        trust="data",
        params={"endpoint": "product/listV2", "countryCode": country},
    )
    cats = flatten_categories(client.call("GET", "/product/getCategory"))
    run_c = store.record_run(
        "cj_categories",
        cats,
        source=SOURCE,
        trust="data",
        params={"endpoint": "product/getCategory"},
    )
    return {"cj_products": (run_p, len(products)), "cj_categories": (run_c, len(cats))}


def offers(client: CJClient, pids: list[str], country: str = "US") -> dict:
    variants, stock, freight, failed = [], [], [], []
    for pid in pids:
        try:
            d = client.detail(pid, country)
            for cc, s in client.stock(pid).items():
                stock.append({"pid": pid, "country": cc, **s})
        except CJError as exc:
            failed.append({"pid": pid, "error": str(exc)})
            continue
        for v in d["variants"]:
            length, width, height = (v["dims_mm"] + [None] * 3)[:3]
            variants.append(
                {
                    "pid": pid,
                    "vid": v["vid"],
                    "variant_sku": v["sku"],
                    "variant_name": v["name"],
                    "cost": v["price"],
                    "weight_g": v["weight_g"],
                    "length_mm": length,
                    "width_mm": width,
                    "height_mm": height,
                    "product_weight_g": d["weight_g"],
                    "packing_weight_g": d["packing_weight_g"],
                    "materials": "|".join(d["materials"]),
                    "suggested_price_low": d["suggested_price_low"],
                    "suggested_price_high": d["suggested_price_high"],
                    "image_count": len(d["images"]),
                }
            )
        # Freight once per product, for its cheapest US variant: quotes differ
        # by weight, and variants of one product are usually within grams.
        priced = [v for v in d["variants"] if v["price"] is not None]
        if priced:
            v = min(priced, key=lambda x: x["price"])
            try:
                for q in client.freight(v["vid"], start=country, zip_code=FREIGHT_ZIP):
                    freight.append(
                        {"pid": pid, "vid": v["vid"], "zip": FREIGHT_ZIP, **q}
                    )
            except CJError as exc:
                failed.append({"pid": pid, "vid": v["vid"], "error": str(exc)})
    out = {}
    for name, rows in (
        ("cj_variants", variants),
        ("cj_stock", stock),
        ("cj_freight", freight),
    ):
        out[name] = (
            store.record_run(
                name,
                rows,
                source=SOURCE,
                trust="data",
                params={"pids": len(pids), "countryCode": country},
            ),
            len(rows),
        )
    out["failed"] = failed
    return out


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="Load CJ data into the lake")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("catalogue")
    c.add_argument("--pages", type=int, default=60)
    o = sub.add_parser("offers")
    o.add_argument("pids", nargs="*")
    o.add_argument("--from-file", help="one pid per line")
    a = ap.parse_args(argv)

    client = CJClient()
    if a.cmd == "catalogue":
        result = catalogue(client, pages=a.pages)
    else:
        pids = list(a.pids)
        if a.from_file:
            pids += [
                x.strip() for x in Path(a.from_file).read_text().split() if x.strip()
            ]
        if not pids:
            ap.error("give pids or --from-file")
        result = offers(client, list(dict.fromkeys(pids)))
    for name, value in result.items():
        if name == "failed":
            print(f"failed: {len(value)}", file=sys.stderr)
        else:
            print(f"{name}: run {value[0]}, {value[1]} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
