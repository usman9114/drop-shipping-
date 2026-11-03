# 13 - Sales: landed-cost ceilings and niche economics

> `head-of-sales`, 2026-11-03. Stage C''. **Evidence quality: low.** No API keys yet. eBay price bands come from web-search snippets (not scraped) and are [secondary] snapshots; every CJ cost and CJ shipping figure is an [estimate] because no CJ price or rate card was retrievable. Treat results as a screen for which niches have headroom, not as product approvals. Model: `scout/margin.py` defaults (13.6% FVF on price + 7% tax, $0.40 per order, 5% ads, 2% disputes, $8 return label). Stress = +$3 duty and double the return rate.

## 1. Landed-cost ceiling table [data: scout.margin output]

Max CJ landed cost (product + US shipping) that still passes >= 20% base and >= 10% stress. Stress is the binding constraint at every price.

| eBay price | Return 5% | Return 8% (default) | Return 12% | Ceiling as % of price (8%) |
|---|---|---|---|---|
| $15 | 4.84 | 3.59 | 1.92 | 24% |
| $20 | 7.85 | 6.34 | 4.34 | 32% |
| $25 | 10.86 | 9.10 | 6.75 | 36% |
| $30 | 13.87 | 11.86 | 9.16 | 40% |
| $40 | 19.90 | 17.37 | 13.99 | 43% |
| $50 | 25.92 | 22.88 | 18.82 | 46% |
| $75 | 40.09 | 36.66 | 30.89 | 49% |

Commands (ceiling found by bisection on `cost`, `ship=0`; scratch script `ceil.py` calls `scout.margin.evaluate`):

```
PYTHONPATH=. python ceil.py        # bisects Inputs(price=P, cost=m, ship=0, return_rate=0.05|0.08|0.12) on .pass
python -m scout.margin --price 30 --cost 11.86 --ship 0                   # default, sits on the line
python -m scout.margin --price 30 --cost 13.87 --ship 0 --return-rate 0.05 # low-return variant
python -m scout.margin --price 30 --cost 9.16 --ship 0 --return-rate 0.12  # high-return variant
```

Reading: with CJ US shipping around $4-6.5 [estimate; one review quotes $4-10 by weight, and CJ handling fees of $0.50-0.85 per order, both [secondary]], a $20 item leaves only ~$1-2 for the product itself. **Practical floor: sell at $25+, ideally $28-40, with landed cost <= 35% of price.** The +$3 duty stress is conservative for US-warehouse stock (duty already paid by CJ); it still stands as the house rule.

## 2. Per-niche price bands and representative products

Price bands are eBay/Amazon/Walmart/retailer snapshots from search snippets [secondary]. CJ product cost and CJ ship are [estimate] (typical CJ pricing for generic Chinese-made goods; unverified). Return rate set to 0.05 for passive collector supplies, 0.08 for the rest. Results from `PYTHONPATH=. python niche.py` (same `Inputs`/`evaluate` as the CLI; e.g. `python -m scout.margin --price 29 --cost 7 --ship 4.5 --return-rate 0.05`).

### tcg-supplies
Price evidence [secondary]: 25-pack 35pt one-touch magnetic holders on eBay US: generic LOVFEN $22.99, Ultra Pro $35-50, Pro-Mold $51.95 ([listing](https://www.ebay.com/itm/167480493658)). Branded names can't be used, so the generic band is $23-30.

| Product | Price | Landed (cost+ship) | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Magnetic holder 35pt, 25-pack | 29 | 11.50 (7.0+4.5) | 9.30 | 32.1% | 16.1% | **yes** |
| 9-pocket binder, 360-card | 28 | 15.00 (9.0+6.0) | 5.05 | 18.0% | 1.6% | no |
| 1000 sleeves + 2 storage boxes bundle | 30 | 14.00 (8.0+6.0) | 7.54 | 25.1% | 9.5% | no (just) |

Notes: multi-pack is the natural unit (25/50-packs, mixed-thickness 35/55/75/130pt assortments Temu rarely bundles). Variant risk: thickness (pt) variants, 4-6 SKUs, medium stock-sync risk. Weight: holders and sleeves light; binders and boxes ~1-2 lb, push shipping. Promoted Listings: needed, competitive keyword space (5-8% rate likely).

### collectibles-display
Price evidence [secondary]: single minifigure acrylic case $6.99-12.99, 12-figure case $25.99, 60-figure $68-85, 100-figure $125-160 (iDisplayIt, Kingdom Brick Supply via [reach.dog](https://reach.dog/shop/kingdom-brick-supply/products/60-lego-minifigures-display-case)). Note LEGO is a trademark: use generic "minifigure" wording only.

| Product | Price | Landed | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Acrylic risers set of 5 | 24 | 11.50 (6.5+5.0) | 4.72 | 19.7% | -2.3% | no |
| Minifigure case 3-pack | 26 | 13.50 (8.0+5.5) | 4.15 | 16.0% | -4.9% | no |
| Cube case 4-pack (ball/baseball) | 28 | 16.00 (9.5+6.5) | 3.09 | 11.0% | -8.8% | no |

Notes: bulky and fragile (acrylic scratches and cracks, so returns/damage likely above 8%), shipping $5-8, margin is worst of the set. Sizes are the main variant axis (interior dimensions). Larger multi-figure cases ($60+) would pass on price but are oversize and freight-prone. Promoted Listings: medium.

### coin-supplies
Price evidence [secondary]: 100 flips $3.60-17.99 (BCW $17.99, Guardhouse 2.5x2.5 $13.95), flip storage box $9.99, 12/24-pocket album pages $7.59-8.54 on eBay, 20 pocket pages $6.50 ([Coin Supply Express](https://www.coinsupplyexpress.com/guardhouse-2-5-x-2-5-unplasticized-coin-flips-100-pk-782515), [BCW](https://www.bcwsupplies.com/coin-supplies/clear)). Single items sit at $7-18, below the viable floor.

| Product | Price | Landed | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Flips 100 + box bundle | 19 | 9.00 (4.5+4.5) | 4.35 | 22.9% | 0.7% | no |
| Capsules assorted 100 + album | 24 | 12.00 (7.0+5.0) | 5.07 | 21.1% | 2.7% | no |
| 120-pocket album + 100 flips | 26 | 13.50 (8.0+5.5) | 5.06 | 19.5% | 2.1% | no |

Notes: coin buyers value archival specs (PVC-free), which Chinese generics often fail, so the "accurate description" angle matters; honesty about PVC is a compliance and defect issue. Bundles of 300-500 pieces ($30+) would pass but few buyers need that. Sizes (capsule mm) mean 10+ variants, high sync risk. Light parcels. Promoted Listings: low-medium.

### vinyl-record-care
Price evidence [secondary]: cleaning kits $10-31 (Music Nomad $19.99, Hudson Hi-Fi $30.95, Vinyl Styl $29.95), 12" outer sleeves 50-pack $11-17 (MoFi $24.95), 7" 50-pack $13-15 ([Turntable Lab](https://turntablelab.com/products/vinyl-styl-ultimate-record-care-kit-record-cleaning-kit), [BCW](https://www.bcwsupplies.com/12-inch-record-sleeves-polypropylene-50-pack)). Kits are a $20-25 market; sleeves are commodity at $11-17.

| Product | Price | Landed | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Cleaning kit 5-in-1 | 22 | 10.00 (5.5+4.5) | 5.58 | 25.4% | 5.6% | no |
| LP outer sleeves 100 + inner | 24 | 11.50 (6.0+5.5) | 5.57 | 23.2% | 4.8% | no |
| Display stand + brush bundle | 28 | 13.50 (8.0+5.5) | 6.55 | 23.4% | 7.0% | no |

Notes: cleaning kit contains liquid (compliance veto per decision 0001: sell dry kits only). Sleeves are heavy in volume (100 = ~1 lb). Few variants (size 7/10/12"), low sync risk. Strong bundle story: sleeves + brush + stand "starter kit". Promoted Listings: medium.

### watch-accessories
Price evidence [secondary]: link remover kits $10-30 (Jorest $9.99, Maystar 480pc $14.39, Eventronic $29.95); no NATO strap or 12-slot box price found (gap) ([Walmart](https://www.walmart.com/c/kp/remove-watch-link), [eBay category](https://www.ebay.com/b/Watch-Link-Pin-Removers/117039/bn_56798167?mag=1)). NATO strap 5-pack $20-24 and box $30-40 are [estimate].

| Product | Price | Landed | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Link remover/repair kit 168pc | 22 | 9.00 (5.0+4.0) | 5.78 | 26.3% | 2.9% | no |
| NATO strap 5-pack | 22 | 8.50 (5.0+3.5) | 6.28 | 28.5% | 5.2% | no |
| Watch box 12-slot | 34 | 18.50 (12.0+6.5) | 4.91 | 14.4% | -3.1% | no |

Notes: straps are very light (cheapest shipping), but width (18/20/22mm) x colour gives 20+ variants and high sync risk. Multi-pack straps (5-6 colours) is a real bundle Temu does carry, but eBay buyers search by lug width. Kits: undifferentiated, saturated. Box: bulky, returns higher. Promoted Listings: needed, high keyword competition.

### hobby-modeling-tools
Price evidence [secondary]: hobby tool kits $21.95-37.99 (Army Painter $37.99, Vallejo $26-29, Modelcraft 9pc $21.95), sprue cutter $6-7, wet palette $33 plus $12-15 refills, generic 40pc set $26.99 ([Army Painter](https://thearmypainter.com/shop/us/tl5023p), [Hobby Lobby](https://hobbylobby.com/crafts-hobbies/model-kits/paint-brushes/sprue-cutter/p/1222)). Brands excluded; generic kits sit at $22-30.

| Product | Price | Landed | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Hobby tool kit 40pc | 26 | 11.00 (6.5+4.5) | 7.56 | 29.1% | 11.7% | **yes** |
| Wet palette + 50 sheets | 22 | 10.00 (5.5+4.5) | 5.58 | 25.4% | 5.6% | no |
| Paint storage rack 3-tier | 32 | 19.00 (11.0+8.0) | 4.03 | 12.6% | -2.3% | no |

Notes: the best natural bundle niche (kit is the standard unit; brand kits cost $26-38 so generic kits at $24-30 undercut). Few variants (kit contents), low sync risk. Hobby knives have blades: check eBay knife policy and age restriction before listing. Light parcel for kits, racks bulky. Promoted Listings: medium (4-6%).

### auto-detailing-tools
Price evidence [secondary]: 24pc brush set w/ drill brushes $9.99, 7-pack drill brushes $7.99, 27pc kit $23, foam lances $68-105 on eBay (MJJC), 45pc kit $99.99 ([Slickdeals](https://slickdeals.net/f/18627415-24-piece-car-detailing-brush-set-w-drill-brush-attachments-9-99-free-shipping-w-prime-or-on-35), [DealNews](https://www.dealnews.com/products/TTRCB-27-Piece-Car-Detailing-Kit/499087.html)). Brush sets are already at $8-23 on Amazon, which is a price ceiling for us.

| Product | Price | Landed | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Brush set 24pc w/ drill brushes | 21 | 9.50 (5.0+4.5) | 4.56 | 21.7% | -2.5% | no |
| Trim removal tool 25pc | 20 | 7.50 (3.5+4.0) | 5.84 | 29.2% | 4.2% | no |
| Foam cannon + 3 mitts bundle | 36 | 16.00 (10.0+6.0) | 8.85 | 24.6% | 7.6% | no |

Notes: Amazon price anchor is the problem (commodity, sub-$12 on deals). Foam cannon bundle has the best dollar margin but fails stress marginally; at a $40 price with $16 landed it would pass. Brass fittings and bulk weight (~2 lb) raise shipping. Variants: thread/pressure-washer fittings (compatibility errors drive returns, above 8%). Promoted Listings: needed, 6-8%.

### pet-grooming-supplies
Price evidence [secondary]: kits $11-37 (7pc $12.99 Walmart, 3pc $17.08 Target, 7-in-1 $27.95), slicker brush alone $19.99 ([Target](https://www.target.com/p/-/A-1003104332), [Discount Cave](https://reach.dog/shop/discount-cave/products/7-in-1-pet-grooming-kit-free-shipping)).

| Product | Price | Landed | Base net $ | Base % | Stress % | Pass |
|---|---|---|---|---|---|---|
| Grooming kit 7pc | 20 | 9.50 (5.0+4.5) | 3.84 | 19.2% | -5.8% | no |
| Deshedding + slicker 2-pack | 22 | 9.50 (5.0+4.5) | 5.28 | 24.0% | 0.6% | no |
| Pet hair remover + glove bundle | 18 | 8.50 (4.0+4.5) | 3.40 | 18.9% | -8.2% | no |

Notes: mass-market, Temu/Amazon native, shopper price anchor $12-20. Sizing/colour variants moderate. Nail clippers are sharp: policy check. Promoted Listings: high need, as eBay is not a pet destination (doc 08/decision 0001).

## 3. Ranked summary

Headroom score = how likely a product in the niche reaches >= 20% base / >= 10% stress at a believable price, given price band, bundle potential, shipping weight and return risk. All [estimate], resting on [secondary] prices and [estimate] CJ costs.

| Rank | Niche | Headroom (0-5) | Why |
|---|---|---|---|
| 1 | tcg-supplies | 4.0 | Only niche where eBay US shows a $23-35 band for a light 25-pack; passes with 32%/16%. Multi-pack is the normal unit; low returns. Binders/boxes fail, so scope to holders and sleeves-by-pack. |
| 2 | hobby-modeling-tools | 3.5 | Tool kits at $24-30 undercut $26-38 branded kits; passes 29%/12%. Few variants, light. Blade policy check; racks and palettes don't pass. |
| 3 | vinyl-record-care | 2.5 | Base 23-25% but stress 5-7%. Needs bundles at $28+ and dry kits only. |
| 4 | watch-accessories | 2.0 | Cheap shipping but single items $20-22 stress-fail; 20+ strap variants are the worst sync risk. |
| 5 | auto-detailing-tools | 2.0 | Best dollar margin on cannon bundle ($8.85) but Amazon sub-$12 anchor and fitment returns. |
| 6 | coin-supplies | 1.5 | Single items $7-18, below floor; bundles pass base but stress 1-3%. |
| 7 | pet-grooming-supplies | 1.0 | $12-20 anchor, base 19-24%, stress negative. |
| 8 | collectibles-display | 1.0 | Fragile/bulky, landed $11-16 on $24-28 prices; fails across the board. |

## 4. Gaps and next steps
- Replace [estimate] CJ cost/shipping with the CJ catalog and shipping calculator once keys exist (`data-analyst`); the single most sensitive input is CJ ship ($4 vs $6.5 moves a $26 product by ~8 points of margin).
- Replace price snapshots with eBay Browse API sold/active medians; snippets here are mixed with non-US (eBay.de) and brand prices.
- No NATO strap, 12-slot watch box, coin capsule or binder price was found.
- A product passing here is not approved: Promoted Listings rate (5% assumed) may need 7-8% in TCG and auto, which cuts ~2-3 points.

## Sources
Web-search snippets (retrieved 2026-11-03, snapshots): ebay.com/itm/167480493658; reach.dog (Kingdom Brick Supply, iDisplayIt); coinsupplyexpress.com; bcwsupplies.com; turntablelab.com; walmart.com/c/kp/remove-watch-link; ebay.com/b/Watch-Link-Pin-Removers/117039; thearmypainter.com; hobbylobby.com; slickdeals.net/f/18627415; dealnews.com; target.com/p/-/A-1003104332; CJ US warehouse reviews (blog.cjdropshipping.cn, revenuegeeks.com, hustlegotreal.com).
