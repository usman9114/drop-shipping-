#!/usr/bin/env python3
"""commit-msg hook: reject commits that carry AI-assistant attribution.

Project rule: commits are authored by the human owner only. This blocks
Co-Authored-By trailers, session links and "Generated with" footers that
name an AI assistant, and an author/committer identity that is not a person.
"""

from __future__ import annotations

import re
import subprocess
import sys

MESSAGE_PATTERNS = [
    r"co-authored-by:.*\b(claude|anthropic|copilot|chatgpt|openai|gemini|cursor)\b",
    r"\bclaude-session:",
    r"generated (with|by) \[?(claude|copilot|chatgpt|cursor)",
    r"noreply@anthropic\.com",
    r"claude\.(ai|com)/code",
]

IDENTITY_PATTERN = re.compile(r"(^claude\b|anthropic\.com|^copilot\b)", re.IGNORECASE)


def git_ident(var: str) -> str:
    try:
        out = subprocess.run(
            ["git", "var", var], capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    # "Name <email> timestamp tz" -> "Name <email>"
    return out.rsplit(" ", 2)[0].strip()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: check_no_ai_attribution.py <commit-msg-file>", file=sys.stderr)
        return 2

    with open(argv[1], encoding="utf-8", errors="replace") as fh:
        lines = [ln for ln in fh.read().splitlines() if not ln.startswith("#")]
    message = "\n".join(lines)

    problems: list[str] = []
    for pattern in MESSAGE_PATTERNS:
        for match in re.finditer(pattern, message, re.IGNORECASE | re.MULTILINE):
            problems.append(
                f"commit message contains AI attribution: {match.group(0)!r}"
            )

    for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        ident = git_ident(var)
        if ident and IDENTITY_PATTERN.search(ident):
            problems.append(
                f"{var} is {ident!r}; set your own identity with "
                "`git config user.name` / `git config user.email`"
            )

    if problems:
        print(
            "Commit rejected (no AI attribution allowed in this repo):", file=sys.stderr
        )
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
