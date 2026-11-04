"""Fill the warehouse's LLM product-type cache for titles the rules missed.

The LLM never runs inside dbt. This command reads unclassified titles of the
pre-filtered candidates (mart.mart_prefilter), asks a free model for a short generic product type, and appends
(sha256 of lower-cased title, type, model, prompt version) to the seed
warehouse/seeds/llm_product_type_cache.csv. Titles themselves are not stored,
so the committed cache carries no CJ text. Re-running only asks about titles
that are not cached yet, so results stay fixed once written.

    python -m scout.classify --limit 100
    python -m scout.classify --phrases          # eBay search phrase per candidate

`--phrases` fills warehouse/seeds/llm_search_phrase_cache.csv the same way: one
phrase a buyer would type, used as the Terapeak search for that product.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

CACHE = Path("warehouse/seeds/llm_product_type_cache.csv")
DB = Path("data/private/warehouse.duckdb")
PROMPT_VERSION = "pt-v1"
FIELDS = ["title_sha256", "product_type", "model", "prompt_version"]
_TYPE = re.compile(r"^[a-z][a-z0-9 &'-]{1,40}$")
PHRASE_CACHE = Path("warehouse/seeds/llm_search_phrase_cache.csv")
PHRASE_VERSION = "phrase-v1"
PHRASE_FIELDS = ["title_sha256", "search_phrase", "model", "prompt_version"]
_PHRASE = re.compile(r"^[a-z0-9][a-z0-9 .&'/-]{2,60}$")

PHRASE_PROMPT = """For each product title, write the search a US eBay buyer would type to
find this exact kind of item: 2-6 lower-case words, the most specific generic
terms (item type plus the one or two attributes buyers filter on, such as size,
material or count). No brand names, no marketing words, no colours unless the
colour is the point. Return only JSON: {{"labels": [{{"i": <index>, "phrase": "<phrase>"}}, ...]}}

Titles:
{titles}"""

PROMPT = """You label marketplace product titles with a short generic product type.
Rules: 1-4 lower-case words, a common noun phrase a shopper would search
(e.g. "pet collar and leash", "bathroom shelf", "necklace"). No brand names,
no colours, no sizes, no materials. Reuse one of these existing types when it
fits: {types}.
Return only JSON: {{"labels": [{{"i": <index>, "type": "<type>"}}, ...]}}

Titles:
{titles}"""


def title_hash(title: str) -> str:
    return hashlib.sha256(title.lower().encode("utf-8")).hexdigest()


def load_cache(path: Path = CACHE) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(newline="") as fh:
        return {r["title_sha256"]: r for r in csv.DictReader(fh)}


def parse_labels(text: str, n: int, key: str = "type", pattern=_TYPE) -> dict[int, str]:
    """Keep only well-formed labels for indexes we asked about."""
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
    except ValueError:
        return {}
    out = {}
    for item in data.get("labels", []) if isinstance(data, dict) else []:
        if not isinstance(item, dict):
            continue
        i, t = item.get("i"), str(item.get(key, "")).strip().lower()
        if isinstance(i, int) and 0 <= i < n and pattern.match(t):
            out[i] = t
    return out


def classify(
    titles: list[str], known_types: list[str], chat, batch: int = 25
) -> list[dict]:
    rows = []
    for start in range(0, len(titles), batch):
        chunk = titles[start : start + batch]
        listing = "\n".join(f"{i}. {t}" for i, t in enumerate(chunk))
        reply = chat(
            PROMPT.format(types=", ".join(sorted(known_types)), titles=listing),
            task="bulk",
            json_mode=True,
        )
        for i, t in parse_labels(reply.get("text", ""), len(chunk)).items():
            rows.append(
                {
                    "title_sha256": title_hash(chunk[i]),
                    "product_type": t,
                    "model": reply.get("model", "?"),
                    "prompt_version": PROMPT_VERSION,
                }
            )
    return rows


def phrases(titles: list[str], chat, batch: int = 25) -> list[dict]:
    rows = []
    for start in range(0, len(titles), batch):
        chunk = titles[start : start + batch]
        listing = "\n".join(f"{i}. {t}" for i, t in enumerate(chunk))
        reply = chat(PHRASE_PROMPT.format(titles=listing), task="bulk", json_mode=True)
        found = parse_labels(reply.get("text", ""), len(chunk), "phrase", _PHRASE)
        for i, phrase in found.items():
            rows.append(
                {
                    "title_sha256": title_hash(chunk[i]),
                    "search_phrase": phrase,
                    "model": reply.get("model", "?"),
                    "prompt_version": PHRASE_VERSION,
                }
            )
    return rows


def _append(path: Path, fields: list[str], rows: list[dict]) -> None:
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        if write_header:
            w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    import duckdb

    from scout.llm import chat

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--phrases", action="store_true", help="search phrases instead")
    a = ap.parse_args(argv)

    con = duckdb.connect(str(DB), read_only=True)
    if a.phrases:
        titles = [
            r[0]
            for r in con.execute(
                "select p.title from core.core_dim_product p "
                "join mart.mart_supply_candidates m using (pid) "
                "where m.is_viable order by m.min_price"
            ).fetchall()
        ]
        con.close()
        cached = load_cache(PHRASE_CACHE)
        todo = [t for t in titles if t and title_hash(t) not in cached][: a.limit]
        new = phrases(todo, chat)
        _append(PHRASE_CACHE, PHRASE_FIELDS, new)
        print(f"asked {len(todo)}, cached {len(new)}", file=sys.stderr)
        return 0
    rows = con.execute(
        "select p.title from core.core_dim_product p "
        "join mart.mart_prefilter f using (pid) "
        "where p.product_type is null order by p.pid"
    ).fetchall()
    known = [
        r[0]
        for r in con.execute(
            "select distinct product_type from core.core_dim_product "
            "where product_type is not null"
        ).fetchall()
    ]
    con.close()
    cache = load_cache()
    todo = [t for (t,) in rows if t and title_hash(t) not in cache][: a.limit]
    new = classify(todo, known, chat)
    _append(CACHE, FIELDS, new)
    print(f"asked {len(todo)}, cached {len(new)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
