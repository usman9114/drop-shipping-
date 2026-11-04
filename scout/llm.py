"""LLM client: Z.ai GLM Flash first, then Claude Haiku / Sonnet via OpenRouter.

**Phase one is free only** (owner, 2026-11-04): Haiku and Sonnet routes are skipped
unless SCOUT_ALLOW_PAID=1 is set. Owner routing: GLM and OpenRouter Sonnet and Haiku do the work;
Opus is the advisor (planning and review in the Claude Code session), never a
worker here. Order per task: free GLM Flash -> Haiku 5.5 (bulk, vision; about
$0.10/$0.50 per million tokens in/out) or Sonnet 5.5 (reasoning, code; about
$2/$10) -> OpenRouter free models as a last resort. Paid calls draw on the
OpenRouter credit, so GLM stays first.

Falls back on errors or rate limits. Free-tier limits: 20 req/min, and 50 req/day until the account has
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

# "provider:model", ordered by preference. GLM Flash is free (docs.z.ai pricing);
# Claude Haiku/Sonnet are paid OpenRouter routes (ids and prices checked on
# openrouter.ai/api/v1/models 2026-11-04); ":free" models are the last resort.
# Models whose provider key is missing are skipped.
HAIKU = "openrouter:anthropic/claude-haiku-5.5"
SONNET = "openrouter:anthropic/claude-sonnet-5.5"
FREE_MODELS: dict[str, list[str]] = {
    "bulk": [  # fast classification / tagging / extraction
        "zai:glm-4.5-flash",
        HAIKU,
        "openrouter:nvidia/nemotron-3.5-lightning:free",
        "openrouter:google/gemma-4-26b-a4b-it:free",
        "openrouter:liquid/lfm-2.5-2.6b:free",
    ],
    "reasoning": [  # harder analysis, drafting copy
        "zai:glm-4.7-flash",
        SONNET,
        "zai:glm-4.5-flash",
        "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        "openrouter:google/gemma-4-31b-it:free",
    ],
    "code": [  # code drafts; Opus (advisor) reviews before anything is committed
        "zai:glm-4.7-flash",
        SONNET,
        "zai:glm-4.5-flash",
        "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
    ],
    "vision": [  # image QA, image -> attributes
        "zai:glm-4.6v-flash",
        HAIKU,
        "openrouter:nvidia/nemotron-3.5-super-vl:free",
        "openrouter:nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "openrouter:google/gemma-4-31b-it:free",
    ],
    "safety": ["openrouter:nvidia/nemotron-3.5-content-safety:free"],
    "haiku": [HAIKU, "zai:glm-4.5-flash"],  # force Haiku (e.g. a second opinion)
    "sonnet": [SONNET, "zai:glm-4.7-flash"],  # force Sonnet
}
MODELS = FREE_MODELS  # the name predates paid routes; kept for callers


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


def is_paid(spec: str) -> bool:
    """Paid route = a Claude model on OpenRouter. GLM Flash and ':free' models cost nothing."""
    return spec.startswith("openrouter:anthropic/")


def paid_allowed() -> bool:
    """Paid routes are opt-in: set SCOUT_ALLOW_PAID=1 (owner decision, never by default)."""
    return os.environ.get("SCOUT_ALLOW_PAID") == "1"


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


MAX_IMAGE_BYTES = 5_000_000


def _read_image(url: str) -> tuple[bytes, str]:
    """Fetch one image with a size cap. Local files must sit under the working
    directory or the system temp directory; only http(s) URLs are fetched."""
    import mimetypes
    import tempfile
    from pathlib import Path

    if url.startswith(("http://", "https://")):
        req = urllib.request.Request(url, headers={"User-Agent": "dropship-poc-scout"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read(MAX_IMAGE_BYTES + 1)
            mime = resp.headers.get_content_type()
    elif "://" in url:
        raise LLMError(f"unsupported image URL scheme: {url.split('://', 1)[0]}")
    else:
        path = Path(url).resolve()
        roots = [Path.cwd().resolve(), Path(tempfile.gettempdir()).resolve()]
        if not any(path.is_relative_to(r) for r in roots):
            raise LLMError("local images must be under the working or temp directory")
        raw = path.read_bytes()[: MAX_IMAGE_BYTES + 1]
        mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    if len(raw) > MAX_IMAGE_BYTES:
        raise LLMError(f"image larger than {MAX_IMAGE_BYTES} bytes")
    if not mime.startswith("image/"):
        raise LLMError(f"not an image: {mime}")
    return raw, mime


def _inline_images(messages: list[dict]) -> list[dict]:
    """Send images as base64 data URLs (Z.ai can't fetch many URLs itself)."""
    import base64

    out = []
    for msg in messages:
        if not isinstance(msg["content"], list):
            out.append(msg)
            continue
        parts = []
        for part in msg["content"]:
            url = part.get("image_url", {}).get("url", "")
            if part.get("type") == "image_url" and not url.startswith("data:"):
                raw, mime = _read_image(url)
                url = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
                part = {"type": "image_url", "image_url": {"url": url}}
            parts.append(part)
        out.append({**msg, "content": parts})
    return out


def _extract_text(data) -> str | None:
    """Return the reply text, or None when the response is unusable."""
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(text, str) or not text.strip():
        return None
    return text


def chat(
    prompt: str,
    task: str = "bulk",
    image_urls: list[str] | None = None,
    system: str | None = None,
    json_mode: bool = False,
    max_tokens: int = 2048,  # reasoning models spend part of this on hidden thinking
    models: list[str]
    | None = None,  # exact 'provider:model' specs; overrides the task list
) -> dict:
    """Return {'model': ..., 'text': ...}. Tries each free model for the task.

    An empty or malformed reply counts as a failure and falls through to the
    next model."""
    candidates = models or FREE_MODELS[task]
    if not paid_allowed():  # phase one: free models only (owner, 2026-11-04)
        candidates = [m for m in candidates if not is_paid(m)]
    models = [m for m in candidates if _key(m.split(":", 1)[0])]
    if not models:
        need = sorted(
            {v for m in candidates for v in PROVIDERS[m.split(":", 1)[0]]["keys"]}
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
    if image_urls:  # download once, before any provider is tried
        try:
            messages = _inline_images(messages)
        except LLMError:
            raise
        except (OSError, ValueError, urllib.error.URLError) as exc:
            raise LLMError(f"could not load image: {type(exc).__name__}") from exc

    errors = []
    for spec in models:
        provider, model = spec.split(":", 1)
        key = _key(provider)
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
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
            except urllib.error.HTTPError as exc:
                # Error bodies can echo our prompt: keep only a short prefix.
                body = exc.read().decode(errors="replace")[:120]
                errors.append(f"{spec}: HTTP {exc.code} {body}")
                if exc.code in (429, 500, 502, 503) and attempt < 2:
                    time.sleep(5 * (attempt + 1))  # free tiers are often overloaded
                    continue
                break
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                errors.append(f"{spec}: {type(exc).__name__}")
                break
            text = _extract_text(data)
            if text is None:
                errors.append(f"{spec}: empty or malformed reply")
                break
            actual = data.get("model", model) if isinstance(data, dict) else model
            return {"model": f"{provider}:{actual}", "text": text}
    raise LLMError("all free models failed:\n  " + "\n  ".join(errors))


def chat_many(
    prompts: list[str],
    *,
    workers: int = 8,
    task: str = "bulk",
    **kwargs,
) -> list[dict]:
    """Run many prompts in parallel. Returns one dict per prompt, in order:
    {'model', 'text'} on success or {'error': ...} on failure (never raises).

    GLM Flash is free; workers sets how many calls run at once. Each call keeps
    chat()'s own retry and fallback behaviour."""
    from concurrent.futures import ThreadPoolExecutor

    def one(p: str) -> dict:
        err = ""
        for attempt in range(3):  # parallel bursts can hit the provider's rate limit
            try:
                return chat(p, task=task, **kwargs)
            except Exception as exc:  # recorded per prompt, never aborts the batch
                err = f"{type(exc).__name__}: {exc}"[:200]
                if "429" not in err and "rate" not in err.lower():
                    break
                time.sleep(4 * (attempt + 1))
        return {"error": err}

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        return list(ex.map(one, prompts))


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
