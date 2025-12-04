import warnings

import pytest

from codex_ml.models.registry import get_model, model_registry


@pytest.fixture()
def dummy_model_registration():
    name = "__dummy__"

    @model_registry.register(name, override=True)
    def _builder(cfg):
        return {"cfg": cfg}

    yield name


def test_lora_validation_strict_rejects_invalid_dtype(dummy_model_registration):
    with pytest.raises(ValueError):
        get_model(
            dummy_model_registration,
            {"lora": {"enabled": True, "dtype": "not-a-dtype"}},
            adapter_loader=lambda model, cfg: {"adapted": cfg},
        )


def test_lora_validation_non_strict_warns(dummy_model_registration):
    with warnings.catch_warnings(record=True) as caught:
        model = get_model(
            dummy_model_registration,
            {"lora": {"enabled": True, "dtype": "bad", "strict_validation": False}},
            adapter_loader=lambda model, cfg: {"adapted": cfg},
        )
    assert any("Unsupported lora.dtype" in str(w.message) for w in caught)
    assert model.get("adapted") is not None
