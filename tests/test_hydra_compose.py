"""Ensure Hydra structured configs compose correctly."""

from __future__ import annotations

import importlib.util
import site
from pathlib import Path
from typing import Tuple

import pytest

from codex_ml.cli.config import register_configs


def _import_hydra_compose() -> Tuple[object, object]:
    """Import Hydra compose/initialize without clashing with the local package."""

    module = pytest.importorskip("hydra")
    module_path = Path(getattr(module, "__file__", ""))
    if "site-packages" in str(module_path):
        return module.compose, module.initialize  # type: ignore[attr-defined]

    for root in site.getsitepackages():
        candidate = Path(root) / "hydra" / "__init__.py"
        if candidate.exists():
            spec = importlib.util.spec_from_file_location("_hydra_core", candidate)
            if spec and spec.loader:
                hydra_core = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(hydra_core)
                return hydra_core.compose, hydra_core.initialize  # type: ignore[attr-defined]

    pytest.skip("hydra-core not available; local package shadows import")


def test_composes_and_overrides() -> None:
    """Structured configs should compose experiment presets and overrides."""

    compose, initialize = _import_hydra_compose()

    register_configs()
    with initialize(version_base="1.3", config_path=None):
        cfg = compose(
            config_name="app",
            overrides=["experiment=debug", "training.max_epochs=2"],
        )

    assert cfg.training.max_epochs == 2
    assert cfg.model.name
