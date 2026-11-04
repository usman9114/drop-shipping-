# Runbook: Terapeak research session (manual, about 90 minutes)

> Why this exists: eBay's API license does not let us store or analyse eBay data or use it to model prices without written permission (decision 0004). Terapeak is eBay's own research tool for sellers. You read it by hand and record **your own observations**. Do not copy listing text or images, and do not paste raw exports into the repo. eBay's User Agreement (2026) bans scrapers, data-mining tools and AI-driven bots, so this stays manual; there is no Terapeak API or export.

## What you need
An eBay seller account (a free personal account is enough to start). Open **Seller Hub → Research → Product research**.

## Which products

Use the newest **`data/observations/terapeak-sheet-YYYY-MM-DD.csv`** (exported by `make wh-export` from the warehouse). One row per product type that CJ can ship from its US warehouse at a passing margin. Copy it to `terapeak-YYYY-MM-DD-filled.csv` and fill in your copy. Work top to bottom; rows are sorted by how many CJ products back them.

Columns already filled by the warehouse (do not edit):

| Column | Meaning |
|---|---|
| `product_type`, `search_phrase` | what to search (adjust the phrase if results are off; note it in `notes`) |
| `cj_products` | how many CJ US products fit this type |
| `price_floor_best` | the lowest price at which the cheapest CJ product passes our margin model (≥ 20% base, ≥ 10% stress) |
| `price_floor_median` | the same for the median CJ product in the type |
| `review_flags` | rules that want a human look (e.g. jewelry heavy metals, chemicals) |

The question per row: **do sold listings go for at least `price_floor_best`, and often?**

## For each row
Search the phrase. Set: **United States**, **last 90 days**, **Sold** tab, condition **New**. Fill in:

| Column | What to write |
|---|---|
| `date`, `observer` | today, your initials |
| `sold_count_90d` | items sold in the window |
| `avg_sold_price`, `sold_price_min`, `sold_price_max` | from the summary and the price range |
| `avg_shipping` | average shipping charged, 0 if free |
| `free_shipping_share_pct` | rough share of sold listings with free shipping |
| `active_listings` | count from the **Active** tab with the same filters |
| `sell_through_pct` | Terapeak's figure if shown, otherwise `sold ÷ (sold + active) × 100` |
| `sellers_with_20plus_sales` | how many sellers account for most sales (rough count) |
| `notes` | bundle sizes that sell best, brand names to avoid, anything odd |

## Rules
- Record only the numbers and your notes. No titles, no images, no seller names.
- Use the same window and filters for every row so the rows compare.
- If a search returns fewer than about 20 sold items, write the count and leave the price columns blank. Do not guess.
- Commit the CSV (it is your own observation data). Do not paste Terapeak screenshots into the repo.

## What I do with it
The warehouse loads your filled sheet and joins it to CJ cost and freight. A product type goes forward when the average sold price is at or above `price_floor_best`, sell-through is about 50% or more, and enough units sell (at least ~20 in 90 days). Compliance review and test orders follow.
