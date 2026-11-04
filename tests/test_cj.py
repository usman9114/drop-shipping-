"""CJ client tests use recorded-shape replies. They prove our handling of the
documented shapes, not that CJ behaves that way: that needs a live key."""

import pytest

from scout import cj

TOKEN_OK = {"code": 200, "data": {"accessToken": "T1", "refreshToken": "R1"}}
LIST_OK = {
    "code": 200,
    "data": {
        "content": [
            {
                "productList": [
                    {
                        "id": "P1",
                        "nameEn": "Magnetic card holder",
                        "sku": "S1",
                        "sellPrice": "1.20 -- 3.50",
                        "bigImage": "https://img/1.jpg",
                        "warehouseInventoryNum": 120,
                        "listedNum": 9,
                    }
                ]
            }
        ],
        "totalRecords": 1,
    },
}
EMPTY = {"code": 200, "data": {"content": []}}


class FakeResp:
    def __init__(self, payload, status=200):
        self._p = payload
        self.status_code = status

    def json(self):
        if isinstance(self._p, Exception):
            raise self._p
        return self._p


class FakeSession:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def request(self, method, url, params=None, json=None, headers=None, timeout=None):
        self.calls.append(
            {"method": method, "url": url, "params": params, "headers": headers}
        )
        return FakeResp(self.replies.pop(0))


def client(replies):
    session = FakeSession(replies)
    return cj.CJClient(api_key="k", session=session, sleep=lambda s: None), session


def test_search_authenticates_then_sends_the_token_and_filters():
    c, s = client([TOKEN_OK, LIST_OK, EMPTY])
    rows = c.search("card holder", country="US", pages=3)
    assert len(rows) == 1
    assert s.calls[1]["headers"] == {"CJ-Access-Token": "T1"}
    assert s.calls[1]["params"]["countryCode"] == "US"
    assert rows[0]["pid"] == "P1"
    assert (rows[0]["price_low"], rows[0]["price_high"]) == (1.2, 3.5)


def test_error_envelope_raises_with_the_code():
    c, _ = client([TOKEN_OK, {"code": 1600200, "message": "Too many requests"}])
    with pytest.raises(cj.CJError) as err:
        c.search("x")
    assert err.value.code == 1600200


def test_expired_token_is_refreshed_once():
    c, s = client(
        [
            TOKEN_OK,
            {"code": 1600001, "message": "invalid token"},
            {"code": 200, "data": {"accessToken": "T2"}},
            LIST_OK,
            EMPTY,
        ]
    )
    assert len(c.search("x", pages=2)) == 1
    assert s.calls[3]["headers"] == {"CJ-Access-Token": "T2"}


def test_a_second_auth_failure_is_not_retried_forever():
    bad = {"code": 1600001, "message": "invalid token"}
    c, _ = client([TOKEN_OK, bad, TOKEN_OK, bad])
    with pytest.raises(cj.CJError):
        c.search("x")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("12.5", (12.5, 12.5)),
        ("1.20 -- 3.50", (1.2, 3.5)),
        (4, (4.0, 4.0)),
        (None, (None, None)),
    ],
)
def test_parse_price(raw, expected):
    assert cj.parse_price(raw) == expected


def test_detail_normalizes_images_and_variants():
    detail = {
        "code": 200,
        "data": {
            "pid": "P1",
            "productNameEn": "Holder",
            "bigImage": "b.jpg",
            "productImageSet": ["i1.jpg", "i2.jpg"],
            "variants": [{"vid": "V1", "variantSku": "S1-A", "variantSellPrice": 2.5}],
        },
    }
    c, _ = client([TOKEN_OK, detail])
    d = c.detail("P1")
    assert d["images"] == ["b.jpg", "i1.jpg", "i2.jpg"]
    assert d["variants"][0]["vid"] == "V1"


def test_missing_key_is_a_clear_error(monkeypatch):
    monkeypatch.delenv("CJ_API_KEY", raising=False)
    with pytest.raises(cj.CJError, match="CJ_API_KEY"):
        cj.CJClient()


def test_raw_output_must_stay_under_data_private(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert cj.private_path("data/private/x.json").name == "x.json"
    with pytest.raises(SystemExit):
        cj.private_path("docs/x.json")


def test_a_non_json_response_is_a_clear_error():
    c, _ = client([TOKEN_OK, ValueError("no json")])
    with pytest.raises(cj.CJError, match="not JSON"):
        c.search("x")


def test_negative_prices_are_unusable():
    assert cj.parse_price("-5") == (None, None)
    assert cj.parse_price(" -3.20") == (None, None)


def test_malformed_shapes_do_not_crash_search():
    odd = {"code": 200, "data": {"content": ["junk", {"productList": "nope"}, 7]}}
    c, _ = client([TOKEN_OK, odd])
    assert c.search("x") == []


def test_detail_ignores_junk_variants_and_images():
    d = {
        "code": 200,
        "data": {
            "pid": "P",
            "bigImage": None,
            "productImageSet": [None, 3, "ok.jpg"],
            "variants": ["x", {"vid": "V"}],
        },
    }
    c, _ = client([TOKEN_OK, d])
    out = c.detail("P")
    assert out["images"] == ["ok.jpg"]
    assert [v["vid"] for v in out["variants"]] == ["V"]


# Shapes below follow live CJ replies seen on 2026-11-04 (values are made up).


def test_detail_parses_live_string_numbers_and_json_list_fields():
    detail = {
        "code": 200,
        "data": {
            "pid": "P1",
            "productWeight": "30.00",
            "packingWeight": "45.00",
            "suggestSellPrice": "10.29 - 11.94",
            "materialNameEn": '["Leather"]',
            "packingNameEn": '["Plastic bags"]',
            "variants": [
                {
                    "vid": "V1",
                    "variantSellPrice": 1.36,
                    "variantWeight": 45.0,
                    "variantLength": 107,
                    "variantWidth": 82,
                    "variantHeight": 5,
                    "inventories": None,
                }
            ],
        },
    }
    c, _ = client([TOKEN_OK, detail])
    d = c.detail("P1")
    assert d["weight_g"] == 30.0 and d["packing_weight_g"] == 45.0
    assert (d["suggested_price_low"], d["suggested_price_high"]) == (10.29, 11.94)
    assert d["materials"] == ["Leather"] and d["packing"] == ["Plastic bags"]
    assert d["variants"][0]["dims_mm"] == [107, 82, 5]
    assert d["variants"][0]["price"] == 1.36


def test_stock_is_keyed_by_warehouse_country():
    reply = {
        "code": 200,
        "data": {
            "inventories": [
                {
                    "countryCode": "CN",
                    "totalInventoryNum": 900,
                    "cjInventoryNum": 0,
                    "factoryInventoryNum": 900,
                },
                {
                    "countryCode": "US",
                    "totalInventoryNum": 28,
                    "cjInventoryNum": 28,
                    "factoryInventoryNum": 0,
                },
                "junk",
            ]
        },
    }
    c, session = client([TOKEN_OK, reply])
    s = c.stock("P1")
    assert s["US"] == {"total": 28, "cj": 28, "factory": 0}
    assert set(s) == {"CN", "US"}
    assert session.calls[-1]["url"].endswith("/product/stock/getInventoryByPid")


def test_freight_quotes_are_parsed_and_sorted_cheapest_first():
    reply = {
        "code": 200,
        "data": [
            {"logisticName": "B", "logisticPrice": 7.1, "logisticAging": "2-5"},
            {"logisticName": "A", "logisticPrice": 5.18, "logisticAging": "3-8"},
            {"logisticName": "C", "logisticPrice": None, "logisticAging": None},
        ],
    }
    c, _ = client([TOKEN_OK, reply])
    q = c.freight("V1", zip_code="10001")
    assert [x["carrier"] for x in q] == ["A", "B", "C"]
    assert (q[0]["days_low"], q[0]["days_high"]) == (3, 8)
    assert q[2]["days_low"] is None


def test_search_without_keyword_lists_the_country_catalogue():
    c, session = client([TOKEN_OK, LIST_OK])
    rows = c.search(None, country="US")
    params = session.calls[-1]["params"]
    assert "keyWord" not in params and params["countryCode"] == "US"
    assert rows[0]["verified_inventory"] is None


def test_odd_numeric_and_list_values_do_not_crash():
    assert cj._num("abc") is None and cj._num("2.5") == 2.5
    assert cj._json_list("Plastic") == ["Plastic"]
    assert cj._json_list(None) == [] and cj._json_list(["a"]) == ["a"]
