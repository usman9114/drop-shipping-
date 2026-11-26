---
name: chatgpt
description: Use the owner's ChatGPT plan (Go) as a mini agent via Codex CLI - sourced web research, image generation (gpt-image), vision (read/inspect images), structured JSON extraction against a schema, and reasoning/writing second opinions. Use for sourced research questions, an independent second opinion next to Claude/GLM, image QA, and graphics - scenes, backgrounds, diagrams, mood boards, UI or report art. Not for CJ product photos placed into scenes (product pixels must stay untouched) and not for bulk classification (use free-llm).
---

# ChatGPT lane (Codex CLI on the owner's ChatGPT plan)

Owner (2026-11-26): "leverage my ChatGPT ... graphics and research ... a mini agent in our Claude env." Decision: `docs/decisions/0019-chatgpt-lane.md`.

How it works: `scout/chatgpt.py` drives `codex exec` (OpenAI Codex CLI, Apache-2.0, pinned in `scripts/install_codex.sh`) signed in with the owner's ChatGPT account. No API key and no per-call bill; it uses the plan's Codex allowance (images use it 3-5x faster). Driving chatgpt.com with a browser is forbidden (OpenAI terms, CLAUDE.md rule 6).

## Setup (once per container)

The "Crypto" cloud environment's setup script runs `scripts/install_codex.sh` in every fresh container (owner 2026-11-26), so Codex is normally already installed; only the login is per session.


```bash
python -m scout.chatgpt status            # installed? logged in? images used today
./scripts/install_codex.sh                # if not installed (~10 s, pinned version)
tools/codex/node_modules/.bin/codex login --device-auth   # run in background; give the owner the URL + code
```

Login needs the owner: show them `https://auth.openai.com/codex/device` and the one-time code from the output (expires in 15 min). Never ask for their password. Cloud containers are wiped, so each new cloud session logs in again.

## Commands (JSON with `--json`)

```bash
python -m scout.chatgpt research "question" [--json] [--out file.md]
python -m scout.chatgpt ask "task" [--image x.png ...] [--search] [--schema s.json] [--json]
python -m scout.chatgpt image "prompt" --out path.png [--json]
python -m scout.chatgpt image "prompt" --out path.png --ref in.png --source-url URL   # style/reference input
```

| Command | Time (tested 2026-11-26) | Output |
|---|---|---|
| `research` | 8-15 s, uses live web search | markdown answer, `urls` list; copy saved to `data/private/chatgpt/` |
| `ask` (text) | ~12 s | reasoning, writing, critique, second opinion |
| `ask --image` | ~5 s | vision: describe, inspect, QA an image (e.g. text/watermark check before listing) |
| `ask --schema` | ~5 s | JSON that matches a JSON Schema (`--output-schema`), parsed into `data` |
| `ask --search` | ~10 s | any task that may need live web search |
| `image` | 25-35 s, one 1024x1024 PNG | PNG plus `<out>.json` sidecar (prompt, model, time, refs + source URLs) |

`--json` output: ask `{model, text, seconds, data?}`; research `{question, model, text, urls, saved, seconds}`; image `{out, meta, model, seconds}`. Errors go to stderr with exit 2.

Usage is logged (counts only) in `data/private/chatgpt_usage.jsonl`; images stop at `SCOUT_CHATGPT_IMAGE_CAP` (default 20/day) to protect the plan allowance. Run several research questions in parallel (3-4 at once is plenty); Go plan limits are unpublished, so stop on a rate-limit error and report it.

## Rules

- **Recompute every number it gives you.** Pilot 2026-11-26: a margin second opinion got its subtraction wrong by $1 ($24.99 - 9 - 4.25 - 0.40 = 11.34, it said 10.34). Use it for framing and risks; arithmetic goes in code (`scout/margin.py`).

- **Generate images one at a time.** Pilot 2026-11-26: five `image` calls started in parallel returned three byte-identical files (the output of one run landed in two other runs' paths), while an earlier batch of four was fine. Each file looked correct on its own, so compare `md5sum` across outputs and look at every image. Run image calls sequentially (about 40 s each); parallel is fine for `research` and `ask`.

- **Research answers are leads.** Label them `[secondary]`/`[unverified]` until you open the cited URL; keep the URLs (CLAUDE.md research convention). Cross-check decision-driving facts with a second source.
- **No CJ product image goes in as `--ref` to be "placed in a scene".** The model redraws every pixel. Product photos for listings need the Phase 1 compositor: cut out the product, generate only the background here, paste the original pixels back, keep the CJ source URL.
- Never use competitor photos, Google Images or marketplace listing images as `--ref`.
- No text, badges, borders or watermarks in listing images (the wrapper adds this to every prompt).
- Prompts go to OpenAI: no secrets, API keys, customer data or the owner's personal details.
- Keep generated images out of git unless they are docs/UI assets the owner wants; the sidecar JSON travels with the PNG.

## Delegation

Subagent `chatgpt-worker` (Haiku) runs these commands, checks the output and reports. Hand it one research topic or one image brief per call.
