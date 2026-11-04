# Operating plan: from desk research to first sale, without the engineering trap

> Written 2026-11-04. Owner: repo owner (engineer, not a salesperson). Inputs: `docs/handoff/session-state.md`, decision 0002 (niche, 24 product types, kill criteria §3.8), decision 0005 (CJ client), doc 18 (CJ unknowns), `scout/llm.py` (free-model router).
>
> One question drives every week: **will a stranger pay for this product, at this price, and do we keep money after fees, returns and ads?** Build only what answers that question next.

## 0. Status today

| Item | State |
|---|---|
| Tests | 64 passing; hooks installed |
| Env vars in the cloud container | **None set**: `CJ_API_KEY`, `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `ZAI_API_KEY`, `OPENROUTER_API_KEY` are all missing. Add them in the cloud environment settings (environment menu → Edit → environment variables or network secrets) and start a **new** session; a running session does not pick them up. A local `.env` is not visible to a cloud container. |
| OpenRouter credit | €10 bought (owner, 2026-11-04) |
| CJ inactivity deadline | Key created ~2026-11-04. CJ may disable API access after 30 days without a transaction [unverified]. **First test order before ~2026-12-01.** |

## 1. Guardrails against the engineering trap

1. **Every build task names the decision it unblocks and a deadline.** If it unblocks no decision in the next two weeks, it goes to the parking lot (§6).
2. **Time split until the first sale: at most 30% code, at least 70% product, listings, orders and buyer messages.** Log hours per week in the weekly review.
3. **No new infrastructure before 20 live listings.** Postgres stays parked (decision 0004). Files, CLIs and CSVs are enough for 24 product types.
4. **Manual first, automate the third time.** Do a step by hand twice, write down the steps, then decide whether code earns its keep. eBay License 9.6 makes order forwarding and tracking manual anyway.
5. **Kill dates are binding.** The kill criteria in decision 0002 §3.8 and the phase kill criteria in `00-summary.md` are applied on the dates below, not renegotiated.
6. **"Sales" here is measurable work, not cold calls.** On eBay, selling is title, photos, price, item specifics, handling time and message response time. Those are inputs we can A/B and measure, which suits an engineer.

## 2. Model plan: GLM + OpenRouter, and what the €10 is for

**The €10 is mainly an unlock, not a budget.** OpenRouter raises the daily cap on `:free` models (about 50 requests/day → about 1,000/day) once an account has bought at least 10 credits [unverified for Nov 2026; check https://openrouter.ai/docs/api-reference/limits]. Keep the balance mostly untouched so the higher cap stays and paid calls stay a deliberate choice. Note: €10 after card fees may land slightly under or over 10 credits; check the balance page.

Routing stays in `scout/llm.py` (free first: Z.ai GLM Flash, then OpenRouter free). Proposed use per task:

| Job | Task in `scout.llm` | Models (in order) | Volume | Cost |
|---|---|---|---|---|
| Compliance pre-screen of CJ titles and descriptions: brand/game/grader names, PVC, loose magnets, LED/USB, "PSA style", children's | `bulk` | `zai:glm-4.5-flash` → OpenRouter free | ~24 types × ≤100 hits = ≤2,400 short calls, batched 20 per call → ~120 calls | $0 |
| Spec extraction from CJ text into item specifics (material, mm, count, pt) as JSON | `reasoning` | `zai:glm-4.7-flash` → nemotron ultra free | top ~100 products | $0 |
| Image screening: card art, logos, text, watermarks, brand dials in CJ photos (veto, never edit) | `vision` | `zai:glm-4.6v-flash` → nemotron VL free | top ~50 products × ~6 images | $0 |
| Title and description drafts from verified specs only | `reasoning` | `zai:glm-4.7-flash`, cross-checked by a second free model | ~20 listings | $0 |
| Code drafts and tests | `code` / `glm-coder` agent | `zai:glm-4.7-flash` | as needed | $0 |
| Background replacement and lifestyle scene (Phase 1) | not in router yet | Mask the product locally (search for a maintained tool first, e.g. `rembg`; record in `docs/decisions/`), generate **only** the background with a paid image model, composite the original product pixels back on top | ~20 listings × 3–5 images | **The only planned use of the €10**: ~$0.02–0.07/image → $2–7 total |

Rules that keep this honest:

- LLM output is a **draft or a flag**, never a fact. Specs in a listing must match the CJ spec sheet **and** the test unit.
- The compliance pre-screen only removes products. A pass still needs the `compliance-officer` review before listing.
- Raw CJ text sent to a model comes from `data/private/`; model outputs that contain CJ text stay there too. Only ids and our computed flags get committed.
- Track spend: add the OpenRouter balance to the weekly review. Stop paid calls at $5 spent and review.

## 3. Calendar

Dates assume keys are in the environment by 2026-11-06.

### Week 1 (Nov 4–10): real numbers — decides the niche

| # | Task | Who | Unblocks |
|---|---|---|---|
| 1.1 | Add the 5 env vars to the cloud environment; start a new session | owner | everything below |
| 1.2 | `scout.cj search` for the 24 types → `data/private/`; resolve doc 18 unknowns; fix `scout/cj.py` and tests; update doc 18 | Claude | 1.3 |
| 1.3 | Details + freight for hits; LLM compliance pre-screen; `scout.margin` at 8% returns and 5% **and** 7% ads; derived shortlist in `docs/shortlists/` (ids + numbers only) | Claude | 1.5 |
| 1.4 | Terapeak session (~2 h, `docs/runbooks/terapeak-session.md`) | owner | 1.5 |
| 1.5 | Apply kill criteria (0002 §3.8). < ~20 passing products → backup niche, repeat 1.2–1.3 for it | Claude + owner | Week 2 |
| 1.6 | eBay client-credentials token test; Taxonomy item aspects for the target categories only; no Browse data stored | Claude | listing specifics |

**Exit:** a shortlist of 5–10 SKUs with real landed cost, or a recorded kill.

### Week 2 (Nov 11–17): test orders — decides whether the supplier is real

- Owner places test orders for the top 3–5 SKUs to own address (~$60–120). This also resets the CJ inactivity clock.
- Ask CJ in writing: returns and return address, sealed magnets, PVC-free statements, image licence for marketplace use, API data-use terms (doc 18 unknown 8).
- Meanwhile: listing pipeline v0 for those SKUs (spec JSON → title, specifics, description draft; image screening). Text only; no image generation yet.

**Exit (Phase 1 kill criterion):** delivery time or quality doesn't match CJ's claims, or the image licence is refused → stop or switch supplier.

### Week 3–4 (Nov 18 – Dec 1): first listings

- Units arrive: check specs against drafts, photograph nothing for listings (zero-inventory rule: CJ images only).
- Image enhancement for 5–10 SKUs (the €10 use above).
- List 5–10 SKUs by hand on the eBay account. New-seller limits apply; expect payout holds.
- Write the manual order runbook (eBay order → CJ order → tracking upload by hand) and run it on the first order.

### Weeks 5–12 (Dec – Jan): 60-day live test

Track the Phase 2 metrics in `00-summary.md`. Weekly review (30 min, template below). Decision on 2027-01-31: scale, switch niche, or stop.

## 4. Weekly review (every Sunday, 30 min)

```
Week of:            Hours code / non-code:
Listings live:      Views / sales / conversion:
Revenue / net after fees, returns, ads, CJ:
OpenRouter spend to date:
Decision made this week:
Kill criterion checked:            Result:
Next week's one question:
```

## 5. The SaaS option: keep the door open, don't walk through it yet

The tools we need anyway may become a product. The cheapest way to keep that option is to build them **as if** they were going to be extracted, and to let our own store be the proof.

**Likely wedge (hypothesis, not researched):** a *compliance-aware listing builder* for marketplace sellers: supplier product → policy-checked title, item specifics and description; supplier images with only the background enhanced; banned-word, VeRO and picture-policy checks; stress-tested margin at a given return and ad rate. Order-automation tools already crowd the market [unverified], and eBay License 9.6 forbids automating supplier ordering and tracking through the eBay API, so automation of fulfilment is **not** the wedge.

**What we do now (costs nothing extra):**

- Keep modules niche-agnostic: niche rules in data files (`rules/`, the second agent's engine), not in code.
- Keep each step a CLI with JSON in and JSON out (`scout.cj`, `scout.margin`, `scout.llm` already are).
- Log, per listing, which pipeline version produced it, so later we can show "listings built this way convert at X%".

**What we do not do now:** auth, billing, multi-tenant, a web UI, a landing page.

**When to revisit (trigger):** after 60 days live, if our listings show a measurable edge (conversion or return rate) over our own manual baseline, run a one-week validation: research competitors (Haiku agents, one topic each, saved as `docs/research/NN-*.md`), talk to 10 sellers, and check the licence limits for a SaaS (eBay API terms for third-party apps; CJ data redistribution). Only then decide.

**Known constraints a SaaS would inherit:** eBay data cannot be stored or modelled without permission (decision 0004); CJ data-use terms are unconfirmed; the image rule (product pixels untouched) is a feature to sell, not a limitation.

## 6. Parking lot (not before 20 live listings)

Postgres warehouse and dlt sources; Shopify / Instagram channel (`multichannel-shopify.md`); licensed Trends provider (SerpApi, DataForSEO); dashboards; scheduled pulls; a second supplier; SaaS build.

## 7. Owner actions, in order

1. Add the 5 env vars to the cloud environment; start a new session. Rotate the Z.ai and OpenRouter keys first if not done (they were pasted into an earlier chat).
2. Terapeak session this week.
3. Approve test-order budget (~$60–120) once the shortlist lands.
4. Send the CJ questions (§3 Week 2).
5. Decide: public vs private repo (this plan and future shortlists will hold product ids and margins).
