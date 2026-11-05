"""Autopilot entry point: the daily jobs in order, heartbeats and the health check
(docs/plan/autopilot.md rules 1, 8; decision 0016).

    python -m scout.autopilot daily [--only JOB ...] [--force] [--dry-run]
    python -m scout.autopilot health [--max-age-hours 30] [--no-drift]
    python -m scout.autopilot jobs                      # list the job table

Public logs (the repo is public): this module prints through scout.quiet.say()
only, which accepts numbers and short tokens and refuses anything with a dot,
slash or space, so no domain, list or message reaches a log. Each child job's
own output goes to a private log file under data/private/autopilot/logs/
(synced to private storage, never printed, never uploaded as an artifact).

Resumable: every job skips the work it already did (it reads the lake), and the
runner remembers which jobs finished today, so a rerun after a crash or timeout
continues with the first unfinished job. --force reruns them all.

Heartbeat (data/private/lake/_autopilot/heartbeat.json) per job: last start,
last success, status, exit code, seconds, runs and rows added, error rows. Each
daily run also appends one row per job to the lake dataset `autopilot_jobs`.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scout import store
from scout.quiet import exc_token, say

PY = sys.executable or "python3"

# The daily job table: (name, command, timeout in minutes). One place to change.
# Caps keep a run well inside the 6-hour Actions limit; each job resumes the next
# day where it stopped. Discovery is the incremental "new to the list" scan.
JOBS: list[tuple[str, list[str], int]] = [
    ("ranks", [PY, "-m", "scout.stores", "ranks", "--days-back", "1"], 40),
    (
        "discover-new",
        [PY, "-m", "scout.webmeta", "scan-new", "--max-lookups", "100000"],
        60,
    ),
    (
        "meta",
        [
            PY,
            "-m",
            "scout.stores",
            "meta",
            "--max-stores",
            "500",
            "--workers",
            "6",
            "--new-first",
        ],
        45,
    ),
    (
        "light",
        [
            PY,
            "-m",
            "scout.stores",
            "light",
            "--max-stores",
            "300",
            "--workers",
            "6",
            "--new-first",
        ],
        45,
    ),
    ("fingerprints", [PY, "-m", "scout.fingerprints", "--queue", "200"], 60),
    ("build", ["make", "stores-build"], 30),
    ("report", ["make", "stores-report"], 30),
]
DAILY_BUDGET_MIN = 330  # under the 6 h job limit with room for sync and setup

STATE = store.LAKE / "_autopilot"
HEARTBEAT = STATE / "heartbeat.json"
LOGS = Path(os.environ.get("SCOUT_PRIVATE", "data/private")) / "autopilot" / "logs"
LOG_TAIL_BYTES = 256 * 1024

# health thresholds (autopilot.md rule 8)
ERROR_RATE_MAX = 0.10
ERROR_RATE_MIN_ROWS = 20  # fewer rows than this: too small to judge
DRIFT_FACTOR = 2.0
DRIFT_MIN_ROWS = 30  # per week, for the fire-rate comparison
DISK_MAX = 0.80


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def _run_ids() -> set[str]:
    return {r["run_id"] for r in store._runs()}


def _added(before: set[str]) -> tuple[int, int, int]:
    """Runs, rows and error rows written since `before` (from the run log)."""
    runs = rows = errs = 0
    for r in store._runs():
        if r["run_id"] in before:
            continue
        runs += 1
        rows += int(r.get("rows") or 0)
        try:
            with gzip.open(store._checked_path(r), "rt", encoding="utf-8") as fh:
                errs += sum(
                    1 for ln in fh if ln.strip() and json.loads(ln).get("error")
                )
        except (OSError, ValueError):
            pass
    return runs, rows, errs


def _tail_to(log: Path, data: bytes) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_bytes(data[-LOG_TAIL_BYTES:])


def run_job(name: str, cmd: list[str], timeout_min: int, runner=subprocess.run) -> dict:
    """Run one job with its output captured to a private log. Returns counts only."""
    before = _run_ids()
    t0 = time.time()
    status, code = "ok", 0
    try:
        p = runner(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_min * 60,
            check=False,
        )
        code = p.returncode
        out = p.stdout or b""
        if code != 0:
            status = "failed"
    except subprocess.TimeoutExpired as exc:
        status, code, out = "timeout", -1, exc.output or b""
    except Exception as exc:  # e.g. the command is missing
        status, code, out = "failed", -1, exc_token(exc).encode()
    if isinstance(out, str):
        out = out.encode("utf-8", "replace")
    _tail_to(LOGS / _now().strftime("%Y-%m-%d") / f"{name}.log", out)
    runs, rows, errs = _added(before)
    return {
        "job": name,
        "status": status,
        "exit": code,
        "seconds": round(time.time() - t0, 1),
        "runs_added": runs,
        "rows_added": rows,
        "error_rows": errs,
    }


def daily(
    only: list[str] | None = None,
    force: bool = False,
    dry_run: bool = False,
    jobs=None,
    runner=subprocess.run,
) -> int:
    jobs = jobs if jobs is not None else JOBS
    today = _now().strftime("%Y-%m-%d")
    state_file = STATE / f"daily-{today}.json"
    state = {} if force else _read_json(state_file, {})
    hb = _read_json(HEARTBEAT, {"jobs": {}})
    hb.setdefault("jobs", {})
    hb["daily_last_start"] = _now().isoformat(timespec="seconds")
    deadline = time.time() + DAILY_BUDGET_MIN * 60
    results, failed = [], 0
    for name, cmd, tmin in jobs:
        if only and name not in only:
            continue
        if state.get(name) == "ok":
            say("job", job=name, status="done-today")
            continue
        if dry_run:
            say("job", job=name, status="would-run", timeout_min=tmin)
            continue
        left = int((deadline - time.time()) / 60)
        if left < 5:
            say("job", job=name, status="no-time-left")
            failed += 1
            continue
        start = _now().isoformat(timespec="seconds")
        res = run_job(name, cmd, min(tmin, left), runner=runner)
        results.append(res)
        state[name] = res["status"]
        _write_json(state_file, state)
        j = hb["jobs"].setdefault(name, {})
        j.update({k: res[k] for k in res if k != "job"})
        j["last_start"] = start
        if res["status"] == "ok":
            j["last_success"] = _now().isoformat(timespec="seconds")
        else:
            failed += 1
        _write_json(HEARTBEAT, hb)
        say("job", **res)
    if dry_run:
        return 0
    if results:
        store.record_run(
            "autopilot_jobs",
            [{**r, "day": today} for r in results],
            source="autopilot",
            trust="data",
            params={"jobs": len(results), "failed": failed},
            note="one row per job per daily run: status and counts only",
        )
    if not failed:
        hb["daily_last_success"] = _now().isoformat(timespec="seconds")
    _write_json(HEARTBEAT, hb)
    say("daily", jobs=len(results), failed=failed)
    return 1 if failed else 0


# --------------------------------------------------------------------------- health


def _week_rates(rows_by_week: dict[str, list[set[str]]]) -> dict[str, dict[str, float]]:
    out = {}
    for week, rows in rows_by_week.items():
        n = len(rows)
        cnt = Counter(s for r in rows for s in r)
        out[week] = {s: cnt[s] / n for s in cnt} | {"_n": n}
    return out


def drift(rows: list[dict], today: datetime | None = None) -> list[str]:
    """Signals whose fire rate changed more than DRIFT_FACTOR between the last two
    7-day windows. A row is {"day": "YYYY-MM-DD", "signals": [...]}."""
    today = today or _now()
    this_w, last_w = [], []
    for r in rows:
        try:
            d = datetime.fromisoformat(r["day"]).replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue
        age = (today - d).days
        if 0 <= age < 7:
            this_w.append(set(r.get("signals") or []))
        elif 7 <= age < 14:
            last_w.append(set(r.get("signals") or []))
    if len(this_w) < DRIFT_MIN_ROWS or len(last_w) < DRIFT_MIN_ROWS:
        return []
    a = _week_rates({"a": this_w})["a"]
    b = _week_rates({"b": last_w})["b"]
    out = []
    for s in sorted((set(a) | set(b)) - {"_n"}):
        ra, rb = a.get(s, 0.0), b.get(s, 0.0)
        hi, lo = max(ra, rb), min(ra, rb)
        # a signal seen in at least 5% of either week, changing more than 2x
        if hi >= 0.05 and (lo == 0 or hi / lo > DRIFT_FACTOR):
            out.append(s)
    return out


def _fingerprint_signal_rows() -> list[dict]:
    rows = []
    for run in store._runs():
        if run["dataset"] != "web_fingerprints":
            continue
        day = run["run_id"][:4] + "-" + run["run_id"][4:6] + "-" + run["run_id"][6:8]
        try:
            with gzip.open(store._checked_path(run), "rt", encoding="utf-8") as fh:
                for ln in fh:
                    if not ln.strip():
                        continue
                    r = json.loads(ln)
                    if r.get("error"):
                        continue
                    sig = (r.get("page") or {}).get("signature_ids") or []
                    rows.append({"day": day, "signals": sig})
        except (OSError, ValueError):
            continue
    return rows


def health(
    max_age_hours: float = 30.0,
    now: datetime | None = None,
    disk_path: str = ".",
    signal_rows=None,
) -> tuple[int, list[tuple[str, str]]]:
    """Check heartbeats; return (exit code, [(alert, subject token)]). Prints
    alert codes and job or signal ids only."""
    now = now or _now()
    hb = _read_json(HEARTBEAT, None)
    alerts: list[tuple[str, str]] = []
    if hb is None:
        alerts.append(("no-heartbeat", "daily"))
    else:
        last = hb.get("daily_last_start")
        if not last or now - datetime.fromisoformat(last) > timedelta(
            hours=max_age_hours
        ):
            alerts.append(("missed-window", "daily"))
        for name, _cmd, _t in JOBS:
            j = hb.get("jobs", {}).get(name)
            if not j:
                alerts.append(("never-ran", name))
                continue
            ok = j.get("last_success")
            if not ok or now - datetime.fromisoformat(ok) > timedelta(
                hours=max_age_hours
            ):
                alerts.append(("stale-job", name))
            rows = int(j.get("rows_added") or 0)
            if (
                rows >= ERROR_RATE_MIN_ROWS
                and int(j.get("error_rows") or 0) / rows > ERROR_RATE_MAX
            ):
                alerts.append(("error-rate", name))
    rows = signal_rows if signal_rows is not None else _fingerprint_signal_rows()
    for s in drift(rows, now):
        alerts.append(("signal-drift", s))
    du = shutil.disk_usage(disk_path)
    if du.used / du.total > DISK_MAX:
        alerts.append(("disk", "high"))
    return (1 if alerts else 0), alerts


def _safe_token(s: str) -> str:
    import re

    t = re.sub(r"[^a-z0-9_-]", "-", s.lower())[:48].strip("-")
    return t or "unnamed"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Autopilot: daily jobs and health check")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("daily")
    d.add_argument("--only", nargs="+", choices=[j[0] for j in JOBS])
    d.add_argument("--force", action="store_true", help="rerun jobs done today")
    d.add_argument("--dry-run", action="store_true")
    h = sub.add_parser("health")
    h.add_argument("--max-age-hours", type=float, default=30.0)
    h.add_argument(
        "--no-drift",
        action="store_true",
        help="heartbeat only (when the fingerprint rows were not pulled)",
    )
    sub.add_parser("jobs")
    a = ap.parse_args(argv)
    if a.cmd == "jobs":
        for name, _cmd, tmin in JOBS:
            say("job", job=name, timeout_min=tmin)
        return 0
    if a.cmd == "daily":
        return daily(a.only, a.force, a.dry_run)
    code, alerts = health(a.max_age_hours, signal_rows=[] if a.no_drift else None)
    for kind, subject in alerts:
        say("alert", kind=kind, subject=_safe_token(subject))
    _write_json(
        STATE / "health.json",
        {
            "checked_at": _now().isoformat(timespec="seconds"),
            "alerts": [list(x) for x in alerts],
        },
    )
    say("health", alerts=len(alerts))
    return code


if __name__ == "__main__":
    sys.exit(main())
