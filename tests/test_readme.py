import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "readme_build", ROOT / "scripts" / "readme_build.py"
)
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)


def _market(n):
    return {
        "stores": n,
        "profiled": n // 2,
        "with_popularity": n // 3,
        "with_rank_history": 5,
        "categories": 3,
        "top_categories": [["apparel", 10], ["skincare", 4]],
        "median_price": 42.5,
        "price_bands": [1, 2, 3, 4, 5],
        "models": {"brand": 6, "retailer": 2, "dropship": 1, "other": 1},
        "crux_buckets": {str(b): 1 for b in rb.CRUX_ORDER},
        "best_seller_lists": 7,
    }


STATS = {
    "generated_at": "2026-01-02",
    "markets": {"us": _market(100), "pk": _market(60)},
    "weights": {
        "pk_popularity": 0.35,
        "global_rank": 0.2,
        "growth": 0.25,
        "rhythm": 0.2,
    },
    "bucket_score": {
        "1000": 1.0,
        "5000": 0.8,
        "10000": 0.6,
        "50000": 0.4,
        "100000": 0.2,
        "500000": 0.0,
    },
}


def test_sections_and_mermaid():
    md = rb.render(STATS)["README.md"]
    for s in (
        "## At a glance",
        "## Charts",
        "## Roadmap",
        "How the ranking works",
        "How good are the rules",
        "What we do not know",
        "Data sources and terms",
        "Run it yourself",
        "## Project map",
        "> [!NOTE]",
        "> [!WARNING]",
        "> [!IMPORTANT]",
        "- [x]",
        "- [ ]",
        "2026-01-02",
    ):
        assert s in md
    assert md.count("```mermaid") == 2
    assert "flowchart" in md and "gantt" in md


def test_svgs_valid_xml():
    files = rb.render(STATS)
    svgs = {k: v for k, v in files.items() if k.endswith(".svg")}
    assert len(svgs) == 6
    for text in svgs.values():
        assert ET.fromstring(text).tag.endswith("svg")


def test_deterministic():
    assert rb.render(STATS) == rb.render(json.loads(json.dumps(STATS)))


def test_guard_raises_on_leaks():
    ok = "plain text with github.com/x and README.md"
    rb.assert_public_safe(ok, ["shop.example"])
    for bad in (
        "see shop.example",
        "visit other-store.com now",
        "key sk-abc123",
        "token eyJhbGci",
        "AKIAXXXX",
        "-----BEGIN KEY",
    ):
        with pytest.raises(ValueError):
            rb.assert_public_safe(bad, ["shop.example"])
    with pytest.raises(ValueError):
        rb.assert_public_safe("welcome to Lumina Goods", [], ["Lumina Goods"])


def test_guard_passes_generated_output_and_committed_files():
    for text in rb.render(STATS).values():
        rb.assert_public_safe(text, ["shop.example"], ["Lumina Goods"])
    for p in [
        ROOT / "README.md",
        ROOT / "docs/readme/stats.json",
        *(ROOT / "docs/readme").glob("*.svg"),
    ]:
        if p.exists():
            rb.assert_public_safe(p.read_text(encoding="utf-8"))


def test_renders_without_lake(monkeypatch, tmp_path):
    def boom():
        raise OSError("no lake")

    monkeypatch.setattr(rb, "collect", boom)
    monkeypatch.setattr(rb, "OUT", tmp_path)
    monkeypatch.setattr(rb, "ROOT", tmp_path)
    (tmp_path / "docs" / "readme").mkdir(parents=True)
    (tmp_path / "stats.json").write_text(json.dumps(STATS))
    assert rb.main(["--from-stats", str(tmp_path / "stats.json")]) == 0
    assert "At a glance" in (tmp_path / "README.md").read_text()


def test_shrinkage_keeps_last_good_snapshot(tmp_path):
    """A cloud run with a partial lake must not publish near-zero counts."""
    old = tmp_path / "stats.json"
    old.write_text(
        json.dumps({"markets": {"pk": {"stores": 3000}, "us": {"stores": 10000}}})
    )
    grown = {"markets": {"pk": {"stores": 3100}, "us": {"stores": 9950}}}
    assert rb.shrinkage(grown, old) == ""
    partial = {"markets": {"pk": {"stores": 12}, "us": {"stores": 10000}}}
    assert "pk" in rb.shrinkage(partial, old)
    assert rb.shrinkage(partial, tmp_path / "missing.json") == ""


@pytest.mark.parametrize(
    "text",
    [
        "visit shop\u200b.example",
        "visit shop<br/>.example",
        "visit shop\u3002example",
        "visit shop\uff0eexample",
        "visit SHOP.EXAMPLE",
    ],
)
def test_guard_domain_bypasses(text):
    with pytest.raises(ValueError):
        rb.assert_public_safe(text, ["shop.example"])


@pytest.mark.parametrize(
    "text",
    [
        "Zenith Outfitters",
        "Zenith-Outfitters",
        "Zenith\nOutfitters",
        "Zenith\u00a0Outfitters",
        "Zenith<b></b> Outfitters",
        "Zenith\u200b Outfitters",
        "ZENITH   OUTFITTERS",
    ],
)
def test_guard_name_bypasses(text):
    with pytest.raises(ValueError):
        rb.assert_public_safe(f"best: {text}!", [], ["Zenith Outfitters"])
