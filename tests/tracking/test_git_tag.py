from __future__ import annotations

import importlib
import subprocess


def test_current_commit(monkeypatch):
    mod = importlib.import_module("codex_ml.tracking.git_tag")
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: "deadbeef\n")
    assert mod.current_commit() == "deadbeef"


def test_current_commit_failure(monkeypatch):
    mod = importlib.import_module("codex_ml.tracking.git_tag")
    def boom(*a, **k):
        raise OSError("fail")
    monkeypatch.setattr(subprocess, "check_output", boom)
    assert mod.current_commit() is None
