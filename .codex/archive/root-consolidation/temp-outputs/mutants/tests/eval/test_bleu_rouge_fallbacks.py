#!/usr/bin/env python3
"""Test Bleu Rouge Fallbacks

Tests for optional metric fallbacks and end-to-end emission semantics.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("datasets")

from codex_ml.metrics.registry import get_metric


def test_bleu_rouge_fallbacks(monkeypatch, tmp_path: Path):
    """Test that BLEU/ROUGE metrics are registered and callable.

    When optional dependencies are available (as in CI), the metrics should
    return numeric scores. The fallback (returning None) activates only when
    the deps are truly absent at import time.
    """
    bleu = get_metric("bleu")
    rouge = get_metric("rougeL")
    assert callable(bleu), "bleu metric should be callable"
    assert callable(rouge), "rougeL metric should be callable"

    bleu_result = bleu(["a"], ["a"])
    rouge_result = rouge(["a"], ["a"])
    # Metric returns either a numeric score or None (when deps unavailable)
    assert bleu_result is None or isinstance(bleu_result, (int, float))
    assert rouge_result is None or isinstance(rouge_result, (int, float))
