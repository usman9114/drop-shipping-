"""Google Trends (US) evidence pulls.

Usage:
    python -m scout.trends "dog harness" "cat tree" --out data/evidence/trends/pet.csv
    python -m scout.trends --file keywords.txt --out data/evidence/trends/batch.csv

For each keyword (queried alone, so values are 0-100 within that keyword's own
history), reports:
  - mean interest over the last 12 months
  - growth: mean of last 12 months vs the 12 months before (from a 5-year pull)
  - peak months (seasonality) and peak/trough ratio
Values are relative interest, not search volume. Compare growth and
seasonality across keywords, not absolute levels.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import date
from pathlib import Path

CACHE_DIR = Path("data/evidence/trends/.cache")
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def _fetch(keyword: str, timeframe: str, geo: str, retries: int = 4):
    from pytrends.request import TrendReq

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = f"{keyword}|{timeframe}|{geo}|{date.today().isoformat()}"
    cache = CACHE_DIR / (str(abs(hash(key)) % 10**12) + ".json")
    if cache.exists():
        data = json.loads(cache.read_text())
        if data.get("key") == key:
            return data["series"]

    delay = 5.0
    for attempt in range(retries):
        try:
            client = TrendReq(hl="en-US", tz=300)
            client.build_payload([keyword], timeframe=timeframe, geo=geo)
            df = client.interest_over_time()
            series = (
                []
                if df.empty
                else [
                    (idx.date().isoformat(), int(v)) for idx, v in df[keyword].items()
                ]
            )
            cache.write_text(json.dumps({"key": key, "series": series}))
            return series
        except Exception as exc:  # pytrends raises generic errors on 429
            if attempt == retries - 1:
                raise RuntimeError(
                    f"Trends fetch failed for {keyword!r}: {exc}"
                ) from exc
            time.sleep(delay)
            delay *= 2
    return []


def analyze(keyword: str, geo: str = "US") -> dict:
    five_y = _fetch(keyword, "today 5-y", geo)
    if not five_y:
        return {"keyword": keyword, "status": "no_data"}

    # five_y is weekly; split into last 52 points and the 52 before.
    last = [v for _, v in five_y[-52:]]
    prev = [v for _, v in five_y[-104:-52]]
    mean_last = sum(last) / len(last) if last else 0
    mean_prev = sum(prev) / len(prev) if prev else 0
    growth = (mean_last - mean_prev) / mean_prev if mean_prev else None

    by_month: dict[int, list[int]] = {}
    for d, v in five_y[-156:]:  # last ~3 years for seasonality
        by_month.setdefault(int(d[5:7]), []).append(v)
    month_avg = {m: sum(vs) / len(vs) for m, vs in by_month.items() if vs}
    ranked = sorted(month_avg, key=month_avg.get, reverse=True)
    trough = min(month_avg.values()) if month_avg else 0
    peak = max(month_avg.values()) if month_avg else 0

    return {
        "keyword": keyword,
        "status": "ok",
        "mean_interest_12m": round(mean_last, 1),
        "growth_12m_vs_prior": None if growth is None else round(growth, 3),
        "peak_months": ",".join(MONTHS[m - 1] for m in ranked[:3]),
        "seasonality_ratio": round(peak / trough, 2) if trough else None,
        "weeks": len(five_y),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("keywords", nargs="*")
    ap.add_argument("--file", help="text file, one keyword per line (# comments ok)")
    ap.add_argument("--geo", default="US")
    ap.add_argument("--out", help="CSV output path")
    ap.add_argument("--sleep", type=float, default=2.0, help="seconds between keywords")
    args = ap.parse_args(argv)

    kws = list(args.keywords)
    if args.file:
        for line in Path(args.file).read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                kws.append(line)
    if not kws:
        ap.error("no keywords given")

    rows = []
    for i, kw in enumerate(kws):
        try:
            rows.append(analyze(kw, args.geo))
        except RuntimeError as exc:
            rows.append({"keyword": kw, "status": f"error: {exc}"})
        print(json.dumps(rows[-1]), file=sys.stderr)
        if i < len(kws) - 1:
            time.sleep(args.sleep)

    fields = [
        "keyword",
        "status",
        "mean_interest_12m",
        "growth_12m_vs_prior",
        "peak_months",
        "seasonality_ratio",
        "weeks",
    ]
    out = open(args.out, "w", newline="") if args.out else sys.stdout
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    w = csv.DictWriter(
        out, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
    )
    w.writeheader()
    w.writerows(rows)
    if args.out:
        out.close()
        print(f"wrote {args.out} ({len(rows)} keywords)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
