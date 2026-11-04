"""Snapshot job: completeness gate and polite fetching (fake responses, no network)."""

from urllib import robotparser

from scout import snapshot_job as job


class Resp:
    def __init__(self, status=200, products=None, headers=None, text=""):
        self.status_code = status
        self.ok = status < 400
        self.headers = headers or {}
        self._products = products or []
        self.text = text

    def json(self):
        return {"products": self._products}


class Session:
    """Returns queued responses per page number found in the URL."""

    def __init__(self, pages):
        self.pages = pages  # {page: [Resp, ...]}
        self.calls = []

    def get(self, url, timeout=30):
        self.calls.append(url)
        page = int(url.split("page=")[1]) if "page=" in url else 0
        queue = self.pages.get(page, [Resp(200, [])])
        return queue.pop(0) if len(queue) > 1 else queue[0]


def rp(text=""):
    r = robotparser.RobotFileParser()
    r.parse(text.splitlines())
    return r


def prods(n, start=1):
    return [
        {"id": start + i, "handle": f"p{start + i}", "variants": []} for i in range(n)
    ]


def test_feed_status_rules():
    assert job.feed_status(2, False, 400, 410, False) == ("complete", "")
    assert job.feed_status(2, False, 100, 400, False)[0] == "partial"  # too few
    assert job.feed_status(40, True, 10000, 20000, False)[0] == "partial"  # cap hit
    assert job.feed_status(1, False, 250, None, True)[0] == "partial"  # a page failed
    assert job.feed_status(0, False, 0, None, True)[0] == "failed"


def test_complete_feed_across_two_pages():
    s = Session({1: [Resp(200, prods(250))], 2: [Resp(200, prods(40, 251))]})
    out = job.fetch_feed(s, "https://x.com", rp(), 290, sleep=lambda _: None)
    assert (
        out["status"] == "complete"
        and len(out["products"]) == 290
        and out["pages"] == 2
    )


def test_failure_mid_catalogue_is_partial_not_complete():
    s = Session({1: [Resp(200, prods(250))], 2: [Resp(500)]})
    out = job.fetch_feed(s, "https://x.com", rp(), 500, sleep=lambda _: None)
    assert out["status"] == "partial" and len(out["products"]) == 250


def test_430_and_403_block_the_store_and_stop():
    for code in (430, 403):
        s = Session({1: [Resp(200, prods(250))], 2: [Resp(code)]})
        out = job.fetch_feed(s, "https://x.com", rp(), 500, sleep=lambda _: None)
        assert out["status"] == "blocked" and out["reason"] == f"HTTP {code}"
        assert len(s.calls) == 2  # no retry, no workaround


def test_long_retry_after_skips_the_store():
    s = Session({1: [Resp(429, headers={"Retry-After": "3600"})]})
    out = job.fetch_feed(s, "https://x.com", rp(), 100, sleep=lambda _: None)
    assert out["status"] == "failed" and "over budget" in out["reason"]


def test_short_retry_after_is_honoured_then_succeeds():
    waits = []
    s = Session({1: [Resp(429, headers={"Retry-After": "7"}), Resp(200, prods(3))]})
    out = job.fetch_feed(s, "https://x.com", rp(), 3, sleep=waits.append)
    assert out["status"] == "complete" and waits and waits[0] >= 7


def test_robots_disallow_stops_before_fetching():
    s = Session({1: [Resp(200, prods(3))]})
    out = job.fetch_feed(
        s,
        "https://x.com",
        rp("User-agent: *\nDisallow: /products.json"),
        3,
        sleep=lambda _: None,
    )
    assert out["status"] == "failed" and s.calls == []


def test_page_cap_marks_partial(monkeypatch):
    monkeypatch.setattr(job, "MAX_PAGES", 2)
    s = Session({1: [Resp(200, prods(250))], 2: [Resp(200, prods(250, 251))]})
    out = job.fetch_feed(s, "https://x.com", rp(), None, sleep=lambda _: None)
    assert out["status"] == "partial" and "page cap" in out["reason"]


def test_review_sample_uses_the_three_lowest_ids_and_names_the_app():
    html = (
        '<script src="https://cdn.judge.me/x.js"></script><script type="application/ld+json">'
        '{"aggregateRating":{"reviewCount":"12","ratingValue":"4.7"}}</script>'
    )

    class PS(Session):
        def get(self, url, timeout=30):
            self.calls.append(url)
            return Resp(200, text=html)

    products = prods(10)[::-1]  # unsorted on purpose
    s = PS({})
    out = job.review_sample(s, "https://x.com", rp(), products, sleep=lambda _: None)
    assert out["review_product_ids"] == [1, 2, 3]
    assert out["review_count_sample"] == 36 and out["review_app"] == "judge.me"


def _store_row(date, domain, status, reviews=None, app="judge.me"):
    return {
        "domain": domain,
        "snapshot_date": date,
        "status": status,
        "review_count_sample": reviews,
        "review_app": app,
    }


def _prod_row(date, domain, pid, price, available=True):
    return {
        "domain": domain,
        "snapshot_date": date,
        "product_id": pid,
        "created": "2026-01-01",
        "updated": "2026-01-02",
        "min_price": price,
        "variants": {str(pid * 10): {"price": price, "available": available}},
    }


def test_diff_runs_uses_completeness_flags_and_review_delta(monkeypatch):
    rows = {
        "web_snapshot_stores": [
            _store_row("2026-11-04", "a.com", "complete", 10),
            _store_row("2026-11-11", "a.com", "partial", 14),
            _store_row("2026-11-04", "b.com", "complete", 5, "okendo"),
            _store_row("2026-11-11", "b.com", "complete", 9, "yotpo"),
        ],
        "web_snapshot_products": [
            _prod_row("2026-11-04", "a.com", 1, 10.0),
            _prod_row("2026-11-04", "a.com", 2, 20.0),
            _prod_row("2026-11-11", "a.com", 1, 12.0, available=False),
            _prod_row("2026-11-11", "a.com", 3, 5.0),
        ],
    }
    monkeypatch.setattr(job.stores, "_all_rows", lambda ds: rows.get(ds, []))
    out = {r["domain"]: r for r in job.diff_runs()}
    a = out["a.com"]
    assert a["removed_count"] == 0  # new snapshot partial: no removals reported
    assert (
        a["new_count"] == 1
        and a["repriced_count"] == 1
        and a["went_unavailable_count"] == 1
    )
    assert a["review_delta"] == 4
    assert out["b.com"]["review_delta"] is None  # review app changed: not comparable
