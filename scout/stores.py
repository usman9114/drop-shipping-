"""Store profiler: turn a Shopify store's public machine records into evidence.

Step 1 of the owner's plan (2026-11-04): find the best online stores and
understand exactly what they do. Discovery is `scout.webmeta scan` (Tranco top
1M + DNS). This module profiles the stores it found, in two passes:

  meta   /robots.txt + /meta.json for every Shopify hit, best rank first.
         Keeps country, province, currency, ships-to countries, published
         product and collection counts, and the shop id (sequential, so it dates
         the store). City, description and owner details are dropped.
  deep   for the strongest stores: up to a few pages of /products.json
         (aggregates only: dates, prices, vendors, categories, dropship traces),
         the homepage (ad pixels, email/SMS, affiliate, review apps, social
         handles), one product page (review count), DNS TXT/MX/www CNAME.
  ranks  the store's Tranco rank on earlier dates (rank growth).

Rules kept here: robots.txt is read and obeyed for every URL; a pause between
requests to the same store; a fixed User-Agent that names the project; no
titles, descriptions, images or personal data are stored, only counts and
shares. Results stay in the private lake (data/private/); only aggregates are
committed.

Usage:
    python -m scout.stores meta  --max-stores 3000 --workers 4
    python -m scout.stores deep  --max-stores 300  --workers 4 --pages 4
    python -m scout.stores ranks --days-back 90 365
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from scout.robots import RobotRules
from scout import store, webmeta

RULES = Path("warehouse/seeds/store_category_rules.csv")

# --- pure functions (tested, no network) ------------------------------------


def meta_summary(meta: dict) -> dict:
    """The /meta.json fields we keep. No city, description or contact data."""
    ships = meta.get("ships_to_countries") or []
    if not isinstance(ships, list):
        ships = []
    return {
        "shop_id": meta.get("id"),
        "shop_name": meta.get("name"),
        "country": meta.get("country"),
        "province": meta.get("province"),
        "currency": meta.get("currency"),
        "ships_to_count": len(ships),
        "ships_to_us": "US" in ships or "*" in ships,
        "published_products": meta.get("published_products_count"),
        "published_collections": meta.get("published_collections_count"),
        "installments": bool(meta.get("offers_shop_pay_installments")),
    }


def load_rules(path: Path = RULES) -> list[tuple[str, re.Pattern]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = sorted(csv.DictReader(fh), key=lambda r: int(r["priority"]))
    return [(r["category"], re.compile(r["pattern"], re.I)) for r in rows]


def classify_product(text: str, rules: list[tuple[str, re.Pattern]]) -> str:
    for cat, pat in rules:
        if pat.search(text):
            return cat
    return "other"


def _product_text(p: dict) -> tuple[str, str]:
    """(type text, title+tags text). Type is tried first: it is the merchant's label."""
    tags = p.get("tags") or []
    if isinstance(tags, str):
        tags = tags.split(",")
    tags = [t for t in tags if not str(t).startswith("_")]  # internal tags
    return (
        p.get("product_type") or "",
        f"{p.get('title') or ''} {' '.join(map(str, tags))}",
    )


def product_category(p: dict, rules) -> str:
    ptype, rest = _product_text(p)
    if ptype.strip():
        c = classify_product(ptype, rules)
        if c != "other":
            return c
    return classify_product(rest, rules)


# Traces that a product was imported from a marketplace supplier.
# AliExpress image ids look like H/S/U + 32 hex chars; Shopify keeps file names.
AE_IMAGE = re.compile(
    r"/(?:[HSU][0-9a-f]{32}[a-z]?)(?:_[^/]*)?\.(?:jpe?g|png|webp)", re.I
)
# DSers/Oberlo-style SKUs carry AliExpress property pairs: a short numeric
# property id, a numeric value id, then "#name" or ";next-pair"
# ("14:200004889#Black;5:20129901", "200000182:193#Black"). Brand SKUs such as
# "5564:XL#L" or "10045041000:100072:XL" (tommyjohn.com, 2026-11-05) must not match.
DSERS_SKU = re.compile(r"^\d{1,9}:\d{1,12}(?:#|;\d{1,9}:\d)")
# CJ SKUs start with "CJ" plus letters and a long digit run ("CJYZ319118002BY").
CJ_SKU = re.compile(r"^CJ[A-Z]{2,6}\d{6,}", re.I)
DROPSHIP_SKU = re.compile(rf"{DSERS_SKU.pattern}|#\d{{3,}}|{CJ_SKU.pattern}", re.I)
DROPSHIP_VENDORS = re.compile(
    r"aliexpress|cj ?dropshipping|cjdropshipping|zendrop|autods|spocket|dsers|syncee|"
    r"modalyst|wholesale2b|doba|appscenic",
    re.I,
)
POD_VENDORS = re.compile(r"printful|printify|gelato|teelaunch|gooten|customcat", re.I)


def dropship_traces(p: dict) -> dict[str, bool]:
    imgs = [i.get("src") or "" for i in (p.get("images") or []) if isinstance(i, dict)]
    skus = [
        str(v.get("sku") or "")
        for v in (p.get("variants") or [])
        if isinstance(v, dict)
    ]
    vendor = str(p.get("vendor") or "")
    tags = p.get("tags") or []
    tags_text = " ".join(tags) if isinstance(tags, list) else str(tags)
    return {
        "ae_image": any(AE_IMAGE.search(u) for u in imgs),
        "dropship_sku": any(DROPSHIP_SKU.search(s) for s in skus if s),
        "dropship_vendor": bool(DROPSHIP_VENDORS.search(vendor + " " + tags_text)),
        "pod_vendor": bool(POD_VENDORS.search(vendor + " " + tags_text)),
    }


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def vendor_is_shop(vendor: str, shop_name: str, domain: str) -> bool:
    v = _norm(vendor)
    if len(v) < 3:
        return False
    names = {_norm(shop_name), _norm(domain.split(".")[0])}
    return any(n and (v in n or n in v) for n in names)


# Vendor values that name a product line of the store itself, not another brand.
# Pakistani fashion brands fill the vendor field with lines and collections
# ("Unstitched", "Pret", "Men"), which made one brand look like a 30-brand
# retailer (hand check 2026-11-22, docs/decisions/0019). Whole value only.
LINE_VENDOR = re.compile(
    r"^(?:(?:un)?stitched|pret|ready[ -]?to[ -]?wear|rtw|luxury|lawn|kurta|eastern|"
    r"western|festive|formals?|casuals?|basics|essentials|signature|premium|"
    r"(?:wo)?men|ladies|gents|kids|girls|boys|baby|infants?|teens?|junior|home|"
    r"fragrances?|perfumes?|accessories|jewel(?:le)?ry|footwear|shoes|bags|"
    r"makeup|skin ?care|beauty|fabrics?|textiles?|bedding|towels|winter|summer|"
    r"eid|wedding|bridal|collections?|new arrivals?|sale|outlet|default|"
    r"vendor|unknown|na|n/?a)$",
    re.I,
)

# Third-party brands sold by Pakistani department, baby, beauty and electronics
# stores (hand check 2026-11-22). A title naming one of them, when the vendor is
# the store's own name, means a resold product. Lower-case whole words.
KNOWN_BRANDS = re.compile(
    r"\b(?:xiaomi|redmi|samsung|apple|iphone|oppo|vivo|realme|infinix|tecno|"
    r"huawei|honor|anker|baseus|ugreen|jbl|sony|lenovo|hp|dell|logitech|philips|"
    r"panasonic|braun|tefal|kenwood|black ?\+? ?decker|westpoint|anex|dawlance|"
    r"haier|pel|chicco|pigeon|philips avent|avent|tommee tippee|mee mee|"
    r"huggies|pampers|molfix|johnson'?s|mothercare|fisher[- ]price|lego|"
    r"hasbro|mattel|barbie|hot wheels|l'?or[eé]al|maybelline|garnier|nivea|"
    r"dove|ponds?|olay|neutrogena|cetaphil|the ordinary|cerave|revlon|"
    r"rimmel|nyx|mac|clinique|est[eé]e lauder|loreal|nestl[eé]|unilever|"
    r"colgate|gillette|oral[- ]?b|dettol|lux|sunsilk|head ?& ?shoulders|"
    r"pantene|tresemm[eé]|nike|adidas|puma|skechers|reebok|casio|"
    r"tupperware|pyrex|corelle|luminarc|borosil)\b",
    re.I,
)


# Pakistani brands name vendors after whole collections ("Lux Pret Vol-2 Winter
# 2026", "Men Kurta", "Luxury Attars"), so for that market a line word anywhere
# in the value counts. Used only when market == "pk" (business_model): in the US
# "Nike Men" is another brand, not a line.
LINE_WORDS_PK = re.compile(
    r"(?:\b(?:(?:un)?stitched|pret|ready to wear|luxury|lux|lawn|kurtas?|kameez|"
    r"shalwar|shirts?|trousers?|sweaters?|activewear|eastern|western|festive|"
    r"formals?|casuals?|ethnic|fancy|basics|essentials|signature|premium|"
    r"(?:wo)?mens?|ladies|gents|kids|girls|boys|baby|toddlers?|infants?|"
    r"junior|home|fragrances?|perfumes?|attars?|bakhoor|testers?|deals?|kits?|"
    r"accessories|jewel(?:le)?ry|footwear|shoes|bags|makeup|fabrics?|bedding|"
    r"winter|summer|spring|autumn|eid|wedding|bridal|collections?|edit|drop|"
    r"vol|boutique|limited edition|silk|khaddar|jalabiyas?)\b|"
    r"(?:^|[\s'_-])(?:20)?2\d\b)",
    re.I,
)


def line_share(s: dict, shop_name: str, domain: str) -> float | None:
    """line_vendor_share recomputed from saved vendor_names (None if not saved)."""
    names = s.get("vendor_names")
    n = s.get("products_sampled") or 0
    if not names or not n:
        return None
    hit = sum(c for v, c in names.items() if vendor_is_line(v, shop_name, domain))
    return round(hit / n, 3)


def vendor_is_line(vendor: str, shop_name: str, domain: str) -> bool:
    """The store's own name, or a product-line or collection name of its label
    (broad match; business_model trusts it only for the Pakistan market)."""
    v = vendor.strip()
    return (
        vendor_is_shop(v, shop_name, domain)
        or bool(LINE_VENDOR.match(v))
        or bool(LINE_WORDS_PK.search(v))
    )


def _quantile(xs: list[float], q: float) -> float | None:
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 2)


def summarize_feed(
    products: list[dict], shop_name: str, domain: str, rules, today: date
) -> dict:
    """Aggregates from /products.json pages. No titles or text are returned."""
    items = [p for p in products if isinstance(p, dict)]
    n = len(items)
    created = sorted(
        str(p.get("created_at") or "")[:10] for p in items if p.get("created_at")
    )
    ages = []
    for c in created:
        try:
            ages.append((today - date.fromisoformat(c)).days)
        except ValueError:
            pass
    prices, discounted, variants, available = [], 0, 0, 0
    vendors: dict[str, int] = {}
    cats: dict[str, int] = {}
    types: dict[str, int] = {}
    traces = {"ae_image": 0, "dropship_sku": 0, "dropship_vendor": 0, "pod_vendor": 0}
    own_vendor = line_vendor = brand_titles = 0
    brands_seen: set[str] = set()
    for p in items:
        vs = [v for v in (p.get("variants") or []) if isinstance(v, dict)]
        variants += len(vs)
        pp = []
        disc = False
        for v in vs:
            try:
                price = float(v.get("price"))
            except (TypeError, ValueError):
                continue
            if price <= 0:
                continue  # free samples, placeholders
            pp.append(price)
            try:
                if float(v.get("compare_at_price") or 0) > price:
                    disc = True
            except (TypeError, ValueError):
                pass
            if v.get("available"):
                available += 1
        if pp:
            prices.append(min(pp))  # entry price of the product
        discounted += disc
        vend = str(p.get("vendor") or "").strip()
        if vend:
            vendors[vend] = vendors.get(vend, 0) + 1
            own_vendor += vendor_is_shop(vend, shop_name, domain)
            line_vendor += vendor_is_line(vend, shop_name, domain)
        title = str(p.get("title") or "")
        hit = KNOWN_BRANDS.search(title)
        if hit and not vendor_is_shop(hit.group(0), shop_name, domain):
            brand_titles += 1
            brands_seen.add(_norm(hit.group(0)))
        c = product_category(p, rules)
        cats[c] = cats.get(c, 0) + 1
        t = (p.get("product_type") or "").strip().lower()
        if t:
            types[t] = types.get(t, 0) + 1
        for k, hit in dropship_traces(p).items():
            traces[k] += hit
    top_vendor = max(vendors.values()) if vendors else 0

    def share(x: int) -> float | None:
        return round(x / n, 3) if n else None

    real_cats = {k: v for k, v in cats.items() if k not in ("non_product", "other")}
    if sum(real_cats.values()) < 0.3 * n:  # rules cover too little: say so
        real_cats = {k: v for k, v in cats.items() if k != "non_product"}
    top_cat = max(real_cats, key=lambda k: real_cats[k]) if real_cats else None
    months: dict[str, int] = {}
    for c in created:
        months[c[:7]] = months.get(c[:7], 0) + 1
    return {
        "products_sampled": n,
        "oldest_created": created[0] if created else None,
        "newest_created": created[-1] if created else None,
        "added_30d": sum(a <= 30 for a in ages),
        "added_90d": sum(a <= 90 for a in ages),
        "added_365d": sum(a <= 365 for a in ages),
        "created_by_month": months,
        "price_p25": _quantile(prices, 0.25),
        "price_median": _quantile(prices, 0.5),
        "price_p75": _quantile(prices, 0.75),
        "discount_share": share(discounted),
        "variants_per_product": round(variants / n, 2) if n else None,
        "available_variant_share": round(available / variants, 3) if variants else None,
        "vendors": len(vendors),
        "top_vendor_share": share(top_vendor),
        "own_vendor_share": share(own_vendor),
        "line_vendor_share": share(line_vendor),
        # every vendor with its count (capped): lets relabel re-score vendor
        # rules from saved evidence, no refetch (principle 13)
        "vendor_names": dict(sorted(vendors.items(), key=lambda kv: -kv[1])[:100]),
        "brand_title_share": share(brand_titles),
        "brands_named": len(brands_seen),
        "category_counts": cats,
        "top_category": top_cat,
        "top_category_share": share(real_cats[top_cat]) if top_cat else None,
        "top_types": sorted(types, key=lambda t: -types[t])[:5],
        "ae_image_share": share(traces["ae_image"]),
        "dropship_sku_share": share(traces["dropship_sku"]),
        "dropship_vendor_share": share(traces["dropship_vendor"]),
        "pod_share": share(traces["pod_vendor"]),
    }


# Only real script/link sources count: page builders (e.g. PageFly) embed maps of
# every app they can integrate with, which names apps the store never installed.
DROPSHIP_APPS = re.compile(
    r"""(?:src|href)\s*=\s*["'][^"']*(?:dsers|zendrop|autods|spocket|cjdropshipping|"""
    r"""syncee|alidropship)[^"']*["']""",
    re.I,
)


def category_spread(s: dict) -> int:
    """Categories holding at least 8% of the classified products (not other/gift cards)."""
    cc = {
        k: v
        for k, v in (s.get("category_counts") or {}).items()
        if k not in ("non_product", "other")
    }
    n = sum(cc.values())
    return sum(1 for v in cc.values() if n and v / n >= 0.08)


GENERAL_MIN_CATEGORIES = 4
GENERAL_MIN_DISCOUNT = 0.5
GENERAL_MIN_PRODUCTS = 50
# Markets where the general-store pattern is not used: Pakistani brands run
# near-permanent sales across apparel, home and kids lines, so the pattern
# labelled real brands "general" (hand check 2026-11-22). Dropship traces still apply.
GENERAL_UNVALIDATED = {"pk"}
# Share of titles naming a known third-party brand that marks a store as a
# reseller of other brands' goods (hand check 2026-11-22).
RESOLD_MIN_BRAND_TITLES = 0.3


def business_model(
    s: dict, homepage_dropship_app: bool = False
) -> tuple[str, list[str]]:
    """brand | general | retailer | reseller | dropship | pod | unclear, with the reasons.

    general: one name over many unrelated categories with permanent discounts, the
    typical dropshipper shape (copyable); a hypothesis, validated separately.

    brand: makes or commissions its own goods (its own name, or one vendor holding
    half or more of a small catalogue). retailer: 10+ vendors with none dominant,
    a big multi-brand retailer, publisher or house-brand portfolio (many labels,
    one owner); not copyable at our scale. reseller: 6 to 9 vendors, none
    dominant (a boutique reselling other brands). A vendor holding half the catalogue,
    or five labels or fewer, means a brand. The 10-vendor line comes from a
    25-store hand check where 7 of 9 'resellers' with 12-20 vendors were big
    retailers or portfolio owners; recheck it on the larger validation sample.
    dropship: marketplace-import traces. pod: print on demand.

    Supplier traces win when present because they are direct evidence. A
    dropshipping app on the homepage is only a supporting signal: app developers
    (and page builders) ship that code on their own sites, so it needs some trace
    in the products as well. Validated on a hand-checked sample; see
    docs/reviews/2026-11-04-business-model-validation.md.
    """
    why = []
    n = s.get("products_sampled") or 0
    if n == 0:
        return "unclear", ["no product feed"]
    ds = max(
        s.get("ae_image_share") or 0,
        s.get("dropship_sku_share") or 0,
        s.get("dropship_vendor_share") or 0,
    )
    if ds >= 0.2 or (homepage_dropship_app and ds >= 0.05):
        why.append(f"supplier-import traces on {ds:.0%} of products")
        if homepage_dropship_app:
            why.append("dropshipping app code on homepage")
        return "dropship", why
    if (s.get("pod_share") or 0) >= 0.3:
        return "pod", [f"print-on-demand vendor on {s['pod_share']:.0%} of products"]
    # Resold goods under the store's own vendor name (Pakistani department and
    # electronics stores, hand check 2026-11-22): titles name other brands.
    bt = s.get("brand_title_share")
    if bt is not None and bt >= RESOLD_MIN_BRAND_TITLES:
        named = s.get("brands_named") or 0
        kind = "retailer" if named >= 3 else "reseller"
        return kind, [f"{bt:.0%} of titles name another brand ({named} brands)"]
    own = s.get("own_vendor_share") or 0
    line = s.get("line_vendor_share") if s.get("market") == "pk" else None
    if line is not None and line > own:
        why.append(f"vendor is own name or a product line on {line:.0%}")
        own = line
    top = s.get("top_vendor_share") or 0
    vendors = s.get("vendors") or 0
    spread = category_spread(s)
    if (
        s.get("market") not in GENERAL_UNVALIDATED
        and (own >= 0.5 or top >= 0.5)
        and n >= GENERAL_MIN_PRODUCTS
        and spread >= GENERAL_MIN_CATEGORIES
        and (s.get("discount_share") or 0) >= GENERAL_MIN_DISCOUNT
    ):
        # A dropshipper often enters its own store name as the vendor, so the vendor
        # alone cannot prove "own goods". Many unrelated categories under one name
        # plus permanent discounts is the general-store pattern.
        return "general", [
            f"general store pattern: {spread} categories, "
            f"{s['discount_share']:.0%} of products discounted"
        ]
    if own >= 0.5:
        return "brand", why or [f"own name is the vendor on {own:.0%} of products"]
    if top >= 0.5:
        return "brand", [f"one vendor holds {top:.0%} of {vendors} vendors"]
    if vendors <= 5:  # a handful of labels is a brand with sub-labels
        return "brand", [f"only {vendors} vendors (own sub-labels), largest {top:.0%}"]
    if vendors >= 10 and top < 0.5:
        return "retailer", [f"{vendors} vendors, largest has {top:.0%}"]
    if vendors >= 5 and top < 0.5:
        return "reseller", [f"{vendors} vendors, largest has {top:.0%}"]
    return "unclear", [f"{vendors} vendors, largest {top:.0%}, own {own:.0%}"]


def fit_shop_age(points: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Calibration for shop id -> earliest possible start date.

    Shopify shop ids are sequential. For each store, its oldest product date is
    an upper bound on its start. The lower envelope (running minimum from the
    largest id down) is a monotone id -> date curve.
    """
    pts = sorted((int(i), d) for i, d in points if i and d)
    out: list[tuple[int, str]] = []
    best = None
    for i, d in reversed(pts):
        if best is None or d < best:
            best = d
        out.append((i, best))
    return sorted(out)


def shop_started_by(shop_id: int | None, curve: list[tuple[int, str]]) -> str | None:
    """Latest calibration date at or above this id = the store existed by then."""
    if not shop_id or not curve:
        return None
    for i, d in curve:
        if i >= shop_id:
            return d
    return None


# --- network passes ---------------------------------------------------------


def _robots(s, base: str):
    rp = RobotRules()
    r = s.get(base + "/robots.txt", timeout=20)
    rp.parse(r.text.splitlines() if r.ok else [])
    return rp


def _shop_hits() -> list[dict]:
    """Every Shopify domain from the scan (and older discover runs), best rank first."""
    seen: dict[str, int] = {}
    for ds in ("web_scan", "web_dns"):
        for r in _all_rows(ds):
            if ds == "web_dns" and not r.get("is_shopify"):
                continue
            d, rank = r["domain"], r["tranco_rank"]
            if d not in seen or rank < seen[d]:
                seen[d] = rank
    skip = re.compile(
        r"(^|\.)(shopify|myshopify|shopifycdn|shopifysvc|shopify-?plus)\.", re.I
    )
    return [
        {"domain": d, "tranco_rank": r}
        for d, r in sorted(seen.items(), key=lambda x: x[1])
        if not skip.search(d + ".")
    ]


def new_hits() -> set[str]:
    """Shopify domains found by incremental discovery (web_scan runs in mode "new")."""
    import gzip
    import json

    out: set[str] = set()
    for run in store._runs():
        if (
            run["dataset"] != "web_scan"
            or (run.get("params") or {}).get("mode") != "new"
        ):
            continue
        with gzip.open(store._checked_path(run), "rt", encoding="utf-8") as fh:
            out |= {json.loads(x)["domain"] for x in fh if x.strip()}
    return out


def _new_first(items: list[dict], new: set[str]) -> list[dict]:
    """Stable sort: newly discovered stores first, each group in its own order."""
    return sorted(items, key=lambda h: h["domain"] not in new)


def _all_rows(dataset: str) -> list[dict]:
    import gzip
    import json

    rows = []
    for run in store._runs():
        if run["dataset"] != dataset:
            continue
        with gzip.open(store._checked_path(run), "rt", encoding="utf-8") as fh:
            rows += [json.loads(x) for x in fh if x.strip()]
    return rows


def latest_good(rows: list[dict]) -> dict[str, dict]:
    """Latest row per domain, ignoring failed fetches (rows with an error).

    A transient failure on a refresh must never replace a good earlier profile."""
    out: dict[str, dict] = {}
    for r in rows:  # runs are in order; later rows win
        if not r.get("error"):
            out[r["domain"]] = r
    return out


MAX_FAILS = 3  # a store that failed this many fetches is left alone (no daily retry)


def gave_up(rows: list[dict], max_fails: int = MAX_FAILS) -> set[str]:
    """Domains with max_fails or more failed fetches and no good row.

    HTTP 429 is not counted: it means we were throttled (Shopify limits by our
    user agent across all its stores), not that the store is broken."""
    fails: dict[str, int] = {}
    for r in rows:
        if r.get("error") and r.get("error") != "HTTP429":
            fails[r["domain"]] = fails.get(r["domain"], 0) + 1
    good = set(latest_good(rows))
    return {d for d, n in fails.items() if n >= max_fails and d not in good}


def _done(dataset: str) -> set[str]:
    """Domains already answered, plus those that failed MAX_FAILS times. Other
    failed fetches are not done: they get retried."""
    rows = _all_rows(dataset)
    return set(latest_good(rows)) | gave_up(rows)


def _parallel(fn, items: list, workers: int) -> list:
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def _meta_one(hit: dict, pause: float) -> dict:
    d = hit["domain"]
    base = f"https://{d}"
    row = {"domain": d, "tranco_rank": hit["tranco_rank"]}
    s = webmeta._session()
    try:
        rp = _robots(s, base)
        row["meta_allowed"] = rp.can_fetch(webmeta.UA, base + "/meta.json")
        row["feed_allowed"] = rp.can_fetch(webmeta.UA, base + "/products.json")
        if row["meta_allowed"]:
            time.sleep(pause)
            r = s.get(base + "/meta.json", timeout=20)
            row["status"] = r.status_code
            if r.ok and "json" in r.headers.get("content-type", ""):
                row.update(meta_summary(r.json()))
                row["final_host"] = r.url.split("/")[2]
    except Exception as exc:
        row["error"] = type(exc).__name__
    return row


def run_meta(
    max_stores: int,
    workers: int,
    pause: float,
    batch: int = 500,
    new_first: bool = False,
) -> dict:
    done = _done("web_meta")
    todo = [h for h in _shop_hits() if h["domain"] not in done]
    if new_first:
        todo = _new_first(todo, new_hits())
    todo = todo[:max_stores]
    out = {}
    for i in range(0, len(todo), batch):
        chunk = todo[i : i + batch]
        rows = _parallel(lambda h: _meta_one(h, pause), chunk, workers)
        run = store.record_run(
            "web_meta",
            rows,
            source="shopify_meta_json",
            trust="data",
            params={"n": len(chunk), "workers": workers},
            note="robots.txt respected; /meta.json fields: country, currency, counts, shop id",
        )
        ok = sum(1 for r in rows if r.get("shop_id"))
        print(
            f"meta batch {i}: {len(rows)} stores, {ok} answered",
            file=sys.stderr,
            flush=True,
        )
        out[f"web_meta {i}"] = (run, len(rows))
    return out


HOME_EXTRA = {
    "dropship_app": DROPSHIP_APPS.pattern,
    "pod_app": r"printful|printify|gelato\.com|teelaunch",
    "influencer_app": r"grin\.co|aspire\.io|upfluence|collabs|shopify-?collabs|dovetale",
    "subscriptions": r"rechargepayments|rechargecdn|skio|loopsubscriptions|seal-?subscriptions",
    "bnpl": r"afterpay|klarna|affirm|sezzle|shop ?pay installments",
    "upsell_app": r"rebuy|zipify|reconvert|bold-?upsell|frequently-?bought",
    "chat_support": r"gorgias|tidio|zendesk|intercom|re:?amaze|richpanel",
    "tiktok_shop": r"shop\.tiktok\.com|tiktokshop",
    "amazon_link": r"amazon\.com/(?:stores|shops|dp)/",
}


def homepage_signals(html: str) -> dict:
    tags = set(webmeta.traffic_tags(html))
    tags |= {k for k, p in HOME_EXTRA.items() if re.search(p, html, re.I)}
    blocks = webmeta.jsonld(html)
    same_as = {u for b in blocks for u in (b.get("sameAs") or []) if isinstance(u, str)}
    socials = webmeta.social_links(html + " " + " ".join(sorted(same_as)))
    return {"traffic_tags": sorted(tags), "social_networks": sorted(socials)}


BEST_NAME = re.compile(
    r"best[- ]?sell|top[- ]?sell|most[- ]?popular|hot[- ]?sell|trending|fan[- ]?favou?rite",
    re.I,
)
# evergreen handles beat campaign ones ("best-sellers" over "eid-sale-best-seller-2026")
BEST_EVERGREEN = re.compile(
    r"^(?:all-)?(?:best[- ]?sell(?:er|ing)s?(?:-products?)?|top[- ]?sell(?:er|ing)s?|most-popular)$",
    re.I,
)


def pick_best_collection(collections: list[dict]) -> dict | None:
    """The store's best-seller collection: evergreen handle first, then the
    largest of the rest. Empty collections are skipped."""
    cands = [
        c
        for c in collections
        if BEST_NAME.search((c.get("handle") or "") + " " + (c.get("title") or ""))
        and (c.get("products_count") or 0) > 0
    ]
    if not cands:
        return None
    green = [c for c in cands if BEST_EVERGREEN.match(c.get("handle") or "")]
    return max(green or cands, key=lambda c: c.get("products_count") or 0)


def summarize_best(products: list[dict], today: date) -> dict:
    """Aggregates over a best-seller collection's products (ids only, no titles)."""
    prices, disc, new90 = [], 0, 0
    for p in products:
        vs = [v for v in (p.get("variants") or []) if isinstance(v, dict)]
        pp = []
        for v in vs:
            try:
                x = float(v.get("price"))
            except (TypeError, ValueError):
                continue
            if x > 0:
                pp.append(x)
        if pp:
            prices.append(min(pp))
        try:
            disc += any(
                float(v.get("compare_at_price") or 0) > float(v.get("price"))
                for v in vs
            )
        except (TypeError, ValueError):
            pass
        try:
            new90 += (
                today - date.fromisoformat(str(p.get("created_at"))[:10])
            ).days <= 90
        except ValueError:
            pass
    n = len(products)
    return {
        "best_n": n,
        "best_product_ids": [p.get("id") for p in products if p.get("id")],
        "best_price_median": _quantile(prices, 0.5),
        "best_discount_share": round(disc / n, 3) if n else None,
        "best_added_90d_share": round(new90 / n, 3) if n else None,
    }


def _best_one(hit: dict, pause: float, today: date) -> dict:
    """Two requests: /collections.json, then the best-seller collection's feed.
    Never uses sort_by (robots.txt forbids it, decision 0021)."""
    d = hit["domain"]
    base = f"https://{hit.get('final_host') or d}"
    row = {"domain": d, "tranco_rank": hit["tranco_rank"]}
    s = webmeta._session()
    try:
        rp = _robots(s, base)
        url = base + "/collections.json?limit=250"
        if not rp.can_fetch(webmeta.UA, url):
            row["feed_allowed"] = False
            return row
        time.sleep(pause)
        r = s.get(url, timeout=30)
        if not r.ok:
            row["error"] = f"HTTP{r.status_code}"
            return row
        cols = r.json().get("collections") or []
        row["collections_seen"] = len(cols)
        pick = pick_best_collection(cols)
        if not pick:
            row["best_collection"] = None
            return row
        row["best_collection"] = pick["handle"]
        feed = f"{base}/collections/{pick['handle']}/products.json?limit=50"
        if not rp.can_fetch(webmeta.UA, feed):
            row["feed_allowed"] = False
            return row
        time.sleep(pause)
        r = s.get(feed, timeout=30)
        if not r.ok:
            row["error"] = f"HTTP{r.status_code}"
            return row
        row.update(summarize_best(r.json().get("products") or [], today))
    except Exception as exc:
        row["error"] = type(exc).__name__
    return row


def run_best(domains: list[str], workers: int, pause: float) -> dict:
    """Best-seller collection evidence for a chosen list of stores."""
    metas = latest_good(_all_rows("web_meta"))
    rows_all = _all_rows("web_store_best")
    done = set(latest_good(rows_all)) | gave_up(rows_all)
    todo = [metas[d] for d in domains if d in metas and d not in done]
    today = datetime.now(timezone.utc).date()
    print(f"best: {len(todo)} to read", file=sys.stderr, flush=True)
    rows = _parallel(lambda h: _best_one(h, pause, today), todo, workers)
    run = store.record_run(
        "web_store_best",
        rows,
        source="shopify_collections_json",
        trust="data",
        params={"n": len(rows)},
        note="merchant best-seller collection; no sort_by (robots.txt); ids and aggregates only",
    )
    got = sum(1 for r in rows if r.get("best_n"))
    print(
        f"best: {len(rows)} stores, {got} with a best-seller collection",
        file=sys.stderr,
    )
    return {"web_store_best": (run, len(rows))}


def _home_one(hit: dict, pause: float) -> dict:
    """Homepage only: social accounts linked, ad pixels, apps. One request."""
    d = hit["domain"]
    base = f"https://{hit.get('final_host') or d}"
    row = {"domain": d, "tranco_rank": hit["tranco_rank"]}
    s = webmeta._session()
    try:
        rp = _robots(s, base)
        if not rp.can_fetch(webmeta.UA, base + "/"):
            row["home_allowed"] = False
            return row
        time.sleep(pause)
        r = s.get(base + "/", timeout=30)
        row["home_status"] = r.status_code
        if not r.ok:
            row["error"] = f"HTTP{r.status_code}"
            return row
        html = r.text
        row.update(homepage_signals(html))
        row["social_handles"] = webmeta.social_links(html)
    except Exception as exc:
        row["error"] = type(exc).__name__
    return row


def run_home(domains: list[str], workers: int, pause: float) -> dict:
    """Homepage signals for a chosen list of stores (e.g. the top-ranked)."""
    metas = latest_good(_all_rows("web_meta"))
    done = set(latest_good(_all_rows("web_store_home"))) | gave_up(
        _all_rows("web_store_home")
    )
    todo = [metas[d] for d in domains if d in metas and d not in done]
    print(f"home: {len(todo)} to read", file=sys.stderr, flush=True)
    rows = _parallel(lambda h: _home_one(h, pause), todo, workers)
    run = store.record_run(
        "web_store_home",
        rows,
        source="shopify_homepage",
        trust="data",
        params={"n": len(rows)},
        note="one homepage request per store, robots.txt respected; social links, pixels, apps",
    )
    print(
        f"home: {len(rows)} stores, {sum(1 for r in rows if not r.get('error'))} ok",
        file=sys.stderr,
    )
    return {"web_store_home": (run, len(rows))}


def _deep_one(hit: dict, pages: int, pause: float, rules, today: date) -> dict:
    d = hit["domain"]
    host = hit.get("final_host") or d
    base = f"https://{host}"
    row = {"domain": d, "tranco_rank": hit["tranco_rank"]}
    if pk_store(hit):
        row["market"] = "pk"
    s = webmeta._session()
    try:
        rp = _robots(s, base)
        prods: list[dict] = []
        total = hit.get("published_products") or 0
        last = max(1, math.ceil(total / 250)) if total else 1
        wanted = list(range(1, min(pages, last) + 1))
        if last > pages and last <= 100:
            wanted.append(last)  # the last page holds the oldest products
        for pg in wanted:
            url = f"{base}/products.json?limit=250&page={pg}"
            if not rp.can_fetch(webmeta.UA, url):
                row["feed_allowed"] = False
                break
            time.sleep(pause)
            r = s.get(url, timeout=30)
            if not r.ok:
                row["feed_status"] = r.status_code
                break
            got = r.json().get("products") or []
            prods += got
            if len(got) < 250:
                break
        row.update(summarize_feed(prods, hit.get("shop_name") or "", d, rules, today))
        if rp.can_fetch(webmeta.UA, base + "/"):
            time.sleep(pause)
            html = s.get(base + "/", timeout=30).text
            row.update(homepage_signals(html))
            handle = next((p.get("handle") for p in prods if p.get("handle")), None)
            page = f"{base}/products/{handle}" if handle else None
            if page and rp.can_fetch(webmeta.UA, page):
                time.sleep(pause)
                cnt, val = webmeta.aggregate_rating(
                    webmeta.jsonld(s.get(page, timeout=30).text)
                )
                row.update(sample_review_count=cnt, sample_rating=val)
        txt = webmeta.dns(s, d, "TXT")
        row["dns_signals"] = webmeta.txt_signals(txt)
        row["mx"] = sorted(
            {m.split()[-1].rstrip(".").lower() for m in webmeta.dns(s, d, "MX") if m}
        )
    except Exception as exc:
        row["error"] = type(exc).__name__
    model, why = business_model(row, "dropship_app" in (row.get("traffic_tags") or []))
    row["business_model"], row["business_model_why"] = model, why
    return row


def us_store(m: dict) -> bool:
    """Sells to the US in dollars: USD storefront, and US-based or ships to the US."""
    return m.get("currency") == "USD" and (
        m.get("country") == "US" or bool(m.get("ships_to_us"))
    )


def pk_store(m: dict) -> bool:
    """Sells to Pakistan in rupees: PKR storefront (owner, 2026-11-22).

    Currency, not the registered country: Pakistani brands registered in the
    UK, US or UAE still price in PKR for Pakistani buyers."""
    return m.get("currency") == "PKR"


MARKETS = {"us": us_store, "pk": pk_store}


def in_market(m: dict, market: str | None) -> bool:
    """True when the store sells in `market` ("us", "pk"); None means any market."""
    return market is None or MARKETS[market](m)


def deep_targets(
    max_stores: int,
    us_only: bool = True,
    refresh: bool = False,
    market: str | None = None,
) -> list[dict]:
    """Stores with a working /meta.json, best Tranco rank first, not yet profiled."""
    done = set() if refresh else _done("web_store_deep")
    metas = {}
    for r in _all_rows("web_meta"):
        if r.get("shop_id"):
            metas[r["domain"]] = r
    out = []
    for m in sorted(metas.values(), key=lambda r: r["tranco_rank"]):
        if m["domain"] in done:
            continue
        if not in_market(m, market or ("us" if us_only else None)):
            continue
        out.append(m)
    return out[:max_stores]


def run_deep(
    max_stores: int,
    workers: int,
    pages: int,
    pause: float,
    us_only: bool,
    refresh: bool = False,
    batch: int = 100,
    market: str | None = None,
) -> dict:
    rules = load_rules()
    today = datetime.now(timezone.utc).date()
    todo = deep_targets(max_stores, us_only, refresh, market)
    out = {}
    for i in range(0, len(todo), batch):
        chunk = todo[i : i + batch]
        rows = _parallel(
            lambda h: _deep_one(h, pages, pause, rules, today), chunk, workers
        )
        run = store.record_run(
            "web_store_deep",
            rows,
            source="shopify_storefront+google_public_dns",
            trust="data",
            params={
                "n": len(chunk),
                "pages": pages,
                "us_only": us_only,
                "market": market or ("us" if us_only else "all"),
            },
            note="robots.txt respected; feed aggregates (no titles), homepage tags, DNS TXT/MX",
        )
        print(f"deep batch {i}: {len(rows)} stores", file=sys.stderr, flush=True)
        out[f"web_store_deep {i}"] = (run, len(rows))
    return out


def _light_one(hit: dict, pause: float, rules, today: date) -> dict:
    """Cheap screen: one page of the feed, no homepage, no DNS. Enough for the
    business model, price band, categories and release rhythm."""
    d = hit["domain"]
    base = f"https://{hit.get('final_host') or d}"
    row = {"domain": d, "tranco_rank": hit["tranco_rank"]}
    if pk_store(hit):
        row["market"] = "pk"
    s = webmeta._session()
    try:
        rp = _robots(s, base)
        url = base + "/products.json?limit=250"
        if not rp.can_fetch(webmeta.UA, url):
            row["feed_allowed"] = False
            return row
        time.sleep(pause)
        r = s.get(url, timeout=30)
        row["feed_status"] = r.status_code
        if not r.ok:
            row["error"] = f"HTTP{r.status_code}"
            return row
        row.update(
            summarize_feed(
                r.json().get("products") or [],
                hit.get("shop_name") or "",
                d,
                rules,
                today,
            )
        )
        row["business_model"], row["business_model_why"] = business_model(row)
    except Exception as exc:
        row["error"] = type(exc).__name__
    return row


def run_light(
    max_stores: int,
    workers: int,
    pause: float,
    stride: int = 1,
    batch: int = 300,
    new_first: bool = False,
    market: str = "us",
    domains: set[str] | None = None,
) -> dict:
    """domains: re-read exactly these stores (any market, even if done), e.g. a
    hand-check set after a rule change that needs new evidence."""
    rules = load_rules()
    today = datetime.now(timezone.utc).date()
    done = set() if domains else _done("web_store_light")
    metas = latest_good(_all_rows("web_meta"))
    todo = [
        m
        for m in sorted(metas.values(), key=lambda r: r["tranco_rank"])
        if m.get("shop_id")
        and (m["domain"] in domains if domains else in_market(m, market))
        and m["domain"] not in done
    ][::stride]  # stride spreads a sample over the whole rank range
    if new_first:
        todo = _new_first(todo, new_hits())
    todo = todo[:max_stores]
    out = {}
    for i in range(0, len(todo), batch):
        chunk = todo[i : i + batch]
        rows = _parallel(lambda h: _light_one(h, pause, rules, today), chunk, workers)
        run = store.record_run(
            "web_store_light",
            rows,
            source="shopify_products_json",
            trust="data",
            params={"n": len(chunk), "market": market},
            note="one feed page per store, robots.txt respected; aggregates only",
        )
        ok = sum(1 for r in rows if r.get("business_model"))
        print(
            f"light batch {i}: {len(rows)} stores, {ok} labelled",
            file=sys.stderr,
            flush=True,
        )
        out[f"web_store_light {i}"] = (run, len(rows))
    return out


def relabel() -> dict:
    """Recompute business_model for every profiled store from its saved evidence.

    Rule changes need no refetching: the evidence is already in the lake. Writes
    one new run per dataset (deep and light) holding the latest good row per domain."""
    out = {}
    metas = latest_good(_all_rows("web_meta"))
    for ds in ("web_store_deep", "web_store_light"):
        latest = latest_good(_all_rows(ds))
        if not latest:
            continue
        rows, changed = [], 0
        for r in latest.values():
            if not r.get("products_sampled"):
                rows.append(r)
                continue
            m = metas.get(r["domain"], {})
            if pk_store(m):
                r = {**r, "market": "pk"}
            ls = line_share(r, m.get("shop_name") or "", r["domain"])
            if ls is not None:
                r = {**r, "line_vendor_share": ls}
            model, why = business_model(
                r, "dropship_app" in (r.get("traffic_tags") or [])
            )
            changed += model != r.get("business_model")
            rows.append({**r, "business_model": model, "business_model_why": why})
        run = store.record_run(
            ds,
            rows,
            source="relabel",
            trust="data",
            params={"relabel": True, "changed": changed},
            note="business_model recomputed from saved evidence; no refetch",
        )
        print(
            f"relabel {ds}: {len(rows)} stores, {changed} labels changed",
            file=sys.stderr,
        )
        out[f"{ds} (relabel)"] = (run, len(rows))
    return out


def run_ranks(days_back: list[int]) -> dict:
    """Tranco rank of every Shopify hit on earlier list dates (rank growth)."""
    hits = {h["domain"] for h in _shop_hits()}
    today = datetime.now(timezone.utc).date()
    rows = []
    dates = []
    for back in days_back:
        dt = (today - timedelta(days=back)).isoformat()
        try:
            lst = webmeta._tranco_list(dt)
        except Exception as exc:
            print(f"tranco list {dt}: {exc}", file=sys.stderr)
            continue
        dates.append(dt)
        top = lst.top(1_000_000)
        for rank, d in enumerate(top, 1):
            if d in hits:
                rows.append(
                    {
                        "domain": d,
                        "list_date": dt,
                        "list_id": lst.list_id,
                        "tranco_rank": rank,
                    }
                )
    run = store.record_run(
        "web_ranks",
        rows,
        source="tranco",
        trust="data",
        params={"dates": dates, "stores": len(hits)},
        note="Tranco default list on earlier dates; ranks of scanned Shopify stores only",
    )
    return {"web_ranks": (run, len(rows))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Shopify store profiler (public records)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("meta")
    m.add_argument("--max-stores", type=int, default=3000)
    m.add_argument("--workers", type=int, default=4)
    m.add_argument("--pause", type=float, default=1.0)
    m.add_argument("--new-first", action="store_true", help="newly discovered first")
    d = sub.add_parser("deep")
    d.add_argument("--max-stores", type=int, default=300)
    d.add_argument("--workers", type=int, default=4)
    d.add_argument("--pages", type=int, default=4)
    d.add_argument("--pause", type=float, default=1.0)
    d.add_argument("--all-countries", action="store_true")
    d.add_argument("--market", choices=sorted(MARKETS), help="us (default) or pk")
    d.add_argument(
        "--refresh", action="store_true", help="re-profile stores already done"
    )
    lt = sub.add_parser(
        "light", help="one feed page per US store: business model screen"
    )
    lt.add_argument("--max-stores", type=int, default=30)
    lt.add_argument("--workers", type=int, default=6)
    lt.add_argument("--pause", type=float, default=1.0)
    lt.add_argument("--stride", type=int, default=1, help="take every Nth store")
    lt.add_argument("--new-first", action="store_true", help="newly discovered first")
    lt.add_argument("--market", choices=sorted(MARKETS), default="us")
    lt.add_argument("--domains", help="file with one domain per line: re-read these")
    hp = sub.add_parser("home", help="homepage signals for stores listed in a file")
    hp.add_argument("--domains", required=True, help="file, one domain per line")
    hp.add_argument("--workers", type=int, default=1)
    hp.add_argument("--pause", type=float, default=4.0)
    bp = sub.add_parser(
        "best", help="best-seller collection of stores listed in a file"
    )
    bp.add_argument("--domains", required=True, help="file, one domain per line")
    bp.add_argument("--workers", type=int, default=1)
    bp.add_argument("--pause", type=float, default=4.0)
    sub.add_parser("relabel", help="recompute business_model from saved evidence")
    r = sub.add_parser("ranks")
    r.add_argument("--days-back", type=int, nargs="+", default=[90, 365])
    a = ap.parse_args(argv)
    if a.cmd == "meta":
        out = run_meta(a.max_stores, a.workers, a.pause, new_first=a.new_first)
    elif a.cmd == "deep":
        out = run_deep(
            a.max_stores,
            a.workers,
            a.pages,
            a.pause,
            not a.all_countries,
            a.refresh,
            market=a.market,
        )
    elif a.cmd == "light":
        out = run_light(
            a.max_stores,
            a.workers,
            a.pause,
            a.stride,
            new_first=a.new_first,
            market=a.market,
            domains=(
                {x.strip() for x in open(a.domains) if x.strip()} if a.domains else None
            ),
        )
    elif a.cmd == "home":
        out = run_home(
            [x.strip() for x in open(a.domains) if x.strip()], a.workers, a.pause
        )
    elif a.cmd == "best":
        out = run_best(
            [x.strip() for x in open(a.domains) if x.strip()], a.workers, a.pause
        )
    elif a.cmd == "relabel":
        out = relabel()
    else:
        out = run_ranks(a.days_back)
    for k, (run, n) in out.items():
        print(f"{k}: run {run}, {n} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
