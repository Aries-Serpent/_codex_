"""
Test Tracking Guards

Test module for tracking guards.
"""

from __future__ import annotations

import os
from pathlib import Path

from src.codex_utils.tracking.guards import (
    _is_allowlisted,
    _is_remote_uri,
    ensure_mlflow_offline,
    ensure_wandb_offline,
)


def test_is_remote_uri_heuristics():
    assert _is_remote_uri("http://example.com"), "Condition must be true"
    assert _is_remote_uri("https://example.com"), "Condition must be true"
    assert not _is_remote_uri("file:///tmp/x"), "Condition must be true"
    assert not _is_remote_uri("/local/path"), "Condition must be true"
    assert not _is_remote_uri(""), "Condition must be true"


def test_allowlist_basic():
    assert _is_allowlisted("api.github.com", "api.github.com,mlflow.mycorp.local")
    assert not _is_allowlisted("example.com", "api.github.com,mlflow.mycorp.local")


def test_ensure_mlflow_offline_defaults(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.setenv("CODEX_ALLOWLIST_HOSTS", "")
    effective = ensure_mlflow_offline(tmp_path)
    assert effective.startswith("file://"), "Condition must be true"
    assert os.environ.get("MLFLOW_TRACKING_URI", "").startswith("file://")


def test_ensure_mlflow_offline_coerce_remote_when_not_allowlisted(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://mlflow.remote/some/path")
    monkeypatch.setenv("CODEX_ALLOWLIST_HOSTS", "api.github.com")  # not the mlflow host
    effective = ensure_mlflow_offline(tmp_path)
    assert effective.startswith("file://"), "Condition must be true"


def test_ensure_mlflow_offline_respect_allowlisted(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://mlflow.mycorp.local/path")
    monkeypatch.setenv("CODEX_ALLOWLIST_HOSTS", "mlflow.mycorp.local")
    effective = ensure_mlflow_offline(tmp_path)
    assert effective == "http://mlflow.mycorp.local/path", "effective is not valid"


def test_ensure_wandb_offline_default(monkeypatch):
    monkeypatch.delenv("WANDB_MODE", raising=False)
    mode = ensure_wandb_offline()
    assert mode == "offline", "mode is not valid"
    assert os.environ["WANDB_MODE"] == "offline", "Condition must be true"
