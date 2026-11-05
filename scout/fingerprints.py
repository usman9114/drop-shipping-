"""Supply fingerprints: read the hidden traces a store leaves and estimate its source.

Workstream W2 of docs/plan/supply-fingerprints-plan.md. Public pages only
(homepage, one product page, /products.json page 1); robots.txt is read and
obeyed for every URL; one honest User-Agent (webmeta.UA); requests to one host
are sequential with a pause, many hosts run in parallel; no rendering, no
stealth, no login, no checkout. We keep a small signal dict per store: ids,
counts, shares and country names. Never HTML, product text or images.

Layout
  SIGNATURES        data table of app/script/feed signatures (edit data, not code)
  WEIGHTS           every weight used by supply_estimate, in one place
  page_signals      pure: HTML -> signature ids, theme, app-embed handles, script hosts
  feed_signals      pure: products.json list -> counts and shares
  supply_estimate   pure: (page, feed) -> source_guess, warehouse_guess, confidence, evidence
  run / main        network + lake (python -m scout.fingerprints --domains-file X)

TODO(owner merge): SIGNATURES is seeded from what we already know. Entries will
be merged from the W1 research docs docs/research/33a-fingerprints-aliexpress-tools.md,
33b-fingerprints-us-suppliers-3pl.md and 33c-fingerprints-pod-themes-tracking.md.
Anything not yet seen on a live store stays evidence='unverified'.

Usage:
    python -m scout.fingerprints --domains-file domains.txt --max-concurrent 8 --pause 1.0
"""

from __future__ import annotations

import argparse
import asyncio
import re
import statistics
import sys
import time
import urllib.robotparser
from collections import Counter, defaultdict

from scout import store, stores, webmeta

# --- signature table ---------------------------------------------------------
# family: importer | supplier | 3pl | pod | tracking | review_import | theme | fomo
# where: page_source (homepage / product page HTML) | feed (vendor, tags, handles, SKUs, image URLs)
# implies_source: aliexpress | cj | 1688 | us_supplier | pod | wholesale |
#                 china_shipping | domestic_shipping | none
# evidence: observed (seen on a live store by us) | docs (vendor docs/listing) | unverified
SIGNATURES: list[dict] = [
    {
        "id": "aliorders",
        "family": "importer",
        "name": "AliOrders (FireApps)",
        "where": "page_source",
        "pattern": r"aliorders\.fireapps\.io|fireapps\.io/[^\"' ]*aliorders",
        "implies_source": "aliexpress",
        "strength": "strong",
        "evidence": "observed",
        "note": "seen on woodenearth.com 2026-11-05",
    },
    {
        "id": "dsers",
        "family": "importer",
        "name": "DSers",
        "where": "page_source",
        "pattern": r"dsers\.com|\bdsers-",
        "implies_source": "aliexpress",
        "strength": "strong",
        "evidence": "unverified",
        "note": "AliExpress official partner importer",
    },
    {
        "id": "dsers_feed",
        "family": "importer",
        "name": "DSers (vendor/tag)",
        "where": "feed",
        "pattern": r"\bdsers\b",
        "implies_source": "aliexpress",
        "strength": "medium",
        "evidence": "unverified",
        "note": "vendor or tag text",
    },
    {
        "id": "cjdropshipping",
        "family": "supplier",
        "name": "CJdropshipping",
        "where": "page_source",
        "pattern": r"cjdropshipping\.com|cj-?dropshipping",
        "implies_source": "cj",
        "strength": "strong",
        "evidence": "unverified",
        "note": "app or tracking links",
    },
    {
        "id": "cj_feed",
        "family": "supplier",
        "name": "CJ (vendor/tag)",
        "where": "feed",
        "pattern": r"cj ?dropshipping|cjdropshipping",
        "implies_source": "cj",
        "strength": "medium",
        "evidence": "unverified",
        "note": "vendor or tag text",
    },
    {
        "id": "zendrop",
        "family": "importer",
        "name": "Zendrop",
        "where": "page_source",
        "pattern": r"zendrop\.com|\bzendrop-",
        "implies_source": "aliexpress",
        "strength": "strong",
        "evidence": "unverified",
        "note": "mixed China and US suppliers; AliExpress is the default guess",
    },
    {
        "id": "zendrop_feed",
        "family": "importer",
        "name": "Zendrop (vendor/tag)",
        "where": "feed",
        "pattern": r"\bzendrop\b",
        "implies_source": "aliexpress",
        "strength": "medium",
        "evidence": "unverified",
        "note": "vendor or tag text",
    },
    {
        "id": "spocket",
        "family": "supplier",
        "name": "Spocket",
        "where": "page_source",
        "pattern": r"spocket\.co",
        "implies_source": "us_supplier",
        "strength": "strong",
        "evidence": "unverified",
        "note": "US/EU supplier marketplace",
    },
    {
        "id": "spocket_feed",
        "family": "supplier",
        "name": "Spocket (vendor/tag)",
        "where": "feed",
        "pattern": r"\bspocket\b",
        "implies_source": "us_supplier",
        "strength": "medium",
        "evidence": "unverified",
        "note": "vendor or tag text",
    },
    {
        "id": "autods",
        "family": "importer",
        "name": "AutoDS",
        "where": "page_source",
        "pattern": r"autods\.com",
        "implies_source": "aliexpress",
        "strength": "strong",
        "evidence": "unverified",
        "note": "multi-source importer",
    },
    {
        "id": "autods_feed",
        "family": "importer",
        "name": "AutoDS (vendor/tag)",
        "where": "feed",
        "pattern": r"\bautods\b",
        "implies_source": "aliexpress",
        "strength": "medium",
        "evidence": "unverified",
        "note": "vendor or tag text",
    },
    {
        "id": "syncee",
        "family": "supplier",
        "name": "Syncee",
        "where": "page_source",
        "pattern": r"syncee\.(?:co|io|com)",
        "implies_source": "wholesale",
        "strength": "strong",
        "evidence": "unverified",
        "note": "EU/US wholesale marketplace",
    },
    {
        "id": "alidropship",
        "family": "importer",
        "name": "AliDropship",
        "where": "page_source",
        "pattern": r"alidropship\.com",
        "implies_source": "aliexpress",
        "strength": "strong",
        "evidence": "unverified",
        "note": "",
    },
    {
        "id": "oberlo",
        "family": "importer",
        "name": "Oberlo",
        "where": "page_source",
        "pattern": r"oberlo\.com",
        "implies_source": "aliexpress",
        "strength": "medium",
        "evidence": "unverified",
        "note": "shut down 2022; leftovers only",
    },
    {
        "id": "printful",
        "family": "pod",
        "name": "Printful",
        "where": "page_source",
        "pattern": r"printful\.com",
        "implies_source": "pod",
        "strength": "strong",
        "evidence": "unverified",
        "note": "",
    },
    {
        "id": "printify",
        "family": "pod",
        "name": "Printify",
        "where": "page_source",
        "pattern": r"printify\.com",
        "implies_source": "pod",
        "strength": "strong",
        "evidence": "unverified",
        "note": "",
    },
    {
        "id": "gelato",
        "family": "pod",
        "name": "Gelato",
        "where": "page_source",
        "pattern": r"gelato\.com|gelatoapi",
        "implies_source": "pod",
        "strength": "strong",
        "evidence": "unverified",
        "note": "",
    },
    {
        "id": "ali_reviews",
        "family": "review_import",
        "name": "Ali Reviews",
        "where": "page_source",
        "pattern": r"ali[-_ ]?reviews|alireviews",
        "implies_source": "aliexpress",
        "strength": "medium",
        "evidence": "unverified",
        "note": "imports AliExpress reviews",
    },
    {
        "id": "ryviu",
        "family": "review_import",
        "name": "Ryviu",
        "where": "page_source",
        "pattern": r"ryviu\.(?:com|io)|\bryviu-",
        "implies_source": "none",
        "strength": "weak",
        "evidence": "unverified",
        "note": "review importer; also used by real brands",
    },
    {
        "id": "kudosi",
        "family": "review_import",
        "name": "Kudosi",
        "where": "page_source",
        "pattern": r"kudosi",
        "implies_source": "none",
        "strength": "weak",
        "evidence": "unverified",
        "note": "review importer",
    },
    {
        "id": "loox",
        "family": "review_import",
        "name": "Loox",
        "where": "page_source",
        "pattern": r"loox\.io",
        "implies_source": "none",
        "strength": "weak",
        "evidence": "unverified",
        "note": "photo reviews; common on real brands too",
    },
    {
        "id": "parcelpanel",
        "family": "tracking",
        "name": "ParcelPanel",
        "where": "page_source",
        "pattern": r"parcelpanel\.com|parcel-panel",
        "implies_source": "china_shipping",
        "strength": "weak",
        "evidence": "unverified",
        "note": "order tracking; popular with China-shipped stores",
    },
    {
        "id": "track123",
        "family": "tracking",
        "name": "Track123",
        "where": "page_source",
        "pattern": r"track123\.com",
        "implies_source": "china_shipping",
        "strength": "weak",
        "evidence": "unverified",
        "note": "",
    },
    {
        "id": "17track",
        "family": "tracking",
        "name": "17TRACK",
        "where": "page_source",
        "pattern": r"17track\.net",
        "implies_source": "china_shipping",
        "strength": "medium",
        "evidence": "unverified",
        "note": "China-carrier tracking aggregator",
    },
    {
        "id": "aftership",
        "family": "tracking",
        "name": "AfterShip",
        "where": "page_source",
        "pattern": r"aftership\.com",
        "implies_source": "none",
        "strength": "weak",
        "evidence": "unverified",
        "note": "used by brands and dropshippers alike",
    },
]

# --- weights (principle 4: one place) ----------------------------------------
# A source's score is the noisy-or of its contributions: 1 - prod(1 - w).
# Strong signals dominate; weak ones can only nudge. All weights are clamped to [0, 1].
# Calibration is pending W3 (docs/research/35); until then these are judgement, not measurement.
WEIGHTS = {
    # page signature: base weight by strength, scaled by how well attested the entry is
    "strength": {"strong": 0.6, "medium": 0.3, "weak": 0.1},
    "evidence_mult": {"observed": 1.0, "docs": 0.9, "unverified": 0.5},
    # feed rules: (min share or count to fire, {source: weight})
    "feed": {
        "ae_image_share": (0.05, {"aliexpress": 0.55}),
        "o1cn_share": (0.05, {"aliexpress": 0.25, "1688": 0.15}),
        "ae_item_id_share": (0.02, {"aliexpress": 0.6}),
        "dsers_sku_share": (0.05, {"aliexpress": 0.5}),
        "cj_sku_share": (0.05, {"cj": 0.6}),
        "ships_from": (1, {"aliexpress": 0.5}),  # option present (count of products)
        "vendor_supplier_share": (0.2, {"aliexpress": 0.2}),
        "boilerplate_share": (0.1, {"aliexpress": 0.25}),
        "cjk_share": (
            0.05,
            {"1688": 0.12, "aliexpress": 0.05},
        ),  # weak: pilot showed a real brand at 14%
    },
    # source-less dropship behaviour: cannot pick a source, only nudge confidence
    "generic": {
        "bulk_burst_big": 0.2,
        "bulk_burst_small": 0.1,
        "grams_zero": 0.1,
        "compare_ratio": 0.1,
    },
    "bulk_burst_big_n": 50,
    "bulk_burst_small_n": 20,
    "grams_zero_share": 0.8,
    "compare_ratio_min": 2.0,
    "family_nudge": 0.05,  # theme / fomo / review_import with no source implication
    "contested_penalty": 0.5,  # confidence -= this * runner-up score
    "generic_nudge_cap": 0.1,
    "min_source_score": 0.2,  # below this the source is 'unknown'
    "min_generic_for_dropship": 0.25,
    "assumed_china_min_conf": 0.5,
}

# --- patterns ---------------------------------------------------------------
_THEME_BLOCK = re.compile(r"Shopify\.theme\s*=\s*\{(.{0,600}?)\}", re.S)
_THEME_NAME = re.compile(r'"name"\s*:\s*"([^"]{1,80})"')
_THEME_ID = re.compile(r'"theme_store_id"\s*:\s*(\d+|null)')
_EMBED = re.compile(
    r"cdn\.shopify\.com/extensions/[0-9a-f][0-9a-f-]{7,}/([a-z0-9][a-z0-9_-]*?)-\d[\w.]*/"
)
_URL_HOST = re.compile(r"https?:?(?:\\?/){2}([a-z0-9.-]+\.[a-z]{2,})", re.I)

_O1CN = re.compile(r"O1CN01[0-9A-Za-z]{6,}")
_ITEM_ID = re.compile(r"(?<!\d)1005\d{12}(?!\d)")
_DSERS_SKU = stores.DSERS_SKU  # one definition, shared with the classifier
_CJ_SKU = stores.CJ_SKU
_SHIPS_FROM = re.compile(r"^\s*ships?\s*from\s*$", re.I)
_SUPPLIER_VENDOR = re.compile(
    r"^shop\d{3,}|\bstore\d*$|\b(?:trading|factory|international)\b|co\.?,?\s*ltd|"
    + stores.DROPSHIP_VENDORS.pattern,
    re.I,
)
_BOILERPLATE = re.compile(
    r"manual\s+measurement|light\s+and\s+screen\s+difference|"
    r"allow\s+\d\s*[-~]\s*\d\s*cm|package\s+(?:includes?|contents?)\s*:\s*\d+\s*[x×]",
    re.I,
)
_COUNTRY_ALIAS = {
    "cn": "China",
    "china": "China",
    "china mainland": "China",
    "mainland china": "China",
    "us": "United States",
    "usa": "United States",
    "united states": "United States",
}
_CJK = re.compile(r"[一-鿿]")

_COMPILED = [(s, re.compile(s["pattern"], re.I)) for s in SIGNATURES]
_BY_ID = {s["id"]: s for s in SIGNATURES}


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


# --- extractors (pure) -------------------------------------------------------
def page_signals(html: str) -> dict:
    """HTML in, signal dict out. Nothing from the page text is kept."""
    html = html or ""
    ids = sorted(
        s["id"]
        for s, rx in _COMPILED
        if s["where"] == "page_source" and rx.search(html)
    )
    theme_name, theme_id = None, None
    m = _THEME_BLOCK.search(html)
    if m:
        n = _THEME_NAME.search(m.group(1))
        t = _THEME_ID.search(m.group(1))
        theme_name = n.group(1) if n else None
        theme_id = int(t.group(1)) if t and t.group(1) != "null" else None
    embeds = sorted(set(_EMBED.findall(html)))
    hosts: set[str] = set()
    for am in re.finditer(r"asyncLoad", html):
        window = html[am.start() : am.start() + 4000]
        hosts.update(h.lower() for h in _URL_HOST.findall(window))
    return {
        "signature_ids": ids,
        "theme_name": theme_name,
        "theme_store_id": theme_id,
        "app_embed_handles": embeds,
        "asyncload_hosts": sorted(hosts),
    }


def _country(v: str) -> str | None:
    """Normalise a 'Ships From' value: case-fold, alias CN/China Mainland, drop placeholders."""
    v = " ".join(str(v).split())
    if not v or v.lower() in ("default", "default title", "other"):
        return None
    return _COUNTRY_ALIAS.get(v.lower(), v.title())


def _share(k: int, n: int) -> float:
    return round(k / n, 3) if n else 0.0


def _tags(p: dict) -> list[str]:
    t = p.get("tags") or []
    return [str(x) for x in (t.split(",") if isinstance(t, str) else t)]


def feed_signals(products: list[dict], domain: str | None = None) -> dict:
    """products.json list in, counts and shares out. No titles, text or URLs kept."""
    items = [p for p in products if isinstance(p, dict)]
    n = len(items)
    c = Counter()
    ships_values: set[str] = set()
    feed_sig_ids: set[str] = set()
    minutes: Counter = Counter()
    nvar = zero_g = 0
    ratios: list[float] = []
    feed_rx = [(s["id"], rx) for s, rx in _COMPILED if s["where"] == "feed"]
    for p in items:
        imgs = [
            str(i.get("src") or "")
            for i in (p.get("images") or [])
            if isinstance(i, dict)
        ]
        vs = [v for v in (p.get("variants") or []) if isinstance(v, dict)]
        skus = [str(v.get("sku") or "") for v in vs if v.get("sku")]
        handle = str(p.get("handle") or "")
        tags = _tags(p)
        vendor = str(p.get("vendor") or "")
        idtext = " ".join([handle, *skus, *tags])
        c["ae_image"] += any(stores.AE_IMAGE.search(u) for u in imgs)
        c["o1cn"] += any(_O1CN.search(u) for u in imgs)
        c["ae_item_id"] += bool(_ITEM_ID.search(idtext))
        c["dsers_sku"] += any(_DSERS_SKU.search(s) for s in skus)
        c["cj_sku"] += any(_CJ_SKU.search(s) for s in skus)
        if vendor and not (domain and stores.vendor_is_shop(vendor, "", domain)):
            c["vendor_supplier"] += bool(_SUPPLIER_VENDOR.search(vendor))
        blob = f"{vendor} {' '.join(tags)}"
        feed_sig_ids.update(i for i, rx in feed_rx if rx.search(blob))
        body = str(p.get("body_html") or "")
        c["boilerplate"] += bool(_BOILERPLATE.search(body))
        c["cjk"] += bool(_CJK.search(f"{p.get('title') or ''} {body}"))
        for o in p.get("options") or []:
            if isinstance(o, dict) and _SHIPS_FROM.match(str(o.get("name") or "")):
                c["ships_from"] += 1
                ships_values.update(
                    x for x in map(_country, o.get("values") or []) if x
                )
        if p.get("created_at"):
            minutes[str(p["created_at"])[:16]] += 1
        for v in vs:
            nvar += 1
            try:
                if float(v.get("grams") or 0) == 0:
                    zero_g += 1
            except (TypeError, ValueError):
                pass
            try:
                price, cmp_ = (
                    float(v.get("price")),
                    float(v.get("compare_at_price") or 0),
                )
                if price > 0 and cmp_ > price:
                    ratios.append(cmp_ / price)
            except (TypeError, ValueError):
                pass
    return {
        "n_products": n,
        "n_variants": nvar,
        "ae_image_share": _share(c["ae_image"], n),
        "o1cn_share": _share(c["o1cn"], n),
        "ae_item_id_share": _share(c["ae_item_id"], n),
        "dsers_sku_share": _share(c["dsers_sku"], n),
        "cj_sku_share": _share(c["cj_sku"], n),
        "ships_from": c["ships_from"],
        "ships_from_values": sorted(ships_values),
        "vendor_supplier_share": _share(c["vendor_supplier"], n),
        "boilerplate_count": c["boilerplate"],
        "boilerplate_share": _share(c["boilerplate"], n),
        "cjk_count": c["cjk"],
        "cjk_share": _share(c["cjk"], n),
        "bulk_burst_max": max(minutes.values(), default=0),
        "grams_zero_share": _share(zero_g, nvar),
        "compare_ratio_median": round(statistics.median(ratios), 2) if ratios else None,
        "signature_ids": sorted(feed_sig_ids),
    }


def _noisy_or(ws: list[float]) -> float:
    p = 1.0
    for w in ws:
        p *= 1 - _clamp(w)
    return round(1 - p, 3)


def supply_estimate(page: dict | None, feed: dict | None) -> dict:
    """Combine page and feed signals. Weights live in WEIGHTS; see the docstring there."""
    page, feed = page or {}, feed or {}
    W = WEIGHTS
    src: dict[str, list[float]] = defaultdict(list)
    ship: dict[str, list[float]] = defaultdict(list)
    generic: list[float] = []
    evidence: list[str] = []

    for sid in sorted(
        set(page.get("signature_ids") or []) | set(feed.get("signature_ids") or [])
    ):
        s = _BY_ID.get(sid)
        if not s:
            continue
        w = _clamp(W["strength"][s["strength"]] * W["evidence_mult"][s["evidence"]])
        imp = s["implies_source"]
        if imp in ("china_shipping", "domestic_shipping"):
            ship[imp].append(w)
        elif imp == "none":
            if s["family"] in ("theme", "fomo", "review_import"):
                generic.append(W["family_nudge"])
        else:
            src[imp].append(w)
        evidence.append(f"signature {sid} ({s['strength']}/{s['evidence']}) -> {imp}")

    for key, (thr, targets) in W["feed"].items():
        val = feed.get(key) or 0
        if val and val >= thr:
            for source, w in targets.items():
                src[source].append(w)
            evidence.append(f"feed {key}={val} -> " + ",".join(targets))

    if (feed.get("bulk_burst_max") or 0) >= W["bulk_burst_big_n"]:
        generic.append(W["generic"]["bulk_burst_big"])
        evidence.append(
            f"bulk import burst {feed['bulk_burst_max']} products in one minute"
        )
    elif (feed.get("bulk_burst_max") or 0) >= W["bulk_burst_small_n"]:
        generic.append(W["generic"]["bulk_burst_small"])
        evidence.append(
            f"bulk import burst {feed['bulk_burst_max']} products in one minute"
        )
    if (feed.get("grams_zero_share") or 0) >= W["grams_zero_share"]:
        generic.append(W["generic"]["grams_zero"])
        evidence.append(f"grams=0 on {feed['grams_zero_share']:.0%} of variants")
    if (feed.get("compare_ratio_median") or 0) >= W["compare_ratio_min"]:
        generic.append(W["generic"]["compare_ratio"])
        evidence.append(f"median compare-at/price {feed['compare_ratio_median']}")

    scores = sorted(((_noisy_or(v), k) for k, v in src.items()), reverse=True)
    gscore = _noisy_or(generic)
    best, best_src = scores[0] if scores else (0.0, "unknown")
    second = scores[1][0] if len(scores) > 1 else 0.0
    if best >= W["min_source_score"]:
        guess = best_src
        conf = (
            best
            - W["contested_penalty"] * second
            + min(W["generic_nudge_cap"], gscore * 0.3)
        )
    elif gscore >= W["min_generic_for_dropship"]:
        guess, conf = "unknown_dropship", gscore * 0.5
    else:
        guess, conf = "unknown", 0.0
    conf = round(_clamp(conf), 2)

    values = feed.get("ships_from_values") or []
    if values:
        warehouse = values[0] if len(values) == 1 else "mixed: " + "|".join(values)
        evidence.append(f"'Ships From' option values: {values}")
    elif _noisy_or(ship["china_shipping"]) >= 0.1 and _noisy_or(
        ship["china_shipping"]
    ) > _noisy_or(ship["domestic_shipping"]):
        warehouse = "China"
    elif _noisy_or(ship["domestic_shipping"]) >= 0.1:
        warehouse = "US"
    elif guess in ("aliexpress", "1688") and conf >= W["assumed_china_min_conf"]:
        warehouse = "China (assumed)"
    else:
        warehouse = "unknown"
    return {
        "source_guess": guess,
        "warehouse_guess": warehouse,
        "confidence": conf,
        "evidence": evidence,
    }


# --- fetch (network) ---------------------------------------------------------
def _merge_page(a: dict, b: dict) -> dict:
    return {
        "signature_ids": sorted(set(a["signature_ids"]) | set(b["signature_ids"])),
        "theme_name": a["theme_name"] or b["theme_name"],
        "theme_store_id": a["theme_store_id"] or b["theme_store_id"],
        "app_embed_handles": sorted(
            set(a["app_embed_handles"]) | set(b["app_embed_handles"])
        ),
        "asyncload_hosts": sorted(
            set(a["asyncload_hosts"]) | set(b["asyncload_hosts"])
        ),
    }


def fingerprint_host(domain: str, host: str | None, pause: float) -> dict:
    """Sequential, polite fetch of one store: robots, homepage, products.json, one product page."""
    import requests

    base = f"https://{host or domain}"
    s = requests.Session()
    s.headers["User-Agent"] = webmeta.UA
    row: dict = {"domain": domain, "errors": [], "robots_blocked": []}
    rp = urllib.robotparser.RobotFileParser()
    try:
        r = s.get(base + "/robots.txt", timeout=20)
        rp.parse(r.text.splitlines() if r.ok else [])
    except Exception as exc:
        row["error"] = f"robots:{type(exc).__name__}"
        return row
    time.sleep(pause)

    def get(path: str):
        url = base + path
        if not rp.can_fetch(webmeta.UA, url):
            row["robots_blocked"].append(
                path.split("?")[0] if "/products/" not in path else "/products/*"
            )
            return None
        try:
            resp = s.get(url, timeout=25)
        except Exception as exc:
            row["errors"].append(f"{path.split('?')[0]}:{type(exc).__name__}")
            return None
        finally:
            time.sleep(pause)
        if not resp.ok:
            row["errors"].append(f"{path.split('?')[0]}:HTTP{resp.status_code}")
            return None
        return resp

    page = page_signals("")
    home = get("/")
    if home is not None:
        page = page_signals(home.text)
    products: list[dict] = []
    feed_resp = get("/products.json?limit=250")
    if feed_resp is not None:
        try:
            products = feed_resp.json().get("products") or []
        except ValueError:
            row["errors"].append("products.json:badjson")
    if products and products[0].get("handle"):
        pp = get(f"/products/{products[0]['handle']}")
        if pp is not None:
            page = _merge_page(page, page_signals(pp.text))
    feed = feed_signals(products, domain)
    row.update({"page": page, "feed": feed, "estimate": supply_estimate(page, feed)})
    if not row["errors"]:
        row.pop("errors")
    if not row["robots_blocked"]:
        row.pop("robots_blocked")
    return row


async def fingerprint_many(
    targets: list[dict], max_concurrent: int, pause: float
) -> list[dict]:
    sem = asyncio.Semaphore(max_concurrent)

    async def one(t: dict) -> dict:
        async with sem:
            row = await asyncio.to_thread(
                fingerprint_host, t["domain"], t.get("final_host"), pause
            )
        row.update(
            {
                "tranco_rank": t.get("tranco_rank"),
                "business_model": t.get("business_model"),
            }
        )
        return row

    return await asyncio.gather(*(one(t) for t in targets))


def run(domains: list[str], max_concurrent: int = 8, pause: float = 1.0) -> dict:
    deep = stores.latest_good(stores._all_rows("web_store_deep"))
    light = stores.latest_good(stores._all_rows("web_store_light"))
    meta = stores.latest_good(stores._all_rows("web_meta"))
    targets = []
    for d in domains:
        base = deep.get(d) or light.get(d) or {}
        targets.append(
            {
                "domain": d,
                "final_host": (meta.get(d) or {}).get("final_host"),
                "tranco_rank": base.get("tranco_rank"),
                "business_model": base.get("business_model"),
            }
        )
    rows = asyncio.run(fingerprint_many(targets, max_concurrent, pause))
    runid = store.record_run(
        "web_fingerprints",
        rows,
        source="store_public_pages",
        trust="data",
        params={"n": len(rows), "max_concurrent": max_concurrent, "pause": pause},
        note="supply fingerprints: signature ids, counts and shares only; no page text or images; "
        "one honest UA, robots.txt respected per URL, no rendering",
    )
    guesses = Counter(r.get("estimate", {}).get("source_guess", "error") for r in rows)
    print(
        f"fingerprints: {len(rows)} stores -> {dict(guesses)} run {runid}",
        file=sys.stderr,
    )
    return {"web_fingerprints": (runid, len(rows))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Supply fingerprints for Shopify stores")
    ap.add_argument("--domains-file", required=True, help="one domain per line")
    ap.add_argument("--max-concurrent", type=int, default=8)
    ap.add_argument("--pause", type=float, default=1.0)
    a = ap.parse_args(argv)
    doms = open(a.domains_file, encoding="utf-8").read().split()
    for k, (rid, n) in run(doms, a.max_concurrent, a.pause).items():
        print(f"{k}: run {rid}, {n} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
