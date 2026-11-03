# 04 — Tooling, APIs and AI listing pipeline

> Researched 2026-11-03 by a web-search agent. Several official eBay pages failed to load (403/404), so some API figures come from search snippets and secondary sources. Items marked **[unverified]** need checking on developer.ebay.com before you build on them.

## 1. eBay developer APIs

| API | What it gives us | Access |
|---|---|---|
| **Marketplace Insights** (sold items, ~90 days) | Sold prices and counts. This is the key input for picking products. | **Limited Release**: only developers approved by eBay business units. Forum posts report requests failing or being declined. Assume we can't get it. |
| **Terapeak** (Seller Hub → Research) | About 3 years of sold data | **UI only.** No public API found. |
| **Browse API** | Active listings: search, prices, competition counts | 5,000 calls/day by default. A snippet says it needs an additional license **[unverified]**. |
| **Sell Inventory / Offer** | Create and manage listings | About 2M calls/day by default |
| **Fulfillment** | Orders, tracking upload | Standard Sell API |
| **Taxonomy** | Categories and required item specifics | Standard |
| **Feed (Buy)** | Bulk item feeds | Limited release. Not in the sandbox. |

- A new developer account gets a free tier of about 5,000 calls/day. The **Application Growth Check** raises limits. The sandbox has static data.
- The Developer Analytics API `rate_limit` resource reports current usage.

## 2. Third-party research tools

| Tool | Focus | Price (conflicting sources) | API? |
|---|---|---|---|
| ZIK Analytics | eBay research and competitor analysis | $14–30/mo | Not confirmed |
| DSM Tool | Listing/import from Amazon, AliExpress and Walmart to eBay (retail arbitrage, see 01) | — | — |
| Sell The Trend | All-in-one research | ~$33–50/mo | Not found |
| AutoDS | Order automation, import, fulfillment | low entry tier **[unverified]** | — |
| Kalodata / Minea | TikTok Shop / ad research | €49–99/mo (Minea, stale) | No |
| Helium 10 / Jungle Scout | Amazon | $249+/mo top tier | API on higher tiers |

## 3. Finding winning products programmatically

- There is no official "winner" metric. Common proxies:
  - **Sell-through** = sold ÷ (sold + active)
  - sold-count trend
  - competition count
  - spread between supplier price and marketplace price
- Sold data is the hard input, and access to it is gated.
- Open-source projects on GitHub:
  - `driscoll42/ebayMarketAnalyzer`: sold-listing price stats. eBay CAPTCHAs now block it, so it works from manually saved search pages.
  - `leoncvlt/bidbybid`: sold-auction prices, by scraping.
  - `FaustinoLopez/ebay-sell-through-tool`: sell-through calculator **[unverified]**.
- **Scraping sold listings likely breaches eBay's terms and breaks easily.** Prefer Terapeak manual exports, or an approved Marketplace Insights application.

## 4. AI for listings

- **Background removal:** Photoroom API costs about $0.02 per image (Basic plan). remove.bg is about $9/mo for 40 credits. One unconfirmed claim says remove.bg's self-service API shuts down on 2026-12-01.
- **Generative edits (approximate cost per image):**

  | Model | Cost |
  |---|---|
  | Gemini image ("Nano Banana 2") | $0.045–0.067 |
  | OpenAI gpt-image-1.5 | ~$0.04 |
  | Flux 2 Pro / Kontext (best for image-to-image) | $0.045–0.06 |

  Verify these on the official pricing pages.
- **eBay Magical Listing** (US/UK, April 2025): free AI listing generation from a photo. An upgraded version came in Q4 2025.
- **Policy:** images must "accurately represent the item". AI images are not banned and no label is required **[unverified]**. Wrong AI-written claims (for example "includes lens kit") lead to INAD returns. **AI must improve presentation, never invent features.**

## 5. Cassini / Best Match ranking factors

eBay publishes no weights. Secondary sources consistently list:

- title keyword relevance
- item specifics and correct category
- product identifiers (UPC, MPN)
- completeness
- photo quality
- price competitiveness
- seller performance
- return policy and handling time

Missing required specifics can hide a listing from search.

## Takeaways for the PoC

1. Don't depend on sold-data APIs. Use Terapeak UI exports or the Browse API's active-listing data as proxies, and apply for Marketplace Insights in parallel.
2. Build listing creation on the Sell Inventory API.
3. Use an image API for cleanup. Keep AI-generated content factually tied to the supplier's specs.
4. Re-check vendor prices before spending money.

## Sources
1. https://developer.ebay.com/api-docs/buy/marketplace-insights/overview.html
2. https://community.ebay.com/t5/RESTful-Sell-APIs-Marketing/Marketplace-Insight-API-responded-with-Access-denied/m-p/35066714
3. https://innovation.ebayinc.com/stories/new-improved-terapeak-research-2-0-in-ebay-seller-hub/
4. https://developer.ebay.com/develop/get-started/api-call-limits (snippet only)
5. https://developer.ebay.com/develop/api/buy/api_call_limits
6. https://www.developer.ebay.com/api-docs/buy/feed/v1/static/overview.html
7. https://www.zikanalytics.com/home/pricing
8. https://www.sellthetrend.com/blog/sell-the-trend-vs-autods-2
9. https://creatify.ai/blog/kalodata-pricing-plans-and-what-you-ll-actually-pay-in-2026
10. https://revenuegeeks.com/?p=5995
11. https://www.github.com/driscoll42/ebayMarketAnalyzer
12. https://github.com/leoncvlt/bidbybid
13. https://docs.photoroom.com/remove-background-api-basic-plan/pricing
14. https://costbench.com/compare/photoroom-vs-remove-bg/
15. https://invideo.io/blog/ai-image-model-pricing/
16. https://www.digitalcommerce360.com/2025/04/15/ebay-ai-aided-tool-cut-steps-create-listings/
17. https://nightjar.so/help-desk/does-ebay-allow-ai-generated-product-photos-in-listings
18. https://www.valueaddedresource.net/ebay-tests-ai-fashion-models-alters-images/
19. https://sellercentre.ebay.com.sg/listing-basics/advance-your-listing/best-match-1-introduction
20. https://www.frooition.com/ebay-seo-guide
