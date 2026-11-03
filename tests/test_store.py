"""The evidence store must be append-only, traceable and tamper-evident."""

import gzip
import json

import pytest

from scout import store

ROWS = [
    {"keyword": "a", "week": "2026-01-04", "value": 5},
    {"keyword": "b", "week": "2026-01-04", "value": 7},
]


@pytest.fixture
def lake(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "LAKE", tmp_path / "lake")
    monkeypatch.setattr(store, "RUNS", tmp_path / "lake" / "_runs.jsonl")
    monkeypatch.setattr(store, "DB", tmp_path / "db" / "scout.db")
    return tmp_path


def test_record_then_rebuild_round_trips(lake):
    run_id = store.record_run("trend_points", ROWS, source="t", trust="data")
    assert store.rebuild() == {"trend_points": 2}
    rows = store.query("SELECT keyword, run_id FROM trend_points ORDER BY keyword")
    assert [r[0] for r in rows[1:]] == ["a", "b"]
    assert {r[1] for r in rows[1:]} == {run_id}
    assert store.query("SELECT verified FROM runs")[1][0] == 1


def test_unknown_trust_level_is_rejected(lake):
    with pytest.raises(ValueError, match="trust"):
        store.record_run("x", [{"a": 1}], source="s", trust="vibes")


def test_edited_lake_file_is_flagged(lake):
    store.record_run("trend_points", ROWS, source="t", trust="data")
    path = next((lake / "lake" / "trend_points").rglob("*.jsonl.gz"))
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"keyword": "EDITED", "run_id": "x"}) + "\n")
    store.rebuild()
    assert store.query("SELECT verified FROM runs")[1][0] == 0


def test_new_columns_in_a_later_run_are_added(lake):
    store.record_run("d", [{"a": 1}], source="t", trust="data")
    store.record_run("d", [{"a": 2, "b": "new"}], source="t", trust="data")
    assert store.rebuild() == {"d": 2}
    rows = store.query("SELECT a, b FROM d ORDER BY a")
    assert rows[1] == (1, None)
    assert rows[2] == (2, "new")


def test_runs_are_never_overwritten(lake):
    first = store.record_run("d", [{"a": 1}], source="t", trust="data")
    second = store.record_run("d", [{"a": 1}], source="t", trust="data")
    assert first != second
    assert len(store._runs()) == 2
