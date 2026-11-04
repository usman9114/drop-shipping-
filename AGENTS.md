# Agent working agreement: reverse-engineering mindset

## Purpose and scope

Work backward from a business decision to the evidence that could change it.
Discover useful mechanisms, test them, and leave reproducible findings.
Do not substitute a familiar tool list or a persuasive explanation for an investigation.

Our operating question is:

> Can we acquire a buyer, deliver what we promised, resolve problems, and retain
> enough profit to repeat it?

These instructions apply across the repository. Read [CLAUDE.md](CLAUDE.md),
[shared team rules](.claude/agents/_team-rules.md), and the relevant task handoff
before working. Their project constraints still apply; this file adds a research
method, not permission to change accepted decisions or expand a task's scope.
Use the knowledge graph as directed there. Work on your own branch and submit
changes into `research/feasibility-poc`; never push directly to that branch.

## The investigation loop

Apply this loop to substantial discovery, feasibility and implementation choices.
Scale the effort to the decision: a simple factual question needs a direct check,
not a new report, integration or multi-agent exercise.

1. **Name the decision.** State what we need to decide, what is unknown, and what
   evidence would change the next action. Define a useful result before searching.
2. **Work backward to observable traces.** Ask what systems, records and public
   artifacts the activity would leave behind. Identify who produces those traces,
   why they exist, and whether we can legitimately access and use them.
3. **Search for the mechanism.** Search technical terms, documentation, examples
   and adjacent disciplines as well as commercial tools. For example, investigate
   `reverse IP lookup` and `technology detection` when seeking stores, rather than
   relying only on a query for the best ecommerce research software.
4. **Test the cheapest useful path.** Use an existing connector, permitted lookup
   or manual sample before building an integration or proposing a subscription.
   For a source comparison, try the same question and comparable sample on a few
   candidates. Record inaccessible features as untested, not as failures.
5. **Try to disprove the explanation.** Check alternative causes, stale records,
   duplicates, irrelevant matches and counterexamples. Ask what would make the
   proposed opportunity fail even if the observed signal is real.
6. **Make a bounded decision.** Recommend use, further validation, or rejection
   for a specific purpose. State the strongest evidence, limitations and next
   cheapest check. Stop when further research would not change the next action;
   if blocked, identify the exact missing evidence or access.
7. **Keep the reusable lesson.** Record the successful query or procedure, failed
   approaches and their reasons, and when to recheck. Extend existing research
   and decision records instead of creating overlapping documents.

## Find sources by the traces they expose

This table suggests investigation paths, not approved integrations or verified facts.

| Question | Traces to investigate | What the trace alone cannot establish |
| --- | --- | --- |
| Which stores could be relevant? | DNS/hosting associations, platform fingerprints, directories | Active trading, target market, sales or profit |
| What do they offer? | Public product pages, collections, bundles, prices and delivery policies | Units sold, realized prices or actual delivery performance |
| How do buyers discover them? | Ad libraries, search visibility, referring links and public campaigns | Acquisition cost, conversion rate or incremental sales |
| Where might buyers be disappointed? | Reviews, support policies, recurring public complaints | Representative defect or return rates |
| Can we deliver a comparable offer? | Authorized supplier specifications, freight quotes and availability | Product equivalence, reliable fulfillment or permission to sell |
| Why might the model work? | Changes over time and comparable successful and unsuccessful examples | Causation or repeatable economics for our business |

An unexpected source is worth testing because of the trace it exposes, not because
it is obscure. A popular source earns no automatic preference either.

### Example: using MyIP.ms as a lead source

The hypothesis is: shared hosting infrastructure can reveal domains worth examining.
Follow the chain: hosting association -> domain -> verified active store -> relevant
offer -> independently supported demand -> supplier and margin checks -> pilot.

Test each link. The IP owner may be a platform, not the merchant. Hosting country
does not establish merchant location or customer market. Shared IPs and CDNs can
produce unrelated matches; directory records may be historical or incomplete.
Popularity estimates do not establish orders, and orders do not establish profit.

Compare this discovery path with another permitted path using the same niche and
qualification criteria. MyIP.ms is a worked example, not a required provider or a
claim that it outperforms alternatives. Verify current access, terms and capabilities.

## Evidence and source evaluation

- Label decision-driving claims `[data]`, `[primary]`, `[secondary]`, `[estimate]`
  or `[unverified]` as required by the project. Separate observation, inference
  and hypothesis; an official vendor claim proves what it advertises, not accuracy.
- Keep source URL or command/run ID, observation date, applicable period/market,
  sampling method and known limitations. Preserve disagreement between sources;
  investigate shared upstream data before treating agreement as corroboration.
- Evaluate sources by relevant verified results, unique useful discoveries,
  freshness, false positives, missing coverage, reproducibility, permitted use,
  cost and effort. Report counts with denominators; small samples do not prove
  population accuracy. Do not manufacture precision with arbitrary scores.
- Distinguish **discovered**, **documentation checked**, **sample tested**, and
  **integrated**. Never imply a tool or API was tested because its marketing page
  was read. Recommend a source for the job it demonstrated, with remaining gaps.
- Account for selection and survivorship bias. Study failed or inactive examples
  where available. Visible ads, review counts, installed apps and best-seller labels
  are signals to investigate, not verified revenue, profitability or causal proof.
  Absence from a directory or search result is not proof that something does not exist.
- Reverse-engineer the customer problem and operating mechanism. Do not assume we
  can reproduce a brand's audience, supplier terms, economics or advantages.

## Connect research to the system

- **Data layer:** preserve provenance, observation time, units, currency, entity
  identity, permissions and missingness. Join stores by verified domains/identities,
  not a shared IP. Distinguish brands, stores, products and variants. An unknown
  value is not zero, false or a passing check.
- **Analytics layer:** use deterministic, versioned calculations for margins and
  feasibility. Keep measured results separate from scenarios and vendor estimates.
- **Intelligence layer:** AI leads investigation, proposes explanations, compares
  evidence and identifies the next useful experiment. It must expose uncertainty
  and abstain when evidence is insufficient; it cannot invent missing facts.
- **Application layer:** connect recommendations to an authorized task or test,
  with outcome tracking and reconciliation. A recommendation does not authorize
  spending, outreach, publishing, account creation or changes to external systems.

Existing source-terms, privacy, image and platform rules remain binding. Public
visibility is not permission for bulk collection, retention, redistribution or
model use. Do not bypass access controls or copy competitors' protected assets.
Keep raw provider data and personal information out of this public repository.
Use existing permitted storage and contracts; do not build a parallel evidence store.

## Completion and communication

For substantial research, update the appropriate existing research or decision file
with this compact record. Include only information permitted in the public repo:

```text
Decision and unknown:
Hypothesis and observable trace:
Sources tried; access/test status:
Procedure, date, sample and selection method:
Findings with evidence labels and citations:
Counterevidence, limitations and unknowns:
Recommendation and next check / stop condition:
```

Keep user updates brief: finding, implication, next action. Lead the final answer
with the result and link the artifact; leave the full investigation in the file.
Do not narrate every search, repeat caveats, or ask for information already available.
If intent is ambiguous, make useful independent progress and ask one focused question.
Do not speculate about how someone discovered a source; explain the mechanism we
can reproduce and test ourselves.

A substantial finding is ready when another engineer can reproduce the lead,
identify its uncertainty, and explain why the source is useful for this decision.

For repository changes, run `make setup` once per clone, refresh the knowledge
graph, and keep `make test` and `pre-commit run --all-files` green before pushing.
Follow the existing authorship and commit-hook rules. A research task does not
authorize unrelated code changes, paid services or a production launch.
