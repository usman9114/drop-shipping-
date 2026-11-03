# Runbook: Terapeak research session (manual, about 90 minutes)

> Why this exists: eBay's API license does not let us store or analyse eBay data or use it to model prices without written permission (decision 0004). Terapeak is eBay's own research tool for sellers. You read it by hand and record **your own observations**. Do not copy listing text or images, and do not paste raw exports into the repo. Terapeak's own terms were not checked; if they restrict this, tell me and we stop.

## What you need
An eBay seller account (a free personal account is enough to start). Open **Seller Hub → Research → Product research**.

## Which products
The 10 to 12 product types for the primary niche are in `docs/decisions/0002-niche-selection.md` (section "primary spec"). Start with the five that have the highest margin ceiling in `docs/research/13-sales-niche-economics.md`.

## For each product type
Search a plain phrase (for example "magnetic card holder 35pt"). Set: **United States**, **last 90 days**, **Sold** tab, condition **New**. Record one row in `docs/templates/terapeak-observations.csv` (copy it to `data/observations/terapeak-YYYY-MM-DD.csv`):

| Column | What to write |
|---|---|
| `product_type`, `search_phrase` | what you searched |
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
`sales-lead` merges the sold-price bands with CJ landed costs, reruns `scout.margin`, and `head-of-marketing` re-scores the niche. Rows that show sell-through under about 30% or an average price under $20 count against the niche.
