"""Autopilot: quiet public logs, resumable daily runs, heartbeats and alerts."""

import ast
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scout import autopilot as ap
from scout import quiet, store

ROOT = Path(__file__).resolve().parent.parent
LEAK = "leaky-store.example"


@pytest.fixture
def lake(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "LAKE", tmp_path / "lake")
    monkeypatch.setattr(store, "RUNS", tmp_path / "lake" / "_runs.jsonl")
    monkeypatch.setattr(ap, "STATE", tmp_path / "lake" / "_autopilot")
    monkeypatch.setattr(
        ap, "HEARTBEAT", tmp_path / "lake" / "_autopilot" / "heartbeat.json"
    )
    monkeypatch.setattr(ap, "LOGS", tmp_path / "logs")
    return tmp_path


# --- quiet logging ---------------------------------------------------------


@pytest.mark.parametrize(
    "bad", ["shop.example.com", "https://x", "a b", "/tmp/x", "a@b", "Error", "x" * 60]
)
def test_say_refuses_anything_that_could_name_a_store(bad):
    with pytest.raises(quiet.LeakError):
        quiet.line("job", job=bad)


def test_say_accepts_counts_and_tokens():
    assert quiet.line("job", job="meta", rows=5, ok=True, s=1.25) == (
        "job job=meta rows=5 ok=true s=1.25"
    )


def test_exception_becomes_its_class_name_only():
    assert quiet.exc_token(ConnectionError(f"host={LEAK}")) == "connectionerror"


@pytest.mark.parametrize("module", ["scout/autopilot.py", "scout/lake_sync.py"])
def test_entry_points_print_only_through_say(module):
    """No print() or sys.stdout/stderr writes: the only output path is quiet.say."""
    tree = ast.parse((ROOT / module).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "print":
            pytest.fail(f"print() in {module} line {node.lineno}")
        if isinstance(node, ast.Attribute) and node.attr in ("stdout", "stderr"):
            if getattr(node.value, "id", "") == "sys":
                pytest.fail(f"sys.{node.attr} in {module} line {node.lineno}")


def _workflow_commands(wf: str) -> list[str]:
    """Every shell command of every `run:` step, block scalars flattened."""
    cmds, lines = [], wf.splitlines()
    for i, ln in enumerate(lines):
        t = ln.strip()
        if not t.startswith("run:"):
            continue
        rest = t[len("run:") :].strip()
        if rest not in ("|", ">", "|-"):
            cmds.append(rest)
            continue
        indent = len(ln) - len(ln.lstrip())
        for nxt in lines[i + 1 :]:
            if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                break
            if nxt.strip():
                cmds.append(nxt.strip())
    return cmds


def test_workflow_uploads_no_artifacts_and_runs_only_quiet_entry_points():
    wf = (ROOT / ".github/workflows/autopilot.yml").read_text()
    assert "upload-artifact" not in wf
    assert "set -x" not in wf and "xtrace" not in wf
    assert "echo $" not in wf  # never echo a variable
    allowed = (
        "pip install",
        "python -m scout.autopilot",
        "python -m scout.lake_sync",
        "git config user.",
        "git add README.md docs/readme/",
        "git diff --cached --quiet",
        "git commit -q -m",
        "git pull -q --rebase",
        "git push -q",
        "if ",
        "else",
        "fi",
        'echo "readme unchanged"',
    )
    for cmd in _workflow_commands(wf):
        assert cmd.startswith(allowed), f"unexpected step command: {cmd}"


def test_readme_commit_step_is_limited_to_readme_paths():
    wf = (ROOT / ".github/workflows/autopilot.yml").read_text()
    allc = _workflow_commands(wf)
    assert any("git diff --cached --quiet" in c for c in allc)
    cmds = [c for c in allc if c.startswith("git ")]
    for c in cmds:
        if c.startswith("git add"):
            assert c == "git add README.md docs/readme/"
        if c.startswith("git commit"):
            assert c.endswith("-- README.md docs/readme/")
            assert "README: daily refresh" in c
            for banned in ("Co-Authored", "Claude", "Generated with"):
                assert banned not in c
    assert "github-actions[bot]" in wf
    # write access only on the daily job; the workflow default stays read-only
    assert wf.count("contents: write") == 1
    assert wf.index("contents: write") > wf.index("autopilot-daily")
    top = wf[: wf.index("jobs:")]
    assert "contents: read" in top and "write" not in top


def test_actions_are_pinned_to_current_majors():
    for name in ("autopilot", "ci"):
        wf = (ROOT / f".github/workflows/{name}.yml").read_text()
        assert "checkout@v4" not in wf and "setup-python@v5" not in wf


def test_health_job_skips_without_lake_storage(lake, capsys, monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    assert ap.main(["health", "--no-drift", "--need-storage"]) == 0
    assert "reason=no-lake-storage" in capsys.readouterr().out
    # with storage configured a missing heartbeat is a real alert
    monkeypatch.setenv("SUPABASE_URL", "x")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "y")
    assert ap.main(["health", "--no-drift", "--need-storage"]) == 1


def test_health_workflow_asks_for_storage():
    wf = (ROOT / ".github/workflows/autopilot.yml").read_text()
    assert "health --no-drift --need-storage" in wf


# --- Pakistan jobs, crux and readme ---------------------------------------


def _job(name):
    return next(cmd for n, cmd, _ in ap.JOBS if n == name)


def test_pakistan_jobs_are_slow_and_polite():
    for name in ("pk-meta", "pk-light", "pk-home", "pk-best"):
        cmd = _job(name)
        assert cmd[cmd.index("--workers") + 1] == "1", name
        assert cmd[cmd.index("--pause") + 1] == "5", name
        assert "--max-stores" in cmd
    for name in ("pk-light", "pk-home", "pk-best"):
        assert _job(name)[_job(name).index("--market") + 1] == "pk"
    assert "--outside-tranco" in _job("pk-meta")
    for name in ("meta", "light"):  # six workers brought HTTP 429
        assert int(_job(name)[_job(name).index("--workers") + 1]) <= 3


def test_job_order_puts_fetching_before_build_and_readme_last():
    names = [n for n, _, _ in ap.JOBS]
    assert names[-1] == "readme" and names.index("report") < names.index("readme")
    assert names.index("crux") < names.index("pk-discover") < names.index("pk-meta")
    assert names.index("pk-light") < names.index("pk-home") < names.index("pk-best")
    assert names.index("pk-best") < names.index("build")
    assert "readme" in ap.ALWAYS


def test_crux_is_a_quiet_noop_without_credentials_or_when_pulled(lake, monkeypatch):
    from scout import crux

    pulls = []
    monkeypatch.setattr(crux, "pull", lambda c: pulls.append(c) or {})
    assert ap.crux_monthly(env={}) == "no-credentials"
    now = datetime(2026, 11, 25, tzinfo=timezone.utc)
    runs = [
        {
            "dataset": "crux_origins",
            "run_id": "20261103T010101",
            "params": {"country": "pk"},
        }
    ]
    env = {"GOOGLE_APPLICATION_CREDENTIALS": "x.json"}
    assert ap.crux_monthly(env=env, runs=runs, now=now) == "pulled-this-month"
    assert pulls == []
    # last month's pull does not count: it pulls
    old = [{**runs[0], "run_id": "20261003T010101"}]
    assert ap.crux_monthly(env=env, runs=old, now=now) == "pulled"
    assert pulls == ["pk"]

    def boom(c):
        raise SystemExit("stop: 9.0 GB is above MAX_GB")  # the cost guard

    monkeypatch.setattr(crux, "pull", boom)
    assert ap.crux_monthly(env=env, runs=[], now=now).startswith("failed-")


def test_crux_command_exits_zero_without_credentials(lake, capsys, monkeypatch):
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    assert ap.main(["crux"]) == 0
    assert "status=no-credentials" in capsys.readouterr().out


def test_readme_job_skips_when_the_script_is_missing(tmp_path):
    assert ap.readme_refresh(tmp_path / "nope.py") == "script-missing"
    ok = tmp_path / "ok.py"
    ok.write_text("")
    assert ap.readme_refresh(ok) == "ok"
    bad = tmp_path / "bad.py"
    bad.write_text("raise SystemExit(3)")
    assert ap.readme_refresh(bad) == "failed"


def test_gcp_credentials_file_only_when_set_and_never_printed(tmp_path, capsys):
    gh = tmp_path / "gh_env"
    assert ap.gcp_credentials(env={"GITHUB_ENV": str(gh)}) == "not-set"
    assert not gh.exists()
    bad = {"GCP_SA_JSON": "{nope", "GITHUB_ENV": str(gh)}
    assert ap.gcp_credentials(env=bad) == "not-json"
    secret = '{"project_id": "p", "private_key": "TOPSECRET"}'
    env = {"GCP_SA_JSON": secret, "GITHUB_ENV": str(gh)}
    assert ap.gcp_credentials(env=env, tmp_dir=tmp_path) == "written"
    line = gh.read_text().strip()
    assert line.startswith("GOOGLE_APPLICATION_CREDENTIALS=")
    path = Path(line.split("=", 1)[1])
    assert path.read_text() == secret and (path.stat().st_mode & 0o077) == 0
    assert "TOPSECRET" not in capsys.readouterr().out + line


def test_ci_workflow_has_matrix_and_guards():
    wf = (ROOT / ".github/workflows/ci.yml").read_text()
    assert '"3.9"' in wf and '"3.12"' in wf
    for job in ("test:", "lint:", "readme-guard:"):
        assert job in wf
    assert "autopilot daily --dry-run" in wf and "market_rank --help" in wf
    assert "--from-stats docs/readme/stats.json" in wf


def test_a_leaky_job_does_not_reach_the_public_log(lake, capfd):
    leaky = [
        "-c",
        f"import sys; print('{LEAK}'); print('{LEAK}', file=sys.stderr); "
        f"raise SystemExit('failed on https://{LEAK}/products.json')",
    ]
    jobs = [("leaky", [sys.executable, *leaky], 1)]
    assert ap.daily(jobs=jobs) == 1
    out, err = capfd.readouterr()
    assert LEAK not in out and LEAK not in err
    assert "job=leaky status=failed" in out
    log = next((lake / "logs").rglob("leaky.log")).read_text()
    assert LEAK in log  # kept, but only in the private log


# --- daily runner ----------------------------------------------------------


def _ok_runner(record):
    class P:
        returncode, stdout = 0, b"done"

    def run(cmd, **kw):
        record.append((cmd, kw))
        if cmd[0] == "writes-rows":
            store.record_run(
                "web_meta",
                [{"domain": "a"}, {"domain": "b", "error": "x"}],
                source="t",
                trust="data",
            )
        return P()

    return run


def test_daily_runs_in_order_counts_rows_and_captures_output(lake):
    calls = []
    jobs = [("one", ["writes-rows"], 5), ("two", ["noop"], 5)]
    assert ap.daily(jobs=jobs, runner=_ok_runner(calls)) == 0
    assert [c[0][0] for c in calls] == ["writes-rows", "noop"]
    assert all(kw["stdout"] is not None for _, kw in calls)  # never inherits the log
    hb = json.loads(ap.HEARTBEAT.read_text())
    assert hb["jobs"]["one"]["rows_added"] == 2
    assert hb["jobs"]["one"]["error_rows"] == 1
    assert "daily_last_success" in hb
    assert any(r["dataset"] == "autopilot_jobs" for r in store._runs())


def test_a_rerun_the_same_day_resumes_at_the_failed_job(lake, capsys):
    state = {"n": 0}

    class Fail:
        returncode, stdout = 2, b""

    class Ok:
        returncode, stdout = 0, b""

    def runner(cmd, **kw):
        state["n"] += 1
        return Fail() if cmd == ["b"] and state["n"] == 2 else Ok()

    jobs = [("a", ["a"], 5), ("b", ["b"], 5)]
    assert ap.daily(jobs=jobs, runner=runner) == 1
    capsys.readouterr()
    assert ap.daily(jobs=jobs, runner=runner) == 0
    out = capsys.readouterr().out
    assert "job=a status=done-today" in out
    assert state["n"] == 3  # a once, b twice


def test_dry_run_runs_nothing(lake, capsys):
    calls = []
    assert ap.daily(jobs=[("a", ["a"], 5)], dry_run=True, runner=_ok_runner(calls)) == 0
    assert calls == [] and "status=would-run" in capsys.readouterr().out


def test_every_job_fits_the_actions_limit():
    assert sum(t for _, _, t in ap.JOBS) <= 6 * 60
    assert ap.DAILY_BUDGET_MIN < 6 * 60


# --- health ----------------------------------------------------------------


def _heartbeat(now, age_hours=1, rows=100, errs=0):
    t = (now - timedelta(hours=age_hours)).isoformat()
    ap._write_json(
        ap.HEARTBEAT,
        {
            "daily_last_start": t,
            "jobs": {
                n: {"last_success": t, "rows_added": rows, "error_rows": errs}
                for n, _, _ in ap.JOBS
            },
        },
    )


NOW = datetime(2026, 11, 20, 12, tzinfo=timezone.utc)


def test_healthy_heartbeat_has_no_alerts(lake):
    _heartbeat(NOW)
    code, alerts = ap.health(now=NOW, signal_rows=[])
    assert alerts == [] or alerts == [("disk", "high")]


def test_missing_heartbeat_and_stale_jobs_alert(lake):
    assert ("no-heartbeat", "daily") in ap.health(now=NOW, signal_rows=[])[1]
    _heartbeat(NOW, age_hours=48)
    _, alerts = ap.health(now=NOW, signal_rows=[])
    assert ("missed-window", "daily") in alerts
    assert ("stale-job", "meta") in alerts


def test_error_rate_above_ten_percent_alerts(lake):
    _heartbeat(NOW, rows=100, errs=11)
    _, alerts = ap.health(now=NOW, signal_rows=[])
    assert ("error-rate", "fingerprints") in alerts
    _heartbeat(NOW, rows=10, errs=5)  # too few rows to judge
    assert not any(a == "error-rate" for a, _ in ap.health(now=NOW, signal_rows=[])[1])


def _rows(days_ago, n, share, sig="cj_app"):
    day = (NOW - timedelta(days=days_ago)).date().isoformat()
    k = int(n * share)
    return [{"day": day, "signals": [sig] if i < k else []} for i in range(n)]


def test_signal_fire_rate_doubling_week_on_week_alerts():
    rows = _rows(2, 40, 0.5) + _rows(9, 40, 0.2)
    assert ap.drift(rows, NOW) == ["cj_app"]
    steady = _rows(2, 40, 0.3) + _rows(9, 40, 0.25)
    assert ap.drift(steady, NOW) == []
    small = _rows(2, 10, 0.9) + _rows(9, 10, 0.1)
    assert ap.drift(small, NOW) == []


def test_seed_fills_only_missing_build_datasets(lake):
    store.record_run("web_meta", [{"domain": "a"}], source="t", trust="data")
    assert ap.seed_empty_datasets() == len(ap.BUILD_DATASETS) - 1
    assert ap.seed_empty_datasets() == 0  # idempotent
    meta_runs = [r for r in store._runs() if r["dataset"] == "web_meta"]
    assert len(meta_runs) == 1  # a dataset with data is never given an empty run


def test_build_datasets_match_the_staging_models():
    import re

    found = set()
    for f in (ROOT / "warehouse/models/staging").glob("stg_web_*.sql"):
        found |= set(re.findall(r"lake\('([a-z_]+)'", f.read_text()))
    assert found == set(ap.BUILD_DATASETS)


def test_derived_steps_rerun_the_same_day(lake, capsys):
    calls = []
    jobs = [("meta", ["meta"], 5), ("build", ["build"], 5)]
    ap.daily(jobs=jobs, runner=_ok_runner(calls))
    ap.daily(jobs=jobs, runner=_ok_runner(calls))
    assert [c[0][0] for c in calls] == ["meta", "build", "build"]
