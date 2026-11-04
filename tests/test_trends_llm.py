"""Offline tests for the Trends maths and the LLM router. No network, no keys."""

from datetime import date, timedelta

import pytest

from scout import llm, trends

KEY_VARS = [v for p in llm.PROVIDERS.values() for v in p["keys"]]


def _weekly(values):
    start = date(2021, 11, 7)
    return [((start + timedelta(weeks=i)).isoformat(), v) for i, v in enumerate(values)]


def test_growth_compares_last_52_weeks_with_the_52_before(monkeypatch):
    series = _weekly([10] * 208 + [20] * 52)
    monkeypatch.setattr(trends, "_fetch", lambda *a, **k: series)
    r = trends.analyze("anything")
    assert r["status"] == "ok"
    assert r["growth_12m_vs_prior"] == pytest.approx(1.0)
    assert r["mean_interest_12m"] == pytest.approx(20.0)


def test_empty_series_reports_no_data(monkeypatch):
    monkeypatch.setattr(trends, "_fetch", lambda *a, **k: [])
    assert trends.analyze("anything")["status"] == "no_data"


@pytest.fixture
def no_keys(monkeypatch):
    for var in KEY_VARS:
        monkeypatch.delenv(var, raising=False)


def test_chat_without_any_key_fails_clearly(no_keys):
    with pytest.raises(llm.LLMError, match="no API key"):
        llm.chat("hi", task="bulk")


def test_only_providers_with_keys_are_tried(no_keys, monkeypatch):
    monkeypatch.setenv("ZAI_KEY", "x")
    tried = []

    def fake_post(payload, provider, key, timeout=0):
        tried.append((provider, payload["model"]))
        return {"model": payload["model"], "choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(llm, "_post", fake_post)
    out = llm.chat("hi", task="bulk")
    assert out["text"] == "ok"
    assert tried and all(p == "zai" for p, _ in tried)


def test_thinking_is_disabled_for_zai_non_reasoning_tasks(no_keys, monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "x")
    seen = {}

    def fake_post(payload, provider, key, timeout=0):
        seen.update(payload)
        return {"model": "m", "choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(llm, "_post", fake_post)
    llm.chat("hi", task="code")
    assert seen["thinking"] == {"type": "disabled"}


def test_data_urls_are_left_alone():
    msgs = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/png;base64,AAAA"},
                }
            ],
        }
    ]
    assert llm._inline_images(msgs) == msgs


def _reply(content):
    return {"model": "m", "choices": [{"message": {"content": content}}]}


@pytest.mark.parametrize(
    "bad", [_reply(""), _reply("   "), {"choices": []}, {"nope": 1}, _reply(None)]
)
def test_empty_or_malformed_replies_fall_through_to_the_next_model(
    no_keys, monkeypatch, bad
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    replies = [bad, _reply("good")]
    monkeypatch.setattr(llm, "_post", lambda *a, **k: replies.pop(0))
    assert llm.chat("hi", task="bulk")["text"] == "good"


def test_all_empty_replies_raise(no_keys, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    monkeypatch.setattr(llm, "_post", lambda *a, **k: _reply(""))
    with pytest.raises(llm.LLMError, match="empty or malformed"):
        llm.chat("hi", task="bulk")


def test_local_images_outside_allowed_roots_are_refused(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(llm.LLMError, match="working or temp"):
        llm._read_image("/etc/hostname")


def test_unsupported_url_schemes_are_refused():
    with pytest.raises(llm.LLMError, match="scheme"):
        llm._read_image("file:///etc/passwd")


def test_oversized_images_are_refused(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    big = tmp_path / "big.png"
    big.write_bytes(b"0" * (llm.MAX_IMAGE_BYTES + 10))
    with pytest.raises(llm.LLMError, match="larger"):
        llm._read_image(str(big))


def test_images_are_loaded_once_not_per_model(no_keys, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    img = tmp_path / "a.png"
    img.write_bytes(b"\x89PNG")
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    calls = []
    real = llm._inline_images

    def counting(msgs):
        calls.append(1)
        return real(msgs)

    monkeypatch.setattr(llm, "_inline_images", counting)
    replies = [_reply(""), _reply("ok")]
    monkeypatch.setattr(llm, "_post", lambda *a, **k: replies.pop(0))
    assert llm.chat("hi", task="vision", image_urls=[str(img)])["text"] == "ok"
    assert len(calls) == 1


def test_explicit_models_override_the_task_list(no_keys, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    seen = []

    def fake_post(payload, provider, key, timeout=0):
        seen.append(f"{provider}:{payload['model']}")
        return _reply("ok")

    monkeypatch.setattr(llm, "_post", fake_post)
    llm.chat("hi", task="bulk", models=["openrouter:some/model:free"])
    assert seen == ["openrouter:some/model:free"]
