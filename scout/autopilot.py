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
# Caps keep a run well inside the 6-hour Actions limit (tests/test_autopilot.py
# checks that the timeouts sum to under 6 h); each job resumes the next day where
# it stopped. Discovery is the incremental "new to the list" scan.
#
# Rate limits: Shopify throttles (HTTP 429) across all stores per user agent, and
# six parallel workers triggered it in the Pakistan runs. US meta and light run 3
# workers with a 2 s pause. Pakistan jobs run 1 worker, 5 s pause (the tested safe
# setting); a 429 is not counted as a store failure, so it is retried next day.
#
# Time maths, one-worker Pakistan jobs at about 7 s a store (robots.txt, 5 s
# pause, one request) and 12 s for best (two paced requests):
#   pk-meta   150 stores = 17.5 min   cap 25
#   pk-light  200 stores = 23 min     cap 25
#   pk-home   120 stores = 14 min     cap 20
#   pk-best   100 stores = 20 min     cap 25
#   pk-discover is DNS only, no site requests: cap 15
# Typical day (observed US jobs about 6 min, Pakistan about 80 min) is far inside
# the 330 min budget; the timeouts sum to 305 so even a worst case fits.
JOBS: list[tuple[str, list[str], int]] = [
    ("ranks", [PY, "-m", "scout.stores", "ranks", "--days-back", "1"], 20),
    (
        "discover-new",
        [PY, "-m", "scout.webmeta", "scan-new", "--max-lookups", "100000"],
        30,
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
            "3",
            "--pause",
            "2",
            "--new-first",
        ],
        30,
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
            "3",
            "--pause",
            "2",
            "--new-first",
        ],
        30,
    ),
    ("fingerprints", [PY, "-m", "scout.fingerprints", "--queue", "200"], 45),
    # Pakistan market (decisions 0019 to 0021). CrUX popularity is pulled once a
    # month (a quiet no-op without Google credentials), then new origins are
    # DNS-checked for Shopify, then read slowly.
    ("crux", [PY, "-m", "scout.autopilot", "crux"], 10),
    (
        "pk-discover",
        [PY, "-m", "scout.crux", "discover", "--country", "pk", "--limit", "20000"],
        15,
    ),
    (
        "pk-meta",
        [
            PY,
            "-m",
            "scout.stores",
            "meta",
            "--max-stores",
            "150",
            "--workers",
            "1",
            "--pause",
            "5",
            "--outside-tranco",
        ],
        25,
    ),
    (
        "pk-light",
        [
            PY,
            "-m",
            "scout.stores",
            "light",
            "--market",
            "pk",
            "--max-stores",
            "200",
            "--workers",
            "1",
            "--pause",
            "5",
        ],
        25,
    ),
    (
        "pk-home",
        [
            PY,
            "-m",
            "scout.stores",
            "home",
            "--market",
            "pk",
            "--max-stores",
            "120",
            "--workers",
            "1",
            "--pause",
            "5",
        ],
        20,
    ),
    (
        "pk-best",
        [
            PY,
            "-m",
            "scout.stores",
            "best",
            "--market",
            "pk",
            "--max-stores",
            "100",
            "--workers",
            "1",
            "--pause",
            "5",
        ],
        25,
    ),
    ("seed", [PY, "-m", "scout.autopilot", "seed"], 2),
    ("build", ["make", "stores-build"], 15),
    ("report", ["make", "stores-report"], 10),
    # README refresh from the committed stats (scripts/readme_build.py); the
    # workflow commits README.md and docs/readme/ if they changed.
    ("readme", [PY, "-m", "scout.autopilot", "readme"], 3),
]
# Derived steps rerun on every invocation: they are cheap, and a rerun the same
# day must pick up what the fetch jobs added since the first run.
ALWAYS = {"seed", "build", "report", "readme"}
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
        if state.get(name) == "ok" and name not in ALWAYS:
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


# Datasets the store build reads (warehouse/models/staging/stg_web_*.sql). dbt's
# read_json fails on a dataset with no files, so an empty lake needs one empty run.
BUILD_DATASETS = [
    "web_scan",
    "web_meta",
    "web_store_light",
    "web_store_deep",
    "web_ranks",
]


def seed_empty_datasets(datasets: list[str] = BUILD_DATASETS) -> int:
    """Record one empty, labelled run for each dataset that has no files yet.
    Never for a dataset with data: a newer empty run would hide the latest rows."""
    n = 0
    for ds in datasets:
        if any((store.LAKE / ds).glob("*/*.jsonl.gz")):
            continue
        store.record_run(
            ds,
            [],
            source="autopilot",
            trust="data",
            params={"seed": True},
            note="empty placeholder so the warehouse build can read the dataset",
        )
        n += 1
    return n


def crux_monthly(country: str = "pk", env=None, runs=None, now=None) -> str:
    """Pull the CrUX popularity table once a month. Returns a status token:
    no-credentials, pulled-this-month, pulled or failed. Never raises, never
    prints anything but through say()."""
    import contextlib

    env = os.environ if env is None else env
    if not env.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return "no-credentials"
    month = (now or _now()).strftime("%Y%m")
    runs = store._runs() if runs is None else runs
    if any(
        r["dataset"] == "crux_origins"
        and (r.get("params") or {}).get("country") == country
        and r["run_id"][:6] == month
        for r in runs
    ):
        return "pulled-this-month"
    try:
        from scout import crux

        with open(os.devnull, "w") as dn, contextlib.redirect_stderr(dn):
            crux.pull(country)
    except BaseException as exc:  # SystemExit from the cost guard included
        return "failed-" + _safe_token(exc_token(exc))
    return "pulled"


def gcp_credentials(env=None, tmp_dir: Path | None = None) -> str:
    """Write the GCP_SA_JSON secret to a private temp file and point
    GOOGLE_APPLICATION_CREDENTIALS at it for later steps (via GITHUB_ENV).
    Nothing about the value is printed. Returns a status token."""
    import tempfile

    env = os.environ if env is None else env
    raw = env.get("GCP_SA_JSON", "")
    if not raw.strip():
        return "not-set"
    try:
        json.loads(raw)
    except ValueError:
        return "not-json"
    fd, name = tempfile.mkstemp(suffix=".json", dir=tmp_dir)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:  # mkstemp makes it 0600
        fh.write(raw)
    gh_env = env.get("GITHUB_ENV")
    if not gh_env:
        return "no-github-env"
    with open(gh_env, "a", encoding="utf-8") as fh:
        fh.write(f"GOOGLE_APPLICATION_CREDENTIALS={name}\n")
    return "written"


README_SCRIPT = Path("scripts/readme_build.py")


def readme_refresh(script: Path = README_SCRIPT, runner=subprocess.run) -> str:
    """Run scripts/readme_build.py if it exists; its output is not printed."""
    if not script.exists():
        return "script-missing"
    p = runner(
        [PY, str(script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return "ok" if p.returncode == 0 else "failed"


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


def storage_configured(env=None) -> bool:
    env = os.environ if env is None else env
    return bool(env.get("SUPABASE_URL") and env.get("SUPABASE_SERVICE_KEY"))


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
        "--need-storage",
        action="store_true",
        help="heartbeat lives in private storage: skip (exit 0) when it is not configured",
    )
    h.add_argument(
        "--no-drift",
        action="store_true",
        help="heartbeat only (when the fingerprint rows were not pulled)",
    )
    sub.add_parser("jobs")
    sub.add_parser("crux", help="monthly CrUX pull (no-op without credentials)")
    sub.add_parser("gcp-credentials", help="GCP_SA_JSON secret -> temp file (CI)")
    sub.add_parser("readme", help="run scripts/readme_build.py if present")
    sub.add_parser(
        "seed", help="empty placeholder runs for build datasets with no files"
    )
    a = ap.parse_args(argv)
    if a.cmd == "seed":
        say("seed", datasets=seed_empty_datasets())
        return 0
    if a.cmd == "crux":
        st = crux_monthly()
        say("crux", status=st)
        return 1 if st.startswith("failed") else 0
    if a.cmd == "gcp-credentials":
        say("gcp-credentials", status=gcp_credentials())
        return 0
    if a.cmd == "readme":
        st = readme_refresh()
        say("readme", status=st)
        return 1 if st == "failed" else 0
    if a.cmd == "jobs":
        for name, _cmd, tmin in JOBS:
            say("job", job=name, timeout_min=tmin)
        return 0
    if a.cmd == "daily":
        return daily(a.only, a.force, a.dry_run)
    if a.need_storage and not storage_configured():
        # A fresh runner has no heartbeat without the lake: not a pipeline failure.
        say("health", skipped=True, reason="no-lake-storage")
        return 0
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
