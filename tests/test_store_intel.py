"""Store stories: packs, gaps, grounding, template (no network, no DB)."""

from scout import store_intel as si

ROW = {
    "domain": "example-store.com",
    "tranco_rank": 120000,
    "rank_earliest": 240000,
    "rank_earliest_date": "2025-11-04",
    "rank_growth_log": 0.693,
    "country": "US",
    "currency": "USD",
    "published_products": 400,
    "products_sampled": 250,
    "existed_by": "2019-03-01",
    "added_30d": 12,
    "added_90d": 40,
    "added_365d": 150,
    "price_p25": 18.0,
    "price_median": 29.0,
    "price_p75": 45.0,
    "discount_share": 0.6,
    "top_category": "jewelry_watches",
    "top_category_share": 0.82,
    "business_model": "unclear",
    "business_model_why": ["3 vendors, largest 70%"],
    "paid_ads": ["meta_pixel", "tiktok_pixel"],
    "retention": ["klaviyo_email"],
    "partners": [],
    "conversion": ["reviews_app"],
    "social_networks": ["instagram"],
    "dns_signals": ["meta_business"],
    "sample_review_count": None,
    "best_score": 0.91,
}


def test_pack_has_no_domain_and_names_gaps():
    p = si.pack(ROW)
    assert "domain" not in p
    assert "revenue and order volume" in p["gaps"]
    assert any("review counts" in g for g in p["gaps"])
    assert any("older catalogue" in g for g in p["gaps"])


def test_grounding_accepts_pack_numbers_and_percent_shares():
    p = si.pack(ROW)
    assert si.grounded("Rank rose from 240000 to 120000; 82% are jewelry.", p)
    assert si.grounded("It added 40 products in 90 days.", p)
    assert not si.grounded("It makes $2 million a year.", p)


def test_template_is_grounded_and_flags_brands():
    p = si.pack(ROW)
    text = si.template(p)
    assert si.grounded(text, p)
    assert "method copyable" in text
    brand = si.pack({**ROW, "business_model": "brand"})
    assert "not copyable" in si.template(brand)


def test_narrate_falls_back_when_model_invents_numbers():
    p = si.pack(ROW)
    fake = lambda *a, **k: {"text": "Revenue is 5000000 dollars.", "model": "m"}  # noqa: E731
    text, method, row = si.narrate(p, {}, fake)
    assert method == "template (model text rejected)" and row is None
    ok = lambda *a, **k: {"text": "It sells jewelry at a median of 29.", "model": "m"}  # noqa: E731
    text, method, row = si.narrate(p, {}, ok)
    assert method == "llm" and row["narrative"] == text
