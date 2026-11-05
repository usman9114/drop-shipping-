"""Batch runner, second opinion and usage report of scout.llm (no network)."""

import json

from scout import llm


def _write(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def _read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def test_batch_writes_one_result_per_id(tmp_path, monkeypatch):
    inp, out = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write(inp, [{"id": "a", "prompt": "p1"}, {"id": "b", "prompt": "p2"}])
    monkeypatch.setattr(
        llm,
        "chat_many",
        lambda ps, **k: [{"model": "m", "text": p.upper()} for p in ps],
    )
    c = llm.run_batch(str(inp), str(out))
    assert c == {"total": 2, "skipped": 0, "ok": 2, "error": 0}
    assert {r["id"]: r["text"] for r in _read(out)} == {"a": "P1", "b": "P2"}


def test_batch_resumes_and_retries_errors(tmp_path, monkeypatch):
    inp, out = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write(inp, [{"id": i, "prompt": f"p{i}"} for i in range(3)])
    _write(out, [{"id": 0, "text": "done"}, {"id": 1, "error": "429"}])
    seen = []

    def fake(ps, **k):
        seen.extend(ps)
        return [{"model": "m", "text": "ok"} for _ in ps]

    monkeypatch.setattr(llm, "chat_many", fake)
    c = llm.run_batch(str(inp), str(out))
    assert seen == ["p1", "p2"]  # id 0 skipped, id 1 retried
    assert c["skipped"] == 1 and c["ok"] == 2


def test_batch_rejects_duplicate_ids(tmp_path):
    inp = tmp_path / "in.jsonl"
    _write(inp, [{"id": 1, "prompt": "a"}, {"id": 1, "prompt": "b"}])
    try:
        llm.run_batch(str(inp), str(tmp_path / "o.jsonl"))
    except ValueError:
        return
    raise AssertionError("duplicate ids accepted")


def test_batch_records_errors_without_stopping(tmp_path, monkeypatch):
    inp, out = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write(inp, [{"id": "x", "prompt": "a"}, {"id": "y", "prompt": "b"}])
    monkeypatch.setattr(
        llm, "chat_many", lambda ps, **k: [{"error": "boom"}, {"text": "fine"}]
    )
    c = llm.run_batch(str(inp), str(out))
    assert c["error"] == 1 and c["ok"] == 1


def test_second_opinion_agreement(monkeypatch):
    replies = iter([{"text": "Dropship\nbecause..."}, {"text": "dropship."}])
    monkeypatch.setattr(llm, "chat", lambda *a, **k: next(replies))
    o = llm.second_opinion("label?")
    assert o["agree"] is True


def test_second_opinion_disagreement_and_failure(monkeypatch):
    replies = iter([{"text": "brand"}, {"text": "dropship"}])
    monkeypatch.setattr(llm, "chat", lambda *a, **k: next(replies))
    assert llm.second_opinion("label?")["agree"] is False

    def boom(*a, **k):
        raise llm.LLMError("down")

    monkeypatch.setattr(llm, "chat", boom)
    assert llm.second_opinion("label?")["agree"] is None


def test_usage_reports_cap(monkeypatch):
    monkeypatch.setattr(llm, "or_free_used", lambda: 100)
    u = llm.usage()
    assert u["or_free_left"] == u["or_free_cap"] - 100
