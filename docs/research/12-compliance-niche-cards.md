# 12 — Compliance risk cards for the 8 candidate niches

> `compliance-officer`, 2026-11-03. Stage C' of `docs/plan/ai-team.md`. Inputs: `docs/decisions/0001-niche-candidates.md` (product-type lists), research docs 01, 05, 06, 10, `data/evidence/trends/candidates.txt`.
> **Risk screening, not legal advice.** Where a call is uncertain it is marked `[unverified]` or "counsel to confirm". Evidence labels follow `_team-rules.md`: [primary] official source, [secondary] law-firm/vendor/blog, [estimate] our judgment.
> **No [data] here:** no CJ catalog pull exists yet, so every "CJ source image present" and "ships from US warehouse" check is deferred to the SKU-level gate (section 0.3).

## 0. Shared rules

### 0.1 Checks that apply to every niche

| Check | Rule applied to all 8 niches |
|---|---|
| eBay policy | Dropshipping from a wholesale supplier (CJ) is allowed; buying from a retail marketplace is not [primary, doc 01]. CJ is a wholesale supplier, so OK. |
| Claims | State handling and delivery time from CJ US-warehouse reality (2-5 days typical, 2-8 range [secondary, doc 09]) plus our own handling. No "fast"/"next-day" claims. FTC Mail Order Rule applies [secondary, doc 05]. |
| Images | CJ image only (`bigImage`/`productImageSet`/`variantImage`), product pixels untouched, no text/borders/watermarks [primary eBay picture policy, doc 06]. **Open issue:** doc 06 found no image-licensing clause in CJ's ToS. Written permission or CJ's paid photo service is still needed before listing at scale. That affects all 8 niches equally and is not repeated per card. |
| Safety default | Veto on children's products, radio, lithium, mains power without UL/ETL, cosmetics/ingestibles, branded goods. Per-niche exclusion lists below apply it. |

### 0.2 Wording rules that apply to every niche (eBay IP policy)

eBay's own IP page says a brand name may appear only when the product is specifically designed for that brand and a compatibility phrase ("compatible with", "fits", "for") precedes it. If the product is not specifically compatible, the brand name must not appear at all. A logo on an item not made by the brand cannot be listed [primary, https://www.ebay.com/sellercenter/resources/intellectual-property, search-snippet reading; re-read the live page before launch].

**Our house rule, stricter than eBay's:** no third-party brand or licensed-character name in titles, item specifics, descriptions or search tags, with one narrow exception. A compatibility phrase may name a brand only when (a) the item is genuinely sized for that product, (b) compliance has approved the specific term, and (c) the brand name is not in the first 40 characters of the title. Default is to describe by dimension and generic type.

### 0.3 SKU-level gate (before any listing in any niche)

1. CJ source image URL saved and image has no text, border, watermark, logo or licensed art.
2. Product photo shows no brand marks or character art (reject the SKU, do not crop it).
3. Reverse-check the shape against USPTO design patents (Google Patents "design" filter or USPTO search) for any SKU that looks like a trending gadget `[manual step; no tool in repo yet]`.
4. Material/chemistry question answered by the supplier in writing for PVC, brass, leather, painted or coated items (Prop 65).
5. Test order received and photographed before the SKU goes live (doc 06 section 4).

### 0.4 Design-patent / Schedule A finding (checked for this card set)

A web search for Schedule A (N.D. Ill.) design-patent suits on magnetic card holders, foam cannons, pet clippers/brushes and watch tools **found no case on those product types** [secondary, PatSnap case digests; search is not a docket search]. It did find Schedule A suits on hairbrushes (Bounce Curl), a metal nibbler tool attachment, friendship-bracelet makers, brooms and battery packs, with outcomes spread across voluntary dismissal, settlement and default judgment [secondary]. Doc 10 reports defendants won no resolved cases 2023 to mid-2024 [secondary].

**Reading:** absence of a hit is weak evidence. It does not clear any product. It does mean the risk is a per-SKU check (step 3 above), not a niche-level veto. Hairbrush-shaped pet brushes are the closest analogy to a litigated product type.
Sources: https://www.patsnap.com/resources/blog/litigation/bounce-curl-llc-v-schedule-a-defendants-permanent-injunction-settlement-in-hair-brush-design-patent-case-patsnap-eureka/ ; https://www.patsnap.com/resources/blog/litigation/guangdongsheng-v-schedule-a-defendants-metal-nibbler-patent-patsnap-2/ ; docs/research/10-category-risk.md.

### 0.5 Prop 65 finding (checked for this card set)

California AG notices and settlements concentrate on **DEHP (a phthalate plasticizer) in flexible vinyl/PVC parts** and **lead in brass** (a settlement example uses < 100 ppm lead as "lead-free" for brass, and 1,000 ppm DEHP as a reformulation limit; thresholds vary by product and settlement) [secondary, CA AG documents surfaced by search, e.g. https://oag.ca.gov/system/files/prop65/notices/2023-01944.pdf ; https://oag.ca.gov/system/files/prop65/settlements/2021-00185S0388.pdf; SGS 2026 summary https://www.sgs.com/news/2026/07/safeguards-09726-california-proposition-65-chemical-reformulation-in-consumer-products, figures not verified]. Penalties up to $2,500 per violation per day [secondary]. Doc 10: > 5,000 notices in 2025, mostly lead in glass, ceramics and brass.
**Consequence for us:** flexible PVC and brass/leaded metal are the two material triggers. Require "PVC-free"/"lead-free brass" statements from the supplier, or exclude the SKU, or add a Prop 65 warning (our decision, counsel to confirm).

### 0.6 "Graded card" / "PSA" wording finding

eBay itself runs PSA grading and Authenticity Guarantee for trading cards [primary, https://www.ebay.com/help/buying/paying-items/using-psa-grading-service?id=5639]. Listings on eBay (including eBay.de) use phrases like "PSA Style" for unbranded holders [secondary, search result listing]. The search did **not** show whether PSA or eBay has objected to that wording, nor any nominative-fair-use ruling `[unverified]`.
**Decision rule:** "graded card" and "graded card slab" are descriptive and acceptable. "PSA", "BGS", "Beckett", "CGC", "SGC", "PCGS", "NGC" never go in titles, tags or the first paragraph. A single descriptive fit line in the body ("fits standard-thickness graded card slabs from major grading companies") is the most we do. "PSA style/size" is a **veto in the title** because it is the exact phrase most likely to draw a VeRO report [estimate].

---

## 1. tcg-supplies

| Check | Result |
|---|---|
| eBay policy | OK. Trading cards have a 13.25% FVF tier; supplies may be 13.6% [primary doc 01 / unverified for supplies]. No prohibited category. |
| IP | Main risk. Incumbent brands (Ultra Pro, BCW etc.) and game IP (Pokemon, Magic, sports leagues) are VeRO-active. Grading-company marks (section 0.6). Generic card holders, sleeves and binders are not design-patent-prone as far as found (section 0.4: no hit for magnetic card holders `[unverified]`). Sleeves printed with character art are veto. |
| Safety regs | CPSIA: adult-collector positioning only, no cartoon art, no "kids"/"for children" wording; plain card holders are general-use [estimate; counsel to confirm]. CPSC magnet rule (16 CFR 1262) concerns loose/separable magnets in consumer products; magnetic holders have embedded, non-separable magnets, likely outside scope `[unverified]`. Require supplier confirmation that magnets are sealed and not removable. Flexible PVC sleeves: Prop 65 DEHP (section 0.5). No electronics. |
| Claims | No "PSA-approved/safe/compatible" claims. "Archival", "acid-free", "UV-resistant" and "fits 35pt/55pt" need a supplier spec sheet. No "ships in 1-2 days" unless the CJ warehouse is US and tested. |
| Images | CJ image must not show branded cards, licensed card art or grading labels in the picture. Many card-holder photos include a Pokemon/sports card inside: **reject or find a clean variant**. Clean-background enhancement is fine. |
| Verdict | ⚠️ pass with conditions |

**Exclude:** anything printed with TCG/sports art; sleeves/deck boxes sold "for Pokemon/Magic/Yu-Gi-Oh"; PVC soft sleeves without a PVC-free statement; LED-lit cases; magnetic holders where magnets are loose or removable; "PSA/BGS style" holders; novelty children's card albums.
**Do:** "magnetic card holder, 35pt, fits standard trading cards", "graded card slab storage box, holds 20", "side-loading toploader" `[toploader is a generic term, brand-free, but confirm]`, interior dimensions in mm.
**Don't:** "PSA", "BGS", "Pokemon", "MTG", "NFL", "Topps"; "Ultra Pro style"; "kids"; "perfect gift for children".

## 2. collectibles-display

| Check | Result |
|---|---|
| eBay policy | OK. Display cases are ordinary merchandise. |
| IP | Biggest wording risk: LEGO, Funko, Hot Wheels, Matchbox, sports leagues. Cases with printed character art, team logos or a licensed minifigure in the photo are veto. Generic acrylic cubes are not design-patent-prone `[estimate; no Schedule A hit found]`. |
| Safety regs | CPSIA: display cases are general-use but figure buyers skew young. Avoid "toy", "for kids", "Lego display for children" wording and any toy-box styling [estimate; counsel to confirm]. Acrylic edges and breakage are a quality, not regulatory, issue. UL/ETL and lithium: LED-lit cases are a default veto. Glass: Prop 65 lead in glass (doc 10), so exclude glass. |
| Claims | "UV protection / 99% UV" is an FTC-substantiation claim: only with a supplier test report, otherwise say "clear acrylic". "Dustproof" is fine if the case closes. No "fits all LEGO" claims. Quote exact interior dimensions from CJ and verify on the test unit. |
| Images | Photos usually show a branded figure or minifigure inside. Reject SKUs where the CJ image contains LEGO/Funko/character art, or use only clean empty-case images. Do not composite a different figure in (misrepresentation of the item, picture policy). |
| Verdict | ⚠️ pass with conditions |

**Exclude:** LED-lit or USB-powered cases; glass domes/glass shadow boxes; cases printed with logos/characters; "Lego-compatible" baseplates and "compatible with Hot Wheels" cases in titles; helmet/jersey cases (oversize, doc 0001); anything marketed to children.
**Do:** "acrylic display case 12x12x12 in, clear, dust cover", "1:64 die-cast wall display case, 24 slots", "minifigure-size display frame" (generic).
**Don't:** "LEGO", "Funko Pop", "Hot Wheels", "Pokemon", "MLB/NFL licensed"; "UV-proof" unless documented.

## 3. coin-supplies

| Check | Result |
|---|---|
| eBay policy | OK for supplies. We do **not** list coins or bullion (counterfeit/authenticity rules, outside CJ goods). Supplies FVF may be 13.6%, not 13.25% [unverified]. |
| IP | Low. Avoid grading/third-party marks: PCGS, NGC, ANACS, and publisher marks (Whitman, Lighthouse, Littleton, Dansco, Intercept Shield) `[trademark status unverified, treat as marks]`. Generic holders and albums are not design-patent-prone `[estimate]`. |
| Safety regs | The main issue is **PVC flips** (Prop 65 DEHP, and PVC damages coins) -> list only PVC-free. Brass/lead: loupe housings, brass display stands, vintage-style metal cases could carry lead (section 0.5). Wooden display cases: possible formaldehyde (composite wood, TSCA Title VI) `[unverified for our SKUs; ask supplier for CARB/TSCA statement]`. No CPSIA exposure if marketed to adult collectors. No electronics (LED loupes and scales are vetoed: button-cell lithium). |
| Claims | "PVC-free", "archival", "acid-free" must be on the supplier spec. "Safe for rare coins" is an implied-warranty claim: avoid. Stated capsule inner diameters must be measured on the test unit. |
| Images | Photos often show real coins or commemorative items: coin faces are generally fine but must not be a depicted copyrighted medal or a non-US-mint replica sold as authentic. Reject images with watermarks/price stickers. |
| Verdict | ✅ pass (minor conditions: PVC-free proof, no coins sold) |

**Exclude:** coins, bullion, "replica"/"souvenir" coins (counterfeit/Hobby Protection Act issues `[unverified]`); PVC flips; LED loupes; digital scales; brass novelty cases without lead statement; cotton gloves with printed brands.
**Do:** "PVC-free 2x2 coin flips, 100 pack", "coin capsules 40 mm inner diameter, 50 pack with foam rings", "coin album, 20 pockets per page".
**Don't:** "PCGS/NGC holder style", "Whitman compatible", "collectible coin" with product images of coins offered for sale.

## 4. vinyl-record-care

| Check | Result |
|---|---|
| eBay policy | OK. Music category FVF is 15.3% for records themselves [primary doc 01]; accessories are probably the general 13.6% `[unverified]`. We do not sell records, turntables or electronics. |
| IP | Low. Avoid Discwasher, Spin-Clean, Audio-Technica, Pro-Ject, Crosley, Mobile Fidelity and any artist/album cover art [marks, estimate]. Carbon-fibre brush and sleeve shapes are generic. Records shown in photos must not be recognizable album covers. |
| Safety regs | Anti-static HDPE/PP sleeves: no regulatory issue. PVC outer sleeves or PVC mats: Prop 65 DEHP (section 0.5); prefer PE/PP/rubber/cork. Cleaning fluid is excluded (flammable, hazmat). Powered cleaners/ultrasonic/turntables are excluded (mains, UL/ETL). Stylus brushes are fine. Wood shelves: formaldehyde statement `[unverified]`. |
| Claims | "Anti-static", "archival", "scratch-free" need supplier basis; soften to "anti-static HDPE" (a material fact). No claims that a brush "restores sound" or "removes scratches". No "universal fit for all turntables" unless dimensions match. |
| Images | CJ photos commonly show famous album covers or brand-printed turntables. Reject or use clean variants. |
| Verdict | ✅ pass (dry/passive items only) |

**Exclude:** cleaning fluids/sprays (hazmat), ultrasonic/vacuum cleaners, turntables/styluses with electronics, PVC-heavy products without a statement, record clamps/weights described with brand compatibility, printed sleeves with artist/album art.
**Do:** "12-inch LP anti-static inner sleeves, HDPE, 50 pack", "carbon fibre record brush, dry cleaning".
**Don't:** "Audio-Technica style", "Spin-Clean compatible", album titles, "restores", "removes scratches".

## 5. watch-accessories

| Check | Result |
|---|---|
| eBay policy | Check the **Watches** category rules: authenticity expectations are high and watches are a luxury focus [primary doc 08 via 0001]. We sell accessories only, never watches or parts that claim to be genuine brand parts. Leather goods/jewelry FVF tiers might apply to straps `[unverified]`. |
| IP | **Highest brand risk after tcg.** Rolex, Omega, Seiko, G-Shock/Casio, Apple Watch, Garmin and "Bergeon" (tool brand) are VeRO-active. Lug-width wording is the safe path. Counterfeit-spares risk: spring bars and tools "for Rolex" are exactly what VeRO targets. Watch tools/boxes have no Schedule A hit found (section 0.4, weak evidence). |
| Safety regs | Leather straps: Prop 65 (chromium VI/lead in finishes) `[estimate, doc 0001]` and nickel-release in metal buckles `[unverified]`. Watch boxes with glass lids: lead in glass (Prop 65 exposure is low for lids, but ask). No batteries, winders or smart bands (lithium/radio/FCC). Watch-repair kits include sharp pins and small parts: do not market to children. |
| Claims | "Genuine leather" requires FTC leather-guide care: say "leather" only if the supplier confirms; "faux leather/PU" otherwise. "Waterproof" or "dive-safe" straps: no unless documented. Lug-width and length accuracy must be measured. |
| Images | CJ strap photos usually show a branded watch on the wrist (Apple Watch, G-Shock, Rolex). Reject any image where a brand dial or logo is visible; product pixels cannot be altered to hide it. This will kill many strap SKUs. |
| Verdict | ⚠️ pass with conditions (tools and boxes yes, straps risky) |

**Exclude:** smartwatch bands named for any brand; watch winders; batteries; case-back openers or spring bars "for Rolex/Omega/Seiko"; straps that display a brand logo on the clasp or in the image; "genuine leather" without proof; replica watches or dials.
**Do:** "watch link remover tool kit, 5-piece", "NATO-style nylon strap, 20 mm lug width", "10-slot watch storage box, faux leather".
**Don't:** "Rolex", "Seiko", "Apple Watch", "G-Shock", "Bergeon", "Omega"; "luxury watch" as a keyword for generic items.

## 6. hobby-modeling-tools

| Check | Result |
|---|---|
| eBay policy | Hobby knives and blades: eBay has a **Knives policy** (certain knives are restricted or prohibited) `[unverified, not read this session; compliance must read https://www.ebay.com/help/policies/prohibited-restricted-items/knives-policy before listing hobby knives/scalpels]`. Paints/glues/solvents are excluded (hazmat). |
| IP | Games Workshop (Warhammer, Citadel), Bandai (Gundam), Tamiya, Vallejo, Army Painter, GodHand and Mr. Hobby are all brands, and GW/Bandai are VeRO-active [secondary, doc 0001]. "Wet palette" is a generic term. Sprue cutters and hobby knives are generic tools: no Schedule A hit found (section 0.4, weak evidence). |
| Safety regs | CPSIA: model tools are adult-hobby tools, but "starter model kits for kids" are children's products: veto that wording. Hobby knives need sharp-object warnings in the description. Brass pin vises/cutters: lead in brass (Prop 65) so ask for statement or use steel. Rubber/PVC cutting mats: DEHP check. Airbrush compressors (mains) and LED magnifiers (lithium) are vetoed. Art materials (paint) fall under LHAMA/ASTM D4236 [secondary, doc 0001], so excluded. |
| Claims | "Flush cut", "hardened steel", "SK5" etc. are material claims: only with a supplier spec. "Self-healing" for mats is fine. No "professional grade/GodHand quality". |
| Images | CJ photos often include Gundam/Warhammer models or branded paint pots in frame: reject these. A tool on a clean background is fine. |
| Verdict | ⚠️ pass with conditions |

**Exclude:** paints, glue, putty, solvents, airbrush compressors, LED magnifiers, children's model kits, anything shown with a GW or Bandai model, replica knives/tactical knives, blades sold as weapons.
**Do:** "single-blade sprue cutter, flush cut", "model tool kit, 20 pieces, hobby knife with 10 spare blades" (after knife-policy check), "wet palette, 40 sheets, for miniature painting".
**Don't:** "Warhammer", "40K", "Gundam", "Citadel", "Tamiya", "GodHand", "for kids".

## 7. auto-detailing-tools

| Check | Result |
|---|---|
| eBay policy | OK for tools. Chemicals (soaps, coatings, waxes) are excluded: hazmat/shipping restrictions. Motors Parts & Accessories category rules apply; do not list vehicle-fitment parts that need compatibility data `[estimate]`. |
| IP | Brands: Chemical Guys, Meguiar's, Griot's Garage, Adam's Polishes, Karcher, Gtechniq. Foam cannon is a generic gadget but pressure-washer connector standards (M22, 1/4 quick connect) are fine to state as dimensions. No Schedule A hit for foam cannons found (section 0.4 weak). Trim-removal tools are generic. Drill-brush sets are a common gadget; run the design-patent check (step 3, section 0.3). |
| Safety regs | **Foam cannons and fittings:** brass is common, so Prop 65 lead risk (section 0.5): require "lead-free brass or stainless" statement. Pressure-rated parts: state max PSI only if the supplier documents it (injury risk if overstated). Drill brushes: for use with a user's own drill, no motor sold. Cordless polishers/vacuums: lithium/mains veto. Microfiber: no issue. Chemicals excluded. |
| Claims | "Scratch-free", "swirl-free" wash mitt and "safe for ceramic coating" are performance claims: avoid. Maximum pressure / compatibility with specific washers (Karcher, Ryobi): only generic thread type. |
| Images | Photos often show a branded car, logo'd pressure washer or chemical bottles. Reject if a brand logo is visible; product pixels untouched. |
| Verdict | ⚠️ pass with conditions |

**Exclude:** chemicals, polishers, vacuums, pressure washers, bulky buckets, any item with lithium or mains plug, brass foam cannons without a lead statement, "universal fit" fitment parts.
**Do:** "foam cannon, 1/4 in quick connect, 1 L bottle, stainless", "detailing brush set, 5 sizes, synthetic bristle", "trim removal tool kit, nylon, 5 pieces".
**Don't:** "Karcher compatible", "Chemical Guys style", "Meguiar's", "ceramic safe", "swirl-free".

## 8. pet-grooming-supplies

| Check | Result |
|---|---|
| eBay policy | OK. Pet supplies are not restricted for manual tools. Treatments, flea/tick products, medications and edible chews are excluded (EPA/FIFRA, ingestibles). |
| IP | Brands: FURminator (VeRO-active, a trademark and utility/design-patent holder `[unverified]`), Hertzko, Safari, Andis, Wahl, Oster, Chris Christensen. "Deshedding tool" is generic but "FURminator-style" is a veto. **Self-cleaning slicker brushes** and **hair-remover rollers** are the likeliest design-patent gadgets in the niche: closest analogy is the Schedule A hairbrush litigation (section 0.4) [secondary]. |
| Safety regs | Outside CPSC jurisdiction for pet items, except choking/sharp injuries to people; pet products are not children's products. **Electric clippers and nail grinders are veto** (lithium/mains, UL/ETL, and FCC if there is a wireless charger). Manual clippers and combs: no regulation, but add sharp-edge handling note. Prop 65: rubber/PVC grips (DEHP), metal parts (lead). Bath brushes with silicone: fine. |
| Claims | No veterinary or health claims ("prevents matting infections", "treats skin conditions", "reduces shedding by 90%"). "Pain-free/safe for sensitive skin" is a safety claim: avoid. Quick-sensor nail clippers or LED nail clippers: LED has a battery, so exclude. |
| Images | CJ photos commonly show breed-specific dogs (fine) or branded packaging. Reject images with watermarks or brand text. |
| Verdict | ⚠️ pass with conditions (lowest regulatory exposure; mostly wording and patent check) |

**Exclude:** electric clippers/trimmers/grinders, steam brushes, battery-powered pet vacuums, flea/tick products, shampoos and sprays, edible chews, self-cleaning slicker brushes and hair-remover rollers until the design-patent check clears each SKU, anything marketed as treating a condition.
**Do:** "dog slicker brush, stainless pins, medium", "dog nail clipper, stainless steel, large breed", "cat grooming brush, soft bristle".
**Don't:** "FURminator", "Andis", "Wahl", "vet recommended", "cures/prevents/treats".

---

## Ranked summary

| Rank | Niche | Verdict | Top 3 conditions |
|---|---|---|---|
| 1 | coin-supplies | ✅ | 1. PVC-free only (Prop 65 DEHP, coin damage). 2. Never list coins or bullion; no PCGS/NGC/Whitman wording. 3. Brass/wood items need lead/formaldehyde statement or exclude. |
| 2 | vinyl-record-care | ✅ | 1. Dry, passive items only; no fluids or electronics. 2. No album art or turntable brands in titles or CJ images. 3. Prefer HDPE/PP/cork; PVC only with statement. |
| 3 | pet-grooming-supplies | ⚠️ | 1. Manual tools only (no clippers/grinders). 2. Design-patent check on self-cleaning brushes and hair rollers per SKU. 3. No health claims; no FURminator-style wording. |
| 4 | hobby-modeling-tools | ⚠️ | 1. Read eBay knives policy before listing knives. 2. No Warhammer/Gundam names or images; no kids' kits. 3. No paints, glues or powered/lithium items; brass needs lead statement. |
| 5 | auto-detailing-tools | ⚠️ | 1. Lead-free brass or stainless on foam cannons. 2. No chemicals, no powered items, no brand compatibility wording. 3. No performance claims ("swirl-free", PSI) without documents. |
| 6 | collectibles-display | ⚠️ | 1. Reject CJ images showing LEGO/Funko/character art; no brand words. 2. No LED/glass; no child-oriented wording. 3. UV claim only with test report; verify dimensions on test unit. |
| 7 | tcg-supplies | ⚠️ | 1. Never use PSA/BGS/Pokemon/MTG/league names (including "PSA style"). 2. Magnet holders: sealed non-removable magnets confirmed; PVC sleeves only with statement. 3. No licensed art in listing images; adult-collector positioning only. |
| 8 | watch-accessories | ⚠️ | 1. No watch-brand names, "for Rolex" tools or smartwatch bands. 2. Reject CJ images that show branded dials; this limits straps. 3. "Genuine leather" only with proof; Prop 65 check on leather/metal. |

Ranking reflects compliance exposure only, not margin or demand. Tcg-supplies is the most brand-exposed but has the strongest demand per doc 0001; the condition set above is workable if title discipline is enforced. Watch-accessories ranks last because the image problem (brand dials in CJ photos) can only be fixed by SKU rejection, not by editing.

## Open items (not resolved here)

- CJ image-licence gap (doc 06) affects all niches.
- eBay Knives policy, Watches category rules and Supplies FVF tier: not read this session.
- Magnet rule applicability (16 CFR 1262) for embedded-magnet holders: counsel to confirm.
- Design-patent search is a manual USPTO step; no tooling exists yet.
- Prop 65 numeric thresholds above came from search snippets; confirm with OEHHA before relying on them.

## Sources

- docs/research/01-ebay-policy.md, 05-legal-and-platforms.md, 06-image-sourcing.md, 10-category-risk.md; docs/decisions/0001-niche-candidates.md [primary/secondary as labelled in those files]
- eBay IP policy: https://www.ebay.com/sellercenter/resources/intellectual-property [primary, snippet only]
- eBay PSA grading service: https://www.ebay.com/help/buying/paying-items/using-psa-grading-service?id=5639 [primary, snippet only]
- Schedule A digests (PatSnap): https://www.patsnap.com/resources/blog/litigation/bounce-curl-llc-v-schedule-a-defendants-permanent-injunction-settlement-in-hair-brush-design-patent-case-patsnap-eureka/ ; https://www.patsnap.com/resources/blog/litigation/guangdongsheng-v-schedule-a-defendants-metal-nibbler-patent-patsnap-2/ [secondary]
- Prop 65 notices/settlements: https://oag.ca.gov/system/files/prop65/notices/2023-01944.pdf ; https://oag.ca.gov/system/files/prop65/settlements/2021-00185S0388.pdf ; https://www.sgs.com/news/2026/07/safeguards-09726-california-proposition-65-chemical-reformulation-in-consumer-products [secondary, not fully read]
