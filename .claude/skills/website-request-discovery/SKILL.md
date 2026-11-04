---
name: website-request-discovery
description: Inspect permitted browser network requests, document request and response contracts, and build a tested API client or adapter for a specific website workflow. Also distinguish observable traffic signals from private analytics.
---

# Website request discovery

Use when the user asks to inspect a website's network activity, understand its
request payloads, or turn a permitted browser workflow into a reusable integration.
Read root AGENTS.md, CLAUDE.md and applicable source decisions first. Announce use
of this skill. This skill authorizes no purchases, messages or account changes.

## Define the job

Identify the URL, desired operation and fields, whether the site belongs to the
user, and the available authorized session. Start with read-only inspection.
Resolve missing context from the project before asking one focused question.
Prefer a documented API, maintained SDK or existing connector when it meets the
need. Record build-versus-reuse before implementing a client.

Inspect current source terms and record allowed access, retention and model use.
Apply the project's source-terms gate. A browser-visible endpoint is not necessarily
a public or supported API. Possession of a session does not authorize every action.
Do not bypass authentication, CAPTCHA, paywalls, signatures or account permissions.
Do not probe other users' identifiers or retrieve their private records.

## Observe a minimal browser workflow

1. Discover available browser/DevTools network tools. If unavailable, report that
   limit and use official documentation or a user-provided sanitized capture.
   Never claim inspection based only on a page's HTML or a search result.
2. Open the intended page in an authorized browser context. Capture only the
   requests necessary for one read-only action, such as a search or page change.
   Avoid full-session HAR exports; these can contain credentials and personal data.
3. Separate relevant fetch/XHR, GraphQL or WebSocket exchanges from advertisements,
   assets and analytics beacons. Record the initiator and corresponding UI action.
4. Observe method, origin/path, query keys, content type, payload structure, response
   shape, status and pagination. Observe cache/rate-limit headers where available.
   Describe authentication and CSRF requirements without exposing secret values.
5. Change one harmless filter or page at a time to determine which fields matter.
   Record only observed behavior; label undocumented assumptions as unverified.

GET does not guarantee a harmless operation, and POST does not imply a write:
classify the actual operation. Viewing a submit button does not authorize clicking
it. Require task authorization before reproducing orders, messages, deletes or other
state-changing actions. Do not replay an uncertain mutation after a timeout.

## Produce a sanitized contract

For each relevant operation, record:

```text
Source URL, documentation/terms URL, inspected date:
Workflow and authorization scope:
Status: observed / replay tested / client implemented / integrated
Method and endpoint template:
Query and body schema (types, optional fields, synthetic example):
Required headers (names only for credentials):
Authentication mechanism and expiry/refresh requirements:
Response schema and field meanings:
Pagination, sorting, limits and error behavior:
Permitted retention/use and known limitations:
Evidence reference and validation performed:
```

Never commit cookies, bearer tokens, API keys, signed URLs, session IDs, raw HARs,
personal records or restricted provider responses. Redact secrets in paths, query
strings, bodies and responses as well as headers. Use invented fixtures marked
MOCK. Gitignore alone does not make restricted retention acceptable.

## Validate before building

Replay the smallest permitted read-only request through the supported auth path.
Use timeouts and a small request budget; respect rate limits and Retry-After.
Compare returned values with the browser for the same filters and observation time.
Check one pagination boundary and an empty result where practical. Distinguish
observed errors from synthetic test cases. Stop on access denial; do not rotate
identities or proxies to evade it. Record untested behavior explicitly.

An internal endpoint may change without notice. If automation is prohibited or
access is unavailable, document the contract only to the extent permitted and
identify an official API or manual alternative. Do not promise a working client.

## Build only within the requested scope

“Make an API out of it” normally means a client/adapter for an existing endpoint.
A hosted wrapper service is a separate deployment decision, not an automatic step.
Follow existing connector interfaces and source contracts; do not create a second
evidence store. Keep credentials in the existing secret mechanism, never source.

Implement explicit request/response models, parameter validation, bounded pagination,
timeouts, cancellation and rate limits. Retry only operations safe to retry; reconcile
uncertain mutations. Fail visibly on schema changes and authentication expiry.
Restrict allowed upstream hosts; never expose an arbitrary authenticated URL proxy.
Preserve TLS verification. Sanitize logs and surface source/time provenance.

Test with synthetic fixtures: valid and empty results, malformed fields, pagination
termination, authentication failure, throttling and secret redaction. No live site
calls or real credentials in CI. Follow project checks before committing/pushing.
Document execution, credentials by variable name, limits and remaining uncertainties.
Do not deploy, purchase access or publish a wrapper unless authorized.

## Traffic investigation limits

An IP association can discover domains; it cannot disclose a competitor's visitor
logs, conversions, acquisition costs or profit. Shared hosting/CDNs may serve many
unrelated businesses. Keep domain identity separate from IP identity.

For a discovered domain, investigate permitted evidence about:

- Estimated visits, audience countries and channel mix from analytics providers.
- Search visibility and keywords from search evidence and SEO providers.
- Public ads, offers and landing pages from advertising libraries.
- Public referring links, social activity and campaign parameters.

Verify current provider coverage and methods before recommending one. Label these
as estimates or observed public signals, retain observation dates and account for
small-site gaps. Independent sources may share upstream data. Running ads or a
large follower count does not prove profitable traffic.

Browser network inspection shows what *our browser* sends and receives. An analytics
tag, tracking ID or event payload reveals instrumentation, not aggregate analytics
access or actual sales. Exact first-party traffic requires authorized analytics/log
access; reconciled orders are needed to validate conversions and economics.

## Completion

Return a short finding, the contract/client path, what was actually tested, and the
next useful step. Keep full details in the artifact. Success means another engineer
can reproduce the permitted workflow without copied credentials or hidden guesses.
