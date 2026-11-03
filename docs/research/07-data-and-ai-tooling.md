# 07 — Data sources and free AI tooling

> Researched 2026-11-03 by `market-researcher` (Haiku). The eBay developer pages and Amazon's help pages returned 403/503, so those claims rest on search snippets **[unverified]**. The OpenRouter and Real-ESRGAN claims were fetched directly.
>
> **[data]** = tested from our environment on 2026-11-03.

## 1. Google Trends

| Option | Status |
|---|---|
| **Official Google Trends API (alpha)** | Access by application only, in rolling batches. Rolling 1,800-day window; relative values. No public quota published. Apply: https://developers.google.com/search/apis/trends |
| **pytrends** (unofficial) | Repo reportedly archived in April 2025, with 429s common **[unverified]**. **[data]** A US 12-month pull for "dog harness" succeeded from our environment on 2026-11-03. |

`scout.trends` uses pytrends with caching and backoff. We should also apply for the official alpha.

## 2. eBay Browse API

- **[data]** `api.ebay.com` returned **403 from Akamai** to a request without a token on 2026-11-03. We need to recheck with an OAuth token before concluding that this environment can reach eBay.
- **Application token:**
  - Client-credentials grant.
  - The token endpoint allows **1,000 tokens/day**; tokens last about 2 hours **[unverified]**.
- **Quota:**
  - Browse is ~5,000 calls/day, which is **[unverified]**.
  - Check the real quota with `GET /developer/analytics/v1/rate_limit`.
- **Competition proxy:**
  - `fieldgroups=ASPECT_REFINEMENTS,CATEGORY_REFINEMENTS` returns `aspectDistributions[].matchCount` and `categoryDistributions`.
  - The response also has a top-level `total` (listing count) **[unverified]**.
- **Price proxy:** min, median and max from item summaries. These are sample-based (one page of results, not the whole market).

## 3. Other free US demand signals

| Source | Access | Use |
|---|---|---|
| Google Keyword Planner | Free with a Google Ads account, no ad spend needed | Absolute search-volume ranges |
| Pinterest Trends | Free business account | Home, decor and seasonal interest |
| TikTok Creative Center | Free; may need a business account | Viral product signals |
| Amazon Best Sellers / Movers & Shakers | **Manual browsing only.** Amazon's Conditions of Use prohibit scraping. | Sanity check |

## 4. OpenRouter free models (fetched: https://openrouter.ai/docs/limits)

- `:free` models are limited to **20 requests/min**.
- Daily cap:
  - **50 requests/day** if the account has bought less than $10 of credits in total.
  - **1,000 requests/day** once lifetime purchases reach **$10**. This is a one-time purchase; the credits aren't spent by free calls.
- The limits apply per account, not per key. A negative balance causes errors.
- **Privacy:** providers set their own logging and training policies. **Treat free routes as non-private.** Never send keys, customer data or supplier contracts.
- **Fallback:** use the `models` array in the request, or retry a 429 on a different `:free` model. Each model has its own rate limit.

**[data]** As of 2026-11-03, 14 `:free` models are available. None outputs images.

| Use | Free models |
|---|---|
| Vision (image QA, image→attributes) | `nvidia/nemotron-3.5-super-vl:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `google/gemma-4-31b-it:free`, `google/gemma-4-26b-a4b-it:free` |
| Heavy text reasoning | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| Fast bulk text | `nvidia/nemotron-3.5-lightning:free`, `liquid/lfm-2.5-2.6b:free` |
| Content safety | `nvidia/nemotron-3.5-content-safety:free` |

## 5. Image tools (for Phase 1)

| Tool | License | Commercial use? |
|---|---|---|
| **BiRefNet** | MIT **[unverified]** | Yes (preferred) |
| rembg | MIT wrapper; **each model has its own license** | Depends on the model |
| **BRIA RMBG-2.0** | CC BY-NC 4.0 | **No.** Needs a paid BRIA license. **Do not use.** |
| Real-ESRGAN | BSD-3-Clause (fetched). Check the weights' license separately. | Yes |

All of these run on CPU, slowly at high resolution.

## Sources
- https://developers.google.com/search/blog/2025/07/trends-api
- https://developers.google.com/search/apis/trends
- https://pypi.org/project/trendreq/ (vendor)
- https://developer.ebay.com/api-docs/static/oauth-rate-limits.html (snippet)
- https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search (snippet)
- https://developer.ebay.com/api-docs/developer/analytics/resources/rate_limit/methods/getRateLimits (snippet)
- https://openrouter.ai/docs/limits (fetched)
- https://openrouter.ai/docs/guides/privacy/provider-logging
- https://www.truefoundry.com/blog/openrouter-free-models-whats-actually-free-and-what-it-costs-you (third-party)
- https://github.com/xinntao/Real-ESRGAN (fetched)
- https://huggingface.co/briaai/RMBG-2.0
- https://ice-ice-bear.github.io/posts/2026-04-15-birefnet/ (blog)
- https://ads.tiktok.com/help/article/creative-center
- https://www.tailwindapp.com/pinterest-marketing/course/pinterest-trends
