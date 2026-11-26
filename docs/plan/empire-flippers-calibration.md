# Empire Flippers calibration pass

> 2026-11-23. Owner approved the idea; manual reading only. Purpose: see real revenue and profit of Shopify and dropship businesses for sale, and check whether our `[proxy]` signals point at the profitable ones. Context: `docs/plan/tool-shortlist.md` (ground-truth row), CLAUDE.md principles 2, 3 and 6.

## Rules before you start

1. **Read Empire Flippers' terms first** and write the date, what you may keep, and the link at the top of your filled sheet (terms gate). Until then keep the sheet in `data/private/research/`, never in git.
2. **Manual reading only.** No scraping, no scripts against the site, no bypassing the login or the hidden business name.
3. Record what the listing shows. Do not guess a store's name from its numbers, and do not contact sellers for this.
4. A listing is a **biased sample**: only businesses that someone wants to sell, mostly US and Western stores. It calibrates what a profitable store looks like. It says nothing about Pakistan or about eBay demand.

## Which listings (aim for 20)

- Category: e-commerce, Shopify or dropshipping. Include a few with a higher and a lower profit so the sample is not all winners.
- Prefer listings that show **monthly profit for 12 months** and the **traffic split**.
- Skip content sites, apps and Amazon FBA brands, except as a labelled contrast.

## What to record per listing

| Column | Where to look | Why |
|---|---|---|
| `listing_id`, `date_seen` | listing page | traceability |
| `model` | description: dropship, own brand, print on demand, reseller | compare with our rule labels |
| `niche` | description | our category names |
| `age_months` | listing | store age |
| `revenue_12m`, `profit_12m` | listing financials (state the currency) | the real numbers |
| `net_margin` | profit / revenue | the ground truth we lack |
| `trend` | monthly chart: rising, flat, falling | compare with our rank growth |
| `traffic_split` | listing: paid, organic, email, social, direct | compare with our ad pixel and channel signals |
| `paid_share` | share of traffic or sales from paid ads, if given | effort and budget proxy |
| `monthly_visits` | listing or analytics screenshot | compare with Tranco and CrUX popularity |
| `products` | number of SKUs | compare with `published_products` |
| `avg_order_value` | listing | compare with our median price |
| `supplier` | AliExpress, CJ, US supplier, own | compare with our supply fingerprints |
| `ads_channels` | Meta, Google, TikTok | compare with our homepage pixels |
| `asking_price`, `multiple` | listing | what the market pays for profit |
| `owner_hours_week` | listing | effort |
| `notes` | anything odd (one hero product, seasonal, a single supplier) | caveats |

Blank template: `docs/plan/empire-flippers-template.csv`. Save the filled copy as `data/private/research/ef-listings.csv`.

## What we compare afterwards (small first, principle 10)

1. **Margin sanity:** the real net margin of dropship and reseller stores. The project's go bar is 15% realized; if listed stores earn far less or more, our margin model needs adjusting before any spend.
2. **Paid reliance:** how much of the profit depends on paid ads. A store that needs ads to sell is not a free copy.
3. **Traffic versus profit:** if monthly visits barely predict profit across the 20, then Tranco and CrUX rank is a weak proxy for success, and the ranking page must say so.
4. **Product count and price:** typical SKU count and order value of profitable dropship stores, to compare with the Pakistani stores we rank.
5. **Hero-product share:** if most profit comes from one or two products, "replicate the store" is the wrong frame and "replicate the product" is the right one.

## What would change the plan

- Dropship stores in the sample mostly lose money or depend on heavy ad spend: the copy-the-winner idea needs stricter filters before Phase 1.
- Profit concentrates in own-brand stores: our ranking of brands shows demand only, as already stated.
- Traffic does not track profit: stop using rank as a success signal and lean on the business-model and margin checks.

## Not in scope

Buying a business, contacting sellers, paying for an Empire Flippers plan, scraping the site, any Pakistan-specific conclusion.
