# UI v0: store card, side panel and lead inbox card (design only)

> 2026-11-05. Scope from `docs/plan/ui-ux-brief.md`, "small first" step: the **store card and side panel** and the **lead inbox card**, shown to the owner before the other three views (niche board, supply view, autopilot health), the full data contract and the stack decision note.
>
> Prototype: private claude.ai artifact "Store Scout prototype" (https://claude.ai/artifact/7kEP8ziWtk3QPo3sRqZWTC; owner-only until shared). Two clickable screens. **All store names and numbers in it are invented**; no real store, domain or list is in the prototype or in this file.

## Information architecture (all five views, first cut)

```
Niche board ──▶ Stores (cards) ──▶ Side panel "Success key": Story · Evidence · Score · Raw numbers
     │                 │                         └─▶ Verify (public page + date seen)
     │                 └─▶ Supply view (source mix, CJ match)
     └─▶ Lead inbox (parked) ──▶ Lead detail: Problem · Why it scores · Draft · Approve / Watch / Skip
Autopilot health (separate tab: runs, failures, budgets)
```

Progressive disclosure, as the brief asks: **card** (answer in one glance) → **panel** (story and evidence, one click) → **Raw numbers** tab (every field with label and source column, two clicks).

## Flow 1: study a store

1. Owner opens Stores (filter: All, Established, Risers = `mart_candidate_pool.slice`).
2. Each card shows: grade (A to D), three numbers with labels (traffic rank `PROXY`, median price `DATA`, products added in 90 days `DATA`), a rank sparkline over the 26 lists, a one-line supply guess with confidence (`PROXY`).
3. "Why this store?" opens the side panel:
   - **Story**: the `scout.store_intel` paragraph, four questions (what it sells, traffic, source, growth) each with a label, and the standing gaps box (revenue, ad spend, channel split, margin).
   - **Evidence**: one row per claim, with where it was seen, the date, the label and a Verify link.
   - **Score**: best score and its four parts (percentile × weight), plus "what would change the order" (principle 4).
   - **Raw numbers**: field, value, label, source column.
4. Card ends in a decision: Shortlist, Watch or Skip (toggle). Decisions are the only thing the UI writes.

## Flow 2: review a lead (parked idea, design only)

1. Inbox list: one row per lead, ordered by potential, showing the top problem and status.
2. Detail: **Problem we can show** (each issue: what we observed, confidence, VERIFIED/UNVERIFIED, seen date, Verify link, and a "Do not claim" line taken from the guardrails in `opportunity-store-rescue.md`); **Why it scores** (effort, fit, underperformance, fixability with their inputs); **Draft message** built from verified flags only, editable.
3. Actions: Approve draft (a person copies and sends it; the tool never sends), Watch (recheck in 30 days), Skip.

## Design rules applied

- Label chips on every number: DATA (blue), PROXY (orange), UNKNOWN (grey, dashed). Colours differ in lightness as well as hue.
- No proxy shown as sales: the card says "traffic rank", never "visits" or "revenue".
- Every claim has a date seen and a Verify link (hidden in the shared prototype because names are anonymised).
- Store-level fields that would be private for a client audience (domain, verify links) are isolated in the panel header and evidence rows, so an "agency view" can hide them in one place (brief: "who uses it", item 2).

## Data contract: store card and side panel

Label: what the UI shows next to the value. Status: **have** (column exists today), **derive** (computable from existing columns, no new fetch), **gap** (needs new collection or is not public).

| UI field | Source (dataset or mart . column) | Label | Status |
|---|---|---|---|
| Store name | `mart_store_profile.domain` | | have (private; anonymised in prototype) |
| Category | `mart_store_universe.top_category`, `top_category_share` | DATA | have |
| Business model and why | `web_store_deep.business_model`, `business_model_why` | PROXY (a classifier) | have; accuracy per doc 35 must be shown in a tooltip |
| Slice | `mart_candidate_pool.slice` (established / riser) | | have |
| Grade A to D | `mart_candidate_pool.own_grade`, signals `s_traffic`, `s_rising`, `s_steady`, `s_active`, `s_marketing` | PROXY | have |
| Traffic rank | `mart_store_profile.tranco_rank` (or `mart_store_rank_trend.rank_now`) | PROXY | have |
| Rank sparkline | `stg_web_ranks` (`domain`, `list_date`, `tranco_rank`), 26 dates | PROXY | have (absence = rank above 1M: draw as a gap, not zero) |
| Trend sentence | `mart_store_rank_trend.growth_old_to_recent`, `breakout`, `emerged`, `fading`, `dates_present` | PROXY | derive (text rule) |
| Median entry price, p25 to p75 | `web_store_deep.price_median`, `price_p25`, `price_p75` | DATA | have |
| Discount share | `web_store_deep.discount_share` | DATA | have |
| Products added 30/90/365 days | `web_store_deep.added_30d`, `added_90d`, `added_365d` (newest 250 sampled) | DATA | have |
| Catalogue size | `mart_store_profile.published_products` | DATA | have |
| Existed by | `mart_store_profile.existed_by` | PROXY ("existed by", never "founded") | have |
| Ad pixels, retention, partners, conversion apps | `mart_store_profile.paid_ads`, `retention`, `partners`, `conversion` | DATA (code seen) | have |
| DNS verifications | `web_store_deep.dns_signals` | DATA | have |
| Supply guess, warehouse, confidence, evidence | `web_fingerprints` row `estimate.source_guess`, `warehouse_guess`, `confidence`, `evidence`, `mixed_sources` | PROXY | have for 105 stores only; **gap** for the other 11,310 screened stores until fingerprints run at scale (session-state "Next" 3) |
| Theme and app embeds | `web_fingerprints` `theme_name`, `app_embed_handles`, `asyncload_hosts` | DATA | have (105 stores) |
| Review app and count | `web_reviews.review_app`, `review_count`; or `mart_store_profile.sample_review_count` | DATA | have (pilot: 15 of 30 found) |
| Story paragraph | `scout.store_intel` output (`data/private/llm_store_story_cache.csv`, `PROMPT_VERSION`) | mixed; gaps listed | have (cached file, not a table) — **gap**: store as a dataset with `pack_hash` so the UI can show which evidence version it describes |
| Standing gaps | `scout.store_intel.STANDING_GAPS` + `gaps()` | UNKNOWN | have |
| Best score and parts | `mart_store_profile.best_score`, `pct_traffic`, `pct_growth`, `pct_rhythm`, `pct_stack`; weights 0.45 / 0.20 / 0.20 / 0.15 in the SQL | PROXY | have — **gap**: weights live in SQL text; expose them as a small table or config so the UI reads, not copies, them |
| Date seen | `runs.fetched_at` for the run that produced each row | | derive (join run_id) |
| Verify link | homepage, `/products.json`, `/meta.json` of the domain; Tranco list id | | derive — **gap**: product-page URL for reviews is saved only as `web_reviews.url_path` |
| Owner decision (shortlist / watch / skip) | none | | **gap**: new table `ui_decisions(domain, decision, note, decided_at)`; the only thing the UI writes |
| Revenue, orders, ad spend, margin | none public | UNKNOWN | gap by nature (calibration idea: Empire Flippers listings, `tool-shortlist.md`) |

## Data contract: lead inbox card

Almost all of it is a **gap** today: the flags are designed (`opportunity-store-rescue.md`, "What the autopilot keeps now") but not collected.

| UI field | Source | Label | Status |
|---|---|---|---|
| Effort inputs | `mart_store_profile.paid_ads`, `retention`, `added_90d`; app count from `web_fingerprints` | PROXY | have (partly; effort apps such as Gorgias, Recharge not yet signatures, session-state "Next" 2) |
| Fit | `mart_niche_copyable` + candidate-pool grades in the same `top_category` | PROXY | derive |
| Underperformance | `mart_store_rank_trend.fading`, `growth_old_to_recent`, `rank_recent_median`; reviews vs catalogue age | PROXY | derive |
| Fixability and issues | flags `ua_only`, `aw_without_conversion`, `meta_pixel_duplicate`, `product_jsonld_missing`, `noindex_products`, `soldout_share`, `days_since_last_product` | DATA (what we saw) | **gap**: not collected; `soldout_share` and `days_since_last_product` derive from the feed we already fetch (`available_variant_share`, `newest_created`) |
| Issue confidence | per-flag constant from the rescue doc table (high / medium) | | derive (one table of flag definitions) |
| Verified / unverified | hand check of a flag on that store | | **gap**: needs `lead_checks(domain, flag, checked_by, checked_at, result)` |
| "Do not claim" line | per-flag text, from the rescue doc guardrails | | derive (same flag table) |
| Potential score | effort × fit × underperformance × fixability, draft weights 0.30 / 0.25 / 0.20 / 0.25 | PROXY | **gap**: not built; weights must sit in one config |
| Draft message | template per flag, optionally polished by GLM via `scout.llm` | | **gap**; compliance review before any send |
| Status (approved / watch / skip) | none | | **gap**: `ui_decisions` as above |
| Contact channel | the store's published business channel | | gap; out of scope until the outreach phase is approved |

## Open owner questions from this step

1. Do the card's three headline numbers (traffic rank, median price, added in 90 days) answer your first question about a store, or should supply source be a headline number too?
2. Is "Shortlist / Watch / Skip" the right set of decisions, and should a skip require a reason?
3. Lead inbox: should an UNVERIFIED issue appear in the draft at all? The prototype keeps it on the card but out of the draft.

## Next (after owner feedback)

Niche board, supply view and autopilot health screens; the full data contract across all five views; the stack decision note in `docs/decisions/`.
