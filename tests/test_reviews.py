"""Review-count parsing (no network)."""

from scout import reviews


def test_counts_from_each_pattern_and_preference():
    html = (
        '<div class="jdgm-prev-badge" data-number-of-reviews="42"></div>'
        '<script type="application/ld+json">{"aggregateRating":{"reviewCount":"1,994"}}</script>'
        "<span>10,990 Reviews</span>"
    )
    found = reviews.review_counts(html)
    assert found["judgeme_badge"] == 42
    assert found["visible_text"] == 10990
    assert reviews.best_count({"visible_text": 5, "judgeme_badge": 7}) == 7
    assert reviews.best_count({"jsonld_reviewcount": 3, "visible_text": 9}) == 3
    assert reviews.best_count({}) is None


def test_implausible_and_zero_counts_are_ignored():
    assert reviews.review_counts("0 reviews") == {}
    assert reviews.review_counts("99999999 reviews") == {}


def test_block_pages_are_recognised_and_never_parsed_as_counts():
    assert reviews.is_blocked(403, "")
    assert reviews.is_blocked(200, "<div id='cf-challenge'>Verify you are human</div>")
    assert not reviews.is_blocked(200, "<html>normal product page</html>")


def test_review_app_detection():
    assert reviews.review_app('<script src="https://cdn.judge.me/x.js">') == "judge.me"
    assert reviews.review_app("<div>no app</div>") is None
