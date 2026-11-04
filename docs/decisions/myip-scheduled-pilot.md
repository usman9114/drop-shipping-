# Proposed: scheduled MyIP API sample pilot

## Scope and reuse

Use existing GitHub Actions scheduling and the maintained requests library already
used by this repository. No custom scheduler, browser crawler or paid subscription.
The job runs the provider's documented public example once per invocation. This is
a transport/schema smoke check, not a Shopify discovery pipeline or demand evidence.

[primary] https://myip.ms/info/api documents low-volume automated access to its
public sample queries. https://myip.ms/info/terms restricts unauthorized automation.
Sample access does not resolve licensing for a retained discovery dataset; this
pilot saves no source records, response bodies, visitor data or raw artifacts.
Only operational timestamp and pass/fail metadata enter workflow logs. Do not
register this as a production source or ingest it into the evidence lake.

## Schedule and operation

Proposed schedule: daily 07:17 UTC; GitHub may delay scheduled jobs. Manual dispatch
is also defined. Scheduled workflows run from the default branch, so the schedule
is not activated merely by opening this PR. Repository Actions must be enabled.

Local equivalent: `python scripts/myip_sample_check.py`.
The fixed sample URL uses no credentials. One request, no retries, bounded response
size, connection/read timeouts and a two-minute job timeout. Redirects fail closed.
A nonzero exit marks failure; normal repository notification settings apply.
No messages are sent to external recipients.

Stop by disabling the workflow. A failed schema check requires investigation, not
additional requests or fallback HTML scraping. Tests are synthetic and offline.

## Gate before useful Shopify discovery

Validate an authorized Shopify IP query, confirm full-list/pagination support and
rate/billing limits, and record retention/use terms in the existing source registry.
Preserve separate current and historical domains. Provider popularity figures are
not verified sales or customer traffic channels. No such discovery integration is
enabled by this pilot.

## Validation on 2026-11-04

[data] `python scripts/myip_sample_check.py` passed against the live official
sample at 19:56:11 UTC. Both current and historical list contracts were validated;
no domain records were saved. This tests the worker, not GitHub's cron trigger.
