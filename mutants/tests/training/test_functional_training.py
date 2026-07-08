import pytest

pytest.importorskip("tensorboard")
"""Lightweight coverage for training.functional_training helpers."""

from __future__ import annotations

from pathlib import Path

from training import functional_training as ft


def test_normalize_and_local_detection(tmp_path):
    assert ft._normalize_identifier(None) is None, "Condition must be true"
    assert ft._normalize_identifier(Path("/tmp")) == "/tmp", "Condition must be true"
    assert ft._looks_like_local_source("./data/file.txt"), "Data must not be empty"
    assert not ft._looks_like_local_source("hf://org/model"), "Condition must be true"


def test_system_metrics_collection(monkeypatch):
    monkeypatch.setattr(ft, "collect_system_metrics", lambda: {"cpu": 1.0, "mem": 2})
    metrics = ft._maybe_collect_system_metrics(True)
    assert metrics == {"cpu": 1.0, "mem": 2.0}

    metrics_disabled = ft._maybe_collect_system_metrics(False)
    assert metrics_disabled is None, "metrics_disabled is not valid"
