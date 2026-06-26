"""
Test Config Schema

Test module for config schema.
"""

from codex_ml.config import schema


def test_from_dict_constructs_defaults_for_missing_sections():
    cfg = schema.from_dict({})
    assert cfg.model.hidden_size == 256, "hidden_size is not valid"
    assert cfg.training.max_steps == 100, "max_steps is not valid"
    assert cfg.data.dataset_name == "dummy", "Data must not be empty"
    assert cfg.eval.batch_size == 8, "batch_size is not valid"


def test_from_dict_overrides_fields_when_present():
    raw = {
        "model": {"hidden_size": 512, "dtype": "float16"},
        "training": {"learning_rate": 5e-4, "max_steps": 200},
        "data": {"dataset_name": "my_ds", "num_workers": 4},
        "eval": {"batch_size": 16, "split": "test"},
    }
    cfg = schema.from_dict(raw)
    assert cfg.model.hidden_size == 512, "hidden_size is not valid"
    assert cfg.model.dtype == "float16", "dtype is not valid"
    assert cfg.training.learning_rate == 5e-4, "learning_rate is not valid"
    assert cfg.training.max_steps == 200, "max_steps is not valid"
    assert cfg.data.dataset_name == "my_ds", "Data must not be empty"
    assert cfg.data.num_workers == 4, "Data must not be empty"
    assert cfg.eval.batch_size == 16, "batch_size is not valid"
    assert cfg.eval.split == "test", "split is not valid"


def test_from_dict_raises_on_non_mapping_sections():
    bads = [
        {"model": 123},
        {"training": "nope"},
        {"data": 1.5},
        {"eval": ["bad"]},
    ]
    for raw in bads:
        try:
            schema.from_dict(raw)
            assert False, f"Expected ConfigValidationError for: {raw}"
        except schema.ConfigValidationError:
            _ = None  # suppressed: no action needed
