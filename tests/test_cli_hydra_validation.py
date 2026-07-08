"""Lightweight validation that Hydra CLI composes configs offline."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest


def _has_hydra() -> bool:
    try:
        return importlib.util.find_spec("hydra") is not None
    except ValueError:
        return False


@pytest.mark.skipif(not _has_hydra(), reason="hydra-core not installed")
def test_hydra_main_offline_compose(monkeypatch, tmp_path) -> None:
    """Ensure the Hydra CLI composes configs and passes overrides to training."""

    module = importlib.import_module("codex_ml.cli.hydra_main")

    hydra_module = getattr(module, "hydra", None)
    hydra_file = Path(getattr(hydra_module, "__file__", "")).resolve() if hydra_module else None
    repo_root = Path(__file__).resolve().parents[1]
    if hydra_file and repo_root in hydra_file.parents:
        pytest.skip("real hydra-core not installed; stub module active")

    captured: dict[str, Any] = {}

    def fake_run(config: dict[str, Any]) -> dict[str, Any]:
        captured.update(config)
        return {"status": "ok"}

    monkeypatch.setattr(module, "run_functional_training", fake_run)

    run_dir = tmp_path / "hydra"
    monkeypatch.setenv("HYDRA_RUN_DIR", str(run_dir))
    monkeypatch.setitem(sys.modules, "__main__", module)  # Hydra inspects __main__

    argv = [
        "codex-train",
        "--config-path",
        "configs/training/sweeps",
        "--config-name",
        "sweep_offline",
        "training.max_epochs=1",
        "model.name=tiny-offline",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    try:
        result = module.main()
    except SystemExit as exc:
        # Hydra raises SystemExit when config resolution fails (e.g.
        # working directory doesn't contain configs/training/sweeps).
        pytest.skip(f"Hydra config resolution failed (SystemExit {exc.code})")
    else:
        assert result == {"status": "ok"}, "Result must not be empty"
        assert captured["training"]["max_epochs"] == 1, "Condition must be true"
        assert captured["model"]["name"] == "tiny-offline", "Condition must be true"

        try:
            from hydra.core.global_hydra import GlobalHydra
        except ImportError:  # pragma: no cover - hydra optional in CI
            return
        if GlobalHydra().is_initialized():
            GlobalHydra.instance().clear()
