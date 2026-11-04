# 20 — Source pilots: what each source actually discovered

> 2026-11-04. Applies the **source evaluation standard** (`CLAUDE.md`): each source tested on a small sample, scored on what it found. Pilots A–D (look-alike store discovery, fashion jewelry and press-on nails), E (published best-seller evidence), F (product-level sales-volume sources), G (CJ `listedNum`, run by the orchestrator with the live key). Store domains and raw data stay out of this public repo.

> **2026-11-04: Terapeak dropped** (owner: if it cannot be automated, it is out). Automated replacements are listed in decision 0008.

## Scorecard

| Pilot | Source | Relevant leads found | Terms for automated use | Verdict |
|---|---|---|---|---|
| A | **myip.ms** reverse IP on Shopify addresses | **0**. Listing and terms pages sit behind a "prove you're not a robot" gate. | Unclear; full terms unreadable without passing the gate | **Terms read 2026-11-04: robots, scrapers and page-scraping are prohibited (§III(e)); the official Myip.ms API is the approved channel.** No scraper; API only if the owner buys access. Replaced by Tranco + DNS (decision 0009). Shopify's root-domain address 23.227.38.65 confirmed via search snippet only. |
| B | **Certificate logs (crt.sh)** + RDAP + Wayback | **0 confirmed US stores.** `%nail%` gave 197 names, mostly salons, app demos and non-US shops; `%jewelry%` results looked truncated at 2017. Specific keywords returned nothing. | crt.sh terms unreachable (502); rate-limits under parallel load | **Drop for discovery.** Keep RDAP and certificate dates for dating a known domain. |
| — | Wayback Machine (archive dating) | 0 of 12 lookups succeeded | n/a | **Blocked by this sandbox's network** (connections reset), not by the archive. Needs an environment fix before use. |
| C | **Meta Ad Library, Google Ads Transparency, TikTok Creative Center** | **0** in automated fetches | Meta and TikTok **prohibit** automated collection; Google unclear, no API. Meta's API doesn't cover US commercial ads [secondary] | **Manual browser only.** Browser steps recorded below. |
| D | **Page fingerprinting** (8 stores found via search) | 8 profiled: platform 7/8 (Shopify), review app 7/8, social links 7/8, Klaviyo email 5/8, affiliate program 3/8. **Dropship signals 0/8.** | Respect robots.txt (3 redirects were not followed: a lapse to fix) | **Keep as the dossier tool.** Search surfaces established brands, not dropshippers, so it needs a better discovery source upstream. Homepage-only is too shallow for supply signals. |
| E | Published reports (Adobe, Shopify, TikTok trackers, eBay, Amazon lists, Etsy, Census) | Category-level evidence with numbers (see doc 21) | Public pages, read only | **Useful for "why" and category direction; no product-level US sales.** Amazon's lists are curation, not sales. |
| F | Product-level sales sources | **eBay Product Research (Terapeak)**: sold counts per search, up to 3 years [primary]. **Keepa** `monthlySold` = Amazon's "bought in past month" [primary docs]. CJ: **no sales field exists** [primary]. AliExpress volume field unverified. TikTok trackers: vendor estimates, collection method unclear. | Terapeak manual; Keepa terms not read; TikTok trackers likely scrape | **Terapeak first, Keepa second.** Hold AliExpress and TikTok tools. |
| G | **CJ `listedNum`** (stores that imported a product), full US catalogue | 3,963 US-stocked products ranked. Median 49 listings, p90 666, max 38,743. | Our own supplier's API | **Useful as a "what dropshippers bet on" signal, not sales.** The margin-viable shortlist has a median of 418 (8× the catalogue), so cheap viable items are also the crowded ones. |

## What worked, what didn't

- **Discovery of look-alike stores is the weak link.** Every automated discovery route (reverse IP, certificate logs, ad libraries) was gated, prohibited or noisy for this niche. Fingerprinting works once we have the right stores.
- **The most valuable sales source is manual:** Terapeak, on our own channel.
- **The cheapest real signal we have is CJ `listedNum`,** which needs interpreting (validated demand or saturation) before use.

## Manual steps that remain valuable (owner, about 20–30 minutes each)

| Source | Steps |
|---|---|
| Meta Ad Library | facebook.com/ads/library → Country: United States → All ads → Active → search a product phrase. For each ad note: page name, "started running" date, format (video or image), landing domain. |
| Google Ads Transparency | adstransparency.google.com → Region: United States → search the phrase → open advertisers → note domain, first and last shown dates, format. |
| TikTok Creative Center | ads.tiktok.com/business/creativecenter → Top Ads → United States → keyword → sort by likes or duration → note brand, run period, format. |
| myip.ms | Read its terms in a browser first. If allowed, open "sites on IP 23.227.38.65" and look for stores named after our product types. |
| eBay Terapeak | Seller Hub → Research → Product research → United States, 90 days, Sold → record sold count, average price, sell-through (template in `docs/runbooks/terapeak-session.md`). |

## Fixes for the next round

- Pilot agents must follow robots.txt redirects before fetching.
- Wayback access fails at this sandbox's network relay; request the host be allowed if archive dating matters.
- Re-test crt.sh with sequential queries and longer keyword variants only if discovery stays blocked elsewhere.
