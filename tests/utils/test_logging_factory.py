"""Smoke tests for :mod:`utils.logging_factory`."""

from __future__ import annotations

import logging
import sys
from types import SimpleNamespace

from utils import logging_factory


def test_init_logging_offline(monkeypatch):
    monkeypatch.delenv("WANDB_MODE", raising=False)
    logger = logging_factory.init_logging(mode="offline", project="test-project")
    assert isinstance(logger, logging.Logger)
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_init_logging_wandb_stub(monkeypatch):
    fake_wandb = SimpleNamespace(init=lambda project=None: None)
    monkeypatch.setitem(sys.modules, "wandb", fake_wandb)
    monkeypatch.delenv("WANDB_API_KEY", raising=False)

    logger = logging_factory.init_logging(mode="wandb", project="demo")
    assert logger.name == "demo", "name is not valid"
    # WANDB_MODE should be forced offline when no API key present
    assert logging_factory.os.environ.get("WANDB_MODE") == "offline", "logging_fact is not valid"
