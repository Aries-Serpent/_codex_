from __future__ import annotations

import pytest


def test_register_and_get_model():
    from codex_ml.models.loader_registry import (
        get_model,
        list_models,
        register_model,
        unregister_model,
    )

    @register_model("dummy-model")
    def _factory(**kwargs):
        return {"model": "dummy", **kwargs}

    try:
        factory = get_model("dummy-model")
        produced = factory(device_map="cpu")
        assert produced["model"] == "dummy"
        assert "dummy-model" in list_models()
    finally:
        unregister_model("dummy-model")


def test_registry_disable_env(monkeypatch):
    from codex_ml.models.loader_registry import (
        get_model,
        register_model,
        unregister_model,
    )

    monkeypatch.setenv("CODEX_MODEL_REGISTRY_DISABLE", "1")

    @register_model("env-disabled")
    def _factory(**kwargs):  # pragma: no cover - should not run
        return kwargs

    try:
        with pytest.raises(KeyError):
            get_model("env-disabled")
    finally:
        unregister_model("env-disabled")
        monkeypatch.delenv("CODEX_MODEL_REGISTRY_DISABLE", raising=False)


def test_modeling_prefers_registry():
    from codex_ml.models.loader_registry import register_model, unregister_model
    from codex_ml.utils import modeling

    @register_model("registry-demo")
    def _factory(**kwargs):
        return {"model": "m", "tokenizer": "t"}

    try:
        model, tokenizer = modeling.load_model_and_tokenizer("registry-demo")
        assert model == "m"
        assert tokenizer == "t"
    finally:
        unregister_model("registry-demo")


def test_loader_prefers_registry_kwargs():
    from codex_ml.modeling import codex_model_loader
    from codex_ml.models.loader_registry import register_model, unregister_model

    captured: dict[str, object] = {}

    @register_model("loader-demo")
    def _factory(**kwargs):
        captured.update(kwargs)
        return object()

    try:
        res = codex_model_loader.load_model_with_optional_lora(
            "loader-demo",
            dtype="fp16",
            device_map="cpu",
            lora_enabled=True,
            lora_path="/tmp/adapter",
            lora_r=4,
            extra_flag=True,
        )
        assert res.__class__ is object
        assert captured["model_name"] == "loader-demo"
        assert captured["lora_enabled"] is True
        assert captured["dtype"] == "fp16"
        assert captured["device_map"] == "cpu"
        assert captured["extra_flag"] is True
    finally:
        unregister_model("loader-demo")
