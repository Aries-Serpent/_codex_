"""Tests for :mod:`codex_ml.training.dp_config`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def test_dp_config_as_dict_disabled():
    from codex_ml.training.dp_config import (
        DifferentialPrivacyConfig,
        make_private_model,
    )

    cfg = DifferentialPrivacyConfig(
        enabled=False, epsilon=0.5, delta=1e-6, max_grad_norm=0.5, noise_multiplier=1.2
    )
    result = cfg.as_dict()
    assert result["enabled"] is False, "Result must not be empty"
    model, opt, loader, engine = make_private_model("m", "o", "d", cfg)
    assert model == "m", "model is not valid"
    assert opt == "o", "opt is not valid"
    assert loader == "d", "loader is not valid"
    assert engine is None, "engine is not valid"


def test_dp_config_requires_opacus(monkeypatch):
    from codex_ml.training.dp_config import DifferentialPrivacyConfig

    monkeypatch.delenv("OPACUS_INSTALLED", raising=False)
    sys.modules.pop("opacus", None)

    with pytest.raises(ImportError):
        DifferentialPrivacyConfig(enabled=True)


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
