"""Public-log guard for the autopilot (decision 0016: the repo is public, so are
GitHub Actions logs).

Everything the autopilot entry points print goes through `say()`. It prints one
line of `event key=value ...` and only accepts numbers, booleans and short
lowercase tokens without dots, slashes, `@` or spaces. A domain, URL, e-mail,
file path or exception message cannot pass, so a store list cannot leak into a
log by accident. Free text from child jobs goes to private log files instead.
"""

from __future__ import annotations

import re
import sys

# a token: lowercase letters, digits, - and _ only; no dot means no domain or URL
TOKEN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")


class LeakError(ValueError):
    """A value that could carry a name, domain or path was passed to say()."""


def _ok(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(round(value, 3)) if isinstance(value, float) else str(value)
    if value is None:
        return "none"
    if isinstance(value, str) and TOKEN.match(value):
        return value
    raise LeakError("say() takes numbers, booleans and short lowercase tokens only")


def line(event: str, **fields) -> str:
    parts = [_ok(event)]
    for k, v in fields.items():
        parts.append(f"{_ok(k.lower())}={_ok(v)}")
    return " ".join(parts)


def say(event: str, **fields) -> None:
    """Print one public-safe line to stdout."""
    print(line(event, **fields), file=sys.stdout, flush=True)


def exc_token(exc: BaseException) -> str:
    """An exception as a safe token: its class name only, never its message."""
    name = re.sub(r"[^a-z0-9_-]", "", type(exc).__name__.lower())
    return name[:48] or "error"
