"""MOCK fixtures only; no live HTTP calls in CI."""

import pytest

from scripts import myip_sample_check as sample


def mock_payload():
    return {
        "status": "ok",
        "ip_address": "217.199.217.100",
        "websites_on_ip_now": [],
        "websites_on_ip_before": [{"website": "historical.example"}],
    }


def test_history_does_not_become_current_leads():
    result = sample.validate(mock_payload())
    assert result == {"status": "pass", "schema": "current_and_historical_lists"}
    assert "historical.example" not in str(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "error"),
        ("ip_address", "192.0.2.1"),
        ("websites_on_ip_now", None),
        ("websites_on_ip_before", {}),
        ("websites_on_ip_now", [{"website": ""}]),
    ],
)
def test_invalid_contract_fails(field, value):
    payload = mock_payload()
    payload[field] = value
    with pytest.raises(ValueError):
        sample.validate(payload)


def test_failure_logs_no_provider_content(monkeypatch, capsys):
    def fail():
        raise sample.requests.RequestException("MOCK private response contents")

    monkeypatch.setattr(sample, "check", fail)
    assert sample.main() == 1
    output = capsys.readouterr().out
    assert '"status": "fail"' in output
    assert "private response" not in output
