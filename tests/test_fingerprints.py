"""Pure logic of the supply-fingerprint extractors (no network)."""

from scout import fingerprints as fp


def prod(**kw):
    base = {
        "handle": "x",
        "vendor": "Acme",
        "tags": [],
        "images": [],
        "variants": [{"price": "10", "sku": "A1", "grams": 200}],
        "options": [],
    }
    base.update(kw)
    return base


# page_signals
def test_aliorders_script_fires():
    html = '<script src="https://aliorders.fireapps.io/api/shop/x.js"></script>'
    assert "aliorders" in fp.page_signals(html)["signature_ids"]


def test_plain_page_fires_nothing():
    s = fp.page_signals("<html><body>hello shop</body></html>")
    assert s["signature_ids"] == [] and s["theme_name"] is None


def test_several_apps_detected():
    html = "x cdn.shopify.com y track123.com z loox.io printful.com"
    assert {"track123", "loox", "printful"} <= set(
        fp.page_signals(html)["signature_ids"]
    )


def test_theme_name_and_store_id():
    html = (
        'Shopify.theme = {"name":"Debutify","id":5,"theme_store_id":796,"role":"main"};'
    )
    s = fp.page_signals(html)
    assert (s["theme_name"], s["theme_store_id"]) == ("Debutify", 796)


def test_theme_store_id_null():
    html = 'Shopify.theme = {"name":"custom","id":5,"theme_store_id":null};'
    assert fp.page_signals(html)["theme_store_id"] is None


def test_app_embed_handles():
    html = "https://cdn.shopify.com/extensions/0198a1b2-1234-7abc-8def-0123456789ab/ali-reviews-12/assets/a.js"
    assert fp.page_signals(html)["app_embed_handles"] == ["ali-reviews"]


def test_asyncload_hosts_hostnames_only():
    html = 'var asyncLoad = {urls:["https://a.example.com/x.js?k=1","https://cdn.b.io/y.js"]}'
    assert fp.page_signals(html)["asyncload_hosts"] == ["a.example.com", "cdn.b.io"]


def test_no_asyncload_no_hosts():
    assert (
        fp.page_signals('<script src="https://zzz.com/a.js">')["asyncload_hosts"] == []
    )


# feed_signals
def test_ae_image_and_o1cn():
    ae = "https://cdn.shopify.com/s/files/H" + "a" * 32 + ".jpg"
    ali = "https://cdn.shopify.com/s/files/O1CN01AbCdEfGh_!!123.jpg"
    f = fp.feed_signals(
        [prod(images=[{"src": ae}]), prod(images=[{"src": ali}]), prod()]
    )
    assert f["ae_image_share"] == 0.333 and f["o1cn_share"] == 0.333


def test_item_id_in_handle_sku_tags():
    f = fp.feed_signals(
        [
            prod(handle="gadget-1005004123456789"),
            prod(tags=["1005001234567890"]),
            prod(),
            prod(),
        ]
    )
    assert f["ae_item_id_share"] == 0.5


def test_item_id_needs_exact_16_digits():
    assert (
        fp.feed_signals([prod(handle="sku-10050041234567890")])["ae_item_id_share"]
        == 0.0
    )


def test_dsers_and_cj_sku():
    p1 = prod(variants=[{"price": "5", "sku": "14:200006152#Black", "grams": 0}])
    p2 = prod(variants=[{"price": "5", "sku": "CJYD123456789", "grams": 0}])
    f = fp.feed_signals([p1, p2])
    assert f["dsers_sku_share"] == 0.5 and f["cj_sku_share"] == 0.5


def test_ships_from_values_kept():
    o = [{"name": "Ships From", "values": ["China", "United States"]}]
    f = fp.feed_signals([prod(options=o)])
    assert f["ships_from"] == 1 and f["ships_from_values"] == ["China", "United States"]


def test_ships_from_values_normalised():
    o = [
        {
            "name": "Ships From",
            "values": ["CHINA", "CN", "China Mainland", "spain", "Spain", "default"],
        }
    ]
    assert fp.feed_signals([prod(options=o)])["ships_from_values"] == ["China", "Spain"]


def test_cjk_alone_does_not_pick_a_source():
    assert fp.supply_estimate({}, {"cjk_share": 0.15})["source_guess"] == "unknown"


def test_supplier_vendor_but_not_own_brand():
    f = fp.feed_signals(
        [
            prod(vendor="Shop1102345 Store"),
            prod(vendor="Acme"),
            prod(vendor="Acme Store"),
        ],
        domain="acme.com",
    )
    assert f["vendor_supplier_share"] == 0.333


def test_boilerplate_and_cjk_counts_only():
    body = "Please allow 1-3cm differs due to manual measurement."
    f = fp.feed_signals(
        [prod(body_html=body, title="花 dress"), prod(body_html="Handmade in Ohio")]
    )
    assert f["boilerplate_count"] == 1 and f["cjk_count"] == 1
    assert "manual" not in str(f)


def test_bulk_burst_and_grams_and_ratio():
    ps = [
        prod(
            created_at="2026-01-01T10:05:%02d" % i,
            variants=[{"price": "10", "compare_at_price": "30", "grams": 0}],
        )
        for i in range(5)
    ]
    ps.append(prod(created_at="2026-02-01T09:00:00"))
    f = fp.feed_signals(ps)
    assert f["bulk_burst_max"] == 5
    assert f["compare_ratio_median"] == 3.0
    assert f["grams_zero_share"] == 0.833


def test_feed_vendor_tag_signature():
    assert "dsers_feed" in fp.feed_signals([prod(tags=["DSers", "x"])])["signature_ids"]


def test_brand_like_feed_is_quiet():
    brand = [
        prod(
            vendor="Acme",
            handle=f"item-{i}",
            created_at=f"2026-0{1 + i % 9}-01T10:00:00",
            images=[{"src": f"https://cdn.shopify.com/s/files/acme_{i}.jpg"}],
            variants=[{"price": "50", "sku": f"AC-{i:04d}", "grams": 300}],
            body_html="Made in Vermont.",
        )
        for i in range(30)
    ]
    f = fp.feed_signals(brand, "acme.com")
    for k in (
        "ae_image_share",
        "o1cn_share",
        "ae_item_id_share",
        "dsers_sku_share",
        "cj_sku_share",
        "vendor_supplier_share",
        "boilerplate_share",
        "cjk_share",
        "grams_zero_share",
    ):
        assert f[k] == 0.0, k
    assert f["ships_from"] == 0 and f["signature_ids"] == []
    assert (
        fp.supply_estimate(fp.page_signals("<html></html>"), f)["source_guess"]
        == "unknown"
    )


# supply_estimate
def test_no_evidence_is_unknown():
    e = fp.supply_estimate(None, None)
    assert (e["source_guess"], e["confidence"], e["warehouse_guess"]) == (
        "unknown",
        0.0,
        "unknown",
    )


def test_aliorders_means_aliexpress():
    e = fp.supply_estimate(fp.page_signals("aliorders.fireapps.io"), {})
    assert e["source_guess"] == "aliexpress" and e["confidence"] >= 0.5


def test_unverified_signature_weighs_less_than_observed():
    obs = fp.supply_estimate({"signature_ids": ["aliorders"]}, {})["confidence"]
    unv = fp.supply_estimate({"signature_ids": ["dsers"]}, {})["confidence"]
    assert obs > unv


def test_weak_signals_alone_do_not_pick_source():
    e = fp.supply_estimate({"signature_ids": ["loox", "aftership"]}, {})
    assert e["source_guess"] == "unknown"


def test_generic_only_no_longer_claims_dropship():
    """W3: bulk burst 62%, compare-at 71%, grams=0 32% precision; 2 brands were
    called unknown_dropship on these alone. They stay as evidence, not a verdict."""
    e = fp.supply_estimate(
        {},
        {"bulk_burst_max": 80, "grams_zero_share": 0.95, "compare_ratio_median": 3.0},
    )
    assert e["source_guess"] == "unknown" and e["confidence"] == 0.0
    assert any("bulk import burst" in x for x in e["evidence"])
    assert not any("grams=0" in x for x in e["evidence"])  # weight 0: dropped


def test_ships_from_sets_warehouse():
    e = fp.supply_estimate(
        {}, {"ships_from": 3, "ships_from_values": ["United States"]}
    )
    assert e["warehouse_guess"] == "United States" and e["source_guess"] == "aliexpress"
    e2 = fp.supply_estimate(
        {}, {"ships_from": 3, "ships_from_values": ["China", "Spain"]}
    )
    assert e2["warehouse_guess"] == "mixed: China|Spain"


def test_cj_sku_means_cj():
    assert fp.supply_estimate({}, {"cj_sku_share": 0.4})["source_guess"] == "cj"


def test_contested_source_lowers_confidence():
    clear = fp.supply_estimate({}, {"cj_sku_share": 0.4})["confidence"]
    mixed = fp.supply_estimate({}, {"cj_sku_share": 0.4, "ae_image_share": 0.4})[
        "confidence"
    ]
    assert mixed < clear + 0.1 and mixed < 0.6


def test_weights_clamped_and_confidence_in_range():
    assert fp._clamp(1.7) == 1.0 and fp._clamp(-1) == 0.0
    big = {
        "ae_image_share": 1,
        "ae_item_id_share": 1,
        "dsers_sku_share": 1,
        "ships_from": 9,
        "boilerplate_share": 1,
        "vendor_supplier_share": 1,
        "bulk_burst_max": 500,
        "grams_zero_share": 1,
        "compare_ratio_median": 5,
        "signature_ids": ["dsers_feed"],
    }
    e = fp.supply_estimate(
        {"signature_ids": ["aliorders", "dsers", "ali_reviews"]}, big
    )
    assert 0 <= e["confidence"] <= 1


def test_all_weights_within_unit_interval():
    for _thr, targets in fp.WEIGHTS["feed"].values():
        assert all(0 <= w <= 1 for w in targets.values())
    assert all(0 <= w <= 1 for w in fp.WEIGHTS["strength"].values())


def test_signature_table_is_well_formed():
    ids = [s["id"] for s in fp.SIGNATURES]
    assert len(ids) == len(set(ids))
    for s in fp.SIGNATURES:
        assert (
            s["strength"] in fp.WEIGHTS["strength"]
            and s["evidence"] in fp.WEIGHTS["evidence_mult"]
        )
        assert s["where"] in ("page_source", "feed")


def test_dsers_sku_rejects_brand_style_skus():
    """tommyjohn.com SKUs (2026-11-05) made the old rule fire on a real brand."""
    from scout import stores

    for brand_sku in (
        "5564:XL#L",
        "10045041000:100072:XL/XXL",
        "5561:M/L#M#XS",
        "1234:5678",
    ):
        assert not stores.DSERS_SKU.search(brand_sku), brand_sku
        assert not stores.DROPSHIP_SKU.search(brand_sku), brand_sku
    for ds in (
        "14:200004889#A Children bed  ;5:20129901",
        "14:29#Black;200007763:201336100",
        "200000182:193#Black",
    ):
        assert stores.DSERS_SKU.search(ds), ds


def test_sku_shape_is_content_free_and_rule_compatible():
    from scout import stores

    assert fp.sku_shape("14:200004889#Black") == "99:999999999#AAAAA"
    assert fp.sku_shape("10045041000:100072:XL/XXL") == "99999999999:999999:AA/AAA"
    # the corrected DSers rule gives the same verdict on the shape as on the SKU
    for sku in ("14:200004889#Black;5:20129901", "5564:XL#L", "10045041000:100072:XL"):
        assert bool(stores.DSERS_SKU.search(sku)) == bool(
            stores.DSERS_SKU.search(fp.sku_shape(sku))
        )


def test_feed_keeps_sku_shapes_not_skus():
    f = fp.feed_signals(
        [prod(variants=[{"price": "5", "sku": "CJYZ319118002BY", "grams": 0}])]
    )
    assert f["sku_shapes"] == {"AAAA999999999AA": 1}


# --- W3 validation errors (docs/research/35), one test each -------------------
def _feed(n=60, **kw):
    return {"n_products": n, **kw}


def test_w3_cj_store_with_small_ae_image_share_stays_cj():
    e = fp.supply_estimate({}, _feed(cj_sku_share=0.5, ae_image_share=0.09))
    assert e["source_guess"] == "cj" and e["confidence"] >= 0.7


def test_w3_cj_store_with_small_dsers_share_stays_cj():
    e = fp.supply_estimate({}, _feed(cj_sku_share=0.5, dsers_sku_share=0.072))
    assert e["source_guess"] == "cj"


def test_w3_real_ae_image_and_dsers_shares_still_fire():
    assert fp.supply_estimate({}, _feed(ae_image_share=0.39))["source_guess"] == (
        "aliexpress"
    )
    assert fp.supply_estimate({}, _feed(dsers_sku_share=0.49))["source_guess"] == (
        "aliexpress"
    )


def test_w3_printful_pixel_alone_is_not_pod():
    page = fp.page_signals('<script src="https://www.printful.com/pixel.js">')
    assert "printful" in page["signature_ids"]
    assert fp.supply_estimate(page, _feed())["source_guess"] == "unknown"


def test_w3_pagefly_alireviews_name_map_does_not_fire():
    html = '{"Judgeme":"judgeme","AliReviews":"ali-reviews","Loox":"loox"}'
    assert "ali_reviews" not in fp.page_signals(html)["signature_ids"]


def test_w3_real_ali_reviews_widget_fires_weakly():
    html = (
        "https://cdn.shopify.com/extensions/0198a1b2-1234-7abc-8def-0123456789ab/"
        "ali-reviews-301/assets/alireviews.min.js"
    )
    page = fp.page_signals(html)
    assert "ali_reviews" in page["signature_ids"]
    assert fp.supply_estimate(page, _feed())["source_guess"] == "unknown"  # weak alone


def test_w3_cj_vendor_routes_to_cj_not_aliexpress():
    f = fp.feed_signals([prod(vendor="Cj Dropshipping") for _ in range(12)], "x.com")
    assert f["cj_vendor_share"] == 1.0 and f["vendor_supplier_share"] == 0.0
    assert "aliexpress" not in str(fp.supply_estimate({}, f)["evidence"])


def test_w3_vendor_rule_needs_ten_products():
    f = fp.feed_signals([prod(vendor="Shop1102345 Store") for _ in range(9)], "x.com")
    assert f["vendor_supplier_share"] == 1.0
    assert not any(
        "vendor_supplier" in x for x in fp.supply_estimate({}, f)["evidence"]
    )


def test_w3_demo_site_with_one_product_gets_no_source():
    f = fp.feed_signals(
        [prod(vendor="TPO Demo store", images=[{"src": "/H" + "a" * 32 + ".jpg"}])],
        "tpo.com",
    )
    e = fp.supply_estimate({"signature_ids": ["aliorders"]}, f)
    assert e["source_guess"] == "unknown" and e["confidence"] == 0.0


def test_w3_blocked_feed_keeps_page_signatures():
    e = fp.supply_estimate({"signature_ids": ["aliorders"]}, fp.feed_signals([]))
    assert e["source_guess"] == "aliexpress"


def test_w3_amazon_plus_aliexpress_store_is_mixed():
    skus = ["B0ABC12345", "B0XYZ98765"]  # pragma: allowlist secret (fake ASIN)
    ps = [
        prod(
            images=[{"src": "/H" + "b" * 32 + ".jpg"}],
            variants=[{"price": "9", "sku": skus[i % 2], "grams": 0}],
        )
        for i in range(10)
    ]
    f = fp.feed_signals(ps, "x.com")
    assert f["asin_sku_share"] == 1.0
    e = fp.supply_estimate({}, {**f, "ships_from": 4, "ships_from_values": ["China"]})
    assert e["source_guess"] == "mixed"
    assert e["mixed_sources"] == ["aliexpress", "dropship_other"]
    assert e["confidence"] < 0.9


def test_w3_asin_only_store_is_dropship_other():
    ps = [prod(variants=[{"price": "9", "sku": "B0ABC1234%d" % i}]) for i in range(8)]
    e = fp.supply_estimate({}, fp.feed_signals(ps))
    assert e["source_guess"] == "dropship_other"


def test_w3_pod_sku_shape_is_pod():
    ps = [
        prod(variants=[{"price": "25", "sku": "250311PODAB12#%d" % i}])
        for i in range(8)
    ]
    f = fp.feed_signals(ps)
    assert f["pod_sku_share"] == 1.0
    assert fp.supply_estimate({}, f)["source_guess"] == "pod"


def test_w3_asin_and_pod_rules_reject_lookalikes():
    near_asins = (
        "B0ABC1234 B0ABC123456 b0abc12345 AB0ABC12345"  # pragma: allowlist secret
    )
    for sku in near_asins.split():
        assert not fp._ASIN_SKU.search(sku), sku
    assert not fp._POD_SKU.search("25031PODAB12#3")
    assert not fp._POD_SKU.search("250311POD-AB12#3")


def test_w3_trendsi_and_collective_tags():
    f = fp.feed_signals(
        [prod(tags=["Ship From Overseas"]), prod(tags=["Shopify Collective"])]
    )
    assert {"trendsi", "shopify_collective"} <= set(f["signature_ids"])


def test_w3_cj_image_hosts_are_cj_observed():
    for host in (
        "https://cf.cjdropshipping.com/a.jpg",
        "https://cc-west-usa.oss-accelerate.aliyuncs.com/b.jpg",
    ):
        page = fp.page_signals(host)
        assert page["signature_ids"] == ["cjdropshipping"], host
        e = fp.supply_estimate(page, _feed())
        assert e["source_guess"] == "cj" and e["confidence"] >= 0.6


def test_w3_cj_sku_weight():
    assert fp.WEIGHTS["feed"]["cj_sku_share"][1]["cj"] == 0.7


def test_rule_version_bumped_for_w3():
    assert fp.RULE_VERSION == "2026-11-05.3"
