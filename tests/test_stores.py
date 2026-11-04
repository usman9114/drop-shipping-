"""Pure logic of the store profiler (no network)."""

from datetime import date

import pytest

from scout import stores, webmeta

RULES = stores.load_rules()
TODAY = date(2026, 11, 4)


def _p(
    title="",
    ptype="",
    vendor="Acme",
    created="2026-10-20",
    prices=("20",),
    compare=None,
    sku="",
    img="https://cdn.shopify.com/s/files/1/x/products/front.jpg",
    tags=(),
):
    return {
        "title": title,
        "product_type": ptype,
        "vendor": vendor,
        "created_at": created + "T10:00:00-04:00",
        "tags": list(tags),
        "variants": [
            {"price": p, "compare_at_price": compare, "sku": sku, "available": True}
            for p in prices
        ],
        "images": [{"src": img}],
    }


def test_meta_summary_drops_city_and_description():
    out = stores.meta_summary(
        {
            "id": 5,
            "name": "Acme",
            "city": "Somewhere",
            "description": "x",
            "country": "US",
            "province": "Texas",
            "currency": "USD",
            "ships_to_countries": ["US", "CA"],
            "published_products_count": 40,
        }
    )
    assert "city" not in out and "description" not in out
    assert out["ships_to_us"] and out["ships_to_count"] == 2
    assert out["published_products"] == 40


@pytest.mark.parametrize(
    ("ptype", "title", "expected"),
    [
        ("Necklaces", "", "jewelry_watches"),
        ("", "Merino Wool Runner Shoes", "footwear"),
        ("", "Dog Harness No Pull", "pet"),
        ("", "Gift Card", "non_product"),
        ("", "Vitamin D3 Gummies", "health_supplements"),
        ("", "Linen Duvet Cover", "bedding_bath"),
        ("", "Zzzz", "other"),
    ],
)
def test_product_category(ptype, title, expected):
    assert stores.product_category(_p(title=title, ptype=ptype), RULES) == expected


def test_type_wins_over_title_but_falls_back_when_unknown():
    p = _p(title="Dog print hoodie", ptype="Hoodies")
    assert stores.product_category(p, RULES) == "apparel"
    p = _p(title="Dog print hoodie", ptype="Misc")
    assert stores.product_category(p, RULES) == "pet"


def test_dropship_traces():
    ae = _p(
        img="https://cdn.shopify.com/s/files/1/products/"
        "Hb1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f.jpg?v=1"
    )
    assert stores.dropship_traces(ae)["ae_image"]
    assert stores.dropship_traces(_p(sku="200000182:193#Black"))["dropship_sku"]
    assert stores.dropship_traces(_p(sku="CJYD1234567801AZ"))["dropship_sku"]
    assert stores.dropship_traces(_p(vendor="Printful"))["pod_vendor"]
    clean = stores.dropship_traces(_p(sku="SD26100029-101-06"))
    assert not any(clean.values())


def test_vendor_is_shop():
    assert stores.vendor_is_shop("Allbirds", "Allbirds", "allbirds.com")
    assert stores.vendor_is_shop("Acme Co", "", "acmeco.com")
    assert not stores.vendor_is_shop("Nike", "Foot Shop", "footshop.com")
    assert not stores.vendor_is_shop("X", "X", "x.com")  # too short to trust


def test_summarize_feed_aggregates_without_text():
    prods = [
        _p(
            title="Gold Necklace",
            vendor="Acme",
            created="2026-10-20",
            prices=("30", "40"),
            compare="50",
        ),
        _p(title="Silver Ring", vendor="Acme", created="2026-06-01", prices=("20",)),
        _p(title="Gift Card", vendor="Acme", created="2024-01-01", prices=("10",)),
    ]
    s = stores.summarize_feed(prods, "Acme", "acme.com", RULES, TODAY)
    assert s["products_sampled"] == 3
    assert s["oldest_created"] == "2024-01-01" and s["newest_created"] == "2026-10-20"
    assert (s["added_30d"], s["added_90d"], s["added_365d"]) == (1, 1, 2)
    assert s["price_median"] == 20.0  # entry prices 30, 20, 10
    assert s["discount_share"] == round(1 / 3, 3)
    assert s["own_vendor_share"] == 1.0
    assert s["top_category"] == "jewelry_watches"  # gift card is not a category
    assert s["top_category_share"] == round(2 / 3, 3)
    flat = repr(s)
    assert "Necklace" not in flat and "Ring" not in flat


def test_business_model_rules():
    base = {
        "products_sampled": 100,
        "ae_image_share": 0,
        "dropship_sku_share": 0,
        "dropship_vendor_share": 0,
        "pod_share": 0,
        "vendors": 1,
        "top_vendor_share": 1.0,
        "own_vendor_share": 1.0,
    }
    assert stores.business_model(base)[0] == "brand"
    assert stores.business_model({**base, "ae_image_share": 0.5})[0] == "dropship"
    assert stores.business_model(base, homepage_dropship_app=True)[0] == "dropship"
    assert stores.business_model({**base, "pod_share": 0.8})[0] == "pod"
    reseller = {**base, "vendors": 30, "top_vendor_share": 0.2, "own_vendor_share": 0.0}
    assert stores.business_model(reseller)[0] == "reseller"
    assert stores.business_model({"products_sampled": 0})[0] == "unclear"


def test_shop_age_curve_is_monotone_lower_envelope():
    pts = [
        (100, "2015-01-01"),
        (200, "2014-06-01"),
        (300, "2019-01-01"),
        (400, "2018-01-01"),
    ]
    curve = stores.fit_shop_age(pts)
    dates = [d for _, d in curve]
    assert dates == sorted(dates)
    assert curve == [
        (100, "2014-06-01"),
        (200, "2014-06-01"),
        (300, "2018-01-01"),
        (400, "2018-01-01"),
    ]
    assert stores.shop_started_by(250, curve) == "2018-01-01"
    assert stores.shop_started_by(999, curve) is None


def test_homepage_signals_include_marketing_apps():
    html = (
        '<script src="https://connect.facebook.net/en_US/fbevents.js"></script>'
        '<script src="https://static.klaviyo.com/onsite/js/klaviyo.js"></script>'
        '<script src="https://cdn.uppromote.com/x.js"></script>'
        '<script src="https://js.afterpay.com/x"></script>'
        '<a href="https://www.instagram.com/acme_co/">ig</a>'
    )
    out = stores.homepage_signals(html)
    for t in ("meta_pixel", "klaviyo_email", "affiliate_program", "bnpl"):
        assert t in out["traffic_tags"]
    assert out["social_networks"] == ["instagram"]


def test_scan_tranche_keeps_only_shopify_and_counts(monkeypatch):
    fake = {
        "a.com": (["23.227.38.65"], ""),
        "b.com": (["1.2.3.4"], ""),
        "c.com": ([], "rcode3"),
    }
    rows, counts = webmeta.scan_tranche(
        list(fake), 10, qps=0, workers=2, resolver=lambda d: fake[d]
    )
    assert rows == [{"domain": "a.com", "tranco_rank": 11, "a": "23.227.38.65"}]
    assert counts == {"looked_up": 3, "resolved": 2, "errors": 1, "shopify": 1}


def test_web_pixel_settings_identify_platforms():
    # escaped JSON as Shopify embeds it in webPixelsConfigList
    html = (
        'webPixelsConfigList":[{"configuration":"{\\"pixel_id\\":\\"123\\",'
        '\\"pixel_type\\":\\"facebook_pixel\\"}","apiClientId":2329312},'
        '{"configuration":"{\\"pixelCode\\":\\"C9X\\"}","apiClientId":4383523},'
        '{"configuration":"{\\"redditPixelId\\":\\"t2_x\\"}","apiClientId":304258285569}]'
    )
    tags = webmeta.traffic_tags(html)
    assert {"meta_pixel", "tiktok_pixel", "reddit_pixel", "shopify_web_pixels"} <= set(
        tags
    )


def test_page_builder_app_maps_are_not_installs():
    pagefly_map = (
        '"AliReviews": "https://cdn.shopify.com/extensions/x/ali.js", "DSers": 1'
    )
    assert "dropship_app" not in stores.homepage_signals(pagefly_map)["traffic_tags"]
    real = '<script src="https://cdn.dsers.com/js/app.js"></script>'
    assert "dropship_app" in stores.homepage_signals(real)["traffic_tags"]


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Smart Lock with Keypad", "smart_home_security"),
        ("A7 Envelopes 100 pack", "office_paper"),
        ("Sonic Electric Toothbrush", "personal_care"),
        ("PLA Filament 1kg", "maker_3d_laser"),
    ],
)
def test_added_categories(title, expected):
    assert stores.product_category(_p(title=title), RULES) == expected


def test_us_store_needs_dollars_and_us_reach():
    assert stores.us_store({"currency": "USD", "country": "US"})
    assert stores.us_store({"currency": "USD", "country": "HK", "ships_to_us": True})
    assert not stores.us_store({"currency": "PKR", "country": "US"})
    assert not stores.us_store(
        {"currency": "USD", "country": "PK", "ships_to_us": False}
    )


def test_zero_prices_are_ignored():
    s = stores.summarize_feed([_p(prices=("0", "25"))], "x", "x.com", RULES, TODAY)
    assert s["price_median"] == 25.0
