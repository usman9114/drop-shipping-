"""Export the data file the Store Scout UI reads (decision 0018).

    python scripts/ui_export.py            # writes data/private/ui/store-scout.json

One JSON file, built from the warehouse and the lake. It is PRIVATE (it names
stores): it lives under data/private/ and is published only beside the owner's
private artifact, never committed. The shape of this file is the UI's data
contract (docs/design/ui-v0-store-card-and-leads.md) in code.

Which stores: the candidate pool (300), every store the classifier calls
dropship, reseller, general or pod, and every store with a named supply source.
Brands outside the pool are left out: the question is how copyable stores work.

Labels (CLAUDE.md principle 2) travel with the data in `labels`, and the score
weights in `score_weights`, so the page reads them and never copies them.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scout import fingerprints, store, store_intel, stores  # noqa: E402

DB = Path("data/private/warehouse.duckdb")
OUT = Path("data/private/ui/store-scout.json")
COPYABLE = {"dropship", "reseller", "general", "pod"}

# Same weights as warehouse/models/marts/mart_store_profile.sql (best_score).
SCORE_WEIGHTS = {
    "pct_traffic": [0.45, "traffic level (Tranco rank percentile)"],
    "pct_growth": [0.20, "rank growth against the earliest list"],
    "pct_rhythm": [0.20, "products added in the last 90 days"],
    "pct_stack": [0.15, "breadth of ad, email and conversion tools seen"],
}
GRADE_SIGNALS = {
    "s_traffic": "recent rank inside the top 150,000",
    "s_rising": "recent rank at least 35% better than 9+ months ago, not fading",
    "s_steady": "on at least 20 of the rank lists",
    "s_active": "20+ products added in the last 90 days",
    "s_marketing": "2+ ad pixels, or ads plus email/SMS (deep-profiled stores only)",
}
LABELS = {
    "rank": "PROXY",
    "spark": "PROXY",
    "trend": "PROXY",
    "grade": "PROXY",
    "score": "PROXY",
    "model": "PROXY",
    "supply": "PROXY",
    "existed_by": "PROXY",
    "price": "DATA",
    "discount": "DATA",
    "added": "DATA",
    "products": "DATA",
    "stack": "DATA",
    "category": "DATA",
    "reviews": "DATA",
    "theme": "DATA",
    "revenue": "UNKNOWN",
}
# doc 35 (hand-checked sample of 67 stores, rule version before 2026-11-05.3)
VALIDATION = {
    "named_source_right": "28 of 31 (90%)",
    "dropship_or_not": "89%",
    "source": "docs/research/35-fingerprint-validation.md",
    "note": "accuracy after the 2026-11-05.3 rule changes is not measured yet",
}


def _rows(con, sql: str) -> list[dict]:
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _c(v):
    """JSON-safe, compact."""
    if isinstance(v, float):
        return round(v, 3)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


def _split(v) -> list[str]:
    if not v:
        return []
    if isinstance(v, list):
        return v
    return [x for x in str(v).replace("|", ",").split(",") if x.strip()]


def _run_dates() -> dict[str, str]:
    return {r["run_id"]: (r.get("fetched_at") or "")[:10] for r in store._runs()}


def latest_fingerprints() -> dict[str, dict]:
    """Latest good fingerprint row per store (later runs win)."""
    out = {}
    for r in stores._all_rows("web_fingerprints"):
        if not r.get("error"):
            out[r["domain"]] = r
    return out


def trend_sentence(t: dict) -> str:
    if not t:
        return "No rank history: the store is not on the earlier lists."
    g = t.get("growth_old_to_recent")
    n, of = t.get("dates_present"), t.get("n_dates")
    if t.get("breakout"):
        head = "Breakout: recent rank far better than a year ago"
    elif t.get("emerged"):
        head = "Emerged: entered the top 1M during the period"
    elif t.get("fading"):
        head = "Fading: recent rank worse than before"
    elif g is not None and g >= 0.35:
        head = "Rising"
    elif g is not None and g <= -0.35:
        head = "Falling"
    else:
        head = "Steady"
    return f"{head}; on {n} of {of} rank lists."


def light_story(u: dict) -> str:
    cat = str(u.get("top_category") or "unclassified").replace("_", " ")
    return (
        f"Sells mainly {cat}; {u.get('published_products')} published products, entry "
        f"prices {u.get('price_p25')} to {u.get('price_p75')} (median "
        f"{u.get('price_median')}). Added {u.get('added_90d')} products in 90 days. "
        f"Model: {u.get('business_model')}. Light profile only (one feed page): ad "
        f"pixels, apps and reviews were not read for this store."
    )


def build(con) -> dict:
    run_date = _run_dates()
    fps = latest_fingerprints()
    named = {
        d
        for d, r in fps.items()
        if (r.get("estimate") or {}).get("source_guess") not in (None, "unknown")
    }
    universe = {
        r["domain"]: r for r in _rows(con, "select * from mart.mart_store_universe")
    }
    pool = {
        r["domain"]: r for r in _rows(con, "select * from mart.mart_candidate_pool")
    }
    profile = {
        r["domain"]: r for r in _rows(con, "select * from mart.mart_store_profile")
    }
    trend = {
        r["domain"]: r for r in _rows(con, "select * from mart.mart_store_rank_trend")
    }
    keep = set(pool) | {
        d for d, u in universe.items() if u["business_model"] in COPYABLE
    }
    keep |= named & set(universe)
    dates = [
        r["list_date"].isoformat()
        for r in _rows(
            con, "select distinct list_date from stg.stg_web_ranks order by 1"
        )
    ]
    didx = {d: i for i, d in enumerate(dates)}
    spark: dict[str, list] = {}
    for dom, ld, rk in con.execute(
        "select domain, list_date, tranco_rank from stg.stg_web_ranks"
    ).fetchall():
        if dom in keep:
            spark.setdefault(dom, [None] * len(dates))[didx[ld.isoformat()]] = rk
    cache = store_intel.load_cache()
    out_stores = []
    for d in sorted(
        keep, key=lambda x: (universe.get(x) or pool.get(x))["tranco_rank"]
    ):
        u = universe.get(d) or pool[d]
        p, c, t, f = profile.get(d), pool.get(d), trend.get(d), fps.get(d)
        est = (f or {}).get("estimate") or {}
        page = (f or {}).get("page") or {}
        if p:
            pk = store_intel.pack(p)
            hit = cache.get(store_intel.pack_hash(pk))
            story = hit["narrative"] if hit else store_intel.template(pk)
            gaps = pk["gaps"]
        else:
            story, gaps = light_story(u), list(store_intel.STANDING_GAPS)
        s = {
            "d": d,
            "cat": u.get("top_category"),
            "cat_share": _c(u.get("top_category_share")),
            "model": u.get("business_model"),
            "model_why": _split((p or {}).get("business_model_why")),
            "depth": u.get("depth"),
            "slice": (c or {}).get("slice"),
            "grade": (c or {}).get("own_grade"),
            "signals": {k: bool(c[k]) for k in GRADE_SIGNALS} if c else None,
            "rank": u.get("tranco_rank"),
            "spark": spark.get(d),
            "trend": trend_sentence(t),
            "growth": _c((t or {}).get("growth_old_to_recent")),
            "price": [
                _c(u.get("price_p25")),
                _c(u.get("price_median")),
                _c(u.get("price_p75")),
            ],
            "disc": _c(u.get("discount_share")),
            "added": [
                _c((p or {}).get("added_30d")),
                _c(u.get("added_90d")),
                _c(u.get("added_365d")),
            ],
            "products": u.get("published_products"),
            "existed_by": _c(
                (p or {}).get("existed_by") or (c or {}).get("existed_by")
            ),
            "country": (p or {}).get("country"),
            "ads": _split((p or c or {}).get("paid_ads")),
            "retention": _split((p or c or {}).get("retention")),
            "partners": _split((p or c or {}).get("partners")),
            "conversion": _split((p or {}).get("conversion")),
            "reviews": [
                (p or {}).get("sample_review_count"),
                _c((p or {}).get("sample_rating")),
            ],
            "supply": {
                "guess": est.get("source_guess"),
                "warehouse": est.get("warehouse_guess"),
                "conf": _c(est.get("confidence")),
                "evidence": est.get("evidence") or [],
                "mixed": est.get("mixed_sources") or [],
                "seen": run_date.get(f.get("run_id"), ""),
                "rule": f.get("rule_version"),
            }
            if f
            else None,
            "theme": page.get("theme_name"),
            "apps": (page.get("app_embed_handles") or [])[:12],
            "effort": fingerprints.effort_apps(page) if f else None,
            "score": {
                "best": _c(p.get("best_score")),
                **{k: _c(p.get(k)) for k in SCORE_WEIGHTS},
            }
            if p
            else None,
            "story": story,
            "gaps": gaps,
            "seen": run_date.get((p or {}).get("run_id"), ""),
        }
        out_stores.append(s)

    # niche board: the copyable-niche mart plus the supply mix we observed there
    mix: dict[str, Counter] = {}
    for d, f in fps.items():
        cat = (universe.get(d) or {}).get("top_category")
        g = (f.get("estimate") or {}).get("source_guess") or "unknown"
        if cat:
            mix.setdefault(cat, Counter())[g] += 1
    niches = []
    for n in _rows(
        con,
        "select * from mart.mart_niche_copyable order by copyable_traffic_weight desc",
    ):
        row = {k: _c(v) for k, v in n.items()}
        row["supply_mix"] = dict(mix.get(n["category"], {}))
        niches.append(row)

    # supply view
    by_model: dict[str, Counter] = {}
    apps, sigs, wh, effort = Counter(), Counter(), Counter(), Counter()
    for d, f in fps.items():
        est = f.get("estimate") or {}
        m = (
            (universe.get(d) or {}).get("business_model")
            or f.get("business_model")
            or "unprofiled"
        )
        by_model.setdefault(m, Counter())[est.get("source_guess") or "unknown"] += 1
        if est.get("source_guess") not in (None, "unknown"):
            w = est.get("warehouse_guess") or "unknown"
            wh["several countries" if w.startswith("mixed") else w] += 1
        apps.update((f.get("page") or {}).get("app_embed_handles") or [])
        effort.update(fingerprints.effort_apps(f.get("page") or {}))
        sigs.update((f.get("page") or {}).get("signature_ids") or [])
        sigs.update((f.get("feed") or {}).get("signature_ids") or [])
    supply = {
        "fingerprinted": len(fps),
        "screened": len(universe),
        "rule_version": fingerprints.RULE_VERSION,
        "by_source": dict(Counter(g for c in by_model.values() for g in c.elements())),
        "by_model": {m: dict(c) for m, c in by_model.items()},
        "warehouse_of_named": dict(wh),
        "top_apps": apps.most_common(25),
        "effort_apps": effort.most_common(),
        "top_signatures": sigs.most_common(25),
        "validation": VALIDATION,
    }

    # autopilot health: heartbeat plus the run log, counts only
    hb_path = store.LAKE / "_autopilot" / "heartbeat.json"
    hb = json.loads(hb_path.read_text()) if hb_path.exists() else {}
    per: dict[str, dict] = {}
    for r in store._runs():
        x = per.setdefault(r["dataset"], {"runs": 0, "rows": 0, "last": ""})
        x["runs"] += 1
        x["rows"] += int(r.get("rows") or 0)
        x["last"] = max(x["last"], (r.get("fetched_at") or "")[:16])
    health_path = store.LAKE / "_autopilot" / "health.json"
    autopilot = {
        "heartbeat": hb,
        "health": json.loads(health_path.read_text()) if health_path.exists() else None,
        "datasets": per,
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rank_dates": dates,
        "labels": LABELS,
        "score_weights": SCORE_WEIGHTS,
        "grade_signals": GRADE_SIGNALS,
        "standing_gaps": store_intel.STANDING_GAPS,
        "counts": {
            "shopify_hits": len(
                {r["domain"] for r in _rows(con, "select domain from stg.stg_web_scan")}
            ),
            "screened": len(universe),
            "deep": len(profile),
            "pool": len(pool),
            "in_ui": len(out_stores),
            "by_model": dict(Counter(u["business_model"] for u in universe.values())),
        },
        "stores": out_stores,
        "niches": niches,
        "supply": supply,
        "autopilot": autopilot,
    }


def main() -> int:
    import duckdb

    con = duckdb.connect(str(DB), read_only=True)
    data = build(con)
    con.close()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(data, separators=(",", ":"), default=str), encoding="utf-8"
    )
    c = data["counts"]
    print(
        f"wrote {OUT}: {c['in_ui']} stores, {len(data['niches'])} niches, "
        f"{data['supply']['fingerprinted']} fingerprinted, {OUT.stat().st_size // 1024} KB",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
