# 11 - Google Trends check of Stage B candidates (US)

Date: 2026-11-03. Stage C (quantitative check) of `docs/plan/ai-team.md`. Source keywords: `data/evidence/trends/candidates.txt` (48 generic keywords, 8 niches x 6; decision `docs/decisions/0001-niche-candidates.md`).
All numbers are **[data]** (our own pull) unless stated. No keyword failed; all 48 returned a 5-year weekly series (262 weeks).

## Commands (exact)

```
python -m scout.trends --file data/evidence/trends/candidates.txt --out data/evidence/trends/candidates-2026-11-03.csv
# aggregation (read-only over the pytrends cache data/evidence/trends/.cache/, same-day series):
python data/evidence/trends/aggregate_candidates.py   # writes the keyword-metrics and niche-summary CSVs; the ranking CSV adds trend_score as defined below
```

Files in `data/evidence/trends/`: `candidates-2026-11-03.csv` (raw scout output), `candidates-2026-11-03-keyword-metrics.csv` (per keyword, with extra robustness metrics), `candidates-2026-11-03-niche-summary.csv` (all niche aggregates), `candidates-2026-11-03-niche-ranking.csv` (ranked).

## Headline finding: the scout's growth numbers are distorted, do not use them as-is

1. **Common spike in Apr-Jun 2026.** All 48 keywords have May or Jun (45 also Apr) among their top-3 "peak months", including evergreen ones such as `dog nail clippers`. In the last 52 weeks, the Apr-Jun 2026 mean is a median ~3.8x the rest of the year (column `spike_ratio`; 1.3x for `dog nail clippers`, up to 14x for sparse keywords). A spike this uniform across unrelated niches is most likely a Google Trends sampling/data artifact or bot/automated traffic, not real demand. **[data]** for the pattern; the cause is **[estimate]**.
2. **Therefore the headline `growth_12m_vs_prior` (up to +5,600%, 47/48 positive) is inflated** by that spike and by near-zero baselines, and the scout's `peak_months` and `seasonality_ratio` mostly measure the spike, not seasonality.
3. **Many series are sparse.** Google reports 0 when volume is below its threshold. 19 of 48 keywords are flagged sparse (>=25% zero weeks in the last 104 weeks, or mean_12m < 10). Growth on a zero baseline is meaningless (e.g. `coin storage box` +5,663%; `sprue cutter` has no growth value, mean 2.3, 97% zero weeks).

**Robust substitute used for ranking:** `yoy_last20w` = mean of the last 20 weeks (about 21 Jun to 1 Nov 2026, after the spike) vs the same 20 weeks a year earlier. Still relative and still noisy, but free of the Apr-Jun artifact. Positive almost everywhere (a modest broad rise, +0.1 to +0.7 in the median niche), which could itself partly be a Google-side level shift; treat the cross-niche *differences*, not the absolute values, as the signal.

## Trend score (transparent)

`trend_score = median(yoy_last20w across the niche's 6 keywords) x share of keywords with yoy_last20w > 0`

Growth multiplied by consistency. Level (`mean_interest_12m`) is NOT in the score, as each keyword is normalized to its own peak (0-100), so levels are not comparable across keywords. A `confidence` column counts non-sparse keywords: high >=5, medium 3-4, low <=2.

## Per-niche ranking

| Rank | Niche | Trend score | Median yoy (last 20w) | Share yoy>0 | Median 12m growth (scout, inflated) | Share growing (scout) | Median mean_interest_12m | Sparse kw | Median seasonality ratio (scout) | Q4 index | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | tcg-supplies | 0.66 | +0.66 | 1.00 | +1.75 | 1.00 | 29.9 | 0/6 | 3.1 | 1.20 | high |
| 2 | watch-accessories | 0.52 | +0.62 | 0.83 | +4.03 | 1.00 | 21.7 | 1/6 | 4.4 | 1.21 | high |
| 3 | vinyl-record-care | 0.39 | +0.58 | 0.67 | +2.67 | 1.00 | 25.9 | 5/6 | 7.3 | 1.78 | low |
| 4 | collectibles-display | 0.35 | +0.42 | 0.83 | +3.58 | 1.00 | 27.6 | 3/6 | 3.2 | 1.30 | medium |
| 5 | auto-detailing-tools | 0.27 | +0.27 | 1.00 | +1.23 | 1.00 | 27.4 | 2/6 | 4.0 | 0.85 | medium |
| 6 | hobby-modeling-tools | 0.20 | +0.30 | 0.67 | +6.97 | 0.83 | 20.4 | 4/6 | 2.4 | 1.67 | low |
| 7 | coin-supplies | 0.17 | +0.20 | 0.83 | +1.59 | 1.00 | 35.2 | 3/6 | 3.2 | 1.14 | medium |
| 8 | pet-grooming-supplies | 0.11 | +0.17 | 0.67 | +1.07 | 1.00 | 28.1 | 1/6 | 3.2 | 0.97 | high |

Dominant peak months (scout, spike-driven, counts of 6): tcg-supplies Apr x6, May x6, Jun x6; watch-accessories Apr x6, May x6, Jun x6; vinyl-record-care Apr x6, May x5, Dec x3; collectibles-display Apr x6, May x6, Jun x5; auto-detailing-tools Apr x6, May x6, Jun x5; hobby-modeling-tools Apr x5, May x5, Jun x5; coin-supplies May x6, Apr x5, Jun x3; pet-grooming-supplies May x6, Jun x6, Apr x5.

Q4 index = mean weekly interest 15 Oct-31 Dec over 2021-2025 divided by the 2021-2025 overall mean (1.0 = no Q4 lift). Excludes 2026, so the artifact is not included.

## Flags for a Nov/Dec start

- **Q4 lift (historical, 2021-2025):** vinyl-record-care 1.78 (`record cleaning kit` 2.31, `record display stand` 1.88, `record storage box` 1.82; gift pattern), hobby-modeling-tools 1.67 (driven by sparse keywords, `hobby tool kit` 2.47; non-sparse `wet palette` 1.07, `hobby knife` 1.30), collectibles-display 1.30, watch-accessories 1.21 (`watch travel case` 1.67), tcg-supplies 1.20, coin-supplies 1.14. Several of these are small-sample (sparse) so the Q4 lift is indicative only.
- **Q4 flat or negative:** auto-detailing-tools 0.85 and pet-grooming-supplies 0.97 (cat grooming brush 0.46, car wash mitt 0.56, foam cannon 0.65): outdoor/seasonal products that peak in warm months; a Nov/Dec start would launch into the trough.
- **Strongly seasonal / spiky (scout ratio >8):** `record cleaning kit` 21.9, `watch repair kit` 17.2, `car detailing brushes` 15.4, `minifigure display case` 13.8, `cat grooming brush` 11.4, `coin capsules` 9.9. Ratios are mostly spike-driven, not trustworthy.
- **Sparse, do not trust:** see `Sparse` column below. Entire vinyl-record-care niche is mostly sparse (5/6), so its position (rank 3) is low confidence.

## Per-keyword table

`yoy20w` = post-spike YoY (last 20w vs same weeks prior year). `zero%` = share of zero weeks in last 104 weeks. `spike` = Apr-Jun 2026 mean / rest of last 52 weeks. `Q4` = Q4 index. `growth`, `peak`, `seas` are the scout's raw outputs (inflated, see above).

| Niche | Keyword | mean_12m | yoy20w | zero% | spike | Q4 | growth (scout) | peak (scout) | seas (scout) | Sparse |
|---|---|---|---|---|---|---|---|---|---|---|
| tcg-supplies | card display case | 32.6 | 0.61 | 0 | 3.1 | 1.18 | 1.81 | Apr,May,Jun | 2.8 |  |
| tcg-supplies | magnetic card holder | 26.9 | 0.71 | 0 | 3.8 | 1.19 | 2.01 | Apr,May,Jun | 3.5 |  |
| tcg-supplies | trading card binder | 42.7 | 0.80 | 0 | 2.1 | 1.36 | 0.95 | May,Apr,Jun | 1.9 |  |
| tcg-supplies | graded card case | 27.2 | 0.42 | 3 | 3.7 | 1.23 | 1.70 | Apr,May,Jun | 3.4 |  |
| tcg-supplies | card storage box | 24.9 | 0.84 | 0 | 4.9 | 1.21 | 3.00 | Apr,May,Jun | 4.7 |  |
| tcg-supplies | card sleeves | 48.8 | 0.27 | 0 | 1.8 | 1.07 | 0.49 | Apr,May,Jun | 1.6 |  |
| collectibles-display | acrylic display case | 28.5 | 0.42 | 0 | 4.0 | 1.08 | 1.52 | Apr,May,Jun | 2.9 |  |
| collectibles-display | figure display case | 27.8 | 0.34 | 10 | 3.6 | 1.24 | 1.51 | Apr,May,Mar | 3.3 |  |
| collectibles-display | minifigure display case | 27.5 | 2.69 | 65 | 4.4 | 1.36 | 5.65 | May,Apr,Jun | 13.8 | YES |
| collectibles-display | diecast display case | 16.8 | 3.38 | 57 | 6.2 | 1.93 | 5.86 | Apr,May,Jun |  | YES |
| collectibles-display | baseball display case | 30.3 | 0.26 | 2 | 3.6 | 1.07 | 1.07 | Apr,May,Jun | 3.1 |  |
| collectibles-display | acrylic display risers | 23.8 |  | 72 | 7.8 | 1.45 | 17.22 | May,Apr,Jun |  | YES |
| coin-supplies | coin holders | 39.4 | -0.14 | 0 | 1.6 | 1.18 | 0.21 | Apr,Feb,May | 1.7 |  |
| coin-supplies | coin capsules | 18.7 | 0.15 | 42 | 7.1 | 1.10 | 6.05 | Apr,May,Jun | 9.9 | YES |
| coin-supplies | coin album | 37.1 | 0.25 | 0 | 2.0 | 1.08 | 1.67 | Jul,Jun,May | 3.2 |  |
| coin-supplies | coin display case | 33.3 | 0.62 | 26 | 3.5 | 1.51 | 1.51 | Apr,May,Dec | 4.1 | YES |
| coin-supplies | coin storage box | 21.1 | 2.32 | 71 | 6.2 | 1.51 | 56.63 | Apr,May,Jun |  | YES |
| coin-supplies | coin flips | 37.8 | 0.02 | 0 | 1.5 | 0.97 | 0.17 | Apr,May,Mar | 2.4 |  |
| vinyl-record-care | record cleaning kit | 30.2 | 1.51 | 47 | 3.6 | 2.31 | 3.27 | Dec,Apr,May | 21.9 | YES |
| vinyl-record-care | vinyl record sleeves | 11.9 | 0.00 | 39 | 1.3 | 1.28 | 1.90 | Feb,Dec,Apr | 8.7 | YES |
| vinyl-record-care | record display stand | 31.3 | 1.01 | 49 | 3.3 | 1.88 | 2.08 | May,Apr,Dec | 7.3 | YES |
| vinyl-record-care | record cleaning brush | 21.3 |  | 78 | 3.0 | 1.74 | 27.44 | Apr,May,Feb |  | YES |
| vinyl-record-care | turntable mat | 21.5 | 0.44 | 6 | 4.8 | 1.17 | 1.91 | Apr,May,Mar | 5.3 |  |
| vinyl-record-care | record storage box | 35.5 | 0.58 | 36 | 3.2 | 1.82 | 4.19 | May,Apr,Jun | 6.4 | YES |
| watch-accessories | watch box | 23.2 | 0.62 | 0 | 4.5 | 1.27 | 2.65 | Apr,May,Jun | 4.4 |  |
| watch-accessories | watch repair kit | 15.2 | 0.83 | 0 | 10.4 | 1.14 | 7.88 | Apr,May,Jun | 17.2 |  |
| watch-accessories | watch strap | 21.9 | 0.29 | 0 | 4.2 | 1.12 | 1.79 | Apr,May,Jun | 4.2 |  |
| watch-accessories | nato watch strap | 49.1 | 0.34 | 0 | 1.8 | 1.00 | 0.57 | May,Apr,Jun | 1.5 |  |
| watch-accessories | watch link remover | 17.3 |  | 75 | 11.2 | 3.05 | 21.00 | Apr,May,Jun |  | YES |
| watch-accessories | watch travel case | 21.5 | 0.80 | 0 | 5.7 | 1.67 | 5.41 | Apr,May,Jun | 8.7 |  |
| hobby-modeling-tools | hobby tool kit | 17.9 | 1.24 | 75 | 11.4 | 2.47 | 15.30 | Apr,May,Jun |  | YES |
| hobby-modeling-tools | model kit tools | 22.8 | -0.04 | 35 | 4.7 | 2.03 | 6.97 | Apr,May,Jun | 8.1 | YES |
| hobby-modeling-tools | wet palette | 27.9 | 0.30 | 0 | 3.0 | 1.07 | 0.84 | Apr,May,Jun | 2.4 |  |
| hobby-modeling-tools | paint storage rack | 16.9 | 4.00 | 69 | 14.6 | 1.19 | 10.72 | Apr,May,Jun |  | YES |
| hobby-modeling-tools | hobby knife | 41.6 | 0.29 | 0 | 2.2 | 1.30 | 0.71 | May,Dec,Jun | 1.9 |  |
| hobby-modeling-tools | sprue cutter | 2.3 |  | 97 | 14.3 | 4.04 |  | Apr,Dec,Oct |  | YES |
| auto-detailing-tools | car detailing brushes | 26.0 | 0.47 | 59 | 4.3 | 0.82 | 2.03 | Apr,May,Jun | 15.4 | YES |
| auto-detailing-tools | car detailing kit | 26.8 | 0.21 | 0 | 3.5 | 1.00 | 1.21 | Apr,May,Jun | 4.0 |  |
| auto-detailing-tools | foam cannon | 30.8 | 0.02 | 0 | 3.2 | 0.65 | 0.59 | Apr,May,Jun | 4.0 |  |
| auto-detailing-tools | trim removal tool | 32.7 | 0.11 | 0 | 2.3 | 0.95 | 0.62 | Apr,May,Jun | 2.1 |  |
| auto-detailing-tools | drill brush set | 14.7 | 1.60 | 51 | 10.6 | 0.88 | 11.77 | Apr,May,Mar |  | YES |
| auto-detailing-tools | car wash mitt | 28.1 | 0.32 | 15 | 3.8 | 0.56 | 1.24 | Apr,May,Jun | 6.8 |  |
| pet-grooming-supplies | dog grooming kit | 24.8 | 0.34 | 0 | 5.3 | 1.02 | 1.58 | Apr,May,Jun | 4.1 |  |
| pet-grooming-supplies | slicker brush | 27.5 | 0.28 | 0 | 3.8 | 0.97 | 1.19 | Apr,May,Jun | 3.3 |  |
| pet-grooming-supplies | deshedding brush | 37.6 | 0.06 | 0 | 2.5 | 0.76 | 0.38 | May,Jun,Apr | 2.6 |  |
| pet-grooming-supplies | dog nail clippers | 68.8 | -0.09 | 0 | 1.3 | 0.98 | 0.10 | May,Jun,Jul | 1.2 |  |
| pet-grooming-supplies | pet hair remover | 28.7 | -0.12 | 0 | 3.1 | 0.97 | 0.96 | Apr,May,Jun | 3.1 |  |
| pet-grooming-supplies | cat grooming brush | 23.2 | 0.34 | 46 | 5.1 | 0.46 | 2.42 | May,Apr,Jun | 11.4 | YES |

Blank cells: value not computable (zero baseline) or not returned by the scout. `sprue cutter` is effectively unusable (mean 2.3, 97% zero weeks).

## Method limits

- Google Trends values are **relative interest (0-100), normalized per keyword to its own peak in the window**. They are not search volume. Levels cannot be compared across keywords; a keyword with a small absolute volume can look as "big" as a popular one.
- Each keyword was queried alone (`scout.trends` design), so no cross-keyword scaling is available. Cross-niche comparison uses growth/consistency only.
- Low-volume keywords are thresholded and sampled: zero weeks and spiky values make growth and seasonality noisy. 19/48 flagged sparse.
- pytrends is an unofficial client of Google's undocumented endpoint; results can change between pulls (sampling), and the Apr-Jun 2026 anomaly above is unexplained. Re-pull on another day and compare before trusting any single value. The pull is cached per day, so a same-day rerun returns identical data.
- The 5-year weekly series is used; "last 12 months" = last 52 weekly points; seasonality = last 156 weeks (3 years), which includes the 2026 spike year.
- `yoy_last20w`, `spike_ratio`, `zero%`, `Q4` are our own additions computed from the same cached series; the thresholds (sparse = >=25% zeros or mean_12m<10) are arbitrary judgement calls.
- Demand proxy only: nothing here covers eBay sold volume, price, competition or margin. Those come from the eBay/CJ branches (API keys not yet available).

## Suggested next steps

- Re-pull a subset (e.g. top 3 niches) on a different day and with `--sleep 5` to check the Apr-Jun anomaly.
- Cross-check the top niches (tcg-supplies, watch-accessories, collectibles-display) against eBay sold data when the Browse API key exists.
