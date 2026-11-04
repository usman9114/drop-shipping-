# 26. Calibration set widening: Shopify-hosted stores that publish revenue

Date: 2026-11-04. Owner: market-researcher (Haiku). Status: partial. Target was 10 usable entries; this run found **1 partial entry with USD revenue**, plus 4 weak entries without comparable USD revenue. The target is not met.

Excluded from this run by instruction: BARK and Allbirds (already in the set). Gymshark and Honest are noted as weak below.

## Method and limits (read first)

- **SEC EDGAR full-text search was blocked.** Direct requests to `efts.sec.gov/LATEST/search-index` with the requested User-Agent returned HTTP 403 ("Your Request Originates from an Undeclared Automated Tool") for all four phrases. I did not try to get around this. Phrase discovery was done with general web search over sec.gov pages instead, which covers far less than EFTS. A browser search of EDGAR full text for "run on Shopify", "built on Shopify", "Shopify Plus" and "our ecommerce platform is Shopify" (10-K filter) is the owner's next step.
- **UK Companies House and press search were not run in this pass.** Gymshark's UK accounts were not checked.
- **Tranco rank was not checked.** No rank is given for any domain, so the top-1M filter is unverified for every row.
- Several 10-K fetches were truncated (Solo Brands, Grove FY2024). Where the figure comes from a search excerpt rather than the fetched text, the table says so.
- Case-study pages are published by Shopify, a conflicted source. They are marketing copy and carry no filing-grade figures.

## Table: entries found

| # | Brand | Domain | Fiscal year | Revenue (USD) | Scope | Filing or press URL | Shopify quote (verbatim) | Strength |
|---|---|---|---|---|---|---|---|---|
| 1 | Grove Collaborative Holdings | grove.co [unverified: domain not in the filing text fetched] | FY2025 | $173.7M net revenue ($173,716K). FY2024: $203.4M ($203,425K) | Total company (consolidated net revenue) | FY2025 10-K: https://www.sec.gov/Archives/edgar/data/1841761/000184176126000010/grov-20251231.htm . FY2024 10-K: https://www.sec.gov/Archives/edgar/data/1841761/000162828025013839/grov-20241231.htm | FY2024 10-K, risk-factor summary: "...including our transition to Shopify, could materially and adversely affect our business." Forward-looking statements: "...the advantages and impacts of transitioning to Shopify;" | **partial**. The filing says the company is moving from a legacy in-house platform to Shopify. It does not say the store is fully on Shopify. |
| 2 | Transformer Table | not stated [unknown] | not stated [unknown] | "surpassed $100 million in annual sales" (floor, no exact figure) | not stated [unknown] | https://www.casestudies.com/company/shopify-plus/case-study/transformer-table-scales-to-over-100-million-after-moving-to-shopify-plus (Shopify-published case study, conflicted) | "the company looked to Shopify Plus and its international sales tools." No sentence says the store runs on Shopify. | **weak** |
| 3 | Memobottle | not stated [unknown] | not stated [unknown] | none. "310% increase in global revenue"; period not stated | not stated [unknown] | https://www.casestudies.com/company/shopify-plus/case-study/memobottle-grows-global-revenue-by-310-with-shopify-plus | "Shopify Plus was the vendor chosen to help them scale." | **weak** |
| 4 | Bydee | not stated [unknown] | not stated [unknown] | none. "a 189% increase in global sales revenue" over two years | not stated [unknown] | https://www.casestudies.com/company/shopify/case-study/bydee-grows-global-sales-by-189-with-international-selling-tools-on-the-shopify-plus-plan | "After moving to Shopify and later upgrading to the Shopify Plus plan" | **weak** |
| 5 | Desmond & Dempsey | not stated [unknown] | not stated [unknown] | none. Headline "250% revenue growth" (search snippet only, page not fetched) [unverified] | not stated [unknown] | https://www.casestudies.com/company/shopify-plus/case-study/after-reclaiming-sunday-mornings-desmond-dempseys-growth-surged-250 | headline only: "migrating to Shopify Plus in 2018" [unverified] | **weak** |

Notes on the table:
- Row 1 is the only entry with a filing and USD revenue. Its FY2025 revenue comes from the 10-K as quoted in a search excerpt and in the Business Wire release dated 2026-03-05 (https://www.businesswire.com/news/home/20260305220738/en/grove-announces-fourth-quarter-and-full-year-2025-financial-results). The fetched 10-K text stopped before the financial statements. Treat the figure as [data] from the 10-K as excerpted, pending a full read. The company also says the revenue decline was driven by lower advertising spend and "disruptions related to the migration."
- Rows 2 to 5 have no fiscal year, no USD total, no domain and no scope. They cannot serve as ground truth for a revenue estimator. They are listed only so the owner sees what the lower tier contains.
- The "Shopify Plus" marketing pages carry a "©2026" footer and no publication date. Dates are therefore [unknown].

## Checked and not found

| Company | What was checked | Result |
|---|---|---|
| Solo Brands (CIK 1870600) | FY2025 10-K, first 100k of 331k characters (https://www.sec.gov/Archives/edgar/data/1870600/000187060026000013/dtc-20251231.htm); search excerpts for FY2021 to FY2024 | No "Shopify" or named ecommerce platform in the text read. DTC was 63.5% of FY2025 sales. Rest of the filing not read. **Not found.** |
| Digital Brands Group (CIK 1668010) | Search excerpts for FY2021 to FY2025 10-Ks | No Shopify mention in excerpts. **Not found.** |
| Kidpik (CIK 1861522) | Search excerpts for FY2022 and FY2023 10-Ks | Own site kidpik.com and Amazon/Walmart named; platform not named. **Not found.** |
| Lovesac; Lulu's Fashion Lounge | Search excerpts (cover pages only) | No platform named. **Not found.** |
| Honest Company (CIK 1530979) | Search excerpts for FY2021 to FY2025 10-Ks | No Shopify mention found. Honest.com is named as its "flagship digital platform" (FY2023); the FY2025 10-K says the company moved away from Honest.com as a shipping channel from 2025-12-31. **Weak / not confirmed.** |
| Gymshark (UK) | Not searched in this pass (no Companies House or press check) | **Gap.** Earlier brief lists it as weak. Gymshark is private; no filing exists to check. |
| Nogin | Shopify Plus press release (Seychelles Imports, via marketscreener) | Nogin is a Shopify Plus service partner, not a store that publishes revenue. **Excluded.** |
| Shopify Inc. | FY2024 and FY2025 10-K | Platform vendor, not a store. **Excluded.** |

## Tranco check

Not done. No domain above has a Tranco rank. Rows 2 to 5 and the Grove domain are unverified.

## Summary

1. Entries with a filing that says the store runs on Shopify (strong): **0**.
2. Entries with a filing that says the company is moving to Shopify (partial): **1** (Grove Collaborative, with USD revenue FY2025 $173.7M, FY2024 $203.4M).
3. Entries from Shopify-published case studies with no USD totals, periods or domains (weak): **4** (Transformer Table, Memobottle, Bydee, Desmond & Dempsey, the last from its headline only).
4. Checked with no Shopify evidence (not found): **5** (Solo Brands, Digital Brands Group, Kidpik, Lovesac, Lulu's), plus Honest (weak).
5. Target of 10 usable entries is **not met**. The owner should run the EDGAR full-text search in a browser, add a Companies House pass for UK brands, and check Tranco ranks before this set is used as ground truth.

## Sources

1. Grove Collaborative FY2025 10-K, https://www.sec.gov/Archives/edgar/data/1841761/000184176126000010/grov-20251231.htm (revenue figures via search excerpt; fetch truncated before financials)
2. Grove Collaborative FY2024 10-K, https://www.sec.gov/Archives/edgar/data/1841761/000162828025013839/grov-20241231.htm (Shopify quotes verified by fetch; migration start date not found in visible text)
3. Grove Collaborative FY2024 ARS (search excerpt only), https://www.sec.gov/Archives/edgar/data/1841761/000162828025020645/grovecollaborativeholdings.pdf
4. Grove Announces Fourth Quarter and Full Year 2025 Financial Results, Business Wire, 2026-03-05, https://www.businesswire.com/news/home/20260305220738/en/grove-announces-fourth-quarter-and-full-year-2025-financial-results
5. Transformer Table case study (Shopify-published), https://www.casestudies.com/company/shopify-plus/case-study/transformer-table-scales-to-over-100-million-after-moving-to-shopify-plus
6. Memobottle case study (Shopify-published), https://www.casestudies.com/company/shopify-plus/case-study/memobottle-grows-global-revenue-by-310-with-shopify-plus
7. Bydee case study (Shopify-published), https://www.casestudies.com/company/shopify/case-study/bydee-grows-global-sales-by-189-with-international-selling-tools-on-the-shopify-plus-plan
8. Desmond & Dempsey case study (headline only), https://www.casestudies.com/company/shopify-plus/case-study/after-reclaiming-sunday-mornings-desmond-dempseys-growth-surged-250
9. Solo Brands FY2025 10-K, https://www.sec.gov/Archives/edgar/data/1870600/000187060026000013/dtc-20251231.htm (truncated read)
10. Digital Brands Group FY2025 10-K, https://www.sec.gov/Archives/edgar/data/0001668010/000149315226016851/form10-k.htm (search excerpt)
11. Kidpik FY2023 10-K, https://www.sec.gov/Archives/edgar/data/1861522/000149315224014214/form10-k.htm (search excerpt)
12. Honest Company FY2025 10-K, https://www.sec.gov/Archives/edgar/data/1530979/000162828026011634/hnst-20251231.htm (search excerpt)
13. Nogin / Seychelles Imports press release, https://ca.marketscreener.com/quote/stock/NOGIN-INC-143061013/news/Nogin-Announces-Agreement-with-Seychelles-Imports-LLC-to-Plug-Into-Nogin-s-Intelligent-Commerce-Te-43011656
14. SEC EDGAR full-text search (blocked, HTTP 403 to automated request), https://efts.sec.gov/LATEST/search-index
