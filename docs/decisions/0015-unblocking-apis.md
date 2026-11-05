# 0015 — ZenRows and ScrapingBee as a paid fallback tier

> 2026-11-05. **Owner decision:** "We need ZenRows and ScrapingBee features, all of them." This replaces the "no unblocking APIs" line in decision 0014 and `docs/plan/tool-shortlist.md`, and amends CLAUDE.md principle 6 for public store pages. Code: `scout/unblock.py`, tests `tests/test_unblock.py`.

## What is adopted

| Service | Features used | Key | Cost (vendor docs, read 2026-11-05) |
|---|---|---|---|
| **ZenRows** Universal Scraper API | `mode=auto` (picks JS rendering and premium proxy, bills only the configuration that worked), `js_render`, `premium_proxy`, `proxy_country`, `original_status` | `ZENROWS_API_KEY` (query parameter, so an environment variable, not the network-secret form) | credit weights: standard 1, JS 5, premium 10, both 25; `X-Request-Cost` header |
| **ScrapingBee** HTML API | `render_js`, `premium_proxy`, `stealth_proxy` (last resort), `country_code` | `SCRAPINGBEE_API_KEY` (sent as `Authorization: Bearer`) | render_js 5, premium 10 (25 with JS), stealth 75 per success |

Both are reused services, not home-grown (CLAUDE.md "reuse before build"); called over plain HTTP, so no new Python dependency.

## How they are used

1. **Fallback, not default.** `scout.unblock.fetch` tries our own plain request first (free). Only a blocked page (403, 429, 430, 503, or a challenge page) or a failure escalates: ZenRows, then ScrapingBee premium, then ScrapingBee stealth. In the 105-store run the plain tier already served all but one page, so spend should stay small.
2. **Budget in code.** A daily credit cap (`SCOUT_UNBLOCK_DAILY_CREDITS`, default 1,000) is counted in `data/private/unblock_usage.json`; paid tiers stop when it is reached. `python -m scout.unblock --usage` shows it.
3. **Provenance.** Every fetch records the tier that served it and the credits spent, so reports can say how a number was obtained.
4. **Kept:** robots.txt is still checked before a fetch (default; `respect_robots=False` exists for owner-approved cases); public pages only, no logins; we store signals (counts, flags, ids), not page content; no personal data.

## Scope

- **Approved now:** public pages of online stores (Shopify storefronts, product pages, feeds, policy pages) and the store-audit checks in `docs/plan/opportunity-store-rescue.md`.
- **Separate owner decision, not switched on by this note:** sites whose terms explicitly forbid automated collection and that have sued scrapers or offer official APIs (Meta Ad Library, TikTok Creative Center, Trustpilot; decision 0013). Using an unblocker there is a legal and account risk the owner should take knowingly, per site.

## Owner steps

1. Create accounts (both offer a free trial; plans are paid) and put `ZENROWS_API_KEY` and `SCRAPINGBEE_API_KEY` in the cloud environment's variables (or the local `.env`), never in chat or the repo.
2. Set the daily credit cap if 1,000 is wrong for the chosen plans.
