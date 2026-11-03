# 06 — Image sourcing under zero inventory

> Researched 2026-11-03 by a web-search agent. Several quotes were fetched through a summarizing model and are close paraphrases, so check them against the live pages. Not legal advice.

We never hold stock, so we can't photograph products ourselves. Every listing image must come from a source that gives us the right to use it.

## 1. Which suppliers license their images to us

| Supplier | Licenses images for resale listings? | Paid photo service? | Notes |
|---|---|---|---|
| **Spocket** | ✅ **Explicit in ToS:** "Suppliers give Spocket and Spocket retailers the right to use such images for sales and marketing purposes." | not checked | Images must accurately reflect the product. No eBay-specific language. Editing isn't explicitly addressed. |
| **Zendrop** | ✅ **Help center** (not ToS): images may be used and **edited** for listings and marketing | No (suggests samples or freelancers) | Same article: Zendrop "cannot guarantee the copyright ownership of all product images". |
| **CJ Dropshipping** | ❌ **No licensing clause found** in ToS. ToS bans reselling "any portion of the Service". | ✅ **Paid Photography/Video Service**, ~2 working days (blog snippet); price unconfirmed | Best API (03), but image rights need the paid service or written permission. |
| Wholesale2B | ❓ Datafeed includes image URLs; terms not found | — | — |
| Doba | ❓ | — | — |
| Syncee | ❓ (built-in background remover for retailers) | — | — |
| Inventory Source | ❓ ToS defers to each supplier's own terms | — | — |
| AliExpress | ❓ Official IP page returned 404 | — | Retail marketplace anyway (01) |

**Takeaway:** the supplier with the best API (CJ) and the suppliers with clear image licenses (Spocket, Zendrop) are different companies. Options for the PoC:

- **A. CJ for automation plus CJ's paid photo service** for the shortlisted SKUs only. The rights are clean if CJ's service terms assign or license the photos to us. Confirm before paying.
- **B. Spocket or Zendrop for licensed images**, with order automation through their app integrations. Their public APIs are unconfirmed (03).
- **C. Written image permission** from a specific CJ/Wholesale2B supplier, saved as evidence.
- **D. eBay catalog (ePID) stock photos**, where a catalog product has one. This is limited to catalog-matched items.

## 2. What eBay's picture policy allows (fetched)

**Prohibited:**

- photos that don't accurately represent the item
- **added borders**
- **added text, artwork or marketing material**
- **watermarks of any type**

So **infographic overlays, badges and text callouts are NOT allowed on eBay images.** Put that content in the description or item specifics instead.

**Allowed in practice:**

- background cleanup (white or neutral background)
- lighting and color correction that stays faithful to the product
- upscaling and cropping
- lifestyle scenes, provided they don't misrepresent the item: no added accessories, no wrong scale, no wrong color

eBay has no official statement on AI-edited or AI-generated images. Vendor blogs disagree, so the safe rule is that **the product pixels stay real and AI only changes the surroundings**.

**Stock photos:** banned only for used, damaged or defective items. For new items, forum posts say manufacturer-permitted stock photos are fine **[unverified]**.

## 3. eBay catalog (ePID) images

- In the Trading API, a catalog product's stock photo is included by default (`IncludeStockPhotoURL` = true). It can serve as the gallery image (`UseStockPhotoURLAsGallery`).
- Only some catalog products have stock photos. Whether we can add our own images alongside it is **[unverified]**.

## 4. Checking quality and delivery without stock

- **Test order:** buy one unit through the normal dropship flow, shipped to our own address. This measures real delivery time and packaging and confirms the product matches the images. Samples cost about $3–10 each **[unverified]**.
- CJ's pre-shipment inspection applies to goods sent to CJ's warehouse, not to a unit shipped to us.
- **Checklist per SKU:** specs match, defects, packaging (no retailer branding), real tracking, delivery days.

## Pipeline rules derived from this

1. Store, per image, the **source and license evidence**: supplier, ToS clause or permission email, date.
2. Allowed AI operations:
   - background removal or replacement
   - relighting and color correction
   - upscaling
   - lifestyle compositing **around** the unaltered product
3. **Forbidden:**
   - text, badges or borders on images
   - watermarks
   - changing the product itself
   - adding accessories that aren't included
4. Feature claims go into the description and item specifics, sourced from supplier specs only.

## Sources
- Spocket ToS: https://www.spocket.co/terms-of-service
- Zendrop image use: https://support.zendrop.com/en/articles/11101560-can-i-use-zendrop-product-images-for-marketing-and-social-media-campaigns
- Zendrop branded products: https://support.zendrop.com/en/articles/10139175-how-to-handle-branded-copyrighted-and-trademarked-products-on-zendrop
- CJ ToS: https://cjdropshipping.com/termsofservice
- CJ video service: https://blog.cjdropshipping.cn/detail/how-to-use-video-shooting-service-from-cj-dropshipping
- Syncee supplier conditions: https://help.syncee.com/en/articles/9503831-conditions-for-listed-suppliers
- Inventory Source ToS archive: https://tostracker.app/document/inventorysource
- eBay picture policy: https://www.ebay.com/help/policies/listing-policies/picture-policy?id=4370
- eBay images/text policy: https://www.ebay.com/help/policies/listing-policies/images-text-policy?id=4240
- eBay catalog products (Trading API): https://developer.ebay.com/api-docs/user-guides/static/trading-user-guide/catalog-products.html
- eBay Inventory API matching products: https://developer.ebay.com/api-docs/sell/static/inventory/matching-products.html
- AI photo policy (vendor blogs): https://nightjar.so/help-desk/does-ebay-allow-ai-generated-product-photos-in-listings ; https://www.rewarx.com/blogs/ai-product-photography-platform-policies
