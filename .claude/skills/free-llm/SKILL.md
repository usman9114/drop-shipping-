---
name: free-llm
description: Offload bulk text and image work to the project's free models (Z.ai GLM Flash, 8 parallel workers, plus the OpenRouter free lane, 900 calls a day) through scout.llm. Use for classifying, tagging, extracting fields, summarising fetched pages, image QA, code drafts and independent second opinions on any batch of more than a few items, instead of spending Claude tokens on it.
---

# Free models: GLM Flash + OpenRouter free lane

Owner (2026-11-05): "use GLM and OpenRouter to get the most out of them." Claude agents plan, check and decide; free models do the volume.

## Commands

```bash
python -m scout.llm --usage                                   # keys present, OpenRouter free calls left today
python -m scout.llm --task bulk "one prompt"                  # single call (bulk|reasoning|code|vision)
python -m scout.llm --batch in.jsonl --out out.jsonl \
    --task bulk --workers 8 --spread 0.15 [--system "..."] [--json]
python -m scout.llm --second-opinion "Label first line: X or Y. ..."   # GLM vs OpenRouter model, reports agree
```

Batch input, one JSON object per line: `{"id": "...", "prompt": "...", "image": "url (optional)", "system": "... (optional)"}`. Output lines carry the same `id` plus `model` and `text`, or `error`. **Resumable**: rerun the same command and finished ids are skipped, failed ids retried. Keep batch files under `data/private/` or the scratchpad, never committed.

In Python: `scout.llm.chat_many(prompts, workers=8, task="bulk", spread=0.15)`, `scout.llm.run_batch(...)`, `scout.llm.second_opinion(prompt)`.

## Limits (tested)

| Lane | Speed | Limit |
|---|---|---|
| GLM Flash (`bulk` = glm-4.5-flash; `reasoning`/`code` = glm-4.7-flash, thinks about a minute per call) | about 1 call/s with 8 workers | 8 workers; 16 gives HTTP errors |
| OpenRouter free (`spread` share) | one call every 3 to 5 s | 1,000/day, capped at 900 in `data/private/llm_usage.json` |

Measured 2026-11-05: 12 bulk prompts in 31 s, 4 of them on the OpenRouter lane, 0 errors. `spread=0.15` keeps both lanes busy; higher makes OpenRouter the bottleneck. Use `bulk` for classification; `reasoning` only when the task needs thought.

## How to get good results

1. **Rules first, model second.** Anything a regex or lookup decides (AliExpress image names, SKU formats, known app hosts) stays in code. Send the model only the fuzzy cases.
2. **Give context the model lacks.** In the 2026-11-05 test GLM Flash called "CJ" a brand ("Korean entertainment company") and "HOMEFUN Store" a brand. Say what the domain is ("CJ = CJ Dropshipping, a supplier") and give 2 or 3 labelled examples in the system prompt.
3. **Ask for the label on the first line, one word,** then a short reason. That makes outputs parseable and lets `--second-opinion` compare them.
4. **Small first** (CLAUDE.md principle 10): run 10 to 30 items, hand-check them, then scale.
5. **Validate before relying** (principle 5): run a second opinion on a sample (or `--spread 0.5` on the sample), report the agreement rate, and hand-check the disagreements. Results are non-deterministic; a single run is not proof.
6. Record the batch: input count, ok/error counts, models used, agreement rate, in the report or `store.record_run` params.

## Never

- Send secrets, `.env` contents, customer data, supplier contracts or personal data. Free routes are not private.
- Turn on paid routes (`SCOUT_ALLOW_PAID=1`) without the owner's approval.
- Present a model label as `[data]`. It is a `[proxy]` until a hand-checked sample gives it an accuracy figure.
