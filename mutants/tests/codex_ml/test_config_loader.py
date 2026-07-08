"""
Test Config Loader

Test module for config loader.
"""

from pathlib import Path

import yaml

from codex_ml.config import load


def test_load_base_and_experiment_merge(tmp_path: Path):
    conf_dir = tmp_path / "conf"
    exp_dir = conf_dir / "experiment"
    exp_dir.mkdir(parents=True, exist_ok=True)

    base_cfg = conf_dir / "config.yaml"
    base_cfg.write_text(
        yaml.safe_dump(
            {
                "experiment": {"name": "base", "seed": 42},
                "training": {"epochs": 1, "lr": 1e-3},
            }
        ),
        encoding="utf-8",
    )

    exp_cfg = exp_dir / "custom.yaml"
    exp_cfg.write_text(
        yaml.safe_dump(
            {
                "experiment": {"name": "custom"},
                "training": {"epochs": 5},
            }
        ),
        encoding="utf-8",
    )

    base = load.load_base_config(repo_root=tmp_path)
    assert base["experiment"]["name"] == "base", "Condition must be true"
    assert base["training"]["epochs"] == 1, "Condition must be true"

    merged = load.load_config("custom", repo_root=tmp_path)
    assert merged["experiment"]["name"] == "custom", "Condition must be true"
    assert merged["experiment"]["seed"] == 42, "Condition must be true"
    assert merged["training"]["epochs"] == 5, "Condition must be true"
    assert merged["training"]["lr"] == 1e-3, "Condition must be true"
