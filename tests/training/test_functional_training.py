"""Lightweight coverage for training.functional_training helpers."""

from __future__ import annotations

from pathlib import Path

from training import functional_training as ft


def test_normalize_and_local_detection(tmp_path):
    assert ft._normalize_identifier(None) is None
    assert ft._normalize_identifier(Path("/tmp")) == "/tmp"
    assert ft._looks_like_local_source("./data/file.txt")
    assert not ft._looks_like_local_source("hf://org/model")


def test_system_metrics_collection(monkeypatch):
    # Patch the source module because _maybe_collect_system_metrics is defined
    # in src.training.functional_training and looks up ``collect_system_metrics``
    # in its own module globals, not in the legacy ``training.functional_training``
    # shim namespace.
    import src.training.functional_training as _src_ft

    monkeypatch.setattr(_src_ft, "collect_system_metrics", lambda: {"cpu": 1.0, "mem": 2})
    metrics = ft._maybe_collect_system_metrics(True)
    assert metrics == {"cpu": 1.0, "mem": 2.0}

    metrics_disabled = ft._maybe_collect_system_metrics(False)
    assert metrics_disabled is None
