"""Offline tests for the warehouse helpers: lake loader and LLM cache."""

from scout import classify, ingest_cj


def test_flatten_categories_keeps_three_levels():
    tree = [
        {
            "categoryFirstName": "Pet Supplies",
            "categoryFirstList": [
                {
                    "categorySecondName": "Pet Toys",
                    "categorySecondList": [
                        {"categoryId": "C1", "categoryName": "Chew Toys"}
                    ],
                }
            ],
        }
    ]
    assert ingest_cj.flatten_categories(tree) == [
        {
            "category_id": "C1",
            "level1": "Pet Supplies",
            "level2": "Pet Toys",
            "level3": "Chew Toys",
        }
    ]
    assert ingest_cj.flatten_categories(None) == []


class FakeCJ:
    def detail(self, pid, country):
        return {
            "weight_g": 30.0,
            "packing_weight_g": 45.0,
            "materials": ["PP"],
            "suggested_price_low": 9.0,
            "suggested_price_high": 11.0,
            "images": ["a"],
            "variants": [
                {
                    "vid": "V2",
                    "sku": "s2",
                    "name": "b",
                    "price": 2.0,
                    "weight_g": 40.0,
                    "dims_mm": [1, 2, 3],
                },
                {
                    "vid": "V1",
                    "sku": "s1",
                    "name": "a",
                    "price": 1.5,
                    "weight_g": 45.0,
                    "dims_mm": [1, 2, 3],
                },
            ],
        }

    def stock(self, pid):
        return {"US": {"total": 28, "cj": 28, "factory": 0}}

    def freight(self, vid, start, zip_code):
        self.freight_vid = vid
        return [{"carrier": "X", "price_usd": 5.2, "days_low": 3, "days_high": 8}]


def test_offers_lands_variants_stock_and_freight_for_cheapest_variant(monkeypatch):
    runs = {}
    monkeypatch.setattr(
        ingest_cj.store,
        "record_run",
        lambda name, rows, **kw: runs.setdefault(name, rows) and f"run-{name}",
    )
    cj = FakeCJ()
    out = ingest_cj.offers(cj, ["P1"])
    assert len(runs["cj_variants"]) == 2 and runs["cj_variants"][0]["materials"] == "PP"
    assert runs["cj_stock"] == [
        {"pid": "P1", "country": "US", "total": 28, "cj": 28, "factory": 0}
    ]
    assert cj.freight_vid == "V1"  # cheapest variant
    assert runs["cj_freight"][0]["zip"] == ingest_cj.FREIGHT_ZIP
    assert out["failed"] == []


def test_parse_labels_keeps_only_valid_entries():
    text = (
        'noise {"labels": [{"i": 0, "type": "Bathroom Shelf"}, {"i": 5, "type": "x y"},'
        ' {"i": 1, "type": "NIKE!!"}, "junk"]}'
    )
    assert classify.parse_labels(text, 2) == {0: "bathroom shelf"}
    assert classify.parse_labels("not json", 2) == {}


def test_classify_caches_by_title_hash_not_title():
    def fake_chat(prompt, task, json_mode):
        return {"model": "m", "text": '{"labels": [{"i": 0, "type": "vase"}]}'}

    rows = classify.classify(["Nordic Flower Vase"], ["necklace"], fake_chat)
    assert rows == [
        {
            "title_sha256": classify.title_hash("nordic flower vase"),
            "product_type": "vase",
            "model": "m",
            "prompt_version": classify.PROMPT_VERSION,
        }
    ]
    assert "Vase" not in str(rows[0]["title_sha256"])


def test_image_verdict_needs_all_checks_and_marks_clean():
    from scout import screen_images as si

    ok = (
        '{"text_overlay": false, "logo_or_brand": false, "watermark": false,'
        ' "border_or_collage": false, "person": true, "child": false}'
    )
    v = si.parse_verdict(ok)
    assert v["clean"] is True and v["person"] is True  # hands/people allowed
    assert (
        si.parse_verdict(ok.replace('"child": false', '"child": true'))["clean"]
        is False
    )
    assert si.parse_verdict('{"text_overlay": false}') is None
    assert (
        si.parse_verdict(
            '{"text_overlay": "no", "logo_or_brand": false, "watermark":'
            ' false, "border_or_collage": false, "person": false,'
            ' "child": false}'
        )
        is None
    )


def test_screen_skips_failures_and_yields_hash_keyed_rows():
    from scout import screen_images as si

    def fake_chat(prompt, task, image_urls, json_mode):
        if "bad" in image_urls[0]:
            raise RuntimeError("model down")
        return {
            "model": "m",
            "text": '{"text_overlay": true, "logo_or_brand": false,'
            ' "watermark": false, "border_or_collage": false, "person": false,'
            ' "child": false}',
        }

    rows = list(si.screen(["https://x/bad.jpg", "https://x/ok.jpg"], fake_chat))
    assert len(rows) == 1 and rows[0]["clean"] is False
    assert rows[0]["image_sha256"] == si.url_hash("https://x/ok.jpg")


def test_image_rows_dedupe_and_number_positions():
    rows = ingest_cj.image_rows("P", {"images": ["a", "b", "a"]})
    assert [(r["position"], r["url"]) for r in rows] == [(0, "a"), (1, "b")]
