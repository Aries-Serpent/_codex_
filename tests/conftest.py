from __future__ import annotations

import builtins
import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    yield


@pytest.fixture
def no_sentencepiece(monkeypatch):
    orig_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "sentencepiece":
            raise ImportError("sentencepiece missing")
        return orig_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "sentencepiece", raising=False)
    yield
