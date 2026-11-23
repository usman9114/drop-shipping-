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


def test_score_orders_popular_growing_active_first_and_skips_unprofiled():
    rows = [
        {
            "domain": "flat",
            "profiled": True,
            "tranco_rank": 5000,
            "crux_bucket": 5000,
            "rank_growth_log": 0,
            "added_90d": 5,
        },
        {
            "domain": "top",
            "profiled": True,
            "tranco_rank": 1000,
            "crux_bucket": 1000,
            "rank_growth_log": 1,
            "added_90d": 50,
        },
        {
            "domain": "small",
            "profiled": True,
            "tranco_rank": None,
            "crux_bucket": 50000,
            "rank_growth_log": None,
            "added_90d": None,
        },
        {
            "domain": "unread",
            "profiled": False,
            "tranco_rank": 100,
            "crux_bucket": 1000,
        },
    ]
    ranked = market_rank.score(rows)
    assert [r["domain"] for r in ranked] == ["top", "flat", "small", "unread"]
    assert ranked[0]["best_score"] == 1.0
    assert ranked[-1]["best_score"] is None  # not scored, listed last
    # a store outside the Tranco top 1M gets no global-rank points
    assert next(r for r in ranked if r["domain"] == "small")["pct_global"] == 0.0


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
def test_pick_best_rules_from_hand_check():
    def pick(*cols):
        c = stores.pick_best_collection(
            [{"handle": h, "title": ttl, "products_count": n} for h, ttl, n in cols]
        )
        return c and c["handle"]

    # evergreen beats a bigger non-evergreen; empty and campaign are skipped
    assert (
        pick(("best-sellers", "B", 40), ("best-selling-collection", "B", 9000))
        == "best-sellers"
    )
    assert (
        pick(("best-seller", "B", 0), ("best-seller-2026", "B", 34))
        == "best-seller-2026"
    )
    # adanslibas, sabritextile: best-seller only in the title
    assert pick(("eid-sale-2026", "Best Sellers", 42)) is None
    assert pick(("printed-kaftaan", "Best Seller", 28)) is None
    # campaigns and dates
    assert (
        pick(("12-12-top-sellings", "x", 103), ("best-selling-5-14-25", "x", 99))
        is None
    )
    assert pick(("best-seller-products-ws-23", "x", 911)) is None
    assert pick(("summer-trending-hit-codes", "x", 11)) is None
    # scoped: one gender, category or brand
    assert pick(("boys-most-popular-products", "x", 50)) is None
    assert pick(("bestsellers-maybelline", "x", 139)) is None
    assert pick(("accessories-seasonal-best-seller", "x", 171)) is None
    # unscoped generic names, counts unreliable (31,930 products on a small shop)
    assert (
        pick(("best-selling-products", "x", 31930), ("hot-selling", "x", 5))
        == "best-selling-products"
    )
    assert pick(("bestseller", "x", 313)) == "bestseller"


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
