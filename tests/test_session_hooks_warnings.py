import logging
from pathlib import Path

from codex.logging import session_hooks


def _fail_open(self, *args, **kwargs):
    raise OSError("fail")


def test_safe_write_text_warns(tmp_path, caplog, monkeypatch):
    path = tmp_path / "a.txt"
    monkeypatch.setattr(Path, "open", _fail_open)
    with caplog.at_level(logging.WARNING):
        session_hooks._safe_write_text(path, "data")
    assert any(rec.levelno == logging.WARNING for rec in caplog.records)


def test_safe_append_json_line_warns(tmp_path, caplog, monkeypatch):
    path = tmp_path / "a.ndjson"
    monkeypatch.setattr(Path, "open", _fail_open)
    with caplog.at_level(logging.WARNING):
        session_hooks._safe_append_json_line(path, {"a": 1})
    assert any(rec.levelno == logging.WARNING for rec in caplog.records)
