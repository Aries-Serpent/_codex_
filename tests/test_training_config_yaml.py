from pathlib import Path

import yaml


def test_training_base_yaml_defaults():
    cfg_path = Path("configs/training/base.yaml")
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    training = data["training"]
    assert training["seed"] == 42
    assert training["model"] == "minilm"
    assert training["dataset"]["format"] == "jsonl"
    assert training["output_dir"] == "runs/default"
