# 16 — Trend and demand sources (US): what we can legitimately ingest

> `market-researcher` (Haiku), 2026-11-03. **[P]** = official page fetched. **[S]** = secondary or vendor. **[unverified]** = conflicting or unconfirmed. Reddit, Etsy and Wikimedia docs pages were unreachable. **No source in this run explicitly bans caching, but most storage terms were not found. Treat every row as restricted until its terms page is read.**

## Verdict by platform

| Platform | Can we use it? | Why |
|---|---|---|
| **TikTok** | Manual reading only for now | Creative Center has no API and the ToS bars automated collection [S]. The Research API is **non-profit academic research only**, commercial users excluded [P]. A licensed dashboard (Kalodata, FastMoss) is the only legitimate machine path, and API access is Enterprise-only or unconfirmed [S]. |
| **Instagram / Meta** | Yes, but narrow | Hashtag search is official and free, but limited to **30 unique hashtags per 7 days** per account, and needs App Review [P]. Meta Content Library is non-commercial research only [P]. The wife's own account insights are a separate, free feed. |
| **Pinterest** | Unclear | Trends API v5 exists (US top/growing keywords, today only, no history) but is aimed at agencies and partners [P]. Approval is unclear. |
| **Reddit** | Probably not worth it | Free only for non-commercial use; commercial reportedly needs a paid contract [S, unverified]. |
| **Amazon** | Only via licensed APIs | Keepa or Rainforest. Scraping is not an option. |

## Sources, ranked by value / cost / legal safety

| Rank | Source | Signal | Cost | Notes |
|---|---|---|---|---|
| 1 | **YouTube Data API v3** | video counts and views per product phrase | free, 10,000 units/day [P] | `search.list` cost conflicts: the Google table fetched says 1 unit, every secondary source says 100. Check the Cloud Console before budgeting. |
| 2 | **DataForSEO Google Trends** | search-interest curves | $0.0027 per standard task, up to 5 keywords [P] (about $2.70 per 1,000 tasks) | Licensed. Better than the archived pytrends for scheduled CI jobs. |
| 2b | SerpApi Google Trends | same | free 250/month, then $25 per 1,000 [P] | Free tier is enough to start. |
| 3 | **Instagram hashtag search** | hashtag volume and posts | free, needs App Review [P] | 30 hashtags/week; pick them from the shortlist only. |
| 4 | Keepa Best Sellers | Amazon demand proxy | token-based, about €49–129/month [S] | 50 tokens per Best Sellers call; 60 tokens/min [P] |
| 5 | Wikimedia Pageviews | article interest | free, no key [S] | weak product signal; data license unconfirmed |
| — | Google Trends official API | search interest | alpha, gated, small pilot [S] | apply anyway |
| — | Exploding Topics API | curated trends | from $249/month [P] | no custom keyword lookups via API [P]. Skip. |

## Storage and use constraints found

- **Meta Content Library:** research use only, no publication of personal data [P].
- **TikTok Research API:** approved non-profit projects only [P].
- **TikTok Creative Center:** ToS restricts automated collection [S].
- Everything else: not found. Each ingester's registry entry must record the terms page and the date it was read **before** the first load.

## Implications for the warehouse

- Keep **social data aggregated** (term × platform × week counts), not raw posts. This is smaller and avoids storing personal content.
- Start with Trends (existing) plus **YouTube** and **SerpApi/DataForSEO** as the stable, licensed feeds. Add Instagram hashtags for the shortlist.
- TikTok signals enter manually (screenshot or note in `meta.manual_observation`, trust = `secondary`) until a licensed API is justified.

## Sources
1. https://ads.tiktok.com/help/article/creative-center?lang=en
2. https://developers.tiktok.com/docs/en/research-api-faq
3. https://conductatlas.com/platform/tiktok/tiktok-terms-of-service/prohibition-on-scraping-and-data-extraction/ [S]
4. https://truto.one/integrations/detail/tiktokshoppartner/ [S]
5. https://www.socialcrawl.dev/blog/best-tiktok-shop-apis-2026 [S]
6. https://creatify.ai/pt/blog/kalodata-pricing-plans-and-what-you-ll-actually-pay-in-2026 [S]
7. https://getpulsesignal.com/pricing/fastmoss [S]
8. https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-facebook-login/hashtag-search
9. https://developers.facebook.com/docs/content-library-and-api/get-access
10. https://developers.pinterest.com/docs/analytics-and-reports/trends/
11. https://www.techloy.com/reddit-api-pricing-in-2026-complete-guide-for-developers-and-businesses/ [S]
12. https://developers.google.com/youtube/v3/determine_quota_cost
13. https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/getting-started.html [S]
14. https://developers.google.com/search/blog/2025/07/trends-api
15. https://www.serpapi.com/pricing
16. https://dataforseo.com/pricing/keywords-data/google-trends
17. https://explodingtopics.com/blog/exploding-topics-api
18. https://keepa.com/api-docs/plans-tokens.html ; https://revenuegeeks.com/keepa-pricing/ [S]
19. https://www.socialcrawl.dev/blog/best-amazon-product-data-apis-2026 [S]
