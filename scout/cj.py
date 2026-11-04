"""Thin read-only client for the CJ Dropshipping catalogue API.

Written from docs/research/18-cj-api-cheatsheet.md; response shapes checked
against the live API on 2026-11-04 (see doc 18, "Live findings").

Usage:
    python -m scout.cj search "magnetic card holder" --country US --pages 2 \
        --out data/private/cj-search.json
    python -m scout.cj detail <pid> --country US --out data/private/cj-detail.json
    python -m scout.cj stock <pid> --out data/private/cj-stock.json
    python -m scout.cj freight <vid> --start US --zip 10001 --out data/private/cj-freight.json

Terms gate: CJ's API data-use terms have not been confirmed, so raw output may
only be written under data/private/ (gitignored). Commit derived decisions,
not raw pulls.

Env: CJ_API_KEY (also read from .env).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

BASE = "https://developers.cjdropshipping.com/api2.0/v1"
MIN_INTERVAL = 1.1  # docs say QPS = 1 (unverified)
PRIVATE_DIR = Path("data/private")


class CJError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(f"CJ error {code}: {message}")
        self.code = code


def parse_price(value) -> tuple[float | None, float | None]:
    """CJ prices may be a number or a range string such as '1.20 -- 3.50'."""
    text = "" if value is None else str(value).strip()
    if re.match(r"^-\s*\d", text):  # a negative price is invalid, not a range
        return (None, None)
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text)]
    return (min(nums), max(nums)) if nums else (None, None)


def _num(value) -> float | None:
    """CJ sends numbers as numbers or strings ('30.00'); anything else is None."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _json_list(value) -> list[str]:
    """Material and packing come as a JSON-encoded list string: '["Leather"]'."""
    if isinstance(value, list):
        return [str(x) for x in value]
    try:
        out = json.loads(value)
    except (TypeError, ValueError):
        return [value] if isinstance(value, str) and value else []
    return [str(x) for x in out] if isinstance(out, list) else []


def _dicts(value) -> list[dict]:
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def normalize_listing(item: dict) -> dict:
    low, high = parse_price(item.get("sellPrice"))
    return {
        "pid": item.get("id"),
        "name": item.get("nameEn"),
        "sku": item.get("sku"),
        "price_low": low,
        "price_high": high,
        "price_raw": item.get("sellPrice"),
        "image": item.get("bigImage"),
        # Stock in the filtered country when countryCode is set (live check:
        # equals the US warehouse total from the stock endpoint).
        "warehouse_inventory": item.get("warehouseInventoryNum"),
        "verified_inventory": item.get("totalVerifiedInventory"),
        "category_id": item.get("categoryId"),
        "listed_num": item.get("listedNum"),
    }


def normalize_detail(data: dict) -> dict:
    """With countryCode=US, CJ returns only the variants stocked in the US.
    variants[].inventories is null in live data: use stock() instead."""
    sug_low, sug_high = parse_price(data.get("suggestSellPrice"))
    return {
        "pid": data.get("pid"),
        "name": data.get("productNameEn"),
        "sku": data.get("productSku"),
        "category": data.get("categoryName"),
        "weight_g": _num(data.get("productWeight")),
        "packing_weight_g": _num(data.get("packingWeight")),
        "materials": _json_list(data.get("materialNameEn")),
        "packing": _json_list(data.get("packingNameEn")),
        "suggested_price_low": sug_low,
        "suggested_price_high": sug_high,
        "images": [
            x
            for x in [data.get("bigImage"), *(data.get("productImageSet") or [])]
            if isinstance(x, str) and x
        ],
        "variants": [
            {
                "vid": v.get("vid"),
                "sku": v.get("variantSku"),
                "image": v.get("variantImage"),
                "name": v.get("variantNameEn"),
                "price": _num(v.get("variantSellPrice")),
                "weight_g": _num(v.get("variantWeight")),
                "dims_mm": [
                    v.get("variantLength"),
                    v.get("variantWidth"),
                    v.get("variantHeight"),
                ],
            }
            for v in _dicts(data.get("variants"))
        ],
    }


def normalize_stock(data) -> dict:
    """Per-country stock from product/stock/getInventoryByPid."""
    by_country: dict[str, dict] = {}
    for inv in _dicts(
        (data or {}).get("inventories") if isinstance(data, dict) else None
    ):
        cc = inv.get("countryCode")
        if cc:
            by_country[cc] = {
                "total": inv.get("totalInventoryNum"),
                "cj": inv.get("cjInventoryNum"),
                "factory": inv.get("factoryInventoryNum"),
            }
    return by_country


def normalize_freight(data) -> list[dict]:
    """Quotes sorted cheapest first. logisticAging is a string range ('3-8'),
    unit not documented (days assumed)."""
    out = []
    for q in _dicts(data):
        days = [int(x) for x in re.findall(r"\d+", str(q.get("logisticAging") or ""))]
        out.append(
            {
                "carrier": q.get("logisticName"),
                "price_usd": _num(q.get("logisticPrice")),
                "days_low": min(days) if days else None,
                "days_high": max(days) if days else None,
            }
        )
    return sorted(out, key=lambda q: (q["price_usd"] is None, q["price_usd"] or 0))


def _default_session():
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    s = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


class CJClient:
    def __init__(self, api_key=None, session=None, sleep=time.sleep):
        self.api_key = api_key or os.environ.get("CJ_API_KEY")
        if not self.api_key:
            raise CJError("-", "CJ_API_KEY is not set")
        self._session = session or _default_session()
        self._sleep = sleep
        self._last = 0.0
        self._token = None

    def _raw(self, method, path, params=None, body=None, token=None):
        wait = MIN_INTERVAL - (time.monotonic() - self._last)
        if wait > 0:
            self._sleep(wait)
        headers = {"CJ-Access-Token": token} if token else {}
        resp = self._session.request(
            method,
            f"{BASE}{path}",
            params=params,
            json=body,
            headers=headers,
            timeout=30,
        )
        self._last = time.monotonic()
        status = getattr(resp, "status_code", 200)
        try:
            payload = resp.json()
        except ValueError as exc:
            raise CJError(status, "response was not JSON") from exc
        if not isinstance(payload, dict):
            raise CJError(status, "unexpected response shape")
        if payload.get("code") != 200:
            raise CJError(
                payload.get("code", status), payload.get("message") or f"HTTP {status}"
            )
        return payload.get("data")

    def _auth(self) -> str:
        data = self._raw(
            "POST", "/authentication/getAccessToken", body={"apiKey": self.api_key}
        )
        self._token = data["accessToken"]
        return self._token

    def call(self, method, path, params=None, body=None):
        for attempt in range(2):
            token = self._token or self._auth()
            try:
                return self._raw(method, path, params, body, token)
            except CJError as exc:
                if exc.code == 1600001 and attempt == 0:  # token expired or invalid
                    self._token = None
                    continue
                raise

    def search(self, keyword=None, country="US", pages=1, size=100) -> list[dict]:
        """country filters to products with stock in that country's warehouse.
        keyword=None lists the whole (filtered) catalogue."""
        rows: list[dict] = []
        for page in range(1, pages + 1):
            params = {"page": page, "size": size}
            if keyword:
                params["keyWord"] = keyword
            if country:
                params["countryCode"] = country
            data = self.call("GET", "/product/listV2", params=params)
            contents = _dicts(
                (data or {}).get("content") if isinstance(data, dict) else None
            )
            items = [p for c in contents for p in _dicts(c.get("productList"))]
            if not items:
                break
            rows += [normalize_listing(i) for i in items]
        return rows

    def detail(self, pid, country="US") -> dict:
        data = self.call(
            "GET", "/product/query", params={"pid": pid, "countryCode": country}
        )
        return normalize_detail(data or {})

    def stock(self, pid) -> dict:
        data = self.call("GET", "/product/stock/getInventoryByPid", params={"pid": pid})
        return normalize_stock(data)

    def freight(
        self, vid, quantity=1, start="US", end="US", zip_code=None
    ) -> list[dict]:
        """Live: a variant with no stock at `start` returns error 1600300
        ("Request body is required...") rather than an empty list."""
        body = {
            "startCountryCode": start,
            "endCountryCode": end,
            "products": [{"vid": vid, "quantity": quantity}],
        }
        if zip_code:
            body["zip"] = zip_code
        return normalize_freight(
            self.call("POST", "/logistic/freightCalculate", body=body)
        )


def private_path(out: str) -> Path:
    """Raw CJ output may only go under data/private/ (terms gate)."""
    path = Path(out).resolve()
    try:
        path.relative_to(PRIVATE_DIR.resolve())
    except ValueError:
        raise SystemExit(
            f"refusing to write raw CJ data outside {PRIVATE_DIR}/ (terms gate)"
        )
    return path


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="CJ catalogue client")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("keyword", nargs="?", help="omit to list the whole catalogue")
    s.add_argument("--country", default="US")
    s.add_argument("--pages", type=int, default=1)
    d = sub.add_parser("detail")
    d.add_argument("pid")
    d.add_argument("--country", default="US")
    st = sub.add_parser("stock")
    st.add_argument("pid")
    f = sub.add_parser("freight")
    f.add_argument("vid")
    f.add_argument("--start", default="US")
    f.add_argument("--zip", dest="zip_code")
    for p in (s, d, st, f):
        p.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    out = private_path(a.out)
    client = CJClient()
    if a.cmd == "search":
        result = client.search(a.keyword, a.country, a.pages)
    elif a.cmd == "detail":
        result = client.detail(a.pid, a.country)
    elif a.cmd == "stock":
        result = client.stock(a.pid)
    else:
        result = client.freight(a.vid, start=a.start, zip_code=a.zip_code)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f"wrote {out} ({len(result)} items)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
