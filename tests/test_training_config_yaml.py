from pathlib import Path

import yaml


def test_training_base_yaml_defaults():
    cfg_path = Path("configs/training/base.yaml")
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    assert data["seed"] == 42
    assert data["model"] == "minilm"
    assert data["dataset"]["format"] == "jsonl"
    assert data["output_dir"] == "runs/default"
