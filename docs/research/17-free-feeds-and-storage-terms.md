# 17 — Free feeds, and what each API lets us store

> `market-researcher` (Haiku), 2026-11-03. The **eBay clauses below were re-fetched and checked against the license text** by the orchestrator. Everything else is as reported by the agent. Research, not legal advice.

## A. eBay API License Agreement (verified against https://developer.ebay.com/develop/apis/api-license-agreement)

| Section | Wording (quoted, capped by the fetch tool) | What it means for us |
|---|---|---|
| 8.1.3 | "Displayed item listing information may not be more than six (6) hours older than information displayed on the eBay Site"; other content "no more than twenty-four (24) hours older" | Listing data we show must be fresh. This is written for displayed content in an Application. |
| 8.1.2(b)(1) | "When the eBay Content is no longer publicly available, you must delete it from your Application." | Delete on delisting |
| 3.1(b) | "All intermediate copies must be deleted when they are no longer required for the purpose for which they were created" | No lingering staging copies |
| 9.7 | no "copy, store or modify eBay Content, other than for the purposes allowed by this API License Agreement" | Storing is allowed only for permitted purposes. The page has **no clause expressly permitting internal research or analysis.** |
| 8.1.4(a) | "You must have eBay's express prior written permission to use or display eBay Content" including "Any site-wide statistics" and "Average selling price or gross merchandise sold for any eBay category" | **Statistics and average selling prices need written permission.** |
| 9.5 | no use of eBay Content, alone or combined with third-party data, "to suggest or model prices" | **Using eBay data to price our listings is restricted.** |
| 9.10 | no use of eBay Content "to train algorithms, conduct machine learning" | No ML on eBay data |
| 9.6 | no use of eBay Services "to promote or engage in seller arbitrage", with examples: "automatically repricing eBay listings in response to price changes on other third-party sites", "automatically ordering sold items from other third-party sites", or "posting tracking information to eBay when items purchased from other third-party sites are shipped" | **Automating CJ orders, tracking upload or repricing through the eBay API is prohibited.** Found by the PR #1 reviewer, re-verified against the license text 2026-11-03. |
| 8.5(2)(d) | no electronic distribution of **Restricted API** data, raw or aggregated | Marketplace Insights (sold data) is Restricted |
| 16.3 | destroy all copies within 10 days after termination | Retention ends with the agreement |

The agreement does not distinguish Buy from Sell APIs for these rules. Restricted APIs are defined by data type (market trends, pricing, sales volumes).

**Second consequence (9.6):** order forwarding to CJ and tracking upload to eBay must be **manual** (or through a path eBay has approved for the supplier's own integration, which is unverified). No API-driven ordering, tracking posts, repricing or stock syncing from CJ.

**Consequence:** the plan to ingest eBay Browse data into the warehouse, compute price statistics and use them to set prices is **not safe without eBay's written permission.** This changes the evidence strategy; see decision 0004.

## B. Other storage terms

| Source | Finding |
|---|---|
| Google (terms effective 2026-07-30) | Prohibits "using automated means to access content from any of our services" in breach of machine-readable rules. **pytrends is unofficial automated access.** [agent reading, unverified for Trends specifically] |
| WIPO Global Brand DB | Automated query and bulk download prohibited; no resale (terms Nov 2022). **Exclude.** |
| CJ | API is free; no data-use or rate-limit terms found on the developer page. CJ clears store data (orders, addresses) on its own schedule. **Developer agreement not located [unverified].** |
| openFDA | CC0, no attribution required. |
| CPSC | No terms page; data is described as available to "software and application developers". |

## C. Free feeds, ranked

| Rank | Feed | Endpoint / notes | Key | Cadence | Verdict |
|---|---|---|---|---|---|
| 1 | **CPSC recalls** | `saferproducts.gov/RestWebServices/Recall?format=json` | none stated | not stated | Highest compliance value. Keep RecallID, URL, pull date. Test the reported broken hazard filter. |
| 2 | **openFDA enforcement** | open.fda.gov JSON | optional (240/min, 120k/day with key) | weekly | CC0. Only FDA-regulated goods. |
| 3 | **Google Product Taxonomy** | static text file, version 2021-09-21 | no | static | Category mapping. License unconfirmed. |
| 4 | **USITC HTS**, **Federal Register** | `hts.usitc.gov/reststop/*`; `federalregister.gov` API | no (secondary) | daily | Duty rates and tariff notices. Verify endpoints first. |
| 5 | **eBay Taxonomy API** | category tree, item aspects | eBay dev account | static | **Reference data only** (category IDs, aspect names). No listings or prices. |
| 6 | **USPTO trademark bulk (CC0)** | data.uspto.gov, key required | yes | not verified | Brand blocklist. Later. |
| defer | PatentsView (design patents), FCC open data, Census e-commerce, UPCitemdb | unreachable or unverified | | | Re-check |
| exclude | eBay Marketplace Insights, WIPO, scraping Google Trends | | | | See above |

## Sources
1. https://developer.ebay.com/develop/apis/api-license-agreement (verified)
2. https://www.saferproducts.gov/RestWebServices/Recall ; https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information
3. https://open.fda.gov/apis/authentication/ ; https://open.fda.gov/apis/drug/enforcement/ ; https://open.fda.gov/terms/
4. https://www.federalregister.gov/reader-aids/developer-resources/rest-api (blocked; snippet)
5. https://developer.uspto.gov/api-catalog/tsdr-data-api (redirected, empty)
6. https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt
7. https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategoryTree
8. https://developer.ebay.com/api-docs/buy/marketplace-insights/overview.html
9. https://www.wipo.int/reference/en/branddb/terms_and_conditions.html
10. https://policies.google.com/terms
11. https://cjdropshipping.com/storeAuthorizationAgreement ; http://developers.cjdropshipping.com/en/summary/
12. https://hts.usitc.gov/ (title only) ; https://opendata.fcc.gov ; https://www.census.gov/retail/ecommerce.html ; https://upcitemdb.com/api/explorer
