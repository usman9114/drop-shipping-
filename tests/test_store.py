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


def test_failed_checksum_rows_are_quarantined_not_loaded(lake):
    store.record_run("trend_points", ROWS, source="t", trust="data")
    path = next((lake / "lake" / "trend_points").rglob("*.jsonl.gz"))
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"keyword": "EDITED", "run_id": "x"}) + "\n")
    assert store.rebuild() == {}
    assert store.query("SELECT verified FROM runs")[1][0] == 0
    tables = store.query("SELECT name FROM sqlite_master WHERE name='trend_points'")
    assert len(tables) == 1  # header only: the table was never created


@pytest.mark.parametrize("name", ["../evil", "a b", "Drop;--", "", "x" * 80])
def test_bad_dataset_names_are_rejected(lake, name):
    with pytest.raises(ValueError, match="dataset"):
        store.record_run(name, [{"a": 1}], source="t", trust="data")


def test_bad_column_names_are_rejected(lake):
    with pytest.raises(ValueError, match="column"):
        store.record_run(
            "d", [{'a"; DROP TABLE runs; --': 1}], source="t", trust="data"
        )


def test_a_failed_rebuild_leaves_the_old_database_intact(lake):
    store.record_run("d", [{"a": 1}], source="t", trust="data")
    store.rebuild()
    with store.RUNS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"run_id": "bad", "dataset": "../x", "path": "x"}) + "\n")
    with pytest.raises(ValueError):
        store.rebuild()
    # query() would try (and fail) to rebuild from the corrupt log, so read the
    # surviving database directly.
    import sqlite3

    con = sqlite3.connect(store.DB)
    assert con.execute("SELECT COUNT(*) FROM d").fetchone()[0] == 1
    con.close()
    assert not store.DB.with_name(store.DB.name + ".tmp").exists()


def test_run_paths_outside_the_lake_are_refused(lake, tmp_path):
    outside = tmp_path / "elsewhere.jsonl.gz"
    with gzip.open(outside, "wt") as fh:
        fh.write("{}\n")
    meta = {"run_id": "r", "dataset": "d", "path": str(outside)}
    store.RUNS.parent.mkdir(parents=True, exist_ok=True)
    store.RUNS.write_text(json.dumps(meta) + "\n")
    with pytest.raises(ValueError, match="outside the lake"):
        store.rebuild()


def test_query_rebuilds_when_the_lake_has_new_runs(lake):
    import os
    import time

    store.record_run("d", [{"a": 1}], source="t", trust="data")
    assert store.query("SELECT COUNT(*) FROM d")[1][0] == 1
    time.sleep(0.02)
    store.record_run("d", [{"a": 2}], source="t", trust="data")
    os.utime(store.RUNS, None)
    assert store.query("SELECT COUNT(*) FROM d")[1][0] == 2


def test_record_run_leaves_no_partial_file_on_failure(lake, monkeypatch):
    import gzip as _gzip

    from scout import store as st

    real_open = _gzip.open

    def failing_open(path, *a, **k):
        fh = real_open(path, *a, **k)

        class Boom:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                fh.close()
                return False

            def write(self, _):
                raise OSError("disk full")

        return Boom()

    monkeypatch.setattr(st.gzip, "open", failing_open)
    import pytest

    with pytest.raises(OSError):
        st.record_run("t_atomic", [{"a": 1}], source="test", trust="mock")
    files = list((st.LAKE / "t_atomic").rglob("*.jsonl.gz"))
    assert files == []  # only a .tmp may remain, never a visible run file
