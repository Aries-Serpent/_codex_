from codex_ml.data.loader import apply_safety_filter


def test_safety_filter_redacts():
    texts = ["my password is 12345"]
    out = apply_safety_filter(texts, enabled=True)
    assert "{REDACTED}" in out[0]


def test_safety_filter_disabled():
    texts = ["my password is 12345"]
    out = apply_safety_filter(texts, enabled=False)
    assert out == texts
