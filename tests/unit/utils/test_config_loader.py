import pytest
from pathlib import Path
from src.codex_ml.utils.config_loader import _flatten_training_section

def test_flatten_training_section():
    cfg = {"training": {"a": 1, "b": 2}, "other": 3}
    flat = _flatten_training_section(cfg)
    assert flat == {"a": 1, "b": 2}
    
    cfg2 = {"a": 1, "b": 2}
    flat2 = _flatten_training_section(cfg2)
    assert flat2 == {"a": 1, "b": 2}

# In config_loader, there's likely load_config or something. Let's inspect config_loader for other methods.

from src.codex_ml.utils.config_loader import (
    _normalize_training_payload,
    _to_config_object,
    _apply_overrides_to_mapping,
    load_training_cfg,
    load_config,
    _AttrDictConfig
)

def test_normalize_training_payload():
    cfg = {"training": {"learning_rate": 0.01}}
    norm = _normalize_training_payload(cfg)
    assert "training" in norm
    assert norm["training"].get("lr") == 0.01
    
def test_attr_dict_config():
    cfg = _AttrDictConfig({"a": 1, "b": {"c": 2}, "d": [1, 2]})
    assert cfg.a == 1
    assert cfg.b.c == 2
    assert cfg.d == [1, 2]
    cfg.e = 3
    assert cfg.e == 3

def test_apply_overrides_to_mapping():
    cfg = {"training": {"lr": 0.01}, "model": "gpt"}
    overrides = ["training.lr=0.05", "model=bert", "new.key=value"]
    updated = _apply_overrides_to_mapping(cfg, overrides)
    assert updated["training"]["lr"] == 0.05
    assert updated["model"] == "bert"
    assert updated["new"]["key"] == "value"

def test_to_config_object():
    cfg = {"a": 1}
    obj = _to_config_object(cfg)
    assert obj.a == 1

def test_load_config(tmp_path):
    f = tmp_path / "test.yaml"
    f.write_text("training:\n  learning_rate: 0.1\n")
    cfg = load_config(config_path=str(f))
    assert cfg.training.lr == 0.1
