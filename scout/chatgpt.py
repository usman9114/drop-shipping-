"""ChatGPT lane: research and image generation through the owner's ChatGPT plan.

Wraps OpenAI Codex CLI (`codex exec`, Apache-2.0) signed in with the owner's ChatGPT
account (Go plan, owner 2026-11-26). No API key, no per-call billing: usage comes
out of the plan's Codex allowance (images use it 3-5x faster). Decision 0019.

    python -m scout.chatgpt status                      # installed? logged in?
    python -m scout.chatgpt research "question" [--json] [--out file.md]
    python -m scout.chatgpt ask "task" [--image x.png] [--search] [--schema s.json] [--json]
    python -m scout.chatgpt image "prompt" --out path.png [--ref img --source-url URL] [--json]

Rules (CLAUDE.md):
- Research answers are [unverified] leads until a source URL is checked; keep the URLs.
- Images: scenes, backgrounds, diagrams, mood boards. NEVER pass a CJ product image as
  --ref to "put it in a scene": the model redraws every pixel, which breaks the
  product-pixels-untouched rule. Product compositing (cut out product, generate
  background here, paste original pixels back) is a Phase 1 job.
- Never pass competitors' or Google Images photos as --ref.
- Every image gets a sidecar <out>.json with prompt, model, time, refs and source URLs.
- No secrets or personal data in prompts: prompts leave the repo for OpenAI.

Setup per container: ./scripts/install_codex.sh, then
`tools/codex/node_modules/.bin/codex login --device-auth` (owner enters the code).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODEX = ROOT / "tools" / "codex" / "node_modules" / ".bin" / "codex"
LOG_DIR = ROOT / "data" / "private" / "chatgpt"
USAGE = ROOT / "data" / "private" / "chatgpt_usage.jsonl"
DAILY_IMAGE_CAP = int(os.environ.get("SCOUT_CHATGPT_IMAGE_CAP", "20"))


class ChatGPTError(RuntimeError):
    pass


def _codex() -> str:
    if CODEX.exists():
        return str(CODEX)
    found = shutil.which("codex")
    if found:
        return found
    raise ChatGPTError("Codex CLI not installed: run ./scripts/install_codex.sh")


def status() -> dict:
    try:
        exe = _codex()
    except ChatGPTError as e:
        return {"installed": False, "logged_in": False, "detail": str(e)}
    ver = subprocess.run(
        [exe, "--version"], capture_output=True, text=True
    ).stdout.strip()
    st = subprocess.run([exe, "login", "status"], capture_output=True, text=True)
    out = (st.stdout + st.stderr).strip()
    return {
        "installed": True,
        "version": ver,
        "logged_in": st.returncode == 0 and "Logged in" in out,
        "detail": out,
        "images_today": _count_today("image"),
        "image_cap": DAILY_IMAGE_CAP,
    }


def _count_today(kind: str) -> int:
    if not USAGE.exists():
        return 0
    today = dt.date.today().isoformat()
    n = 0
    for line in USAGE.read_text().splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("kind") == kind and r.get("date") == today and r.get("ok"):
            n += 1
    return n


def _record(kind: str, ok: bool, seconds: float, model: str | None) -> None:
    USAGE.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "date": dt.date.today().isoformat(),
        "kind": kind,
        "ok": ok,
        "seconds": round(seconds, 1),
        "model": model,
    }
    with USAGE.open("a") as f:
        f.write(json.dumps(row) + "\n")


def _model_from_log(log: str) -> str | None:
    m = re.search(r"^model:\s*(\S+)", log, re.M)
    return m.group(1) if m else None


def _run(
    prompt: str,
    *,
    cwd: Path,
    sandbox: str,
    search: bool,
    images: list[str],
    timeout: int,
    schema: str | None = None,
) -> tuple[str, str]:
    """Run one `codex exec`; return (final message, full log)."""
    last = cwd / ".last_message.md"
    cmd = [
        _codex(),
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "-s",
        sandbox,
        "-C",
        str(cwd),
        "-o",
        str(last),
    ]
    if search:
        cmd += ["-c", "tools.web_search=true"]
    for img in images:
        cmd += ["-i", img]
    if schema:
        cmd += ["--output-schema", schema]
    cmd.append(prompt)
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as e:
        raise ChatGPTError(f"codex timed out after {timeout}s") from e
    log = p.stdout + p.stderr
    if p.returncode != 0:
        tail = "\n".join(log.strip().splitlines()[-8:])
        raise ChatGPTError(f"codex exit {p.returncode}: {tail}")
    msg = last.read_text().strip() if last.exists() else ""
    return msg, log


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower())[:50].strip("-") or "q"


def ask(
    prompt: str,
    images: list[str] | None = None,
    search: bool = False,
    schema: str | None = None,
    timeout: int = 600,
) -> dict:
    """General task: reasoning, writing, vision (images in), structured JSON (schema).

    Read-only sandbox: the model can think, search (if asked) and look at images, but
    cannot write files or run commands that change anything.
    """
    imgs = [str(Path(i).resolve()) for i in (images or [])]
    schema_path = str(Path(schema).resolve()) if schema else None
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            text, log = _run(
                prompt,
                cwd=Path(tmp),
                sandbox="read-only",
                search=search,
                images=imgs,
                timeout=timeout,
                schema=schema_path,
            )
        except ChatGPTError:
            _record("ask", False, time.time() - t0, None)
            raise
    model = _model_from_log(log)
    _record("ask", True, time.time() - t0, model)
    out: dict = {"model": model, "text": text, "seconds": round(time.time() - t0, 1)}
    if schema_path:
        try:
            out["data"] = json.loads(text)
        except json.JSONDecodeError as e:
            raise ChatGPTError(f"schema output was not JSON: {text[:200]}") from e
    return out


def research(question: str, timeout: int = 600) -> dict:
    """Web research answer with source URLs. Saved under data/private/chatgpt/."""
    prompt = (
        "Use web search. Answer concisely in markdown. Every factual claim needs a source "
        "URL in the same bullet. Prefer primary sources (official sites, docs, filings). "
        "Say plainly when something could not be verified.\n\nQuestion: " + question
    )
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            text, log = _run(
                prompt,
                cwd=Path(tmp),
                sandbox="read-only",
                search=True,
                images=[],
                timeout=timeout,
            )
        except ChatGPTError:
            _record("research", False, time.time() - t0, None)
            raise
    model = _model_from_log(log)
    _record("research", True, time.time() - t0, model)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = LOG_DIR / f"{stamp}-{_slug(question)}.md"
    path.write_text(
        f"<!-- chatgpt research, model={model}, {stamp} -->\n# {question}\n\n{text}\n"
    )
    return {
        "question": question,
        "model": model,
        "text": text,
        "urls": sorted(set(re.findall(r"https?://[^\s)\]>]+", text))),
        "saved": str(path),
        "seconds": round(time.time() - t0, 1),
    }


def image(
    prompt: str,
    out: str,
    refs: list[str] | None = None,
    source_urls: list[str] | None = None,
    timeout: int = 900,
) -> dict:
    """Generate one image (gpt-image via Codex $imagegen) to `out`, with a sidecar JSON."""
    refs = refs or []
    source_urls = source_urls or []
    if refs and len(source_urls) != len(refs):
        raise ChatGPTError(
            "every --ref needs a matching --source-url (provenance rule)"
        )
    if _count_today("image") >= DAILY_IMAGE_CAP:
        raise ChatGPTError(
            f"daily image cap {DAILY_IMAGE_CAP} reached "
            "(SCOUT_CHATGPT_IMAGE_CAP to change, owner decision)"
        )
    out_path = Path(out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        full = (
            "$imagegen "
            + prompt.strip()
            + "\nNo text, letters, logos, watermarks, badges or borders unless asked. "
            "Save exactly one PNG named result.png in the current directory."
        )
        try:
            msg, log = _run(
                full,
                cwd=Path(tmp),
                sandbox="workspace-write",
                search=False,
                images=[str(Path(r).resolve()) for r in refs],
                timeout=timeout,
            )
            pngs = sorted(Path(tmp).glob("*.png"), key=lambda p: p.stat().st_mtime)
            if not pngs:
                raise ChatGPTError(f"no image produced; model said: {msg[:300]}")
            shutil.move(str(pngs[-1]), out_path)
        except ChatGPTError:
            _record("image", False, time.time() - t0, None)
            raise
    model = _model_from_log(log)
    _record("image", True, time.time() - t0, model)
    meta = {
        "prompt": prompt,
        "driver_model": model,
        "image_model": "gpt-image via codex $imagegen",
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "refs": [{"path": r, "source_url": u} for r, u in zip(refs, source_urls)],
        "tool": "scout.chatgpt (codex exec, ChatGPT plan)",
        "note": "AI-generated. Not a product photo.",
    }
    Path(str(out_path) + ".json").write_text(json.dumps(meta, indent=2) + "\n")
    return {
        "out": str(out_path),
        "meta": str(out_path) + ".json",
        "model": model,
        "seconds": round(time.time() - t0, 1),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m scout.chatgpt",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    r = sub.add_parser("research")
    r.add_argument("question")
    r.add_argument("--out")
    r.add_argument("--json", action="store_true")
    k = sub.add_parser(
        "ask", help="general task: reasoning, vision (--image), JSON (--schema)"
    )
    k.add_argument("prompt")
    k.add_argument("--image", action="append", default=[])
    k.add_argument("--search", action="store_true", help="allow live web search")
    k.add_argument("--schema", help="JSON Schema file; answer must match it")
    k.add_argument("--json", action="store_true")
    i = sub.add_parser("image")
    i.add_argument("prompt")
    i.add_argument("--out", required=True)
    i.add_argument("--ref", action="append", default=[])
    i.add_argument("--source-url", action="append", default=[])
    i.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "status":
            print(json.dumps(status(), indent=2))
            return 0
        if a.cmd == "research":
            res = research(a.question)
            if a.out:
                Path(a.out).write_text(res["text"] + "\n")
            print(json.dumps(res, indent=2) if a.json else res["text"])
            return 0
        if a.cmd == "ask":
            res = ask(a.prompt, a.image, a.search, a.schema)
            print(json.dumps(res, indent=2) if a.json else res.get("data", res["text"]))
            return 0
        res = image(a.prompt, a.out, a.ref, a.source_url)
        print(json.dumps(res, indent=2) if a.json else res["out"])
        return 0
    except ChatGPTError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
