# 0021 robots.txt wildcards, and the best-seller signal without `sort_by`

> 2026-11-22. Owner asked to add the "best seller" signal suggested in a ChatGPT research note (`?sort_by=best-selling`).

## Finding: our robots check ignored wildcards

Shopify's default robots.txt contains `Disallow: /collections/*sort_by*`. Python's `urllib.robotparser` reads `*` and `$` as literal text, so it reported `/collections/all?sort_by=best-selling` as **allowed**. That request is forbidden, so we do not make it.

- **Fix:** `scout/robots.py` (`RobotRules`), a drop-in for `RobotFileParser` with RFC 9309 matching (wildcards, `$`, longest rule wins, Allow wins ties, named group beats `*`). All nine modules that read robots.txt now use it. Tests: `tests/test_robots.py`.
- **HOMEGROWN:** a maintained library exists (`protego`, from Scrapy, BSD). Installing it needs the owner's approval (principle 7), and the matcher is about 40 lines, so a small own version went in. Owner may swap it for `protego`; the interface is the same.
- **Audit of past fetches:** 59 stores (top 30 Pakistan, top 30 US, robots.txt read 2026-11-22) × 6 URLs we use (`/`, `/meta.json`, `/products.json` pages, `/sitemap.xml`, `/collections.json`): old and new parsers **agree on every one**. No earlier fetch in that sample breached robots.txt.

## Best-seller signal: permitted route

A merchant-made "best sellers" collection is read through `/collections.json` and `/collections/<handle>/products.json` (no `sort_by`, allowed by default Shopify robots.txt). `python -m scout.stores best --domains <file>` writes dataset `web_store_best`: chosen collection handle, product ids (no titles), median price, discount share and share added in the last 90 days.

Pilot, top 30 Pakistan stores `[data]`: 27 have a best-seller-type collection; 18 returned products after skipping empty ones (5 had none usable, 3 returned 0 products).

## What it is and is not

- **Is:** what the merchant chooses to promote as best sellers `[proxy]`. Price of best sellers vs the catalogue median is visible (e.g. best sellers far cheaper than the catalogue at 6 of 18).
- **Is not:** verified sales. Order inside a collection may be manual. Some collections are campaigns ("eid-sale-best-seller") or narrow ("bestsellers-maybelline"). `[unknown]` sales, orders.
- **Not validated:** the collection picker (evergreen handle first, else the largest) sometimes chooses a narrow collection. Needs a hand check of about 20 stores before the signal enters any score (principle 5). It is not in `market_rank.WEIGHTS`.
