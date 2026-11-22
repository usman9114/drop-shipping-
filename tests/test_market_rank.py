from scout import market_rank, stores


def test_pk_store_is_rupee_storefront():
    assert stores.pk_store({"currency": "PKR", "country": "GB"})
    assert not stores.pk_store({"currency": "USD", "country": "PK"})
    assert stores.in_market({"currency": "USD", "country": "US"}, "us")
    assert not stores.in_market({"currency": "PKR", "country": "PK"}, "us")
    assert stores.in_market({"currency": "EUR"}, None)


def test_weights_sum_to_one():
    assert abs(sum(market_rank.WEIGHTS.values()) - 1) < 1e-9


def test_percentile_matches_percent_rank():
    assert market_rank.percentile([10, 20, 20, 30]) == [0, 1 / 3, 1 / 3, 1]
    assert market_rank.percentile([5]) == [0.0]


def test_growth_log():
    assert market_rank.growth_log(1000, 2000) == round(__import__("math").log(2), 3)
    assert market_rank.growth_log(1000, None) is None


def test_score_orders_busier_and_growing_first():
    rows = [
        {"domain": "flat", "tranco_rank": 5000, "rank_growth_log": 0, "added_90d": 5},
        {"domain": "top", "tranco_rank": 1000, "rank_growth_log": 1, "added_90d": 50},
        {
            "domain": "slow",
            "tranco_rank": 9000,
            "rank_growth_log": None,
            "added_90d": None,
        },
    ]
    ranked = market_rank.score(rows)
    assert [r["domain"] for r in ranked] == ["top", "flat", "slow"]
    assert ranked[0]["best_score"] == 1.0


def test_throttled_store_is_not_given_up():
    rows = [{"domain": "a.pk", "error": "HTTP429"}] * 5 + [
        {"domain": "b.pk", "error": "Timeout"}
    ] * 3
    assert stores.gave_up(rows) == {"b.pk"}
