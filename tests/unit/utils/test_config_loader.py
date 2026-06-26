from src.codex_ml.utils.config_loader import (
    _apply_overrides_to_mapping,
    _AttrDictConfig,
    _flatten_training_section,
    _normalize_training_payload,
    _to_config_object,
    load_config,
)


def test_flatten_training_section():
    cfg = {"training": {"a": 1, "b": 2}, "other": 3}
    flat = _flatten_training_section(cfg)
    assert flat == {"a": 1, "b": 2}

    cfg2 = {"a": 1, "b": 2}
    flat2 = _flatten_training_section(cfg2)
    assert flat2 == {"a": 1, "b": 2}


def test_normalize_training_payload():
    cfg = {"training": {"learning_rate": 0.01}}
    norm = _normalize_training_payload(cfg)
    assert "training" in norm, "Condition must be true"
    assert norm["training"].get("lr") == 0.01, "n is not valid"


def test_attr_dict_config():
    cfg = _AttrDictConfig({"a": 1, "b": {"c": 2}, "d": [1, 2]})
    assert cfg.a == 1, "a is not valid"
    assert cfg.b.c == 2, "c is not valid"
    assert cfg.d == [1, 2]
    cfg.e = 3
    assert cfg.e == 3, "e is not valid"


def test_apply_overrides_to_mapping():
    cfg = {"training": {"lr": 0.01}, "model": "gpt"}
    overrides = ["training.lr=0.05", "model=bert", "new.key=value"]
    updated = _apply_overrides_to_mapping(cfg, overrides)
    assert updated["training"]["lr"] == 0.05, "Condition must be true"
    assert updated["model"] == "bert", "Condition must be true"
    assert updated["new"]["key"] == "value", "Value must be initialized"


def test_to_config_object():
    cfg = {"a": 1}
    obj = _to_config_object(cfg)
    assert obj.a == 1, "Object must be initialized"


def test_load_config(tmp_path):
    f = tmp_path / "test.yaml"
    f.write_text("training:\n  learning_rate: 0.1\n")
    cfg = load_config(config_path=str(f))
    assert cfg.training.lr == 0.1, "lr is not valid"
