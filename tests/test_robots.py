from scout.robots import RobotRules

UA = "dropship-poc-research/0.1 (+https://example.com)"

SHOPIFY = """
User-agent: *
Allow: /collections/account
Disallow: /collections/*sort_by*
Disallow: /*/collections/*sort_by*
Disallow: /collections/*+*
Disallow: /admin
Disallow: /cart
"""


def rules(text: str) -> RobotRules:
    r = RobotRules()
    r.parse(text.splitlines())
    return r


def test_shopify_default_blocks_sorted_collections():
    # urllib.robotparser says True for both (wildcards read as literal text)
    r = rules(SHOPIFY)
    assert not r.can_fetch(UA, "https://a.com/collections/all?sort_by=best-selling")
    assert not r.can_fetch(
        UA, "https://a.com/collections/all/products.json?sort_by=best-selling"
    )
    assert not r.can_fetch(UA, "https://a.com/en/collections/all?sort_by=best-selling")
    assert not r.can_fetch(UA, "https://a.com/collections/a+b")


def test_shopify_default_allows_what_we_fetch():
    r = rules(SHOPIFY)
    for path in (
        "/",
        "/products.json?limit=250&page=2",
        "/meta.json",
        "/collections/best-sellers/products.json?limit=50",
    ):
        assert r.can_fetch(UA, "https://a.com" + path), path
    assert not r.can_fetch(UA, "https://a.com/cart")


def test_longest_rule_wins_and_allow_wins_ties():
    r = rules("User-agent: *\nDisallow: /a\nAllow: /a/b\nDisallow: /c\nAllow: /c")
    assert not r.can_fetch(UA, "https://x.com/a/x")
    assert r.can_fetch(UA, "https://x.com/a/b/x")
    assert r.can_fetch(UA, "https://x.com/c")


def test_dollar_anchor_and_empty_disallow():
    r = rules("User-agent: *\nDisallow: /*.json$\n")
    assert not r.can_fetch(UA, "https://x.com/products.json")
    assert r.can_fetch(UA, "https://x.com/products.json?limit=1")
    assert rules("User-agent: *\nDisallow:\n").can_fetch(UA, "https://x.com/anything")


def test_named_group_beats_star_group():
    text = "User-agent: *\nDisallow: /\n\nUser-agent: dropship-poc-research\nAllow: /\n"
    assert rules(text).can_fetch(UA, "https://x.com/products.json")
    assert not rules(text).can_fetch("otherbot/1", "https://x.com/products.json")


def test_no_robots_means_allowed():
    assert rules("").can_fetch(UA, "https://x.com/anything")
