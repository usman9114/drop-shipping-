from scout import market_rank, stores


def test_pk_store_is_rupee_storefront():
    assert stores.pk_store({"currency": "PKR", "country": "GB"})
    assert not stores.pk_store({"currency": "USD", "country": "PK"})
    assert stores.in_market({"currency": "USD", "country": "US"}, "us")
    assert not stores.in_market({"currency": "PKR", "country": "PK"}, "us")
    assert stores.in_market({"currency": "EUR"}, None)


def test_weights_sum_to_one():
    assert abs(sum(market_rank.WEIGHTS.values()) - 1) < 1e-9


def test_percentile_matches_percent_rank():
    assert market_rank.percentile([10, 20, 20, 30]) == [0, 1 / 3, 1 / 3, 1]
    assert market_rank.percentile([5]) == [0.0]


def test_growth_log():
    assert market_rank.growth_log(1000, 2000) == round(__import__("math").log(2), 3)
    assert market_rank.growth_log(1000, None) is None


def test_score_orders_busier_and_growing_first():
    rows = [
        {"domain": "flat", "tranco_rank": 5000, "rank_growth_log": 0, "added_90d": 5},
        {"domain": "top", "tranco_rank": 1000, "rank_growth_log": 1, "added_90d": 50},
        {
            "domain": "slow",
            "tranco_rank": 9000,
            "rank_growth_log": None,
            "added_90d": None,
        },
    ]
    ranked = market_rank.score(rows)
    assert [r["domain"] for r in ranked] == ["top", "flat", "slow"]
    assert ranked[0]["best_score"] == 1.0


def test_throttled_store_is_not_given_up():
    rows = [{"domain": "a.pk", "error": "HTTP429"}] * 5 + [
        {"domain": "b.pk", "error": "Timeout"}
    ] * 3
    assert stores.gave_up(rows) == {"b.pk"}


# Hand check 2026-11-22 (docs/decisions/0019): each error became a case.
def _row(**k):
    base = {"products_sampled": 250, "discount_share": 0.2, "category_counts": {}}
    return {**base, **k}


def test_line_vendors_mean_own_label():
    # J.: 33 vendors that are product lines -> brand, not retailer
    assert stores.vendor_is_line("Unstitched", "J.", "junaidjamshed.com")
    assert stores.vendor_is_line("Ready to Wear", "X", "x.pk")
    assert not stores.vendor_is_line("Chicco", "Baby Planet", "babyplanet.pk")
    r = _row(
        vendors=33, top_vendor_share=0.22, own_vendor_share=0.004, line_vendor_share=0.9
    )
    assert stores.business_model({**r, "market": "pk"})[0] == "brand"
    assert stores.business_model(r)[0] == "retailer"  # US: lines not trusted


def test_collection_vendor_names_are_lines():
    for v in [
        "Lux Pret Vol-2 Winter 2026",
        "Men Kurta",
        "Luxury Attars",
        "Winter '26 Women Pret",
        "Festive Wear 26",
        "SYNCC - Women Short Shirt",
    ]:
        assert stores.vendor_is_line(v, "Shop", "shop.pk"), v
    for v in ["Chicco", "Rimmel", "Kryolan", "Essence"]:
        assert not stores.vendor_is_line(v, "Shop", "shop.pk"), v


def test_pk_brand_on_permanent_sale_is_not_general():
    # Beechtree / Gul Ahmed: one vendor, 4 categories, 99% discounted
    cats = {"apparel": 100, "home_decor": 50, "baby_kids": 50, "fragrance": 50}
    r = _row(
        vendors=2,
        top_vendor_share=0.93,
        own_vendor_share=1.0,
        discount_share=0.99,
        category_counts=cats,
    )
    assert stores.business_model(r)[0] == "general"  # US rule unchanged
    assert stores.business_model({**r, "market": "pk"})[0] == "brand"


def test_own_name_vendor_on_resold_goods():
    # Al-Fatah: own name as vendor, titles name many brands -> retailer
    r = _row(
        vendors=2,
        top_vendor_share=0.54,
        own_vendor_share=1.0,
        brand_title_share=0.6,
        brands_named=12,
    )
    assert stores.business_model(r)[0] == "retailer"
    # Mi Store: one other brand -> reseller
    r = _row(
        vendors=4,
        top_vendor_share=0.9,
        own_vendor_share=1.0,
        brand_title_share=0.8,
        brands_named=2,
    )
    assert stores.business_model(r)[0] == "reseller"


def test_feed_summary_counts_lines_and_brands():
    from datetime import date

    prods = [
        {"title": "Lawn 3pc", "vendor": "Unstitched", "variants": []},
        {"title": "Xiaomi Redmi Buds", "vendor": "Mi Store", "variants": []},
        {"title": "Kurta", "vendor": "Pret", "variants": []},
    ]
    s = stores.summarize_feed(prods, "Mi Store", "mistore.pk", [], date(2026, 11, 22))
    assert s["line_vendor_share"] == 1.0
    assert s["brand_title_share"] == round(1 / 3, 3)
    assert s["vendor_names"]["Unstitched"] == 1


def test_line_share_recomputed_from_saved_vendor_names():
    r = {"products_sampled": 10, "vendor_names": {"Men Kurta": 6, "Chicco": 4}}
    assert stores.line_share(r, "J.", "junaidjamshed.com") == 0.6
    assert stores.line_share({"products_sampled": 10}, "x", "x.pk") is None


# Best-seller collection (decision 0021)
def test_pick_best_prefers_evergreen_over_campaign_and_skips_empty():
    cols = [
        {"handle": "eid-sale-best-seller-2026", "title": "Eid", "products_count": 900},
        {"handle": "best-sellers", "title": "Best Sellers", "products_count": 40},
        {"handle": "best-seller-empty", "title": "x", "products_count": 0},
        {"handle": "shoes", "title": "Shoes", "products_count": 500},
    ]
    assert stores.pick_best_collection(cols)["handle"] == "best-sellers"
    only_campaign = [cols[0], cols[3]]
    assert (
        stores.pick_best_collection(only_campaign)["handle"]
        == "eid-sale-best-seller-2026"
    )
    assert stores.pick_best_collection([cols[3]]) is None


def test_summarize_best_aggregates_only():
    from datetime import date

    prods = [
        {
            "id": 1,
            "created_at": "2026-11-01",
            "variants": [{"price": "100", "compare_at_price": "150"}],
        },
        {
            "id": 2,
            "created_at": "2025-01-01",
            "variants": [{"price": "300", "compare_at_price": None}],
        },
    ]
    s = stores.summarize_best(prods, date(2026, 11, 22))
    assert s["best_n"] == 2 and s["best_product_ids"] == [1, 2]
    assert s["best_price_median"] == 200.0
    assert s["best_discount_share"] == 0.5 and s["best_added_90d_share"] == 0.5
    assert "title" not in s
