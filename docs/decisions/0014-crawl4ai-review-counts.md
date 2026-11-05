# 0014 — Crawl4AI for review counts on store pages

> 2026-11-05. Owner request: "use Crawl4AI and fetch as much as needed". Code: `scout/reviews.py`, tests `tests/test_reviews.py`, optional dependency `requirements-crawl.txt`.

## Scope: what Crawl4AI may and may not fetch

- **Yes:** Shopify stores' own product pages, robots.txt respected, to read the review counts that review apps render in the browser.
- **No:** Trustpilot, Meta Ad Library, TikTok Creative Center. Their terms forbid automated collection by any tool; decision 0013 lists the official routes instead.

## Candidates

| Candidate | Licence | Maintenance | Fit |
|---|---|---|---|
| **Crawl4AI 0.9.5** (unclecode/crawl4ai) | Apache-2.0 | very active, widely used | renders JavaScript with Playwright, honours robots.txt (`check_robots_txt`), reports anti-bot blocks; **chosen** |
| Plain Playwright | Apache-2.0 | maintained | works, but we would rebuild what Crawl4AI already does |
| Plain `requests` | Apache-2.0 | maintained | misses counts that load in the browser |

## Settings that keep us inside our rules

Crawl4AI ships stealth components (playwright-stealth, patchright, a fake user-agent generator) built to hide automation. We switch them **off**: `enable_stealth=False` and our fixed, honest User-Agent. A challenge page (Cloudflare, captcha) or a 403/429/430 ends the attempt as `blocked`. Only counts and the review app's name are stored, never review text. It runs in its own virtualenv, with Playwright pinned to 1.63.0 to match the preinstalled Chromium (no `playwright install`).

## Pilot (small first)

| Step | Stores | Review count found | Notes |
|---|---|---|---|
| Before (one JSON-LD field on one product) | 110 profiled | about 1 in 6 | the gap named in every story |
| Plain fetch, all patterns | 30 | 13 | structured data, Judge.me badge, visible "N reviews" text |
| Plus browser render when the plain fetch finds nothing | 30 | **15** | one store returned a Cloudflare challenge and was left alone |

Counts are the number shown on one product page (`[proxy]` for demand); they become a velocity signal only when tracked weekly with the same review app (decision 0011).
