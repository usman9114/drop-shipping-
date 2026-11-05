# 35. Fingerprint validation (W3): how far can we trust each indicator?

> 2026-11-05. Workstream W3 of `docs/plan/supply-fingerprints-plan.md`. Scored against the lake rows written before `RULE_VERSION` existed (runs `20261105T110803Z-b4db94` 105 stores, `20261105T110543Z-052ec4` 10 brand controls, `20261105T111006Z-d01d44` 30 extra brands, new for this report). Not re-scored with the rule version added in b5abf5f. Per-store truth stays private: `data/private/research/fingerprint-truth.csv` (labels and short notes, no product text or images).

## Method and limits

- 67 stores hand-checked from public data only: `/products.json?limit=60` plus one product page, project UA, robots.txt respected, no rendering. Truth labels: dropship_aliexpress, dropship_cj, dropship_other, pod, brand_or_own_stock, unclear. `[proxy]`: truth is my reading of public traces, not supplier confirmation. 6 stores are `unclear` and left out of every precision figure.
- The sample is **not random**. It holds all 14 `unknown` stores, all 7 AliOrders / CJ-app stores, 10 brand controls, 12 extra brands (the 3 that fired and 4 high-AE-share ones among them), 11 AliExpress-estimated and 8 CJ-estimated stores picked at evenly spaced confidence ranks, 3 "Ships From" stores, 2 POD. Precision below is within this sample; small counts mean wide intervals (18/18 correct has a 95% lower bound of about 82%).
- Truth for a store is read from a 60-product slice (the pipeline reads 250). One case needed the 250-product feed: all 60 sampled products of one CJ store had no SKU, 152 of 250 had CJ SKUs.
- Not measured `[unknown]`: warehouse country (nothing public confirms where a parcel ships from), cost, margin, order volume.

## Per-indicator precision `[data]` (sample, `unclear` excluded)

Precision = fired where the implied source matches truth. For `china_shipping` and `none`-implying apps the test is "store is an AliExpress/CJ dropshipper" (or any dropship for `none`). Recall is against hand-labelled stores of that source (sample is biased, indicative only).

| Indicator | Implies | Fired | Precision | Recall | Verdict | False positives |
|---|---|---|---|---|---|---|
| sig aliorders | aliexpress | 3 | 3/3 100% | 3/15 | evidence | none |
| sig cjdropshipping (page) | cj | 4 | 4/4 100% | 4/12 | evidence | none |
| sig cj_feed | cj | 1 | 1/1 | 1/12 | too few | none |
| feed cj_sku_share | cj | 12 | 12/12 100% | 12/12 | evidence | none |
| feed ae_item_id_share | aliexpress | 4 | 4/4 100% | 4/15 | evidence | none |
| feed o1cn_share | aliexpress | 4 | 4/4 100% | 4/15 | evidence | none |
| feed ae_image_share | aliexpress | 16 | 14/16 88% | 14/15 | evidence | CJ store at 9% share; Amazon+AE mixed store |
| feed ships_from | aliexpress | 8 | 7/8 88% | 7/15 | evidence | Amazon+AE mixed store |
| feed dsers_sku_share | aliexpress | 8 | 6/8 75% | 6/15 | **hint** | CJ store at 7% share; mixed store |
| sig printful | pod | 6 | 1/6 17% | 1/2 | **hint, drop** | script/pixel loaded on AE, CJ and used-gear stores |
| sig ali_reviews | aliexpress | 6 | 2/6 33% | 2/15 | **hint, fix pattern** | 2 hits are a map string `"AliReviews"` inside the PageFly app-block JS; 1 real widget on a non-AliExpress store; 1 CJ store |
| feed vendor_supplier_share | aliexpress | 2 | 0/2 0% | 0/15 | **hint** | n=1 demo store (vendor "TPO Demo store" matched `store$`); vendor "Cj Dropshipping" routed to aliexpress |
| feed boilerplate_share | aliexpress | 2 | 1/2 | 1/15 | too few | CJ/Trendsi mixed store |
| sig dsers_feed | aliexpress | 1 | 0/1 | 0/15 | too few | CJ store |
| feed cjk_share | 1688 | 2 | 1/2 | n/a | **hint** | brand with Chinese channel tag (same as P1 finding) |
| sig ryviu | none (any dropship) | 7 | 6/7 86% | n/a | hint (nudge only) | brand with small POD line |
| sig loox | none | 7 | 4/4 evaluable | n/a | nudge only | 3 unclear |
| sig parcelpanel / track123 / 17track | china_shipping | 4 / 1 / 1 | 2/2, 1/1, 1/1 | n/a | too few; ParcelPanel also appears as a returns page on a brand | none |
| gen bulk_burst >= 20 | any dropship | 15 | 8/13 62% | n/a | **hint** | 5 brands (feed uploads, surplus lots) |
| gen compare_at >= 2x | any dropship | 9 | 5/7 71% | n/a | **hint** | 2 brands |
| gen grams_zero >= 80% | any dropship | 23 | 6/19 32% | n/a | **drop** | 13 brands (own stores rarely fill weights) |

Never fired in the sample (no precision): dsers, zendrop, spocket, autods, syncee, alidropship, oberlo, printify, gelato, kudosi, aftership. They remain `[unknown]`.

## Supply estimate accuracy `[data]` (61 evaluable stores)

| Measure | Result |
|---|---|
| `source_guess` accuracy when a source is named (aliexpress/cj/pod) | 28/31 (90%) |
| Same, only the 18 stores picked at evenly spaced ranks from the AE and CJ estimates | 18/18 (lower bound about 82%) |
| Whole estimate (including `unknown` = "not a dropshipper") | 54/61 (89%) |
| Dropship-or-not: TP / FP / FN | 29 / 2 / 4 |
| Wrong named sources | brand with a Printful pixel guessed pod (0.3); software demo site guessed aliexpress (0.35); Amazon+AE mixed store guessed aliexpress (0.92) |
| Missed (guessed unknown, truth dropship/pod) | 2 `dropship_other` (Amazon ASIN SKUs, a jewelry feed), 2 POD (POD supplier SKU shape) |

Confusion (truth rows, guess columns): AE 15 of 15 aliexpress; CJ 12 of 12 cj; other: 1 aliexpress, 1 unknown_dropship, 2 unknown; pod: 1 pod, 1 unknown; brand: 24 unknown, 2 unknown_dropship, 1 aliexpress, 1 pod.

| Confidence band | n named | correct | Accuracy |
|---|---|---|---|
| below 0.4 | 6 | 4 | 67% |
| 0.4 to 0.6 | 5 | 5 | 100% |
| 0.6 to 0.8 | 12 | 12 | 100% |
| 0.8 and up | 8 | 7 | 88% |

Reading: the score is monotone only up to 0.4. Both wrong low-band guesses come from one weak signal each; the one high-band error is a mixed-source store (Amazon plus AliExpress) that no single-source model can name. Mid bands are under-confident (100% right at 0.4 to 0.8), so the numbers are conservative, not overstated. The "Ships From" country list still says nothing verified about the real warehouse.

## Free-model second opinion `[proxy]`

Task: label each of the 67 stores from a compact trace summary (vendors, first SKUs, image file-name shapes, option names, tags, third-party hosts), system prompt with label definitions and 4 synthetic examples. Models: GLM Flash (`zai:glm-4.5-flash`, 67 ok) and OpenRouter free lane (`nvidia/nemotron-3-ultra`, 66 ok, 1 error).

| Check | Result |
|---|---|
| GLM vs my truth (61, `unclear` excluded) | 52/61 85% |
| Nemotron vs my truth (60) | 55/60 92% |
| GLM vs Nemotron agreement | 53/66 80% |
| Both agree and match truth | 50/53 |

Disagreements hand-checked (13): GLM right on 2 (POD SKU shape, jewelry feed), Nemotron right on 4 (a software demo, two brands GLM called dropship_other, a POD store), both wrong on 2 CJ stores (CJ SKUs only visible beyond the first 6 products), the rest on `unclear` stores where each model guessed. Nemotron defaults to brand_or_own_stock when traces are thin; GLM over-calls dropship_other. Neither is reliable enough to decide alone; useful as a flag on stores the rules label `unknown`. Both found the POD SKU shape (`YYMMDDPOD..#nnn`) that the rules miss.

## Proposed WEIGHTS and rule changes (applied 2026-11-05 in `RULE_VERSION` 2026-11-05.3, see below)

| Item | Now | Proposed | Why `[data]` |
|---|---|---|---|
| `feed.ae_image_share` threshold | 0.05 | **0.20** | true positives all at 0.39 or more; false positives at 0.004 to 0.092 |
| `feed.dsers_sku_share` threshold | 0.05 | **0.20** | true positives 0.49 or more (one 0.008 store is an AliOrders store); CJ store at 0.072 |
| `feed.cj_sku_share` weight | 0.6 | **0.7** | 12/12 correct, shares 0.40 to 1.0 |
| `cjdropshipping` page signature evidence | unverified (x0.5) | **observed** (x1.0) | 4/4 correct, host seen in CJ image/app URLs |
| `printful` page signature | strong, pod | **weak, implies none** (or pod only when vendor/SKU also says POD) | 1/6 precision |
| `ali_reviews` pattern | `ali[-_ ]?reviews\|alireviews` | **require** `ali-reviews-\d+/assets`, `alireviews.min`, `alireviews-review-*` or `ali-widget`; strength weak | 2 of 6 hits were a PageFly name map |
| `feed.vendor_supplier_share` | weight 0.2 | **0.05, only when n_products >= 10**; route "CJ" vendors to cj | 0/2; n=1 demo store fired |
| `generic.grams_zero` | 0.1 | **0.0** | 32% precision |
| `generic.bulk_burst_big` | 0.2 | **0.1** | 62% precision; brands upload in bursts |
| `generic.compare_ratio` | 0.1 | **0.05** | 71% |
| Any source rule, n_products < 5 | fires | **do not fire** (demo/app sites) | two non-store sites produced aliexpress guesses |
| Mixed sources | single best | add `mixed` when two source scores each reach 0.4 | the 0.92 error was Amazon+AE |

Expected effect on this sample, by re-scoring the saved shares by hand: the 2 wrong low-band guesses and the demo-site guess disappear, no true AE/CJ guess falls below 0.2. Not yet re-run through `supply_estimate`; re-score once edited.

## Signatures and rules worth adding (from 33a, 33b, 33c plus what we saw)

| Candidate | Source | Seen in the 67? | Note |
|---|---|---|---|
| Tag `Ship From Overseas` (Trendsi) | 33b | **Yes, 1 store** (1 of 60 products tagged, plus a `trendsi` collection and `trigger_data_tags: Trendsi` in page source), a store that mixes CJ, a wholesaler and Trendsi | add as feed signature, implies us_supplier/wholesale mix |
| Location `Trendsi US` | 33b | not visible in public data | cannot be used; drop |
| `/apps/parcelpanel` tracking path | 33c | 5 stores (tracking page link, one a returns page `/apps/parcelpanel-returns`) | already caught by the parcelpanel host regex; keep weak |
| `alireviews.fireapps.io` | 33a | **No** hit; real widgets load from `cdn.shopify.com/extensions/.../ali-reviews-NNN/assets/alireviews.min.js` and `alireviews-review-star-rating` classes | replace the host guess with these |
| `zopi.io`, `fireapps.io` | 33a | `fireapps.io` on all 3 AliOrders stores; `zopi.io` none | keep `aliorders.fireapps.io`; zopi optional |
| "Ship From" spelling | 33a | only `Ships From` (53 option names), no `Ship From` | current regex already covers both |
| Wizishop SKU prefix `di-` | 33a | none | unverified, skip |
| CJ OSS image hosts `*.cjdropshipping.com`, `cc-west-usa.oss-accelerate.aliyuncs.com` in page | seen | 5 stores | add as cj page signature (observed) |
| POD supplier SKU shape `\d{6}POD[A-Z]{2}\d+#\d+` | seen | 2 stores, both true POD, missed by rules | add; feed now carries `sku_shapes` so re-score without refetch |
| Amazon ASIN SKUs `^B0[0-9A-Z]{8}$` + Amazon image names | seen | 2 stores (one with `amazon` tag and `Sync Pending`) | add as dropship_other / amazon; note CLAUDE.md bars Amazon as our own source, it is only a competitor trace |
| Tag `Shopify Collective` | seen | 1 dropship_other store | add, implies other |
| `jewelershowcase.com` host | seen | 1 jewelry feed store | single sighting, add as unverified |
| Chinese colour words in SKUs / `angelkiss`-style `brand#model#colour` | seen | 1 Chinese own-label brand | not a dropship trace; do not add |
| Shopify `synctrack.io`, `goaffpro`, `appsolve.io`, `debutify` | seen | 4, 6, 2, 1 | dropship-adjacent but also on brands (4 of 4 synctrack stores were brands or unclear); keep out |

## What we still do not know

- Whether `China (assumed)` warehouses are right, and any real ship-from country: no public trace verifies it `[unknown]`.
- Recall on the 11,415-store population: sample is biased toward stores the rules already flagged; the 14 `unknown` stores gave 3 misses out of 14 (21%) `[data]`, and unlabelled brands were not hand-checked.
- Weights for signatures that never fired.
- Truth labels are my reading of public traces; no supplier confirmed any of them.

## Applied (2026-11-05, `RULE_VERSION` 2026-11-05.3)

All rows of the two tables above went into `scout/fingerprints.py`, except `zopi.io` (optional, never seen) and the rows marked skip/drop. Each W3 error is a test in `tests/test_fingerprints.py` (`test_w3_*`, 18 tests). Choices the tables left open:

- **Bulk burst:** big 0.2 -> 0.1 as proposed; small 0.1 -> 0.05 so a bigger burst never weighs less than a smaller one.
- **Consequence:** generic hints now sum to at most 0.145, under `min_generic_for_dropship` 0.25, so burst/compare-at/review apps alone no longer produce `unknown_dropship` (the 2 brands W3 saw labelled that way). They stay in `evidence`.
- **Under 5 products:** applies when the feed has 1 to 4 products. A feed of 0 (products.json missing or robots-blocked) still lets page signatures count.
- **Vendor rule:** weight 0.05 and only with 10+ products; vendors matching `^cj` / "CJ Dropshipping" count as `cj_vendor_share` -> cj (weight 0.05) instead of aliexpress.
- **Mixed:** when the top two source scores each reach 0.4, `source_guess` is `mixed`, `mixed_sources` names them, confidence is the weaker of the two (plus the capped generic nudge).
- **New sources:** `pod_sku_share` (pod 0.6) and `asin_sku_share` (new source `dropship_other` 0.5), both firing at 0.20 share; feed tags `trendsi` (us_supplier, medium/observed) and `shopify_collective` (dropship_other, medium/observed); page host `jewelershowcase.com` (dropship_other, medium/unverified, so 0.15 alone: below the 0.2 source bar until seen again); CJ OSS bucket added to the `cjdropshipping` signature (no double count).
- **SKU shapes cannot re-score the new SKU rules:** `sku_shape` turns letters into `A`, so `POD` and the `B0` ASIN prefix are lost. Rows from before .3 need a refetch for these two rules; the other rule changes re-score from saved shares.

### Accuracy before/after

- **Before** `[data]`: whole estimate 54/61 (89%), named source 28/31 (90%), dropship-or-not FP 2 / FN 4 (tables above).
- **After: not measured.** The truth CSV (`data/private/research/fingerprint-truth.csv`) and the fingerprint lake rows were not in the vault (last export 2026-11-04, and `vault_export.py` did not cover them), so the fresh container that applied these rules could not re-score. `vault_export.py` now exports `web_fingerprints` and the truth CSV.
- **Projection `[proxy]`** from the 7 documented errors, not a measurement: the Printful brand, the demo site, the 2 POD misses and the ASIN store should now be right, and the Amazon+AE store becomes `mixed` (aliexpress + dropship_other); the jewelry-feed store stays missed (unverified host alone is below the bar); the 2 brands called `unknown_dropship` become `unknown`. Risk: the one `dropship_other` store guessed `unknown_dropship` may now fall to `unknown`. Expected range 58 to 60 of 61. Confirm by re-labelling or restoring the truth set and re-running on the 105.
