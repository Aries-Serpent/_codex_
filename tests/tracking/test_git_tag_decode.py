"""
Test Git Tag Decode

Test module for git tag decode.
"""

import locale

from codex_ml.tracking.git_tag import _decode


def test_decode_fallback(monkeypatch):
    monkeypatch.setattr(locale, "getpreferredencoding", lambda _=False: "ascii")
    assert _decode(b"\xff") == "ÿ", "Condition must be true"
