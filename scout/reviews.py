"""Review counts shown on a store's own product pages (decision 0014).

Most review apps (Judge.me, Yotpo, Okendo, Loox, Stamped) render their counts in the
browser, so a plain fetch often misses them. This module reads the plain page first
and, only when that finds nothing, renders it with Crawl4AI (a maintained,
Apache-2.0 headless-browser crawler), pinned in requirements-crawl.txt.

Rules kept (CLAUDE.md principles 6 and 10):
- robots.txt is read for every URL; Crawl4AI also checks it (check_robots_txt=True).
- One fixed User-Agent naming the project. Crawl4AI's stealth mode is ON by default
  (owner decision 2026-11-05, decisions 0014 and 0015); SCOUT_CRAWL_STEALTH=0 turns it off.
- A bot check or challenge page (Cloudflare, captcha, 403/429/430) ends the attempt
  and is recorded as "blocked". Nothing is done to get around it.
- Only counts and the review app's name are kept, never review text.
- Never pointed at sites whose terms forbid automated collection (Trustpilot, Meta
  Ad Library, TikTok Creative Center): store product pages only.

    python -m scout.reviews --max-stores 30             # study set and pool first
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time

from scout import store, stores, webmeta

PATTERNS = {
    "judgeme_badge": re.compile(r'data-number-of-reviews="(\d+)"'),
    "jsonld_reviewcount": re.compile(r'"reviewCount"\s*:\s*"?(\d+)'),
    "jsonld_ratingcount": re.compile(r'"ratingCount"\s*:\s*"?(\d+)'),
    "visible_text": re.compile(r"(\d[\d,]*)\s+(?:Reviews|reviews|Ratings|ratings)\b"),
}
MAX_PLAUSIBLE = 5_000_000
# Crawl4AI stealth (hides headless-browser traces). On by owner decision
# 2026-11-05; set SCOUT_CRAWL_STEALTH=0 to render without it.
STEALTH = os.environ.get("SCOUT_CRAWL_STEALTH", "1") != "0"
BLOCK_MARKERS = re.compile(
    r"cf-challenge|challenge-platform|captcha|verify you are human|access denied", re.I
)
REVIEW_APPS = {
    "judge.me": "judge.me",
    "yotpo": "yotpo",
    "okendo": "okendo",
    "loox.io": "loox",
    "stamped.io": "stamped",
    "junip": "junip",
    "reviews.io": "reviews.io",
}


def review_counts(html: str) -> dict[str, int]:
    """Largest plausible count found by each pattern. Pure."""
    out = {}
    for name, pat in PATTERNS.items():
        vals = []
        for v in pat.findall(html or ""):
            try:
                n = int(v.replace(",", ""))
            except ValueError:
                continue
            if 0 < n < MAX_PLAUSIBLE:
                vals.append(n)
        if vals:
            out[name] = max(vals)
    return out


def best_count(found: dict[str, int]) -> int | None:
    """Prefer structured data, then the app's own badge, then visible text."""
    for key in (
        "jsonld_reviewcount",
        "jsonld_ratingcount",
        "judgeme_badge",
        "visible_text",
    ):
        if key in found:
            return found[key]
    return None


def review_app(html: str) -> str | None:
    low = (html or "").lower()
    return next((name for needle, name in REVIEW_APPS.items() if needle in low), None)


def is_blocked(status: int | None, html: str) -> bool:
    return status in (403, 429, 430) or bool(BLOCK_MARKERS.search((html or "")[:20000]))


def _render(urls: list[str]) -> dict[str, tuple[int | None, str, str]]:
    """Render pages with Crawl4AI (optional dependency). Returns url -> (status, html, error)."""
    import asyncio

    from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

    browser = BrowserConfig(
        headless=True, user_agent=webmeta.UA, enable_stealth=STEALTH, verbose=False
    )
    run = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="domcontentloaded",
        delay_before_return_html=4.0,
        page_timeout=45000,
        check_robots_txt=True,
    )

    async def go():
        out = {}
        async with AsyncWebCrawler(config=browser) as crawler:
            for u in urls:
                r = await crawler.arun(url=u, config=run)
                out[u] = (
                    r.status_code,
                    r.html or "",
                    "" if r.success else str(r.error_message)[:160],
                )
                await asyncio.sleep(1.0)
        return out

    return asyncio.run(go())


def product_url(
    session, domain: str, host: str | None = None
) -> tuple[str | None, str]:
    """First product page of a store, if robots.txt allows the feed and the page."""
    from urllib import robotparser

    base = f"https://{host or domain}"
    rp = robotparser.RobotFileParser()
    r = session.get(base + "/robots.txt", timeout=20)
    rp.parse(r.text.splitlines() if r.ok else [])
    feed = base + "/products.json?limit=5"
    if not rp.can_fetch(webmeta.UA, feed):
        return None, "feed disallowed"
    prods = session.get(feed, timeout=20).json().get("products") or []
    if not prods:
        return None, "no products"
    url = f"{base}/products/{prods[0]['handle']}"
    return (url, "") if rp.can_fetch(webmeta.UA, url) else (None, "page disallowed")


def run(domains: list[str], render: bool = True, pause: float = 1.0) -> dict:
    metas = stores.latest_good(stores._all_rows("web_meta"))
    s = webmeta._session()
    rows, need_render = [], {}
    for d in domains:
        row = {"domain": d}
        try:
            url, why = product_url(s, d, (metas.get(d) or {}).get("final_host"))
            if not url:
                row.update(status=why)
                rows.append(row)
                continue
            time.sleep(pause)
            resp = s.get(url, timeout=30)
            html = resp.text
            if is_blocked(resp.status_code, html):
                row.update(status="blocked", method="static")
            else:
                found = review_counts(html)
                row.update(
                    status="ok",
                    method="static",
                    url_path=url.split("/products/")[-1][:80],
                    review_app=review_app(html),
                    counts=found,
                    review_count=best_count(found),
                )
                if row["review_count"] is None and render:
                    need_render[url] = row
        except Exception as exc:
            row.update(status="error", error=type(exc).__name__)
        rows.append(row)
    if need_render:
        try:
            rendered = _render(list(need_render))
        except ImportError:
            rendered = {}
            print(
                "crawl4ai not installed: skipping render (pip install -r requirements-crawl.txt)",
                file=sys.stderr,
            )
        for url, (status, html, err) in rendered.items():
            row = need_render[url]
            if err or is_blocked(status, html):
                row.update(
                    render_status="blocked" if is_blocked(status, html) else "failed",
                    render_error=err[:120],
                )
                continue
            found = review_counts(html)
            row.update(
                method="rendered",
                counts=found,
                review_count=best_count(found),
                review_app=row.get("review_app") or review_app(html),
            )
    runid = store.record_run(
        "web_reviews",
        rows,
        source="store_product_pages",
        trust="data",
        params={"n": len(rows), "render": render},
        note="review counts shown on one product page per store; robots.txt respected; "
        f"project UA, stealth {'on' if STEALTH else 'off'}; counts only, no review text",
    )
    found = sum(1 for r in rows if r.get("review_count"))
    print(
        f"reviews: {len(rows)} stores, count found for {found}, rendered {len(need_render)}",
        file=sys.stderr,
    )
    return {"web_reviews": (runid, len(rows))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Review counts on store product pages")
    ap.add_argument("--domains-file", help="one domain per line")
    ap.add_argument("--max-stores", type=int, default=30)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args(argv)
    if a.domains_file:
        doms = open(a.domains_file, encoding="utf-8").read().split()
    else:
        deep = stores.latest_good(stores._all_rows("web_store_deep"))
        doms = [d for d, _ in sorted(deep.items(), key=lambda kv: kv[1]["tranco_rank"])]
    out = run(doms[: a.max_stores], render=not a.no_render)
    for k, (rid, n) in out.items():
        print(f"{k}: run {rid}, {n} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
