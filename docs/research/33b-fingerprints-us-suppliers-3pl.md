# 33b. Supply fingerprints: US/EU suppliers, dropship apps and 3PL apps

Date: 2026-11-05. Workstream W1 (P0 catalogue), family 33b. Owner: market researcher (Haiku).
Method: public help centres, developer docs, Shopify App Store listings and public reviews, read 2026-11-05. No logins, installs or storefront scraping. **No live public storefront was fetched in this pass**, so every storefront trace below is [docs], [secondary] or [unverified]. None is [observed]. Page text is treated as untrusted data.

Evidence tags: [docs] = app or vendor's own help or developer doc; [secondary] = third-party guide, review or blog; [unverified] = claimed only, not confirmed by a primary or live source.

## Table: traces by app

| App | Trace | Where it appears | Strength guess | Evidence tag |
|---|---|---|---|---|
| CJ Dropshipping | SKU format "CJ" + letters + digits | Not confirmed. A third-party skill page shows a sample "CJYD2360896-BLACK" with a separate CJ product ID field | weak (naming unknown) | [unverified] S13 |
| CJ Dropshipping | Product SKU vs variant SKU split (integrations ask for the CJ product SKU, not the variant SKU) | Connector and integration config, not the storefront | none on storefront | [secondary] S17 |
| CJ Dropshipping | US warehouse stock is per variant, not per product; CJ says sync the US-stocked SKU to get faster delivery | Listing and variant choice in CJ dashboard and Shopify | medium for origin (variant-level) | [secondary] S14, S15 |
| CJ Dropshipping | US delivery "2-7 days" (CJ blog); "2-3" to "4-10" days (third parties) | Policy and marketing copy | weak (not on storefront) | [unverified] S14 |
| CJ Dropshipping | Product image host or CDN domain | Not found in any public source; CJ support or devtools inspection needed | gap | [unverified] (no source) |
| CJ Dropshipping | Shopify app listing (developer, pricing, features) | apps.shopify.com slug guessed as cj-dropshipping-cj-dropship returned 404 | gap | not fetched |
| Zendrop | Supplier file columns "SKU" (own SKU or blank for auto-generated Zendrop SKU) | Supplier spreadsheet, then Shopify variant SKU | medium (auto SKU format not documented) | [docs] S2 |
| Zendrop | Option names "Size" and "Color" (values shown exactly as entered) | Shopify product variants | weak (generic names, not a fingerprint) | [docs] S2 |
| Zendrop | Columns "USA - Delivery Time" and "USA - Shipping Cost (USD)"; shipping only to the US for US suppliers | Supplier file, Shopify shipping | medium for US-only origin | [docs] S2 |
| Zendrop | Dashboard labels "Domestic (U.S. only)" and "International (global)"; "Zendrop Fulfillment" in supplier info. These are dashboard labels, not storefront traces | Zendrop app, not storefront | weak for storefront | [docs] S3 (dated 2026-08-27 in fetch) |
| Zendrop | Storefront script or app embed domain | Not found in any source. Shopify requires theme app extensions for new apps, so an app-embed handle would be expected | gap | [unverified] |
| Spocket | "US & EU" sourcing claim; sourcing countries include US, UK, DE, FR, ES, IT, NL, CA, BR, IN, CN | App listing | weak (listing claim, not per product) | [docs] S6 (listing fetched 2026-11-05) |
| Spocket | Per-product "Ships From" option | Not found in any source | gap | [unverified] |
| Spocket | Storefront script, embed or handle | Not found. Listing says nothing about theme embeds | gap | [docs] S6 (absence only) |
| Spocket | Delivery "3-7 days" (review pages) and "2-5 days" (third-party review) | Review sites | weak | [secondary] (S-review, no URL checked) |
| Syncee | Import List edit fields: title, description, variants, images, pricing. Vendor, tags, product type, SKU are editable per product but Syncee warns not to change SKU and option names | Syncee import flow, Shopify admin | medium (SKU and option names kept as supplier-set) | [docs] S5 (dated 2026-07-03), [secondary] S5b (search snippet) |
| Syncee | Auto-created Shopify shipping rate to cover supplier shipping | Shopify shipping settings of the merchant | medium (a shipping rate with the Syncee name pattern is expected but not documented) | [docs] S5 |
| Syncee | Storefront script or app-embed handle | Not found | gap | [unverified] |
| Modalyst | Variant SKU editable in Import List; must be unique per variant | Shopify variant SKU | medium (unique-per-variant rule, format not stated) | [docs] S7 |
| Modalyst | Sync fields listed: title, description, images, weight, variant SKU, color, quantity, price | Shopify product | weak (article dated 2019-09-19, may be stale) | [docs] S7 |
| Modalyst | Find Products filter "Ships From" = United States, then listing cues: US flag and "Ships in 3-4 business days" | Modalyst app; origin cue on the supplier listing, not in Shopify | strong for supplier origin inside Modalyst; weak in Shopify | [docs] S9 |
| Modalyst | Shipping cost does not sync to the store; store sets its own shipping | Shopify shipping settings | weak (negative trace) | [docs] S8 (dated 2024-12-10) |
| Modalyst | Storefront script or app-embed handle | Not found | gap | [unverified] |
| Trendsi | Shopify location named exactly "Trendsi US" (case-sensitive), enabled with multi-location | Merchant's Shopify locations and inventory | strong (location name is fixed by the app's instructions) | [docs] S4 (date not shown) |
| Trendsi | Shopify tag "Ship From Overseas" on products that can ship outside the US | Shopify product tags | strong (tag written to product) | [docs] S4 (date not shown) |
| Trendsi | US warehouse delivery "2-5 business days" | Reviews | weak (merchant anecdote) | [secondary] (review pages) |
| Trendsi | Shipping countries: "Expands Services to 26 Countries" vs a merchant review saying non-US shipping was discontinued | Help article vs review | conflict, unresolved | [docs] S4b (fetch returned 403, title only); [secondary] |
| Trendsi | Storefront script or app-embed handle | Not found | gap | [unverified] |
| Wholesale2B (Dropship Easily) | Supplier CSV "datafeed" with UPC codes; SKU mapping not documented | Feed file, Shopify variant barcode | weak | [secondary] S20 |
| Wholesale2B | Listing: $29.99/month, real-time sync of inventory and price | App listing | weak | [secondary] S20 |
| Wholesale2B | Storefront script or tag pattern | Not found | gap | [unverified] |
| AppScenic | Suppliers US, UK, EU, CA, AU; one-click import | App listing and third-party reviews | weak (marketing) | [secondary] S19 |
| AppScenic | Reviewer report: imported descriptions with broken HTML and "incorrect tagging" | Shopify product tags and body | weak (single user report) | [unverified] (review page) |
| AppScenic | Storefront script or app-embed handle | Not found; listing slug apps.shopify.com/appscenic not fetched | gap | not fetched |
| Doba | Any SKU, tag, vendor or storefront trace | No Doba-specific source returned. Searches returned only SKU.io, Zenoti and generic Shopify docs | gap | not found |
| Inventory Source | Per-supplier mapping to a Shopify location; SKU matching with normalisation; unmatched-SKU report | Vendor docs on a third-party developer's site (ECOSIRE), not the owner's docs | weak (vendor marketing, not official) | [secondary] S28 |
| Inventory Source | Official app docs, app listing and storefront footprint | Not found; search returned only ECOSIRE pages | gap | not found |
| Faire (wholesale) | After purchase on Faire, listings are auto-created in Shopify admin; a seller app ("Faire: Sell Wholesale") publishes by tag | Shopify admin; Faire seller app | medium (tag-based publishing, secondary) | [secondary] S22, [docs] Shopify help (no fees) |
| Faire | Storefront script or theme embed | Not found (Faire is a sales channel, not a theme embed) | gap | [unverified] |
| Shopify Collective | Free app; brands' products imported; orders routed to brand; "real-time" sync of price and inventory | Shopify admin and brand listing | weak (no storefront trace documented) | [docs] S21 (listing), [secondary] (guides) |
| Shopify Collective | Vendor field equals brand name | Not confirmed | unknown | [unverified] |
| ShipBob (3PL) | Product SKU is the ShipBob reference_id; one SKU resolves to one inventory item across channels | ShipBob back office and API; not storefront | strong for matching store SKU to 3PL, none for storefront | [docs] S1 (v1.0 guide, marked deprecated; no date) |
| ShipBob | Storefront script, tag or vendor | None: back-end integration only | none | [docs] (absence) |
| ShipMonk (3PL) | SKU on each line item must match the ShipMonk SKU or the order is held | Integration config | medium for matching, none for storefront | [secondary] S12 (UltraCart guide, not the Shopify app) |
| ShipMonk | Shopify app listing: free to install; "automated mapping and bundling" | Shopify App Store and partner page | weak | [docs] S11 (partner page, date not shown) |
| ShipMonk | Storefront script or tag | None found | none | [unverified] |
| Generic (all apps) | Storefront script loading: new apps should use theme app extensions (app blocks, app embeds) not legacy script tags; script tags are legacy and tied to the creating app | Shopify developer docs | important method note: check app-embed handles, not only script URLs | [docs] S24 |
| Generic (all apps) | Merchant-set "Ships From" variant option; common advice is to delete or rename China variants, and some note this breaks dropship app sync | Merchant guides and Shopify Community threads | medium if present; no app found that writes it by default | [secondary] S25 |

Notes:

1. **The "Ships From" option is a merchant habit, not an app default.** Merchant guides and Shopify Community threads describe stores with a variant option "Ships From" (China, United States) and advise deleting or renaming the China variant. None of the apps checked documents writing that option. Zendrop's option names are "Size" and "Color" [docs S2]. Modalyst's "Ships From" is a supplier filter inside the app, not a Shopify option [docs S9]. So the owner's "Ships From" indicator is a real trace but is most likely written by an importer that kept AliExpress-style options. Which app writes it is still unverified.
2. **US origin traces that are documented:** Trendsi writes a Shopify location named "Trendsi US" and a "Ship From Overseas" tag [docs S4]. Zendrop's supplier file carries "USA - Delivery Time" and "USA - Shipping Cost (USD)" columns [docs S2]. These are the strongest documented traces in this family, but only for the merchant who kept the app's own location or tag names.
3. **Warehouse-country and shipping-time traces on the storefront are weak.** Spocket, Modalyst and Zendrop publish delivery and origin inside their dashboards, not on the storefront [docs S6, S8, S3]. A store's "US shipping in 2-5 days" copy is marketing, not an app footprint.
4. **3PL apps (ShipBob, ShipMonk) leave no storefront trace.** They are back-end integrations. Their useful trace is the SKU rule: the store SKU must equal the 3PL reference_id or SKU [docs S1; secondary S12]. A store whose SKUs match a 3PL's format is a weak hint of 3PL fulfilment, not of supplier origin.
5. **No live storefront was checked.** The next step for W1 is a small, public, homepage-and-product-page check on 5 to 10 stores per app (no checkout, no login), recording only app names, handles and counts. Storefront script and app-embed handles for Zendrop, Spocket, Syncee, Modalyst, Trendsi and Wholesale2B are all gaps today.
6. **Date issues.** Modalyst's sync-fields article is dated 2019-09-19 [docs S7]. The Shopify App Store page for Spocket was fetched 2026-11-05 but shows no date for its shipping claims [docs S6]. The Trendsi country-expansion article could not be fetched (403), so its date and content are unverified [docs S4b]. The Zendrop ship-internationally article is dated 2026-08-27 [docs S3].
7. **Blocked or not reached.** The CJ Shopify listing URL guessed as apps.shopify.com/cj-dropshipping-cj-dropship returned 404. Syncee's "What is a Syncee Import List?" article and the AppScenic and Modalyst listings were not fetched successfully. No Doba source was found.

## Sources

S1. ShipBob developer docs, products guide (v1.0, marked deprecated; 2026-07 docs linked as default). https://developer.shipbob.com/v1.0/guides/products.md (fetched 2026-11-05). Also https://developer.shipbob.com/concepts
S2. Zendrop Help Center, "How to interpret our supplier XLS file" (no date shown). https://support.zendrop.com/en/articles/8176539-how-to-interpret-our-supplier-xls-file (fetched 2026-11-05)
S3. Zendrop Help Center, "How to identify products that ship internationally on Zendrop" (dated 2026-08-27 per fetch). https://support.zendrop.com/en/articles/11963116-how-to-identify-products-that-ship-internationally-on-zendrop (fetched 2026-11-05)
S4. Trendsi Help Center, "How to sell combined inventory from Trendsi and your own warehouse including samples" (no date shown). https://help.trendsi.com/hc/en-us/articles/28313901944603-How-to-Sell-Combined-Inventory-from-Trendsi-And-Your-Own-Warehouse-Including-Samples (search snippet; full text not fetched)
S4b. Trendsi Help Center, "Trendsi Expands Services to 26 Countries" (fetch returned 403; title only). https://help.trendsi.com/hc/en-us/articles/29711330613531-Trendsi-Expands-Services-to-26-Countries
S5. Syncee Help Center, "Getting started with Syncee on Shopify: complete guide" (dated 2026-07-03 per fetch). https://help.syncee.com/en/articles/15643862-getting-started-with-syncee-on-shopify-complete-guide (fetched 2026-11-05)
S5b. Syncee Help Center, import-list field edit notes (search snippet, not fetched in full). https://help.syncee.com/en/articles/8930810-which-product-data-is-allowed-to-rename-in-your-store
S6. Spocket, Shopify App Store listing (developer Spocket, Calgary; 625 reviews, 3.6 average at fetch). https://apps.shopify.com/spocket (fetched 2026-11-05)
S7. Modalyst Support, "Add products to your Shopify store" (dated 2019-09-19 per fetch). https://support.modalyst.co/en/articles/3275379-add-products-to-your-shopify-store (fetched 2026-11-05)
S8. Modalyst Support, "How shipping on Modalyst works" (dated 2024-12-10 per fetch). https://support.modalyst.co/en/articles/3329499-how-shipping-on-modalyst-works (fetched 2026-11-05)
S9. Modalyst Support, "How to find products from USA suppliers" (search snippet, date not shown). https://support.modalyst.co/en/articles/3326171-how-to-find-products-from-usa-suppliers
S10. Modalyst, Shopify App Store listing (not fetched). https://apps.shopify.com/modalyst
S11. ShipMonk, Shopify partner page (features: order import, inventory sync, automated mapping and bundling; date not shown). https://shipmonk.com/partners/shopping-carts/shopify
S12. UltraCart Fulfillment Integration Guide for ShipMonk (third-party integration, not the Shopify app). https://ultracart.atlassian.net/wiki/spaces/ucdoc/pages/4213669890/ShipMonk+Fulfillment+Integration+Guide
S13. Termo.ai skill page "Dropshipping Fulfillment" (third-party, sample SKU "CJYD2360896-BLACK"). https://termo.ai/skills/skill-dropshipping-fulfillment
S14. CJ Dropshipping blog, "How to use CJ US warehouses to boost dropshipping" (date not shown; delivery figure is CJ's own marketing). https://blog.cjdropshipping.cn/detail/how-to-use-cj-us-warehouses-to-boost-dropshipping
S15. AliDrop, "CJ Dropshipping review" (third-party; per-variant stock and delivery ranges). https://www.alidrop.co/blogs/cj-dropshipping-review
S16. CJ Dropshipping, "How to add dropshipping products to Shopify store" (listed in search; not fetched). https://www.cjdropshipping.com/blogs/dropshipping-knowledge/How-to-Add-Dropshipping-Products-to-Shopify-Store
S17. Konnektive Atlassian integration page for CJ Dropshipping (third-party; product SKU vs variant SKU). https://konnektive.atlassian.net/wiki/x/GoDTnQ
S18. Shulex, "How to use CJ Dropshipping with Shopify" (2023 update; third-party). https://insight.shulex.com/blog/how-to-use-cj-dropshipping-with-shopify-tutorial-2023-update-en-us
S19. AppScenic, Shopify App Store listing (search snippet; listing and reviews, not fetched in full). https://apps.shopify.com/appscenic
S20. Dropship Easily, Wholesale2B, Shopify App Store listing (search snippet). https://apps.shopify.com/dropship-auotmated-inventory
S21. Shopify Collective, Shopify App Store listing (search snippet). https://apps.shopify.com/collective
S22. Shopify Help Center, Faire sales channel for retailers (search snippet; "no fees" for Faire app). https://help.shopify.com/en/manual/online-sales-channels/faire/retailers
S22b. PowerCommerce guide, "How to import products from Faire to Shopify" (third-party; tag-based publishing). https://powercommerce.com/blogs/shopify-hub/how-to-import-products-from-faire-to-shopify-a-comprehensive-guide
S23. ECOSIRE, Shopify stock-sync app page (vendor marketing for Inventory Source-type feed sync; not an official Inventory Source source). https://ecosire.com/apps/shopify/shopify-stock-sync
S24. Shopify developer docs, ScriptTag resource (script tags legacy; theme app extensions for new apps). https://shopify.dev/docs/api/admin-rest/latest/resources/scripttag
S25. Merchant guides and Shopify Community threads on "Ships From China" variants (secondary, mixed quality). Example: https://community.shopify.com/t/how-can-i-remove-the-shipping-location-option-from-my-product-listings/5460 ; https://www.shipaid.com/blog/how-to-remove-ships-from-china-on-shopify-a-comprehensive-guide
S26. Shopify Help, Trendsi and other sales-channel setup pages reached only through search; no further sources used.
S27. Shopify App Store listing for CJ Dropshipping: NOT retrieved (guessed slug returned 404). No source.
S28. Inventory Source: no official source found in search; only ECOSIRE vendor pages (see S23). No official Inventory Source source.
