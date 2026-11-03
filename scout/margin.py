"""Per-product unit economics for eBay US (see docs/research/02-unit-economics.md).

Usage:
    python -m scout.margin --price 34.99 --cost 9.80 --ship 5.20
    python -m scout.margin --price 34.99 --cost 9.80 --ship 5.20 --json

eBay's final value fee includes payment processing, so there is no separate
processor fee. FVF applies to item + shipping + sales tax.

Refund model (returns and INR/INAD disputes): the sale is forfeited, eBay
credits the variable FVF but keeps the per-order fee, the ad fee is not
refunded (conservative), and the goods are lost (zero inventory: we cannot
restock a return). Relative to a completed sale, each refunded order therefore
costs (price - variable FVF), plus a return label for returns.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass

PASS_NET = 0.20  # base-case net margin required to pass
STRESS_NET = 0.10  # stress-case net margin required to pass


@dataclass
class Inputs:
    price: float  # buyer-paid item price (free shipping listing)
    cost: float  # CJ product cost
    ship: float  # CJ shipping cost to buyer (US warehouse)
    duty: float = 0.0  # import duty per unit, 0 for US-warehouse stock
    fvf_rate: float = 0.136  # eBay final value fee, most categories
    per_order_fee: float | None = None  # default: 0.30 if <=$10 else 0.40
    sales_tax_rate: float = 0.07  # avg US combined rate; FVF is charged on it
    ad_rate: float = 0.05  # Promoted Listings Standard
    return_rate: float = 0.08  # share of orders returned
    return_label: float = 8.0  # prepaid return label we cover
    dispute_rate: float = 0.02  # INR/INAD refunded without return


_RATES = ("fvf_rate", "ad_rate", "return_rate", "dispute_rate")
_AMOUNTS = ("cost", "ship", "duty", "sales_tax_rate", "return_label")


def _check(i: Inputs) -> None:
    """Reject inputs that would silently produce nonsense."""

    def finite(name, value):
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be a finite number >= 0, got {value!r}")

    finite("price", i.price)
    if i.price <= 0:
        raise ValueError("price must be > 0")
    for name in _AMOUNTS + _RATES:
        finite(name, getattr(i, name))
    for name in _RATES:
        if getattr(i, name) > 1:
            raise ValueError(f"{name} is a rate and must be <= 1")
    if i.per_order_fee is not None:
        finite("per_order_fee", i.per_order_fee)
    if i.return_rate + i.dispute_rate > 1:
        raise ValueError("return_rate + dispute_rate must be <= 1")


def _compute_raw(i: Inputs) -> dict:
    """Unrounded economics. Pass/fail decisions use these, never rounded values."""
    _check(i)
    total = i.price * (1 + i.sales_tax_rate)  # what the buyer pays; fees apply to it
    per_order = (
        i.per_order_fee
        if i.per_order_fee is not None
        else (0.30 if total <= 10 else 0.40)
    )
    fvf = i.fvf_rate * total + per_order
    ads = i.ad_rate * i.price
    landed = i.cost + i.ship + i.duty
    contribution = i.price - landed - fvf - ads
    forfeited = i.price - (fvf - per_order)  # revenue lost net of the FVF credit
    returns = i.return_rate * (forfeited + i.return_label)
    disputes = i.dispute_rate * forfeited
    net = contribution - returns - disputes
    return {
        "landed_cost": landed,
        "ebay_fees": fvf,
        "ads": ads,
        "contribution": contribution,
        "returns_reserve": returns,
        "disputes_reserve": disputes,
        "net": net,
        "net_margin": net / i.price,
    }


def _rounded(raw: dict) -> dict:
    return {k: round(v, 3 if k == "net_margin" else 2) for k, v in raw.items()}


def compute(i: Inputs) -> dict:
    return _rounded(_compute_raw(i))


def evaluate(i: Inputs) -> dict:
    base = _compute_raw(i)
    stress_in = Inputs(
        **{
            **asdict(i),
            "duty": i.duty + 3.0,
            "return_rate": min(i.return_rate * 2, 1 - i.dispute_rate),
        }
    )
    stress = _compute_raw(stress_in)
    passed = base["net_margin"] >= PASS_NET and stress["net_margin"] >= STRESS_NET
    return {
        "inputs": asdict(i),
        "base": _rounded(base),
        "stress": _rounded(stress),
        "pass": passed,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--price", type=float, required=True)
    ap.add_argument("--cost", type=float, required=True)
    ap.add_argument("--ship", type=float, required=True)
    ap.add_argument("--duty", type=float, default=0.0)
    ap.add_argument("--ad-rate", type=float, default=0.05)
    ap.add_argument("--return-rate", type=float, default=0.08)
    ap.add_argument("--fvf-rate", type=float, default=0.136)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = evaluate(
        Inputs(
            price=a.price,
            cost=a.cost,
            ship=a.ship,
            duty=a.duty,
            ad_rate=a.ad_rate,
            return_rate=a.return_rate,
            fvf_rate=a.fvf_rate,
        )
    )
    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    print(f"{'':18}{'base':>10}{'stress':>10}")
    for k in res["base"]:
        print(f"{k:18}{res['base'][k]!s:>10}{res['stress'][k]!s:>10}")
    print(f"PASS (>= {PASS_NET:.0%} base, >= {STRESS_NET:.0%} stress): {res['pass']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
