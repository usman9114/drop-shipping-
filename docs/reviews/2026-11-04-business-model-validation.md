# Business-model rules: validation record (R1 exit criterion)

> 2026-11-04. Checks `scout.stores.business_model` against hand judgement. Store names stay in `data/private/validation/`; this file holds counts and error classes only. Script: `scripts/validate_business_model.py` (parallel GLM Flash as a second opinion, 8 workers).

## Rounds

| Round | Sample | Rule version | Result | What we learned |
|---|---|---|---|---|
| 1 | 12 stores, small first | v1: brand ≥ 60% own vendor; reseller 5+ vendors | 2 of 6 decided agree with the free model | Homepage app code alone marked an app developer as a dropshipper; portfolio owners and big retailers were called resellers; small own-label companies fell into "unclear" |
| 2 | 25 stores (seed 11) | v2: app needs a product trace; added `retailer` (30+ vendors); brand at ≥ 50% own or a dominant vendor | 17 of 25 agree with the free model | A failed refresh row (read timeout) replaced a good profile: pipeline bug, fixed with `latest_good` and a test |
| 3 | 25 stores (seed 23), hand-judged by the advisor | v2 | Rules right on **18 of 25 (72%)**, gate is 85% | 7 of the 9 "reseller" labels were big retailers, publishers or house-brand portfolios with 12 to 20 vendors; only 2 were true boutique resellers |

| 4 | 17 fresh stores (seed 5, `--fresh`), hand-judged | v3 (retailer at 10+ vendors) | Rules right on **14 of 17 (82%)**; 14 of 15 agree with the free model | All 3 errors are brands with a few sub-labels or one dominant vendor among many (rule said unclear or reseller) |

## Result and the change made

- The free second opinion is **noisy** (it invented "print on demand" from a tag and "own vendor" shares that were not in the evidence). Agreement with it is a hint, not the truth. Hand judgement decides.
- **Change:** `retailer` now starts at 10 vendors with none dominant; `reseller` is 5 to 9. This line was chosen from the 25-store sample, so it is a hypothesis.
- **v4 change after round 4:** a vendor holding half the catalogue, at any vendor count, means brand; five labels or fewer means brand; reseller is 6 to 9 vendors. Chosen from 17 stores, so again a hypothesis.
- **Gate still open.** The 85% bar is rechecked on at least 30 stores not used for tuning (`--fresh` skips every store already validated), after the full deep profile, before R1 is called final.

## Error classes (carry into the rules and the report)

1. House-brand portfolios and publishers look like resellers from vendor names alone. Treated as `retailer` (not copyable).
2. Marketplaces of third-party makers (print-on-demand style) look like resellers. Still wrong; needs a marketplace signal. Open.
3. Creator merchandise stores look like resellers when they carry a few partner vendors. Open.
4. App developers and page builders ship dropshipping-app code on their own sites. Fixed: needs supplier traces in the products too.

## Pipeline bugs found by testing small

- A refresh that timed out wrote an error-only row, and "latest row wins" replaced a good profile with it, so stores that failed once were also never retried. Fixed in Python and SQL; test `test_failed_refresh_never_replaces_a_good_profile`.
