"""Build README.md (the project's live dashboard) from aggregate stats.

    python scripts/readme_build.py                         # lake -> stats.json -> README + SVGs
    python scripts/readme_build.py --from-stats docs/readme/stats.json   # render only (CI)

Stage 1 `collect()` reads the private lake and keeps aggregates only. Stage 2
`render(stats)` is pure: the same stats give byte-identical files. The README is
public, so `assert_public_safe` refuses any store domain, shop name or secret.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "readme"
MARKETS = ("us", "pk")
MARKET_NAME = {"us": "US", "pk": "PK"}
CURRENCY = {"us": "USD", "pk": "PKR"}
PRICE_BANDS = {
    "us": [(0, 10), (10, 25), (25, 50), (50, 100), (100, 10**9)],
    "pk": [(0, 1500), (1500, 3000), (3000, 6000), (6000, 12000), (12000, 10**9)],
}
CRUX_ORDER = [1000, 5000, 10000, 50000, 100000, 500000]
MODELS = ["brand", "retailer", "general", "reseller", "dropship", "pod", "other"]
REPO = "https://github.com/usman9114/drop-shipping-"

ALLOWED_HOSTS = (
    "github.com",
    "shields.io",
    "tranco-list.eu",
    "developer.chrome.com",
    "cloud.google.com",
    "cjdropshipping.com",
    "ebay.com",
    "creativecommons.org",
    "w3.org",  # SVG xmlns, not a link
)
FILE_EXT = {
    "md",
    "py",
    "json",
    "svg",
    "yml",
    "yaml",
    "csv",
    "txt",
    "html",
    "png",
    "toml",
}
SECRET = re.compile(r"sk-[A-Za-z0-9]|eyJ|AKIA|-----BEGIN")
DOMAINISH = re.compile(
    r"(?<![A-Za-z0-9@_-])[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?![A-Za-z0-9_-])"
)


def _norm(text: str) -> str:
    """Fold look-alike forms so a leak cannot hide: NFKC, tags removed (so
    "acme<br/>.com" joins), zero-width and no-break spaces, ideographic dots,
    hyphens and runs of whitespace between words become one space; lower case."""
    t = unicodedata.normalize("NFKC", text)
    t = re.sub(r"<[^>]*>", "", t)
    t = re.sub("[\u200b-\u200d\ufeff]", "", t)
    t = t.replace("\u00a0", " ").replace("\u3002", ".")
    t = re.sub(r"(?<=\w)-+(?=\w)", " ", t)
    return re.sub(r"\s+", " ", t).lower()


def assert_public_safe(
    text: str, known_domains=(), known_names=(), allow=ALLOWED_HOSTS
) -> None:
    """Raise ValueError when text could leak a store, a shop name or a secret."""
    low = _norm(text)
    bad = [d for d in known_domains if d and _norm(d) in low]
    bad += [
        n
        for n in known_names
        if n and len(n) >= 5 and re.search(rf"(?<!\w){re.escape(_norm(n))}(?!\w)", low)
    ]
    if bad:
        raise ValueError(f"store identity in public output: {len(bad)} match(es)")
    if SECRET.search(text) or SECRET.search(low):
        raise ValueError("secret-looking string in public output")
    for m in [*DOMAINISH.finditer(text), *DOMAINISH.finditer(low)]:
        tok = m.group(0).lower()
        if tok.rsplit(".", 1)[-1] in FILE_EXT or tok.startswith("scout."):
            continue
        if any(
            tok == a
            or tok.endswith("." + a)
            or (" " in _norm(a) and _norm(a).endswith(tok))
            for a in allow
        ):
            continue
        raise ValueError(f"unexpected domain-like token: {tok!r}")


# ---------------------------------------------------------------- stage 1


def _median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def _market_stats(market: str, rows: list[dict], best_domains: set[str]) -> dict:
    prof = [r for r in rows if r.get("profiled")]
    cats: dict[str, int] = {}
    models = dict.fromkeys(MODELS, 0)
    crux = dict.fromkeys(CRUX_ORDER, 0)
    for r in prof:
        c = r.get("top_category")
        if c:
            cats[c] = cats.get(c, 0) + 1
        m = r.get("business_model") or "other"
        models[m if m in models else "other"] += 1  # "unclear" counts as other
    for r in rows:
        if r.get("crux_bucket") in crux:
            crux[r["crux_bucket"]] += 1
    prices = [r["price_median"] for r in prof if r.get("price_median")]
    bands = []
    for lo, hi in PRICE_BANDS[market]:
        bands.append(sum(1 for p in prices if lo <= p < hi))
    top = sorted(cats.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    med = _median(prices)
    return {
        "stores": len(rows),
        "profiled": len(prof),
        "with_popularity": sum(1 for r in rows if r.get("crux_bucket")),
        "with_rank_history": sum(1 for r in rows if r.get("rank_earliest") is not None),
        "categories": len(cats),
        "top_categories": [[k, v] for k, v in top],
        "median_price": None if med is None else round(med, 2),
        "price_bands": bands,
        "models": models,
        "crux_buckets": {str(k): v for k, v in crux.items()},
        "best_seller_lists": len(best_domains & {r["domain"] for r in rows}),
    }


def collect() -> dict:
    """Aggregate the private lake. Needs data/private/lake; never stores identities."""
    sys.path.insert(0, str(ROOT))
    from scout import market_rank, stores

    best = {
        d
        for d, r in stores.latest_good(stores._all_rows("web_store_best")).items()
        if r.get("best_collection")
    }
    out: dict = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "markets": {},
    }
    for m in MARKETS:
        rows = market_rank.score(market_rank.market_rows(m))
        out["markets"][m] = _market_stats(m, rows, best)
    out["weights"] = dict(market_rank.WEIGHTS)
    out["bucket_score"] = {str(k): v for k, v in market_rank.BUCKET_SCORE.items()}
    return out


def lake_identities() -> tuple[list[str], list[str]]:
    sys.path.insert(0, str(ROOT))
    from scout import stores

    metas = stores.latest_good(stores._all_rows("web_meta"))
    names = {str(m["shop_name"]) for m in metas.values() if m.get("shop_name")}
    return sorted(metas), sorted(names)


# ---------------------------------------------------------------- stage 2: SVG

STYLE = (
    "<style>.t{fill:#1f2328;font:12px -apple-system,Segoe UI,Helvetica,Arial,sans-serif}"
    ".h{font-weight:600;font-size:14px}.m{fill:#59636e}.g{stroke:#8c959f;stroke-opacity:.35}"
    ".s0{fill:#0969da}.s1{fill:#bf3989}"
    "@media (prefers-color-scheme:dark){.t{fill:#e6edf3}.m{fill:#9198a1}"
    ".s0{fill:#4493f8}.s1{fill:#db61a2}}</style>"
)


def _esc(x) -> str:
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bars(
    title: str,
    note: str,
    labels: list[str],
    series: list[tuple[str, list[float]]],
    fmt=lambda v: f"{v:,.0f}",
) -> str:
    """Horizontal bar chart, one or two series, theme-aware (CSS media query)."""
    w, left, right, row = 640, 150, 70, 22 * len(series) + 10
    h = 58 + row * len(labels) + (18 if len(series) > 1 else 0)
    top = max([v for _, vs in series for v in vs] + [1])
    span = w - left - right
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
        f'height="{h}" role="img" aria-label="{_esc(title)}">',
        STYLE,
        f'<text class="t h" x="12" y="22">{_esc(title)}</text>',
        f'<text class="t m" x="12" y="40">{_esc(note)}</text>',
    ]
    if len(series) > 1:
        for i, (name, _) in enumerate(series):
            x = 12 + i * 90
            o.append(
                f'<rect class="s{i}" x="{x}" y="46" width="10" height="10" rx="2"/>'
                f'<text class="t" x="{x + 14}" y="55">{_esc(name)}</text>'
            )
    y0 = 58 + (18 if len(series) > 1 else 0)
    o.append(f'<line class="g" x1="{left}" y1="{y0 - 4}" x2="{left}" y2="{h - 4}"/>')
    for j, lab in enumerate(labels):
        y = y0 + j * row
        o.append(
            f'<text class="t" x="{left - 8}" y="{y + 14}" text-anchor="end">{_esc(lab)}</text>'
        )
        for i, (_, vs) in enumerate(series):
            bw = round(vs[j] / top * span, 1)
            by = y + i * 20
            o.append(
                f'<rect class="s{i}" x="{left}" y="{by}" width="{bw}" height="16" rx="3"/>'
                f'<text class="t m" x="{round(left + bw + 6, 1)}" y="{by + 12}">{fmt(vs[j])}</text>'
            )
    o.append("</svg>")
    return "\n".join(o) + "\n"


def band_labels(m: str) -> list[str]:
    cur = CURRENCY[m]
    edges = [lo for lo, _ in PRICE_BANDS[m]][1:]
    names = [f"under {edges[0]:,}"]
    names += [f"{a:,} to {b:,}" for a, b in zip(edges, edges[1:])]
    names.append(f"{edges[-1]:,}+")
    return [f"{n} {cur}" for n in names]


def pct(part: float, whole: float) -> float:
    return round(100 * part / whole, 1) if whole else 0.0


def charts(st: dict) -> dict[str, str]:
    mk = st["markets"]
    out = {}
    for m in MARKETS:
        top = mk[m]["top_categories"] or [["none", 0]]
        out[f"categories_{m}.svg"] = bars(
            f"Top categories, {MARKET_NAME[m]}",
            "profiled stores by main category, rule-based [proxy]",
            [k.replace("_", " ") for k, _ in top],
            [("stores", [v for _, v in top])],
        )
        out[f"prices_{m}.svg"] = bars(
            f"Product price bands, {MARKET_NAME[m]} ({CURRENCY[m]})",
            "stores by median product price [data]",
            band_labels(m),
            [("stores", mk[m]["price_bands"])],
        )
    cb = mk["pk"]["crux_buckets"]
    names = {
        "1000": "top 1k",
        "5000": "top 5k",
        "10000": "top 10k",
        "50000": "top 50k",
        "100000": "top 100k",
        "500000": "top 500k",
    }
    out["popularity_pk.svg"] = bars(
        "Popularity in Pakistan (Chrome UX Report)",
        "stores per bucket, best bucket per store [proxy]",
        [names[str(b)] for b in CRUX_ORDER],
        [("stores", [cb[str(b)] for b in CRUX_ORDER])],
    )
    out["models.svg"] = bars(
        "Business-model mix",
        "share of profiled stores, rule-based [proxy]",
        [x for x in MODELS],
        [
            (
                MARKET_NAME[m],
                [pct(mk[m]["models"].get(x, 0), mk[m]["profiled"]) for x in MODELS],
            )
            for m in MARKETS
        ],
        fmt=lambda v: f"{v:.1f}%",
    )
    return out


# ---------------------------------------------------------------- stage 2: README


def _badge(label: str, msg: str, color: str) -> str:
    q = lambda x: x.replace("-", "--").replace(" ", "_")  # noqa: E731
    return f"![{label}](https://img.shields.io/badge/{q(label)}-{q(msg)}-{color})"


def _fmt_price(v, cur) -> str:
    return "n/a" if v is None else f"{v:,.0f} {cur}"


def _glance(st: dict) -> str:
    mk = st["markets"]
    rows = [
        ("Stores found", lambda m: f"{m['stores']:,}"),
        ("Scored (profiled)", lambda m: f"{m['profiled']:,}"),
        ("With popularity data (Chrome UX)", lambda m: f"{m['with_popularity']:,}"),
        ("Categories seen", lambda m: f"{m['categories']}"),
        ("Median product price", None),
        (
            "Own brand [proxy]",
            lambda m: f"{pct(m['models'].get('brand', 0), m['profiled'])}%",
        ),
        (
            "Reseller or retailer [proxy]",
            lambda m: f"{pct(m['models'].get('reseller', 0) + m['models'].get('retailer', 0), m['profiled'])}%",
        ),
        (
            "Dropship [proxy]",
            lambda m: f"{pct(m['models'].get('dropship', 0), m['profiled'])}%",
        ),
        ("Best-seller lists found", lambda m: f"{m['best_seller_lists']:,}"),
    ]
    out = ["| Per market | US | PK |", "|---|--:|--:|"]
    for name, fn in rows:
        cells = [
            (
                _fmt_price(mk[m]["median_price"], CURRENCY[m])
                if fn is None
                else fn(mk[m])
            )
            for m in MARKETS
        ]
        out.append(f"| {name} | {cells[0]} | {cells[1]} |")
    return "\n".join(out)


def render(st: dict) -> dict[str, str]:
    """Pure: stats in, {relative path: text} out. Same stats, same bytes."""
    d, mk = st["generated_at"], st["markets"]
    # US = USD storefronts, PK = PKR storefronts (stores.in_market by currency):
    # one currency per store, so the sets are disjoint and the sum is the union.
    total = sum(mk[m]["stores"] for m in MARKETS)
    w, bs = st["weights"], st["bucket_score"]
    files = {f"docs/readme/{k}": v for k, v in charts(st).items()}

    def img(n: str) -> str:
        return (
            f'<img src="docs/readme/{n}" width="49%" alt="{n[:-4].replace("_", " ")}">'
        )

    desc = {
        "pk_popularity": "popularity inside Pakistan, Chrome UX bucket [proxy]",
        "growth": "percentile of rank growth over a year [proxy]",
        "global_rank": "inverse percentile of the global Tranco rank [proxy]",
        "rhythm": "percentile of products added in the last 90 days [data]",
    }
    wrows = "\n".join(
        f"| {k.replace('_', ' ')} | {w[k]:.2f} | {desc.get(k, '')} |"
        for k in sorted(w, key=lambda k: (-w[k], k))
    )
    brow = " · ".join(
        f"{int(k) // 1000}k = {v:.1f}"
        for k, v in sorted(bs.items(), key=lambda kv: int(kv[0]))
    )
    readme = f"""<div align="center">

# Shopify store radar for zero-inventory commerce

**We watch the winning stores, learn what sells and at what price, then list better than the incumbents. The supplier ships, we hold no stock.**

[![CI]({REPO}/actions/workflows/ci.yml/badge.svg)]({REPO}/actions/workflows/ci.yml)
[![Autopilot]({REPO}/actions/workflows/autopilot.yml/badge.svg)]({REPO}/actions/workflows/autopilot.yml)
{_badge("stores tracked", f"{total:,}", "0969da")}
{_badge("markets", "US · PK", "2da44e")}
{_badge("last refresh", d, "8250df")}
{_badge("inventory", "zero", "bf3989")}

[At a glance](#at-a-glance) · [Charts](#charts) · [Pipeline](#how-it-works) · [Roadmap](#roadmap) · [Method](#method-and-caveats) · [Project map](#project-map)

</div>

> [!IMPORTANT]
> Every number here is an **aggregate** and is tagged `[data]` (observed), `[proxy]` (indirect signal) or `[unknown]`. No store, shop or product is named in this public page.

## At a glance

{_glance(st)}

> [!NOTE]
> Counts are `[data]`. Business model is a rule-based `[proxy]` (hand-checked, see below). Prices are the median of each store's median product price, in local currency.

## Charts

<p align="center">
{img("categories_us.svg")}
{img("categories_pk.svg")}
</p>
<p align="center">
{img("prices_us.svg")}
{img("prices_pk.svg")}
</p>
<p align="center">
{img("popularity_pk.svg")}
{img("models.svg")}
</p>

## How it works

```mermaid
flowchart LR
  A[Discover<br/>Tranco, Chrome UX, DNS] --> B[Profile<br/>meta, feed, best sellers]
  B --> C[Score<br/>per market, explained]
  C --> D[Niche shortlist<br/>plus margin check]
  D --> E[Operate<br/>eBay, supplier ships]
  E -. own sales data .-> C
```

## Roadmap

```mermaid
gantt
  title Milestones M0 to M6 (targets, each with a measured gate)
  dateFormat YYYY-MM-DD
  axisFormat %b %Y
  section Spine
  M0 Autopilot US + PK, live README :active, m0, 2026-11-01, 2026-11-30
  section Niches
  M1 Shortlist of 10 niches + margin model :m1, 2026-12-01, 31d
  section Operate
  M2 First live eBay test, 20 listings :m2, 2027-01-01, 31d
  M3 First profit, 1000 USD :m3, 2027-02-01, 28d
  M4 Three channels :m4, 2027-04-01, 91d
  section Radar
  M5 Radar beta for sellers :m5, 2027-07-01, 92d
  M6 The million, 2028 :milestone, m6, 2028-01-01, 1d
```

- [x] US store radar on autopilot
- [x] Pakistan radar: Chrome UX popularity and best-seller collections
- [ ] Live README refreshed by CI (first run pending)
- [ ] M0 gate: daily runs green 7 days in a row
- [ ] M1: shortlist of 10 niches with a margin model
- [ ] M2: first live eBay test (20 listings, 2 niches)
- [ ] M3 to M6: profit, three channels, radar beta, the million

## Method and caveats

<details><summary><b>How the ranking works</b></summary>

Each profiled Pakistani store gets four parts from 0 to 1, combined with these weights (one place in code: `market_rank.WEIGHTS`).

| Part | Weight | What it measures |
|---|--:|---|
{wrows}

Chrome UX bucket scores: {brow}.
Why: the US score weights traffic 0.45, growth 0.20 and rhythm 0.20; Pakistan splits traffic between local popularity and the global list because small local stores are invisible to the global list.

**What would change the order:** fast rank growth lifts a store past a busier, flat one; a store that stops adding products drops; stores outside the global top 1M can rank high on popularity but never earn growth points.

> [!WARNING]
> Popularity and rank measure visits, not sales. Revenue, orders, ad spend and margin are `[unknown]` for every store.

</details>

<details><summary><b>How good are the rules</b></summary>

| Check | Result | Note |
|---|--:|---|
| Business model, Pakistan, 40 hand-checked stores | 36 of 40 (90%) | in-sample; 31 of 32 when high confidence; [decision 0019](docs/decisions/0019-pakistan-market-store-ranking.md) |
| Same rules before tuning | 25 of 40 (62%) | US rules as they were; [decision 0019](docs/decisions/0019-pakistan-market-store-ranking.md) |
| Free-model second opinion | 34 of 40 (85%) | disagreement is a review flag; [decision 0019](docs/decisions/0019-pakistan-market-store-ranking.md) |
| Best-seller collection picker, held-out | 19 of 20 (95%) | 87% in-sample; [decision 0021](docs/decisions/0021-robots-wildcards-and-best-seller-collection.md) |
| Chrome UX coverage of PKR stores | 909 of 911 | [decision 0020](docs/decisions/0020-crux-country-popularity.md) |

> [!NOTE]
> Held-out check of the business model for Pakistan is still due. Each error found becomes a test.

</details>

<details><summary><b>What we do not know</b></summary>

- Revenue, orders, conversion, ad spend: `[unknown]`. Public records do not show them.
- Supplier cost and margin per product: `[unknown]` until the margin model (M1).
- Demand on eBay: `[unknown]`. A Shopify store's success shows demand and method, not eBay demand. Only our own live test measures it.
- Social-only sellers (Instagram, WhatsApp) leave no trace on their own pages, so Pakistan is likely under-counted.

</details>

<details><summary><b>Data sources and terms</b></summary>

- Popularity by country: [Chrome UX Report](https://developer.chrome.com/docs/crux), via [BigQuery](https://cloud.google.com/bigquery/public-data), licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Global rank: [Tranco list](https://tranco-list.eu).
- Store pages: public machine records only (`/meta.json`, product feed, `robots.txt` respected). No data is ingested before its terms are read and recorded.
- Supplier: [CJ Dropshipping](https://cjdropshipping.com) product images and catalogue. Marketplace: [eBay](https://www.ebay.com).

</details>

<details><summary><b>Run it yourself</b></summary>

```bash
make setup                       # install hooks and tools
make test                        # run the test suite
python -m scout.market_rank --market pk --top 40
python scripts/readme_build.py   # rebuild this page
```

</details>

## Project map

| Folder | What lives there |
|---|---|
| [`docs/plan/`](docs/plan) | goals, exit criteria, north star, dev loop |
| [`docs/decisions/`](docs/decisions) | every owner decision and terms record |
| [`docs/research/`](docs/research) | sourced research reports |
| [`scout/`](scout) | pipeline: discovery, profiling, ranking, free-model router |
| [`ui/`](ui) | the private explorer; its data files are gitignored and published only to the owner's private page |

<sub>Generated by `scripts/readme_build.py` on {d} UTC from the private lake; numbers are aggregates.</sub>
"""
    files["README.md"] = readme
    return files


def drop_generic(names, text: str) -> list[str]:
    vocab = set(re.findall(r"[a-z]+", text.lower()))
    return [n for n in names if " " in n.strip() or n.lower() not in vocab]


def write(files: dict[str, str], domains=(), names=()) -> None:
    # A one-word shop name that is also an ordinary word the page itself uses
    # ("Retailer") cannot identify a store; multi-word names and domains still count.
    names = drop_generic(names, "\n".join(files.values()))
    for path, text in files.items():
        assert_public_safe(text, domains, names)
    for path, text in sorted(files.items()):
        (ROOT / path).write_text(text, encoding="utf-8")


MIN_KEEP = 0.9  # a market may not lose more than 10% of its stores in one refresh


def shrinkage(new: dict, committed_path: Path) -> str:
    """Why `new` looks like a partial lake compared with the committed snapshot,
    or "" when it is fine (store counts only grow, apart from small cleanups)."""
    try:
        old = json.loads(committed_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    for m, o in old.get("markets", {}).items():
        before = o.get("stores") or 0
        after = (new.get("markets", {}).get(m) or {}).get("stores") or 0
        if before and after < MIN_KEEP * before:
            return f"{m} stores {after} < {MIN_KEEP:.0%} of {before}"
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-stats", help="render from this stats.json, skip the lake")
    a = ap.parse_args(argv)
    domains, names = [], []
    if a.from_stats:
        stats = json.loads(Path(a.from_stats).read_text(encoding="utf-8"))
        try:
            domains, names = lake_identities()
        except (OSError, ValueError, ImportError):
            pass  # no lake: the domain-pattern and secret checks still run
    else:
        try:
            stats = collect()
            domains, names = lake_identities()
        except (OSError, ValueError, ImportError) as e:
            print(
                f"lake unavailable ({e}); rendering from committed stats.json",
                file=sys.stderr,
            )
            stats = json.loads((OUT / "stats.json").read_text(encoding="utf-8"))
        else:
            shrunk = shrinkage(stats, OUT / "stats.json")
            if shrunk:
                # A cloud run with a missing or partial lake must not publish
                # near-zero numbers: keep the last good snapshot.
                print(f"keeping committed stats.json: {shrunk}", file=sys.stderr)
                stats = json.loads((OUT / "stats.json").read_text(encoding="utf-8"))
                write(render(stats), domains, names)
                return 0
            text = json.dumps(stats, indent=1, sort_keys=True) + "\n"
            assert_public_safe(text, domains, drop_generic(names, text))
            OUT.mkdir(parents=True, exist_ok=True)
            (OUT / "stats.json").write_text(text, encoding="utf-8")
    write(render(stats), domains, names)
    print(
        f"README.md and {len(charts(stats))} charts written ({stats['generated_at']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
