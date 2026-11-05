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
