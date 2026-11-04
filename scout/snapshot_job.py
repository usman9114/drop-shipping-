"""Weekly snapshots of the top stores' public product feeds (decision 0011).

Each run fetches /products.json for the best profiled US stores and records,
per product, only ids, dates, prices and availability (`scout.snapshots.compact`).
It also reads the public review count of three fixed products per store, so review
velocity can be measured week to week. Two lake datasets, private:

    web_snapshot_stores    one row per store per run: status, pages, counts, reviews
    web_snapshot_products  one row per product per run (compact form)

A store is **complete** only if every page came back, the page cap was not hit and
the count is close to the store's published count. Otherwise it is `partial`,
`failed` or `blocked`, and the diff reports no removals (and no new products when
the earlier snapshot was partial). 403 or 430 stops a store for the run: no
proxies, no browser impersonation. A Retry-After longer than the budget skips the
store instead of holding a worker. robots.txt is read first for every store.

    python -m scout.snapshot_job run  --max-stores 20 --workers 4   # small first
    python -m scout.snapshot_job diff                               # last two runs
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from urllib import robotparser

from scout import snapshots, store, stores, webmeta

PAGE_SIZE = 250
MAX_PAGES = 40  # 10,000 products; a bigger store is recorded as partial
COMPLETE_RATIO = 0.9  # fetched / published count needed to call a feed complete
RETRY_BUDGET_S = 60.0  # longer Retry-After than this: skip the store this run
REVIEW_SAMPLE = 3
REVIEW_APPS = {
    "judge.me": "judge.me",
    "loox.io": "loox",
    "okendo": "okendo",
    "yotpo": "yotpo",
    "stamped.io": "stamped",
    "junip": "junip",
    "reviews.io": "reviews.io",
}


def feed_status(
    pages: int, truncated: bool, products: int, expected: int | None, failed: bool
) -> tuple[str, str]:
    """(status, reason) for one fetched feed. Pure; decides whether a diff may
    report removals."""
    if failed:
        return "partial" if products else "failed", "a page failed"
    if truncated:
        return "partial", f"page cap of {MAX_PAGES} reached"
    if expected and products < COMPLETE_RATIO * expected:
        return "partial", f"{products} fetched of {expected} published"
    return "complete", ""


def review_app(html: str) -> str | None:
    low = html.lower()
    return next((name for needle, name in REVIEW_APPS.items() if needle in low), None)


def fetch_feed(session, base: str, rp, expected: int | None, sleep=time.sleep) -> dict:
    """Fetch the whole feed politely. Returns {status, reason, pages, products}."""
    products: list[dict] = []
    pages, failed, truncated, http = 0, False, False, None
    for page in range(1, MAX_PAGES + 1):
        url = f"{base}/products.json?limit={PAGE_SIZE}&page={page}"
        if not rp.can_fetch(webmeta.UA, url):
            return {
                "status": "failed",
                "reason": "robots.txt disallows the feed",
                "pages": 0,
                "products": [],
            }
        resp = None
        for attempt in range(3):
            resp = session.get(url, timeout=30)
            http = resp.status_code
            if http in (403, 430):  # blocked: stop, never work around it
                return {
                    "status": "blocked",
                    "reason": f"HTTP {http}",
                    "pages": pages,
                    "products": products,
                }
            if http != 429:
                break
            wait = snapshots.next_delay(
                attempt,
                snapshots.parse_retry_after(
                    resp.headers.get("Retry-After"), time.time()
                ),
            )
            if wait > RETRY_BUDGET_S:
                return {
                    "status": "partial" if products else "failed",
                    "reason": f"Retry-After {wait:.0f}s over budget",
                    "pages": pages,
                    "products": products,
                }
            sleep(wait)
        if resp is None or not resp.ok:
            failed = True
            break
        got = resp.json().get("products") or []
        pages += 1
        products += got
        if len(got) < PAGE_SIZE:
            break
        if page == MAX_PAGES:
            truncated = True
    status, reason = feed_status(pages, truncated, len(products), expected, failed)
    return {
        "status": status,
        "reason": reason or (f"HTTP {http}" if failed else ""),
        "pages": pages,
        "products": products,
    }


def review_sample(
    session, base: str, rp, products: list[dict], sleep=time.sleep
) -> dict:
    """Review count over the three lowest-id products (a stable set week to week)."""
    picks = sorted(
        (p for p in products if isinstance(p.get("id"), int) and p.get("handle")),
        key=lambda p: p["id"],
    )[:REVIEW_SAMPLE]
    total, seen, app = 0, 0, None
    for p in picks:
        url = f"{base}/products/{p['handle']}"
        if not rp.can_fetch(webmeta.UA, url):
            continue
        sleep(1.0)
        html = session.get(url, timeout=30).text
        app = app or review_app(html)
        count, _ = webmeta.aggregate_rating(webmeta.jsonld(html))
        if count is not None:
            total += count
            seen += 1
    return {
        "review_count_sample": total if seen else None,
        "review_products_with_count": seen,
        "review_app": app,
        "review_product_ids": [p["id"] for p in picks],
    }


def snapshot_store(meta: dict, today: str) -> tuple[dict, dict[int, dict]]:
    """Snapshot one store: (store row, compact products)."""
    d = meta["domain"]
    base = f"https://{meta.get('final_host') or d}"
    row = {
        "domain": d,
        "snapshot_date": today,
        "tranco_rank": meta.get("tranco_rank"),
        "published_products": meta.get("published_products"),
    }
    s = webmeta._session()
    try:
        rp = robotparser.RobotFileParser()
        r = s.get(base + "/robots.txt", timeout=20)
        rp.parse(r.text.splitlines() if r.ok else [])
        feed = fetch_feed(s, base, rp, meta.get("published_products"))
        compact = snapshots.compact(feed["products"])
        row.update(
            status=feed["status"],
            reason=feed["reason"],
            pages=feed["pages"],
            products=len(compact),
        )
        if feed["status"] in ("complete", "partial") and feed["products"]:
            row.update(review_sample(s, base, rp, feed["products"]))
        return row, compact
    except Exception as exc:
        row.update(status="failed", reason=type(exc).__name__, pages=0, products=0)
        return row, {}


def run(max_stores: int, workers: int) -> dict:
    from concurrent.futures import ThreadPoolExecutor

    deep = stores.latest_good(stores._all_rows("web_store_deep"))
    metas = stores.latest_good(stores._all_rows("web_meta"))
    targets = []
    for d, r in sorted(deep.items(), key=lambda kv: kv[1]["tranco_rank"]):
        m = metas.get(d)
        if m and stores.us_store(m):
            targets.append({**m, "tranco_rank": r["tranco_rank"]})
    targets = targets[:max_stores]
    today = datetime.now(timezone.utc).date().isoformat()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda m: snapshot_store(m, today), targets))
    store_rows = [r for r, _ in results]
    prod_rows = [
        {"domain": r["domain"], "snapshot_date": today, "product_id": pid, **c}
        for r, comp in results
        for pid, c in comp.items()
    ]
    run_s = store.record_run(
        "web_snapshot_stores",
        store_rows,
        source="store_feeds",
        trust="data",
        params={"n": len(targets)},
        note="status per store; robots.txt respected; private",
    )
    run_p = store.record_run(
        "web_snapshot_products",
        prod_rows,
        source="store_feeds",
        trust="data",
        params={"n": len(targets)},
        note="ids, dates, prices, availability only; private",
    )
    by = {}
    for r in store_rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print(
        f"snapshot: {len(store_rows)} stores {by}, {len(prod_rows)} products",
        file=sys.stderr,
    )
    return {
        "web_snapshot_stores": (run_s, len(store_rows)),
        "web_snapshot_products": (run_p, len(prod_rows)),
    }


def _runs_by_date(rows: list[dict]) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    for r in rows:
        out.setdefault(r["snapshot_date"], {})[r["domain"]] = r
    return out


def diff_runs() -> list[dict]:
    """Diff the last two snapshot dates per store. Returns one summary per store."""
    s_rows = stores._all_rows("web_snapshot_stores")
    p_rows = stores._all_rows("web_snapshot_products")
    dates = sorted({r["snapshot_date"] for r in s_rows})
    if len(dates) < 2:
        print("need two snapshot dates; have", dates, file=sys.stderr)
        return []
    d_old, d_new = dates[-2], dates[-1]
    status = _runs_by_date(s_rows)
    prods: dict[tuple[str, str], dict[int, dict]] = {}
    for r in p_rows:
        key = (r["snapshot_date"], r["domain"])
        prods.setdefault(key, {})[r["product_id"]] = {
            k: r[k] for k in ("created", "updated", "min_price", "variants")
        }
    out = []
    for dom, new_s in status[d_new].items():
        old_s = status[d_old].get(dom)
        if not old_s:
            continue
        res = snapshots.diff(
            {pid: _intkeys(c) for pid, c in prods.get((d_old, dom), {}).items()},
            {pid: _intkeys(c) for pid, c in prods.get((d_new, dom), {}).items()},
            complete=new_s["status"] == "complete",
            old_complete=old_s["status"] == "complete",
        )
        d_reviews = None
        a, b = old_s.get("review_count_sample"), new_s.get("review_count_sample")
        if (
            a is not None
            and b is not None
            and old_s.get("review_app") == new_s.get("review_app")
        ):
            d_reviews = b - a
        out.append(
            {
                "domain": dom,
                "old": d_old,
                "new": d_new,
                **res["counts"],
                "warnings": res["warnings"],
                "review_delta": d_reviews,
            }
        )
    return out


def _intkeys(c: dict) -> dict:
    """JSON turns variant ids into strings; restore ints for the diff."""
    return {**c, "variants": {int(k): v for k, v in (c.get("variants") or {}).items()}}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Weekly store feed snapshots")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--max-stores", type=int, default=20)
    r.add_argument("--workers", type=int, default=4)
    sub.add_parser("diff")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        for k, (rid, n) in run(a.max_stores, a.workers).items():
            print(f"{k}: run {rid}, {n} rows", file=sys.stderr)
    else:
        for row in diff_runs():
            print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
