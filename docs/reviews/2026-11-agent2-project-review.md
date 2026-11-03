# Independent project review — 2026-11-03

Reviewed baseline: `4f97a8b`, branch `agent2/review-and-shortlist`.

**Verdict [estimate]: continue the offline feasibility experiment; do not launch.**
The implementation is a small research toolkit, not a production commerce system.
The zero-inventory thesis is possible, but neither profitable demand nor a compliant,
reliable supply chain has been demonstrated. Better presentation is an untested
conversion hypothesis, not a defensible advantage. The explicit stress test and
honest evidence labels are useful; more orchestration will not close the evidence gap.

## Findings

Effort is an engineering estimate, excluding external approval and legal lead time.

| Severity | Finding and evidence | Recommended fix | Effort |
|---|---|---|---|
| blocker | [data] No live catalog, freight, sold observations or conversion results establish viability. Decision 0002 §§2d, 3.3 models only one passing type, with estimated costs and a premium over a generic incumbent. | Validate identical pack size, material, condition and delivered price for a small non-magnetic cohort; measure realized contribution and labor. Do not call 24 product types 24 viable SKUs. | 2–5 days plus test orders |
| blocker | [primary] The API license prohibits price modeling and restricts derived statistics; it also explicitly addresses automated seller arbitrage, which the research misses. [S2], prohibited-use list. | Ask eBay about the intended ordering/tracking workflow as well as price research. Do not infer wholesale dropshipping policy permission authorizes every API automation. | 1 day + response |
| blocker | [data] The terms gate is not implemented: `scout/store.py:61` accepts any source without terms or retention. Decision 0004 §3 calls existing Trends evidence internal/non-redistributed, but it is tracked in this public repository. CJ private storage exception also conflicts with “unknown terms mean do not store.” | Resolve source permissions and public-history disposition with owner; enforce a source registry before ingestion. Gitignore is not a license. | 1–3 days + decisions |
| high | [data] Terapeak's terms remain unchecked (0004 §3), and its CSV has no CJ ID/SKU, pack size, currency or structured matching key (`docs/templates/terapeak-observations.csv:1`). | Require an explicit operator-selected comparable cohort and shipping basis; never silently join on fuzzy product names. Resolve permitted derived publication before real observations. | 1–2 days |
| high | [data] Margin ads use `ad_rate * price` (`scout/margin.py:50`); the FVF correctly includes tax, but the order-fee threshold uses item price alone (`:47`). [primary] S1 defines total sale to include sales tax. | Verify the ad campaign's current fee base/attribution and refund-credit rules; test the $10 boundary including tax. Confirm exact supplies category, seller location, store tier and surcharges. | 1 day |
| high | [estimate] Return and dispute rates are disjoint assumptions, full refunds assume variable FVF credit, and the stress case is only +$3 duty/doubled returns (`scout/margin.py:54–77`). It excludes labor, payout financing, supplier cancellation, FX and chargeback fees. | Separate commercial contribution from accounting net; run 7–8% ads, realistic freight by destination and delayed-payout scenarios. Do not treat fixed $3 as a tariff forecast for domestic stock. | 1–2 days |
| high | [data] `compute` accepts negative, nonfinite and impossible rates; `evaluate` compares already rounded margins (`scout/margin.py:43–77`). Existing regression tests largely freeze outputs. | Validate input domains and add independent hand-calculated boundary cases, including combined refund probabilities and rounding around pass thresholds. | 0.5–1 day |
| high | [data] `rebuild` imports rows with a failed checksum and `query` exposes them normally (`scout/store.py:121–168`). `tests/test_store.py:38` asserts only the flag. | Quarantine or abort on mismatches; publish a new database atomically only after full verification. | 1 day |
| high | [data] Store dataset names form filesystem paths (`scout/store.py:76`) and quoted SQL identifiers are not escaped (`:147–157`). `rebuild` deletes the old database first (`:108`). Existing DB queries become stale after another ingest (`:175`). | Validate identifiers/paths, rebuild transactionally to a temporary DB, track lake freshness, and test corrupt/truncated/concurrent runs. | 1–2 days |
| high | [data] `_inline_images` reads arbitrary local paths and remote URLs without byte limits (`scout/llm.py:109–138`); its errors occur outside retry handling (`:174`). | Restrict image roots and network destinations before using untrusted inputs; limit size/type/redirects, avoid repeated downloads, and handle image errors explicitly. | 1–2 days |
| medium | [data] Router accepts empty content as success; malformed JSON and empty choices bypass fallback (`scout/llm.py:186–199`). Error bodies may echo private input. | Validate response shape/content and sanitize failures; test 429, timeout, invalid JSON, empty choices/content and provider fallback. | 1 day |
| high | [data] CJ parsing extracts positive digits from negative/malformed price text (`scout/cj.py:43`); normalizers assume dict/list shapes; HTTP status isn't checked before JSON (`:140`). Tests validate invented shapes, not the service. | Keep malformed prices unusable downstream; validate live search/detail/freight fixtures privately, including US variant stock, units and pack quantities. | 1–2 days |
| blocker | [data] Image permission is unresolved (`docs/research/12-compliance-niche-cards.md:17`). No automated text screen can establish image rights, safety or a supplier contract. | Obtain rights before any listing, verify wholesale agreement and clean images; retain private evidence references and require human release approval. | external dependency |
| high | [unverified] Embedded magnets are presumed lower risk; CPSC page was inaccessible in this review (403). Adult wording alone does not determine children's-product classification. | Confirm current magnet-rule status/applicability and age classification against product design/testing with qualified advice; exclude uncertain magnetic items from launch. | external dependency |
| high | [data] Prop 65 supplier statements and settlement concentrations are used as shortcuts (research 12 §0.5). [unverified] Current OEHHA content could not be retrieved usefully. | Assess exposure, materials and applicable exemptions; a warning or “PVC-free” claim is not a substitute for applicable product-safety requirements. Add recall screening, traceability and incident handling. | 2–5 days + testing |
| high | [primary] FTC requires reasonable shipping basis, delay consent or prompt refunds [S4]. Avoiding “fast” wording does not discharge those duties. | Add stock reservation/refresh, handling cutoffs, tracking, delay notices, refund procedure and supplier return address. Include order funding before marketplace payouts. | 3–5 days |
| medium | [data] Decision 0002 demand table maps pet growth 0.11 to 3 despite stated <0.25 → 2; hard floor $15 elsewhere conflicts with its niche floor $25. Old Browse/Trends actions remain after withdrawal. | Keep accepted decisions immutable, but publish a superseding operational decision with corrected scoring and current sources. For this niche use its explicit $25 floor. | 0.5 day |
| high | [estimate] Niche scoring rewards correlated Trends/category/fit evidence and estimated margin premiums; a narrow 0.38 lead is not robust market validation. | Re-score with independent sold evidence, comparable units and uncertainty intervals. Count neither markup-derived prices nor passing models as demand evidence. | 1 day |
| medium | [data] CI runs tests and lint on pushes/PRs, uses read-only permissions and no ingestion (`.github/workflows/ci.yml:1`). It does not run commit-msg checks; local branch hook protects only main/master. | Require CI via server rules on the actual default branch, validate commit metadata in CI, pin actions/dependencies, and add integration/error-path tests. | 1 day |
| medium | [data] Public API confirms default branch `research/feasibility-poc`, no license. README and SECURITY.md absent in tracked tree. [unverified] Protection endpoint returned 401; secret-scanning/push-protection status is not exposed anonymously. | Owner verifies server settings; add onboarding, security reporting and an intentional license. Public visibility alone does not license reuse. | 0.5 day |
| medium | [data] Commit authors expose personal email addresses. Strategy, pricing and supplier playbooks are public. | Owner chooses public/private strategy boundary and future noreply identity. Do not rewrite history or change identity without a decision. | owner decision |
| medium | [data] Research plans repeat source/storage policy inconsistently; stage E is labelled key-blocked although offline construction is possible (`docs/plan/ai-team.md:53`). Data analyst, engineer and sales roles overlap. | Merge operational checklists into one current runbook with explicit source/price/compliance ownership; archive superseded warehouse/Shopify plans. Keep primary evidence and required graph artifacts. | 1 day |

## Primary-source verification, retrieved 2026-11-03

- **S1 [primary]:** https://www.ebay.com/help/selling/fees-credits-invoices/selling-fees?id=4822 — HTTP 200; confirms general 13.6%, category exceptions, tax-inclusive fee base and $0.30/$0.40 order fee. Exact SKU category remains unknown.
- **S2 [primary]:** https://developer.ebay.com/develop/apis/api-license-agreement — HTTP 200; checked the text corresponding to §§8.1.3, 8.1.4, 9.5, 9.7, 9.10. Six/24-hour limits concern displayed content, not blanket retention permission. Statistics clause names site-wide/category statistics; do not generalize it into an independently verified ban on every manual observation. Price-modeling restriction is explicit. The adjacent arbitrage prohibition deserves separate review.
- **S3 [primary]:** https://developers.cjdropshipping.com/en/api/api2/api/product.html — HTTP 200; listV2 documents size 1–100, page 1–1000 and countryCode as inventory-country filtering. This clarifies documented intent, not actual live inventory or delivery guarantees; no live call made.
- **S4 [primary]:** https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule — HTTP 200; reasonable shipping basis, default 30 days absent a statement, delay-consent and refund duties confirmed.
- **S5 [primary]:** https://www.ebay.com/help/selling/posting-items/setting-postage-options/drop-shipping?id=4176 — HTTP 200. Wholesale supplier fulfillment permitted; seller retains responsibility. This is not proof of a particular CJ contractual arrangement.
- **S6 [unverified]:** https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Magnets — HTTP 403. No fresh CPSC verification claimed.
- **S7 [unverified]:** https://www.p65warnings.ca.gov/businesses — returned effectively empty text. No current thresholds verified.

## Validation and limits

[data] Baseline `make test`: 30 passed. Tests are fast and useful for regressions,
but no end-to-end production contract, real delivery or compliance is established.
Review-only changes leave protected implementation and decisions untouched.

[data] Independent history scan uses detect-secrets 1.5.0 over reachable blobs from
`git rev-list --objects --all`, decompressing gzip evidence, rather than only the
working tree. 290 blobs scanned. Detected candidates were graph hashes/signatures, embedded
HTML assets and Docker password-file paths, not confirmed credentials. No live
secret was identified. Personal author emails remain exposed. This is
not proof that deleted/unreachable remote objects or all personal data are absent.
No credential values or author email addresses are reproduced here.

## Questions for the review pull request

1. Which CJ data-use and image rights permit private storage and publication of derived metrics?
2. Are manual Terapeak conclusions approved for this use, and how should a cohort map to CJ variants with identical pack sizes?
3. Who supplies approved freight/handling inputs, category fees and regulatory sign-off?
4. With one required source branch, may the first PR merge before publishing the second? Two independent concurrent PRs cannot share the same head/base pair.
5. Should strategy stay public, and should future commits use an owner-approved noreply identity?

## Top 10 actions

1. Resolve data rights and eBay automation permission before any live ingest.
2. Obtain CJ wholesale/image authorization and resolve public Trends evidence disposition.
3. Collect comparable manual sold observations with explicit unit/pack matching.
4. Verify real CJ US variant stock, freight and handling for a small passive cohort.
5. Confirm category/ad fee bases and run freight, returns and payout sensitivities.
6. Build the offline shortlist with missing-evidence flags and no automatic launch verdict.
7. Resolve magnetic/material/children's-product gates and document human release approval.
8. Fix store integrity, path validation, atomic rebuild and freshness handling.
9. Harden model-router input boundaries and malformed-response fallback.
10. Require branch checks; add onboarding/license/security policy and consolidate active runbooks.
