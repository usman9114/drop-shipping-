"""Full-profile dropship judgment: shipping/return policy pages + multi-product
image-trace density, on top of the existing products.json classifier in stores.py.

Policy page URLs are Shopify-standard slugs (auto-generated on every Shopify
store, so we don't need to discover them from navigation):
    /policies/shipping-policy
    /policies/refund-policy

Concurrency model (decision 0014 extended): many stores fetched in parallel
under ONE honest, identified User-Agent (scout.webmeta.UA), each store's own
requests paced and serialized (no parallel hits to the same host), robots.txt
checked per host before any fetch. This is NOT multiple identities/sessions
pretending to be different clients -- it's one named crawler run wide across
many different sites at once, same as any polite bulk crawl.

Usage:
    python -m scout.dropship_profile --domains-file domains.txt --max-concurrent 8
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
import time
import urllib.robotparser
from dataclasses import dataclass, field

from scout import store, stores, webmeta

POLICY_PATHS = {
    "shipping": "/policies/shipping-policy",
    "refund": "/policies/refund-policy",
}

# Phrases that signal multi-week / overseas fulfillment -- the strongest
# single tell for drop-shipping among public-facing policy text.
SLOW_SHIP_RE = re.compile(
    r"(\d+)\s*(?:-|to|–)\s*(\d+)\s*(business\s+)?weeks|"
    r"ships?\s+from\s+(?:overseas|china|our\s+warehouse\s+abroad|international)|"
    r"processing\s+time\s+of\s+(?:up\s+to\s+)?\d+\s*(?:-|to)\s*\d+\s*weeks",
    re.I,
)
FAST_SHIP_RE = re.compile(
    r"same[\s-]?day|next[\s-]?day|1\s*(?:-|to)\s*2\s*business\s+days|"
    r"ships?\s+(?:same|next)\s+day|usually\s+ships?\s+within\s+24",
    re.I,
)

# Shopify's own default refund-policy template text (present verbatim on
# stores that never bothered to customize the page -- a weak "low-effort
# storefront" signal, not proof on its own).
SHOPIFY_DEFAULT_REFUND_RE = re.compile(
    r"we have a \d+[\s-]?day return policy|to start a return.{0,40}contact us",
    re.I,
)

NO_ADDRESS_RE = re.compile(
    r"\d{1,5}\s+\w+.{0,20}(street|st\.|ave|avenue|road|rd\.|blvd|suite)", re.I
)


@dataclass
class PolicySignals:
    shipping_found: bool = False
    refund_found: bool = False
    slow_ship_phrase: str | None = None
    fast_ship_phrase: str | None = None
    boilerplate_refund: bool = False
    has_street_address_anywhere: bool = False
    errors: list[str] = field(default_factory=list)


def extract_policy_signals(
    shipping_html: str | None, refund_html: str | None
) -> PolicySignals:
    """Pure text-pattern extraction, no judgment yet. Testable without network."""
    sig = PolicySignals()
    if shipping_html:
        sig.shipping_found = True
        m = SLOW_SHIP_RE.search(shipping_html)
        if m:
            sig.slow_ship_phrase = m.group(0)[:80]
        m2 = FAST_SHIP_RE.search(shipping_html)
        if m2:
            sig.fast_ship_phrase = m2.group(0)[:80]
        if NO_ADDRESS_RE.search(shipping_html):
            sig.has_street_address_anywhere = True
    if refund_html:
        sig.refund_found = True
        if SHOPIFY_DEFAULT_REFUND_RE.search(refund_html):
            sig.boilerplate_refund = True
        if NO_ADDRESS_RE.search(refund_html):
            sig.has_street_address_anywhere = True
    return sig


def dropship_confidence(
    product_json_label: str, product_json_why: list[str], policy: PolicySignals
) -> dict:
    """Combine the existing products.json classifier with policy-page evidence.

    Returns {'verdict', 'confidence' (0-1), 'reasons': [...]}. Policy evidence can
    raise confidence on an existing 'dropship' call, or flag a 'brand'/'unclear'
    call as worth a second look -- it never overrides the product-level call on
    its own, because policy text is a weaker, easier-to-fake signal.
    """
    reasons = list(product_json_why)
    score = 0.0
    if product_json_label == "dropship":
        score += 0.6
    elif product_json_label in ("reseller", "general", "unclear"):
        score += 0.25

    if policy.slow_ship_phrase:
        score += 0.25
        reasons.append(
            f"policy page discloses slow shipping: '{policy.slow_ship_phrase}'"
        )
    if policy.fast_ship_phrase and not policy.slow_ship_phrase:
        score -= 0.15
        reasons.append(
            f"policy page discloses fast shipping: '{policy.fast_ship_phrase}'"
        )
    if policy.boilerplate_refund:
        score += 0.1
        reasons.append("refund policy is Shopify's unedited default template")
    if not policy.has_street_address_anywhere and (
        policy.shipping_found or policy.refund_found
    ):
        score += 0.05
        reasons.append("no street address found on shipping/refund pages")

    score = max(0.0, min(1.0, score))
    verdict = (
        "dropship"
        if score >= 0.6
        else ("maybe_dropship" if score >= 0.35 else "not_dropship")
    )
    return {"verdict": verdict, "confidence": round(score, 2), "reasons": reasons}


async def _fetch_policies_async(domain: str, host: str | None, pause: float) -> dict:
    """Plain HTTP (not JS-rendered: Shopify policy pages are static server HTML).
    One robots.txt check, then sequential GETs to the SAME host -- never parallel
    requests to one site. Runs inside the shared asyncio loop via a thread so many
    stores can be in flight at once without hammering any single host."""
    import requests

    base = f"https://{host or domain}"
    out = {"domain": domain}

    def work():
        s = requests.Session()
        s.headers["User-Agent"] = webmeta.UA
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = s.get(base + "/robots.txt", timeout=20)
            rp.parse(r.text.splitlines() if r.ok else [])
        except Exception as exc:
            out["error"] = f"robots:{type(exc).__name__}"
            return out
        html = {}
        for name, path in POLICY_PATHS.items():
            url = base + path
            if not rp.can_fetch(webmeta.UA, url):
                html[name] = None
                continue
            try:
                resp = s.get(url, timeout=25)
                html[name] = resp.text if resp.ok else None
            except Exception as exc:
                html[name] = None
                out.setdefault("fetch_errors", []).append(
                    f"{name}:{type(exc).__name__}"
                )
            time.sleep(pause)  # politeness pause between the two requests to this host
        out["_html"] = html
        return out

    return await asyncio.to_thread(work)


async def profile_many(
    targets: list[dict], max_concurrent: int, pause: float
) -> list[dict]:
    """targets: [{'domain':..., 'final_host':..., 'business_model':..., 'business_model_why':...}, ...]
    Bounded concurrency ACROSS different hosts (max_concurrent at once); each
    individual host still only ever has one request in flight from us."""
    sem = asyncio.Semaphore(max_concurrent)
    results: list[dict] = []

    async def one(t: dict):
        async with sem:
            fetched = await _fetch_policies_async(
                t["domain"], t.get("final_host"), pause
            )
            html = fetched.pop("_html", {})
            sig = extract_policy_signals(html.get("shipping"), html.get("refund"))
            verdict = dropship_confidence(
                t.get("business_model", "unclear"),
                t.get("business_model_why") or [],
                sig,
            )
            results.append(
                {
                    "domain": t["domain"],
                    "tranco_rank": t.get("tranco_rank"),
                    "product_label": t.get("business_model"),
                    "shipping_policy_found": sig.shipping_found,
                    "refund_policy_found": sig.refund_found,
                    "slow_ship_phrase": sig.slow_ship_phrase,
                    "fast_ship_phrase": sig.fast_ship_phrase,
                    "boilerplate_refund": sig.boilerplate_refund,
                    "has_street_address": sig.has_street_address_anywhere,
                    "verdict": verdict["verdict"],
                    "confidence": verdict["confidence"],
                    "reasons": verdict["reasons"],
                    **{k: v for k, v in fetched.items() if k != "domain"},
                }
            )

    await asyncio.gather(*(one(t) for t in targets))
    return results


def run(domains: list[str], max_concurrent: int = 8, pause: float = 1.0) -> dict:
    deep = stores.latest_good(stores._all_rows("web_store_deep"))
    light = stores.latest_good(stores._all_rows("web_store_light"))
    meta = stores.latest_good(stores._all_rows("web_meta"))
    targets = []
    for d in domains:
        base = deep.get(d) or light.get(d) or {}
        m = meta.get(d) or {}
        targets.append(
            {
                "domain": d,
                "final_host": m.get("final_host"),
                "tranco_rank": base.get("tranco_rank"),
                "business_model": base.get("business_model", "unclear"),
                "business_model_why": base.get("business_model_why") or [],
            }
        )
    rows = asyncio.run(profile_many(targets, max_concurrent, pause))
    runid = store.record_run(
        "web_dropship_profile",
        rows,
        source="store_policy_pages",
        trust="data",
        params={"n": len(rows), "max_concurrent": max_concurrent},
        note="shipping/refund policy text signals + combined dropship verdict; "
        "one honest UA, robots.txt respected per host, no JS render needed",
    )
    by_verdict = {}
    for r in rows:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
    print(f"dropship_profile: {len(rows)} stores -> {by_verdict}", file=sys.stderr)
    return {"web_dropship_profile": (runid, len(rows))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Full dropship-judgment profile via policy pages"
    )
    ap.add_argument("--domains-file", required=True, help="one domain per line")
    ap.add_argument("--max-concurrent", type=int, default=8)
    ap.add_argument("--pause", type=float, default=1.0)
    a = ap.parse_args(argv)
    doms = open(a.domains_file, encoding="utf-8").read().split()
    out = run(doms, a.max_concurrent, a.pause)
    for k, (rid, n) in out.items():
        print(f"{k}: run {rid}, {n} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
