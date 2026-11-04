"""Products CJ can ship from the US, with the lowest eBay price that passes
the margin model (scout.margin.min_price) on real cost and freight."""

import sys
from pathlib import Path


def model(dbt, session):
    dbt.config(materialized="table")
    sys.path.insert(0, str(Path.cwd().parent))  # repo root: dbt runs in warehouse/
    from scout.margin import min_price

    max_price = float(dbt.config.get("max_listing_price") or 45.0)
    max_weight = float(dbt.config.get("max_weight_g") or 500)
    min_stock = int(dbt.config.get("min_us_stock") or 20)

    offers = dbt.ref("core_fact_offer").df()
    products = dbt.ref("core_dim_product").df()[
        [
            "pid",
            "product_type",
            "type_method",
            "search_phrase",
            "level1",
            "level2",
            "level3",
            "is_excluded",
            "review_rules",
        ]
    ]
    df = offers.merge(products, on="pid", how="left")
    screen = dbt.ref("enr_image_screen").df()
    df = df.merge(screen, on="pid", how="left")

    def floor(row):
        if row.cost != row.cost or row.ship_usd != row.ship_usd:  # NaN check
            return None
        return min_price(float(row.cost), float(row.ship_usd))

    df["min_price"] = df.apply(floor, axis=1)
    reasons = []
    for row in df.itertuples():
        r = []
        if row.is_excluded:
            r.append("excluded_by_rule")
        if row.ship_usd != row.ship_usd:
            r.append("no_us_freight_quote")
        if (
            row.min_price is None
            or row.min_price != row.min_price
            or row.min_price > max_price
        ):
            r.append("price_floor_above_max")
        if row.ship_weight_g == row.ship_weight_g and row.ship_weight_g > max_weight:
            r.append("too_heavy")
        if row.us_stock != row.us_stock or row.us_stock < min_stock:
            r.append("low_us_stock")
        reasons.append(",".join(r) or None)
    df["fail_reasons"] = reasons
    df["is_viable"] = df["fail_reasons"].isna()
    # Image screen only routes to review (CLAUDE.md: never fabricate images; a
    # product needs at least one clean supplier image to be listable).
    df["needs_image_review"] = (df["images_screened"].fillna(0) > 0) & (
        df["images_clean"].fillna(0) == 0
    )
    return df
