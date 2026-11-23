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
- **Picker:** first version was wrong on 8 of 30 stores (it sometimes chose a narrow or seasonal collection); rewritten and validated below. The signal is not in `market_rank.WEIGHTS`.

## Best-seller picker validation (2026-11-22, principle 5)

Hand-labelled from each store's candidate list (`data/private/research/pk-bestseller-truth*.csv`, private): the label is the handle of the whole-store best-seller collection, or none.

| Picker | Stores | Right |
|---|---|---|
| First version (title or handle match, largest count) | top 30 Pakistan | 22/30 = 73% |
| Rewritten (handle only; skips empty, campaign and scoped handles; evergreen first), same 30 | in-sample | 26/30 = 87% |
| Rewritten, **held-out** (ranks 41 to 70, labelled before reading the picker's answer) | 20 | **19/20 = 95%** |

Errors found and now tests (`test_pick_best_rules_from_hand_check`): best-seller only in a collection's title ("Eid Sale" titled "Best Sellers"); seasonal and dated campaigns (`summer-trending-hit-codes`, `12-12-top-sellings`, `ws-23`); one gender, category or brand (`boys-most-popular-products`, `bestsellers-maybelline`); empty collections; one-word handles (`bestsellers`); counts that cannot be trusted (31,930 on a small shop). **Known limit:** it refuses a scoped handle even when the store sells only that range (a lawn shop's `1-lawn-best-selling`, an abaya shop's `best-seller-abayas`): 5 misses over 50 stores, all "none" where a list existed. Chosen on purpose: no list beats a wrong one.

Result on the top 70: 32 stores have best-seller data (of 68 read). Best-seller median price is **0.89 of the catalogue median** and below it at 18 of 32 `[proxy]`, so merchants' best sellers skew cheaper than their range. Signal still not in `market_rank.WEIGHTS`; adding it is a separate, explained change.

## Owner decision 2026-11-23: no VPN or proxy to get around rate limits

When Shopify answers HTTP 429 we slow down (1 worker, 4 to 6 s apart, 10-minute back-off); we do not rotate IPs through a VPN or proxy to dodge the limit. A proxy stays open only as a narrow option to view Pakistani stores as a local visitor (prices, redirects), if ever needed. Check that the VPN location is Pakistan or neutral during `/meta.json` runs, since stores can change currency by visitor country.
