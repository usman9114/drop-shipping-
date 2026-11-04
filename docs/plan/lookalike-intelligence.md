# Look-alike intelligence: reverse-engineer stores that already succeed

> 2026-11-04. Owner's direction, prompted by a friend's use of myip.ms: study successful stores closely, rebuild the story of how they did it end to end (product, supply, price, launch, traffic), and copy the method, not the content. Method follows the **source evaluation standard** in `CLAUDE.md`.

## 1. The idea in one paragraph

Successful stores leave traces in systems built for other purposes. Shopify stores share a few IP addresses, so a reverse-IP directory (myip.ms) lists thousands of stores on them. Every HTTPS site gets a certificate, so certificate-transparency logs list new store domains as they launch. Web archives date a store's launch and show how its catalogue and prices changed. Ad libraries show who is paying for traffic and with what creative. Page source shows which dropshipping apps a store runs and where its product images are hosted (a CJ or AliExpress image host is a sourcing fingerprint). Joined together, these traces tell the story of a store that works.

## 2. Evidence we need, the traces, and candidate sources

| Evidence | Trace it leaves | Candidate sources (to pilot) |
|---|---|---|
| Which stores sell our candidate products (fashion jewelry, press-on nails, cleaning tools: the CJ US supply screen) | Domain on a shared e-commerce host; product pages; search results | myip.ms reverse IP on Shopify's addresses; certificate logs (crt.sh); licensed search APIs |
| Are they dropshipping, and from whom | Dropship app scripts in page source (DSers, CJ, Zendrop); product images on AliExpress or CJ hosts; shipping-time wording | One page fetch per store, read-only |
| When they started and how they evolved | First archive capture; domain age; catalogue and price changes over time | Wayback Machine CDX API; RDAP domain records |
| How they get traffic | Active ads and creatives; social links; reviews | Meta Ad Library, Google Ads Transparency Center, TikTok Creative Center (probably manual); site links |
| Roughly how big they are | Traffic rank; review counts; ad volume | Tranco list (research top-sites list); review widgets; ad counts |
| eBay look-alikes (our main channel) | Seller stores, sold counts | **Manual Terapeak only.** eBay's terms bar scraping, and its API terms bar storing data. |

## 3. Pilot protocol (small sample, measured)

For each source: check its terms first (automated access allowed, rate limits, storage), then run **at most about 10 requests**, and record:

| Metric | Meaning |
|---|---|
| Relevant leads | stores that actually sell a candidate product |
| Freshness | how recent the data is (dates shown) |
| Unique discoveries | leads no other piloted source found |
| Cost and effort | money, requests, minutes, manual steps |
| Terms | allowed / unclear / prohibited for automated use |
| Story value | which part of the end-to-end story it fills |

Recommend a source only on these results.

## 4. The store dossier (what "crack the code" produces)

One page per store, every line labelled `[data]`, `[inferred]` or `[gap]`:
1. **What it sells:** catalogue size, hero products, price band; which items match CJ US stock and at what CJ cost (margin they likely make).
2. **Supply:** dropship-app and image-host fingerprints, shipping-time promises.
3. **Timeline:** domain age, first archive capture, catalogue and price changes.
4. **Traffic:** ads seen (platform, creative type, how long running), social accounts, reviews, rank band.
5. **Story:** a short narrative of how the store likely works, with the gaps named.

## 5. Rules that still apply

- **Terms gate.** Respect robots.txt and each site's terms. No logins, no bypassing limits, no bulk scraping. A source whose terms forbid automation is used by hand or not at all.
- **No personal data.** Store domains and public business facts only. No owner names, emails or addresses from WHOIS, even if visible.
- **Public repo.** Lead lists and dossiers live in `data/private/` (gitignored). Only source scorecards and anonymised patterns ("4 of 10 stores ran Meta video ads") are committed.
- **Copy the method, not the content.** We learn which products, prices and channels work. We never copy their images, text or branding.

## 6. Pilot 1 (started 2026-11-04)

Four sources in parallel, each by a `market-researcher` agent on a small sample, focused on fashion jewelry and press-on nails sold to US buyers:
- **A:** myip.ms reverse IP on Shopify addresses.
- **B:** certificate transparency (crt.sh), with the Wayback CDX and RDAP for dating.
- **C:** ad libraries (Meta, Google, TikTok).
- **D:** store fingerprinting of about 10 stores found via search.

Results go to `docs/research/20-lookalike-source-pilot.md` as a scorecard.
