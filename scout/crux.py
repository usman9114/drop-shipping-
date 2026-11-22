"""Chrome UX Report (CrUX): which sites real Chrome users in one country visit.

    python -m scout.crux pull --country pk            # latest month -> lake dataset crux_origins
    python -m scout.crux match --country pk            # coverage of our market stores
    python -m scout.crux discover --country pk --max-bucket 50000 [--limit N]
        # DNS-check (apex + www) unscanned origins for Shopify; resumable

Source: Google's public BigQuery dataset `chrome-ux-report.country_<cc>.<YYYYMM>`
(free tier, 1 TB of queries a month; we read two columns, a few MB). Terms:
CrUX is published by Google under CC BY 4.0
(https://developer.chrome.com/docs/crux/methodology). Data: origin and
`experimental.popularity.rank`, a rank *bucket* (1k, 5k, 10k, 50k, 100k, ...)
among origins visited from that country. It is a popularity [proxy], not sales.

Every query is dry-run first; the pull stops if a query would scan more than
MAX_GB (cost guard). Needs GOOGLE_APPLICATION_CREDENTIALS (service account with
BigQuery Job User) in .env.
"""

from __future__ import annotations

import argparse
import sys
from urllib.parse import urlparse

from scout import store

MAX_GB = 5.0


def _client():
    import json
    import os

    from dotenv import load_dotenv
    from google.cloud import bigquery

    load_dotenv(".env")
    path = os.path.expanduser(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
    project = json.load(open(path))["project_id"]
    return bigquery.Client(project=project), bigquery


def latest_table(client, country: str) -> str:
    tabs = sorted(
        t.table_id for t in client.list_tables(f"chrome-ux-report.country_{country}")
    )
    return tabs[-1]


def host_of(origin: str) -> str:
    """https://www.example.com.pk -> example.com.pk (our domain key)."""
    h = urlparse(origin).hostname or ""
    return h[4:] if h.startswith("www.") else h


def pull(country: str) -> dict:
    client, bq = _client()
    month = latest_table(client, country)
    sql = (
        "select origin, experimental.popularity.rank as rank "
        f"from `chrome-ux-report.country_{country}.{month}` group by 1, 2"
    )
    dry = client.query(
        sql, job_config=bq.QueryJobConfig(dry_run=True, use_query_cache=False)
    )
    gb = dry.total_bytes_processed / 1e9
    print(f"{month}: query scans {gb:.3f} GB", file=sys.stderr)
    if gb > MAX_GB:
        raise SystemExit(f"stop: {gb:.1f} GB is above MAX_GB {MAX_GB}")
    best: dict[str, int] = {}
    for r in client.query(sql).result():
        h = host_of(r.origin)
        if h and (h not in best or r.rank < best[h]):
            best[h] = r.rank
    rows = [
        {"domain": h, "country": country, "month": month, "rank_bucket": rk}
        for h, rk in best.items()
    ]
    run = store.record_run(
        "crux_origins",
        rows,
        source="chrome-ux-report (BigQuery public dataset)",
        trust="data",
        params={"country": country, "month": month, "gb_scanned": round(gb, 3)},
        note="CC BY 4.0; origin + popularity rank bucket only; www folded into the apex",
    )
    return {"crux_origins": (run, len(rows))}


def match(country: str) -> None:
    from collections import Counter

    from scout import stores

    crux = {}
    for r in stores._all_rows("crux_origins"):
        if r["country"] == country:
            crux[r["domain"]] = r["rank_bucket"]
    metas = stores.latest_good(stores._all_rows("web_meta"))
    ours = [
        d for d, m in metas.items() if m.get("shop_id") and stores.in_market(m, country)
    ]
    hit = {d: crux[d] for d in ours if d in crux}
    print(
        f"our {country} stores: {len(ours)}; in CrUX {country}: {len(hit)} ({len(hit) / max(len(ours), 1):.0%})"
    )
    print("buckets:", sorted(Counter(hit.values()).items()))
    shop = {d for d in metas}
    print(
        f"CrUX {country} origins: {len(crux)}; not in our Shopify scan at all: "
        f"{sum(1 for d in crux if d not in shop)}"
    )


# Stores found through CrUX are not in our Tranco scan: they get this marker rank
# (sorts after every Tranco store) and keep their CrUX bucket for ranking.
OUTSIDE_TRANCO = 1_000_001


def discover(
    country: str, max_bucket: int, limit: int | None, batch: int = 5000
) -> dict:
    """DNS only (Google Public DNS), no request to the sites themselves."""
    from concurrent.futures import ThreadPoolExecutor

    from scout import stores, webmeta

    crux = {}
    for r in stores._all_rows("crux_origins"):
        if r["country"] == country and r["rank_bucket"] <= max_bucket:
            crux[r["domain"]] = min(r["rank_bucket"], crux.get(r["domain"], 10**9))
    seen = {r["domain"] for r in stores._all_rows("web_scan")}
    seen |= {r["domain"] for r in stores._all_rows("crux_scan")}
    todo = sorted((b, d) for d, b in crux.items() if d not in seen)[:limit]
    print(f"{len(todo)} origins to check", file=sys.stderr, flush=True)

    def check(bd):
        b, d = bd
        row = {"domain": d, "country": country, "rank_bucket": b, "is_shopify": False}
        for host in (d, "www." + d):
            ips, err = webmeta.resolve_a(host)
            if webmeta.is_shopify(ips, []):
                row.update(is_shopify=True, host=host, a="|".join(ips))
                break
            row.setdefault("error", err or None)
        return row

    out = {}
    for i in range(0, len(todo), batch):
        with ThreadPoolExecutor(8) as ex:
            rows = list(ex.map(check, todo[i : i + batch]))
        run = store.record_run(
            "crux_scan",
            rows,
            source="chrome-ux-report+google_public_dns",
            trust="data",
            params={"country": country, "max_bucket": max_bucket, "n": len(rows)},
            note="DNS A records of apex and www vs Shopify IP range; no site requests",
        )
        hits = [
            {
                "domain": r["domain"],
                "tranco_rank": OUTSIDE_TRANCO,
                "a": r["a"],
                "crux_bucket": r["rank_bucket"],
                "found_by": "crux",
            }
            for r in rows
            if r["is_shopify"]
        ]
        if hits:
            store.record_run(
                "web_scan",
                hits,
                source="chrome-ux-report+google_public_dns",
                trust="data",
                params={"country": country, "found_by": "crux", "n": len(hits)},
                note=f"Shopify stores outside the Tranco scan; tranco_rank={OUTSIDE_TRANCO} is a marker",
            )
        print(
            f"crux_scan batch {i}: {len(rows)} checked, {len(hits)} Shopify",
            file=sys.stderr,
            flush=True,
        )
        out[f"crux_scan {i}"] = (run, len(rows))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chrome UX Report country popularity")
    ap.add_argument("cmd", choices=["pull", "match", "discover"])
    ap.add_argument("--country", default="pk")
    ap.add_argument("--max-bucket", type=int, default=50000)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args(argv)
    if a.cmd == "pull":
        for k, (run, n) in pull(a.country).items():
            print(f"{k}: run {run}, {n} rows", file=sys.stderr)
    elif a.cmd == "discover":
        for k, (run, n) in discover(a.country, a.max_bucket, a.limit).items():
            print(f"{k}: run {run}, {n} rows", file=sys.stderr)
    else:
        match(a.country)
    return 0


if __name__ == "__main__":
    sys.exit(main())
