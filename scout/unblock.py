"""Tiered page fetch: plain first, then ZenRows, then ScrapingBee (decision 0015).

Owner decision 2026-11-05: "we need ZenRows and ScrapingBee features, all of them."
Both are commercial scraping APIs with JavaScript rendering, residential/premium
proxies and anti-bot handling. They cost credits, so they are a **fallback tier**:

    plain   our own request (project User-Agent), free. Most Shopify pages pass here.
    zenrows ZenRows Universal Scraper API, mode=auto (it picks JS render and premium
            proxy itself and bills only the configuration that succeeded)
    scrapingbee  ScrapingBee HTML API, render_js + premium_proxy, then stealth_proxy

A page escalates only when the tier below was blocked (403/429/430, a challenge
page) or failed. Every result records which tier served it and the credits spent,
and a daily credit cap stops escalation before it overspends.

Keys come from the environment (never the repo): ZENROWS_API_KEY,
SCRAPINGBEE_API_KEY. A missing key skips that tier.

    python -m scout.unblock https://store.example/products.json --js
    python -m scout.unblock --usage
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.robotparser
from urllib.parse import urlsplit

ZENROWS_API = "https://api.zenrows.com/v1/"
SCRAPINGBEE_API = "https://app.scrapingbee.com/api/v1"

# Credit weights from the vendors' docs (read 2026-11-05): ZenRows standard 1,
# JS 5, premium 10, both 25; ScrapingBee render_js 5, premium 10 (25 with JS),
# stealth 75. Used only when the response header does not state the cost.
EST_COST = {"zenrows": 25, "scrapingbee_premium": 25, "scrapingbee_stealth": 75}
DAILY_CREDIT_CAP = int(os.environ.get("SCOUT_UNBLOCK_DAILY_CREDITS", "1000"))
USAGE_FILE = "data/private/unblock_usage.json"
TIERS = ("plain", "zenrows", "scrapingbee")

BLOCK_MARKERS = re.compile(
    r"cf-challenge|challenge-platform|captcha|verify you are human|access denied|"
    r"attention required|just a moment\.\.\.",
    re.I,
)
_lock = threading.Lock()


def is_blocked(status: int | None, text: str) -> bool:
    """A block or challenge page, not real content. Pure."""
    return status in (403, 429, 430, 503) or bool(
        BLOCK_MARKERS.search((text or "")[:20000])
    )


def _today() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def credits_used() -> float:
    try:
        with open(USAGE_FILE, encoding="utf-8") as fh:
            d = json.load(fh)
        return float(d.get("credits", 0)) if d.get("date") == _today() else 0.0
    except (OSError, ValueError):
        return 0.0


def _spend(credits: float) -> None:
    with _lock:
        used = credits_used() + credits
        os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
        tmp = USAGE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"date": _today(), "credits": used}, fh)
        os.replace(tmp, USAGE_FILE)


def _budget_left(need: float) -> bool:
    return credits_used() + need <= DAILY_CREDIT_CAP


def _key(name: str) -> str | None:
    try:
        from scout import llm

        llm._load_dotenv()
    except Exception:
        pass
    return os.environ.get(name) or None


def robots_allows(session, url: str, ua: str) -> bool:
    parts = urlsplit(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        r = session.get(f"{parts.scheme}://{parts.netloc}/robots.txt", timeout=20)
        rp.parse(r.text.splitlines() if r.ok else [])
    except Exception:
        return True  # robots unreachable: treat as no rules, as crawlers do
    return rp.can_fetch(ua, url)


def _cost(headers, fallback: float) -> float:
    for h in ("X-Request-Cost", "Spb-cost", "Spb-auto-cost"):
        v = headers.get(h) if headers else None
        if v not in (None, ""):
            try:
                return float(v)
            except ValueError:
                pass
    return fallback


def _plain(session, url: str) -> dict:
    r = session.get(url, timeout=30)
    return {"status": r.status_code, "text": r.text, "cost": 0.0}


def _zenrows(session, url: str, key: str, js: bool, country: str | None) -> dict:
    params = {"apikey": key, "url": url, "mode": "auto", "original_status": "true"}
    if country:
        params.update(premium_proxy="true", proxy_country=country)
    if js:
        params["js_render"] = "true"
    r = session.get(ZENROWS_API, params=params, timeout=120)
    return {
        "status": r.status_code,
        "text": r.text,
        "cost": _cost(r.headers, EST_COST["zenrows"]) if r.ok else 0.0,
    }


def _scrapingbee(
    session, url: str, key: str, stealth: bool, country: str | None
) -> dict:
    params = {"url": url, "render_js": "true", "block_resources": "false"}
    params["stealth_proxy" if stealth else "premium_proxy"] = "true"
    if country:
        params["country_code"] = country
    r = session.get(
        SCRAPINGBEE_API,
        params=params,
        headers={"Authorization": f"Bearer {key}"},
        timeout=150,
    )
    est = EST_COST["scrapingbee_stealth" if stealth else "scrapingbee_premium"]
    return {
        "status": r.status_code,
        "text": r.text,
        "cost": _cost(r.headers, est) if r.ok else 0.0,
    }


def fetch(
    url: str,
    *,
    session=None,
    js: bool = False,
    country: str | None = None,
    max_tier: str = "scrapingbee",
    respect_robots: bool = True,
) -> dict:
    """Fetch one URL, escalating tiers only on a block or failure.

    Returns {'url', 'status', 'text', 'tier', 'cost', 'attempts': [...], 'error'?}.
    'text' is the page for the caller to parse; callers store signals, not pages."""
    import requests

    from scout import webmeta

    s = session or requests.Session()
    if session is None:
        s.headers["User-Agent"] = webmeta.UA
    out = {
        "url": url,
        "status": None,
        "text": "",
        "tier": None,
        "cost": 0.0,
        "attempts": [],
    }
    if respect_robots and not robots_allows(s, url, webmeta.UA):
        out["error"] = "robots_disallow"
        return out
    order = TIERS[: TIERS.index(max_tier) + 1]
    plan = []
    for t in order:
        if t == "plain" and not js:
            plan.append(("plain", None))
        elif t == "zenrows" and (k := _key("ZENROWS_API_KEY")):
            plan.append(("zenrows", k))
        elif t == "scrapingbee" and (k := _key("SCRAPINGBEE_API_KEY")):
            plan += [("scrapingbee", k), ("scrapingbee_stealth", k)]
    for tier, key in plan:
        need = (
            0
            if tier == "plain"
            else EST_COST.get(tier, EST_COST["scrapingbee_premium"])
        )
        if need and not _budget_left(need):
            out["attempts"].append(f"{tier}:daily_cap")
            continue
        try:
            if tier == "plain":
                r = _plain(s, url)
            elif tier == "zenrows":
                r = _zenrows(s, url, key, js, country)
            else:
                r = _scrapingbee(s, url, key, tier.endswith("stealth"), country)
        except Exception as exc:
            out["attempts"].append(f"{tier}:{type(exc).__name__}")
            continue
        if r["cost"]:
            _spend(r["cost"])
            out["cost"] += r["cost"]
        if r["status"] and r["status"] < 400 and not is_blocked(r["status"], r["text"]):
            out.update(status=r["status"], text=r["text"], tier=tier)
            out["attempts"].append(f"{tier}:ok")
            return out
        out["attempts"].append(f"{tier}:{r['status']}")
        out["status"] = r["status"]
    out["error"] = "all_tiers_failed" if plan else "no_tier_available"
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Tiered fetch: plain -> ZenRows -> ScrapingBee"
    )
    ap.add_argument("url", nargs="?")
    ap.add_argument("--js", action="store_true", help="page needs JavaScript rendering")
    ap.add_argument("--country", help="proxy country code, e.g. us")
    ap.add_argument("--max-tier", choices=TIERS, default="scrapingbee")
    ap.add_argument("--usage", action="store_true")
    a = ap.parse_args(argv)
    if a.usage:
        print(
            json.dumps(
                {
                    "date": _today(),
                    "credits_used": credits_used(),
                    "daily_cap": DAILY_CREDIT_CAP,
                    "keys": {
                        k: bool(_key(k))
                        for k in ("ZENROWS_API_KEY", "SCRAPINGBEE_API_KEY")
                    },
                },
                indent=2,
            )
        )
        return 0
    if not a.url:
        ap.error("url required")
    r = fetch(a.url, js=a.js, country=a.country, max_tier=a.max_tier)
    print(
        json.dumps(
            {k: v for k, v in r.items() if k != "text"} | {"bytes": len(r["text"])}
        )
    )
    return 0 if r.get("tier") else 1


if __name__ == "__main__":
    sys.exit(main())
