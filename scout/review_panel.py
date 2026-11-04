"""Review panel: several different free models judge every idea against the
project brief. Deterministic inputs (docs/plan/ideas.yml), structured outputs,
cached answers, a vote tally and a disagreement flag.

The panel advises; it does not decide. A unanimous "drop" or a split vote is a
prompt for the owner and the main session to look again.

Usage:
    python -m scout.review_panel                # all ideas, default panel
    python -m scout.review_panel --ideas I06 I08
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
from datetime import date
from pathlib import Path

IDEAS = Path("docs/plan/ideas.yml")
CACHE = Path("docs/reviews/panel/cache.jsonl")
PROMPT_VERSION = "panel-v1"
PANEL = [
    "zai:glm-4.7-flash",
    "zai:glm-4.5-flash",
    "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter:google/gemma-4-31b-it:free",
]
VERDICTS = {"keep", "modify", "drop"}
SCORES = ("relevance", "evidence", "value_for_effort", "compliance_safety")

SYSTEM = (
    "You are a skeptical reviewer for a small e-commerce experiment. You judge "
    "ideas strictly against the brief. You prefer cheap, decisive tests and you "
    "say plainly when an idea does not serve the goal."
)
PROMPT = """PROJECT BRIEF
{brief}

IDEA {id}: {title}
{description}

Judge whether this idea makes sense for THIS project. Score each 1-5:
- relevance: does it directly help prove or disprove the GOAL?
- evidence: is it backed by the FACTS, or is it an untested assumption?
- value_for_effort: is the benefit worth the work under C4 and C6?
- compliance_safety: does it stay within C3, C5 and C8? (5 = clearly safe)

Return ONLY a JSON object, no prose:
{{"verdict": "keep|modify|drop", "relevance": n, "evidence": n,
  "value_for_effort": n, "compliance_safety": n,
  "constraints": ["C1", "F3"],
  "reason": "one sentence",
  "risk": "the biggest risk, one sentence",
  "cheapest_test": "the cheapest test that would settle it, one sentence"}}"""


def load_ideas(path: Path = IDEAS) -> tuple[str, list[dict]]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["brief"], data["ideas"]


def cache_key(brief: str, idea: dict, model: str) -> str:
    blob = json.dumps([brief, idea, model, PROMPT_VERSION], sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def parse_review(text: str) -> dict | None:
    """Extract and validate the JSON verdict; None when unusable."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        r = json.loads(m.group(0))
    except ValueError:
        return None
    if str(r.get("verdict", "")).lower() not in VERDICTS:
        return None
    r["verdict"] = r["verdict"].lower()
    for k in SCORES:
        try:
            v = int(r.get(k))
        except (TypeError, ValueError):
            return None
        if not 1 <= v <= 5:
            return None
        r[k] = v
    r["constraints"] = [
        c for c in (r.get("constraints") or []) if re.fullmatch(r"[CF]\d{1,2}", str(c))
    ]
    for k in ("reason", "risk", "cheapest_test"):
        r[k] = " ".join(str(r.get(k) or "").split())[:300]
    return r


def load_cache(path: Path = CACHE) -> dict[str, dict]:
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["key"]] = row
    return out


def append_cache(rows: list[dict], path: Path = CACHE) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


def tally(reviews: list[dict]) -> dict:
    """Votes, mean scores and a disagreement flag for one idea."""
    votes = {
        v: sum(1 for r in reviews if r["verdict"] == v)
        for v in ("keep", "modify", "drop")
    }
    n = len(reviews)
    means = {
        k: round(statistics.mean(r[k] for r in reviews), 1) if n else None
        for k in SCORES
    }
    top = max(votes.values()) if n else 0
    return {
        "n": n,
        "votes": votes,
        "means": means,
        "consensus": next(
            (v for v, c in votes.items() if n and c == top and c > n / 2), None
        ),
        "split": n > 1 and top <= n / 2,
    }


def review(
    ideas: list[dict], brief: str, panel: list[str], chat
) -> dict[str, list[dict]]:
    cache = load_cache()
    out: dict[str, list[dict]] = {}
    new = []
    for idea in ideas:
        out[idea["id"]] = []
        for model in panel:
            key = cache_key(brief, idea, model)
            hit = cache.get(key)
            if hit:
                out[idea["id"]].append(hit)
                continue
            try:
                reply = chat(
                    PROMPT.format(brief=brief, **idea),
                    system=SYSTEM,
                    models=[model],
                    max_tokens=900,
                )
                parsed = parse_review(reply["text"])
            except Exception as exc:  # one failed reviewer does not stop the panel
                print(f"  {idea['id']} {model}: {type(exc).__name__}", file=sys.stderr)
                continue
            if parsed is None:
                print(f"  {idea['id']} {model}: unusable answer", file=sys.stderr)
                continue
            row = {"key": key, "idea": idea["id"], "model": model, **parsed}
            new.append(row)
            cache[key] = row
            out[idea["id"]].append(row)
        print(
            f"  {idea['id']}: {len(out[idea['id']])}/{len(panel)} reviews",
            file=sys.stderr,
        )
    append_cache(new)
    return out


def render(ideas: list[dict], results: dict[str, list[dict]], today: str) -> str:
    lines = [
        f"# Idea review panel — {today}",
        "",
        "> Generated by `python -m scout.review_panel` from `docs/plan/ideas.yml`. Each idea is "
        "judged independently by several free models against the same brief and rubric "
        "(scores 1–5). Advisory only: a split vote or a drop consensus is a prompt to look "
        "again, not a decision.",
        "",
        "| Idea | Keep | Modify | Drop | Consensus | Relevance | Evidence | Value/effort | Compliance |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for idea in ideas:
        t = tally(results.get(idea["id"], []))
        m = t["means"]
        cons = t["consensus"] or ("**split**" if t["split"] else "–")
        lines.append(
            f"| {idea['id']} {idea['title']} | {t['votes']['keep']} | {t['votes']['modify']} | "
            f"{t['votes']['drop']} | {cons} | {m['relevance']} | {m['evidence']} | "
            f"{m['value_for_effort']} | {m['compliance_safety']} |"
        )
    lines.append("")
    for idea in ideas:
        lines += [f"## {idea['id']} — {idea['title']}", "", idea["description"], ""]
        for r in results.get(idea["id"], []):
            lines.append(
                f"- **{r['model'].split(':', 1)[1]}** — {r['verdict']} "
                f"({', '.join(r['constraints']) or 'no refs'}): {r['reason']} "
                f"*Risk:* {r['risk']} *Cheapest test:* {r['cheapest_test']}"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Free-model review panel for project ideas"
    )
    ap.add_argument("--ideas", nargs="*", help="idea ids (default: all)")
    ap.add_argument("--panel", nargs="*", default=PANEL, help="provider:model specs")
    ap.add_argument(
        "--out", help="report path (default docs/reviews/<date>-idea-panel.md)"
    )
    a = ap.parse_args(argv)
    brief, ideas = load_ideas()
    if a.ideas:
        ideas = [i for i in ideas if i["id"] in set(a.ideas)]
    from scout.llm import chat

    results = review(ideas, brief, a.panel, chat)
    today = date.today().isoformat()
    out = Path(a.out or f"docs/reviews/{today}-idea-panel.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(ideas, results, today) + "\n", encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
