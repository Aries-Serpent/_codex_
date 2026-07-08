"""
Test Session Hooks Warnings

Test module for session hooks warnings.
"""

from pathlib import Path
from unittest.mock import patch

from codex.logging import session_hooks


def _fail_open(self, *args, **kwargs):
    raise OSError("fail")


def test_safe_write_text_warns(tmp_path, monkeypatch):
    path = tmp_path / "a.txt"
    monkeypatch.setattr(Path, "open", _fail_open)
    # Patch the module-level logger directly so the assertion is immune to
    # logging-propagation state set by other tests (RP-020 fix).
    with patch.object(session_hooks.logger, "warning") as mock_warn:
        session_hooks._safe_write_text(path, "data")
    mock_warn.assert_called_once()


def test_safe_append_json_line_warns(tmp_path, monkeypatch):
    path = tmp_path / "a.ndjson"
    monkeypatch.setattr(Path, "open", _fail_open)
    with patch.object(session_hooks.logger, "warning") as mock_warn:
        session_hooks._safe_append_json_line(path, {"a": 1})
    mock_warn.assert_called_once()
