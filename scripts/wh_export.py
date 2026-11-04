"""Export derived warehouse results to committed files.

Only ids, our labels and our computed numbers leave data/private/: no CJ
titles, images or raw prices (CJ data terms unconfirmed).

    python scripts/wh_export.py            # writes dated files
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import duckdb

DB = "data/private/warehouse.duckdb"
OBS_COLUMNS = [
    "sold_count_90d",
    "avg_sold_price",
    "sold_price_min",
    "sold_price_max",
    "avg_shipping",
    "free_shipping_share_pct",
    "active_listings",
    "sell_through_pct",
    "sellers_with_20plus_sales",
    "notes",
]


def main() -> int:
    today = date.today().isoformat()
    con = duckdb.connect(DB, read_only=True)
    sheet = Path(f"data/observations/terapeak-sheet-{today}.csv")
    blanks = ", ".join(f"null::varchar as {c}" for c in OBS_COLUMNS)
    con.execute(
        f"""copy (
            select priority, '{today}' as date, null::varchar as observer,
                   search_phrase, product_type, cj_products, price_floor_best,
                   price_floor_median, review_flags, all_need_image_review, pids,
                   {blanks}
            from mart.mart_terapeak_sheet
        ) to '{sheet}' (header true)"""
    )
    shortlist = Path(f"docs/shortlists/supply-candidates-{today}.csv")
    con.execute(
        f"""copy (
            select pid, coalesce(product_type, 'unclassified') as product_type,
                   type_method, search_phrase, min_price, is_viable, fail_reasons,
                   review_rules, images_screened, images_clean, needs_image_review
            from mart.mart_supply_candidates
            order by is_viable desc, product_type, min_price
        ) to '{shortlist}' (header true)"""
    )
    print(f"wrote {sheet} and {shortlist}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
