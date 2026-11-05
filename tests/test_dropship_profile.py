"""Pure logic of the policy-page dropship profiler (no network)."""

from scout import dropship_profile as dp


def test_slow_ship_phrase_detected():
    html = "<p>Please allow 2-4 weeks for your order to arrive.</p>"
    sig = dp.extract_policy_signals(html, None)
    assert sig.slow_ship_phrase is not None
    assert sig.fast_ship_phrase is None


def test_fast_ship_phrase_detected():
    html = "<p>Orders ship same day from our Ohio warehouse.</p>"
    sig = dp.extract_policy_signals(html, None)
    assert sig.fast_ship_phrase is not None
    assert sig.slow_ship_phrase is None


def test_overseas_shipping_phrase_detected():
    html = "<p>Items ship from overseas and customs delays may apply.</p>"
    sig = dp.extract_policy_signals(html, None)
    assert sig.slow_ship_phrase is not None


def test_boilerplate_refund_detected():
    html = (
        "<p>We have a 30-day return policy. To start a return, you can contact us.</p>"
    )
    sig = dp.extract_policy_signals(None, html)
    assert sig.boilerplate_refund is True


def test_custom_refund_not_flagged_as_boilerplate():
    html = "<p>Our bespoke returns process: email support@brand.com within 14 days.</p>"
    sig = dp.extract_policy_signals(None, html)
    assert sig.boilerplate_refund is False


def test_street_address_detected():
    html = "<p>Returns: 123 Main Street, Suite 400.</p>"
    sig = dp.extract_policy_signals(None, html)
    assert sig.has_street_address_anywhere is True


def test_missing_pages_yield_empty_signals():
    sig = dp.extract_policy_signals(None, None)
    assert sig.shipping_found is False
    assert sig.refund_found is False
    assert sig.slow_ship_phrase is None


def test_confidence_high_when_product_label_dropship_and_slow_ship():
    sig = dp.PolicySignals(shipping_found=True, slow_ship_phrase="2-4 weeks")
    out = dp.dropship_confidence(
        "dropship", ["supplier-import traces on 60% of products"], sig
    )
    assert out["verdict"] == "dropship"
    assert out["confidence"] >= 0.6


def test_confidence_low_when_brand_and_fast_ship():
    sig = dp.PolicySignals(shipping_found=True, fast_ship_phrase="same day")
    out = dp.dropship_confidence(
        "brand", ["own name is the vendor on 100% of products"], sig
    )
    assert out["verdict"] == "not_dropship"
    assert out["confidence"] < 0.35


def test_maybe_dropship_for_unclear_label_with_boilerplate_refund():
    sig = dp.PolicySignals(refund_found=True, boilerplate_refund=True)
    out = dp.dropship_confidence("unclear", [], sig)
    assert (
        out["confidence"] < 0.6
    )  # policy alone never crosses into a firm 'dropship' call


def test_confidence_never_exceeds_one_or_goes_negative():
    sig = dp.PolicySignals(
        shipping_found=True,
        slow_ship_phrase="x",
        boilerplate_refund=True,
        refund_found=True,
    )
    out = dp.dropship_confidence("dropship", [], sig)
    assert 0.0 <= out["confidence"] <= 1.0
