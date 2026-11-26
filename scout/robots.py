"""robots.txt that understands wildcards (RFC 9309), a drop-in for RobotFileParser.

Python's urllib.robotparser treats `*` and `$` in a rule as literal text, so
`Disallow: /collections/*sort_by*` (Shopify's default) is ignored and
`/collections/all?sort_by=best-selling` looks allowed (found 2026-11-22,
decision 0021). Same interface as RobotFileParser: `parse(lines)` and
`can_fetch(user_agent, url)`.

Rules: the group naming our user-agent token wins over `*`; within a group the
longest matching pattern wins and Allow wins a tie; an empty Disallow allows
everything; the match runs against path plus query.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse


def _pattern(path: str) -> re.Pattern:
    anchored = path.endswith("$")
    body = re.escape(path[:-1] if anchored else path).replace(r"\*", ".*")
    return re.compile(body + ("$" if anchored else ""))


class RobotRules:
    def __init__(self) -> None:
        self.groups: list[tuple[list[str], list[tuple[bool, int, re.Pattern]]]] = []

    def parse(self, lines) -> None:
        agents: list[str] = []
        rules: list[tuple[bool, int, re.Pattern]] = []
        in_rules = False
        self.groups = []

        def close() -> None:
            if agents:
                self.groups.append((agents[:], rules[:]))

        for raw in lines:
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            key, value = (x.strip() for x in line.split(":", 1))
            key = key.lower()
            if key == "user-agent":
                if in_rules:
                    close()
                    agents, rules, in_rules = [], [], False
                agents.append(value.lower())
            elif key in ("allow", "disallow"):
                in_rules = True
                if value:  # an empty Disallow allows everything: no rule
                    rules.append((key == "allow", len(value), _pattern(value)))
        close()

    def _rules_for(self, user_agent: str):
        ua = user_agent.lower()
        named = [
            r for names, r in self.groups if any(n != "*" and n in ua for n in names)
        ]
        if named:
            return [x for r in named for x in r]
        return [x for names, r in self.groups if "*" in names for x in r]

    def can_fetch(self, user_agent: str, url: str) -> bool:
        u = urlparse(url)
        target = (u.path or "/") + (f"?{u.query}" if u.query else "")
        best: tuple[int, bool] | None = None
        for allow, length, pat in self._rules_for(user_agent):
            if pat.match(target) and (best is None or (length, allow) > best):
                best = (length, allow)
        return True if best is None else best[1]
