# Opportunity (parked): stores that try hard but underperform

> 2026-11-05. Owner idea: "We process a lot of data finding successful stores. What about ones that are struggling, where the owner is putting in effort? If a store doesn't meet our criteria but we see potential, we could start cold outreach and help them revamp their system. We don't need to build the system now, but don't leave any meaningful opportunity."
>
> Status: **parked idea, outside phase R1** (CLAUDE.md principle 1). Nothing is built and no one is contacted until the owner approves a phase for it. What we do now is make sure the autopilot **keeps the evidence** this would need, at almost no extra cost.

## The idea in one line

Our crawl already sees thousands of stores that are clearly investing (ad pixels, email and SMS tools, frequent product releases, a paid theme) yet rank low or are falling. Some of them have problems we can **see from public pages and could fix for them**. Those are service leads: the pitch is a specific, checkable problem, not a generic offer.

## How we would quantify "potential"

One score, weights in one place, every input labelled (principle 4). All inputs are `[proxy]`; none is revenue.

| Component | What it measures | Inputs we already collect | Weight (draft) |
|---|---|---|---|
| **Effort** | the owner is spending time and money | ad pixels (Meta, Google Ads, TikTok), email/SMS apps, review app, products added in the last 90 days, paid apps count, active blog | 0.30 |
| **Market fit** | they sell into demand that works for others | niche has grade A/B winners in our study set; price band matches winners; category growth in rank history | 0.25 |
| **Underperformance** | results lag the effort | rank low for their effort level, flat or falling 6-month rank trend, few on-site reviews against catalogue age | 0.20 |
| **Fixability** | we can name a concrete, checkable problem | count and severity of the issues below | 0.25 |

`potential = effort x fit x underperformance x fixability`, multiplied rather than added so a store with zero in any part scores zero (no effort means no buyer for help; nothing fixable means no pitch). A store needs at least one **verified** issue to become a lead.

What would change the order: a verified issue outranks any amount of effort signal; rank trend is noisy for stores outside the top 500k.

## Problems visible from public pages (no checkout, no login)

| Issue | How we would see it | Confidence |
|---|---|---|
| Ads tag without conversion setup: Google Ads id (`AW-`) present, no conversion label or Google & YouTube app pixel; Meta pixel loaded twice (app + theme code) | page source, Shopify `webPixelsConfigList` (we already parse ad tags in `scout.webmeta`) | medium: we see configuration, not whether events fire |
| Legacy Universal Analytics (`UA-`) only, no GA4 | page source | high: UA stopped processing data in 2023 to 2024 |
| Slow mobile pages (LCP, INP, CLS) | Chrome UX Report / PageSpeed Insights API (official Google API; needs a free key, owner step) | high for stores with CrUX data |
| Product pages without Product structured data, missing meta descriptions, `noindex` on products | page source, `/sitemap.xml` | high |
| Catalogue rot: most products sold out, broken image URLs, no new products for months | `/products.json` (already fetched) | high |
| Trust gaps: no shipping or refund policy, unedited default refund text, no contact page | policy pages (`scout.dropship_profile`, already built) | high |
| Slow shipping undisclosed: AliExpress source detected but no delivery time stated | fingerprints + policy text | medium |

**What we must not claim.** The owner's example pitch ("your purchase event isn't firing on mobile Safari") needs a real purchase to prove. We will not place test orders or run checkouts on other people's stores. So a pitch states only what we observed ("your Google Ads tag loads, but we see no conversion setup on your store's pages") and offers to verify with the owner's permission. A wrong claim in a cold email destroys the lead and our credibility.

## Rules if this becomes a phase

- **Compliance first** (compliance officer reviews before any send): US CAN-SPAM rules for commercial email (accurate sender, physical address, working opt-out) `[unverified: to be sourced]`; UK and EU stores fall under GDPR and PECR, which are stricter for unsolicited email `[unverified]`. Start with US stores and business contact channels only.
- **No harvesting personal data.** Contact only through the store's own published business channels (contact form, published support address). No scraping of personal emails, LinkedIn or WHOIS.
- **Small first.** 10 hand-picked leads, hand-written messages, measure reply rate, before any automation.
- **Owner approves** the offer, pricing and each first batch.

## What the autopilot keeps now (cheap, and the only action taken)

We already store ad tags, apps, policy signals, catalogue counts and rank history per store. When the next jobs are built (`docs/plan/autopilot.md`), the homepage fetch will also record these flags at no extra request cost: `ua_only`, `aw_without_conversion`, `meta_pixel_duplicate`, `product_jsonld_missing`, `noindex_products`, `soldout_share`, `days_since_last_product`. Flags only, no page content. That keeps the option open without building the lead system.

## Open questions for the owner

1. Is this a separate business line (service agency) or a side channel of the dropship PoC?
2. Which offer: one-off audit, setup fix, or ongoing management?
3. Approve a free Google API key for Chrome UX Report / PageSpeed data (needed for the speed issues)?

## Review of the owner's "Shopify Audit & Competitor Spy SaaS" blueprint (2026-11-05)

The owner shared a blueprint for a SaaS with two halves: competitor intelligence ("Success Key") and lead generation from technical flaws ("Bleeding Alerts"). Verdict: **the direction fits, and most of the data engine already exists in this repo; three parts conflict with our rules or overclaim and need changing.**

| Blueprint part | What we already have | Verdict |
|---|---|---|
| Tier 1: async `/products.json`, `/meta.json` | `scout.stores` light/deep, `scout.fingerprints`, `scout.snapshot_job` (30,365 stores found, 11,415 screened) | **Keep. Built.** |
| Tier 2: render JS through an "unblocking API" (ZenRows, ScrapingBee) | Crawl4AI render with stealth off, a block ends the attempt (decision 0014) | **Reject the unblocking API.** Those services exist to get around bot checks, which principle 6 and decision 0014 forbid. Keep our honest render; a blocked store is recorded as blocked. |
| Tier 3: LLM "self-healing" CSS selectors | not needed so far: Shopify exposes structured data (products.json, JSON-LD, meta.json) | **Adapt, low priority.** If a selector is ever needed, the free models (GLM) may propose one, but it is checked against a known value and versioned before the autopilot uses it (autopilot rules 2 to 4). |
| Audit A "Pixel blindness": no server-side tracking app (e.g. Elevar) means lost mobile conversions | ad tags and `webPixelsConfigList` parsed in `scout.webmeta` | **Change the claim.** Server-side tracking is invisible in page source: Shopify's own Facebook & Instagram app can send events server-side (Conversions API) `[unverified: to confirm in Shopify/Meta docs]`, so "no Elevar" does not mean "no server-side". The "15 to 25% lost" figure has no source. What we can state: Meta pixel hard-coded in the theme instead of the app pixel, the pixel loaded twice, Universal Analytics only, Google Ads tag without conversion setup. |
| Audit B "Script drag": more than 15 third-party scripts, then a Lighthouse check | asyncLoad script hosts and app embeds parsed in `scout.fingerprints` | **Keep, with honest numbers.** Count third-party script hosts from the homepage we already fetch; speed comes from the PageSpeed Insights / Chrome UX Report API (free key, owner step). Not claimable: "dead scripts from uninstalled apps" (we cannot see what is installed) and "cutting conversion by Z%" (no store-level data). |
| Audit C "Abandoned reviews": review widget present, 0 reviews on flagship products | `scout.reviews` (review app and count per product page; 15 of 30 found in the pilot) | **Keep. Mostly built.** Caveat: `/products.json` order is not sales order, so "flagship" means the newest or first-listed products, not best-sellers. |
| Verify ad spend with the Meta Ad Library | decision 0013: the official API covers EU ads and political ads only; **US commercial ads are not in the API**, and the website forbids automated collection | **Change.** US: ad-pixel presence as a `[proxy]` for "funded", plus the owner's manual Ad Library check on the final shortlist. EU stores: the official API is possible after Meta's identity check. |
| Growth score, product velocity, tech tier | rank history (26 dates, 2 years), feed snapshots, app and theme detection | **Keep. Built**, labelled `[proxy]`. |
| Pitch generator, no sending from the app | free-model batch runner (`scout.llm --batch`, cached) | **Keep.** Pitches come from a template filled with **verified flags only**; GLM may polish wording; a person reviews and sends through the store's published business channel. |
| Dashboard with progressive disclosure | none | **Later, reuse not build** (e.g. Evidence, Metabase or Streamlit over the DuckDB warehouse), decided in `docs/decisions/` when the phase starts. |
| Go to market: 1,000 stores in one high-value niche; pre-sell to 5 agencies | warehouse and niche scores exist | **Keep the method**, with one blocker: selling or sharing store-level data with agencies means publishing data whose terms we hold only for private working copies (CLAUDE.md terms gate). Needs a terms and legal review before any pre-sale. |

**What it would take to run a first test (not started):** 1 niche, about 1,000 stores from our warehouse, the three audits as flags (two of three already computed), a hand check of 30 flagged stores for precision (principle 5), then 10 hand-written diagnostics. Owner decisions first: the questions above, plus whether this is a product to sell (SaaS) or a service we deliver (agency).
