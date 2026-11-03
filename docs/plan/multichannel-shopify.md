# Multichannel plan: one pipeline, eBay + Shopify/Instagram

> Drafted 2026-11-03 by the orchestrator. Status: **proposal, waiting on owner decisions (§6)**. The eBay PoC stays the priority. Shopify is channel 2.

## 1. Why the channels differ

| | eBay | Shopify + Instagram |
|---|---|---|
| Traffic | Built in; buyers already search | **We bring it**: her Instagram, micro-influencers, later ads |
| Main cost | 13.6% final value fee + ads | Plan ~$39/mo + payments ~2.9%+30¢ + **customer acquisition cost** (influencer fees, gifted product, ads) [verify] |
| What wins | Search match, price, item specifics, trust | Content: demonstrable, visual, story-driven products; brand; repeat buyers |
| Images | CJ images, surroundings only; **no text on images** | Text overlays, UGC, reels and lifestyle content are all allowed. Still no fabricated product claims. |
| Product fit | Collectors and hobbyists searching for parts or supplies | Impulse or gift items, $25–60, that look great on camera |

So the **pipeline core is shared** and each **channel gets its own adapter and scoring weights**.

## 2. Shared pipeline (generic `scout` core + channel adapters)

```
sources         research            scoring              content               publish            measure
CJ API ──┐     Trends, eBay       channel-specific      images (CJ-only),     eBay Sell API      sales, CAC,
private- ├──▶  Browse, TikTok/ ─▶ weights + margin ─▶  copy, captions,  ─▶   Shopify Admin  ─▶  margin, returns
label    │     IG signals         + compliance gate     reel scripts          API; IG posting   → back to scoring
supplier ┘                                                                    (she approves)
```

- **Margin model per channel.** `scout.margin` is eBay-only today; add a Shopify mode (plan fee, payment fee, CAC per order instead of FVF).
- **Compliance gate per channel.** Add the FTC Endorsement Guides (#ad on every paid or gifted post) and claim substantiation on social.

## 3. What the AI team can and can't do

| I/the team can do | She/you must do |
|---|---|
| Niche and product research, scoring, economics | Create the Shopify account (her name/business), payments, KYC |
| Store build through the **Shopify Admin API**: products, collections, pages, policies, SEO, theme edits (Liquid) | Buy the domain (~$10–20/yr) and connect it (we give exact steps) |
| Product copy, image enhancement, content calendar, reel scripts, captions (drafted with free models first) | **Approve and post** on Instagram (no auto-posting without her sign-off) |
| Influencer **shortlists, outreach message drafts, a tracking sheet**, terms templates with #ad clause | **Send** the DMs and emails, negotiate, ship gifted items |
| Weekly P&L, CAC, cash flow, sales-tax reminders (finance role) | Sales-tax registration where needed (Shopify Tax helps), bookkeeping sign-off |
| Order-flow automation once live (CJ ↔ Shopify app or API) | Customer service on her accounts (we draft replies) |

Compared with the YouTube video (doc 14), we pick the niche from data, set prices with a real margin model and measured CAC, run compliance before launch, and track every influencer post to a discount code or UTM link. Scaling only follows measured CAC, not hope.

## 4. Beauty and cosmetics: the important caveat

- **Cosmetics** (anything applied to skin or hair: serums, creams, makeup) are a **default compliance veto for CJ dropshipping**:
  - Under **MoCRA**, the "responsible person" on the label must handle safety substantiation, adverse-event reporting and facility/product listing.
  - With CJ we can't verify ingredients or labels.
  - Skin reactions mean returns, chargebacks and liability.
- **Compliant routes for her:**
  - **A. Beauty tools and accessories, not cosmetics** (lowest risk):
    - makeup brushes and organizers
    - makeup bags
    - hair accessories (claw clips, heatless curlers)
    - non-LED mirrors
    - Avoid: patented hairbrush designs (Schedule A), LED or lithium devices, and Prop 65 risk in cheap metal jewelry.
  - **B. Private-label cosmetics from a US/Canada dropship manufacturer that handles labeling and compliance** (platforms such as Blanka or Supliful **[unverified, research needed]**). Higher margin and a real brand, but it needs research and some setup.
- Either route works with her Instagram and influencers, so the content side doesn't change.

## 5. Proposed new team roles

| Role | Model | Owns |
|---|---|---|
| `social-media-manager` | Sonnet (+ free models for drafts) | content calendar, captions, reel scripts, her IG growth plan |
| `creator-outreach` | Sonnet | influencer discovery criteria, shortlist, outreach drafts, deal tracker, #ad compliance |
| `finance-controller` ("accountant") | Sonnet | P&L per channel, CAC, cash flow, subscriptions, sales-tax/1099-K reminders |

The "product hunter" role already exists as `data-analyst` + `head-of-marketing`. It could be renamed.

## 6. Owner decisions needed

1. **Beauty route:** A (tools and accessories via CJ) or B (private-label cosmetics, research first)?
2. **Her Instagram:** is it a Business/Creator account? That's needed for insights via the Meta API. Roughly what's the follower count and audience (location, age)?
3. **Sequencing:** finish the eBay niche decision first, then add the Shopify channel (recommended), or run both in parallel?
4. **Add the 3 roles** in §5?
