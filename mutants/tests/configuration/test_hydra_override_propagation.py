"""Regression tests for Hydra overrides used in Codex configs."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path

import pytest

from codex_ml.cli.config import register_configs
from tests.test_hydra_compose import _import_hydra_compose


def _hydrate_hydra() -> tuple[Callable[..., object], Callable[..., object], type]:
    compose, initialize = _import_hydra_compose()
    module_root = compose.__module__.split(".")[0]
    global_module = importlib.import_module(f"{module_root}.core.global_hydra")
    return compose, initialize, global_module.GlobalHydra


@pytest.fixture(scope="module")
def hydra_components() -> tuple[Callable[..., object], Callable[..., object], type]:
    return _hydrate_hydra()


@pytest.fixture(autouse=True)
def reset_hydra_state(
    hydra_components: tuple[Callable[..., object], Callable[..., object], type],
) -> None:
    """Ensure each test composes configs from a clean Hydra singleton."""

    _, _, GlobalHydra = hydra_components
    with suppress(Exception):
        if GlobalHydra.instance().is_initialized():
            GlobalHydra.instance().clear()
    yield
    with suppress(Exception):
        if GlobalHydra.instance().is_initialized():
            GlobalHydra.instance().clear()


def test_experiment_overrides_and_manual_values(
    hydra_components: tuple[Callable[..., object], Callable[..., object], type], tmp_path: Path
) -> None:
    """Experiment presets should compose and allow explicit overrides."""

    compose, initialize, _ = hydra_components

    register_configs()
    with initialize(version_base="1.3", config_path=None):
        base_cfg = compose(config_name="app")
        debug_cfg = compose(config_name="app", overrides=["experiment=debug"])
        tuned_cfg = compose(
            config_name="app",
            overrides=[
                "experiment=debug",
                "training.batch_size=4",
                f"training.log_dir={tmp_path}",
            ],
        )

    assert base_cfg.training.batch_size == 8, "batch_size is not valid"
    assert debug_cfg.training.batch_size == 2, "batch_size is not valid"
    assert tuned_cfg.training.batch_size == 4, "batch_size is not valid"
    assert str(tuned_cfg.training.log_dir) == str(tmp_path), "Condition must be true"


def test_seed_and_safeguard_overrides_are_respected(
    hydra_components: tuple[Callable[..., object], Callable[..., object], type], tmp_path: Path
) -> None:
    """CLI-style overrides must propagate to the structured config dataclass."""

    compose, initialize, _ = hydra_components

    register_configs()
    metrics_path = tmp_path / "metrics" / "run.ndjson"
    with initialize(version_base="1.3", config_path=None):
        cfg = compose(
            config_name="app",
            overrides=[
                "experiment=fast",
                "training.seed=123",
                "training.deterministic=false",
                f"training.metrics_out={metrics_path}",
                "logging.tensorboard=true",
            ],
        )

    assert cfg.training.seed == 123, "seed is not valid"
    assert cfg.training.deterministic is False, "deterministic is not valid"
    assert cfg.logging.tensorboard is True, "tensorboard is not valid"
    assert str(cfg.training.metrics_out) == str(metrics_path), "Condition must be true"
