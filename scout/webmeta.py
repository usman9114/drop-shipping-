"""Internet-metadata harness: find and profile stores from records the web
already publishes for other purposes. Deterministic; every pull is a lake run.

Traces used (each read through an official, free, machine-readable channel):
  - Tranco top-1M list: domains with real traffic (research ranking list)
  - DNS via Google Public DNS JSON API: A/CNAME (is it Shopify?), TXT
    (domain-verification tokens for ad and marketing platforms, SPF senders), MX
  - Store sitemaps (robots.txt respected): catalogue size and product dates

No personal data is collected: no WHOIS registrants, no emails, no names.

Usage:
    python -m scout.webmeta discover --top 1000000 --max-dns 400
    python -m scout.webmeta sitemaps --max-stores 40
"""

from __future__ import annotations

import argparse
import ipaddress
import re

import sys
import time
import xml.etree.ElementTree as ET
from urllib import robotparser

from scout import store

UA = "dropship-poc-research/0.1 (+https://github.com/usman9114/drop-shipping-)"
DOH = "https://dns.google/resolve"
SHOPIFY_NET = ipaddress.ip_network("23.227.38.0/24")  # Shopify storefront range

# Product words from warehouse/seeds/rule_why.csv product types. Short or
# ambiguous words (cat, ring, bag, tool) are left out on purpose.
KEYWORDS = [
    "nail",
    "jewel",
    "bracelet",
    "necklace",
    "earring",
    "charm",
    "pendant",
    "petsupply",
    "petshop",
    "dogshop",
    "pawshop",
    "groom",
    "leash",
    "collar",
    "cleaning",
    "mop",
    "yoga",
    "fitness",
    "craft",
    "sewing",
    "crystal",
    "vase",
    "sticker",
    "decal",
    "cushion",
    "pillow",
    "wallet",
    "watchband",
    "handbag",
    "tote",
    "backpack",
    "lure",
    "garden",
    "scrunchie",
    "hairclip",
    "lashes",
]

# TXT tokens and SPF includes -> what they reveal (platform used by the store).
TXT_VENDORS = {
    "facebook-domain-verification": "meta_business",
    "google-site-verification": "google_search_console",
    "pinterest-site-verification": "pinterest",
    "tiktok-developers-site-verification": "tiktok",
    "tiktok-domain-verification": "tiktok",
    "apple-domain-verification": "apple",
    "ms=": "microsoft",
    "zoho-verification": "zoho",
    "klaviyo": "klaviyo",
}
SPF_VENDORS = {
    "_spf.google.com": "google_workspace",
    "spf.protection.outlook.com": "microsoft_365",
    "shops.shopify.com": "shopify_email",
    "servers.mcsv.net": "mailchimp",
    "sendgrid.net": "sendgrid",
    "klaviyo": "klaviyo",
    "mailgun.org": "mailgun",
    "zoho.com": "zoho",
}


def keyword_hits(domain: str, keywords: list[str] = KEYWORDS) -> list[str]:
    """Product words found in the registrable name (TLD ignored)."""
    label = domain.lower().rsplit(".", 1)[0].replace("-", "")
    return [k for k in keywords if k in label]


def is_shopify(a_records: list[str], cnames: list[str]) -> bool:
    for ip in a_records:
        try:
            if ipaddress.ip_address(ip) in SHOPIFY_NET:
                return True
        except ValueError:
            continue
    return any("myshopify.com" in c or "shops.shopify.com" in c for c in cnames)


def txt_signals(txts: list[str]) -> list[str]:
    """Platforms revealed by verification tokens and SPF includes."""
    found = set()
    for t in txts:
        low = t.lower().strip('"')
        for token, name in TXT_VENDORS.items():
            if low.startswith(token) or (token == "klaviyo" and "klaviyo" in low):
                found.add(name)
        if low.startswith("v=spf1"):
            for inc, name in SPF_VENDORS.items():
                if inc in low:
                    found.add(name)
    return sorted(found)


def parse_sitemap(xml_text: str) -> tuple[list[str], list[str]]:
    """Return (child sitemap URLs, page lastmod dates) from a sitemap document."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return [], []
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    children = [e.text.strip() for e in root.findall("s:sitemap/s:loc", ns) if e.text]
    dates = [e.text.strip()[:10] for e in root.findall("s:url/s:lastmod", ns) if e.text]
    urls = root.findall("s:url", ns)
    if urls and not dates:
        dates = [""] * len(urls)
    return children, dates


def _session():
    import requests

    s = requests.Session()
    s.headers["User-Agent"] = UA
    return s


def dns(session, name: str, rtype: str) -> list[str]:
    r = session.get(DOH, params={"name": name, "type": rtype}, timeout=20)
    r.raise_for_status()
    return [a.get("data", "") for a in r.json().get("Answer", []) or []]


def discover(top: int, max_dns: int, pause: float = 0.15) -> dict:
    import tranco

    lst = tranco.Tranco(cache=True, cache_dir="data/private/tranco").list()
    domains = lst.top(top)
    list_id = getattr(lst, "list_id", None)
    hits = [(rank, d, keyword_hits(d)) for rank, d in enumerate(domains, 1)]
    hits = [h for h in hits if h[2]]
    rows_domains = [
        {"domain": d, "tranco_rank": r, "keywords": "|".join(k), "list_id": list_id}
        for r, d, k in hits
    ]
    run_d = store.record_run(
        "web_domains",
        rows_domains,
        source="tranco",
        trust="data",
        params={"top": top, "keywords": KEYWORDS, "list_id": list_id},
        note="Tranco research ranking list; keyword match on domain name",
    )
    s = _session()
    rows_dns = []
    for rank, d, _k in hits[:max_dns]:
        try:
            a = dns(s, d, "A")
            cname = dns(s, "www." + d, "CNAME")
            txt = dns(s, d, "TXT")
            mx = dns(s, d, "MX")
            err = ""
        except Exception as exc:  # network or DNS failure is recorded, not fatal
            a, cname, txt, mx, err = [], [], [], [], type(exc).__name__
        rows_dns.append(
            {
                "domain": d,
                "tranco_rank": rank,
                "a": "|".join(a),
                "www_cname": "|".join(cname),
                "is_shopify": is_shopify(a, cname),
                "signals": "|".join(txt_signals(txt)),
                "mx": "|".join(sorted({m.split()[-1].rstrip(".") for m in mx if m})),
                "error": err,
            }
        )
        time.sleep(pause)
    run_n = store.record_run(
        "web_dns",
        rows_dns,
        source="google_public_dns",
        trust="data",
        params={"max_dns": max_dns},
        note="A, www CNAME, TXT, MX via dns.google JSON API",
    )
    return {
        "web_domains": (run_d, len(rows_domains)),
        "web_dns": (run_n, len(rows_dns)),
    }


def _latest(dataset: str) -> list[dict]:
    runs = [r for r in store._runs() if r["dataset"] == dataset]
    if not runs:
        return []
    import gzip
    import json

    path = store._checked_path(runs[-1])
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def sitemaps(max_stores: int, pause: float = 1.0) -> dict:
    shops = [r for r in _latest("web_dns") if r.get("is_shopify")]
    shops.sort(key=lambda r: r["tranco_rank"])
    s = _session()
    rows = []
    for r in shops[:max_stores]:
        d = r["domain"]
        base = f"https://{d}"
        row = {"domain": d, "tranco_rank": r["tranco_rank"], "allowed": None}
        try:
            rp = robotparser.RobotFileParser()
            rp.parse(s.get(base + "/robots.txt", timeout=20).text.splitlines())
            row["allowed"] = rp.can_fetch(UA, base + "/sitemap.xml")
            if row["allowed"]:
                idx = s.get(base + "/sitemap.xml", timeout=20)
                children, _ = parse_sitemap(idx.text)
                prod = [c for c in children if "sitemap_products" in c]
                dates: list[str] = []
                for c in prod[:3]:  # first 3 product sitemaps at most
                    if rp.can_fetch(UA, c):
                        time.sleep(pause)
                        dates += parse_sitemap(s.get(c, timeout=20).text)[1]
                real = sorted(x for x in dates if x)
                row.update(
                    product_sitemaps=len(prod),
                    products_seen=len(dates),
                    first_lastmod=real[0] if real else None,
                    last_lastmod=real[-1] if real else None,
                    lastmods=real,
                )
        except Exception as exc:
            row["error"] = type(exc).__name__
        rows.append(row)
        time.sleep(pause)
    run = store.record_run(
        "web_sitemaps",
        rows,
        source="store_sitemaps",
        trust="data",
        params={"max_stores": max_stores},
        note="robots.txt respected; product sitemap lastmod dates only",
    )
    return {"web_sitemaps": (run, len(rows))}


def summarize_products(payload: dict) -> dict:
    """Per-store aggregates from one /products.json page. No titles are kept."""
    import statistics

    items = [p for p in (payload or {}).get("products", []) if isinstance(p, dict)]
    created = sorted(
        str(p.get("created_at") or "")[:10] for p in items if p.get("created_at")
    )
    months: dict[str, int] = {}
    for c in created:
        months[c[:7]] = months.get(c[:7], 0) + 1
    prices = []
    for p in items:
        for v in p.get("variants") or []:
            try:
                prices.append(float(v.get("price")))
            except (TypeError, ValueError):
                pass
    types: dict[str, int] = {}
    for p in items:
        t = (p.get("product_type") or "").strip().lower()
        if t:
            types[t] = types.get(t, 0) + 1
    return {
        "products_in_page": len(items),
        "oldest_created": created[0] if created else None,
        "newest_created": created[-1] if created else None,
        "created_by_month": months,
        "median_price": round(statistics.median(prices), 2) if prices else None,
        "top_types": sorted(types, key=lambda t: -types[t])[:5],
    }


def products(max_stores: int, pause: float = 1.0) -> dict:
    shops = sorted(
        (r for r in _latest("web_dns") if r.get("is_shopify")),
        key=lambda r: r["tranco_rank"],
    )
    s = _session()
    rows = []
    for r in shops[:max_stores]:
        d = r["domain"]
        base = f"https://{d}"
        row = {"domain": d, "tranco_rank": r["tranco_rank"]}
        try:
            rp = robotparser.RobotFileParser()
            rp.parse(s.get(base + "/robots.txt", timeout=20).text.splitlines())
            url = base + "/products.json?limit=250"
            row["allowed"] = rp.can_fetch(UA, url)
            if row["allowed"]:
                resp = s.get(url, timeout=30)
                row["status"] = resp.status_code
                if resp.ok:
                    row.update(summarize_products(resp.json()))
        except Exception as exc:
            row["error"] = type(exc).__name__
        rows.append(row)
        time.sleep(pause)
    run = store.record_run(
        "web_products",
        rows,
        source="shopify_products_json",
        trust="data",
        params={"max_stores": max_stores, "limit": 250},
        note="one page per store, robots.txt respected; aggregates only, no titles",
    )
    return {"web_products": (run, len(rows))}


# Tags that reveal how a store gets traffic. Each pattern is matched against the
# homepage HTML; a hit means the store installed that platform's code.
TRAFFIC_TAGS = {
    "meta_pixel": r"connect\.facebook\.net/[^\"']*/fbevents\.js|fbq\(\s*['\"]init",
    "tiktok_pixel": r"analytics\.tiktok\.com|ttq\.load\(",
    "google_ads": r"['\"]AW-\d{6,}",
    "google_analytics": r"['\"]G-[A-Z0-9]{6,}['\"]|googletagmanager\.com/gtag/js",
    "pinterest_tag": r"s\.pinimg\.com/ct/core\.js|pintrk\(",
    "snap_pixel": r"sc-static\.net/scevent\.min\.js|snaptr\(",
    "microsoft_ads": r"bat\.bing\.com",
    "reddit_pixel": r"redditstatic\.com/ads/pixel\.js|rdt\(\s*['\"]init",
    "klaviyo_email": r"static\.klaviyo\.com|klaviyo\.com/onsite",
    "sms_marketing": r"attn\.tv|attentivemobile|postscript\.io|smsbump|cdn\.yotpo\.com/sms",
    "affiliate_program": r"uppromote|goaffpro|refersion|socialsnowball|social-snowball|aspireiq|grin\.co|impact\.com/|shareasale",
    "reviews_app": r"judge\.me|loox\.io|okendo|yotpo|stamped\.io|reviews\.io|junip",
    "loyalty_program": r"smile\.io|loyaltylion|yotpo-loyalty|rivo\.io",
    "shopify_web_pixels": r"webPixelsConfigList|web-pixels-manager",
}

SOCIAL = {
    "instagram": r"instagram\.com/([A-Za-z0-9_.]{2,30})",
    "tiktok": r"tiktok\.com/@([A-Za-z0-9_.]{2,30})",
    "facebook": r"facebook\.com/([A-Za-z0-9.\-]{3,60})",
    "pinterest": r"pinterest\.[a-z.]+/([A-Za-z0-9_]{3,30})",
    "youtube": r"youtube\.com/(@[A-Za-z0-9_.\-]{2,40}|channel/[A-Za-z0-9_\-]{10,40}|c/[A-Za-z0-9_\-]{2,40})",
    "x": r"(?:twitter|x)\.com/([A-Za-z0-9_]{2,15})",
}
_SOCIAL_SKIP = {
    "sharer",
    "sharer.php",
    "share",
    "intent",
    "pin",
    "dialog",
    "tr",
    "plugins",
    "p",
    "reel",
    "explore",
    "watch",
    "embed",
    "hashtag",
    "home",
    "login",
    "policies",
}


def traffic_tags(html: str) -> list[str]:
    return sorted(k for k, pat in TRAFFIC_TAGS.items() if re.search(pat, html, re.I))


def social_links(html: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for net, pat in SOCIAL.items():
        handles = []
        for h in re.findall(pat, html):
            h = h.rstrip("/.").split("?")[0]
            if h.lower() in _SOCIAL_SKIP or h.lower().startswith(("sharer", "share")):
                continue
            if h not in handles:
                handles.append(h)
        if handles:
            out[net] = handles[:3]
    return out


def jsonld(html: str) -> list[dict]:
    """schema.org JSON-LD blocks (structured data published for search engines)."""
    import json

    blocks = []
    for raw in re.findall(
        r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", html, re.S | re.I
    ):
        try:
            data = json.loads(raw.strip())
        except ValueError:
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if isinstance(it, dict):
                blocks.append(it)
                blocks += [g for g in it.get("@graph", []) if isinstance(g, dict)]
    return blocks


def aggregate_rating(blocks: list[dict]) -> tuple[int | None, float | None]:
    for b in blocks:
        ar = b.get("aggregateRating")
        if isinstance(ar, dict):
            try:
                count = int(float(ar.get("reviewCount") or ar.get("ratingCount") or 0))
                value = float(ar.get("ratingValue")) if ar.get("ratingValue") else None
                return count, value
            except (TypeError, ValueError):
                continue
    return None, None


def footprint(max_stores: int, pause: float = 1.0) -> dict:
    shops = sorted(
        (r for r in _latest("web_dns") if r.get("is_shopify")),
        key=lambda r: r["tranco_rank"],
    )
    s = _session()
    rows = []
    for r in shops[:max_stores]:
        d = r["domain"]
        base = f"https://{d}"
        row = {
            "domain": d,
            "tranco_rank": r["tranco_rank"],
            "dns_signals": r.get("signals"),
        }
        try:
            rp = robotparser.RobotFileParser()
            rp.parse(s.get(base + "/robots.txt", timeout=20).text.splitlines())
            row["allowed"] = rp.can_fetch(UA, base + "/")
            if row["allowed"]:
                html = s.get(base + "/", timeout=30).text
                blocks = jsonld(html)
                same_as = sorted(
                    {
                        u
                        for b in blocks
                        for u in (b.get("sameAs") or [])
                        if isinstance(u, str)
                    }
                )
                row.update(
                    traffic_tags=traffic_tags(html),
                    socials=social_links(html + " ".join(same_as)),
                    jsonld_same_as=len(same_as),
                )
                feed = base + "/products.json?limit=3"
                if rp.can_fetch(UA, feed):
                    time.sleep(pause)
                    prods = s.get(feed, timeout=30).json().get("products") or []
                    handle = prods[0].get("handle") if prods else None
                    page = f"{base}/products/{handle}" if handle else None
                    if page and rp.can_fetch(UA, page):
                        time.sleep(pause)
                        count, value = aggregate_rating(
                            jsonld(s.get(page, timeout=30).text)
                        )
                        row.update(sample_review_count=count, sample_rating=value)
        except Exception as exc:
            row["error"] = type(exc).__name__
        rows.append(row)
        time.sleep(pause)
    run = store.record_run(
        "web_footprint",
        rows,
        source="store_homepages",
        trust="data",
        params={"max_stores": max_stores},
        note="robots.txt respected; tags, social handles, one product's review count",
    )
    return {"web_footprint": (run, len(rows))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Internet-metadata harness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("discover")
    d.add_argument("--top", type=int, default=1_000_000)
    d.add_argument("--max-dns", type=int, default=400)
    m = sub.add_parser("sitemaps")
    m.add_argument("--max-stores", type=int, default=40)
    pj = sub.add_parser("products")
    pj.add_argument("--max-stores", type=int, default=40)
    fp = sub.add_parser("footprint")
    fp.add_argument("--max-stores", type=int, default=40)
    a = ap.parse_args(argv)
    if a.cmd == "discover":
        out = discover(a.top, a.max_dns)
    elif a.cmd == "sitemaps":
        out = sitemaps(a.max_stores)
    elif a.cmd == "products":
        out = products(a.max_stores)
    else:
        out = footprint(a.max_stores)
    for k, (run, n) in out.items():
        print(f"{k}: run {run}, {n} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
