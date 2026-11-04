"""Screen CJ product images with a free vision model; cache the verdicts.

eBay's picture policy bans text, logos, watermarks and borders, and our own
rules (CLAUDE.md) forbid brand content and images of children. This command
checks the first few images of each viable candidate and appends one row per
image to warehouse/seeds/llm_image_screen_cache.csv, keyed by the sha256 of the
image URL (no URLs or CJ text in git). The warehouse counts clean images per
product. A flag only routes a product to review; it never excludes it.

    python -m scout.screen_images --per-product 3 --limit 300
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

CACHE = Path("warehouse/seeds/llm_image_screen_cache.csv")
DB = Path("data/private/warehouse.duckdb")
PROMPT_VERSION = "img-v1"
CHECKS = [
    "text_overlay",
    "logo_or_brand",
    "watermark",
    "border_or_collage",
    "person",
    "child",
]
FIELDS = ["image_sha256", "clean", *CHECKS, "model", "prompt_version"]

PROMPT = """You check one product photo for an online marketplace listing.
Answer each question with true or false, judging only what is visible:
- text_overlay: any added text, numbers, prices, badges or callouts on the image
  (text printed on the product itself does not count)
- logo_or_brand: any brand logo or trademark, on the product or the image
- watermark: any watermark or semi-transparent mark
- border_or_collage: a frame, border, or several photos combined into one
- person: a person or part of a person (hands count)
- child: a child or baby
Return only JSON with exactly these keys: {"text_overlay": false,
"logo_or_brand": false, "watermark": false, "border_or_collage": false,
"person": false, "child": false}"""


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def parse_verdict(text: str) -> dict | None:
    """All six checks must be present as booleans, otherwise the reply is unusable."""
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except ValueError:
        return None
    if not isinstance(data, dict) or not all(
        isinstance(data.get(k), bool) for k in CHECKS
    ):
        return None
    out = {k: data[k] for k in CHECKS}
    # Hands or people are allowed in lifestyle shots; children are not, and the
    # other four break eBay's picture policy.
    out["clean"] = not any(
        out[k]
        for k in (
            "text_overlay",
            "logo_or_brand",
            "watermark",
            "border_or_collage",
            "child",
        )
    )
    return out


def screen(urls: list[str], chat):
    """Yield one cache row per usable verdict, so callers can write as they go."""
    for url in urls:
        try:
            reply = chat(PROMPT, task="vision", image_urls=[url], json_mode=True)
        except Exception as exc:  # noqa: BLE001 - one bad image must not stop the run
            print(f"skip {url_hash(url)[:12]}: {exc}", file=sys.stderr)
            continue
        verdict = parse_verdict(reply.get("text", ""))
        if verdict is None:
            continue
        yield {
            "image_sha256": url_hash(url),
            **verdict,
            "model": reply.get("model", "?"),
            "prompt_version": PROMPT_VERSION,
        }


def load_cache(path: Path = CACHE) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="") as fh:
        return {r["image_sha256"] for r in csv.DictReader(fh)}


def main(argv: list[str] | None = None) -> int:
    import duckdb

    from scout.llm import chat

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--per-product", type=int, default=3)
    ap.add_argument("--limit", type=int, default=300, help="max model calls")
    a = ap.parse_args(argv)

    con = duckdb.connect(str(DB), read_only=True)
    urls = [
        r[0]
        for r in con.execute(
            "select i.url from stg.stg_cj_images i "
            "join mart.mart_supply_candidates m using (pid) "
            "where m.is_viable and i.position < ? order by m.min_price, i.pid, i.position",
            [a.per_product],
        ).fetchall()
    ]
    con.close()
    cached = load_cache()
    todo = [u for u in urls if url_hash(u) not in cached][: a.limit]
    write_header = not CACHE.exists() or CACHE.stat().st_size == 0
    done = 0
    with CACHE.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        if write_header:
            w.writeheader()
        for row in screen(todo, chat):  # written as we go: a crash keeps progress
            w.writerow(row)
            fh.flush()
            done += 1
    print(f"asked {len(todo)}, cached {done}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
