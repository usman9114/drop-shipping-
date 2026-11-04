"""Pure parsing logic of the internet-metadata harness (no network)."""

import pytest

from scout import webmeta


@pytest.mark.parametrize(
    ("domain", "expected"),
    [
        ("glamnails.com", ["nail"]),
        ("best-jewelry-shop.co.uk", ["jewel"]),
        ("example.com", []),
        ("nailjewel.com", ["nail", "jewel"]),
        ("jewel.nailcare", ["jewel"]),  # only the last label (TLD) is dropped
    ],
)
def test_keyword_hits_use_the_name_not_the_tld(domain, expected):
    assert webmeta.keyword_hits(domain) == expected


def test_shopify_detection_by_ip_range_or_cname():
    assert webmeta.is_shopify(["23.227.38.65"], [])
    assert webmeta.is_shopify([], ["shops.myshopify.com."])
    assert not webmeta.is_shopify(["104.16.1.1"], ["example.netlify.app."])
    assert not webmeta.is_shopify(["not-an-ip"], [])


def test_txt_signals_reveal_platforms():
    txts = [
        '"facebook-domain-verification=abc123"',
        '"google-site-verification=xyz"',
        '"v=spf1 include:_spf.google.com include:shops.shopify.com ~all"',
        '"pinterest-site-verification=1"',
        '"unrelated=1"',
    ]
    assert webmeta.txt_signals(txts) == [
        "google_search_console",
        "google_workspace",
        "meta_business",
        "pinterest",
        "shopify_email",
    ]


def test_parse_sitemap_index_and_urlset():
    index = """<?xml version="1.0"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <sitemap><loc>https://x.com/sitemap_products_1.xml?from=1</loc></sitemap>
      <sitemap><loc>https://x.com/sitemap_pages_1.xml</loc></sitemap>
    </sitemapindex>"""
    children, dates = webmeta.parse_sitemap(index)
    assert children == [
        "https://x.com/sitemap_products_1.xml?from=1",
        "https://x.com/sitemap_pages_1.xml",
    ]
    assert dates == []
    urlset = """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://x.com/products/a</loc><lastmod>2026-10-01T10:00:00-04:00</lastmod></url>
      <url><loc>https://x.com/products/b</loc><lastmod>2025-01-02T00:00:00Z</lastmod></url>
    </urlset>"""
    assert webmeta.parse_sitemap(urlset) == ([], ["2026-10-01", "2025-01-02"])


def test_bad_xml_is_empty_not_a_crash():
    assert webmeta.parse_sitemap("<html>not a sitemap") == ([], [])


def test_summarize_products_keeps_aggregates_only():
    payload = {
        "products": [
            {
                "title": "SECRET NAME",
                "created_at": "2025-03-02T10:00:00Z",
                "product_type": "Necklace",
                "variants": [{"price": "19.99"}, {"price": "24.99"}],
            },
            {
                "title": "OTHER",
                "created_at": "2026-10-20T10:00:00Z",
                "product_type": "necklace",
                "variants": [{"price": "bad"}],
            },
            "junk",
        ]
    }
    out = webmeta.summarize_products(payload)
    assert out["products_in_page"] == 2
    assert (out["oldest_created"], out["newest_created"]) == (
        "2025-03-02",
        "2026-10-20",
    )
    assert out["created_by_month"] == {"2025-03": 1, "2026-10": 1}
    assert out["median_price"] == 22.49
    assert out["top_types"] == ["necklace"]
    assert "SECRET NAME" not in str(out)
