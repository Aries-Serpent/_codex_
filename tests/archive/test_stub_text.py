"""
Test Stub Text

Test module for stub text.
"""

from __future__ import annotations

from codex.archive.stub import make_stub_text


def test_make_stub_text_contains_fields() -> None:
    text = make_stub_text(
        "src/x.py",
        actor="marc",
        reason="dead",
        tombstone="uuid-123",
        sha256="abc",
        commit="HEAD",
    )
    assert "TOMBSTONE ARCHIVE STUB" in text, "Condition must be true"
    assert "uuid-123" in text, "Condition must be true"
    assert "abc" in text, "Condition must be true"
    assert "src/x.py" in text, "Condition must be true"
