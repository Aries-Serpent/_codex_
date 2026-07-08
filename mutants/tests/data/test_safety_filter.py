"""
Test Safety Filter

Test module for safety filter.
"""

import pytest

pytest.importorskip("omegaconf")

from codex_ml.data.loader import apply_safety_filter


def test_safety_filter():
    texts = ["secret", "public"]

    def filt(t: str) -> str:
        return t.replace("secret", "[x]")

    out = apply_safety_filter(texts, True, filt)
    assert out[0] == "[x]", "Condition must be true"
    assert out[1] == "public", "Condition must be true"
    assert apply_safety_filter(texts, False, filt) == texts
