"""The review panel must parse strictly, cache by content and tally honestly."""

import pytest

from scout import review_panel as rp

GOOD = """Sure! {"verdict": "Modify", "relevance": 4, "evidence": "2",
"value_for_effort": 3, "compliance_safety": 5, "constraints": ["C3", "F4", "bogus"],
"reason": "  useful   but untested ", "risk": "noise", "cheapest_test": "run it"}"""


def test_parse_review_validates_and_normalises():
    r = rp.parse_review(GOOD)
    assert r["verdict"] == "modify"
    assert (r["relevance"], r["evidence"]) == (4, 2)
    assert r["constraints"] == ["C3", "F4"]
    assert r["reason"] == "useful but untested"


@pytest.mark.parametrize(
    "bad",
    [
        "no json here",
        '{"verdict": "maybe", "relevance": 3, "evidence": 3, "value_for_effort": 3, "compliance_safety": 3}',
        '{"verdict": "keep", "relevance": 9, "evidence": 3, "value_for_effort": 3, "compliance_safety": 3}',
        '{"verdict": "keep", "relevance": "x", "evidence": 3, "value_for_effort": 3, "compliance_safety": 3}',
    ],
)
def test_parse_review_rejects_bad_answers(bad):
    assert rp.parse_review(bad) is None


def test_cache_key_changes_with_idea_model_or_brief():
    idea = {"id": "I01", "title": "t", "description": "d"}
    k = rp.cache_key("brief", idea, "m1")
    assert k == rp.cache_key("brief", dict(idea), "m1")
    assert k != rp.cache_key("brief", {**idea, "description": "d2"}, "m1")
    assert k != rp.cache_key("brief", idea, "m2")
    assert k != rp.cache_key("brief 2", idea, "m1")


def _r(verdict):
    return {"verdict": verdict, **{s: 3 for s in rp.SCORES}}


def test_tally_majority_and_split():
    t = rp.tally([_r("keep"), _r("keep"), _r("drop")])
    assert t["consensus"] == "keep" and not t["split"]
    t = rp.tally([_r("keep"), _r("drop"), _r("modify"), _r("keep")])
    assert t["consensus"] is None and t["split"]
    assert rp.tally([])["n"] == 0


def test_review_uses_cache_and_survives_a_failing_model(tmp_path, monkeypatch):
    monkeypatch.setattr(rp, "CACHE", tmp_path / "cache.jsonl")
    idea = {"id": "I01", "title": "t", "description": "d"}
    calls = []

    def chat(prompt, system=None, models=None, max_tokens=0):
        calls.append(models[0])
        if models[0] == "bad":
            raise RuntimeError("down")
        return {"model": models[0], "text": GOOD}

    out = rp.review([idea], "brief", ["good", "bad"], chat)
    assert len(out["I01"]) == 1
    calls.clear()
    out = rp.review([idea], "brief", ["good", "bad"], chat)
    assert calls == ["bad"]  # the good answer came from the cache
    assert len(out["I01"]) == 1


def test_ideas_file_loads():
    brief, ideas = rp.load_ideas()
    assert "GOAL" in brief and len(ideas) >= 10
    assert len({i["id"] for i in ideas}) == len(ideas)
