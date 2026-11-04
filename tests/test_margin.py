"""Unit economics are the decision engine, so they get plain, boring tests."""

import pytest

from scout import margin
from scout.margin import Inputs, compute, evaluate


def test_net_is_contribution_minus_reserves():
    r = compute(Inputs(price=30, cost=9, ship=5))
    assert r["net"] == pytest.approx(
        r["contribution"] - r["returns_reserve"] - r["disputes_reserve"], abs=0.02
    )


def test_per_order_fee_steps_when_the_taxed_total_passes_ten_dollars():
    # eBay's order fee depends on the order total, which includes sales tax (7%).
    below = compute(Inputs(price=9.34, cost=1, ship=1))["ebay_fees"]  # total 9.994
    above = compute(Inputs(price=9.35, cost=1, ship=1))["ebay_fees"]  # total 10.0045
    assert below == pytest.approx(0.136 * 9.34 * 1.07 + 0.30, abs=0.01)
    assert above == pytest.approx(0.136 * 9.35 * 1.07 + 0.40, abs=0.01)


def test_higher_cost_lowers_net():
    cheap = compute(Inputs(price=30, cost=6, ship=4))["net"]
    dear = compute(Inputs(price=30, cost=12, ship=4))["net"]
    assert dear < cheap


def test_stress_case_is_never_better_than_base():
    r = evaluate(Inputs(price=35, cost=8, ship=5))
    assert r["stress"]["net"] <= r["base"]["net"]


def test_duty_reduces_net_one_for_one():
    base = compute(Inputs(price=30, cost=9, ship=5, duty=0))["net"]
    duty = compute(Inputs(price=30, cost=9, ship=5, duty=3))["net"]
    assert base - duty == pytest.approx(3.0, abs=0.02)


@pytest.mark.parametrize(
    ("price", "cost", "ship", "base_margin", "stress_margin", "passes"),
    [
        # Regression values recorded on 2026-11-03 from the reviewed model.
        (29.99, 9.0, 5.0, 0.218, 0.028, False),
        (39.99, 8.0, 5.0, 0.368, 0.209, True),
    ],
)
def test_reviewed_cases(price, cost, ship, base_margin, stress_margin, passes):
    r = evaluate(Inputs(price=price, cost=cost, ship=ship))
    assert r["base"]["net_margin"] == pytest.approx(base_margin, abs=0.002)
    assert r["stress"]["net_margin"] == pytest.approx(stress_margin, abs=0.002)
    assert r["pass"] is passes


def test_thin_margin_item_fails_even_in_base_case():
    assert evaluate(Inputs(price=15, cost=7, ship=4))["pass"] is False


def test_hand_calculated_case():
    """Worked by hand, independent of the code path.

    total = 30 * 1.07 = 32.10 ; fees = 0.136 * 32.10 + 0.40 = 4.7656
    ads = 1.50 ; landed = 14 ; contribution = 30 - 14 - 4.7656 - 1.50 = 9.7344
    forfeited = 30 - 4.3656 = 25.6344
    returns = 0.08 * (25.6344 + 8) = 2.69075 ; disputes = 0.02 * 25.6344 = 0.51269
    net = 6.53096 ; margin = 0.2177
    """
    r = compute(Inputs(price=30, cost=9, ship=5))
    assert r["contribution"] == pytest.approx(9.7344, abs=0.006)
    assert r["net"] == pytest.approx(6.53096, abs=0.006)
    assert r["net_margin"] == pytest.approx(0.2177, abs=0.0006)


@pytest.mark.parametrize(
    "bad",
    [
        {"price": 0},
        {"price": -5},
        {"price": float("nan")},
        {"price": float("inf")},
        {"cost": -1},
        {"return_rate": 1.5},
        {"ad_rate": -0.1},
        {"return_rate": 0.7, "dispute_rate": 0.5},
    ],
)
def test_impossible_inputs_are_rejected(bad):
    args = {"price": 30, "cost": 9, "ship": 5, **bad}
    with pytest.raises(ValueError):
        compute(Inputs(**args))


def test_pass_decision_uses_unrounded_margins():
    from scout import margin

    i = Inputs(price=34.5, cost=8.1, ship=5.2)
    raw_base = margin._compute_raw(i)["net_margin"]
    raw_stress = margin._compute_raw(
        Inputs(price=34.5, cost=8.1, ship=5.2, duty=3.0, return_rate=0.16)
    )["net_margin"]
    expected = raw_base >= margin.PASS_NET and raw_stress >= margin.STRESS_NET
    assert evaluate(i)["pass"] is expected


@pytest.mark.parametrize(
    "cost,ship", [(3.0, 5.6), (5.0, 5.6), (8.5, 5.97), (0.5, 5.18), (15.0, 7.0)]
)
def test_min_price_is_the_lowest_passing_price(cost, ship):
    p = margin.min_price(cost, ship)
    assert margin.evaluate(margin.Inputs(price=p, cost=cost, ship=ship))["pass"]
    assert not margin.evaluate(margin.Inputs(price=p - 0.01, cost=cost, ship=ship))[
        "pass"
    ]


def test_min_price_matches_the_documented_ceilings():
    # supply check 2026-11-04: ~$3.50 cost passes at $25, ~$6 at $30, ~$8.50 at $35
    assert 24 <= margin.min_price(3.5, 5.6) <= 25.5
    assert 29 <= margin.min_price(6.0, 5.6) <= 30.5
    assert 34 <= margin.min_price(8.5, 5.6) <= 35.5


def test_min_price_none_when_rates_make_passing_impossible():
    assert margin.min_price(1.0, 1.0, ad_rate=0.7) is None
