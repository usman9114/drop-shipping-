# 24. Traffic calibration and public revenue for Shopify stores

Status: research report, 2026-11-04. Market: US (prices USD unless stated). Owner question: can we calibrate a revenue model (revenue = visits x conversion x AOV) against stores that publish revenue, and where do traffic estimates come from?

## Answer first

- **Rank to visits: no published mapping was found.** Tranco, CrUX and Cloudflare Radar publish ranks or buckets, not visits. The only rank-to-traffic evidence is academic (Zipf-type fits) and is either old (2004) or secondary. Any visit figure we derive from a rank is an [estimate].
- **Calibration set: target of 10 not met.** Three companies have fiscal-year revenue plus a Shopify link we could check (Allbirds, BARK, Gymshark, with caveats). Four more have Shopify case-study revenue with no fiscal year (Bombas, Studio McGee, Transformer Table, Scalpers digital revenue). Honest Company is a partial fit. The gap is structural: few public or filing companies name Shopify as their store platform.
- **Store-level sales estimators: none piloted.** StoreLeads has an official API page, but its pricing, free tier and API terms are conflicting or unverified. Similarweb's terms page did not load. Semrush prices conflict across sources. We did not create accounts (CLAUDE.md, principle 7 requires owner approval).
- **Tranco was downloaded and sampled.** The daily top-1m file is in the session scratchpad (outside the repo). Its licence is not stated on the methodology page, so the terms gate applies before any ingestion.
- **Recommended next step:** run an EDGAR full-text search for "run on Shopify" and "Shopify" in 10-K/S-1 filings (manual, owner-approved), and ask the owner whether a paid StoreLeads or Semrush trial is acceptable for a 20-store pilot.

---

## Part A. Turning a popularity rank into monthly visits

### A1. What each ranking publishes

| Source | Unit | What it measures | Granularity published | Ordering | Freshness | Licence / terms (as read) | Rate limit (as read) | Source |
|---|---|---|---|---|---|---|---|---|
| Tranco (tranco-list.eu) | Registrable domain | Average of 5 providers over 30 days (CrUX, Cloudflare Radar, Farsight, Majestic, Cisco Umbrella). Alexa and Quantcast deprecated. | Full 1M list, Dowdall-scored | Ordered | Daily file exists; the methodology page gives a 30-day window | **Not stated** on methodology page [primary, read 2026-11-04] | None (static file) | [1] |
| CrUX rank magnitude | Origin (scheme+host+port) | Chrome users only; popularity bucket | Buckets: Feb 2021 = 1k, 10k, 100k, 1M, 10M; Oct 2022 added half-steps (1k, 5k, 10k, 50k, 100k, 500k, 1M, 5M, 10M, 50M) | Bucket only, not ordered within a bucket | Monthly, second Tuesday of following month (BigQuery docs, search snippet) | Licence not read this session [unverified]; BigQuery billing applies | Not read this session | [2], [33] |
| Cloudflare Radar domain ranking | Domain, DNS queries to 1.1.1.1 (method per search snippet [secondary]) | DNS popularity, not web visits | Ordered top 100 (daily, last 24h); buckets 200, 500, 1k, 2k, 5k, 10k, 20k, 50k, 100k, 200k, 500k, 1M (weekly, last 7 days) | Top 100 ordered only | Daily (top 100), weekly (buckets) | **Page states no licence or terms** [primary, read 2026-11-04] | **Page states no rate limits**; bearer token required | [3] |

Notes:
- Tranco's own page is internally inconsistent: it says the standard configuration uses five providers in one place and "all four providers" in another. Treat the five-provider list as the current statement [primary].
- CrUX buckets are magnitudes, not positions. A domain in the "top 10k" bucket could be rank 1 through 10,000. This matters for calibration: bucket width is 10x at the top and 2x or 5x in half-steps.
- Cloudflare bucket sizes are on the page, but the order inside each bucket is not published.
- None of the three measures visits. All three rank popularity signals that are then blended or sampled.

### A2. Any published rank-to-visits mapping

| Item | Type | Date | Value | Source | Status |
|---|---|---|---|---|---|
| Zipf-like fit of website popularity by rank | Academic fit (2004 data) | arXiv 2004 (cs/0404010) | Exponent alpha = 1.02 +/- 0.05 over the middle rank range. Plain Zipf fails at the top and tail; the paper proposes a modified law with two extra parameters. | [6] (search snippet, not fetched) | [data] for its dataset; 2004 data, not current |
| "Top-ranked site gets about 9x the visitors of the 100th" | Course-note rule of thumb | undated (course page, Berkeley i202 f11) | rank 1 : rank 100 = 9 : 1 | [5] (search snippet) | [secondary] **Internal conflict:** a 9x gap between rank 1 and rank 100 implies a slope of log10(9)/log10(100) = 0.48, not the -1 Zipf slope in [6]. Do not use either without checking. |
| Power-law extrapolation of total web traffic | Recent paper, uses SimilarWeb site data | arXiv 2404.17095, v1 26 Apr 2024, v2 23 Oct 2024 | Covers over 250,000 sites; top 116 domains estimated at about one-third of total web traffic. Fitted parameters not shown in the fetched text. | [4] (fetched abstract page) | [secondary] for traffic values; the paper's rank model is not in the abstract |
| Visits for one Shopify brand | Third-party estimate | Undated, EcomScout page | solostove.com about 4.2M visits/year, said to be based on SimilarWeb data plus proprietary algorithm | [21] (search snippet) | [estimate], third-party, not verified |

What this means for us:
- No source gives a rank-to-visits function we can cite for 2026. The 2024 paper's method is the closest to a usable model, but its fit is not in the abstract and it uses one vendor's data (SimilarWeb) as ground truth.
- A pilot is possible without new data: once we have 20 or more stores with known or estimated visits and a Tranco or CrUX rank, we can fit log(visits) against log(rank) ourselves. We should fit separately per rank band, since the curve is not a straight line at the extremes [6].
- Any visit number we produce from rank alone is an [estimate] with a wide band. Do not present it as sales or traffic data (principle 2).

---

## Part B. Calibration set: Shopify stores with published revenue

Rule applied: revenue must be stated for a fiscal year, with a source URL. Shopify status needs evidence: a filing sentence, a Shopify case study or press, or a third-party profile (marked as weaker). Tranco ranks are from the file downloaded 2026-11-04 (domain-level; the file's list date is not recorded in the file, so treat as [unverified] date).

### B1. Candidates that meet the revenue and Shopify tests (partly)

| # | Brand | Domain | Tranco rank (2026-11-04 file) | Fiscal year | Revenue (USD unless stated) | Revenue source (URL) | Shopify evidence (URL) | Shopify strength | Store-level or company-level? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Allbirds (NASDAQ: BIRD) | allbirds.com | 68,384 | FY2024 (to 31 Dec 2024) | $189.8M net revenue (FY2023: $254.1M) | Press release 11 Mar 2025 [8]; 10-K [7] | 10-K Item 1 (FY2024): "rely on partners, such as Shopify, to more effectively scale" [7]; Shopify Plus customer story, omnichannel [9] | Partial primary (partner mention) + vendor case | Company-level (DTC is a subset; split not read) |
| 2 | BARK, Inc. (NYSE: BARK) | bark.co | 48,717 | FY2025 (to 31 Mar 2025) | Total revenue $484.2M (secondary summary of 10-K); DTC $415.8M; Commerce $68.3M [10 via search, verify in filing] | 10-K [10] | 10-K Item 1: "bark.co domain, which is run on Shopify"; "migrated to Shopify" in fiscal 2025 [10] | **Strong primary** (direct statement in filing) | Company-level; DTC segment available |
| 3 | Gymshark (private, UK) | gymshark.com | 21,451 | FY to 31 Jul 2024 | GBP 607.3M (FY to 31 Jul 2023: GBP 556.2M); US GBP 251.0M [11, press coverage of Companies House accounts] | Companies House accounts [secondary via press, 25 Apr 2025] | Shopify case study: left Adobe Commerce for Shopify Plus; "GBP 41M in sales during 2017" [12]; trade article 2017 confirms platform switch [13] | Vendor + trade press; no filing | Company-level; the 2017 figure is vendor-stated |
| 4 | The Honest Company (NASDAQ: HNST) | honest.com | 62,633 | FY2025 (to 31 Dec 2025) | Net revenue $371.3M (FY2024: $378.3M) [14, via search snippet of 10-K] | 10-K [14] | Only EcomScout lists Shopify [15] [unverified]; 10-K/shareholder letter says the company exited DTC fulfillment on honest.com (secondary summary) | **Weak / unverified** | Company-level; not store-level: DTC on honest.com reduced |

### B2. Shopify case-study revenue without a usable fiscal year (vendor-stated)

| Brand | Domain | Tranco rank | Revenue claim | Year | Source | Private/public | Use |
|---|---|---|---|---|---|---|---|
| Bombas | bombas.com | 47,245 | About $50M annual sales; ~300% growth; $17.2M in first full year after replatform | Year not stated; $50M tied to a 2018 holiday period in the search summary | [16], [17] | Private | Weak: vendor claim, no year, growth figure unclear |
| Studio McGee | studiomcgee.com | not in top 1M | $100M+ consolidated revenue; >1M orders across McGee & Co. | Year not stated | [18] | Private | Cannot use (not in Tranco top 1M) |
| Transformer Table | transformertable.com | 337,251 | "Over $100M annual sales" | Year not stated | [19] | Private | Out of rank target (>300k) |
| Scalpers | (not checked) | not checked | Digital revenue EUR 4M to EUR 40M after moving to Shopify | Year not stated; digital channel only | Shopify case study via search summary [not fetched] | Private | Channel-only, not usable as store total |

### B3. Candidates excluded

| Brand | Domain | Tranco rank | Why excluded | Source |
|---|---|---|---|---|
| Solo Stove / Solo Brands (NYSE: DTC) | solostove.com | 114,014 | Platform unresolved: EcomScout says Shopify [21]; a vendor case study says BigCommerce [22]. FY2025 10-K does not name a platform in the read portion [20]. DTC was 63.5% of FY2025 sales [20]. Net sales not read. | [20], [21], [22] |
| Kylie Cosmetics | kyliecosmetics.com | 110,737 | Shopify Plus per a secondary blog [unverified]; no standalone revenue disclosed (inside Coty) | not fetched |
| Grove Collaborative (NYSE: GROV) | grove.co | 86,408 | FY2025 net revenue $173.7M [23]. 10-K says it moved its legacy homegrown platform to third-party providers, no vendor named in the read portion. No Shopify evidence. | [23] |
| Lulu's Fashion Lounge (NASDAQ: LVLU) | lulus.com | 25,097 | Shopify case studies are for other brands (Lulu and Georgia). No platform mention in 10-K excerpts read. | searched; no evidence |
| Jones Soda | jonessoda.com (not checked) | not checked | 10-K excerpts read contain no platform mention; only cover pages retrieved. | searched; no evidence |
| The Real Good Food Co. | realgoodfoods.com | not checked | 10-K excerpts read do not mention Shopify; not in our target | searched; no evidence |
| Digital Brands Group | (not checked) | not in top 1M | No Shopify mention in excerpts read | searched; no evidence |
| Smart for Life | (not checked) | not checked | No Shopify mention in search results; revenue conflicting (FY2022 $17.8M press vs $15.9M secondary) | searched; no evidence |
| Mama's Creations (MamaMancini's) | mamamancinis.com (not checked) | not checked | FY2025 revenue $123.3M (company-level); no channel split; Shopify not confirmed | searched; no evidence |
| FIGS | (not checked) | not in top 1M | FY2025 net revenue $631.1M [10-K via search]; DTC platform described, vendor not named in read portion | searched; no evidence |
| Mustang Survival | (not checked) | not checked | Shopify case study (migrated from Salesforce Commerce Cloud); no revenue figure in the case | [search snippet] |
| Giesswein, Stio, Libas, Buildmat, Who Gives a Crap | various | not checked | Shopify case or trade piece; no fiscal-year revenue, or channel-only | [search snippets] |

### B4. What the set can and cannot do

- **Usable for a first calibration test (strict):** BARK (filing-verified Shopify, FY2025 revenue) and Allbirds (filing-partner mention, FY2024 revenue). Both are company-level. Neither gives store-level visits in our sources.
- **Usable with caveats:** Gymshark (vendor-stated Shopify history, UK accounts via press). The revenue is for an international business, so only a share is US store traffic.
- **Not usable for conversion or AOV:** none of the sources give orders, traffic or conversion for the same fiscal year. Bombas gives a 2018 sales level only. Without visits and orders from a same-period source, the test checks only the revenue scale, not the estimator's inputs.
- **Shopify confirmation is the weakest link.** Shopify does not publish merchant-level revenue in the sources we read. Its FY2025 revenue (about $11.56B, up 30%, [24], [25]) is platform revenue, not a merchant benchmark. We did not read Shopify's full 10-K for a merchant list.

Routes to 10 or more (not yet tried):
- EDGAR full-text search (efts.sec.gov, public) for 10-K/S-1 text: "run on Shopify", "built on Shopify", "Shopify Plus". Manual only. The search tool we have does not index EDGAR text well.
- UK Companies House accounts for Shopify-run UK brands (accounts give turnover; platform needs a site check or a case study).
- Shopify Plus customer pages with dated revenue (case studies are vendor-stated; date each one).

---

## Part C. Free or cheap sources of store-level sales estimates

No tool was piloted with an account. Prices and limits below come from search snippets unless marked otherwise. Terms were not confirmed for any tool in this section.

| Tool | What it claims | Free tier | Paid price (US) | API | Automated-use terms | Pilot result | Source |
|---|---|---|---|---|---|---|---|
| StoreLeads | Shopify and other platform store database with sales-type estimates (exact claim not read) | Conflicting: one aggregator says a free trial exists; a competitor says a demo is required and no free tier. Not confirmed. | Third-party: Premium $75/mo, Pro $250/mo, Elite $450/mo, Enterprise $950/mo (subject to change) [unverified] | Official docs: REST API, key from Account > API tab, only on plans with API access; rate limit 5 req/s on Pro and Elite [primary-page snippet, not fetched in full] | **Not found.** The storeleads.app pricing page returned 404 in our fetch. | Not run | [26], [27], [28] |
| Similarweb | Traffic and visit estimates for sites (the basis of several other tools' estimates) | Public site summaries, limits not read [unverified] | Not checked | Not checked | **Terms page fetch returned 404.** Automated access terms unknown. Do not scrape without reading terms (principle 6). | Not run | [28] |
| Semrush | Traffic analytics (Trends add-on) and SEO data | Free account: 10 analytics requests/day, 1 website, 10 keywords (one source) or 10 searches/day (another) [conflicting, secondary] [29] | Pro about $130-140/mo; Guru about $250/mo; Business about $500/mo; Trends add-on $200-289/mo (conflicting) [secondary] [29] | Not checked | Not read | Not run | [29] |
| EcomScout | Store profiles: platform, traffic estimate (solostove.com about 4.2M visits/yr, SimilarWeb-based), reviews | Not checked | Not checked | Not checked | Not read | Looked up 2 domains via search snippet only | [15], [21] |
| TrendTrack | Top Shopify store lists with estimated revenue ranges (e.g. one store $80.4M-$242.4M) | Not checked | Not checked | Not checked | Not read | Not run; estimate is secondary | [31] |
| Tranco top-1m file | Popularity rank only (domain) | Free download | Free | Static file | **Licence not stated** on methodology page [1] | Downloaded and joined to 40 candidate domains, 2026-11-04 | [1], [33] |

Notes:
- Every paid estimator is a modelled guess. Under CLAUDE.md principle 2, any paid revenue estimator needs owner approval before use.
- Pricing pages for StoreLeads, Similarweb and Semrush were not reliable in our search. Re-check on the vendor sites before any spend.
- Tranco lookup pilot: rank data for 40 domains (examples: gymshark.com 21,451; bombas.com 47,245; bark.co 48,717; allbirds.com 68,384; honest.com 62,633; grove.co 86,408; solostove.com 114,014; kyliecosmetics.com 110,737; transformertable.com 337,251). Lookup file is in the session scratchpad, not in the repo. Several candidate domains (chubbies.com, figs.com, sowgood.com, stran.com, digitalbrandsgroup.com, studiomcgee.com) are not in the top 1M file.

---

## Gaps and unverified items

- No rank-to-visits coefficient for Similarweb, Alexa or Tranco was found. The Zipf exponent (1.02) is from 2004 data for the middle ranks only [6].
- Tranco list date for the downloaded file is not recorded in the file. Treat its date as unverified.
- CrUX licence and BigQuery cost were not read this session.
- Cloudflare Radar API rate limits: none stated on the domain-ranking page [3]. Check the API rate-limit page before use (not read).
- Similarweb and StoreLeads terms pages were not readable; no automated-access permission is established.
- Shopify store status for Solo Stove, Honest, Kylie Cosmetics and Gymshark rests on third-party or vendor sources.
- Revenue figures for Gymshark, BARK (total revenue) and Honest come from secondary summaries of filings. Verify against the filing before use.

---

## How we would use these

1. Use BARK (FY2025, filing-verified Shopify) and Allbirds (FY2024, filing-partner mention) as the first two calibration points, and label them company-level, not store-level.
2. Do not fit a rank-to-visits curve yet. Fit it only after we have at least 20 stores with dated visit estimates from a source whose terms we have read.
3. Pull Tranco and CrUX ranks for our candidate stores as a free popularity band (per-decade bucket), recorded as [proxy], never as traffic.
4. Keep store-level sales estimators on hold until the owner approves a trial and their terms are read (principles 6 and 7).
5. Search EDGAR full text for "run on Shopify" to widen the calibration set beyond 3; if fewer than 10 public or filing companies name Shopify, use dated vendor case studies only as a labelled, lower-weight tier.

---

## Sources

1. Tranco methodology, tranco-list.eu, read 2026-11-04: https://tranco-list.eu/methodology
2. Chrome for Developers, "CrUX rank magnitude" blog, Feb 2021 and Oct 2022 datasets: https://developer.chrome.com/blog/crux-rank-magnitude
3. Cloudflare Radar, domain ranking datasets, read 2026-11-04: https://developers.cloudflare.com/radar/investigate/domain-ranking-datasets/
4. Xavier, H.S., "The Web unpacked: a quantitative analysis of global Web usage", arXiv:2404.17095, v1 26 Apr 2024, v2 23 Oct 2024: https://arxiv.org/abs/2404.17095
5. UC Berkeley I202 course note, "Power Laws: What do the Top 100 Visited Sites of the Internet Reveal?" (search snippet, not fetched): https://courses.ischool.berkeley.edu/i202/f11/node/740
6. Krashakov et al., "On the universality of rank distributions of website popularity", arXiv cs/0404010 (search snippet, not fetched): https://arxiv.org/abs/cs/0404010
7. Allbirds, Inc., Form 10-K FY2024 (filed 2025), SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1653909/000162828025012130/bird-20241231.htm
8. Allbirds, "Reports Fourth Quarter and Full Year 2024 Financial Results", 11 Mar 2025: https://allbirds.gcs-web.com/news-releases/news-release-details/allbirds-reports-fourth-quarter-and-full-year-2024-financial
9. Shopify Plus customer story, Allbirds (omnichannel): https://shopify.com.au/plus/customers/allbirds
10. Bark, Inc., Form 10-K FYE 31 Mar 2025, SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1819574/000181957425000024/bark-20250331.htm
11. FashionUnited, "Gymshark hits record revenue in FY24, yet profit continues to fall", 29 Apr 2025 (reports Companies House accounts): https://fashionunited.uk/news/business/gymshark-hits-record-revenue-in-fy24-yet-profit-continues-to-fall/2025042981343
12. Shopify case study, Gymshark (Adobe Commerce to Shopify Plus; GBP 41M in 2017 per vendor): https://www.shopify.com/case-studies/gymshark
13. Retail Technology, "Case study: Fit for Business" (Gymshark, Shopify Plus with Peoplevox, 2017): https://retailtechnology.co.uk/news/6471/case-study:-fit-for-business/
14. The Honest Company, Inc., Form 10-K FY2025, SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1530979/000162828026011634/hnst-20251231.htm
15. EcomScout, store profile honest.com (third-party): https://ecomscout.com/stores/honest.com
16. Shopify, "Ecommerce scalability: Bombas" blog: https://www.shopify.com/enterprise/blog/ecommerce-scalability-bombas
17. casestudies.com summary, "Bombas achieves $50M in annual sales and 300% growth with Shopify Plus": https://www.casestudies.com/company/shopify/case-study/black-friday-scalability-allowed-bombas-to-hit-50m-in-annual-sales-grow-300
18. Shopify case study, Studio McGee: https://www.shopify.com/de/case-studies/studio-mcgee
19. casestudies.com, "Transformer Table scales to over $100 million with Shopify Plus": https://www.casestudies.com/company/shopify-plus/case-study/transformer-table-scales-to-over-100-million-after-moving-to-shopify-plus
20. Solo Brands, Inc., Form 10-K FY2025, SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1870600/000187060026000013/dtc-20251231.htm
21. EcomScout, store profile solostove.com (third-party; says Shopify, about 4.2M visits/yr): https://ecomscout.com/stores/solostove.com
22. casestudies.com, Solo Stove with BigCommerce (vendor): https://www.casestudies.com/company/bigcommerce/case-study/solo-stove-cooks-up-big-growth-with-bigcommerce
23. Grove Collaborative Holdings, Inc., Form 10-K FY2025, SEC EDGAR: https://www.sec.gov/Archives/edgar/data/1841761/000184176126000010/grov-20251231.htm
24. Digital Commerce 360, "Shopify revenue GMV Q4 2025", 17 Feb 2026 (secondary): https://www.digitalcommerce360.com/2026/02/17/shopify-revenue-gmv-q4-2025/
25. Shopify Inc., Form 10-K FY2025 (search result, not fetched): https://www.sec.gov/Archives/edgar/data/1594805/000159480526000007/shop-20251231.htm
26. StoreLeads API page (search result, not fetched): https://storeleads.app/api
27. SyncGTM, "Store Leads Review 2026" (third-party, pricing): https://syncgtm.com/blog/store-leads-review-2026
28. Similarweb terms of use (fetch returned 404; not read): https://www.similarweb.com/terms-of-use/ ; StoreLeads pricing page (fetch returned 404; not read): https://www.storeleads.app/pricing
29. Semrush pricing, third-party summaries (conflicting): https://www.seo.com/blog/semrush-pricing/ and https://costbench.com/software/ai-seo-tools/semrush-ai/free-plan/
30. Tranco daily top-1m file, downloaded 2026-11-04 (SHA-256 3d0523926f93a88e501ebd1899566307eed2cced3f7c96e51167c8b7fc3a14df, 1,000,000 rows, stored in session scratchpad): https://tranco-list.eu/download/daily/top-1m.csv.zip
31. TrendTrack, "Top Shopify stores by revenue in 2025" (estimated ranges, third-party): https://trendtrack.io/blog-post/top-shopify-stores-by-revenue
32. Alphastreet, "Shopify Q4 2025 earnings results", 11 Feb 2026 (secondary): https://news.alphastreet.com/shopify-q4-2025-earnings-results/amp
33. CrUX on BigQuery, developer docs (search snippet; monthly release and table layout): https://developer.chrome.com/docs/crux/bigquery
