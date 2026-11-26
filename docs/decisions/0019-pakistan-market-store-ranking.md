# 0019 Pakistan: rank the best Shopify stores selling in rupees

> 2026-11-22. Owner request: "start this search in Pakistan, rank the top stores and go on." Changes the R1 scope, which said US only (`docs/plan/phase-niche-finder-r1.md`, "Out of scope: non-US markets").

## Decision

1. **Market rule:** a Pakistan store is a Shopify store whose `/meta.json` currency is **PKR** (`scout.stores.pk_store`). Currency, not registered country: 31 PKR stores are registered in the US, 25 in GB and 10 in AE, and they still sell to Pakistani buyers. 2 PK-registered stores price in USD and are left out (they sell abroad).
2. **Discovery reuses the existing scan.** The Tranco top-1M scan (decision 0009) already found every Shopify store and read its `/meta.json`; no new crawl is needed to find Pakistan's stores. Source terms are unchanged: each store's own public machine files, robots.txt respected.
3. **Profiler gets a market switch:** `python -m scout.stores light|deep --market pk` (default stays `us`).
4. **Ranking:** `python -m scout.market_rank --market pk`. Inputs, weights and what changes the order are in the module docstring; the weights live only in `market_rank.WEIGHTS` (traffic 0.55, growth 0.25, rhythm 0.20). The US marketing-stack weight is dropped because only a homepage fetch shows the stack.
5. **Business model is shown, not scored.** The 20-store sample showed the rules (tuned on US stores) mislabel well-known Pakistani brands (a shoe brand as "reseller / baby_kids", an apparel brand as "general"). It needs a hand-checked Pakistan sample and a second opinion (principle 5) before any "copyable" filter is used here.

## First run (2026-11-22)

- 911 PKR Shopify stores in the Tranco top 1M (841 registered in PK). 728 have Tranco rank history (90 and 365 days back).
- Sample of 20 at 6 workers: 20/20 answered. Full run at 6 workers: Shopify answered HTTP 429 to 861 requests after about 50 stores. Shopify throttles by our declared user agent across all its stores, so parallel workers do not help. We keep the honest user agent (no browser disguise; principle 6) and run at 1 worker, 4 s apart, in rounds of 100 with a 10-minute back-off when throttled.
- Fix: an HTTP 429 no longer counts toward `MAX_FAILS` (`stores.gave_up`); a throttled store is ours, not the store's, failure. Test in `tests/test_market_rank.py`.

## Business-model validation for Pakistan (2026-11-22, principle 5)

Truth set: the 44 best-ranked profiled PKR stores, hand-labelled from feed evidence plus public knowledge of the brands (`data/private/research/pk-business-model-truth.csv`, private; 4 left "unclear"). Checker: `python scripts/check_truth.py <truth.csv>`.

| Step | Rules vs hand (40) | What changed |
|---|---|---|
| US rules as they were | 25/40 = 62% | — |
| + line-word vendors, resold-brand titles, no "general" pattern for pk | 31/40 = 78% | `LINE_VENDOR`, `KNOWN_BRANDS`, `GENERAL_UNVALIDATED` |
| + collection-name vendors for pk ("Lux Pret Vol-2 Winter 2026") | **36/40 = 90%** (high-confidence 31/32) | `LINE_WORDS_PK`, used only when market = pk |

Error groups found, each now a test in `tests/test_market_rank.py`: (1) vendors hold product lines and collections, so a brand looked like a 30-brand retailer (J., Nishat, Bonanza, Asim Jofa, Stylo, Outfitters, Bata, Saeed Ghani); (2) brands on permanent sale across apparel, home and kids matched the "general store" pattern (Beechtree, Gul Ahmed); (3) department stores enter their own name as vendor on resold goods (Mi Store fixed via brand names in titles).

**Known errors left (4):** Al-Fatah and Chase Value (own name on resold local brands the lexicon does not know), Baby Planet (dominant vendor is a third-party brand), Dawood Designers (low-confidence truth). Not fixed: each fix would fit one store.

**Second opinion:** free models (GLM 4.5 Flash 37 calls, Nemotron free 7), from the same evidence only: 34/40 = 85% vs hand, 30/40 vs rules. The model is right on all 4 rule errors; the rules are right on all 6 model errors (mostly footwear brands the model called retailers). Disagreement between rule and model is a cheap review flag.

**Caveat:** the 90% is in-sample (the rules were tuned on these 40). A held-out hand check of 20 further PKR stores is due before the copyable filter is used. Evidence now saved per store: every vendor with its count (`vendor_names`, capped at 100), so `stores relabel` re-scores vendor rules without refetching.

## What we know and don't

- Tranco rank is a traffic-popularity `[proxy]`, not sales. Revenue, orders, ad spend and margin are `[unknown]` for every store.
- Pakistani shoppers often buy through Daraz, Instagram and WhatsApp, and many stores run on WooCommerce. A Shopify-only, Tranco-top-1M list misses these. It is a list of the biggest Shopify storefronts, not of the whole market.
- A Pakistani brand's success is demand evidence for Pakistan, not for eBay US (principle 3).

## Open for the owner

- What the Pakistan list is for: (a) selling inside Pakistan (Daraz / own store, local suppliers, cash on delivery), or (b) learning which categories win and taking them to eBay US. The phase plan, supplier (CJ does not fit (a)) and exit criteria differ.
