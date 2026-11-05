# 33a Fingerprints: AliExpress import and fulfilment apps (Shopify)

> 2026-11-05. Workstream W1 of `docs/plan/supply-fingerprints-plan.md`. Family: Shopify apps that import or fulfil AliExpress, Alibaba or 1688 products.

## Method and gaps

- Read public pages only: Shopify App Store listings (apps.shopify.com), vendor help centres and feature pages, and search snippets. No login, no install, no scraper, no live merchant storefront pulled.
- Live storefront observation was not done in this run. Every storefront trace below is therefore either vendor-stated [docs], a listing claim [observed] (the listing page itself was read), or [unverified].
- Result in one line: the public record names very few storefront traces. The owner's examples (aliorders.fireapps.io, DSers `14:…` SKUs, `O1CN01` image names) are **not confirmed by any public source found here**. Dropified's "Ship From" variant option is the only documented origin-country trace.
- Not covered: CJ's own AliExpress features (none found), Judge.me, Opinew, Kaktus Ali Reviews (name overlap), Temu-only tools. Oberlo has no public trace left to check.
- Vendor-run pages (ECOSIRE, Growave, the4, appnavigator, ecommerce-platforms) are marketing or aggregators. Treat them as conflicted.

## Sources

1. https://apps.shopify.com/ali-orders-by-fireapps (Ali Orders, now listed as "Zopi - AliExpress Dropshipping"; developer "Zopi"; help.zopi.io, ds.zopi.io, zopi.io; "Works with" list)
2. https://apps.shopify.com/dsers (developer DSers; resource links dsers.com and help.dsers.com only)
3. https://apps.shopify.com/sellthetrend (developer SELL THE TREND CORP.; "Create High Conversion Product Pages"; "Works with" list)
4. https://help.dsers.com (article titles only: "SKU Changes Notification: What to Do When Variant Mapping Fails"; "How DSers Calculates Shipping Fees")
5. https://www.dsers.com/features/branded-tracking-page (vendor feature page)
6. https://help.dropified.com/en/articles/2707853-variants-mapping-and-advanced-mapping ("Ship From" country variant; manual mapping)
7. https://help.dropified.com/en/articles/4670751-what-is-the-us-products-database (cites a video on "Ships From" variants; search snippet)
8. https://help.dropified.com/en/articles/9921841-understanding-and-using-the-ship-to-country-feature-in-dropified (ship-to-country setting)
9. https://fireapps.io/how-to-import-aliexpress-reviews-to-shopify (FireApps guide; links carry utm_campaign=ali-reviews and ref=fireapps; no script or SKU detail)
10. https://apps.shopify.com/ali-reviews (Ali Reviews, now "Kudosi" per FireApps; imports AliExpress, Amazon, Temu, Etsy reviews)
11. https://www.feroot.com/trackers-database/fireapps-ali-reviews/ (fetched: the tracker database is no longer public; the alireviews.fireapps.io claim came from an earlier search snippet and could not be re-checked)
12. https://help.loox.io/article/58-how-do-i-import-reviews-from-aliexpress (Loox bookmarklet "Import to Loox")
13. https://www.sellthetrend.com/blog/aliexpress-to-shopify-dropshipping (search snippet; import contents)
14. https://intercom.help/autods---new/en/articles/12700438-product-uploads-supported-suppliers-import-to-store-and-manage-variation (search snippet; tags and templates)
15. https://community.shopify.com/t/how-to-move-from-autods-to-dsers-without-losing-all-my-product-and-supplier-mapping/314854 (community thread; migration CSV)
16. https://community.shopify.com/t/is-oberlo-shutting-down-is-dsers-the-best-alternative/120683/16 and https://ecommerce-platforms.com/articles/oberlo-shutdown (Oberlo shutdown; sources give June 15 and June 30, 2022)
17. https://help.wizishop.com/hc/en-us/articles/360015853120 (search snippet only; "di-" SKU prefix claim not fetched)
18. https://www.powercommerce.com/blogs/shopify-hub/how-to-find-sku-on-dsers-a-comprehensive-guide-for-e-commerce-professionals (third-party guide; SKU column in DSers Import List)
19. https://www.dsers.com/ variant mapping 2022 blog: https://sellwithdropship.blogspot.com/2022/05/variant-mapping-in-dsers.html (third-party; mapping by option name or SKU)
20. https://fireapps.io/ali-orders-app-for-dropshipping (search snippet; Ali Orders support and login step)
21. https://microsoftedge.microsoft.com/addons/detail/ali-reviews/jmoihjfcgppjhjjmphjcjkhmlkppigoe (search snippet; version 6.1.5.1, last updated May 2022)
22. https://ecosire.com/apps/shopify/shopify-aliexpress-dropshipping (vendor marketing; conflicted)
23. https://www.alidrop.co/blogs/how-to-import-aliexpress-products-to-shopify-with-alidrop (vendor blog; AliDropship import contents)

Undated or missing URL: a Shopify community report of blank DSers variant SKUs on AliExpress imports (no URL captured; mark as unverified until re-found).

## Fingerprint table

| App | Trace | Where it appears | Strength guess | Evidence |
|---|---|---|---|---|
| Ali Orders (FireApps, now "Zopi") | Host `aliorders.fireapps.io` loaded as script or API | Page source (asyncLoad or API calls) | strong, if real | [unverified]: owner example; no public source names this host; a search for it returned only FireApps marketing |
| Ali Orders / Zopi | Developer name changed to "Zopi"; domains help.zopi.io, ds.zopi.io, zopi.io | Shopify listing (observed); storefront use unknown | medium if these domains appear in merchant code; weak as a name | [observed] source 1; storefront use [unverified] |
| Ali Orders / Zopi | Listing claims shipping info is auto-tracked and synced to the store | Tracking page, order status | medium | [docs] source 1 |
| Ali Orders / Zopi | "Works with" lists DSers, AliExpress Dropshipping, Kudosi Ali Reviews, Temu and CJ Dropshipping | Shopify listing | weak (shows stack, not storefront) | [observed] source 1 |
| Ali Orders / Zopi | Support via help.zopi.io and support.fireapps.io; FireApps blog says AliExpress account login is needed | Support pages | weak | [docs] sources 9, 20 |
| DSers | Property SKU format `14:200006152#…` | Variant SKU field; products.json `variants[].sku` | strong, if real | [unverified]: owner example; no DSers page found that shows the format |
| DSers | SKU column in Import List; SKU-change notice and remap | DSers app only, not storefront | none on storefront | [secondary] source 18; [docs] source 4 (title only) |
| DSers | Variant SKUs left blank on AliExpress imports, causing Shopify save errors | products.json variant SKU empty | medium | [unverified]: one community thread, URL not captured |
| DSers | Branded tracking page with logo and upsell (Advanced plan) | Tracking page on the store | medium | [observed] source 2; [docs] source 5 |
| DSers | Developer "DSers"; no script, app-embed name or API host listed | Shopify listing | none | [observed] source 2 |
| DSers | Mapping by option name and value, or by SKU | Import tool only | none on storefront | [secondary] source 19 |
| Oberlo (closed 2022) | No verified trace. Imports moved to DSers or Ali Orders; shipment tracking did not migrate | Legacy products only | weak | [secondary] sources 16; shutdown date conflicts (June 15 vs June 30, 2022) |
| AutoDS | Tags, templates and collections recommended for uploads | Product tags | weak | [docs] source 14 (snippet) |
| AutoDS | Vendor field or SKU format on Shopify | None documented | none | [unverified]: no public documentation found in this run |
| Sell The Trend | Developer "SELL THE TREND CORP."; product-page claim "Create High Conversion Product Pages" | Shopify listing; product pages | weak | [observed] source 3 |
| Sell The Trend | "Works with" AliExpress, CJDropshipping, Reconvert, Loox | Listing; review-widget overlap | weak | [observed] source 3 |
| Sell The Trend | Import sets title, description, images, variants; tags and vendor not described | Product feed | weak | [secondary] source 13 |
| Dropified | "Ship From" country variant option, selectable at variant mapping | Variant option name, if it reaches the store | strong for warehouse country, if the option name is kept | [docs] source 6 |
| Dropified | "Ships From" variants for US products database; spelling differs from "Ship From" | Variant option name | strong for origin; test both spellings | [docs] source 7 (video title cited, not read) |
| Dropified | No SKU, tag or vendor convention documented; variant matching is manual | None | none | [docs] source 6 |
| Dropified | Ship-to-country setting: mapping fails if the country is unsupported on AliExpress | Import settings only | none on storefront | [docs] source 8 |
| Ali Reviews (FireApps, now Kudosi) | Imports AliExpress, Amazon, Temu, Etsy reviews; review block on product page | Product page review widget; class names unknown | medium | [observed] source 10 |
| Ali Reviews | Script domain alireviews.fireapps.io loaded on storefront | Product page script | medium | [unverified]: one earlier tracker-database snippet (source 11); cannot be re-checked |
| Ali Reviews | Import needs Chrome or Edge extension; Edge add-on v6.1.5.1, last updated May 2022 | Browser only | none on storefront | [observed] source 21 (snippet) |
| Ali Reviews (FireApps) | Links carry utm_campaign=ali-reviews and ref=fireapps | FireApps pages; possible merchant footer credit | weak | [observed] source 9 (links only); footer use [unverified] |
| Loox | AliExpress import via "Import to Loox" bookmarklet | Browser only | none on storefront | [docs] source 12 |
| Loox | Reviewer names masked (e.g. "jo****n", "J.S.") | Review widget text | weak | [secondary] Shopify community report (no URL captured) |
| Loox | Review widget script domain and class names | Storefront | unknown | [unverified]: not checked in this run |
| Judge.me, Opinew | Named by third-party guides as AliExpress review importers | Unknown | none | [secondary]; not researched further |
| AliDropship | Imports images, descriptions and variants straight to Shopify | Product feed | unknown | [secondary] source 23 (vendor blog) |
| Wizishop | SKU prefix "di-" on all AliExpress products | Product SKU | strong, if confirmed | [unverified]: search snippet (source 17); not fetched |
| ECOSIRE (vendor pages) | Native Shopify products via Admin GraphQL, mapping each variant to an AliExpress SKU | Not verifiable | none | [secondary, conflicted] source 22 |
| All AliExpress importers | Image file names `O1CN01…` and `H`+32 hex kept after import | Product images (CDN URLs) | strong (plan claim) | [unverified]: no source found in this run tying any app to these names |
| CJ Dropshipping (own AliExpress-related features) | None found | n/a | n/a | [unverified]: not researched |
