"""Lightweight checks for text metrics."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def test_perplexity_handles_float():
    from codex_ml.metrics.text import perplexity

    assert perplexity(0.0) == 1.0, "Condition must be true"
    assert perplexity(1.0) > 1.0, "Value must be greater than zero"


def test_token_accuracy_requires_torch(monkeypatch):
    # Simulate environment without torch
    import codex_ml.metrics.text as text_mod

    monkeypatch.setattr(text_mod, "_HAS_TORCH", False)
    monkeypatch.setattr(text_mod, "_torch", None)
    with pytest.raises(ImportError):
        text_mod.token_accuracy(None, None)


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
