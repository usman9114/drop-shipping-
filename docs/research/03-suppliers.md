# 03 — Suppliers and their APIs

> Researched 2026-11-03 by a web-search agent. Official pages were reachable for only a few vendors. Most pricing comes from aggregators that disagree by up to 2x. Check vendor pricing pages before spending money.

## Supplier comparison

| Supplier | Origin | Shipping to US (claimed) | Pricing | eBay-compliant "wholesale"? |
|---|---|---|---|---|
| AliExpress (Dropshipping Center) | China | 15–45 days standard; 7–20 Choice/Selection; 3–7 express; some local warehouses | Free; pay per order | **No: retail marketplace** (see 01) |
| CJ Dropshipping | China + US/EU warehouses | Varies (unverified) | Free tier, paid tiers | Dropship agent. A grey area: it presents itself as a supplier/agent, not a retailer |
| Spocket | US/EU suppliers (+ AliExpress/Temu catalog since 2025) | 2–5 business days for US/EU (vendor claim) | $39.99–$299.99/mo (official page) | US/EU suppliers are closer to wholesale |
| Zendrop | Mixed, some US fulfillment | 3–12 days | $49–79/mo, free tier | Agent-style |
| DSers | AliExpress | Same as AliExpress | Free to ~$499/mo | No (AliExpress) |
| Syncee | Global brands marketplace | Varies | ~$19–40/mo | Mixed |
| Doba | US suppliers | — | ~$25–175/mo | Wholesale-leaning |
| Wholesale2B | US wholesale feeds | — | ~$30–38/mo | **Wholesale** |
| Inventory Source | Aggregator of US distributors | — | ~$99/mo | **Wholesale** |
| Faire | US/EU brands | n/a | Brand minimums | Wholesale only, **no dropship** |
| Alibaba | China factories | Slow, sample-first | Free; Trade Assurance | Wholesale (minimum order quantities) |

## API availability (needed for automation)

| Supplier | Catalog | Price/stock | Place order | Tracking | Access |
|---|---|---|---|---|---|
| **CJ Dropshipping** | ✅ | ✅ | ✅ | ✅ | API key → `CJ-Access-Token`. Free, no stated approval gate. **Also has an MCP server.** |
| AliExpress Open Platform | ✅ (affiliate product query) | ✅ | ⚠️ needs business verification and partner approval | likely | App key/secret |
| Doba | ✅ | ✅ | ✅ | ✅ | Paid tier only; ~3–5 req/s (unverified) |
| Inventory Source | ✅ (claimed) | ✅ | ✅ | ✅ | Request access |
| Spocket, Zendrop, DSers, Syncee, Wholesale2B | ❓ | ❓ | ❓ | ❓ | Mostly Shopify/Wix app integrations; public API not confirmed |
| Faire | ❌ | ❌ | ❌ | ❌ | — |

**For a PoC, CJ Dropshipping is the most practical fully-automatable supplier.** Its API is free and covers catalog, stock, orders and tracking, and it has US warehouses. Wholesale2B and Inventory Source are the eBay-policy-safe options, but their API access is gated or unconfirmed.

## Blind shipping and branding

- CJ, Zendrop and others advertise plain packaging, custom inserts and branded packaging. This usually needs a paid plan or a minimum order quantity.
- When ordering from Alibaba, confirm before ordering that the supplier will ship single units with no invoice in the box.

## Quality control

- "Verified" and "Gold Supplier" badges on Alibaba are weak signals.
- **Order samples.** Watch for the "sample trap": the sample is good but bulk quality differs.
- Pay through Trade Assurance. A supplier that refuses to sell samples is a red flag.
- Track the defect rate over your first ~30 orders per supplier.

## Stock/price sync risk on eBay

- Cancelling an order because the item is out of stock **counts as a transaction defect**.
  - The allowed rate is 2%.
  - Below Standard is triggered only when defects involve more than 4 distinct buyers.
  - Misstating the cancel reason to avoid a defect is a policy violation.
- **Mitigation:**
  - sync stock more often than orders arrive
  - set quantity to 0 when the supplier is out
  - prefer suppliers with stock APIs
  - list fewer SKUs with buffer stock
- Defects reportedly age out after ~12 months (forum claim, not policy).

## Sources
- CJ developer docs: https://developers.cjdropshipping.com/en/summary ; MCP: https://developers.cjdropshipping.com/en/api/api2/mcp.html
- Spocket pricing: https://www.spocket.co/pricing
- Zendrop plans: https://support.zendrop.com/en/articles/9981459-zendrop-plans-pricing-and-features
- DSers pricing: https://avada.io/blog/dsers-pricing/
- Syncee: https://syncee.com/pricing
- Doba: https://www.bigcommerce.com/apps/doba ; https://us.fitgap.com/products/006242/doba
- Wholesale2B: https://www.wholesale2b.com/pricing
- Inventory Source: https://www.inventorysource.com/pricing-plans/
- Faire: https://www.faire.com/support/articles/18524831904667
- AliExpress Open Platform: https://openservice.aliexpress.com/ ; unofficial SDK https://github.com/luya2/ae_sdk-api
- AliExpress shipping times: https://findniche.com/blog/aliexpress-shipping-time
- eBay seller standards: https://www.ebay.com/help/policies/selling-policies/seller-standards-policy?id=4347
- eBay global seller performance: https://www.ebay.com/help/selling/selling-seller-performance/global-seller-performance-standards?id=4351
- eBay order cancellation: https://www.ebay.com/help/policies/member-behavior-policies/order-cancellation-policy?id=5298
- Alibaba supplier risk: https://www.globalsources.com/knowledge/is-alibaba-reliable/
