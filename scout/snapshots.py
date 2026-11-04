"""Weekly store snapshots of a Shopify public /products.json feed.

Only ids, numbers and dates are kept. Titles, descriptions and any other text
are dropped by ``compact``, so stored snapshots hold no marketing copy.

Pure functions only: no network, no file I/O, no clock reads (the caller passes
``now``), so every result is deterministic and testable.
"""

from __future__ import annotations

import math
import re
from datetime import UTC
from email.utils import parsedate_to_datetime
from typing import Any

NOTE = "availability flips are a demand proxy, not units sold"
INCOMPLETE_WARNING = "incomplete snapshot: removals not computed"
INCOMPLETE_OLD_WARNING = "incomplete earlier snapshot: new products not computed"

_DIGITS = re.compile(r"[0-9]+")


def _is_int_id(value: Any) -> bool:
    """Return True for a real integer id (bool is excluded)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _parse_price(value: Any) -> float | None:
    """Parse a Shopify price string such as "29.00"; None if missing or invalid."""
    if not isinstance(value, str):
        return None
    try:
        price = float(value)
    except ValueError:
        return None
    return price if math.isfinite(price) else None


def _date_part(value: Any) -> str | None:
    """Return the YYYY-MM-DD prefix of an ISO timestamp, or None if absent."""
    if isinstance(value, str) and value:
        return value[:10]
    return None


def compact(products: list[dict]) -> dict[int, dict]:
    """Reduce a /products.json product list to ids, prices, availability and dates.

    Returns a mapping of product id to::

        {"created": "YYYY-MM-DD" | None,
         "updated": "YYYY-MM-DD" | None,
         "min_price": float | None,
         "variants": {variant_id: {"price": float | None, "available": bool}}}

    Non-dict items and products without an integer id are skipped. Variants
    without an integer id are skipped. Unparsable prices become None and are
    ignored when computing ``min_price``. ``available`` is True only when the
    feed says exactly ``true``.
    """
    result: dict[int, dict] = {}
    for product in products:
        if not isinstance(product, dict) or not _is_int_id(product.get("id")):
            continue

        variants: dict[int, dict] = {}
        prices: list[float] = []
        raw_variants = product.get("variants")
        for variant in raw_variants if isinstance(raw_variants, list) else []:
            if not isinstance(variant, dict) or not _is_int_id(variant.get("id")):
                continue
            price = _parse_price(variant.get("price"))
            variants[variant["id"]] = {
                "price": price,
                "available": variant.get("available") is True,
            }
            if price is not None:
                prices.append(price)

        result[product["id"]] = {
            "created": _date_part(product.get("created_at")),
            "updated": _date_part(product.get("updated_at")),
            "min_price": min(prices) if prices else None,
            "variants": variants,
        }
    return result


def diff(
    old: dict, new: dict, complete: bool = True, old_complete: bool = True
) -> dict:
    """Compare two compact snapshots (outputs of ``compact``).

    ``complete`` must be False when the feed was fetched only in part. Then a
    product missing from ``new`` may just be on a page that failed, so
    ``removed_ids`` is left empty and a warning is added. ``old_complete`` must be
    False when the earlier feed was partial: a product it simply missed would
    otherwise look new, so ``new_ids`` is left empty with a warning.

    Returns a dict with sorted id lists ``new_ids``, ``removed_ids``,
    ``repriced`` (``{"id", "old", "new"}`` where min_price changed, None
    included), ``went_unavailable`` and ``back_in_stock`` (``[product_id,
    variant_id]`` pairs), plus ``counts``, ``warnings`` and ``note``. The
    inputs are not modified.
    """
    new_ids = sorted(set(new) - set(old)) if old_complete else []
    removed_ids = sorted(set(old) - set(new)) if complete else []

    repriced: list[dict] = []
    went_unavailable: list[list[int]] = []
    back_in_stock: list[list[int]] = []

    for pid in sorted(set(old) & set(new)):
        old_prod, new_prod = old[pid], new[pid]
        if old_prod.get("min_price") != new_prod.get("min_price"):
            repriced.append(
                {
                    "id": pid,
                    "old": old_prod.get("min_price"),
                    "new": new_prod.get("min_price"),
                }
            )

        old_variants = old_prod.get("variants", {})
        new_variants = new_prod.get("variants", {})
        for vid in sorted(set(old_variants) & set(new_variants)):
            was = old_variants[vid]["available"]
            now = new_variants[vid]["available"]
            if was and not now:
                went_unavailable.append([pid, vid])
            elif now and not was:
                back_in_stock.append([pid, vid])

    warnings = []
    if not complete:
        warnings.append(INCOMPLETE_WARNING)
    if not old_complete:
        warnings.append(INCOMPLETE_OLD_WARNING)
    return {
        "new_ids": new_ids,
        "removed_ids": removed_ids,
        "repriced": repriced,
        "went_unavailable": went_unavailable,
        "back_in_stock": back_in_stock,
        "counts": {
            "new_count": len(new_ids),
            "removed_count": len(removed_ids),
            "repriced_count": len(repriced),
            "went_unavailable_count": len(went_unavailable),
            "back_in_stock_count": len(back_in_stock),
        },
        "warnings": warnings,
        "note": NOTE,
    }


def parse_retry_after(value: str | None, now: float) -> float | None:
    """Return seconds to wait given a Retry-After header value.

    Accepts non-negative integer seconds ("120") or an HTTP-date. A date with no
    timezone is read as UTC. A date in the past gives 0.0. Returns None when the
    value is missing, empty or invalid (including negative numbers).
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if _DIGITS.fullmatch(text):
        return float(int(text))
    try:
        when = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return max(0.0, when.timestamp() - now)


def next_delay(
    attempt: int,
    retry_after: float | None,
    base: float = 2.0,
    cap: float = 120.0,
) -> float:
    """Return the wait before retry number ``attempt`` (0-based), in seconds.

    The exponential backoff ``base * 2**attempt`` is capped at ``cap``. When the
    server sent a Retry-After, the result is never below it, even if that is
    above ``cap``. A negative Retry-After counts as 0.
    """
    exponent = min(max(0, attempt), 64)  # keeps 2**n finite for huge attempts
    backoff = min(cap, base * 2.0**exponent)
    if retry_after is None:
        return backoff
    return max(backoff, max(0.0, retry_after))
