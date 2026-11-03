# AI team operating plan

> Owner: repo owner. Mode: **opusplan**: Opus plans and decides, Sonnet executes, Haiku searches, free OpenRouter models do bulk work. Market: **US**. Supplier: **CJ Dropshipping (US warehouses)**. **Zero inventory.**

## 1. Org chart

```
                      Owner (human): approves money, accounts, go-live
                                    │
                    Orchestrator: main Claude session (opusplan)
                                    │
                 ┌──────────────────┴──────────────────┐
     head-of-marketing (Opus)                  sales-lead (Sonnet)
     niche, positioning, listing               unit economics, pricing,
     standards, final calls                    eBay ops, KPIs
                 │                                     │
   ┌─────────────┼───────────────┬─────────────────────┤
market-researcher   data-analyst      compliance-officer    creative-producer
(Haiku) web          (Sonnet) Trends,  (Sonnet) policy/IP/   (Sonnet) CJ images +
search, 1 topic      eBay API, CJ API, safety veto           AI enhancement, copy
per agent            free-LLM bulk
                                    │
                 free OpenRouter models (NVIDIA Nemotron, Gemma):
                 bulk classification, tagging, image QA, drafts
```

Agent definitions live in `.claude/agents/*.md`. Shared rules are in `.claude/agents/_team-rules.md`.

## 2. Operating rules

1. **Evidence ledger.** Every decision cites [data], [primary], [secondary] or [estimate] sources. Raw pulls go in `data/evidence/`, research in `docs/research/`, decisions in `docs/decisions/NNNN-*.md`.
2. **Decision gates.**

   | Who | Decides |
   |---|---|
   | head-of-marketing | niche and product shortlist |
   | sales-lead | pricing and margin pass/fail |
   | compliance-officer | veto power |
   | **Owner** | anything that spends money, opens accounts, or goes live |

3. **Model routing (cost discipline).** Free OpenRouter → Haiku → Sonnet → Opus. Use the cheapest tier that can do the job (§4).
4. **No fabrication.** A missing key or missing data stops that branch and is reported. Mock data is labeled `MOCK`.
5. **Hard rules** in `CLAUDE.md` always apply: zero inventory, CJ images only, no AI attribution in git, no scraping that breaches terms.

## 3. Pipeline

| Stage | Owner | Output | Status |
|---|---|---|---|
| A. Evidence wave | market-researcher ×4 | `docs/research/07–10` | ✅ 2026-11-03 |
| B. Candidate niches + keywords | head-of-marketing | `docs/decisions/0001-niche-candidates.md`, `data/evidence/trends/candidates.txt` | ✅ |
| C. Quantitative check | data-analyst | Google Trends table now; eBay Browse + CJ catalog once keys exist | ✅ |
| C'. Risk cards | compliance-officer | per-niche risk cards | ✅ |
| C''. Economics | sales-lead | max landed cost per price point, per niche | ✅ |
| D. Niche decision | head-of-marketing | `docs/decisions/0002-niche-selection.md`: **tcg-supplies** (backups: vinyl-record-care, hobby-modeling-tools) | ✅ 2026-11-03 |
| E. Product shortlist (20–40 SKUs) | data-analyst + sales-lead + compliance | needs CJ and eBay keys | blocked on keys |
| F. Listings | creative-producer | needs CJ images + approval | later |

## 4. Model routing and free models

| Task | Tier | Model |
|---|---|---|
| Bulk classify/tag CJ catalog, extract specs | Free | `nvidia/nemotron-3.5-lightning:free` → `google/gemma-4-26b-a4b-it:free` |
| Image QA (product unaltered? text or watermark?), image → attributes | Free | `nvidia/nemotron-3.5-super-vl:free` → `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` |
| Title and description first drafts | Free | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| Web search | Haiku | `market-researcher` |
| Data pulls, scripts, analysis, risk cards, economics | Sonnet | data-analyst, compliance-officer, sales-lead |
| Synthesis, niche and product decisions | Opus | head-of-marketing |

- Client: `python -m scout.llm --task {bulk,reasoning,vision,safety}`. It tries free models in order and falls back on 429s.
- **Limits:** 20 requests/min. 50/day until the OpenRouter account has bought **$10** of credits in total, then 1,000/day.
- **Free routes aren't private.** Never send keys, customer data or contracts.
- **None of the free models generate images.** Background removal and upscaling run locally (BiRefNet MIT, Real-ESRGAN BSD). Lifestyle scenes need a paid model, with owner approval.

## 5. Niche scoring rubric (0–5 per criterion, weighted)

| # | Criterion | Weight | Evidence source |
|---|---|---|---|
| 1 | Demand level and trend (US) | 20% | Google Trends growth and level [data]; eBay category evidence (08) |
| 2 | eBay fit: buyers prefer eBay over Amazon/Temu here | 15% | 08 (collectibles, parts, hobby), Browse API competition (later) |
| 3 | Margin headroom: typical price ≥ ~3× CJ landed cost | 20% | `scout.margin`; CJ prices (later) |
| 4 | Regulatory and IP risk (inverted: 5 = safest) | 20% | 10 risk table, compliance-officer card |
| 5 | Temu/Amazon price competition (inverted) | 10% | 10 |
| 6 | Operational fit: small and light, few variants, low breakage, CJ US-warehouse depth | 10% | 09, CJ API (later) |
| 7 | Listing-quality upside: better images and specs actually sway buyers | 5% | judgement + competitor listing review |

- **Hard filters** (fail = out): compliance veto; average price below $15 (fees eat the margin); oversize or hazmat.
- **Final pick:** one primary niche and two backups. Each must name **20+ concrete product types** that CJ plausibly stocks in the US.

## 6. What's blocked on the owner

| Need | Why | Where to put it |
|---|---|---|
| `OPENROUTER_API_KEY` | free-model bulk work | Environment settings (see the chat reply) |
| `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET` | Browse API competition and price data | same |
| `CJ_API_KEY` (and `CJ_EMAIL` if required) | US-warehouse catalog, stock, cost | same |
| Optional: $10 OpenRouter credit purchase | raises the free cap from 50 to 1,000 requests/day | owner decision |
| Optional: Terapeak exports | sold-data proxy (sell-through) | manual export from Seller Hub |
