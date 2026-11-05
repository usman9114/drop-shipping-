"""Lake sync to private storage: atomic, never loses runs, quiet without secrets."""

import json

import pytest

from scout import lake_sync as ls


class FakeStorage:
    def __init__(self, fail_after=None):
        self.objects: dict[str, bytes] = {}
        self.puts: list[str] = []
        self.fail_after = fail_after

    def get(self, path):
        return self.objects.get(path)

    def put(self, path, data, upsert):
        if self.fail_after is not None and len(self.puts) >= self.fail_after:
            raise RuntimeError("storage put http500")
        if not upsert and path in self.objects:
            raise ls.Exists()
        self.objects[path] = bytes(data)
        self.puts.append(path)


RUN = "lake/web_meta/2026-11-05/20261105T010101Z-abc123.jsonl.gz"


def _seed(root, run_ids=("r1",), extra=b"db"):
    (root / "lake/web_meta/2026-11-05").mkdir(parents=True, exist_ok=True)
    (root / RUN).write_bytes(b"gz-bytes")
    (root / "lake/_runs.jsonl").write_text(
        "".join(json.dumps({"run_id": r}) + "\n" for r in run_ids)
    )
    (root / "warehouse.duckdb").write_bytes(extra)
    (root / "tranco").mkdir(exist_ok=True)
    (root / "tranco/list.csv").write_text("big list, rebuilt from Tranco")


def test_push_then_pull_round_trips_and_skips_caches(tmp_path):
    a, b, st = tmp_path / "a", tmp_path / "b", FakeStorage()
    _seed(a)
    c = ls.push(st, a)
    assert c["uploaded"] == 3 and c["errors"] == 0
    assert "tranco/list.csv" not in st.objects
    assert st.puts[-1] == ls.MANIFEST  # the manifest is written last
    assert st.puts[0] == RUN  # run files before the run log
    c = ls.pull(st, b)
    assert c["fetched"] == 3
    for rel in (RUN, "lake/_runs.jsonl", "warehouse.duckdb"):
        assert (b / rel).read_bytes() == (a / rel).read_bytes()
    assert ls.push(st, a)["uploaded"] == 0  # nothing changed: nothing sent


def test_a_run_file_is_never_replaced(tmp_path):
    a, st = tmp_path / "a", FakeStorage()
    _seed(a)
    ls.push(st, a)
    (a / RUN).write_bytes(b"tampered")
    c = ls.push(st, a)
    assert c["conflicts"] == 1
    assert st.objects[RUN] == b"gz-bytes"


def test_two_writers_keep_each_others_runs(tmp_path):
    a, b, st = tmp_path / "a", tmp_path / "b", FakeStorage()
    _seed(a, ("r1",))
    _seed(b, ("r2",))
    ls.push(st, a)
    ls.push(st, b)  # merges a's run log first
    remote = [
        json.loads(x)["run_id"]
        for x in st.objects["lake/_runs.jsonl"].decode().splitlines()
    ]
    assert remote == ["r1", "r2"]
    ls.pull(st, a)
    local = [
        json.loads(x)["run_id"]
        for x in (a / "lake/_runs.jsonl").read_text().splitlines()
    ]
    assert local == ["r1", "r2"]


def test_a_push_that_dies_leaves_the_old_manifest(tmp_path):
    a, st = tmp_path / "a", FakeStorage(fail_after=1)
    _seed(a)
    with pytest.raises(RuntimeError):
        ls.push(st, a)  # the manifest upload fails after one file got through
    assert ls.MANIFEST not in st.objects
    assert ls.pull(st, tmp_path / "b")["remote"] == 0  # readers trust the manifest only


def test_retry_after_a_dead_push_accepts_the_same_run_file(tmp_path):
    a, st = tmp_path / "a", FakeStorage(fail_after=1)
    _seed(a)
    with pytest.raises(RuntimeError):
        ls.push(st, a)
    st.fail_after = None
    c = ls.push(st, a)
    assert c["conflicts"] == 0 and ls.MANIFEST in st.objects


def test_dry_run_sends_nothing(tmp_path):
    a, st = tmp_path / "a", FakeStorage()
    _seed(a)
    assert ls.push(st, a, dry_run=True)["uploaded"] == 3
    assert st.objects == {}


def test_a_corrupt_download_is_not_written(tmp_path):
    a, b, st = tmp_path / "a", tmp_path / "b", FakeStorage()
    _seed(a)
    ls.push(st, a)
    st.objects["warehouse.duckdb"] = b"corrupt"
    c = ls.pull(st, b)
    assert c["errors"] == 1
    assert not (b / "warehouse.duckdb").exists()


def test_pull_prefix_fetches_only_that_folder(tmp_path):
    a, b, st = tmp_path / "a", tmp_path / "b", FakeStorage()
    _seed(a)
    (a / "lake/_autopilot").mkdir()
    (a / "lake/_autopilot/heartbeat.json").write_text("{}")
    ls.push(st, a)
    assert ls.pull(st, b, prefix="lake/_autopilot/")["fetched"] == 1
    assert not (b / "warehouse.duckdb").exists()


def test_no_secrets_is_a_quiet_no_op(monkeypatch, capsys):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    assert ls.main(["push"]) == 0
    out = capsys.readouterr().out
    assert "skipped=true" in out and "no-supabase-secrets" in out


def test_kinds_by_path():
    assert ls.kind(RUN) == "immutable"
    assert ls.kind("lake/_runs.jsonl") == "lines"
    assert ls.kind("llm_cache.jsonl") == "lines"
    assert ls.kind("warehouse.duckdb") == "replace"
    assert ls.kind("lake/_autopilot/heartbeat.json") == "replace"


class _Resp:
    def __init__(self, code, text="", content=b""):
        self.status_code, self.text, self.content = code, text, content
        self.ok = 200 <= code < 300


class _Session:
    def __init__(self, resp):
        self.headers, self.calls, self.resp = {}, [], resp

    def request(self, method, url, **kw):
        self.calls.append((method, url, kw))
        return self.resp


def test_supabase_client_shapes_requests():
    s = _Session(_Resp(200))
    st = ls.SupabaseStorage("https://p.supabase.co/", "k", "lake", session=s)
    st.put("lake/a b.json", b"x", upsert=False)
    method, url, kw = s.calls[0]
    assert method == "POST"
    assert url == "https://p.supabase.co/storage/v1/object/lake/lake/a%20b.json"
    assert kw["headers"]["x-upsert"] == "false"
    assert s.headers["apikey"] == "k" and s.headers["Authorization"] == "Bearer k"


@pytest.mark.parametrize("resp", [_Resp(404), _Resp(400, '{"error":"not_found"}')])
def test_supabase_missing_object_is_none(resp):
    st = ls.SupabaseStorage("https://p.supabase.co", "k", session=_Session(resp))
    assert st.get("_manifest.json") is None


def test_supabase_error_carries_status_only():
    st = ls.SupabaseStorage("https://p.supabase.co", "k", session=_Session(_Resp(403)))
    with pytest.raises(RuntimeError) as e:
        st.get("x")
    assert str(e.value) == "storage get http403"
