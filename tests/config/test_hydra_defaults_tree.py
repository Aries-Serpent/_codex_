from __future__ import annotations

from pathlib import Path

import pytest


def _config_root() -> Path:
    return Path(__file__).resolve().parents[2] / "configs"


def test_defaults_files_exist():
    root = _config_root()
    assert (root / "defaults.yaml").is_file()
    assert (root / "data" / "tiny.yaml").is_file()
    assert (root / "model" / "toy.yaml").is_file()
    assert (root / "train" / "small.yaml").is_file()
    assert (root / "tracking" / "offline.yaml").is_file()


def test_hydra_compose_smoke():
    pytest.importorskip("omegaconf")
    try:
        import hydra as hydra_module
        from hydra import compose, initialize_config_dir
        from omegaconf import OmegaConf
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency guard
        pytest.skip(str(exc))

    if hasattr(hydra_module, "_CONFIG_STACK"):
        pytest.skip("Hydra stub active")

    cfg_dir = _config_root().resolve()
    with initialize_config_dir(config_dir=str(cfg_dir), version_base="1.3"):
        cfg = compose(config_name="defaults")
        # Don't resolve interpolations to avoid errors in test environment
        s = OmegaConf.to_container(cfg, resolve=False)
        assert {"data", "model", "train", "tracking"}.issubset(s.keys())
