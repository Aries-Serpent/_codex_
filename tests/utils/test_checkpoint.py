"""Lightweight coverage for :mod:`utils.checkpoint` legacy helpers."""
pytest.importorskip("tensorboard")

from __future__ import annotations

import types

import pytest

import utils.checkpoint as checkpoint


def test_ensure_torch_available_raises(monkeypatch):
    monkeypatch.setattr(checkpoint, "_torch", None)
    with pytest.raises(RuntimeError):
        checkpoint._ensure_torch_available()


def test_torch_supports_weights_only(monkeypatch):
    mock_torch = types.SimpleNamespace(load=lambda filename=None, weights_only=True: None)
    monkeypatch.setattr(checkpoint, "_torch", mock_torch)
    assert checkpoint._torch_supports_weights_only() is True, "Condition must be true"
