"""scout.chatgpt: argument guards and output handling, codex mocked (no network)."""

import json
import subprocess
from pathlib import Path

import pytest

from scout import chatgpt


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(chatgpt, "USAGE", tmp_path / "usage.jsonl")
    monkeypatch.setattr(chatgpt, "LOG_DIR", tmp_path / "log")
    monkeypatch.setattr(chatgpt, "_codex", lambda: "codex")


def _fake_run(write_png: bool, message: str = "done"):
    def run(cmd, **kw):
        cwd = Path(cmd[cmd.index("-C") + 1])
        Path(cmd[cmd.index("-o") + 1]).write_text(message)
        if write_png:
            (cwd / "result.png").write_bytes(b"\x89PNG fake")
        return subprocess.CompletedProcess(cmd, 0, "model: test-model\n", "")

    return run


def test_ref_requires_source_url(tmp_path):
    with pytest.raises(chatgpt.ChatGPTError, match="source-url"):
        chatgpt.image("x", str(tmp_path / "o.png"), refs=["a.png"], source_urls=[])


def test_image_writes_png_and_sidecar(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", _fake_run(True))
    res = chatgpt.image("a desk", str(tmp_path / "o.png"))
    assert Path(res["out"]).read_bytes().startswith(b"\x89PNG")
    meta = json.loads(Path(res["meta"]).read_text())
    assert meta["prompt"] == "a desk" and meta["driver_model"] == "test-model"
    assert chatgpt._count_today("image") == 1


def test_image_without_png_fails_and_is_logged(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", _fake_run(False, "cannot"))
    with pytest.raises(chatgpt.ChatGPTError, match="no image"):
        chatgpt.image("a desk", str(tmp_path / "o.png"))
    assert chatgpt._count_today("image") == 0


def test_daily_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(chatgpt, "DAILY_IMAGE_CAP", 0)
    with pytest.raises(chatgpt.ChatGPTError, match="cap"):
        chatgpt.image("a desk", str(tmp_path / "o.png"))


def test_research_extracts_urls(monkeypatch):
    monkeypatch.setattr(
        subprocess, "run", _fake_run(False, "- fact [s](https://ebay.com/help)")
    )
    res = chatgpt.research("q?")
    assert res["urls"] == ["https://ebay.com/help"]
    assert Path(res["saved"]).exists()


def test_ask_schema_parses_json(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", _fake_run(False, '{"has_text": false}'))
    schema = tmp_path / "s.json"
    schema.write_text("{}")
    assert chatgpt.ask("x", schema=str(schema))["data"] == {"has_text": False}


def test_ask_schema_rejects_non_json(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", _fake_run(False, "sorry"))
    schema = tmp_path / "s.json"
    schema.write_text("{}")
    with pytest.raises(chatgpt.ChatGPTError, match="not JSON"):
        chatgpt.ask("x", schema=str(schema))
