# 0013 — Automating ad and review checks: official routes only

> 2026-11-04. Owner request: automate Meta Ad Library, TikTok Creative Center and Trustpilot, "using a third party plugin or better if we do it directly". Research: docs 32a (Meta), 32b (TikTok), 32c (Trustpilot, Google). Status: **proposed; each route needs an owner step.**

## Rule applied

All three websites forbid scraping or automated collection. A third-party scraper, browser plugin or "scraper API" breaks the same terms on our behalf and risks the owner's accounts, so it is **not used** (CLAUDE.md principle 6). Only official APIs and licensed data.

## What the official routes give

| Source | Official route | Covers | Fields | Access | Cost |
|---|---|---|---|---|---|
| **Meta** | Ad Library API (`ads_archive`) | all ads shown in the **EU**, plus political ads anywhere; **US-only commercial ads: none** | ad text, snapshot link, platforms, languages, EU reach by country/age/gender; no spend for commercial ads | identity check at facebook.com/ID, developer app, token | free [vendor-reported] |
| **TikTok** | Commercial Content API | ads shown in **Europe** (EU, UK, Norway, Switzerland, a few others); no US | first and last shown dates, targeting, reach, advertiser | developer account plus application; approval for a commercial user uncertain | not stated |
| **Google** | BigQuery public dataset `google_ads_transparency_center` | **all advertisers** in the EEA and Turkey, since 2023-03-01; no US | advertiser, creative id, format, region, first and last shown dates, impression ranges | Google account plus a Cloud project; free sandbox, no card | free within the free tier [limit unverified] |
| **Trustpilot** | Data Solutions API (Display or Insights tier) | any company's TrustScore and review count | rating, review total; reviews on higher tiers | contract only, via sales | quote [unpublished] |

## Decision

1. **Automate what the official routes cover:** EU/EEA ads for brands that also sell in Europe (Meta, Google, and TikTok if approved). This shows **creative themes, formats and how long ads run**, which is the method we want to learn, though not the US ad mix.
2. **US ads stay manual:** the owner's 30-minute check per batch on the Ad Library and Creative Center websites.
3. **Trustpilot stays out** until a contract or written permission exists. Our own review signal (counts shown on each store's product pages) continues.
4. Every route's terms are read and recorded before the first stored row (terms gate); results stay in `data/private/` and the vault.

## Owner steps (in order of value per effort)

1. **Google (about 15 minutes, free):** create a Google Cloud project (BigQuery sandbox), then give this environment access (a service-account key added as a secret on the environment). I then run a 20-brand pilot and record the hit rate.
2. **Meta (about 1 to 3 days for the identity check, free):** confirm identity at facebook.com/ID, create a developer app, generate a token, add it as a secret. Pilot on 5 brands by page id.
3. **TikTok (optional):** apply for the Commercial Content API; approval is uncertain for a business.
4. **Trustpilot (optional, paid):** request a Display API quote and ask in writing whether private storage of ratings for about 300 domains is allowed.
