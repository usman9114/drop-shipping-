# 18 — CJ Dropshipping API cheat sheet

> `market-researcher` (Haiku), 2026-11-03, from CJ's official English developer docs. **Nothing here has been run against a live key.** Items under "Unknowns" must be confirmed on the first real call. Base host: `https://developers.cjdropshipping.com`. Every call except authentication sends header `CJ-Access-Token: <accessToken>`. Envelope: `code`, `result`, `message`, `data`, `requestId`, `success` (success is code 200).

## Endpoints

| # | Endpoint | Key params | Response fields we need | Notes |
|---|---|---|---|---|
| 1 | `POST /api2.0/v1/authentication/getAccessToken` | body `apiKey` | `data.accessToken`, `accessTokenExpiryDate`, `refreshToken`, `refreshTokenExpiryDate` | Doc says QPS = 1 [unverified]. Same account within 24 h returns cached tokens. |
| 2 | `POST /api2.0/v1/authentication/refreshAccessToken` | body `refreshToken` | same token fields | |
| 3 | `GET /api2.0/v1/product/listV2` | `keyWord`, `page` (max 1000), `size` (max 100), `countryCode`, `categoryId`, `startSellPrice`, `endSellPrice` | `data.content[].productList[]`: `id`, `nameEn`, `sku`, `spu`, `bigImage`, `sellPrice`, `listedNum`, `warehouseInventoryNum` | `totalRecords` capped at 6000. 50 points per call. |
| 4 | `GET /api2.0/v1/product/query` | one of `pid`, `productSku`, `variantSku`; `countryCode` (returns only variants with stock there) | `pid`, `bigImage`, `productImageSet[]`, `productWeight` (g); `variants[]`: `vid`, `variantSku`, `variantImage`, dimensions (mm), `variantWeight` (g), `variantSellPrice`, `inventories[]` | 10 points per call |
| 5 | `POST /api2.0/v1/product/stock/privateInventory/querySkuDetailPage` | `storageIds` (e.g. `["US"]`), `productId` | `variantId`, `storageId`, `clientAvailableQuantity` | 10 points. May show only the account's own stock [unverified]. |
| 6 | `POST /api2.0/v1/logistic/freightCalculate` | `startCountryCode`, `endCountryCode`, `products[]` of `{vid, quantity}` | `logisticName`, `logisticPrice` (USD), `logisticAging` (e.g. "2-5") | 10 points. For US stock the start country is probably `US` [unverified]. |

Other: the deprecated `GET /product/list` (`countryCode`, `pageSize` up to 200), warehouse detail `GET /warehouse/detail`, product stock summary endpoints (`querySpuPage`, `querySkuListByProductId`). See the sources.

## Limits and errors

- **Points model** (in force since June/July 2026): base **50,000 points/day** (UTC reset) plus 100 points per $1 of trailing transaction volume, replenished per minute. Exhaustion gives HTTP 429. A niche scan of about 3,000 list points plus a few hundred detail calls fits easily.
- **Errors:** `1600001` invalid key or token, `1600002` token empty, `1600003` invalid refresh token, `1600200` too many requests, `1600201` quota used up, `16900500` insufficient points.
- **`1600014` API access disabled: account-level, after 30 days with zero transactions.** [unverified reading] If true, a new key can go dead unless the account places an order within about a month. The Phase 1 test orders would cover this, so time them accordingly.
- **Token lifetime:** 180 days per the auth page; a search snippet said 15 days [conflict].

## Official MCP server

`github.com/CJ-dropshipping/api-mcp` needs Node 20+ and logs in with account email and password or an MCP token. Tools include `search_products`, `query_sku_details`, `calculate_freight`, `get_warehouses`, `create_order`. Good for interactive browsing by an agent; **not suitable for CI** because of the login method. The tool-to-endpoint mapping is undocumented.

## Terms

No API data-storage or redistribution terms were found. Under the repo's terms gate, **raw CJ pulls are not committed to git** until CJ's data-use terms are read and recorded. They go to the gitignored `data/private/`; only our own derived decisions (shortlist, margin results) are committed.

## Live findings (2026-11-04, first key)

Raw replies are in `data/private/probe/` (not committed). Status of each former unknown:

| # | Unknown | Answer [data] |
|---|---|---|
| 1 | Does `listV2` `countryCode` filter to US stock? | **Yes.** `countryCode=US` returns only products with US-warehouse stock: 3,964 products in total. `warehouseInventoryNum` then equals the US total from the stock endpoint (28 = 28 on the sample). Without a country, `totalRecords` stops at 6,000 (a result cap, not the catalogue size). |
| 2 | Do stock endpoints show CJ's public stock? | **Yes.** `GET /product/stock/getInventoryByPid?pid=` and `/product/stock/queryByVid?vid=` return per-warehouse rows (`countryCode` CN/US, `totalInventoryNum`, `cjInventoryNum`, `factoryInventoryNum`) plus `variantInventories`. |
| 3 | `inventories[]` in detail? | Present but **null**. Use the stock endpoints. `product/query` with `countryCode=US` returns only the US-stocked variants (5 of 9 on the sample). |
| 4 | Rate limit, token cap | 1.1 s spacing never hit a 429; latency 1.4–5 s per call. Several `getAccessToken` calls within ~30 min all succeeded. Auth returns `accessTokenExpiryDate`, `refreshToken`, `refreshTokenExpiryDate`, `openId`. |
| 5 | `sellPrice` format | String: single (`"1.36"`) or range (`"0.57 -- 0.69"`). Detail `suggestSellPrice` uses `"10.29 - 11.94"`. `variantSellPrice` is a number. Weights in detail are strings (`"30.00"`). `materialNameEn` / `packingNameEn` are JSON-encoded list strings (`'["Leather"]'`). |
| 6 | Freight start country, `logisticAging` unit | `startCountryCode=US` works for a US-stocked variant: GOFO+ $5.18, `"3-8"` (unit not documented; days assumed). Adding `zip` changes the price ($5.97 for 10001). A variant with no stock at the start country returns **1600300 "Request body is required…"**, not an empty list. CN→US: CJPacket Sensitive Pro $5.13, `"5-11"`. |
| 7 | Points per call | Not in any response. Still unknown. |
| 8 | Data-use terms | Still unknown. Raw stays in `data/private/`. |

Also: the category tree (`/product/getCategory`) has 578 leaves and no trading-card, collectibles-supplies or record-care category. Keyword search matches any word ("card holder" returns wallets and phone mounts), so relevance needs our own filter.

## Minimal call sequence

1. `getAccessToken` with the key.
2. `listV2` with `keyWord`, `countryCode=US`, `size=100`, page through.
3. `product/query` with `pid` and `countryCode=US` for variants and images.
4. Stock per warehouse: `product/stock/getInventoryByPid` (detail `inventories` is null).
5. `freightCalculate` for one unit to a US address.

## Sources
1. https://developers.cjdropshipping.com/en/api/api2/api/auth.html
2. https://developers.cjdropshipping.com/en/api/api2/api/product.html
3. https://developers.cjdropshipping.com/en/api/api2/api/storage.html
4. https://developers.cjdropshipping.com/en/api/api2/api/logistic.html
5. https://developers.cjdropshipping.com/en/api/api2/standard/points.html
6. https://developers.cjdropshipping.com/en/api/api2/standard/ps-code.html
7. https://developers.cjdropshipping.com/en/api/api2/mcp.html ; https://github.com/CJ-dropshipping/api-mcp
8. https://developers.cjdropshipping.com/en/api/api2/standard/frequency.html (did not load)
