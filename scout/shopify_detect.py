"""Detect Shopify stores from a homepage response, whatever DNS or CDN sits in front.

Discovery by DNS (apex A record in 23.227.38.0/24) misses stores behind a custom
CDN or proxy. These signals survive a proxy because Shopify's origin adds them.

Decision rule (`is_shopify`): at least ONE strong header, OR at least TWO weak
markers. Strong headers are Shopify-only names or values: x-shopid,
x-sorting-hat-shopid, x-shopify-stage, powered-by: Shopify. Weak markers are
the server-timing header mentioning shopify and the HTML strings
cdn.shopify.com, `Shopify.shop =`, shopify-features, /cdn/shop/ (any site can
link to Shopify's CDN, so one HTML hit alone is not enough). The rule is
`[unverified]` against a hand-checked sample until the pilot report says otherwise.

`probe` respects robots.txt, fetches the homepage once, and never retries around
403/429/430 or a captcha page (recorded as `blocked`).
"""

from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlparse

from scout.webmeta import UA

HTML_LIMIT = 50_000
TIMEOUT = 20
STRONG_HEADERS = ("x-shopid", "x-sorting-hat-shopid", "x-shopify-stage")
HTML_MARKERS = ("cdn.shopify.com", "shopify.shop =", "shopify-features", "/cdn/shop/")
BLOCK_STATUS = {403, 429, 430}
CAPTCHA_WORDS = ("captcha", "cf-chl", "g-recaptcha", "hcaptcha", "challenge-platform")


def shopify_evidence(status: int, headers: dict, html_head: str) -> list[str]:
    """Signals found, as 'hdr:<name>', 'hdr:server-timing', 'html:<marker>'."""
    h = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    ev: list[str] = []
    for name in STRONG_HEADERS:
        if name in h:
            ev.append(f"hdr:{name}")
    if "shopify" in h.get("powered-by", "").lower():
        ev.append("hdr:powered-by")
    if "shopify" in h.get("server-timing", "").lower():
        ev.append("hdr:server-timing")
    low = (html_head or "")[:HTML_LIMIT].lower()
    for m in HTML_MARKERS:
        if m in low:
            ev.append(f"html:{m}")
    return ev


def is_shopify(evidence: list[str]) -> bool:
    """One strong header, or two weak markers (server-timing counts as weak)."""
    strong = [e for e in evidence if e.startswith("hdr:") and e != "hdr:server-timing"]
    weak = [e for e in evidence if e not in strong]
    return bool(strong) or len(weak) >= 2


def is_blocked(status: int, html_head: str) -> bool:
    if status in BLOCK_STATUS:
        return True
    low = (html_head or "")[:5000].lower()
    return status >= 400 and any(w in low for w in CAPTCHA_WORDS)


def _robots_allows(domain: str, session) -> bool:
    try:
        r = session.get(f"https://{domain}/robots.txt", timeout=TIMEOUT)
    except Exception:
        return True  # unreachable robots.txt: homepage fetch will fail the same way
    if r.status_code in (401, 403):
        return False
    if r.status_code >= 400:
        return True  # no robots.txt means no restrictions
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(r.text.splitlines())
    return rp.can_fetch(UA, f"https://{domain}/")


def probe(domain: str, session) -> dict:
    """One robots.txt fetch, then at most one homepage GET. No retries."""
    row = {
        "domain": domain,
        "outcome": "",
        "status": None,
        "final_host": "",
        "evidence": [],
        "is_shopify": False,
        "probed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        if not _robots_allows(domain, session):
            row["outcome"] = "robots_disallow"
            return row
        r = session.get(
            f"https://{domain}/", timeout=TIMEOUT, allow_redirects=True, stream=True
        )
        try:
            body = r.raw.read(HTML_LIMIT, decode_content=True)
        finally:
            r.close()
        html = body.decode(r.encoding or "utf-8", errors="replace")
        row["status"] = r.status_code
        row["final_host"] = urlparse(r.url).hostname or ""
        if is_blocked(r.status_code, html):
            row["outcome"] = "blocked"
            return row
        row["evidence"] = shopify_evidence(r.status_code, dict(r.headers), html)
        row["is_shopify"] = is_shopify(row["evidence"])
        row["outcome"] = "answered" if r.status_code < 400 else "http_error"
    except Exception as e:  # network failure: record, do not retry
        row["outcome"] = "error"
        row["error"] = type(e).__name__
    return row
