"""Free-first LLM client for OpenRouter.

Routes each task type to a list of free models and falls back on errors or
rate limits. Free-tier limits: 20 req/min, and 50 req/day until the account has
bought $10 of credits in total (then 1,000/day). Free routes are NOT private:
never send keys, customer data or contracts.

Usage:
    python -m scout.llm --task bulk "Classify: 'silicone dog bowl' -> category?"
    python -m scout.llm --task vision --image https://... "Any text or watermark?"
    python -m scout.llm --list-free          # show current free models

Env: OPENROUTER_API_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://openrouter.ai/api/v1"

# Ordered by preference. Verified available on 2026-11-03; refresh with --list-free.
FREE_MODELS: dict[str, list[str]] = {
    "bulk": [  # fast classification / tagging / extraction
        "nvidia/nemotron-3.5-lightning:free",
        "google/gemma-4-26b-a4b-it:free",
        "liquid/lfm-2.5-2.6b:free",
    ],
    "reasoning": [  # harder analysis, drafting copy
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3.5-lightning:free",
    ],
    "vision": [  # image QA, image -> attributes
        "nvidia/nemotron-3.5-super-vl:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "google/gemma-4-31b-it:free",
    ],
    "safety": ["nvidia/nemotron-3.5-content-safety:free"],
}


class LLMError(RuntimeError):
    pass


def _post(payload: dict, key: str, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        f"{API}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "dropship-poc-scout",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def chat(
    prompt: str,
    task: str = "bulk",
    image_urls: list[str] | None = None,
    system: str | None = None,
    json_mode: bool = False,
    max_tokens: int = 1024,
) -> dict:
    """Return {'model': ..., 'text': ...}. Tries each free model for the task."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise LLMError("OPENROUTER_API_KEY is not set")
    models = FREE_MODELS[task]

    content: list[dict] | str = prompt
    if image_urls:
        content = [{"type": "text", "text": prompt}] + [
            {"type": "image_url", "image_url": {"url": u}} for u in image_urls
        ]
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": content}
    ]

    errors = []
    for model in models:
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        for attempt in range(2):
            try:
                data = _post(payload, key)
                text = data["choices"][0]["message"]["content"] or ""
                return {"model": data.get("model", model), "text": text}
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")[:300]
                errors.append(f"{model}: HTTP {exc.code} {body}")
                if exc.code == 429 and attempt == 0:
                    time.sleep(4)
                    continue
                break
            except (urllib.error.URLError, KeyError, TimeoutError) as exc:
                errors.append(f"{model}: {exc}")
                break
    raise LLMError("all free models failed:\n  " + "\n  ".join(errors))


def list_free() -> list[dict]:
    with urllib.request.urlopen(f"{API}/models", timeout=30) as resp:
        models = json.loads(resp.read())["data"]
    return [
        {
            "id": m["id"],
            "in": m.get("architecture", {}).get("input_modalities", []),
            "out": m.get("architecture", {}).get("output_modalities", []),
            "ctx": m.get("context_length"),
        }
        for m in models
        if m["id"].endswith(":free")
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Free-first OpenRouter client")
    ap.add_argument("prompt", nargs="?")
    ap.add_argument("--task", choices=sorted(FREE_MODELS), default="bulk")
    ap.add_argument("--image", action="append", help="image URL (repeatable)")
    ap.add_argument("--system")
    ap.add_argument("--json", action="store_true", help="request JSON output")
    ap.add_argument("--list-free", action="store_true")
    args = ap.parse_args(argv)

    if args.list_free:
        for m in list_free():
            print(
                f"{m['id']:60} {','.join(m['in'])} -> {','.join(m['out'])} ctx={m['ctx']}"
            )
        return 0
    if not args.prompt:
        ap.error("prompt required")
    try:
        out = chat(args.prompt, args.task, args.image, args.system, args.json)
    except LLMError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"[model: {out['model']}]", file=sys.stderr)
    print(out["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
