# 0019 ChatGPT lane: research and images via Codex CLI on the owner's ChatGPT plan

Date: 2026-11-26. Owner request: use the owner's ChatGPT (Go plan) for graphics and research as a mini agent inside the Claude environment.

## Candidates

| Candidate | License / cost | Maintenance signal | Terms | Verdict |
|---|---|---|---|---|
| OpenAI Codex CLI (`@openai/codex`), "Sign in with ChatGPT", `codex exec` headless | Apache-2.0; usage from the ChatGPT plan, no extra bill | Official OpenAI repo, releases several times a week (0.172.0 on 2026-11-24) | Official client for the plan; help center says Codex is included with Go ([help.openai.com/articles/11369540](https://help.openai.com/articles/11369540)) | **Chosen** |
| OpenAI API key (gpt-image, Responses API web search) | Paid per call, separate from ChatGPT | Official | Fine | Fallback only, needs owner spend approval |
| Browser automation of chatgpt.com | - | - | OpenAI Terms of Use forbid automated access/extraction; CLAUDE.md rule 6 | **Rejected** |
| HKUDS/CLI-Anything (owner pointer) | Apache-2.0 per repo `[unverified]` | Active | - | Not installed (unreviewed third-party, rule 7). Borrowed its pattern: one CLI per tool, `--json` output, a SKILL.md documenting commands, a smoke test |

## Pilot (2026-11-26, this container)

- Install: `scripts/install_codex.sh`, Codex 0.169.0 (released 2026-11-13, pinned 2 weeks back from latest), into gitignored `tools/codex/`.
- Login: device code (`codex login --device-auth`), owner approved in the browser. `[data]`
- Research: eBay dropshipping rules question, 15 s, 5 bullets each with an ebay.com URL, live web search confirmed in the log (`web search: site:ebay.com/help ...`). CJ delivery-time question, 8 s, cited CJ FAQ and said what it could not verify. Driver model reported `gpt-6-luna`. `[data]`
- Images on the **Go plan work**: `$imagegen`, 1024x1024 PNG in 27-32 s, two of two prompts followed. `[data]` Plan quota for images on Go is unpublished `[unknown]`; capped at 20/day in code until we see the limit.

- General `ask` (owner: "not only images, explore it"): vision + JSON schema on an image, 5.4 s, correct objects and `has_text=false` `[data]`. Reasoning second opinion on a margin, 11.8 s, good risks with eBay URLs but an arithmetic error ($10.34 instead of $11.34) `[data]`: numbers from this lane are recomputed in code.

## Rules carried in code

- Image refs need a provenance URL per ref; sidecar JSON per image; prompts append "no text/logos/watermarks/badges/borders".
- CJ product photos must not be sent to be re-rendered into scenes (product-pixels rule). Phase 1 builds the compositor (segment product, generate background, paste original pixels back).
- Usage counts in `data/private/chatgpt_usage.jsonl`; research copies in `data/private/chatgpt/`.

## Limits and follow-ups

- Cloud containers are ephemeral: login per new cloud session (owner enters a code). On the owner's own machine the login persists.
- Model output is research leads, not evidence; claims stay `[secondary]/[unverified]` until URLs are checked.
