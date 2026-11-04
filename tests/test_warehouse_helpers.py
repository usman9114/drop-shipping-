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
