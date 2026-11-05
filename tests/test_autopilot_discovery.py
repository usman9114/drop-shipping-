"""Incremental discovery and the new-store queues feeding the autopilot."""

import pytest

from scout import fingerprints, store, stores, webmeta


@pytest.fixture
def lake(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "LAKE", tmp_path / "lake")
    monkeypatch.setattr(store, "RUNS", tmp_path / "lake" / "_runs.jsonl")
    return tmp_path


class FakeList:
    def __init__(self, list_id, domains, date="2026-11-05"):
        self.list_id, self._d, self.date = list_id, domains, date

    def top(self, n):
        return self._d[:n]


def _lists(cur, by_id=None, by_date=None):
    def lists(date=None, list_id=None):
        if list_id:
            return by_id[list_id]
        if date:
            return by_date[date]
        return cur

    return lists


def _resolver(shopify):
    def resolve(d):
        return (["23.227.38.65"] if d in shopify else ["1.2.3.4"]), ""

    return resolve


def test_new_entries_are_the_diff_best_rank_first():
    assert webmeta.new_entries(["a", "b", "c", "d"], ["b", "d"], {"c"}) == [(1, "a")]


def test_scan_new_first_run_diffs_against_the_day_before(lake):
    cur = FakeList("L2", ["old", "new-shop", "new-other"])
    prev = FakeList("L1", ["old"])
    out = webmeta.scan_new(
        lists=_lists(cur, by_date={"2026-11-04": prev}),
        resolver=_resolver({"new-shop"}),
        qps=0,
        workers=2,
    )
    ((run_id, n),) = out.values()
    assert n == 1
    run = store._runs()[-1]
    assert run["params"]["mode"] == "new"
    assert run["params"]["prev_list_id"] == "L1"
    assert run["params"]["new_entries"] == 2 and run["params"]["shopify"] == 1
    rows = stores._all_rows("web_scan")
    assert rows[0]["domain"] == "new-shop" and rows[0]["tranco_rank"] == 2
    assert stores.new_hits() == {"new-shop"}
    assert webmeta.tranches_done() == set()  # not a full-scan tranche


def test_scan_new_is_a_no_op_on_the_same_list_and_diffs_from_the_last_run(lake):
    l1 = FakeList("L1", ["a"])
    l2 = FakeList("L2", ["a", "b"])
    l3 = FakeList("L3", ["a", "b", "c"])
    res = _resolver({"b", "c"})
    webmeta.scan_new(lists=_lists(l2, by_date={"2026-11-04": l1}), resolver=res, qps=0)
    assert webmeta.scan_new(lists=_lists(l2), resolver=res, qps=0) == {}
    webmeta.scan_new(lists=_lists(l3, by_id={"L2": l2}), resolver=res, qps=0)
    assert store._runs()[-1]["params"]["prev_list_id"] == "L2"
    assert stores.new_hits() == {"b", "c"}


def test_scan_new_cap_is_recorded(lake):
    cur = FakeList("L2", ["x1", "x2", "x3"])
    webmeta.scan_new(
        max_lookups=2,
        lists=_lists(cur, by_date={"2026-11-04": FakeList("L1", [])}),
        resolver=_resolver(set()),
        qps=0,
    )
    p = store._runs()[-1]["params"]
    assert p["looked_up"] == 2 and p["truncated"] == 1


def test_new_stores_go_first_in_meta_and_fingerprint_queues(lake):
    store.record_run(
        "web_scan",
        [{"domain": "old", "tranco_rank": 1, "a": ""}],
        source="t",
        trust="data",
        params={"start": 0, "end": 1},
    )
    store.record_run(
        "web_scan",
        [{"domain": "fresh", "tranco_rank": 9, "a": ""}],
        source="t",
        trust="data",
        params={"mode": "new", "list_id": "L"},
    )
    hits = stores._shop_hits()
    assert [h["domain"] for h in stores._new_first(hits, stores.new_hits())] == [
        "fresh",
        "old",
    ]
    store.record_run(
        "web_meta",
        [
            {"domain": "old", "tranco_rank": 1, "shop_id": 1},
            {"domain": "fresh", "tranco_rank": 9, "shop_id": 2},
        ],
        source="t",
        trust="data",
    )
    assert fingerprints.queue(10) == ["fresh"]
    store.record_run(
        "web_fingerprints",
        [{"domain": "fresh", "rule_version": fingerprints.RULE_VERSION}],
        source="t",
        trust="data",
    )
    assert fingerprints.queue(10) == []
    store.record_run(
        "web_fingerprints",
        [{"domain": "fresh", "rule_version": "old"}],
        source="t",
        trust="data",
    )
    assert fingerprints.queue(10) == []  # scored at the current version already
