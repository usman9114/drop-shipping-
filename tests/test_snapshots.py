"""Tests for scout.snapshots (pure logic, no network)."""

import copy
from datetime import UTC, datetime
from email.utils import format_datetime

from scout import snapshots

NOW = 1_700_000_000.0  # fixed clock for Retry-After tests


def _product(
    pid, variants=None, created="2026-01-02T03:04:05-05:00", updated="2026-02-03"
):
    return {
        "id": pid,
        "title": "must not be kept",
        "created_at": created,
        "updated_at": updated,
        "variants": variants or [],
    }


def _variant(vid, price="10.00", available=True):
    return {"id": vid, "price": price, "compare_at_price": None, "available": available}


# compact -------------------------------------------------------------------


def test_compact_keeps_only_ids_numbers_and_dates():
    out = snapshots.compact([_product(7, [_variant(70, "29.00")])])
    assert out == {
        7: {
            "created": "2026-01-02",
            "updated": "2026-02-03",
            "min_price": 29.0,
            "variants": {70: {"price": 29.0, "available": True}},
        }
    }
    assert "title" not in out[7]


def test_compact_skips_non_dict_and_bad_product_ids():
    products = [
        "text",
        None,
        {"created_at": "2026-01-01"},
        {"id": True},
        {"id": "5"},
        {"id": 3.0},
        _product(9),
    ]
    assert list(snapshots.compact(products)) == [9]


def test_compact_empty_input():
    assert snapshots.compact([]) == {}


def test_compact_missing_or_non_string_dates_are_none():
    out = snapshots.compact([{"id": 1, "created_at": None, "updated_at": 20260101}])
    assert out[1]["created"] is None
    assert out[1]["updated"] is None


def test_compact_unparsable_and_non_finite_prices_are_none_and_ignored():
    product = _product(
        1,
        [
            _variant(1, "abc"),
            _variant(2, None),
            _variant(3, "nan"),
            _variant(4, "inf"),
            _variant(5, "12.50"),
            _variant(6, "9.99"),
        ],
    )
    out = snapshots.compact([product])[1]
    assert out["variants"][1]["price"] is None
    assert out["variants"][2]["price"] is None
    assert out["variants"][3]["price"] is None
    assert out["variants"][4]["price"] is None
    assert out["min_price"] == 9.99


def test_compact_min_price_none_when_no_price_parses():
    out = snapshots.compact([_product(1, [_variant(1, "x")])])
    assert out[1]["min_price"] is None


def test_compact_skips_variants_without_int_id_or_not_dicts():
    product = _product(
        1, [{"price": "5.00"}, "junk", _variant(True, "1.00"), _variant(2)]
    )
    out = snapshots.compact([product])[1]
    assert list(out["variants"]) == [2]


def test_compact_available_only_when_exactly_true():
    product = _product(
        1,
        [
            _variant(1, available=True),
            _variant(2, available=False),
            _variant(3, available="true"),
        ],
    )
    variants = snapshots.compact([product])[1]["variants"]
    assert variants[1]["available"] is True
    assert variants[2]["available"] is False
    assert variants[3]["available"] is False


def test_compact_tolerates_missing_or_bad_variants_field():
    out = snapshots.compact([{"id": 1}, {"id": 2, "variants": None}])
    assert out[1]["variants"] == {}
    assert out[2]["variants"] == {}
    assert out[2]["min_price"] is None


# diff ----------------------------------------------------------------------


def _snap(*products):
    return snapshots.compact(list(products))


def test_diff_new_and_removed_ids_when_complete():
    old = _snap(_product(1), _product(2))
    new = _snap(_product(2), _product(3))
    result = snapshots.diff(old, new)
    assert result["new_ids"] == [3]
    assert result["removed_ids"] == [1]
    assert result["counts"]["new_count"] == 1
    assert result["counts"]["removed_count"] == 1
    assert result["warnings"] == []


def test_diff_incomplete_snapshot_does_not_compute_removals():
    old = _snap(_product(1), _product(2))
    new = _snap(_product(2))
    result = snapshots.diff(old, new, complete=False)
    assert result["removed_ids"] == []
    assert result["counts"]["removed_count"] == 0
    assert result["warnings"] == ["incomplete snapshot: removals not computed"]


def test_diff_incomplete_still_reports_new_ids_and_flips():
    old = _snap(_product(1, [_variant(10, available=True)]))
    new = _snap(_product(1, [_variant(10, available=False)]), _product(2))
    result = snapshots.diff(old, new, complete=False)
    assert result["new_ids"] == [2]
    assert result["went_unavailable"] == [[1, 10]]


def test_diff_repriced_including_none_change():
    old = _snap(_product(1, [_variant(1, "10.00")]), _product(2, [_variant(2, "5.00")]))
    new = _snap(_product(1, [_variant(1, "12.00")]), _product(2, [_variant(2, "x")]))
    result = snapshots.diff(old, new)
    assert result["repriced"] == [
        {"id": 1, "old": 10.0, "new": 12.0},
        {"id": 2, "old": 5.0, "new": None},
    ]
    assert result["counts"]["repriced_count"] == 2


def test_diff_unchanged_price_is_not_repriced():
    old = _snap(_product(1, [_variant(1, "10.00")]))
    new = _snap(_product(1, [_variant(1, "10.00")]))
    assert snapshots.diff(old, new)["repriced"] == []


def test_diff_went_unavailable_and_back_in_stock():
    old = _snap(
        _product(1, [_variant(10, available=True), _variant(11, available=False)])
    )
    new = _snap(
        _product(1, [_variant(10, available=False), _variant(11, available=True)])
    )
    result = snapshots.diff(old, new)
    assert result["went_unavailable"] == [[1, 10]]
    assert result["back_in_stock"] == [[1, 11]]
    assert result["counts"]["went_unavailable_count"] == 1
    assert result["counts"]["back_in_stock_count"] == 1


def test_diff_new_variant_on_existing_product_is_not_a_flip():
    old = _snap(_product(1, [_variant(10, available=True)]))
    new = _snap(
        _product(1, [_variant(10, available=True), _variant(11, available=False)])
    )
    result = snapshots.diff(old, new)
    assert result["went_unavailable"] == []
    assert result["back_in_stock"] == []


def test_diff_note_is_always_present():
    result = snapshots.diff({}, {})
    assert result["note"] == "availability flips are a demand proxy, not units sold"


def test_diff_empty_inputs_are_all_zero():
    result = snapshots.diff({}, {})
    assert result["new_ids"] == []
    assert result["removed_ids"] == []
    assert result["warnings"] == []
    assert all(v == 0 for v in result["counts"].values())


def test_diff_does_not_mutate_inputs():
    old = _snap(_product(1, [_variant(10, available=True)]))
    new = _snap(_product(1, [_variant(10, available=False)]), _product(2))
    old_copy, new_copy = copy.deepcopy(old), copy.deepcopy(new)
    snapshots.diff(old, new, complete=False)
    assert old == old_copy
    assert new == new_copy


def test_diff_lists_are_sorted():
    old = _snap(_product(5), _product(1))
    new = _snap(_product(9), _product(3))
    result = snapshots.diff(old, new)
    assert result["new_ids"] == [3, 9]
    assert result["removed_ids"] == [1, 5]


# parse_retry_after ---------------------------------------------------------


def test_retry_after_integer_seconds():
    assert snapshots.parse_retry_after("120", NOW) == 120.0


def test_retry_after_strips_whitespace():
    assert snapshots.parse_retry_after("  30 \n", NOW) == 30.0


def test_retry_after_zero_is_valid():
    assert snapshots.parse_retry_after("0", NOW) == 0.0


def test_retry_after_missing_or_empty_is_none():
    assert snapshots.parse_retry_after(None, NOW) is None
    assert snapshots.parse_retry_after("", NOW) is None
    assert snapshots.parse_retry_after("   ", NOW) is None


def test_retry_after_garbage_is_none():
    assert snapshots.parse_retry_after("abc", NOW) is None
    assert snapshots.parse_retry_after("1.5", NOW) is None
    assert snapshots.parse_retry_after("12s", NOW) is None


def test_retry_after_negative_integer_is_none():
    assert snapshots.parse_retry_after("-5", NOW) is None


def test_retry_after_http_date_in_future_gives_positive_delta():
    when = datetime.fromtimestamp(NOW + 90, tz=UTC)
    value = format_datetime(when, usegmt=True)
    assert snapshots.parse_retry_after(value, NOW) == 90.0


def test_retry_after_http_date_in_past_is_zero_not_negative():
    when = datetime.fromtimestamp(NOW - 500, tz=UTC)
    value = format_datetime(when, usegmt=True)
    assert snapshots.parse_retry_after(value, NOW) == 0.0


def test_retry_after_naive_http_date_is_read_as_utc():
    # RFC 7231 date with no zone: parsed as naive, must be treated as UTC.
    value = "Tue, 14 Nov 2023 22:14:00"
    expected = datetime(2023, 11, 14, 22, 14, 0, tzinfo=UTC).timestamp() - NOW
    assert snapshots.parse_retry_after(value, NOW) == expected


def test_retry_after_invalid_date_is_none():
    assert snapshots.parse_retry_after("Not a date at all", NOW) is None


# next_delay ----------------------------------------------------------------


def test_next_delay_exponential_without_retry_after():
    assert [snapshots.next_delay(n, None) for n in range(4)] == [2.0, 4.0, 8.0, 16.0]


def test_next_delay_is_capped():
    assert snapshots.next_delay(10, None) == 120.0
    assert snapshots.next_delay(10, None, base=2.0, cap=30.0) == 30.0


def test_next_delay_negative_attempt_is_clamped_to_zero():
    assert snapshots.next_delay(-3, None) == 2.0


def test_next_delay_huge_attempt_does_not_overflow():
    assert snapshots.next_delay(10_000, None) == 120.0


def test_next_delay_retry_after_above_backoff_wins():
    assert snapshots.next_delay(0, 45.0) == 45.0


def test_next_delay_retry_after_below_backoff_keeps_backoff():
    assert snapshots.next_delay(4, 3.0) == 32.0


def test_next_delay_retry_after_above_cap_is_returned_unchanged():
    assert snapshots.next_delay(0, 600.0) == 600.0


def test_next_delay_negative_retry_after_counts_as_zero():
    assert snapshots.next_delay(1, -10.0) == 4.0


def test_next_delay_never_below_retry_after():
    for attempt in range(25):
        for retry_after in (0.0, 1.0, 7.5, 119.0, 120.0, 121.0, 400.0):
            assert snapshots.next_delay(attempt, retry_after) >= retry_after


def test_incomplete_earlier_snapshot_does_not_report_new_products():
    old = snapshots.compact([{"id": 1, "variants": []}])
    new = snapshots.compact([{"id": 1, "variants": []}, {"id": 2, "variants": []}])
    assert snapshots.diff(old, new)["new_ids"] == [2]
    out = snapshots.diff(old, new, old_complete=False)
    assert out["new_ids"] == []
    assert snapshots.INCOMPLETE_OLD_WARNING in out["warnings"]
