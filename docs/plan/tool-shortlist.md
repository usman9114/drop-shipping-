# Tool shortlist from the owner (2026-11-05)

> Owner: "Take note of the tools I've suggested; use the existing infrastructure already in place." This is the reuse list: before building anything in these areas, check this table first (CLAUDE.md "reuse before build"). Prices and plan details are from memory and marked `[unverified]` until checked; any paid plan or new account needs the owner's go-ahead (principle 7).

## Use now or next (fits the current pipeline)

| Tool | Use for us | When | Notes |
|---|---|---|---|
| Python requests / httpx / aiohttp / BeautifulSoup, Playwright, crawl4ai | the scraping layer | **in use** | already our stack (`scout.*`, decision 0014) |
| **Supabase (Postgres)** | durable 24/7 storage for the autopilot (store tables, runs, queues) and the backend for a later UI | next, with the hosting decision | answers the storage gap in decision 0012 and `docs/plan/autopilot.md`; free tier `[unverified: limits]` |
| **GitHub Actions / cron** | scheduler for the autopilot jobs | next | the options table in `docs/plan/autopilot.md` |
| Google PageSpeed / Lighthouse API | page speed for the store audits | next | free API key (owner step) |
| Google Sheets | the owner's review queue for leads and shortlists, before any UI | next | cheap stand-in for a UI; written from Python |
| **Gemini API** | a third free model lane in `scout.llm` next to GLM and OpenRouter | next | free tier exists `[unverified: current limits]`; free-tier prompts may be used for training, so the same no-secrets rule applies |
| Shopify app ecosystem (Klaviyo, Gorgias, Recharge, Skio, Nosto, Elevar, Littledata, Judge.me, Loox, Yotpo) | **detection targets**: add their storefront traces to `scout.fingerprints.SIGNATURES` | next | they measure effort and budget (Klaviyo, Gorgias, Recharge = a funded store); Elevar or Littledata present = server-side tracking already done, so no "pixel" pitch |
| Meta Pixel / Google Tag Manager / LinkedIn Insight Tag | detection targets for the tracking audit | partly in use (`scout.webmeta` ad tags) | add GTM container and LinkedIn tag detection |
| **Empire Flippers, BizBuySell** | **real revenue and profit** of Shopify and dropship businesses for sale: ground truth to calibrate our `[proxy]` scores, plus an exit route | next (manual reading first; terms check before any automation) | fills the gap every report names: we never see revenue |
| StoreLeads | benchmark our Shopify discovery (miss rate) and app detection; possible licensed data source | trial when needed (paid) | an official API with terms beats rebuilding their database |
| SimilarWeb | traffic estimates for the final shortlist | manual, free tier | a modelled estimate: `[proxy]`, never sales |
| Koala Inspector | owner's manual spot checks of a store | manual | browser extension |
| Meta Ad Library | ads running, for the final shortlist | manual for US (decision 0013) | official API only covers EU and political ads |
| Bright Data | its **ready-made datasets** (licensed Shopify store data) | only if our discovery falls short | the Web Unlocker part: see "held back" below |
| Cloudflare | detection: Shopify stores behind Cloudflare are missed by our IP-range check | next | header-based detection in the discovery job |

## For the outreach test (after R1, owner approval)

| Tool | Use |
|---|---|
| Apollo.io, Hunter | find the owner or marketing contact for a store domain from a licensed B2B database |
| NeverBounce | verify every address before sending (protects the sending domain) |
| Instantly or Smartlead | sending from a separate warmed-up domain, opt-out handling, low daily volume |
| Loom | a 2-minute screen recording of each store's actual issue: the most credible form of the diagnostic |
| Cal.com | booking link in the message |
| Make.com / Zapier | glue for owner-run steps (new reply -> Sheet -> Cal.com) where no Python job is worth writing |
| LinkedIn Sales Navigator | manual lookup of the decision-maker for high-value leads |

## Later (UI and content)

- **UI stack**: Next.js, React, Tailwind, shadcn/ui, Tremor on top of Supabase. Matches the "lead inbox" idea: one card per store with problem, evidence, verify link, draft message.
- **Video and content** (OpusClip, Submagic, Descript, CapCut): marketing content for the service or our own store, and possibly eBay listing videos from CJ images. Not before a phase needs it.

## Not relevant to this project

- Tenable, Qualys, CyCognito, Jira, ServiceNow (enterprise security and IT). CyCognito's idea, mapping what an organisation exposes publicly, is the same method as our fingerprinting, but the tools themselves do not serve us.
- Cursor, GitHub Copilot: coding assistants; the repo is already developed with Claude Code and the free models.

## Held back, with the reason

- **ScrapingBee, ZenRows, Bright Data Web Unlocker** (the unblocking features). Their purpose is to get past bot checks; decision 0014 and principle 6 keep that off. In practice we have not needed them: the 105-store fingerprint run had 0 robots blocks and 1 page error, and Shopify's public `/products.json` and `/meta.json` rarely block an honest client. If a measured block rate ever limits the pipeline, the owner decides with the site's terms in hand. Their plain proxy or rendering features, without bot-check bypass, are not ruled out.
