# 00 — Research summary and PoC plan

**Question:** can we find good products on eBay (and similar marketplaces), make *better* listings (images, descriptions), and dropship them profitably?

**Date:** 2026-11-03. **Inputs:** five parallel web-research reports (01–05 in this folder), cross-checked and edited during synthesis.

## Verdict (short)

**The naive version fails. A narrower version is worth a PoC.**

The version everyone has heard about, *find a winning AliExpress product, copy a top listing, dropship it on eBay*, has four problems. Any one of them is enough to make it fail:

1. **It's against eBay policy.** Only *wholesale-supplier* dropshipping is allowed. Buying from "another retailer or marketplace" (AliExpress, Amazon, Walmart, Temu) after the sale is banned (01 §1).
2. **Cloning listings is IP infringement.** Copied photos and text get removed through VeRO and lead to account suspension. AI-editing someone else's photo doesn't clear the copyright (05 §1).
3. **The economics have collapsed.** Fees are ~14–19% including ads. US de minimis ended in 2025 and the EU added a €3 duty in 2026. Temu and Shein sell the same items direct. Modeled net is **~6–21%** before any mistakes (02 §1).
4. **The operations are brittle.** 2–5 week China shipping breaks handling-time promises (FTC Mail Order Rule) and drives INR/INAD disputes. Out-of-stock cancellations count as defects, and new sellers face payout holds of up to 21 days (01, 03).

**What could work:** our edge is **product selection backed by data**, plus **better listings built from supplier-licensed content**, using **wholesale suppliers that have APIs and stock in their own US/EU warehouses**, in **niches Temu doesn't serve well**. This lines up with the 2025–26 tariff changes, which favor stock that is already in the country.

## Constraint: zero inventory (owner decision, 2026-11-03)

- **We never hold or buy stock.** Every order is paid to the supplier after the buyer pays, and the supplier ships directly to the buyer.
- "US-warehouse supplier" means the **supplier's** warehouse. We own nothing in it.
- Working capital pays only for orders already sold. It covers the gap until eBay releases funds held for new sellers (up to 21 days).
- **Consequence for images:** we can't photograph products ourselves. Listing images must come from supplier images **licensed for reseller use**, a supplier's paid photo service, or eBay catalog images. AI may only *enhance* a licensed image (background, lighting, upscaling, lifestyle scene around the unaltered product). eBay bans added text, borders and watermarks on images. It must never invent features. See `06-image-sourcing.md`.
- **Consequence for QC:** quality and delivery time are checked with **test orders through the normal dropship flow**, shipped to our own address, plus supplier QC/inspection services. These are one-off orders, not stock.

## The thesis to test

> For a defined product niche, we can systematically find items where
> (a) eBay demand is proven (sell-through above a threshold),
> (b) a domestic wholesale supplier with an API can ship in ≤ 5 days, and
> (c) modeled net margin is ≥ 20% after all fees, ads, returns and duties,
> and then outsell incumbent listings of the same item through better listings: our own photos, AI-enhanced presentation, accurate specs, compatibility charts.

## What makes this different from "what everyone is doing"

| Most dropshippers | Our PoC |
|---|---|
| AliExpress / Amazon retail arbitrage | Wholesale or US-warehouse supplier with an API (policy-compliant) |
| Copy competitors' or unlicensed supplier photos and text | **Supplier-licensed** images, AI-enhanced; specs pulled from structured supplier data |
| Hold stock or prepay inventory | **Zero inventory:** the supplier ships every order |
| Pick products by gut feel or a course's "winning product" list | A scoring model: sell-through, competition, landed margin, delivery time, IP and compliance flags |
| Manual stock checks | Automated price/stock sync, auto-zero quantity when the supplier runs out |
| Broad "trending" catalog | One niche, tens of SKUs, not thousands |

## PoC plan (feasibility before money)

### Phase 0: desk feasibility, $0, ~1–2 weeks of build

Build `product-scout`:

1. **Supplier side:** pull a catalog from **CJ Dropshipping's API**, filtered to US-warehouse stock. CJ's API is free and covers catalog, stock, orders and tracking (03). Add Wholesale2B or Inventory Source later if we can get API access.
2. **Demand side:**
   - The **eBay Browse API** gives active-listing counts and price distribution per item. It's on the free developer tier.
   - **Terapeak CSV exports** (Seller Hub UI, manual) give sold counts.
   - Marketplace Insights (sold-data API) is limited release. Apply, but don't depend on it (04).
3. **Margin model:** price minus supplier cost, shipping, duty, 13.6% FVF (on price plus tax), $0.40, ad rate, return-rate reserve and an INR/INAD reserve. The worked example is in 02 §1.
4. **Risk flags:** brand or trademark terms, battery or radio (FCC), children's product (CPSIA), design-patent-prone gadget categories (05).
5. **Output:** a ranked shortlist.

**Kill criterion:** fewer than ~20 SKUs in one niche reach ≥ 20% modeled net with sell-through ≥ 50% and ≤ 5-day delivery.

### Phase 1: listing quality, ~$100–200 (no stock)

- Place **test orders** for the top 5–10 SKUs through the normal dropship flow, shipped to our own address. These measure real delivery time and quality, and the items aren't resold. Supplier QC/inspection services are an alternative.
- Run **supplier-licensed** images through the image pipeline: background cleanup, lighting, upscaling, lifestyle scenes. No text, badges or borders, which eBay bans; feature callouts go in the description. Cost is ~$0.02–0.07 per image. Keep the product itself unaltered.
- Use an LLM to write titles, item specifics and descriptions grounded **only** in supplier specs, verified against what the test order showed.

**Kill criterion:** test-order quality or real delivery time doesn't match the supplier's claims, or the supplier's terms don't license its images for marketplace use.

### Phase 2: live micro-test, ~$300–500 working capital, 60 days

- List 10–20 SKUs on a new eBay account. Expect new-seller limits and payout holds.
- Track:

  | Metric | Target |
  |---|---|
  | Views → sales conversion | vs. incumbent listings of the same item |
  | Realized net margin | — |
  | Defect rate | < 2% |
  | Return rate | — |
  | Hours per order | — |

**Go criterion:** realized net ≥ 15% and defect rate under 2%, with a workable **manual** routine for ordering and tracking. API automation of CJ orders or tracking is prohibited (eBay API License 9.6).

## Open questions to resolve before building

1. **Which niche?** We need one candidate (e.g. hobby parts, pet, home-office accessories, replacement parts) to scope Phase 0.
2. **Market:** US only for the PoC? The EU adds GPSR responsible-person and 14-day withdrawal obligations (05).
3. **Can we get API keys?** eBay developer account (free), CJ API key (free), and possibly Marketplace Insights (apply).
4. ~~Who photographs samples?~~ **Resolved: zero inventory.** Images come from supplier-licensed sources (see `06-image-sourcing.md`).

5. ~~Which supplier?~~ **Decided 2026-11-03: CJ Dropshipping** for catalog, stock, orders and tracking. Images: **CJ's own images, with AI enhancing only the surroundings** (decided 2026-11-03; see `06-image-sourcing.md` §5). CJ's paid copyrighted photos come later if the PoC works.

> **Update 2026-11-03:** eBay's API license restricts storing eBay data, computing statistics or average selling prices from it, and using it to model prices without written permission (`docs/research/17`, decision 0004). Phase 0 therefore cannot rely on automated eBay Browse data; it uses manual Terapeak reading, non-eBay evidence, and later our own account's data.

> **Update 2026-11-03 (PR #1 review):** eBay API License 9.6 prohibits automating orders from other sites, posting tracking for them, and repricing from their prices. The first 10 to 20 listings are handled manually; whether CJ's own eBay integration is allowed is unverified.

> **Update 2026-11-04 (later):** Terapeak and other manual steps are dropped; the evidence pipeline is automated (decisions 0007, 0008). Store discovery and profiling now come from internet metadata: traffic rankings, DNS, sitemaps and storefront product feeds.

## Confidence

- **High:** eBay fees and seller standards; the dropshipping policy text (UK page); the de minimis timeline (Federal Register); NRF return rate.
- **Medium:** supplier API capabilities (CJ docs verified; others not); AI image costs.
- **Low:** all margin, success-rate and "what winners do" claims. They come from vendors selling tools or courses. Phase 0 exists to replace them with our own numbers.
