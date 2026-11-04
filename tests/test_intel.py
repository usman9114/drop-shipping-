"""The intelligence layer must be reproducible and must not invent numbers."""

import pytest

from scout import intel

ROW = {
    "product_type": "pet grooming tool",
    "cj_products": 12,
    "viable_products": 7,
    "median_price_floor": 21.5,
    "best_price_floor": 18.29,
    "median_listed": 640,
    "popular_products": 5,
    "flagged_products": 0,
    "median_units_per_day": None,
    "total_units_per_day": None,
    "velocity_span_days": None,
    "why_tags": "problem_solver|video_demo|routine_care",
}


def test_pack_derives_flags():
    p = intel.pack(ROW)
    assert p["impulse_price"] is True  # 21.5 <= 25
    assert p["velocity_measured"] is False


def test_pack_hash_is_stable_and_sensitive():
    p = intel.pack(ROW)
    assert intel.pack_hash(p) == intel.pack_hash(intel.pack(dict(ROW)))
    assert intel.pack_hash(p) != intel.pack_hash(
        intel.pack({**ROW, "viable_products": 8})
    )


@pytest.mark.parametrize(
    ("text", "ok"),
    [
        ("7 of 12 pass; floor $21.5 and 640 stores list them.", True),
        ("Sells well because of video demos; eBay data not measured yet.", True),
        ("About 30% of buyers return it.", False),  # 30 is not in the pack
        ("It sells 1,200 units a month.", False),
    ],
)
def test_grounding_rejects_numbers_not_in_the_pack(text, ok):
    assert intel.grounded(text, intel.pack(ROW)) is ok


def test_template_is_deterministic_and_grounded():
    p = intel.pack(ROW)
    t = intel.template(p)
    assert t == intel.template(intel.pack(ROW))
    assert intel.grounded(t, p)
    assert "Not measured yet: stock velocity and marketplace demand." in t


def test_cache_hit_never_calls_the_model():
    p = intel.pack(ROW)
    cache = {intel.pack_hash(p): {"narrative": "cached text"}}

    def boom(*a, **k):
        raise AssertionError("model must not be called")

    assert intel.narrate(p, cache, boom)[:2] == ("cached text", "cache")


def test_ungrounded_model_text_falls_back_to_template():
    p = intel.pack(ROW)
    fake = lambda *a, **k: {"model": "m", "text": "It has a 42% repeat rate."}  # noqa: E731
    text, method, row = intel.narrate(p, {}, fake)
    assert method == "template (model text rejected)"
    assert text == intel.template(p)
    assert row is None


def test_grounded_model_text_is_used_and_cached():
    p = intel.pack(ROW)
    fake = lambda *a, **k: {"model": "zai:m", "text": "7 of 12 pass at a $21.5 floor."}  # noqa: E731
    text, method, row = intel.narrate(p, {}, fake)
    assert method == "llm" and row["pack_sha256"] == intel.pack_hash(p)


def test_model_failure_falls_back_to_template():
    def fail(*a, **k):
        raise RuntimeError("provider down")

    text, method, _ = intel.narrate(intel.pack(ROW), {}, fail)
    assert method == "template"


def test_cache_round_trip(tmp_path):
    path = tmp_path / "cache.csv"
    row = {
        "pack_sha256": "abc",
        "product_type": "x",
        "narrative": 'has, commas and "quotes"',
        "model": "m",
        "prompt_version": intel.PROMPT_VERSION,
    }
    intel.append_cache([row], path)
    assert intel.load_cache(path)["abc"]["narrative"] == 'has, commas and "quotes"'


def test_render_lists_every_type_and_method():
    p = intel.pack(ROW)
    md = intel.render([(p, "text here", "template")], "2026-11-04")
    assert "| pet grooming tool | 7 / 12 |" in md
    assert "*Narrative: template.*" in md
