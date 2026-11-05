# 32a. Meta Ad Library API: official route for brand ad monitoring

Date: 2026-11-05. Researcher: market-researcher. Question: can we automatically see which ads ~17 US-focused Shopify brands (Stanley, Cupshe, xTool, Momcozy, Elegoo, Nanit, New Era ...) run, via Meta's official route?

Limits of this pass: facebook.com/ads/library/api and /help pages returned HTTP 403 to our fetcher, so the access steps, rate limits and API terms come from third-party pages and are **[unverified]**. Field and parameter facts come from developers.facebook.com pages (fetched and summarised by WebFetch, not read raw).

## 1. Summary table

| Question | Answer | Status | Src |
|---|---|---|---|
| Does the API return US commercial ads? | No evidence that it does. Meta describes API coverage as "ads about social issues, elections or politics, plus ads delivering to the EU and associated territories", plus branded content | [primary] | 1 |
| What does `ad_reached_countries` do? | "Ads that did not reach any location in the EU will only return if they are about social issues, elections, or politics." So a commercial ad that never reached the EU is not returned | [primary] | 2 |
| UK commercial ads? | GB is a valid country code and UK targeting/reach fields exist (`age_country_gender_reach_breakdown` covers "UK & EU"). Whether all UK commercial ads are returned is not stated on the pages read | [primary] partial; rest [unverified] | 3 |
| Search by page id or keyword | Both. `search_page_ids`: "up to ten IDs, separated by commas". `search_terms`: 100 characters or fewer | [primary] | 2 |
| `ad_type` | Default ALL; also EMPLOYMENT_ADS, FINANCIAL_PRODUCTS_AND_SERVICES_ADS, HOUSING_ADS, POLITICAL_AND_ISSUE_ADS | [primary] | 2 |
| Creative text | `ad_creative_bodies`: "text which displays in each unique ad card"; also link titles/captions/descriptions fields exist [unverified: not seen on the page read] | [primary] | 3 |
| Creative itself | `ad_snapshot_url`: "URL link which displays the archived ad" (a web page, not a media file) | [primary] | 3 |
| Start/stop dates | Fields exist (`ad_delivery_start_time`, `ad_delivery_stop_time`) [unverified: not in the excerpt read] | [unverified] | 3 |
| Impressions and spend | Ranges only, and "available only for POLITICAL_AND_ISSUE_ADS". So none for a commercial brand ad | [primary] | 3 |
| EU reach | `eu_total_reach` (int): "estimated combined ad reach for all locations inside the European Union", only for ads delivered to the EU. `age_country_gender_reach_breakdown`: demographic distribution of Accounts Center accounts reached, for UK and EU ads | [primary] | 3 |
| Other fields | `languages` (ISO 639-1), `publisher_platforms` (Facebook, Instagram ...), `page_id`, `page_name`, `currency`; targeting fields `target_ages`, `target_gender`, `target_locations` for UK/EU ads [secondary for targeting] | [primary]/[secondary] | 3, 7 |
| Landing URL | Not seen as a field. The snapshot page may show the link; extracting it from the snapshot would mean scraping a page, which is out of scope | [unverified] | - |
| Rate limits | Not documented on the pages read. The Graph API page lists error 613 as "a custom rate limit has been reached" and says to check the specific API's docs; the general app formula is "200 * Number of Users" per hour, with no statement that it applies to `ads_archive` | [primary] for 613 text; applicability [unverified] | 4 |
| Cost | No fee found for the Ad Library API itself [unverified, one vendor blog] | [unverified] | 6 |
| Data-use terms | Not read from an official page. A third-party SDK says to follow Meta Platform Terms and "Ad Library API Terms"; a vendor blog says reselling archive data or using it for ad targeting is prohibited. Whether private storage and analysis is allowed is **not confirmed** | [unverified] | 6, 8 |

## 2. Access steps (all [unverified] until the owner reads the official page)

Third-party guides agree on the shape of it. They disagree on details (whether `ads_read` or App Review is needed).

1. Facebook account of the owner, with identity and location confirmed at facebook.com/ID. This is the same check Meta uses for political advertisers. It involves an ID document. The vendor estimate is "one to three business days" (vendor claim, not Meta). [secondary: 5, 6]
2. A Meta developer account and an app at developers.facebook.com. [secondary]
3. Accept Meta's access terms for the Ad Library API. One source calls them "Authorized Access to Public Information" terms, with no standard App Review. [secondary, contradicted by another vendor that says production tokens need review]
4. Generate an access token and call `GET graph.facebook.com/<version>/ads_archive`, with `access_token` and `ad_reached_countries` both mandatory. [secondary]
5. A known failure: "Application does not have permission for this action" on `ads_archive`, usually an incomplete ID or app setup. [secondary: Meta developer community thread]

The Meta help article that should hold these steps (facebook.com/help/2405092116183307) returned only a topic summary, not the instructions.

## 3. Report, CSV and Meta Content Library

| Route | What it is | Helps us? | Src |
|---|---|---|---|
| Ad Library Report | "aggregated view" of social issue, election and political ads per country, downloadable. Available in countries that require authorisation to run such ads | No: political ads only | 1 |
| CSV downloads | Not mentioned on the Meta tools page read | No evidence | 1 |
| Meta Content Library and API | Researcher "clean room". Eligibility: lead researcher at a not-for-profit academic institution, or a non-academic not-for-profit "with a primary purpose of scientific or public interest research". Commercial users do not qualify on the stated criteria. Review takes about 2-3 weeks at the data-access centre plus 2-3 weeks at Meta; no fee in Meta's Secure Research Environment (the SOMAR enclave has fees, reported at $371/month) | **No: we are a for-profit PoC** | 5, 9 |

## 4. Practical coverage for us (plain statement)

- A brand's ads appear only if they were **delivered to at least one EU location** (or are political/issue ads, which a Shopify product brand does not run).
- **US-only advertisers show nothing.** A brand that runs ads only to US audiences is invisible to this API. That is the case for any of the 17 that do not target the EU.
- Brands that also sell in the EU (Stanley, Cupshe, xTool, Momcozy, Elegoo, Nanit are likely, **[unverified]**: we have not checked which of the 17 run EU ads) would show their EU-delivered ads: creative text, `ad_snapshot_url`, languages, platforms, `eu_total_reach`, age/gender/country reach.
- What we would see is the EU version of their advertising (EU languages, EU offers). It is a **[proxy]** for their US creative strategy, not the US ads. Reach is an EU estimate and not spend or sales. Spend and impressions are not available for these ads.
- Pilot not yet run. By our source-evaluation standard this route is a hypothesis until a 10-30 page-id test shows how many of the 17 return ads, how fresh they are, and what fields come back.

## 5. Recommendation (limited to the evidence)

Automate (legally, once the owner has read the terms):
- Official `ads_archive` calls with `search_page_ids` (10 per request), `ad_reached_countries` set to EU countries, `ad_type=ALL`, for the ~17 brands. This is the only automatable official route.
- Store the output under `data/private/` (gitignored) until the terms are read and recorded in `meta.source` (CLAUDE.md terms gate). Do not commit or publish.
- Use an existing client rather than writing one: reuse before build. A candidate is the `meta-ads-library` npm SDK (v1.0.1) or plain `requests`; not vetted, so a decision note in `docs/decisions/` comes first.

Stays manual:
- US commercial ads: owner looking at the Ad Library website by hand, no scripts, no browser automation, no third-party scrapers (Apify, SearchAPI, Metapi and similar are noted only, not used: they breach the same terms).
- Spend, impressions, landing URLs, and any estimate of US ad volume: not available from the official route.

Owner steps:
1. Read the Ad Library API terms and Meta Platform Terms on an official page you can open in a browser (our fetcher was blocked). Record date, retention rule and link; confirm whether private storage and analysis is allowed.
2. Confirm identity at facebook.com/ID (ID document; time [unverified], vendors say 1-3 business days).
3. Create a developer account and app at developers.facebook.com; generate a token.
4. Look up the 17 brands' Facebook page ids by hand (via the Ad Library site).
5. Tell us when the token exists. Then run a small pilot first: 5 brands, EU country list, record how many return ads, field coverage and rate-limit behaviour (watch for error 613).
6. Optional: ask whether a brand's page shows any EU ads by a manual search first. That costs nothing and tells you if step 2-3 are worth doing.

## Sources

1. Meta, Ad Library tools: https://transparency.meta.com/researchtools/ad-library-tools (fetched 2026-11-05)
2. Meta, Graph API `ads_archive` reference (parameters): https://developers.facebook.com/docs/graph-api/reference/ads_archive/ (fetched 2026-11-05)
3. Meta, Graph API `archived-ad` reference (fields): https://developers.facebook.com/docs/graph-api/reference/archived-ad/ (fetched 2026-11-05)
4. Meta, Graph API rate limiting: https://developers.facebook.com/docs/graph-api/overview/rate-limiting/ (fetched 2026-11-05)
5. Meta, Content Library get access: https://developers.facebook.com/docs/content-library-and-api/get-access (fetched 2026-11-05); application via Research Tools Manager; SOMAR newsletter Winter 2026: https://www.icpsr.umich.edu/sites/somar/somar-newsletter-archive/somar-newsletter-winter-2026 (search snippet only)
6. Third-party (secondary, vendors, conflicted): Zernio https://docs.zernio.com/platforms/meta-ads/ad-library ; Hookd https://www.gethookd.ai/learn/how-to-use-meta-ad-library-api-access-token-generation-documentation/ ; adsuploader https://adsuploader.com/blog/facebook-ad-library-api ; Metapi https://metapi.io/compare/facebook-ad-library-api ; SDK README https://cdn.jsdelivr.net/npm/meta-ads-library@1.0.1/README.md
7. adlibrary.com, EU DSA ad repositories (secondary): https://adlibrary.com/posts/eu-dsa-ad-repositories-developers
8. Meta developer community thread on permission error (secondary): https://developers.secure.facebook.com/community/threads/478369017924489
9. Not fetchable (HTTP 403, official, owner should open): https://www.facebook.com/ads/library/api ; Meta help article https://www.facebook.com/help/2405092116183307 (returned a summary without steps)
