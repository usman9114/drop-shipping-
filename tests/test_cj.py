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
    def __init__(self, payload):
        self._p = payload

    def json(self):
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
