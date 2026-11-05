import pytest


@pytest.fixture(autouse=True)
def _no_llm_cache(monkeypatch):
    """Tests never read or write the real LLM answer cache."""
    from scout import llm

    monkeypatch.setattr(llm, "CACHE_FILE", "off")
    monkeypatch.setattr(llm, "_cache", None)
