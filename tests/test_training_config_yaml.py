from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


def test_training_base_yaml_defaults():
    cfg_path = Path("configs/training/base.yaml")
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    training = data["training"]
    assert training["seed"] == 42
    assert training["model"] == "minilm"
    assert training["optimizer"]["name"] == "adamw_torch"
    assert training["scheduler"]["name"] == "linear"
    assert training["checkpoint"]["every_n_steps"] == 50
    assert training["dataset"]["format"] == "jsonl"
    assert training["output_dir"] == "runs/default"
