"""
Test Offline Wandb

Test module for offline wandb.
"""

from __future__ import annotations

import os

import pytest

from src.training.offline_wandb import force_offline


def test_force_offline_sets_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WANDB_MODE", raising=False)
    force_offline()
    assert os.environ.get("WANDB_MODE") == "offline"
