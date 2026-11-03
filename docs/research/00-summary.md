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

**What could work:** our edge is **product selection backed by data**, plus **original, high-quality listings**, using **domestic (US/EU-warehouse) wholesale suppliers that have APIs**, in **niches Temu doesn't serve well**. This lines up with the 2025–26 tariff changes, which favor domestic stock.

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
| Copy the supplier's photos and text | Original photos of a **sample unit**, AI-enhanced; specs pulled from structured supplier data |
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

### Phase 1: listing quality, ~$100–200

- Order samples of the top 5–10 SKUs to check quality and actual delivery time.
- Photograph them. Run them through the image pipeline (background removal plus AI lifestyle scenes built **around our own photo**, ~$0.02–0.07 per image).
- Use an LLM to write titles, item specifics and descriptions grounded **only** in supplier specs and the physical sample.

**Kill criterion:** sample quality or real delivery time doesn't match the supplier's claims.

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

**Go criterion:** realized net ≥ 15% and defect rate under 2%, with a path to automating ordering and tracking through the APIs.

## Open questions to resolve before building

1. **Which niche?** We need one candidate (e.g. hobby parts, pet, home-office accessories, replacement parts) to scope Phase 0.
2. **Market:** US only for the PoC? The EU adds GPSR responsible-person and 14-day withdrawal obligations (05).
3. **Can we get API keys?** eBay developer account (free), CJ API key (free), and possibly Marketplace Insights (apply).
4. **Who photographs samples?** Original images are the core differentiator and the main IP safeguard.

## Confidence

- **High:** eBay fees and seller standards; the dropshipping policy text (UK page); the de minimis timeline (Federal Register); NRF return rate.
- **Medium:** supplier API capabilities (CJ docs verified; others not); AI image costs.
- **Low:** all margin, success-rate and "what winners do" claims. They come from vendors selling tools or courses. Phase 0 exists to replace them with our own numbers.
