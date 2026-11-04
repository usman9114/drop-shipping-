"""Bounded official API sample check; no source rows are retained or logged."""

import json
from datetime import datetime, timezone

import requests

URL = "https://api.myip.ms/217.199.217.100"
MAX_BYTES = 1_000_000


def validate(payload):
    """Validate the documented sample without mistaking history for live leads."""
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        raise ValueError("sample status invalid")
    if payload.get("ip_address") != "217.199.217.100":
        raise ValueError("unexpected sample identity")
    for key in ("websites_on_ip_now", "websites_on_ip_before"):
        rows = payload.get(key)
        if not isinstance(rows, list):
            raise ValueError("sample schema changed")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("website"), str):
                raise ValueError("sample row invalid")
            if not row["website"].strip():
                raise ValueError("sample website empty")
    return {"status": "pass", "schema": "current_and_historical_lists"}


def check():
    # Fixed public sample only: no keys, arbitrary URLs, pagination or retries.
    with requests.get(URL, timeout=(10, 20), allow_redirects=False, stream=True) as r:
        if r.status_code != 200:
            raise ValueError("sample HTTP status invalid")
        body = bytearray()
        for chunk in r.iter_content(chunk_size=16384):
            body.extend(chunk)
            if len(body) > MAX_BYTES:
                raise ValueError("sample response exceeds limit")
        return validate(json.loads(body))


def main():
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "mode": "sample"}
    try:
        report.update(check())
    except (requests.RequestException, ValueError):
        # Provider bodies, URLs with secrets and transport exception text stay out
        # of public workflow logs. No raw response files or artifacts are created.
        report.update(status="fail", reason="transport_or_contract_check_failed")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
