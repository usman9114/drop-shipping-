# 32b. TikTok ads: official routes to see other advertisers' ads

Researched 2026-11-05. Question: can we automatically see which TikTok ads ~17 US-focused Shopify brands run, using only official routes?
Tags: [primary] = fetched from a TikTok page today; [secondary] = third-party; **[unverified]** = not confirmed on an official page.

## Short answer

No official route gives automated access to US ads from other advertisers. The Commercial Content Library and API hold EU/EEA/UK/CH/TR ads only [primary], so they show at most a brand's European ads. The Creative Center has no documented API or export [unverified, absence]. US-focused brand ads stay manual.

## Table

| # | Route | Covers | Fields | Who can use it | Cost / limits | Automatable legally? |
|---|---|---|---|---|---|---|
| 1 | Commercial Content API (`open.tiktokapis.com/v2/research/adlib/ad/query/`) | "ONLY ... data from EU countries" [primary, S1]. Third-party lists 33 regions (EU27, IS, LI, NO, UK, CH, TR) and says US ads are not included [secondary, S5] | Published date, last seen date, targeting info, number of people who saw the ad; advertiser metadata; disapproved ads (selected) [primary, S1]. About 32 fields incl. creative URL, payer, reach by region/age/gender [secondary, S5] | Dev account plus application. S1 says "public and researchers can access" and requester "can be located in any country". Newsroom (2023) says researchers apply [primary, S2]. S5 claims commercial users and advertisers are "explicitly ineligible" **[unverified]** | Cost not stated [primary]. Rate limit not stated on official getting-started page [primary, S3]; "about 1,000 requests/day" and 12 ads/page are [secondary, S5] | Yes for EU ads, if approved. Our brands' US ads: no |
| 2 | TikTok Commercial Content Library (library.tiktok.com) | Europe only: "only data from Europe is available" [primary, S2]. Anyone can access [primary, S2] | Paid ads: creatives, run dates, targeting (age, gender), number of people served [primary, S2]; non-ad branded content labelled as paid partnership [primary, S2] | Public | Free. Export: none documented **[unverified]**. The page returned empty to WebFetch (JS app), so UI features not confirmed | Manual viewing only. No official export found |
| 3 | Creative Center (Top Ads etc.) | Promoted/top-performing ads, not a per-advertiser registry | n/a | Public web UI | No official API or export found **[unverified]** | Terms say no automation per owner brief; not confirmed (see notes) |
| 4 | TikTok Marketing/Business API, Research API | Own ad accounts (Marketing API). Research API = organic public content, not ads **[unverified]** | n/a | Advertisers manage their own accounts | n/a | No route to another advertiser's ads |

## Notes

### 1. Commercial Content API [primary unless tagged]
- Official page: "These APIs are made available globally and will include ads data from EU to begin with" and "we are ONLY including data from EU countries" (S1).
- Application steps (S1): create a TikTok for Developers account with an official email; complete the online application (used to validate applications); "You should hear back from us within 2 working days of submitting your complete application"; if approved, log in and find the client key.
- Retention on TikTok's side: ad data available "until one year since the advertisement was last shown to any user" (S1).
- Endpoint and parameters (S3): `POST https://open.tiktokapis.com/v2/research/adlib/ad/query/?fields=ad.id`. Filters shown: `ad_published_date_range` (min/max), `country_code_list` or `country_code` (examples inconsistent), `search_term`. No advertiser-name filter is documented. `max_count` default 10; pagination via `search_id` and `has_more`.
- Data-use, storage and sharing terms: not stated on the getting-started page or product page. Developer Terms of Service are linked from S1 but I could not read them. **Unread, so treat as "do not retain or publish" under the CLAUDE.md terms gate until the owner records them.**
- Rate limits and cost: not stated officially. Third-party: free, OAuth, soft rate limit returns HTTP 200 with plain-text body, signed video URLs expire in about 24 h [secondary, S5].
- Eligibility conflict: the official page is open ("public and researchers", any country). The 2023 newsroom says "researchers" must apply. A third-party guide claims academics and non-profits only, and that commercial users are ineligible [secondary, S5]. We are a commercial business, so **approval is uncertain; the application outcome is the only test.**

### 2. Ad Library website
- Same dataset as the API [primary, S2]: Europe only, public. The UI could not be fetched (empty page), so filters and any export button are **[unverified]**.
- TikTok says "We plan to include more advertising data from more countries in the future" (S2, 2023). No US date given. Nothing newer found.

### 3. Creative Center
- I could not retrieve the Creative Center terms text: every candidate URL returned 404 or a login stub (S6, S7). The owner brief states the terms forbid automated collection; I did **not** confirm the wording **[unverified]**.
- TikTok's general US Terms of Service reportedly bar automated extraction without written approval (Section 3.4, per press and a tracker) [secondary, S8, S9]. Same direction, still not the Creative Center text.
- No Creative Center API, bulk export or CSV found on any TikTok page searched **[unverified]**.
- Third-party scrapers (Apify actors and similar, e.g. S10) exist; out of scope, same terms problem.

### 4. Coverage for our 17 brands
- Stanley, Cupshe, xTool, Momcozy, Elegoo, Reebok, New Era: all run US-targeted ads. Those are not in the library [secondary, S5].
- What the library could show: ads these brands serve to EU/UK users. Brands with EU storefronts (Reebok, New Era, Stanley, Elegoo, xTool likely) may appear; **this is a hypothesis, not tested.** EU creatives are often the same global creatives, which is a proxy for US creative themes at best [proxy]. Not a measure of US ads, spend or sales.
- No spend, revenue or conversion data in any official route (reach and targeting only, EU).

## Recommendation (evidence-limited)

Automate legally:
- Only EU-region ads via the Commercial Content API, and only after approval and after the Developer Terms are read and recorded in `meta.source` (date, `max_retention`, license link). Until then, no retention.

Stays manual:
- Anything about US ads: look up each brand in the Creative Center by hand, and screenshot or note findings as manual research. No browser automation, no scrapers.
- Manual viewing of library.tiktok.com for a handful of brands as a cheap pilot (no automation).

Owner steps:
1. Read TikTok for Developers Terms of Service and the Commercial Content API terms; record date, retention and license link in `docs/decisions/`.
2. Create a TikTok for Developers account with a business email and submit the Commercial Content API application (S1). Be honest about the purpose (competitive research for an e-commerce business). Expect about 2 working days; refusal is possible.
3. If approved: run a pilot per CLAUDE.md principle 10 on 3 to 5 brands (e.g. Reebok, New Era, Stanley, Elegoo, xTool) with `search_term` = brand name and an EU country code. Record ads found, first/last seen dates and whether creatives match US ones, then decide.
4. Read the Creative Center terms at the footer link on the Creative Center page and record the exact automation clause. This closes the one [unverified] item the brief rests on.
5. Do not use the Marketing API or Research API for this; neither exposes other advertisers' ads [unverified, no official page says otherwise].

## Sources
1. https://developers.tiktok.com/products/commercial-content-api/ (fetched 2026-11-05) [primary]
2. https://newsroom.tiktok.com/tiktoks-research-api-and-commercial-content-library?lang=en-GB (fetched 2026-11-05; July 2023 post) [primary]
3. https://developers.tiktok.com/doc/commercial-content-api-getting-started (fetched 2026-11-05) [primary]
4. https://library.tiktok.com/ads (fetched 2026-11-05; returned empty)
5. https://dev.to/odeeb/the-tiktok-ad-library-api-a-developers-honest-guide-to-the-dsa-commercial-content-library-5446 [secondary; author sells an Apify actor, so conflicted]
6. https://ads.tiktok.com/business/en-US/terms-of-service/creative-center (404 on 2026-11-05)
7. https://ads.tiktok.com/i18n/official/policy/terms (login stub on 2026-11-05)
8. https://decrypt.co/380229/someone-scraped-5-billion-tiktok-videos-posted-data-hugging-face [secondary, general ToS 3.4]
9. https://conductatlas.com/platform/tiktok/tiktok-terms-of-service/prohibition-on-scraping-and-data-extraction/ [secondary]
10. https://apify.com/bovi/tiktok-ads-library-scraper [third-party scraper; noted only, out of scope]
