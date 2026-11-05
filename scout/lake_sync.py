"""Sync the private data folder with a private Supabase Storage bucket (decision 0016).

    python -m scout.lake_sync pull [--dry-run] [--prefix lake/_autopilot/]
    python -m scout.lake_sync push [--dry-run]     # data/private/ -> bucket
    python -m scout.lake_sync status               # counts: local, remote, to push

Env: SUPABASE_URL, SUPABASE_SERVICE_KEY, optional SUPABASE_BUCKET (default "lake").
Without the two secrets every command is a no-op that says so and exits 0, so the
autopilot runs locally and in a fork without storage.

What is synced: every file under data/private/ except caches that rebuild
(tranco/, dbt/, vault/) and temp files. Three kinds of file, by path:

  immutable  lake/<dataset>/<date>/<run_id>.jsonl.gz   uploaded once, never replaced
  lines      lake/_runs.jsonl, llm_cache.jsonl          union of lines on pull and push
  replace    everything else (warehouse.duckdb, usage,  newer copy wins
             heartbeats, private reports)

The bucket holds `_manifest.json` (path -> sha256, size, updated_at). It is
written last, after every file it lists, so a run that dies mid-push leaves the
previous manifest valid: readers only trust what the manifest names. Downloads
are checked against the manifest's sha256 and written to a temp name, then
renamed, so a local file is never half-written. One writer at a time is the
workflow's job (concurrency group); push still merges the remote line files
first, so a second writer cannot drop the first one's runs.

Output is counts only (scout.quiet): the repo and its Actions logs are public.

HOMEGROWN (thin): supabase-py / storage3 is the maintained client, but adding it
needs an owner-approved install; these four REST calls use `requests`, already a
dependency. See docs/decisions/0017-lake-sync-supabase.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from scout.quiet import exc_token, say

ROOT = Path(os.environ.get("SCOUT_PRIVATE", "data/private"))
MANIFEST = "_manifest.json"
SKIP_DIRS = {"tranco", "dbt", "vault"}
MAX_BYTES = 50 * 1024 * 1024  # Supabase free plan: 50 MB per file
_RUN_FILE = re.compile(
    r"^lake/[a-z][a-z0-9_]{0,62}/\d{4}-\d{2}-\d{2}/[^/]+\.jsonl\.gz$"
)
LINE_FILES = {"lake/_runs.jsonl": "run_id", "llm_cache.jsonl": None}


class Exists(Exception):
    """Upload refused because the object is already there."""


class SupabaseStorage:
    """The four Storage REST calls we need. Errors carry the status code only."""

    def __init__(self, url: str, key: str, bucket: str = "lake", session=None):
        import requests

        self.base = url.rstrip("/") + "/storage/v1/object"
        self.bucket = bucket
        self.s = session or requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {key}", "apikey": key})

    def _url(self, path: str) -> str:
        return f"{self.base}/{quote(self.bucket)}/{quote(path)}"

    def _call(self, method: str, path: str, **kw):
        for attempt in range(4):
            try:
                r = self.s.request(method, self._url(path), timeout=180, **kw)
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2**attempt)
                continue
            if r.status_code >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return r
        return r

    @staticmethod
    def _missing(r) -> bool:
        # Storage answers a missing object with 404, or 400 carrying "not_found".
        return r.status_code == 404 or (
            r.status_code == 400 and "not_found" in r.text.lower().replace(" ", "_")
        )

    def get(self, path: str) -> bytes | None:
        r = self._call("GET", path)
        if self._missing(r):
            return None
        if not r.ok:
            raise RuntimeError(f"storage get http{r.status_code}")
        return r.content

    def put(self, path: str, data: bytes, upsert: bool) -> None:
        r = self._call(
            "POST",
            path,
            data=data,
            headers={
                "x-upsert": "true" if upsert else "false",
                "content-type": "application/octet-stream",
            },
        )
        if r.status_code in (400, 409) and not upsert and "exist" in r.text.lower():
            raise Exists()
        if not r.ok:
            raise RuntimeError(f"storage put http{r.status_code}")


def storage_from_env():
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        return None
    return SupabaseStorage(url, key, os.environ.get("SUPABASE_BUCKET", "lake"))


def kind(rel: str) -> str:
    if rel in LINE_FILES:
        return "lines"
    if _RUN_FILE.match(rel):
        return "immutable"
    return "replace"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_files(root: Path = None) -> dict[str, Path]:
    root = root or ROOT
    out = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if rel.split("/")[0] in SKIP_DIRS or rel == MANIFEST:
            continue
        if p.name.endswith((".tmp", ".lock")) or ".tmp." in p.name:
            continue
        out[rel] = p
    return out


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".sync.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def merge_lines(remote: bytes, local: bytes, key: str | None) -> bytes:
    """Union of two line files: remote order first, then local-only lines.
    With a key, a line is identified by that JSON field (e.g. run_id)."""
    out, seen = [], set()
    for blob in (remote, local):
        for ln in blob.decode("utf-8").splitlines():
            if not ln.strip():
                continue
            ident = ln
            if key:
                try:
                    ident = json.loads(ln).get(key) or ln
                except ValueError:
                    pass
            if ident in seen:
                continue
            seen.add(ident)
            out.append(ln)
    return ("\n".join(out) + "\n").encode("utf-8") if out else b""


def _manifest(st) -> dict:
    raw = st.get(MANIFEST)
    if not raw:
        return {"version": 1, "files": {}}
    m = json.loads(raw)
    m.setdefault("files", {})
    return m


def _mtime_iso(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(
        timespec="seconds"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def pull(st, root: Path = None, dry_run: bool = False, prefix: str = "") -> dict:
    root = root or ROOT
    m = _manifest(st)
    if prefix:
        m["files"] = {k: v for k, v in m["files"].items() if k.startswith(prefix)}
    local = local_files(root)
    c = dict(
        remote=len(m["files"]),
        fetched=0,
        merged=0,
        kept_local=0,
        same=0,
        conflicts=0,
        errors=0,
    )
    for rel, info in sorted(m["files"].items()):
        path = root / rel
        k = kind(rel)
        have = path.read_bytes() if rel in local else None
        if have is not None and sha(have) == info["sha256"]:
            c["same"] += 1
            continue
        if have is not None and k == "immutable":
            c["conflicts"] += 1  # a run file never changes; keep ours, flag it
            continue
        if (
            have is not None
            and k == "replace"
            and _mtime_iso(path) > info["updated_at"]
        ):
            c["kept_local"] += 1
            continue
        if dry_run:
            c["fetched"] += 1
            continue
        try:
            data = st.get(rel)
        except Exception:
            c["errors"] += 1
            continue
        if data is None or sha(data) != info["sha256"]:
            c["errors"] += 1
            continue
        if have is not None and k == "lines":
            _write_atomic(path, merge_lines(data, have, LINE_FILES[rel]))
            c["merged"] += 1
        else:
            _write_atomic(path, data)
            c["fetched"] += 1
    return c


def push(st, root: Path = None, dry_run: bool = False) -> dict:
    root = root or ROOT
    m = _manifest(st)
    files = m["files"]
    c = dict(local=0, uploaded=0, same=0, merged=0, conflicts=0, too_big=0, errors=0)
    # 1. Fold the remote line files into ours first, so nothing remote is dropped.
    for rel, key in LINE_FILES.items():
        path = root / rel
        if rel in files and path.exists() and not dry_run:
            data = st.get(rel)
            if data is not None and sha(data) != sha(path.read_bytes()):
                _write_atomic(path, merge_lines(data, path.read_bytes(), key))
                c["merged"] += 1
    local = local_files(root)
    c["local"] = len(local)
    # 2. Run files first, then the rest, then the run log; the manifest last.
    order = sorted(
        local, key=lambda r: (kind(r) != "immutable", r == "lake/_runs.jsonl", r)
    )
    for rel in order:
        p = local[rel]
        data = p.read_bytes()
        digest = sha(data)
        old = files.get(rel)
        if old and old["sha256"] == digest:
            c["same"] += 1
            continue
        k = kind(rel)
        if old and k == "immutable":
            c["conflicts"] += 1
            continue
        if len(data) > MAX_BYTES:
            c["too_big"] += 1
            continue
        if dry_run:
            c["uploaded"] += 1
            continue
        try:
            st.put(rel, data, upsert=(k != "immutable"))
        except Exists:
            # uploaded by a run that died before its manifest: same file is fine
            remote = st.get(rel)
            if remote is None or sha(remote) != digest:
                c["conflicts"] += 1
                continue
        except Exception:
            c["errors"] += 1
            continue
        files[rel] = {"sha256": digest, "size": len(data), "updated_at": _now()}
        c["uploaded"] += 1
    if not dry_run and c["uploaded"]:
        m.update({"version": 1, "updated_at": _now(), "files": files})
        st.put(MANIFEST, json.dumps(m, sort_keys=True, indent=1).encode(), upsert=True)
    return c


def status(st, root: Path = None) -> dict:
    root = root or ROOT
    m = _manifest(st)
    local = local_files(root)
    behind = sum(
        1
        for rel, p in local.items()
        if m["files"].get(rel, {}).get("sha256") != sha(p.read_bytes())
    )
    return dict(
        local=len(local),
        remote=len(m["files"]),
        to_push=behind,
        remote_only=len(set(m["files"]) - set(local)),
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sync data/private with Supabase Storage")
    ap.add_argument("cmd", choices=["pull", "push", "status"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prefix", default="", help="pull only paths under this prefix")
    a = ap.parse_args(argv)
    st = storage_from_env()
    if st is None:
        say("lake-sync", cmd=a.cmd, skipped=True, reason="no-supabase-secrets")
        return 0
    try:
        if a.cmd == "pull":
            c = pull(st, dry_run=a.dry_run, prefix=a.prefix)
        elif a.cmd == "push":
            c = push(st, dry_run=a.dry_run)
        else:
            c = status(st)
    except Exception as exc:  # message may hold a URL: print the class only
        say("lake-sync", cmd=a.cmd, ok=False, error=exc_token(exc))
        return 1
    say("lake-sync", cmd=a.cmd, dry_run=a.dry_run, **c)
    return 1 if c.get("errors") else 0


if __name__ == "__main__":
    sys.exit(main())
