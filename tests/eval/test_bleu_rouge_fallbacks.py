#!/usr/bin/env python3
"""Tests for optional metric fallbacks and end-to-end emission semantics."""

from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

pytest.importorskip("datasets")

from codex_ml.eval.eval_runner import evaluate_datasets  # noqa: E402
from codex_ml.metrics.registry import get_metric  # noqa: E402


def test_bleu_rouge_fallbacks(monkeypatch, tmp_path: Path):
    # Simulate missing optional deps
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if (
            name.startswith("nltk")
            or name.startswith("rouge_score")
            or name.startswith("sacrebleu")
        ):
            raise ImportError("missing optional dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    # Registry should return callables that yield None
    bleu = get_metric("bleu")
    rouge = get_metric("rougeL")
    assert bleu(["a"], ["a"]) is None
    assert rouge(["a"], ["a"]) is None

    # End-to-end: values are None in NDJSON when optional deps are absent
    out = tmp_path
    evaluate_datasets(["toy_copy_task"], ["bleu", "rougeL"], out)
    nd = out / "metrics.ndjson"
    rows = [json.loads(line) for line in nd.read_text().splitlines()]
    assert len(rows) == 2
    assert all(r["value"] is None for r in rows)
