"""Export the data file for the Pakistan tab of Store Scout (decisions 0019 to 0021).

    python scripts/ui_export_pk.py       # writes data/private/ui/pakistan.json

Built from the lake only (no warehouse): ranking from scout.market_rank, plus the
homepage signals (web_store_home) and the best-seller collection (web_store_best).
PRIVATE (it names stores): publish only beside the owner's private artifact,
never commit. Labels (CLAUDE.md principle 2) travel with the data.
"""

from __future__ import annotations

import json
import statistics as st
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scout import market_rank, store, stores  # noqa: E402

OUT = Path("data/private/ui/pakistan.json")
AD_TAGS = {
    "meta_pixel", "tiktok_pixel", "google_ads", "pinterest_tag", "snap_pixel",
    "microsoft_ads", "reddit_pixel",
}  # fmt: skip
LABELS = {
    "popularity": "PROXY",
    "rank": "PROXY",
    "growth": "PROXY",
    "score": "PROXY",
    "model": "PROXY",
    "best": "PROXY",
    "social": "PROXY",
    "price": "DATA",
    "discount": "DATA",
    "added": "DATA",
    "products": "DATA",
    "category": "DATA",
    "revenue": "UNKNOWN",
}
SCORE_PARTS = {
    "pct_pk": [
        "pk_popularity",
        "popularity among Chrome users in Pakistan (CrUX bucket)",
    ],
    "pct_global": ["global_rank", "global traffic rank (Tranco), 0 outside the top 1M"],
    "pct_growth": ["growth", "rank growth over the last year (Tranco)"],
    "pct_rhythm": ["rhythm", "products added in the last 90 days"],
}


def _med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def main() -> int:
    rows = market_rank.score(market_rank.market_rows("pk"))
    dates = sorted({r["list_date"] for r in stores._all_rows("web_ranks")})
    hist: dict[str, dict[str, int]] = {}
    for r in stores._all_rows("web_ranks"):
        hist.setdefault(r["domain"], {})[r["list_date"]] = r["tranco_rank"]
    home = stores.latest_good(stores._all_rows("web_store_home"))
    best = stores.latest_good(stores._all_rows("web_store_best"))
    found_by_crux = {
        r["domain"] for r in stores._all_rows("web_scan") if r.get("found_by") == "crux"
    }
    out = []
    for i, r in enumerate(rows, 1):
        d = r["domain"]
        h, b = home.get(d, {}), best.get(d, {})
        tags = set(h.get("traffic_tags") or [])
        ratio = None
        if b.get("best_price_median") and r.get("price_median"):
            ratio = round(b["best_price_median"] / r["price_median"], 2)
        s = {
            "d": d,
            "name": r.get("shop_name"),
            "n": i if r["best_score"] is not None else None,  # rank among scored
            "via": "crux" if d in found_by_crux else "tranco",
            "rank": r["tranco_rank"],
            "crux": r["crux_bucket"],
            "growth": r["rank_growth_log"],
            "spark": [hist.get(d, {}).get(x) for x in dates] if d in hist else None,
            "scored": r["best_score"] is not None,
            "score": (
                {
                    "best": r["best_score"],
                    **{k: r[k] for k in SCORE_PARTS},
                }
                if r["best_score"] is not None
                else None
            ),
            "country": r["country"],
            "products": r["published_products"],
        }
        if r["profiled"]:
            s.update(
                cat=r["top_category"],
                cat_share=r["top_category_share"],
                model=r["business_model"],
                model_why=r["business_model_why"] or [],
                price=[r["price_p25"], r["price_median"], r["price_p75"]],
                disc=r["discount_share"],
                added=[r["added_30d"], r["added_90d"], r["added_365d"]],
                vendors=r["vendors"],
                seen=(r["newest_created"] or "")[:10],
            )
        if h and not h.get("error"):
            s.update(
                social=h.get("social_networks") or [],
                ads=sorted(tags & AD_TAGS),
                apps=sorted(tags - AD_TAGS),
            )
        if b.get("best_n"):
            s["best"] = {
                "collection": b["best_collection"],
                "n": b["best_n"],
                "price": b["best_price_median"],
                "ratio": ratio,
                "disc": b["best_discount_share"],
                "new90": b["best_added_90d_share"],
            }
        out.append(s)

    prof = [s for s in out if s["scored"]]
    cats: dict[str, list[dict]] = {}
    for s in prof:
        cats.setdefault(s.get("cat") or "other", []).append(s)
    categories = sorted(
        (
            {
                "category": c,
                "stores": len(v),
                "top_bucket": sum(1 for x in v if x["crux"] and x["crux"] <= 5000),
                "median_price": _med(x["price"][1] for x in v),
                "median_added_90d": _med(x["added"][1] for x in v),
                "median_best_ratio": _med(
                    x["best"]["ratio"] for x in v if x.get("best")
                ),
                "brands": sum(1 for x in v if x.get("model") == "brand"),
                "resold": sum(
                    1 for x in v if x.get("model") in ("reseller", "retailer")
                ),
                "other_models": sum(
                    1
                    for x in v
                    if x.get("model") not in ("brand", "reseller", "retailer")
                ),
            }
            for c, v in cats.items()
        ),
        key=lambda x: -x["stores"],
    )
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "market": "pk",
        "currency": "PKR",
        "rank_dates": dates,
        "labels": LABELS,
        "score_weights": {
            k: [market_rank.WEIGHTS[v[0]], v[1]] for k, v in SCORE_PARTS.items()
        },
        "counts": {
            "stores": len(out),
            "scored": len(prof),
            "with_crux": sum(1 for s in out if s["crux"]),
            "with_history": sum(1 for s in out if s["spark"]),
            "found_by_crux": sum(1 for s in out if s["via"] == "crux"),
            "with_homepage": sum(1 for s in out if "social" in s),
            "with_best": sum(1 for s in out if "best" in s),
        },
        "models": Counter(s.get("model") for s in prof),
        "categories": categories,
        "validation": {
            "model": "40 hand-checked stores: 36 right (90%), in-sample; held-out check due",
            "model_second_opinion": "free models agree with hand labels on 34 of 40 (85%)",
            "best_seller": "held-out: 19 of 20 right (95%); 5 misses in 50 are all 'none'",
            "docs": "docs/decisions/0019, 0020, 0021",
        },
        "credits": "Popularity: Chrome UX Report, Google, CC BY 4.0. Global rank: Tranco.",
        "stores": out,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(
        f"{OUT}: {OUT.stat().st_size / 1e6:.2f} MB, {len(out)} stores, "
        f"{len(prof)} scored, {len(categories)} categories",
        file=sys.stderr,
    )
    _ = store  # lake helpers are reached through scout.stores
    return 0


if __name__ == "__main__":
    sys.exit(main())
