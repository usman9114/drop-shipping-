# 33c. Supply fingerprints: print-on-demand apps, themes and marketing kits, tracking apps and carriers

> Workstream W1 (see `docs/plan/supply-fingerprints-plan.md`). Family 33c. Public sources only, accessed 2026-11-05. No logins, installs or scrapers. Page text was treated as untrusted data.
>
> **Limit of this pilot:** no live merchant storefront was fetched. Storefront traces (script hosts, `Shopify.theme`, tracking-page paths on a real store) are therefore **[unverified]** until a live store is checked. Listing pages on apps.shopify.com and vendor docs were read directly and are tagged accordingly.

## Table: traces by tool or carrier

| Tool or carrier | Trace | Where it appears | What it reveals about supply | Evidence tag |
|---|---|---|---|---|
| Parcel Panel (ParcelPanel) | Default tracking page path `/apps/parcelpanel` on the store domain, served through Shopify's app proxy | Store domain, `/apps/parcelpanel` (vendor docs, article 44) | Store uses ParcelPanel tracking. Tells us the store tracks its orders, not where stock comes from | [docs] https://docs.parcelpanel.com/article/44 |
| Parcel Panel | Tracking widget on the order-status page (app block or older toggle) | Order status page (vendor docs) | Post-purchase tracking app installed. Weak on supply | [docs] https://docs.parcelpanel.com/shopify/tracking-page/order-status-page |
| Parcel Panel | Custom tracking page built in admin with a container div and script tag | Custom Shopify page (vendor docs) | Script tag name and container id would be a fingerprint. Exact strings not captured | [docs] https://docs.parcelpanel.com/article/44 ; [unverified] exact markup |
| Track123 | Branded tracking page and order lookup page, "interactive map-based tracking pages" | Vendor app listing (feature list) | App installed. The page names no carriers, so it reveals no origin on its own | [observed] https://apps.shopify.com/track123 (accessed 2026-11-05) |
| Track123 | Carrier coverage: no Chinese carrier named on the listing; carrier count not stated | Vendor app listing | No origin signal from the listing. Carrier list would need the app's own carrier page | [observed] https://apps.shopify.com/track123 |
| 17TRACK (Shopify app) | Free plan "Access 3,300+ carriers"; feature "hiding Chinese origin info in one click" | Vendor app listing | The app offers a feature to hide China origin on tracking pages. Its presence is a reason to check tracking text carefully, not a supply signal | [observed] https://apps.shopify.com/17track (accessed 2026-11-05) |
| 17TRACK (carrier coverage) | Lists YunExpress, YANWEN, 4PX on its own site; app listing mentions Cainiao and Yun Express. Counts differ between pages (1,700+ vs 3,200+) | 17TRACK site and app listing (search snippets) | Carrier names on a store tracking page would reveal origin. Cainiao support is disputed | [unreliable: lookalike domain, not 17TRACK's own site] https://17tracsks.it.com/ ; [observed listing] https://apps.shopify.com/17track ; conflict noted |
| 17TRACK / Cainiao | Shopify community thread: users report 17TRACK and AfterShip cannot track Cainiao orders | Shopify community forum | Cainiao tracking may be missing from these apps. Do not rely on Cainiao as a tracking-page signal | [secondary] https://community.shopify.com/t/how-do-you-guys-are-tracking-cainiao-orders/13325 ; [unverified] date and current status |
| AfterShip | Carrier page for YunExpress; users enter a YunExpress number and the AfterShip Tracking Page collects data | AfterShip carrier pages | Confirms YunExpress is a tracked China-origin carrier in the AfterShip ecosystem | [secondary] https://www.aftership.com/he/carriers/yunexpress (search snippet; en page returned HTTP 403 on fetch, 2026-11-05) |
| TrackingMore | Network of 1622 carriers including YunExpress; YunExpress tracking page | TrackingMore carrier page | Confirms YunExpress coverage. Vendor claim | [secondary] https://www.trackingmore.com/yunexpress-tracking/en.html |
| Yanwen | Tracking number format: 13 alphanumeric characters, two letters at the start, ends in YP, CN or YW, 9 digits between | Tracking number on a store's shipping or tracking page (CWILL carrier page) | A number in this format shows a Yanwen shipment, so the store ships from China via a China 3PL | [secondary] https://www.cwill.com/carriers/yanwen/ ; number format is vendor-described, [unverified] against real samples |
| Yanwen | Described as "a leading 3PL service provider for cross-border e-commerce sellers in China" (Beijing Yanwen Logistics Co., Ltd.). Also no longer supports China Post tracking | CWILL carrier page | Direct statement of China origin for the carrier | [secondary] https://www.cwill.com/carriers/yanwen/ |
| Yanwen | Own tracking subdomain track.yw56.com.cn | Carrier site (search snippet) | Tracking link on a store page pointing to this host reveals Yanwen | [unverified] https://www.parcelpanel.com/couriers/yanwen/ redirects to cwill.com; the subdomain was not fetched |
| 4PX | Named as a carrier on 17TRACK and in tracking vendor lists | 17TRACK site (search snippet) | China-origin 3PL. Not fetched directly | [unverified] |
| YunExpress | Named as carrier on 17TRACK, AfterShip, TrackingMore | Tracking vendor carrier lists | China-origin carrier (YunExpress is a China cross-border logistics brand). Origin statement itself not fetched | [secondary] + [unverified] for origin statement |
| Cainiao | Named as carrier in Shopify community threads; support in tracking apps disputed | Shopify community | China-origin (Alibaba logistics). Presence on a tracking page points to AliExpress-linked shipping | [secondary] https://community.shopify.com/t/how-do-you-guys-are-tracking-cainiao-orders/13325 |
| CNE, SF International, China Post | Not researched in this run | none found | Would need carrier pages and tracking-page checks | [unverified] (not checked) |
| ePacket | Not researched in this run. ePacket is a USPS international service that carries China-origin parcels | none found | Would need USPS and carrier-page checks | [unverified] (not checked) |
| USPS, UPS, FedEx (domestic) | Not researched in this run | none found | Domestic carriers alone point to US shipping but do not rule out a US 3PL or a China 3PL that uses USPS last mile | [unverified] (not checked) |
| Shopify theme (any store) | `Shopify.theme` object in page source with `name`, numeric `id` and `theme_store_id` | Page source of any live Shopify storefront, per third-party detector guides | Theme identity. Merchants often rename themes. Not a supply signal alone | [secondary] https://shopplaza.io/blog/shopify-theme-detector.html ; https://bsscommerce.com/shopify/shopify-theme-detector/ ; [unverified] exact object shape |
| Shopify theme_store_id | Read-only field in the Admin REST theme resource. Returns null if the theme is not made by Shopify or was not installed from the Theme Store. Dawn example id 887 (third-party list) | Shopify Admin REST docs | A null value means a custom or non-Shopify theme. The field is not in the storefront unless the theme exposes `Shopify.theme`. Used to check whether a theme came from the Theme Store | [docs] https://shopify.dev/docs/api/admin-rest/2024-07/resources/theme ; id 887 [secondary] https://craftshift.com/shopify-theme-store-id-list-2026/ |
| Debutify | Dropshipping-positioned theme; vendor says it is built for speed and conversions; Debutify and affiliate pages claim it is free | Vendor site and affiliate pages | Dropshipper playbook signal (weak). Store status on Theme Store unclear. Theme_store_id not found | [secondary] https://debutify.com/dropshipping ; [unverified] theme_store_id and store status |
| Debutify | Installed by upload of a .zip under Online Store > Themes (one guide) | Third-party guide | Custom theme upload means `theme_store_id` is likely null | [secondary] https://www.debutify.com/blog/top-shopify-themes-for-dropshipping ; [unverified] |
| Booster | Dropshipping roundups list it; vendor claims 60+ presets and 3.9/5 on Theme Store. Price varies by source ($197 to $398) | Vendor pages (boostertheme.com), Shopify community | Dropshipper playbook signal (weak). Vendor-run claims | [secondary] https://boostertheme.com/shrine-vs-booster-theme ; https://community.shopify.com/t/booster-theme/320303 ; price conflict noted |
| Shrine | Minimalist, product-focused theme; prices $199/year, $299 lifetime, or $420 across sources | Third-party reviews, Booster vendor page (competitor) | Dropshipper playbook signal (weak). Thin independent coverage | [secondary] https://boostertheme.com/shrine-vs-booster-theme ; [unverified] price |
| Turbo | Speed-focused theme for large catalogues, about $425 one-time (most sources agree) | Roundups and Booster comparison | Weak signal for supply. Best-reviewed of the three | [secondary] https://boostertheme.com/booster-theme-vs-turbo ; [unverified] price |
| Vitals | Bundle of 40+ features, countdown timers, social proof and recent-sales pop-ups | Shopify app listing (search snippet), vendor blog (avada.io) | Urgency and FOMO kit. Common on dropship stores, not specific to them | [secondary] https://avada.io/blog/vitals-app-shopify/ ; [unverified] storefront trace |
| Hurrify | Countdown timer bar for FOMO scarcity. 4.8 stars from 7 reviews. Performance complaints reported | Shopify app listing (search snippet) | Urgency signal (weak). Script host not captured | [secondary] https://apps.shopify.com/urgency ; [unverified] storefront trace |
| Sales pop-ups (recent-sales apps such as SalesPush, Urgenzy, Sales FOMO) | Pop-up script that shows recent orders | App listings (search snippets) | Urgency kit (weak). Script host per app not captured | [secondary] https://apps.shopify.com/recently-bought-sales-popup ; [unverified] |
| Printful | Shopify app from the Shopify App Store; the connection is made by logging in with Printful credentials | Third-party guide (powercommerce.com) | Printful-connected store. Strongly indicates print-on-demand supply, not dropshipping of CJ-type goods | [secondary] https://powercommerce.com/blogs/shopify-hub/how-to-connect-printful-to-shopify-a-comprehensive-guide-for-e-commerce-success ; [unverified] storefront script host and CDN domain not found |
| Printify | Shopify app with a mockup generator; publishing syncs the product to the store | Shopify app listing (search snippet, apps.shopify.com/printify) | Printify-connected store. Print-on-demand supply | [secondary] https://apps.shopify.com/printify%20 ; [unverified] storefront script host and mockup domain not found |
| Gelato | Shopify app "Gelato: Print on Demand", free to install with trial, 4.8 rating from 759 reviews | Shopify app listing (apps.shopify.com/gelato-print-on-demand) | Gelato-connected store. Print-on-demand supply | [observed] https://apps.shopify.com/gelato-print-on-demand (rating taken from search snippet, accessed 2026-11-05); [unverified] storefront trace |
| Gooten | Network described as 50+ manufacturers in 70+ regions, or 30+ partners in 70+ locations (sources conflict) | Vendor and blog text (search snippet) | Print-on-demand network with regional production | [secondary] ; [unverified] counts |
| CustomCat | Shopify POD app for digital printing and dropshipping | App listing (search snippet) | Print-on-demand supply | [secondary] ; [unverified] storefront trace |
| SPOD | Described by Gelato's blog as fastest production with sustainability focus | Competitor blog (search snippet) | Print-on-demand supply. Claim is from a competitor, so treat as conflicted | [secondary, conflicted] https://www.gelato.com/blog/shopify-print-on-demand-apps ; [unverified] storefront trace |
| Teelaunch | Custom apparel POD with global fulfilment (vendor and ranking blogs) | Ranking blogs (search snippet) | Print-on-demand supply | [secondary] ; [unverified] storefront trace |

## Notes

1. **Storefront traces not yet observed.** Script hosts, app-embed handles and CDN domains for the POD apps (Printful, Printify, Gelato, Teelaunch, CustomCat, Gooten, SPOD) were not found in public documentation in this run. The next step is a live check of 5 to 10 public storefronts known to use each app, reading page source for `asyncLoad` script URLs and `cdn.shopify.com/extensions/...` handles. Those are [observed] only once fetched.
2. **Themes.** `Shopify.theme` and `theme_store_id` are real but need a live check. The Admin REST docs confirm that `theme_store_id` is null for non-Shopify or non-Theme-Store themes. A null on a storefront cannot be read from the public page unless the `Shopify.theme` object is exposed.
3. **Tracking apps.** Tracking pages (`/apps/parcelpanel`, Track123 pages, 17TRACK pages) show the app but not the origin. Origin comes from carrier names and tracking-number formats on the page. Yanwen has a checkable number format. The 17TRACK listing shows a "hide Chinese origin" feature, so absence of China carriers on a page is weak evidence.
4. **Conflicts.** Carrier counts differ across 17TRACK, AfterShip and Track123 pages. Cainiao support in tracking apps is disputed. Booster and Shrine prices differ by source.
5. **Not covered in this run.** CNE, SF International, China Post, ePacket, USPS, UPS and FedEx were not checked on their own pages. Next step: carrier pages and a sample of real tracking numbers from public tracking pages.

## Sources

1. https://docs.parcelpanel.com/article/44 (ParcelPanel default tracking page, vendor docs, accessed 2026-11-05)
2. https://docs.parcelpanel.com/shopify/tracking-page/order-status-page (ParcelPanel order-status widget, vendor docs)
3. https://apps.shopify.com/track123 (Track123 Shopify listing, accessed 2026-11-05)
4. https://apps.shopify.com/17track (17TRACK Shopify listing, accessed 2026-11-05)
5. https://17tracsks.it.com/ (lookalike of 17track.net, not the vendor's site; do not rely on it)
6. https://community.shopify.com/t/how-do-you-guys-are-tracking-cainiao-orders/13325 (Shopify community, user reports)
7. https://www.aftership.com/he/carriers/yunexpress (AfterShip YunExpress page, search snippet; en version returned HTTP 403)
8. https://www.trackingmore.com/yunexpress-tracking/en.html (TrackingMore YunExpress page, search snippet)
9. https://www.cwill.com/carriers/yanwen/ (Yanwen carrier page, accessed 2026-11-05; redirect from parcelpanel.com/couriers/yanwen/)
10. https://shopify.dev/docs/api/admin-rest/2024-07/resources/theme (Shopify Admin REST theme resource, accessed 2026-11-05)
11. https://craftshift.com/shopify-theme-store-id-list-2026/ (third-party theme store id list, unofficial)
12. https://shopplaza.io/blog/shopify-theme-detector.html (third-party theme detector guide, vendor blog)
13. https://bsscommerce.com/shopify/shopify-theme-detector/ (third-party theme detector guide, vendor blog)
14. https://debutify.com/dropshipping (Debutify vendor page, conflicted)
15. https://www.debutify.com/blog/top-shopify-themes-for-dropshipping (Debutify vendor blog, conflicted)
16. https://boostertheme.com/shrine-vs-booster-theme (Booster vendor comparison, conflicted: competitor claims)
17. https://boostertheme.com/booster-theme-vs-turbo (Booster vendor comparison, conflicted)
18. https://community.shopify.com/t/booster-theme/320303 (Shopify community thread on Booster)
19. https://powercommerce.com/blogs/shopify-hub/how-to-connect-printful-to-shopify-a-comprehensive-guide-for-e-commerce-success (Printful connection guide, third-party)
20. https://apps.shopify.com/printify%20 (Printify Shopify listing, search snippet)
21. https://apps.shopify.com/gelato-print-on-demand (Gelato Shopify listing, accessed 2026-11-05 via search)
22. https://www.gelato.com/blog/shopify-print-on-demand-apps (Gelato blog, competitor-authored, conflicted on SPOD)
23. https://avada.io/blog/vitals-app-shopify/ (Vitals overview, vendor blog)
24. https://apps.shopify.com/urgency (urgency app listings, search snippet, Hurrify)
25. https://apps.shopify.com/recently-bought-sales-popup (sales pop-up listings, search snippet)
