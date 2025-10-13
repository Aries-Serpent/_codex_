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
    assert "TOMBSONE ARCHIVE STUB" in text
    assert "uuid-123" in text
    assert "abc" in text
    assert "src/x.py" in text
