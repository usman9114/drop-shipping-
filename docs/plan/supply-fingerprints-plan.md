# Plan: read a store's hidden supply fingerprints and estimate its source

> 2026-11-05. Owner: "aliorders.fireapps.io — super smart, this is what I was talking about. Be street smart: we need more indicators like this. Let the whole team focus on how we can extract hidden patterns from a website (CJ or AliExpress plugin etc.) so we can approximate their source."
>
> Rules unchanged: public pages only (homepage, product pages, `/products.json`), robots.txt read first, one honest User-Agent, no checkout, no login, no bot-check workarounds. We store **counts, flags, hashes and app names**, never product text or images.

## Goal

For every screened store, produce a **supply estimate**: where its products most likely come from (AliExpress, CJ, 1688/Taobao, a US supplier or 3PL, print on demand, wholesale, or its own production), which warehouse country ships them, and the evidence behind it with a confidence. For the strongest dropshippers, match their products to CJ's catalogue to approximate **their cost and margin**.

## The traces a store leaves (indicator catalogue, first draft)

| Layer | Trace | What it reveals | Strength |
|---|---|---|---|
| **App scripts** | Script URLs a Shopify app injects (`asyncLoad` URL list in the page source), app-embed asset paths (`cdn.shopify.com/extensions/<id>/<app-handle>-…`), app API calls (e.g. `aliorders.fireapps.io/api/shop/…`) | the installed fulfilment, importer, review and tracking apps by name | **strong** |
| **Product feed: images** | Alibaba-family file names kept after import: `O1CN01…` (Taobao/1688/AliExpress CDN), `H`/`S`/`U` + 32 hex (AliExpress), CJ image naming | the original listing platform | **strong** |
| **Product feed: ids** | AliExpress item ids (16 digits starting `1005…`) in handles, SKUs, tags or body; DSers property SKUs (`14:200006152#…`); CJ SKUs (`CJ…` + digits); other importer SKU formats | importer tool and exact supplier listing | **strong** |
| **Product feed: options** | A variant option called **"Ships From"** with values like China / United States / Spain | supplier platform (AliExpress keeps it) **and the warehouse country**: the domestic-3PL question answered directly | **strong** |
| **Product feed: vendor and tags** | vendor = supplier shop name ("…Store", "Shop1102…"), "AliExpress", "CJ"; tags such as `dsers`, `zendrop`, `ali` | importer and supplier | medium |
| **Product feed: copied supplier text** | AliExpress boilerplate (we count matches only): "Please allow 1-3cm differs due to manual measurement", "Due to the light and screen difference", "Package includes: 1 x", stray Chinese characters | listing copied from a marketplace | medium |
| **Product feed: behaviour** | hundreds of products created in the same minute (bulk import); `grams` = 0; inventory not tracked; compare-at prices 2 to 5 times the price | importer use, no own stock | medium |
| **Tracking and logistics** | order-tracking app (ParcelPanel, Track123, 17TRACK, AfterShip pages) and carriers named on the tracking or shipping page: YunExpress, Yanwen, 4PX, Cainiao, CNE, ePacket, China Post vs USPS/UPS only | shipping origin (China vs domestic) | **strong** when carriers are named |
| **Theme and marketing kit** | `Shopify.theme` name and theme-store id (dropship-favoured themes such as Debutify, Booster, Shrine), urgency/FOMO and review-import apps (Vitals, sales pop-ups, Loox/Ali Reviews/Kudosi/Ryviu importing AliExpress photo reviews) | dropship playbook | weak to medium |
| **Policies** | shipping times, "ships from overseas", customs notes, return address abroad | origin | weak alone (noisy: promo banners, backorders) |
| **Product match to suppliers** | perceptual hash of a store's product image and its title, matched against **CJ's catalogue through our CJ API** | the likely CJ product **and its cost**, so their margin | **strong when matched** |

## Team and workstreams

| Workstream | Owner (agent) | Output |
|---|---|---|
| W1 **Fingerprint catalogue**: the public storefront footprint of each supplier, importer, tracking and review app (script domains, app-embed handles, SKU and image formats), from public docs and app listings, then checked on live stores | Market researchers (Haiku, parallel, one family each) | `docs/research/33a-c-*.md` |
| W2 **Extractor**: `scout/fingerprints.py`: page-source app detection, theme, product-feed signals (images, ids, "Ships From", vendor, boilerplate counts, bulk-import bursts), tracking-page carriers; tested | Data engineer (Sonnet) | module, tests, pilot |
| W3 **Validation**: labelled set (stores with a confirmed app = positives, known brands = negatives); precision and recall per indicator; weights for the supply estimate | Data analyst (Sonnet) | `docs/research/35-fingerprint-validation.md` |
| W4 **Source match**: for top dropshippers, match products to CJ by image hash and title; estimated cost and margin | Sales lead (Sonnet) with the CJ client | `docs/research/36-source-match.md` |
| W5 **Compliance check**: robots, public pages only, counts not content, no circumvention | Compliance officer (Sonnet) | review note |
| Synthesis: weights, supply-estimate rules, decisions | Advisor (Opus) | decision note |

## Phases (small first)

1. **P0 catalogue** (W1, parallel now): AliExpress tools; US suppliers and 3PLs; print-on-demand, wholesale, themes, review importers and tracking apps.
2. **P1 extractor pilot** (W2): 20 stores (10 dropship-labelled including the AliOrders store, 10 known brands). Exit: every indicator fires on at least one positive and on no brand control, or its noise is documented.
3. **P2 validation** (W3): about 100 labelled stores; precision per indicator; weighting.
4. **P3 full run**: all 11,415 screened stores (homepage, one product page, feed already held).
5. **P4 source match** (W4): top 50 dropshippers against CJ; cost and margin estimates.
6. **P5 use it**: supply source and warehouse country become columns in the niche shortlist and the watchlist; domestic-3PL dropshippers become their own study group.

## Exit criteria

- Supply estimate with evidence for every screened store, confidence stated.
- Each indicator's precision measured on labelled stores; anything under 80% is a hint, not evidence.
- At least 20 dropship products matched to CJ with a cost estimate.
- No raw store text or images stored; tests and pre-commit pass.

## P0 result (2026-11-05)

Three catalogue reports (33a, 33b, 33c). Main finding: **vendors almost never document what their app leaves on a storefront.** Nearly every storefront trace is `[unverified]`; the AliOrders host, DSers property SKUs and Alibaba image names are not in any public doc. So the catalogue must be built by **observation on live stores** (P1 pilot), not from docs. Useful documented traces:

- Trendsi writes a fixed Shopify tag "Ship From Overseas" and a location "Trendsi US" (33b).
- Dropified uses a "Ship From" / "Ships From" variant option (both spellings to test) (33a).
- ParcelPanel's tracking page lives at `/apps/parcelpanel` (33c).
- AliOrders' developer is now "Zopi" (zopi.io domains); Ali Reviews (now Kudosi) may load from `alireviews.fireapps.io` (33a).
- New Shopify apps load through theme app extensions, so app-embed handles matter more than script tags (33b).
- 17TRACK can hide China origin on tracking pages; absence of a China carrier is weak evidence (33c).

## P1 result (2026-11-05)

`scout/fingerprints.py` built (31 tests). Pilot 20 stores (10 dropship-labelled, 10 brands): no signature or source signal fired on any brand; all 10 brands ended `unknown` at confidence 0.

**Bug found and fixed:** the DSers SKU rule (`^\d{3,}:\d+`) matched Tommy John's own SKUs (`10045041000:100072:XL`), and the same loose rule sat in the business-model classifier, which is why that brand was labelled dropship. The rule now needs an AliExpress property pair followed by `#name` or `;next-pair` (`14:200004889#Black;5:20129901`); brand SKUs are test cases.

**105 dropship-labelled stores** (run `20261105T110803Z-b4db94`, 2 minutes, 1 page error) `[data]`:

| Supply estimate | Stores |
|---|---|
| AliExpress | 65 |
| CJ Dropshipping | 24 |
| Print on demand | 2 |
| No supply trace (`unknown`) | 14 |

- Confidence: strong (0.8 or more) 27, medium 53, weak 12, none 13.
- Apps seen in page source: Loox 16, Printful 12, Ryviu 9, ParcelPanel 9, Ali Reviews 9, CJ Dropshipping app 4, 17TRACK 4, **AliOrders 3**, DSers 2.
- Feed traces: AliExpress image names on 61 stores, DSers SKUs 31, CJ SKUs 25, AliExpress item ids 12, Alibaba `O1CN01` images 7, copied AliExpress text 13, **"Ships From" option on 18**.
- Warehouse: China stated 8, China assumed 41, multi-country option list 13, unknown 43.
- The 14 `unknown` stores (including tommyjohn.com and renewlife.com) are the likely false positives of the old classifier rule; the full classifier needs a refetch with the corrected rule, since saved counts used the old one.

Caveats: weights are judgement, not measured; "Ships From" with about ten countries looks like AliExpress's all-country list, not a real warehouse split; Printful's script fired on 12 stores but drove a POD estimate on only 2. All of this is `[proxy]` until W3 measures precision.

## P2 result (2026-11-05)

Validation on 67 hand-checked stores (`docs/research/35-fingerprint-validation.md`) `[data]`, within a non-random sample:

- The supply estimate named a source on 31 stores and was right on 28 (90%); dropship-or-not 54/61 (89%).
- Strong rules held: AliOrders 3/3, CJ app 4/4, CJ SKUs 12/12, AliExpress item ids 4/4, `O1CN01` images 4/4; AliExpress image names 14/16 and "Ships From" 7/8.
- Below 80% (hints only): DSers SKUs 6/8, Printful script 1/6, Ali Reviews 2/6 (a page-builder app map, not the widget), bulk-import burst, compare-at ratio; grams = 0 at 32% is dropped.
- Missed: Amazon-ASIN dropshippers and POD stores with supplier SKU shapes; new signatures proposed.
- Free models as second opinion: GLM 85%, the OpenRouter model 92% against the hand labels; where both agree, 50/53 correct. Use them to flag stores the rules leave `unknown`, not to decide.
- Warehouse country cannot be verified from public data `[unknown]`.

Next: apply the proposed weights and signatures with tests, bump `RULE_VERSION`, re-score (`docs/handoff/session-state.md`, next steps).
