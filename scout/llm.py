"""Free-first LLM client (Z.ai GLM Flash + OpenRouter free models).

Routes each task type to a list of free models and falls back on errors or
rate limits. Free-tier limits: 20 req/min, and 50 req/day until the account has
bought $10 of credits in total (then 1,000/day). Free routes are NOT private:
never send keys, customer data or contracts.

Usage:
    python -m scout.llm --task bulk "Classify: 'silicone dog bowl' -> category?"
    python -m scout.llm --task vision --image https://... "Any text or watermark?"
    python -m scout.llm --list-free          # show current free models

Env: ZAI_API_KEY (Z.ai GLM Flash, free) and/or OPENROUTER_API_KEY
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

# Providers: OpenAI-compatible chat endpoints. Key env vars are tried in order.
PROVIDERS = {
    "openrouter": {"base": API, "keys": ["OPENROUTER_API_KEY"]},
    "zai": {
        "base": "https://api.z.ai/api/paas/v4",
        "keys": ["ZAI_API_KEY", "ZAI_KEY", "Z_AI_API_KEY", "ZHIPUAI_API_KEY"],
    },
}

# "provider:model", ordered by preference. All free (OpenRouter ":free" verified
# 2026-11-03; Z.ai Flash models listed as Free on docs.z.ai pricing). Models whose
# provider key is missing are skipped.
FREE_MODELS: dict[str, list[str]] = {
    "bulk": [  # fast classification / tagging / extraction
        "zai:glm-4.5-flash",
        "openrouter:nvidia/nemotron-3.5-lightning:free",
        "openrouter:google/gemma-4-26b-a4b-it:free",
        "openrouter:liquid/lfm-2.5-2.6b:free",
    ],
    "reasoning": [  # harder analysis, drafting copy
        "zai:glm-4.7-flash",
        "zai:glm-4.5-flash",
        "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        "openrouter:google/gemma-4-31b-it:free",
    ],
    "code": [  # code drafts; Claude reviews before anything is committed
        "zai:glm-4.7-flash",
        "zai:glm-4.5-flash",
        "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
    ],
    "vision": [  # image QA, image -> attributes
        "zai:glm-4.6v-flash",
        "openrouter:nvidia/nemotron-3.5-super-vl:free",
        "openrouter:nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "openrouter:google/gemma-4-31b-it:free",
    ],
    "safety": ["openrouter:nvidia/nemotron-3.5-content-safety:free"],
}


def _load_dotenv(path: str = ".env") -> None:
    """Load KEY=VALUE lines from .env without overriding the real environment."""
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except OSError:
        pass


_load_dotenv()


class LLMError(RuntimeError):
    pass


def _key(provider: str) -> str | None:
    for var in PROVIDERS[provider]["keys"]:
        if os.environ.get(var):
            return os.environ[var]
    return None


def _post(payload: dict, provider: str, key: str, timeout: int = 180) -> dict:
    req = urllib.request.Request(
        f"{PROVIDERS[provider]['base']}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "dropship-poc-scout",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _inline_images(messages: list[dict]) -> list[dict]:
    """Z.ai can't fetch many image URLs itself; send them as base64 data URLs."""
    import base64
    import mimetypes

    out = []
    for msg in messages:
        if not isinstance(msg["content"], list):
            out.append(msg)
            continue
        parts = []
        for part in msg["content"]:
            url = part.get("image_url", {}).get("url", "")
            if part.get("type") == "image_url" and not url.startswith("data:"):
                if url.startswith(("http://", "https://")):
                    req = urllib.request.Request(
                        url, headers={"User-Agent": "dropship-poc-scout"}
                    )
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        raw = resp.read()
                        mime = resp.headers.get_content_type()
                else:  # local file path
                    with open(url, "rb") as fh:
                        raw = fh.read()
                    mime = mimetypes.guess_type(url)[0] or "image/jpeg"
                url = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
                part = {"type": "image_url", "image_url": {"url": url}}
            parts.append(part)
        out.append({**msg, "content": parts})
    return out


def chat(
    prompt: str,
    task: str = "bulk",
    image_urls: list[str] | None = None,
    system: str | None = None,
    json_mode: bool = False,
    max_tokens: int = 1024,
) -> dict:
    """Return {'model': ..., 'text': ...}. Tries each free model for the task."""
    models = [m for m in FREE_MODELS[task] if _key(m.split(":", 1)[0])]
    if not models:
        need = sorted(
            {
                v
                for m in FREE_MODELS[task]
                for v in PROVIDERS[m.split(":", 1)[0]]["keys"]
            }
        )
        raise LLMError(f"no API key set for task {task!r}; set one of {need}")

    content: list[dict] | str = prompt
    if image_urls:
        content = [{"type": "text", "text": prompt}] + [
            {"type": "image_url", "image_url": {"url": u}} for u in image_urls
        ]
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": content}
    ]

    errors = []
    for spec in models:
        provider, model = spec.split(":", 1)
        key = _key(provider)
        msgs = (
            _inline_images(messages) if provider == "zai" and image_urls else messages
        )
        payload = {"model": model, "messages": msgs, "max_tokens": max_tokens}
        if provider == "zai":
            # GLM Flash models think by default and can spend the whole token
            # budget on hidden reasoning; keep it off except for reasoning tasks.
            if task == "reasoning":
                payload["max_tokens"] = max(max_tokens, 4096)
            else:
                payload["thinking"] = {"type": "disabled"}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        for attempt in range(3):
            try:
                data = _post(payload, provider, key)
                text = data["choices"][0]["message"]["content"] or ""
                return {"model": f"{provider}:{data.get('model', model)}", "text": text}
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")[:300]
                errors.append(f"{spec}: HTTP {exc.code} {body}")
                if exc.code in (429, 500, 502, 503) and attempt < 2:
                    time.sleep(5 * (attempt + 1))  # free tiers are often overloaded
                    continue
                break
            except (urllib.error.URLError, KeyError, TimeoutError) as exc:
                errors.append(f"{spec}: {exc}")
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
