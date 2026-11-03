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


def compute(i: Inputs) -> dict:
    per_order = (
        i.per_order_fee
        if i.per_order_fee is not None
        else (0.30 if i.price <= 10 else 0.40)
    )
    fvf = i.fvf_rate * i.price * (1 + i.sales_tax_rate) + per_order
    ads = i.ad_rate * i.price
    landed = i.cost + i.ship + i.duty
    contribution = i.price - landed - fvf - ads
    forfeited = i.price - (fvf - per_order)  # revenue lost net of FVF credit
    returns = i.return_rate * (forfeited + i.return_label)
    disputes = i.dispute_rate * forfeited
    net = contribution - returns - disputes
    return {
        "landed_cost": round(landed, 2),
        "ebay_fees": round(fvf, 2),
        "ads": round(ads, 2),
        "contribution": round(contribution, 2),
        "returns_reserve": round(returns, 2),
        "disputes_reserve": round(disputes, 2),
        "net": round(net, 2),
        "net_margin": round(net / i.price, 3) if i.price else None,
    }


def evaluate(i: Inputs) -> dict:
    base = compute(i)
    stress_in = Inputs(
        **{**asdict(i), "duty": i.duty + 3.0, "return_rate": i.return_rate * 2}
    )
    stress = compute(stress_in)
    passed = (base["net_margin"] or 0) >= PASS_NET and (
        stress["net_margin"] or 0
    ) >= STRESS_NET
    return {"inputs": asdict(i), "base": base, "stress": stress, "pass": passed}


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
