# CJ supply check, 2026-11-04: trading-card supplies fail K1; so do both backups

> First live run of the CJ API (`scout/cj.py`, `scripts/cj_sweep.py`). Raw responses are in `data/private/` only (CJ data terms unconfirmed). This note holds derived counts, ids and our own numbers. Data: `cj-sweep-tcg.json`, `cj-sweep-vinyl.json`, `cj-sweep-hobby.json` in this folder.

## 1. Result

| Niche | Product types searched | Relevant CJ **US-warehouse** SKUs | Relevant CJ SKUs, any warehouse | Kill check |
|---|---|---|---|---|
| `tcg-supplies` (primary) | 24 (decision 0002 §3.3) | **0** | ~1 (a 9-grid A4 binder) | **K1 fails** (< 40 US SKUs) |
| `vinyl-record-care` (backup 1) | 8 | ≤ 4 (titles not yet checked) | ≤ 6 | fails the same bar |
| `hobby-modeling-tools` (backup 2) | 9 | ≤ 8 (mostly generic organizers and clamps) | ≤ 34 | fails the same bar |

Method: one or two generic phrases per product type, `product/listV2` page 1 (50 results), with and without `countryCode=US`. A hit counts only if its title matches a type-specific regex (in `scripts/cj_sweep_*.json`). For tcg I checked every regex hit by hand: all 11 US hits and all global hits but one were false positives (wallets, jackets, a drywall dolly, "booster" supplements). CJ's 578-leaf category tree has no trading-card, collectibles-supplies or record-care category.

Limits: page 1 only, and CJ's keyword search is loose (any word matches). A deeper pull could find a few more SKUs, but not the 40+ that K1 needs: the full US catalogue is only 3,964 products (§2).

## 2. What CJ's US warehouse actually holds

Full `listV2?countryCode=US` pull: **3,964 products** (all carry US stock).

| Top-level category | Products |
|---|---|
| Home, Garden & Furniture | 1,749 |
| Women's Clothing | 706 |
| Health, Beauty & Hair | 349 |
| Jewelry & Watches | 243 |
| Home Improvement | 196 |
| Automobiles & Motorcycles | 166 |
| Sports & Outdoors | 133 |
| Pet Supplies | 117 |
| Bags & Shoes | 103 |
| Men's Clothing | 97 |
| Toys, Kids & Babies; Consumer Electronics; Computer & Office; Phones | 29 / 24 / 13 / 10 |

Price quartiles (CJ cost): **$6.30 / $31.90 / $97.38**: much of the catalogue is furniture. US stock: 916 products have 1–19 units, 1,276 have 20–99, 1,772 have 100+.

**926 products** cost ≤ $12 with ≥ 20 US units. Largest groups: women's tops (160), skin care (145), fashion jewelry (129), makeup (66), home storage (63), women's outerwear (45), women's shoes (42). Skin care and makeup carry FDA/MoCRA and eBay restrictions; clothing and shoes carry size returns.

## 3. Real cost floor

CJ US→US freight for a 45 g parcel: **$5.18** (no zip) to **$5.97** (NYC zip), carrier GOFO+, quoted "3-8" (days, unit not documented). Margin model at $5.60 shipping, 8% returns, 5% ads (`python -m scout.margin`):

| Listing price | Max CJ cost that passes (≥ 20% base, ≥ 10% stress) |
|---|---|
| $25 | ~ $3.50 |
| $30 | ~ $6 |
| $35 | ~ $8.50 |

Shipping alone is ~19–22% of a $25–30 sale. Cheap, light items only work as $30+ bundles.

## 4. Options (owner decision)

| Option | What it means | For | Against |
|---|---|---|---|
| **A. Supply-first on CJ US** (recommended) | Score the 926 cheap, stocked US products: drop regulated and size-return categories by rule, cluster into product types with the free GLM model, then a Terapeak session on the top ~15 clusters | Uses what CJ can ship in 3–8 days; same pipeline; one week; free | Categories are generic and crowded (home storage, kitchen, pet, tools, party); demand unproven |
| B. Keep tcg, ship from China | CJ sourcing requests for magnetic holders, binders, slab cases; CJPacket from CN (quote seen: 5–11 days) | Niche research stays valid | No such SKUs in CJ today; slower than US eBay sellers; breaks K6 (≤ 5 business days); sourcing lead time unknown |
| C. Keep tcg, other US supplier | A US distributor that dropships card supplies | Fast US shipping | Mostly branded goods (VeRO, thin margins); new supplier research; may break the "generic, better listing" thesis |

**Recommendation: A, timeboxed to one week, with B as a free side probe** (2–3 CJ sourcing requests to learn cost and lead time, no commitment). If option A yields fewer than 20 passing products after Terapeak, stop and revisit the supplier choice rather than the niche.

## 5. Other findings

- eBay keys in the environment are **sandbox** keys (`-SBX-`): sandbox token 200, production 401. Production keys arrive with eBay developer approval. The earlier 403 from this container no longer occurs.
- `OPENROUTER_API_KEY` is not visible in the container (other four keys are). The free GLM route works without it.
