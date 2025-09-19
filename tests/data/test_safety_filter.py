import pytest

pytest.importorskip("omegaconf")

from codex_ml.data.loader import apply_safety_filter


def test_safety_filter():
    texts = ["secret", "public"]

    def filt(t: str) -> str:
        return t.replace("secret", "[x]")

    out = apply_safety_filter(texts, True, filt)
    assert out[0] == "[x]"
    assert out[1] == "public"
    assert apply_safety_filter(texts, False, filt) == texts
