# 0001 — Candidate niches (Stage B)

> Owner: `head-of-marketing`. Date: 2026-11-03. Status: **proposed**, waiting on Stage C data (Trends, eBay Browse, CJ catalog), compliance risk cards and sales-lead economics. The final pick is `0002-niche-selection.md`.
>
> **Evidence quality: low.** This memo has no [data] yet. Rubric scores are [estimate]s anchored on research docs 01–10 ([primary] where eBay's own filings or fee pages say so, [secondary] otherwise). Stage C exists to replace the estimates.

## 1. Decision

Carry **8 candidate niches** into Stage C. Five are "picks-and-shovels" niches: supplies for collectors and hobbyists who already shop on eBay. Two are plain low-risk categories kept as controls. One sits in between (watch accessories).

| # | Slug | One-line thesis | Prelim. score (0–5) |
|---|---|---|---|
| 1 | `tcg-supplies` | Sell storage and display to the trading-card buyers driving eBay's fastest growth. | **3.75** |
| 2 | `hobby-modeling-tools` | Tools for miniature and scale-model builders: small, light, unregulated, and bought by hobbyists who already shop eBay. | **3.70** |
| 3 | `vinyl-record-care` | Sleeves, brushes and display for record collectors. Passive goods with no electronics and spec-driven buying. | **3.50** |
| 4 | `coin-supplies` | Archival holders and albums for coin collectors, a core eBay vertical. Tiny parcels; specs (PVC-free, sizes) win the sale. | **3.35** |
| 5 | `pet-grooming-supplies` | Manual grooming tools. Lowest-risk plain category (doc 10), but eBay is not a pet destination. Control niche. | **3.35** |
| 6 | `collectibles-display` | Acrylic cases and risers for figures, die-cast and sports memorabilia, sold with exact interior dimensions. | **3.30** |
| 7 | `watch-accessories` | Boxes, straps and tools for watch hobbyists, riding eBay's luxury and watch focus categories. | **3.30** |
| 8 | `auto-detailing-tools` | Non-chemical detailing tools next to eBay's Motors Parts & Accessories growth ("repair over replace"). | **3.30** |

The spread (3.30–3.75) is smaller than the error in the estimates. **No niche is preferred yet.** The order is only a prior.

## 2. Evidence table

### 2a. Margin constraint behind the price targets

`python -m scout.margin --price P --cost L --ship 0 --json` (L = landed cost = CJ product + CJ US shipping; defaults: 13.6% FVF on price plus 7% tax, $0.40 per order, 5% ads, 8% returns, 2% disputes; stress adds $3 duty and doubles returns). This is model output on assumed inputs [estimate], not market data.

| Price | Landed $5 | Landed $7 | Landed $9 | Landed $12 |
|---|---|---|---|---|
| $15 | 31.6% / 0.5% ❌ | 18.3% / −12.8% ❌ | 5.0% ❌ | −15.0% ❌ |
| $20 | 41.7% / 16.7% ✅ | 31.7% / 6.7% ❌ | 21.7% / −3.3% ❌ | 6.7% ❌ |
| $25 | 47.7% / 26.3% ✅ | 39.7% / 18.3% ✅ | 31.7% / 10.3% ✅ | 19.7% ❌ |
| $35 | 54.6% ✅ | 48.9% ✅ | 43.2% ✅ | 34.6% / 17.4% ✅ |

Cells show base net / stress net. ✅ means ≥ 20% base and ≥ 10% stress.

**Implication:** a $15 single item never passes. The sweet spot is **$25–45 with landed cost ≤ ~⅓ of price**. CJ US shipping alone is probably $4–6 per small parcel [estimate, unverified], so niches need **natural kits, bundles, multi-packs or display pieces** in the $25–45 band. That favours the picks-and-shovels niches below, where "50-pack", "tool kit" and "display case" are normal buying units.

### 2b. Rubric scores (`docs/plan/ai-team.md` §5)

Scale 0–5, 5 = best. Risk and Temu are inverted, so 5 = safest or least competition. **Every cell is [estimate]** unless a source is named.

| Niche | Demand 20% | eBay fit 15% | Margin 20% | Risk 20% | Temu/Amz 10% | Ops 10% | Listing 5% | **Weighted** |
|---|---|---|---|---|---|---|---|---|
| tcg-supplies | 4 | 5 (08 [primary]) | 3 | 4 | 2 | 4 | 4 | **3.75** |
| hobby-modeling-tools | 3 | 4 | 4 | 4 (10: craft/hobby = 2 [secondary]) | 3 | 4 | 4 | **3.70** |
| vinyl-record-care | 3 | 4 | 3 | 4 | 3 | 4 | 4 | **3.50** |
| coin-supplies | 2 | 5 (01: coins have their own FVF tier [primary]) | 2 | 4 | 3 | 5 | 4 | **3.35** |
| pet-grooming-supplies | 4 | 2 | 3 | 4 (10: pet = 2 [secondary]) | 3 (10: "med" [secondary]) | 4 | 3 | **3.35** |
| collectibles-display | 3 | 4 (08 [primary]) | 3 | 4 | 3 | 2 | 4 | **3.30** |
| watch-accessories | 3 | 4 (08: luxury focus category [primary]) | 4 | 3 | 2 | 3 | 4 | **3.30** |
| auto-detailing-tools | 4 | 3 (08: P&A +1 pt GMV [primary]) | 3 | 4 (10: car interior = 3 [secondary]) | 2 | 3 | 3 | **3.30** |

Hard filters (compliance veto, average price < $15, oversize or hazmat): every niche **passes conditionally**. Each niche is scoped to exclude its vetoed sub-types (powered, lithium, liquids, children's, branded, oversize), listed under "excluded" in §3.

### 2c. Sources for the shared premises

| Claim | Label | Source |
|---|---|---|
| Collectibles were the largest contributor to eBay GMV growth in Q4 2025 and Q3 2026 | [primary] | 08; eBay Q3 2026 exhibit 99.1 (SEC) |
| Trading cards: sports accelerating; TCGplayer passed $1B trailing-12-month GMV | [primary]/[secondary] | 08 |
| Pokémon #1 eBay search in 2025; PSA grading terms in the top 10 | [primary] | 08 (eBay Collected 2025) |
| Motors P&A added > 1 pt of GMV growth in Q4 2025 | [primary] | 08 |
| Luxury (incl. watches) and sneakers are eBay focus categories | [primary] | 08 |
| Pet, craft/hobby and bathroom are the lowest-risk categories (risk 2) | [secondary] | 10 |
| Schedule A design-patent suits target trending gadgets; defendants won no resolved cases 2023 to mid-2024 | [secondary] | 10 |
| Prop 65: > 5,000 notices in 2025, mostly lead in glass, ceramics and brass | [secondary] | 10 |
| CJ US-warehouse category depth: no hard data; pet, home and fitness are mentioned | [secondary] | 09 |
| CJ US delivery 2–5 days typical (2–8 range) | [secondary] | 09 |

## 3. Candidate cards

### 3.1 `tcg-supplies`: trading-card storage and display

- **Thesis:** cards are eBay's fastest-growing vertical [primary, 08], and every card bought or graded needs a holder, binder or case. The buyer is already on eBay.
- **Target buyer:** adult collectors and flippers (sports cards, TCG, graded-slab owners) buying 2–20 cards a month. They search by fit ("35pt", "graded slab").
- **Product types CJ plausibly stocks** [estimate, CJ catalog to confirm]:
  1. magnetic one-touch card holders (35pt–130pt), in multi-packs
  2. graded-slab storage cases (10–50 slot, aluminium or PP)
  3. graded-slab display stands and easels
  4. 9-pocket and 4-pocket zip binders
  5. side-loading binder pages
  6. acrylic sealed-product cases (booster-box-sized UV acrylic boxes)
  7. single-card acrylic frames and wall mounts
  8. multi-card UV display cases
  9. semi-rigid card savers, penny-sleeve bulk packs
  10. plastic card storage boxes and sorting trays
  11. unbranded deck boxes
- **Excluded:** anything with Pokémon, Magic, NFL, MLB or other licensed art or names; "PSA/BGS" in titles (use slab dimensions; compliance decides on nominative use); LED-lit cases.
- **Key risks:**
  - IP: incumbents are brands (Ultra Pro, BCW and similar). We sell generic items, so titles must never borrow brand terms.
  - Temu and Amazon are cheap on sleeves and toploaders. Compete with bundles (e.g. 25 magnetic holders + stand).
  - Magnets: the CPSC magnet rule (16 CFR 1262) probably does not cover embedded, non-separable magnets [estimate; compliance to confirm].
  - Children's-product line: Pokémon has young buyers. Keep generic designs with no cartoon art and adult-collector positioning.
  - Acrylic scratches and cracks in transit (INAD).
  - The FVF for supplies may be 13.6%, not the 13.25% card tier [unverified].
- **Confirm or kill:**
  - Trends: "card display case", "magnetic card holder", "graded card case" flat or rising over 12 months.
  - Browse API: median price ≥ $20 for bundles; how many listings come from US-located sellers.
  - CJ: ≥ 40 US-warehouse SKUs with landed cost ≤ ⅓ of the eBay median.
  - **Kill if:** CJ US stock is mostly single cheap toploader packs under $15.

### 3.2 `hobby-modeling-tools`: miniature and scale-model tools

- **Thesis:** wargaming and model-kit hobbyists buy kits on eBay and need precise tools. Tools are passive, small and light. Doc 10 rates craft/hobby among the lowest-risk categories [secondary]. Hobbyists judge tools on specs (blade type, flush-cut), which plays to structured listings.
- **Target buyer:** adult miniature painters and plastic-model builders (wargaming, mecha kits, scale military/auto/aircraft).
- **Product types:**
  1. flush sprue cutters
  2. hobby knife sets with spare blades
  3. self-healing cutting mats (A4/A3)
  4. modeling tool kits (files, tweezers, scribers)
  5. pin vise hand drills with micro bits
  6. sanding sticks and needle files
  7. wet palettes
  8. paint dropper-bottle storage racks
  9. miniature painting handles
  10. parts trays and organizers
  11. non-powered helping hands
  12. airbrush cleaning pots and brush sets
- **Excluded:** paints, glues, putties and solvents (LHAMA/ASTM D4236 labelling for art materials, flammable hazmat) [secondary; compliance to confirm]; airbrush compressors (mains-powered); LED magnifiers with lithium cells.
- **Key risks:**
  - Brand VeRO: Games Workshop and Bandai enforce hard. Never use "Warhammer", "Gundam", "Citadel" or similar. Use "miniature" and "model kit".
  - Blades: ship-safe, but listings need sharp-object handling notes.
  - Demand is thinner than tcg [estimate]. Trends will show whether "wet palette" and "sprue cutter" have enough volume.
- **Confirm or kill:**
  - Trends level and trend.
  - Browse API active-listing counts (enough demand, not saturated).
  - CJ depth: hobby tools may mostly ship from China [estimate].
  - **Kill if:** < 20 US-warehouse SKUs.

### 3.3 `vinyl-record-care`: record sleeves, cleaning and display

- **Thesis:** vinyl buyers are collectors who buy records on eBay. Their accessories are passive (no electronics), buying turns on materials (HDPE vs paper sleeves, mil thickness), and multi-packs land naturally in the $20–40 band.
- **Target buyer:** adult record collectors with 100+ LPs, plus new turntable owners.
- **Product types:**
  1. anti-static inner sleeves (HDPE / rice-paper, 50–100 packs)
  2. polypropylene outer sleeves (packs)
  3. carbon-fibre record brushes
  4. velvet cleaning brushes
  5. dry cleaning kits (brush + stylus brush, **no fluid**)
  6. stylus brushes
  7. record weights and clamps
  8. cork, rubber and felt turntable mats
  9. "now playing" display stands
  10. wall-mount record shelves
  11. LP divider cards
  12. 45 rpm adapters
- **Excluded:** cleaning fluids (isopropyl is flammable/hazmat); powered ultrasonic cleaners; turntables and electronics; heavy wooden crates (oversize/weight).
- **Key risks:**
  - PVC outer sleeves may trigger Prop 65 (phthalates). Prefer PP/PE.
  - Record-store and Amazon competition on sleeves.
  - eBay fit is my judgement. Doc 08 does not cover records [estimate].
- **Confirm or kill:**
  - Trends: "vinyl record sleeves", "record display stand".
  - Browse API median prices for 50-packs.
  - CJ US depth (unknown).
  - **Kill if:** sleeves are only available China-direct (2–3 week shipping) or US stock is stands only.

### 3.4 `coin-supplies`: archival coin holders and albums

- **Thesis:** coins are a core eBay vertical with their own fee tier [primary, 01]. Collectors pay for **archival-safe** storage, and accurate specs (PVC-free, capsule inner diameter) are exactly where listings fail today [estimate]. Parcels are the smallest and least breakable in the set.
- **Target buyer:** adult coin collectors and bullion stackers who need capsules, flips and albums sized to specific coins.
- **Product types:**
  1. PVC-free plastic flips
  2. 2×2 cardboard/mylar holders (bulk)
  3. coin capsules in assorted diameters with foam rings
  4. coin albums and binders with 20-pocket pages
  5. replacement album pages
  6. graded-slab coin storage boxes
  7. round coin tubes
  8. wooden or aluminium coin display cases
  9. 2×2 storage boxes
  10. flat-clinch staplers for 2×2s
  11. cotton/nitrile handling gloves
  12. non-LED 10× loupes
- **Excluded:** coins and bullion (not CJ goods; counterfeit risk); LED loupes and digital scales (button-cell lithium); PVC flips (Prop 65 DEHP and coin damage).
- **Key risks:**
  - **Low unit prices.** This niche only passes the $15 floor with bundles (100 capsules plus box, album sets).
  - Demand is steady, not booming. Gold and silver price spikes may lift stacker demand [estimate].
  - Supplies may not get the 13.25% coin FVF [unverified].
- **Confirm or kill:**
  - Browse API: median price of capsule/album bundles ≥ $20.
  - CJ: US stock of albums and display cases.
  - **Kill if:** median basket < $15 and bundling can't fix it.

### 3.5 `pet-grooming-supplies`: manual grooming tools (control niche)

- **Thesis:** pet supplies are the lowest-risk category in doc 10 (outside CPSC scope apart from food, low IP risk, 8–12% returns) [secondary], and CJ reportedly has pet depth [secondary, 09]. Kept as the **control**: low risk and big demand, but probably weak eBay fit.
- **Target buyer:** dog and cat owners grooming at home, especially of long-haired or double-coated breeds.
- **Product types:**
  1. slicker brushes (non-self-cleaning designs)
  2. deshedding combs and rakes
  3. dual-sided pin/bristle brushes
  4. dematting combs
  5. flea combs
  6. guillotine and scissor nail clippers
  7. grooming shear sets
  8. grooming gloves
  9. bath and shampoo brushes
  10. manual nail files
  11. multi-tool grooming kits (bundles)
  12. reusable hair-remover rollers (patent check required)
- **Excluded:** electric clippers and nail grinders (lithium); shampoos and flea/tick treatments (EPA/FIFRA pesticides, liquids); edible chews (ingestibles); beds and crates (bulky).
- **Key risks:**
  - **Weak eBay fit.** Chewy and Amazon own pet consumables and tools [estimate].
  - Schedule A risk on trending pet gadgets (self-cleaning slicker brushes, hair-remover rollers) [secondary pattern, 10; specific suits unverified].
  - Temu competition is "med" [secondary].
- **Confirm or kill:**
  - Browse API: share of sold/active listings priced above $20.
  - Trends: strong level expected.
  - **Kill if:** eBay prices cluster under $15 (Temu-anchored).

### 3.6 `collectibles-display`: acrylic display for figures, die-cast and memorabilia

- **Thesis:** collectibles drive eBay's growth [primary, 08], including collectible toys and figures. Owners want dust-free, UV-protected display, and **exact interior dimensions** are the main buying question, which suits structured listings.
- **Target buyer:** adult collectors of vinyl/designer figures, minifigures, 1:64 and 1:24 die-cast, and signed balls.
- **Product types:**
  1. acrylic display cubes in size steps
  2. stackable figure display boxes with dust covers
  3. minifigure wall display frames
  4. 1:64 multi-slot die-cast wall cases
  5. single 1:24/1:18 die-cast cases
  6. UV baseball display cubes
  7. hockey-puck and golf-ball display cases
  8. acrylic risers and step stands
  9. mirror-back display cases
  10. non-powered rotating display turntables
  11. acrylic-front shadow boxes
- **Excluded:** LED-lit cases (mains or lithium); glass domes and glass shadow boxes (breakage, Prop 65 lead); helmet, jersey and basketball cases (oversize).
- **Key risks:**
  - **Ops:** acrylic breaks and scratches; big boxes add dimensional weight; many size variants.
  - Trademarks: "LEGO", "Funko", "Hot Wheels" are off-limits in titles. Use "minifigure", "vinyl figure", "1:64 die-cast".
  - The figure-collecting buyer is younger, but display cases are general-use, not children's products [estimate; compliance to confirm].
  - UV-protection claims need supplier substantiation (FTC).
- **Confirm or kill:**
  - CJ US-warehouse acrylic depth and per-variant stock.
  - CJ shipping cost for boxes over 30 cm.
  - **Kill if:** landed cost of the mid-size cases is > ⅓ of the eBay median.

### 3.7 `watch-accessories`: watch boxes, straps and tools

- **Thesis:** watches are part of eBay's luxury focus [primary, 08]. Enthusiasts buy boxes, straps and DIY tools, and **sizing (lug width, wrist length)** is a natural place for a better listing (fit charts in the description).
- **Target buyer:** adult watch hobbyists with 3–20 watches who resize bracelets, swap straps and store collections.
- **Product types:**
  1. 6/10/12-slot watch boxes
  2. watch travel rolls and cases
  3. watch repair tool kits
  4. link remover / pin pusher tools
  5. case-back opener wrenches
  6. spring-bar tools
  7. spring-bar assortments, including quick-release
  8. nylon (NATO-style) straps
  9. leather straps
  10. generic silicone/rubber straps (by lug width)
  11. watch stands
  12. case-work cushions
- **Excluded:** smartwatch bands named for a brand (Apple Watch and similar: VeRO, Temu saturation); watch winders (mains/lithium); batteries (lithium coin cells); anything "for Rolex/Omega" in titles.
- **Key risks:**
  - **Variant explosion on straps** (width × colour × length) breaks the few-variants preference (09).
  - Leather may trigger Prop 65 (chromium) [estimate].
  - Temu is very cheap on straps.
  - Brand-compatibility wording draws VeRO.
- **Confirm or kill:**
  - Browse API median price for boxes and tool kits.
  - CJ US-variant stock for straps.
  - **Kill if:** the niche only works through straps (variant- and Temu-heavy).

### 3.8 `auto-detailing-tools`: non-chemical car-care tools

- **Thesis:** eBay Motors P&A is a growth driver ("repair over replace") [primary, 08], and DIY detailers buy tool sets. Liquids are excluded, so the niche stays out of hazmat.
- **Target buyer:** DIY car owners and enthusiasts detailing at home; side-hustle mobile detailers.
- **Product types:**
  1. detailing brush sets (boar-hair, synthetic)
  2. drill brush attachment sets
  3. foam cannons for pressure washers
  4. wash mitts
  5. microfiber towel multi-packs
  6. wheel and rim brushes
  7. tire and dressing applicator pads
  8. trim removal tool kits
  9. clay mitts and clay towels (no lubricant)
  10. vent and crevice brushes
  11. valve-stem caps
  12. interior detailing kits (brushes + towels)
- **Excluded:** chemicals, waxes, ceramic coatings (liquids/hazmat); polishers and cordless vacuums (mains/lithium); grit-guard buckets (bulky).
- **Key risks:**
  - eBay P&A demand is mostly **fitment parts**, which CJ can't supply. Generic detailing tools are an Amazon category, so eBay fit is uncertain.
  - Temu is cheap on brushes.
  - Foam cannons are heavy-ish (brass) and may trigger Prop 65 (lead in brass) [secondary pattern, 10].
- **Confirm or kill:**
  - Browse API competition count vs median price.
  - Trends seasonality (spring peak).
  - **Kill if:** median eBay price < $20 for kits.

## 4. Alternatives considered and rejected

| Niche | Why rejected | Label |
|---|---|---|
| Bathroom accessories | Low regulatory risk (10), but weak eBay fit; Temu very cheap on small items; ceramic breakage plus Prop 65 lead in ceramics/brass; showerheads face California flow limits; average price < $15. | [secondary]/[estimate] |
| Shipping supplies for eBay sellers (mailers, tape, boxes) | Clever picks-and-shovels play, but heavy and bulky for the price; Uline and Amazon set prices; CJ shipping would eat the margin. | [estimate] |
| Sneaker care and display | Sneakers are an eBay focus category [primary, 08], but drop-front boxes are bulky; crease protectors carry brand and design-patent risk; cleaners are liquids. **Reserve** if tcg/collectibles-display fail. | [estimate] |
| Comic-book bags, boards and boxes | Strong eBay buyer, but cardboard boxes are bulky and bags/boards cheap (< $15 per pack). Small display items fold into `collectibles-display`. | [estimate] |
| Fishing tackle | Lead sinkers (Prop 65, some state bans); seasonal; Temu-heavy. | [estimate] |
| Aquarium supplies | Core items (heaters, pumps, filters) are mains-powered; liquids. A tools-only subset is too thin. | [estimate] |
| Yarn and knitting tools | Average price < $15; Temu-heavy; ceramic yarn bowls carry Prop 65 risk. | [estimate] |
| Jewelry-making supplies | Lead and cadmium in findings (Prop 65, state laws); low price. | [estimate] |
| Houseplant accessories | Grow lights are mains-powered; pots bulky or ceramic; Temu-heavy. | [estimate] |
| Phone accessories, LED lighting, toys, baby, beauty tools | Doc 10 risk 4–5, plus default vetoes (FCC, lithium, UL, CPSIA, MoCRA) and Schedule A targets. | [secondary] |
| Kitchen gadgets | FDA food contact; blender accessories are Schedule A targets (10). | [secondary] |
| Home organization | Bulky; storage ~80% cheaper on Temu (10). | [secondary] |
| Fitness accessories, camping | Weight and shipping cost; lithium and fuel (10). | [secondary] |
| Knives / EDC | eBay knife policy and state-by-state law. | [estimate] |
| Licensed collectibles merchandise (Pokémon, sports teams) | Branded goods: compliance default veto. | rule |

## 5. Risks (cross-niche)

1. **CJ US-warehouse depth is unknown for every niche** (09: no per-category data). This is the biggest single unknown. Collector supplies may mostly ship from China.
2. **Amazon Prime speed.** Our 2–8 day CJ US delivery [secondary, 09] loses to Prime on generic supplies. The edge has to be being where the buyer already is (eBay) plus bundles and specs, not speed.
3. **Collector buyers are exacting.** A wrong dimension means INAD. Listings must use CJ specs checked against a test order (Phase 1).
4. **Image rights.** CJ has no explicit image licence [unverified, 06]. The risk is the same for every niche, so it doesn't change the ranking.
5. **The scores are estimates.** Ties within ~0.3 should be treated as ties.

## 6. What would change our mind

- **Trends:** a niche whose core terms fell more than 20% over 12 months drops a demand point. A niche with high, rising volume (e.g. pet) gains.
- **Browse API:** eBay median prices under $20 for a niche's core types fail the margin criterion, whatever the demand.
- **CJ catalog:** fewer than 40 US-warehouse SKUs in a niche, or landed cost above ⅓ of the eBay median, is an effective kill (we need 20+ passing SKUs for the Phase 0 kill criterion).
- **Compliance card:** a ❌ veto removes the niche. A ⚠️ that removes the core product types (e.g. magnets in `tcg-supplies`) is treated as a veto.

## 7. Next actions with owners

| # | Action | Owner | Input / output |
|---|---|---|---|
| 1 | Run Trends on all 48 keywords; table level, 12-month growth and seasonality per niche | data-analyst | `python -m scout.trends --file data/evidence/trends/candidates.txt --out data/evidence/trends/candidates.csv` |
| 2 | Risk card per niche, including: magnets (tcg), LHAMA (hobby), Prop 65 PVC/brass/leather, brand terms in titles, children's-product line for tcg/figures | compliance-officer | `docs/decisions/` or `data/evidence/compliance/` |
| 3 | Max landed cost at $20 / $25 / $35 / $45 per niche; check FVF tier for card and coin supplies | sales-lead | `scout.margin` runs |
| 4 | Once keys exist: CJ US-warehouse SKU count, cost and stock per niche; eBay Browse active count and median price for the product types above | data-analyst | blocked on `CJ_API_KEY`, `EBAY_CLIENT_ID/SECRET` |
| 5 | Optional: Terapeak sell-through for the top 3 niches | Owner (manual export) | `data/evidence/terapeak/` |
| 6 | Niche decision (one primary, two backups, 20+ product types each) | head-of-marketing | `docs/decisions/0002-niche-selection.md` |
