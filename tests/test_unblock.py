"""Tier escalation, budget cap and block detection of scout.unblock (no network)."""

import pytest

from scout import unblock as ub


class Resp:
    def __init__(self, status=200, text="<html>ok</html>" * 30, headers=None):
        self.status_code, self.text, self.headers = status, text, headers or {}
        self.ok = status < 400


class Session:
    """Answers robots.txt with no rules, then serves queued responses per host."""

    def __init__(self, plain=None, zen=None, bee=None):
        self.queues = {
            "plain": list(plain or []),
            "zen": list(zen or []),
            "bee": list(bee or []),
        }
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, headers=None, timeout=None):
        if url.endswith("/robots.txt"):
            return Resp(404, "")
        lane = "zen" if "zenrows" in url else "bee" if "scrapingbee" in url else "plain"
        self.calls.append((lane, params or {}, headers or {}))
        return self.queues[lane].pop(0)


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(ub, "USAGE_FILE", str(tmp_path / "u.json"))
    monkeypatch.setattr(ub, "DAILY_CREDIT_CAP", 1000)
    keys = {
        "ZENROWS_API_KEY": "zk",  # pragma: allowlist secret
        "SCRAPINGBEE_API_KEY": "bk",  # pragma: allowlist secret
    }
    monkeypatch.setattr(ub, "_key", lambda name: keys.get(name))


def test_plain_success_spends_nothing():
    s = Session(plain=[Resp()])
    r = ub.fetch("https://shop.example/products.json", session=s)
    assert r["tier"] == "plain" and r["cost"] == 0 and ub.credits_used() == 0


def test_block_escalates_to_zenrows_and_records_cost():
    s = Session(
        plain=[Resp(403, "Access denied")], zen=[Resp(headers={"X-Request-Cost": "10"})]
    )
    r = ub.fetch("https://shop.example/", session=s)
    assert r["tier"] == "zenrows" and r["cost"] == 10 and ub.credits_used() == 10
    params = s.calls[1][1]
    assert params["mode"] == "auto"
    assert params["apikey"] == "zk"  # pragma: allowlist secret


def test_challenge_page_with_200_counts_as_blocked():
    s = Session(
        plain=[Resp(200, "<title>Just a moment...</title> cf-challenge")],
        zen=[Resp(403, "")],
        bee=[Resp(headers={"Spb-cost": "25"})],
    )
    r = ub.fetch("https://shop.example/", session=s)
    assert r["tier"] == "scrapingbee"
    assert s.calls[2][2]["Authorization"] == "Bearer bk"  # key in header, not URL
    assert s.calls[2][1].get("premium_proxy") == "true"


def test_scrapingbee_stealth_is_last_resort():
    s = Session(plain=[Resp(429)], zen=[Resp(403)], bee=[Resp(403), Resp()])
    r = ub.fetch("https://shop.example/", session=s)
    assert r["tier"] == "scrapingbee_stealth"
    assert s.calls[-1][1].get("stealth_proxy") == "true"
    assert r["cost"] == ub.EST_COST["scrapingbee_stealth"]  # no header: estimate


def test_daily_cap_stops_paid_tiers():
    ub._spend(995)
    s = Session(plain=[Resp(403)])
    r = ub.fetch("https://shop.example/", session=s)
    assert r["tier"] is None and r["error"] == "all_tiers_failed"
    assert any("daily_cap" in a for a in r["attempts"])
    assert [c[0] for c in s.calls] == ["plain"]


def test_js_pages_skip_the_plain_tier():
    s = Session(zen=[Resp()])
    r = ub.fetch("https://shop.example/", session=s, js=True)
    assert r["tier"] == "zenrows" and s.calls[0][1]["js_render"] == "true"


def test_max_tier_plain_never_spends(monkeypatch):
    s = Session(plain=[Resp(403)])
    r = ub.fetch("https://shop.example/", session=s, max_tier="plain")
    assert r["tier"] is None and len(s.calls) == 1


def test_no_keys_means_plain_only(monkeypatch):
    monkeypatch.setattr(ub, "_key", lambda name: None)
    s = Session(plain=[Resp(403)])
    r = ub.fetch("https://shop.example/", session=s)
    assert r["tier"] is None and [c[0] for c in s.calls] == ["plain"]


def test_failed_paid_call_is_not_billed():
    s = Session(
        plain=[Resp(403)],
        zen=[Resp(500, "", {"X-Request-Cost": "25"})],
        bee=[Resp(), Resp()],
    )
    r = ub.fetch("https://shop.example/", session=s)
    assert r["tier"] == "scrapingbee"
    assert ub.credits_used() == r["cost"]  # the 500 cost nothing


def test_is_blocked():
    assert ub.is_blocked(403, "")
    assert ub.is_blocked(200, "Please verify you are human")
    assert not ub.is_blocked(200, "<html>products</html>")
