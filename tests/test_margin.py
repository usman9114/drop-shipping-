"""Unit economics are the decision engine, so they get plain, boring tests."""

import pytest

from scout.margin import Inputs, compute, evaluate


def test_net_is_contribution_minus_reserves():
    r = compute(Inputs(price=30, cost=9, ship=5))
    assert r["net"] == pytest.approx(
        r["contribution"] - r["returns_reserve"] - r["disputes_reserve"], abs=0.02
    )


def test_per_order_fee_steps_at_ten_dollars():
    at_ten = compute(Inputs(price=10.00, cost=1, ship=1))["ebay_fees"]
    above = compute(Inputs(price=10.01, cost=1, ship=1))["ebay_fees"]
    assert at_ten == pytest.approx(0.136 * 10.00 * 1.07 + 0.30, abs=0.01)
    assert above == pytest.approx(0.136 * 10.01 * 1.07 + 0.40, abs=0.01)


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
