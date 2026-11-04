"""Shopify detection by response evidence (fixtures only, no network)."""

from scout import shopify_detect as sd

PAGE = (
    '<html><head><link href="https://cdn.shopify.com/s/files/1/x.css">'
    "<script>Shopify.shop = 'a.myshopify.com';</script></head></html>"
)


def test_strong_header_alone():
    ev = sd.shopify_evidence(200, {"X-ShopId": "123"}, "")
    assert ev == ["hdr:x-shopid"]
    assert sd.is_shopify(ev)


def test_header_names_case_insensitive_and_values():
    h = {
        "X-Sorting-Hat-ShopId": "1",
        "X-Shopify-Stage": "production",
        "Powered-By": "Shopify",
    }
    ev = sd.shopify_evidence(200, h, "")
    assert set(ev) == {
        "hdr:x-sorting-hat-shopid",
        "hdr:x-shopify-stage",
        "hdr:powered-by",
    }


def test_powered_by_other_is_not_shopify():
    ev = sd.shopify_evidence(200, {"powered-by": "Express"}, "")
    assert ev == [] and not sd.is_shopify(ev)


def test_one_html_marker_not_enough():
    ev = sd.shopify_evidence(200, {}, '<img src="https://cdn.shopify.com/a.png">')
    assert ev == ["html:cdn.shopify.com"]
    assert not sd.is_shopify(ev)


def test_two_html_markers_enough():
    ev = sd.shopify_evidence(200, {}, PAGE)
    assert "html:cdn.shopify.com" in ev and "html:shopify.shop =" in ev
    assert sd.is_shopify(ev)


def test_server_timing_is_weak():
    ev = sd.shopify_evidence(200, {"server-timing": "shopify;dur=1"}, "")
    assert ev == ["hdr:server-timing"] and not sd.is_shopify(ev)
    ev = sd.shopify_evidence(
        200, {"server-timing": "x;desc=Shopify"}, "/cdn/shop/files/a.jpg"
    )
    assert sd.is_shopify(ev)


def test_html_beyond_limit_ignored():
    html = "x" * sd.HTML_LIMIT + PAGE
    assert sd.shopify_evidence(200, {}, html) == []


def test_empty():
    assert sd.shopify_evidence(200, {}, "") == []
    assert not sd.is_shopify([])


def test_blocked():
    assert sd.is_blocked(403, "")
    assert sd.is_blocked(429, "")
    assert sd.is_blocked(430, "")
    assert sd.is_blocked(503, "<div id='cf-chl-widget'>")
    assert not sd.is_blocked(200, "hello captcha in a blog post")
    assert not sd.is_blocked(404, "not found")


class _Resp:
    def __init__(self, status=200, text="", url="https://a.com/", headers=None):
        self.status_code, self.text, self.url = status, text, url
        self.headers = headers or {}
        self.encoding = "utf-8"
        self.raw = self
        self._b = text.encode()

    def read(self, n, decode_content=True):
        return self._b[:n]

    def close(self):
        pass


class _Sess:
    def __init__(self, robots, home):
        self.robots, self.home, self.calls = robots, home, []

    def get(self, url, **kw):
        self.calls.append(url)
        return self.robots if url.endswith("/robots.txt") else self.home


def test_probe_found():
    s = _Sess(_Resp(404), _Resp(200, PAGE, "https://www.a.com/", {"x-shopid": "1"}))
    row = sd.probe("a.com", s)
    assert row["outcome"] == "answered" and row["is_shopify"]
    assert row["final_host"] == "www.a.com"
    assert s.calls == ["https://a.com/robots.txt", "https://a.com/"]


def test_probe_robots_disallow_no_homepage_fetch():
    s = _Sess(_Resp(200, "User-agent: *\nDisallow: /"), _Resp(200))
    row = sd.probe("a.com", s)
    assert row["outcome"] == "robots_disallow"
    assert s.calls == ["https://a.com/robots.txt"]


def test_probe_blocked_no_retry():
    s = _Sess(_Resp(404), _Resp(403))
    row = sd.probe("a.com", s)
    assert row["outcome"] == "blocked" and not row["is_shopify"]
    assert s.calls.count("https://a.com/") == 1
