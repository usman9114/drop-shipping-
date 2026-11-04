# 28. Discovery miss rate: Shopify stores hidden behind a CDN or proxy

> 2026-11-04. Phase 1 of `docs/plan/top-stores-inspiration-plan.md`. Aggregates only, no domain names. Raw rows are in the private lake (dataset `web_shopify_probe`, runs `20261104T2325..` and `20261104T233053Z-36eccb`).

## Question

Discovery marks a domain as Shopify only if its apex A record is in 23.227.38.0/24 (`scout.webmeta.scan`, hits via `scout.stores._shop_hits()`). How many Shopify stores in the Tranco top 200k does that miss?

## Method

- Pool: Tranco ranks 1 to 200,000 minus every domain in `_shop_hits()` = 197,339 domains (2,661 domains in that range are already hits `[data]`).
- Sample: reproducible random draw, seed 42, 550 distinct domains (a pilot of 50, then 500 more from the same draw). Ranks are spread evenly across the range.
- Probe (`scout/shopify_detect.py`): robots.txt first with the project UA; homepage GET only if allowed; one request, no retry; 20 s timeout; first 50 KB read; 8 workers, 1 s pause per worker. 403/429/430 or a captcha page is recorded as `blocked` and never retried.
- Rule: one strong header (`x-shopid`, `x-sorting-hat-shopid`, `x-shopify-stage`, `powered-by: Shopify`) or two weak markers (`server-timing` mentioning shopify, or HTML `cdn.shopify.com`, `Shopify.shop =`, `shopify-features`, `/cdn/shop/`).
- Positive control: 5 known DNS hits probed. 3 showed the full signal set, 1 showed `powered-by` only (still detected), 1 was blocked (403). So the detector fires on real stores `[data]`, n = 5 is small.

## Results `[data]`

| Outcome | Domains | Share of 550 |
|---|---|---|
| Homepage answered (2xx/3xx) | 320 | 58% |
| HTTP error status (4xx/5xx other than block) | 18 | 3% |
| Blocked (403/429/430/captcha), not retried | 12 | 2% |
| Skipped, robots.txt disallows | 60 | 11% |
| Network error (proxy 71, connection 46, SSL 20, timeout 3) | 140 | 25% |
| **Shopify found by headers** | **0** | |
| **Shopify found by HTML markers only** | **0** | |
| Any Shopify signal at all | 0 | |

Signals that fired: none. No `x-shopid`, `powered-by`, `server-timing` or HTML marker appeared in any of the 338 homepages that returned a status.

## Implied miss rate

- Point estimate: 0 hidden Shopify stores per 1,000 non-hit domains `[proxy]` (denominator: the 338 domains that returned a page; blocked, robots-disallowed and errored domains are unknown).
- 95% upper bound (Wilson, 0 of 338): 1.1% = 11 per 1,000. Rule of three gives 0.9%.
- Estimated hidden stores in the top 200k: 0, with a 95% interval of 0 to about 2,200 (1.1% of 197,339). The interval is wide because the sample is small.
- Against the plan's test: hidden stores would exceed 15% of the 2,661 found if the true rate is above 0.20% of non-hit domains (about 400 stores). Our upper bound of 1.1% does not exclude that. The point estimate of 0 says it is unlikely, but this sample cannot prove it.

## Caveats `[unverified]`

- 25% of probes failed at network level. Many `ProxyError` rows are the sandbox's outbound proxy refusing hosts, not the sites. Hidden stores could sit disproportionately in that group. The estimate is for reachable sites only.
- 11% of domains disallow us in robots.txt and 2% block us. We respect both, so those stay unknown.
- The pool is all non-hit domains, mostly not stores at all (portals, media, tools). The plan suggested sampling domains that "look like stores". The miss rate among store-like domains could be higher than 0 to 1.1%; this pilot did not filter.
- The detection rule has one hand check (5 positives, no hand-checked negatives). Standing rule 5 (validate before relying) is not yet met.
- A Shopify store on a headless or fully custom front end (Hydrogen, proxied checkout only) may show none of these signals.
- Rank 200k is the cutoff; behaviour above it is untested.

## Recommendation

Do not add header detection to discovery yet. The evidence does not show a miss problem (0 of 338), and a 15% miss would be 0.2% of the pool, which needs about 1,500 responding domains to exclude at 95%. Proportionate next step, in order:

1. Re-run the probe from a network without the sandbox proxy (owner's machine or CI) on a store-like subset (name contains a product word, or `/products.json` present) to cut the 25% error share, about 1,500 domains, about 1 hour at 8 workers.
2. Only if hidden stores exceed 15% of found in that range (0.2% of the pool), wire `shopify_evidence` into `scout.webmeta.scan` as a second pass over non-hits in the top 200k.
3. Add a hand-checked negative sample (30 domains) to validate the rule.

Until then the DNS-based discovery stands as a candidate generator; the miss rate is `[proxy]`, bounded at 0 to 1.1% of non-hit domains.

## Advisor reading (2026-11-04)

Accepted for R1: no header detection in discovery. The pilot rules out a **large** gap (95% upper bound about 1.1% of non-hit domains) but not a small one, and the sample was not limited to store-like domains, so the miss rate **among real stores** is still unmeasured. Headless or custom front ends that show no Shopify markers at all stay invisible to both methods. Practical consequence: the top-stores list can miss some large brands on custom stacks; the report says so. Revisit only if the owner names a known Shopify store that we failed to find.
