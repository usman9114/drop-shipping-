# 0002 — Niche selection (Stage D)

> Owner: `head-of-marketing`. Date: 2026-11-03. Status: **decided, conditional.** The pick holds until the CJ and eBay Browse pulls in §7 run; the kill criteria in §3.8 decide whether it survives them.
>
> Inputs: `0001-niche-candidates.md` (candidates, prior scores), `docs/research/11-trends-candidates.md` (Google Trends, [data]), `12-compliance-niche-cards.md` (compliance verdicts), `13-sales-niche-economics.md` (landed-cost ceilings, margin screen), `14-video-ai-dropshipping-7-days.md` (external review, minor).
>
> **Evidence quality: low to medium.** Demand now has our own [data] (Trends), but it is relative interest, not volume, and carries an unexplained Apr–Jun 2026 spike. **Every CJ cost and CJ shipping figure is an [estimate]**, and eBay prices are [secondary] search-snippet snapshots. No eBay sold data, no Browse API competition data and no CJ US-warehouse catalog exist yet. Treat this as the best bet on current evidence, not a validated niche.

## 1. Decision

| Role | Niche | Weighted score (0001 → 0002) | Why, in one line |
|---|---|---|---|
| **Primary** | `tcg-supplies`: trading-card storage, protection and display | 3.75 → **3.83** | Strongest and most consistent demand signal (Trends 6/6 keywords up post-spike, high confidence), the strongest eBay fit ([primary] 08), and the only niche with an eBay US price snapshot that passes the margin model. Its price is compliance exposure (brand words, card art in CJ photos), which title and image discipline can manage. |
| Backup 1 | `vinyl-record-care` (dry, passive items only) | 3.50 → **3.45** | Cleanest compliance verdict, best Q4 lift (1.78). Weak on margin (stress 5–7% at snippet prices) and demand is low-confidence (5/6 keywords sparse). Works only as $28+ bundles. |
| Backup 2 | `hobby-modeling-tools` (tools only, no paints/glues/powered) | 3.70 → **3.30** | Tool kits pass the margin model (29% / 11.7%) and undercut branded kits. Demand fell to the weakest tier with low confidence (4/6 sparse); eBay knives policy still unread. |

- The primary leads #2 by **0.38**, just outside the ±0.3 tie band set in 0001. It stays top in every sensitivity case in §2c except one (margin drops to 2 *and* risk drops to 2 together).
- **The two backups are a tie** (0.15 apart). The order between them is decided by whichever has more CJ US-warehouse SKUs passing margin when the pull runs (§7).
- `coin-supplies` (3.25) is the fourth-place reserve. It is the cleanest compliance case but fails the $15 average-price hard filter on single items and no modeled bundle passes stress.
- Market: **US only**. Prices USD.

## 2. Evidence table

### 2a. Rescore on the §5 rubric (0–5, 5 = best; Risk and Temu/Amazon inverted)

Half points are used where new evidence moved a score but not by a full step.

| Niche | Demand 20% | eBay fit 15% | Margin 20% | Risk 20% | Temu/Amz 10% | Ops 10% | Listing 5% | **0002** | 0001 | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| **tcg-supplies** | **5** (+1) | 5 | **3.5** (+0.5) | **3** (−1) | 2 | 4 | **3.5** (−0.5) | **3.83** | 3.75 | +0.08 |
| vinyl-record-care | 3 | 4 | **2.5** (−0.5) | **4.5** (+0.5) | 3 | **3.5** (−0.5) | 4 | **3.45** | 3.50 | −0.05 |
| hobby-modeling-tools | **2** (−1) | 4 | **3.5** (−0.5) | **3.5** (−0.5) | 3 | 4 | 4 | **3.30** | 3.70 | −0.40 |
| coin-supplies | 2 | 5 | **1.5** (−0.5) | **4.5** (+0.5) | 3 | **4** (−1) | 4 | **3.25** | 3.35 | −0.10 |
| watch-accessories | **4** (+1) | 4 | **2** (−2) | **2.5** (−0.5) | 2 | **2.5** (−0.5) | **3** (−1) | **2.90** | 3.30 | −0.40 |
| collectibles-display | 3 | 4 | **1** (−2) | **3.5** (−0.5) | 3 | 2 | **3.5** (−0.5) | **2.78** | 3.30 | −0.52 |
| auto-detailing-tools | **3** (−1) | 3 | **2** (−1) | **3.5** (−0.5) | **1.5** (−0.5) | **2.5** (−0.5) | 3 | **2.70** | 3.30 | −0.60 |
| pet-grooming-supplies | **3** (−1) | 2 | **1** (−2) | 4 | **2** (−1) | **3.5** (−0.5) | 3 | **2.60** | 3.35 | −0.75 |

Bold cells changed vs 0001. Weighted = Σ(score × weight). The spread widened from 0.45 (3.30–3.75) to **1.23** (2.60–3.83): the new evidence separates the niches more than 0001's priors did.

**Hard filters** (compliance veto; average price < $15; oversize or hazmat):

| Niche | Result |
|---|---|
| tcg-supplies, vinyl, hobby, watch, auto, pet | Pass conditionally (vetoed sub-types excluded per 12) |
| coin-supplies | **Borderline fail** on average price: single items $7–18 [secondary, 13]; passes only as bundles, none of which pass stress |
| collectibles-display | Pass, but larger cases that would clear the margin are oversize |

### 2b. What changed per criterion, and why

| Criterion | Rule used for 0002 | Main moves |
|---|---|---|
| Demand | Trends post-spike `trend_score` and confidence from 11 [data]. Map: ≥ 0.6 → 5; 0.45–0.6 → 4; 0.25–0.45 → 3; < 0.25 → 2. Low confidence caps at 3. Q4 index < 1.0 costs nothing extra here but is listed as a launch-timing risk. | tcg 0.66 / high → **5**. watch 0.52 / high → **4**. vinyl 0.39 / low → 3 (capped). collectibles 0.35 / medium → 3. auto 0.27, Q4 0.85 → **3**. pet 0.11 / high, Q4 0.97 → **3** (high level expected in 0001 cannot be confirmed: Trends levels are not comparable across keywords). hobby 0.20 / low → **2**. coin 0.17 → 2. |
| eBay fit | No new evidence (Browse API blocked). 0001 values kept. | none |
| Margin | Sales-lead headroom (13 §3), adjusted where my review of its pricing disagrees. | **tcg 4.0 → 3.5:** the passing product is priced at $29 against a $22.99 generic incumbent [secondary], and at the default 8% return rate it fails stress (9.3%) [data: `python -m scout.margin --price 29 --cost 11.5 --ship 0`]. It passes at $30 (11.1%) or at 5% returns (16.1%). Headroom is real but thinner than 13 states. hobby 3.5 kept (kit at $26 undercuts a $26.99 generic). Others taken from 13. |
| Risk | Compliance verdict and rank in 12: "pass" → 4.5; "pass with conditions" mapped by rank. | coin, vinyl (pass) → **4.5**. pet 4. hobby (knives policy unread), auto (brass lead), collectibles → 3.5. **tcg → 3** (most brand-exposed; PSA wording; card art in CJ photos; magnet rule unconfirmed). **watch → 2.5** (brand dials in CJ strap photos can only be fixed by rejecting SKUs). |
| Temu/Amazon | 13 price anchors. | auto → 1.5 (Amazon brush sets $8–23, deals under $12). pet → 2 ($12–20 anchor). |
| Ops | 13 variant and weight notes. | coin → 4 (10+ capsule-size variants). watch → 2.5 (20+ strap variants). auto → 2.5 (brass weight, fitment returns). vinyl, pet → 3.5. CJ US depth is still unknown for every niche. |
| Listing | 12 image findings: share of CJ photos we will have to reject. | tcg, collectibles −0.5 (card art / branded figures inside cases). watch −1 (brand dials). Specs-driven upside unchanged. |

### 2c. Sensitivity of the primary pick

| Scenario | tcg score | Still #1? |
|---|---|---|
| Base | 3.83 | yes (vinyl 3.45) |
| Trends re-pull halves tcg growth → Demand 4 | 3.63 | yes |
| VeRO/brand exposure worse than expected → Risk 2 | 3.63 | yes |
| CJ costs higher, nothing passes at $25–30 → Margin 2 | 3.53 | yes, inside the tie band |
| Margin 2 **and** Risk 2 | 3.33 | **no**: ties hobby (3.30), behind vinyl (3.45) |
| 0001 sales-lead margin taken as-is (4.0) | 3.93 | yes |

### 2d. Key evidence behind the decision

| Claim | Label | Source |
|---|---|---|
| tcg Trends: 6/6 keywords up in the last 20 weeks vs a year earlier (median +0.66), 0/6 sparse, Q4 index 1.20 | [data] | 11; `data/evidence/trends/candidates-2026-11-03-niche-ranking.csv` |
| A uniform Apr–Jun 2026 spike hits all 48 keywords; scout 12-month growth figures are inflated and not used | [data] pattern, [estimate] cause | 11 |
| Collectibles were the largest contributor to eBay GMV growth (Q4 2025, Q3 2026); Pokémon #1 eBay search 2025; PSA terms in the top 10 | [primary] | 08 via 0001 |
| Generic 25-pack 35pt magnetic holders list at $22.99 on eBay US; branded $35–52 | [secondary] | 13; ebay.com/itm/167480493658 |
| Landed-cost ceilings: $25 → $9.10, $30 → $11.86, $40 → $17.37 at 8% returns | [data] model output on assumed fees | 13 §1 |
| tcg 25-pack at $29 / $11.50 landed: 28.7% base, 9.3% stress at 8% returns (fail); 32.1% / 16.1% at 5% (pass); $30 at 8%: 30.1% / 11.1% (pass) | [data] model output; inputs [estimate] | `python -m scout.margin --price 29 --cost 11.5 --ship 0 [--return-rate 0.05]`; `--price 30` |
| CJ product cost $7 and US shipping $4.50 for a 25-pack | [estimate] | 13 |
| tcg compliance: pass with conditions; PSA/BGS/game/league names banned; "PSA style" a title veto; magnets must be sealed; card art in photos means reject | [primary] eBay IP page snippet + [estimate] | 12 §0.2, §0.6, §1 |
| Magnet rule 16 CFR 1262 likely does not cover embedded, non-separable magnets | [unverified] | 12 §1 |
| eBay needs about 3× landed cost to pass (vs 2–2.5× on Shopify) | [estimate] | 14 |
| CJ US-warehouse depth per category: no data | — | 09, 12 §0.3 |

## 3. Primary niche: `tcg-supplies`

### 3.1 Target buyer

| Segment | Who | What they buy | Share of effort |
|---|---|---|---|
| A. Raw-card collectors | Adults (18+) collecting sports cards or TCG singles, buying 2–20 cards a month on eBay | Magnetic holders, rigid holders, binders, sleeves | 40% |
| B. Graded-slab owners | Adults who own or submit graded cards | Slab storage cases, slab stands, wall displays | 35% |
| C. Sealed-product collectors | Adults who keep sealed boxes and packs | Acrylic sealed-box cases, pack holders | 10% |
| D. Card sellers and breakers | eBay card sellers who ship singles | Bulk sleeves, rigid holders, resealable bags, card mailers | 15% |

All segments are **adults**. We never target or imply children (CPSIA line, 12 §1).

**Search words** (Trends keywords are [data]; the rest are my [estimate], to be checked against Browse API result counts):

- Trends-tested: `card display case`, `magnetic card holder`, `trading card binder`, `graded card case`, `card storage box`, `card sleeves`.
- Spec words buyers add: `35pt`, `55pt`, `75pt`, `130pt`, `180pt`, `magnetic`, `UV`, `9 pocket`, `side loading`, `zipper binder`, `graded slab`, `slab case`, `slab stand`, `20 slot`, `50 slot`, `3x4`, `screw down`, `sealed box case`.
- Pending compliance (§3.6): `toploader`, `one touch`, `penny sleeves`, `team bags`, `card saver`.

### 3.2 Positioning vs Amazon and Temu

| | Amazon | Temu | eBay incumbents (generic) | **Us** |
|---|---|---|---|---|
| Wins on | Prime speed, brands (Ultra Pro, BCW) | Lowest price | Being where the card buyer is | Being where the card buyer is, **exact fit**, **job-sized bundles** |
| Loses on | Not where cards are bought | 7–15 day shipping, vague specs | Thin specs, card art in photos, single packs | Slower than Prime; not the cheapest |

**Positioning line:** *the right holder for the card you just bought, specified to the millimetre, in the quantity you actually need, shipped from a US warehouse.*

Concretely:

1. **Fit first.** Every listing states card thickness (pt), interior and exterior mm/in and capacity, and carries a fit chart in the description. Wrong fit is the main INAD risk, so this cuts returns as well as selling.
2. **Bundles sized to a job.** "25 magnetic holders 35pt + 5 stands", "mixed-thickness magnetic assortment", "slab case 20-slot + 20 slab sleeves". Temu rarely bundles across thickness; Amazon brands sell single-SKU packs.
3. **Price in the middle.** Target $27–35: above the cheapest generic, well below branded ($35–52). We do not compete at $15–23.
4. **No speed claims.** We state handling time and the eBay delivery estimate only (FTC Mail Order Rule, 12 §0.1). We lose to Prime on speed and say nothing about it.
5. **Clean, honest photos.** Empty product, no borrowed card art, consistent lifestyle backgrounds. Incumbents often show licensed cards inside the holder.

### 3.3 Product types to pull from CJ (24)

Every type is generic and unbranded. The excluded list (12 §1) applies to all: no licensed or character art; no "for Pokémon/Magic/Yu-Gi-Oh"; no LED or USB lighting; no loose or removable magnets; no flexible PVC without a PVC-free statement; no "PSA/BGS style"; no children's albums. "Unit" is the eBay listing unit; singles under $25 are sold only inside bundles.

| # | Product type | eBay unit (target price) | Conditions | Margin status |
|---|---|---|---|---|
| 1 | Magnetic card holders, 35pt | 25-pack (+ stands) ($29–32) | Sealed magnets confirmed in writing | Modeled pass at $30 [estimate] |
| 2 | Magnetic holders, mixed-thickness assortment (35/55/75/100/130pt) | 25–30 pack ($30–35) | as #1 | unmodeled |
| 3 | Thick-card magnetic holders, 180pt+ (relic/patch cards) | 10–15 pack ($27–32) | as #1 | unmodeled |
| 4 | Stands for magnetic holders (acrylic or PP) | bundle add-on or 10-pack | — | add-on |
| 5 | Rigid card holders 3×4 in | 100-pack + sleeves ($25–28) | Rigid, unplasticized material statement | unmodeled, thin |
| 6 | Card sleeves, PP, bulk | 1,000 + inside bundles only | PP only; PVC excluded | add-on (fails alone) |
| 7 | Semi-rigid card holders (submission-size) | 50–100 pack ($25–30) | Generic name only (§3.6) | unmodeled |
| 8 | Resealable card bags | 100–200 pack, bundle | Generic name only | add-on |
| 9 | 9-pocket zipper binder (360 / 720 cards), side-loading | 1 ($28–35) | PP pages, PVC-free | **Modeled fail at $28 / $15 landed**; needs ≤ $10 landed or $35 |
| 10 | 4-pocket binder for rigid/magnetic holders | 1 ($28–35) | as #9 | unmodeled |
| 11 | Graded-slab binder (slab pockets) | 1 ($30–40) | as #9 | unmodeled |
| 12 | Replacement 9-pocket pages | 50–100 pack ($25–30) | PP, PVC-free statement | unmodeled |
| 13 | Graded-slab storage case, 20–50 slot (aluminium or PP hard case) | 1 ($30–45) | Exact slot dimensions in mm | unmodeled; weight risk |
| 14 | Graded-slab storage box, plastic, 1–2 row | 1–2 pack ($25–30) | — | unmodeled |
| 15 | Graded-slab display stands / easels | 10-pack ($25–28) | — | unmodeled |
| 16 | Graded-slab wall display frame (multi-slab) | 1 ($30–40) | No UV claim without report | unmodeled; breakage risk |
| 17 | Acrylic sealed-box display case (booster-box size) | 1–2 pack ($28–40) | Interior mm stated; no game names | unmodeled; breakage risk |
| 18 | Acrylic sealed-pack holders | 10-pack ($25–30) | as #17 | unmodeled |
| 19 | Single-card screw-down acrylic holders | 10–20 pack ($25–30) | — | unmodeled |
| 20 | Multi-card wall display frame / UV display case | 1 ($28–40) | "UV" only with supplier test report | unmodeled; breakage risk |
| 21 | Plastic card storage boxes (800–3,200 count) / sorting trays | 2–4 pack ($25–30) | Cardboard boxes excluded (bulk) | unmodeled; dimensional weight |
| 22 | Unbranded deck boxes (100+ sleeved cards) | 4–6 pack ($25–30) | No printed art | unmodeled |
| 23 | Card-seller shipping kit (rigid card mailers + holders + bags) | 50-mailer kit ($25–30) | Light rigid mailers only; no boxes | unmodeled; segment D test |
| 24 | Acrylic card centering gauge + microfibre slab cloths | kit or add-on | No LED loupe, no lithium | add-on |

Only #1 has a modeled margin and #9 a modeled fail; everything else is **unmodeled**. CJ US-warehouse availability for all 24 is **unknown**. The pull in §7 settles both.

### 3.4 Price band and landed-cost ceiling

| Rule | Value | Basis |
|---|---|---|
| Listing price band | **$25–45**, sweet spot **$27–35** | 13 §1; generic eBay band $23–30 [secondary] |
| Floor | No listing below **$25**. Items that only work cheaper go inside bundles. | 0001 §2a, 13 §1 |
| Landed-cost ceiling (CJ product + CJ US shipping + CJ handling fee) | Use the **8% return-rate column** until we have return data: $25 → **$9.10**, $27 → ~$10.2, $30 → **$11.86**, $35 → ~$14.6, $40 → **$17.37**, $45 → ~$20.1 | 13 §1 [data, model]; $27/$35/$45 interpolated |
| Screening shortcut | Landed ≤ **36% of price** at $25–30, ≤ **40%** at $35–45 | from the same table |
| Stretch (after Phase 1–2 return data) | 5% return column for soft goods (holders, sleeves, binders); acrylic and slab items stay at 8% or higher | 13 used 5% for collector supplies; I don't accept it for acrylic |
| Ad rate assumption | Model default 5%; **re-run at 7%** before go-live (13 §4 warns tcg may need 7–8%) | 13 §4 |

### 3.5 Listing standards

**Title formula** (eBay max 80 characters; every element factual and sourced from CJ specs checked on the test order):

```
[Count] [Generic product type] [Key spec: pt / slots / interior size] [Material or verified feature] for [Trading / Sports Cards | Graded Card Slabs] [+ bundle extra]
```

Examples (illustrative, not approved SKUs):

- `25 Magnetic Card Holders 35pt with 5 Stands, Clear, for Trading and Sports Cards`
- `Graded Card Slab Storage Case 50 Slot, Aluminium, Foam Insert, Lockable`
- `9 Pocket Zipper Card Binder 360 Cards, Side Loading, PVC Free Pages`

Rules:

- Lead with count and product type. No brand, game, league or grader name anywhere in the title.
- Units: pt for thickness; mm in the description, inches in the title only when that is how buyers search (3x4, 12x12).
- No ALL CAPS words, no "L@@K", no "!", no "fast shipping", no "best".
- Spec words only if the CJ spec sheet supports them **and** the test unit matches.

**Required item specifics** (final names come from the eBay Taxonomy API `getItemAspectsForCategory`, §7; until then this is the house list):

| Item specific | Value rule |
|---|---|
| Brand | `Unbranded` |
| MPN | `Does Not Apply` |
| Type | Generic type, e.g. "Magnetic Card Holder", "Card Binder", "Slab Storage Case" |
| Card thickness / Compatible card size | pt value(s) or slab dimensions |
| Capacity | Number of cards or slabs held |
| Number in pack | Exact count; matches the title |
| Material | PP, PET, acrylic (PMMA), aluminium, etc., per CJ spec |
| Interior dimensions | mm (custom specific) |
| Exterior dimensions | mm (custom specific) |
| Color | as pictured |
| Features | Only verified: "Magnetic Closure", "Zipper", "Side Loading", "UV Resistant" (only with a report) |
| Country of manufacture | from CJ data |
| Package weight / size | for calculated shipping and dimensional checks |

**Description structure** (mobile-first, no external links, no active content):

1. One sentence: what it is and what it fits.
2. **What's in the box:** counts per component.
3. **Fit chart:** thickness (pt) → holder size; slab dimensions in mm and in. One allowed fit line for graded slabs: "fits standard-thickness graded card slabs from major grading companies" (12 §0.6). No grader names.
4. **Specs table:** material, interior and exterior mm, weight, closure type.
5. **Not included / not affiliated:** "Cards not included. Not affiliated with any card manufacturer, game publisher, league or grading company."
6. **Shipping:** ships from a US warehouse; our handling time; delivery per eBay's estimate. No "fast" or "next-day".
7. **Returns:** 30-day returns, buyer-friendly wording.

**Banned words** (titles, item specifics, descriptions, tags):

| Group | Banned |
|---|---|
| Graders | PSA, BGS, Beckett, CGC, SGC, PCGS, NGC, "PSA style", "PSA size", "BGS style" |
| Games and IP | Pokémon / Pokemon, MTG, Magic: The Gathering, Yu-Gi-Oh, Lorcana, One Piece, Digimon, Flesh and Blood, Star Wars, Marvel, Disney |
| Card makers and leagues | Topps, Panini, Upper Deck, Bowman, Donruss, Fleer, Leaf, NFL, NBA, MLB, NHL, MLS, WNBA, NCAA, FIFA, UFC, WWE |
| Supply brands | Ultra Pro, BCW, Pro-Mold, Cardboard Gold, Vault X, Dragon Shield, Gamegenic, Ultimate Guard, KMC, "… style", "… compatible" |
| Pending trademark check (do not use until compliance clears) | "One-Touch", "Toploader" / "Top Loader", "Card Saver", "Team Bags", "Penny Sleeves" |
| Children | kids, children, toy, "gift for kids", "for boys/girls" |
| Unproven claims | archival, acid-free, UV-proof, 99% UV, "protects value", "investment grade", "museum quality", authentic, official, licensed, genuine, "PSA approved", "grading safe" |
| Speed and hype | fast, next-day, same-day, best, #1, L@@K, rare, hot |

"Archival", "acid-free" and "UV resistant" move from banned to allowed only for a SKU with a supplier spec sheet on file.

**Image rules:**

- **Source:** CJ images only (`bigImage`, `productImageSet`, `variantImage`). Store the CJ source URL with every generated image.
- **Reject the SKU** (do not edit the image) if any CJ image shows:
  - card art or a branded card inside the product
  - a grading label, logo, watermark, price sticker or text
  - Clean variants from other CJ images may be used instead.
- **AI changes surroundings only:** background, lighting, upscaling, lifestyle scene (a desk, shelf or display wall).
  - Never add cards, slabs or art into or onto the product.
  - Never fill an empty holder.
  - Never alter product pixels.
- **Image set:** main image on plain white or light-grey, product filling 80–90% of the frame, ≥ 1600 px on the long side. Follow with angle shots, a component shot for bundles, and one lifestyle scene.
- **eBay picture policy:** no text, badges, borders or watermarks. Dimensions go in the description, not on the image.

**Tone:** precise, spec-first and collector-literate, like a good hobby-shop clerk. Plain English, short sentences, metric and imperial. No hype, no exclamation marks, no emoji, no urgency, no claims we cannot document.

### 3.6 Compliance conditions carried from 12

- Sealed, non-removable magnets confirmed in writing for every magnetic SKU; 16 CFR 1262 applicability confirmed by counsel before magnetic SKUs go live.
- PVC-free / unplasticized statement for sleeves, pages and rigid holders, or exclude the SKU (Prop 65 DEHP).
- Trademark status of "one-touch", "toploader", "card saver", "team bags" and "penny sleeves": compliance-officer to check on USPTO TESS before any of them enters a title. Until then the generic descriptions in §3.3 apply. This costs search reach, so it is worth checking early.
- Supplies FVF tier (13.6% vs 13.25% card tier): unverified; the model already uses 13.6%.

### 3.7 Expected weaknesses we accept

- We are not the cheapest. Buyers who sort by price go to the $22.99 generic or Temu.
- Prime beats us on speed for anyone who shops Amazon first.
- Acrylic and slab items add breakage risk; they are second-wave SKUs after holders, binders and boxes.

### 3.8 Kill criteria for `tcg-supplies`

Thresholds are my judgement unless a source is named. Any one **kill** trigger moves us to the leading backup.

| # | Stage | Trigger | Action | Measured by |
|---|---|---|---|---|
| K1 | Key arrival (CJ) | < **40** CJ US-warehouse SKUs across the 24 types, **or** < **20** SKUs passing ≥ 20% base / ≥ 10% stress at 8% returns using real CJ cost + US shipping and the eBay Browse median price | **Kill** | data-analyst + sales-lead |
| K2 | Key arrival (CJ images) | After rejecting SKUs whose CJ images show card art, logos or grading labels, < **20** margin-passing SKUs remain | **Kill** | free-model image screen + compliance-officer spot check |
| K3 | Key arrival (Browse) | Median active price (US-located, Unbranded) for the core units (magnetic holder 25-pack, slab case 20+ slot, 9-pocket binder) < **$22** | **Kill** (no room for $27–35) | data-analyst |
| K4 | Key arrival (Browse) | For ≥ 2 of the 3 core units, ≥ **60%** of the first 50 Best Match results are US-located generic listings priced below our break-even price (price at which landed = ceiling) | **Kill** | data-analyst |
| K5 | Compliance | Embedded magnets ruled in scope of 16 CFR 1262 **and** no compliant alternative | Drop magnetic types; **kill** if < 20 passing SKUs remain | compliance-officer |
| K6 | Phase 1 test orders | Any of: median delivery > 5 business days; interior dimensions off by > 1 mm from CJ spec on ≥ 2 of 5 units; ≥ 1 of 5 acrylic/slab items arrives cracked; product differs from CJ image | Drop affected SKUs; **kill** if < 20 remain | sales-lead (orders) + head-of-marketing (review) |
| K7 | Phase 2 live (60 days) | Realized net < 15%, **or** defect rate ≥ 2%, **or** INAD returns > 8% | **Kill** (00-summary Go criterion) | data-analyst |
| K8 | Phase 2 live | ≥ 2 VeRO takedowns or one account-level IP warning | **Kill** immediately | compliance-officer |
| W1 | Trends re-pull | tcg post-spike YoY ≤ 0 on a second-day pull | **Re-rank** (Demand → 3, score 3.43: ties vinyl), not kill | market-researcher / data-analyst |

## 4. Alternatives considered

| Option | Score | Why not primary |
|---|---|---|
| `vinyl-record-care` | 3.45 | **Backup 1.** Cleanest compliance and best Q4 lift (1.78) for a Nov/Dec start. No modeled product passes stress (5–7%); demand is low-confidence (5/6 sparse); sleeves are bulky. Needs $28+ dry bundles (sleeves + brush + stand). |
| `hobby-modeling-tools` | 3.30 | **Backup 2.** Generic 40-piece kit at $26 passes (29.1% / 11.7%) and undercuts branded kits. Demand is the weakest signal in the set (`sprue cutter` unusable, 4/6 sparse). eBay knives policy unread. Strong Q4 index (1.67) is driven by sparse keywords. |
| `coin-supplies` | 3.25 | Reserve. Clean compliance pass and strong eBay fit, but single items $7–18 and no bundle passes stress (0.7–2.7%); 10+ size variants. |
| `watch-accessories` | 2.90 | Demand is second-best (0.52, high), but straps carry brand dials in CJ photos and 20+ variants, single items stress-fail, and the box fails base. Brand exposure is the highest in the set. |
| `collectibles-display` | 2.78 | Fails margin across the board (11–20% base, negative stress); fragile and bulky. Its best items (slab and sealed-box acrylic) are already inside the tcg list (#16–20). |
| `auto-detailing-tools` | 2.70 | Amazon sub-$12 anchor; Q4 trough (0.85) for a November start; brass lead and fitment returns. |
| `pet-grooming-supplies` | 2.60 | Weakest growth (0.11), Q4 flat, $12–20 Temu/Amazon anchor, every modeled product fails stress. Control niche confirmed as a control. |
| Merge tcg + collectibles-display into one "collector display" niche | — | Rejected. Collectibles adds bulk and breakage without demand evidence. The card-relevant acrylic types are already in §3.3. |
| Wait for API keys before choosing | — | Rejected. Phase 0 needs a niche to scope the CJ and Browse queries. The pick is cheap to reverse because the kill criteria fire on the first pull. |

## 5. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **CJ US-warehouse depth for card supplies is thin;** most stock ships from China | medium-high [estimate] | kill (K1) | Pull first; backups ready; don't build listings before the pull |
| 2 | **CJ costs higher than the $7 + $4.50 estimate.** Shipping is the most sensitive input ($4 vs $6.50 moves a $26 item ~8 points, 13 §4) | medium | margin → 2; score still #1 but in the tie band | Use real CJ freight quotes per SKU; price at $30+ |
| 3 | **CJ photos show licensed cards inside holders** | high [12] | fewer usable SKUs (K2) | Reject per SKU; prefer variants with empty product |
| 4 | **VeRO / brand complaints** (PSA, Ultra Pro "one-touch", game IP) | medium | account risk (K8) | Banned-word linter in the listing generator; compliance sign-off on every title in Phase 2 |
| 5 | **Price position:** buyers anchor on the $22.99 generic | medium | low conversion | Bundles and fit charts justify +$5–8; Phase 2 measures views → sales vs incumbents |
| 6 | **Promoted Listings needs 7–8%**, not 5% | medium | −2 to −3 margin points (13 §4) | Re-run ceilings at 7% before go-live |
| 7 | **Trends artifact:** the 2026 rise is partly a Google-side level shift | medium | demand overstated | Re-pull on another day (W1); Terapeak sold data from owner |
| 8 | **Card-market cycle** (TCG booms cool) | low-medium, 60-day horizon | demand drop | Sports + TCG + slab segments diversify; 60-day test limits exposure |
| 9 | **Young buyers** (TCG skews young) pull us across the CPSIA line | low | regulatory | Adult positioning, no art, banned "kids" words |
| 10 | **Magnet rule** applies to embedded magnets | low [unverified] | lose types #1–4 (K5) | Counsel confirmation; non-magnetic types as fallback |
| 11 | **CJ image licence** not explicit (06) | applies to all niches | blocks scale | Written permission or CJ paid photo service (owner) |

## 6. What would change our mind

- **CJ pull** (K1, K2): too few US SKUs or passing SKUs → switch to the backup with more passing SKUs. If neither backup has 20, consider `coin-supplies` bundles, then re-open the candidate list (sneaker care was the 0001 reserve).
- **Browse API** (K3, K4): eBay medians under $22 or a wall of cheap US sellers → kill tcg; check whether vinyl kit bundles sit at $28+.
- **Trends re-pull** (W1): tcg growth disappears → score 3.43, a tie with vinyl; the CJ pull then decides.
- **Sales-lead real-cost rerun:** if tcg margin drops to 2 and compliance moves tcg risk to 2 (e.g. a "toploader"/"one-touch" trademark finding plus heavy image rejection), tcg falls to 3.33 and vinyl leads.
- **Terapeak sell-through** (owner, optional): < 50% sell-through on the core units fails the 00-summary thesis condition (a) and triggers K1-level review.

## 7. Next actions with owners: verify once keys arrive

Order matters: rows 1–4 run first and can kill the niche before any listing work.

| # | What must be verified | Owner | Command / output | Kill link |
|---|---|---|---|---|
| 1 | **CJ US-warehouse catalog** for each of the 24 product types (§3.3): product search by generic keyword, US warehouse only. Per SKU and variant record: sell price, US stock quantity, weight and dimensions, materials, variant count, image URLs (`bigImage`, `productImageSet`, `variantImage`). Same pull, smaller, for vinyl and hobby. | data-analyst | `data/evidence/cj/tcg-supplies-<date>.csv` (+ `vinyl-…`, `hobby-…`). Confirm the warehouse-filter and stock endpoints in CJ's API docs before coding. | K1 |
| 2 | **CJ US shipping cost and handling fee** to 3 sample zips (East, Central, West) per SKU, using CJ's freight calculation endpoint. Record the carrier and quoted days. | data-analyst | same CSV, `ship_usd`, `ship_days` columns | K1, K6 |
| 3 | **eBay Browse API competition and price** for ~25 queries (the 6 Trends keywords + one per product type): total active count; price p25 / median / p75 filtered to US item location and Brand = Unbranded; share of US-located sellers; free-shipping share; first-50 Best Match price list. Counts and prices only: no copying of titles, text or images. | data-analyst | `data/evidence/ebay/browse-tcg-<date>.csv` | K3, K4 |
| 4 | **Per-SKU margin rerun** with real CJ cost + shipping at the Browse median, at 8% returns and 5% / 7% ad rates; list passing SKUs; recheck the $25 floor | sales-lead | `python -m scout.margin …` per SKU → `data/evidence/margin/tcg-<date>.csv` | K1 |
| 5 | **CJ image screen:** classify every image for card art, logos, grading labels and text (free OpenRouter model); compliance spot-checks 10% | data-analyst (free model) + compliance-officer | `python -m scout.llm …` → `data/evidence/cj/tcg-image-flags-<date>.csv` | K2 |
| 6 | **eBay category and item specifics:** Taxonomy API category suggestions for each product type and `getItemAspectsForCategory` (required / recommended aspects); confirm the FVF tier for card supplies on eBay's fee page | data-analyst (API) + sales-lead (fee page) | `data/evidence/ebay/taxonomy-tcg-<date>.json`; updates §3.5 | — |
| 7 | **Trademark check** on "one-touch", "toploader", "card saver", "team bags", "penny sleeves"; **16 CFR 1262** applicability to embedded magnets; supplier PVC-free and sealed-magnet statements for shortlisted SKUs | compliance-officer | `data/evidence/compliance/tcg-<date>.md` | K5 |
| 8 | **Trends re-pull** for tcg, vinyl and hobby on a different day (`--sleep 5`) to test the Apr–Jun artifact | market-researcher (run) / data-analyst (compare) | `data/evidence/trends/candidates-<date2>.csv` | W1 |
| 9 | **Terapeak sold data** for the 6 Trends keywords + the 3 core units (sell-through, average sold price) | Owner (manual export) | `data/evidence/terapeak/` | thesis (a) |
| 10 | **CJ image licence:** written permission or paid photo service quote | Owner | `docs/decisions/` note | blocks scale |
| 11 | **Final review** of the shortlist (pricing from row 4, flags from rows 5 and 7) before any Phase 1 test order | head-of-marketing | `docs/decisions/0003-tcg-shortlist.md` | — |

**Blocked on the owner:** `CJ_API_KEY` (rows 1, 2, 5), `EBAY_CLIENT_ID` / `EBAY_CLIENT_SECRET` (rows 3, 6), optional `OPENROUTER_API_KEY` credit (row 5), Terapeak export (row 9).
