from __future__ import annotations

import types
from typing import Any

import pytest

from codex_ml.modeling import factory


def _fake_loader(name: str, **kwargs: Any) -> tuple[str, dict[str, Any]]:
    return name, kwargs


def test_build_model_validates_dtype(monkeypatch):
    captured: dict[str, Any] = {}

    fake_torch = types.SimpleNamespace(float16=object())
    monkeypatch.setattr(factory, "optional_import", lambda _: (fake_torch, True))

    config = factory.ModelFactoryConfig(
        model_name_or_path="stub",
        dtype="float16",
    )

    result_name, loader_kwargs = factory.build_model(config, loader=_fake_loader)
    captured.update(loader_kwargs)

    assert result_name == "stub"
    assert captured["dtype"] == "float16"


def test_build_model_rejects_unknown_dtype(monkeypatch):
    monkeypatch.setattr(factory, "optional_import", lambda _: (types.SimpleNamespace(), True))

    config = factory.ModelFactoryConfig(model_name_or_path="stub", dtype="does_not_exist")

    with pytest.raises(ValueError, match="Unknown torch dtype"):
        factory.build_model(config, loader=_fake_loader)


def test_build_model_requires_torch_for_dtype(monkeypatch):
    monkeypatch.setattr(factory, "optional_import", lambda _: (None, False))

    config = factory.ModelFactoryConfig(model_name_or_path="stub", dtype="float16")

    with pytest.raises(RuntimeError, match="torch must be installed"):
        factory.build_model(config, loader=_fake_loader)


def test_build_model_blocks_peft_without_env(monkeypatch):
    monkeypatch.delenv(factory.ENV_ENABLE_PEFT, raising=False)

    peft_cfg = factory.PeftAdapterConfig(path="adapter")
    config = factory.ModelFactoryConfig(
        model_name_or_path="stub",
        enable_peft=True,
        peft=peft_cfg,
    )

    _, loader_kwargs = factory.build_model(config, loader=_fake_loader)
    assert loader_kwargs.get("lora_enabled") is False
    assert "lora_path" not in loader_kwargs


def test_build_model_enables_peft_with_env(monkeypatch):
    monkeypatch.setenv(factory.ENV_ENABLE_PEFT, "1")

    peft_cfg = factory.PeftAdapterConfig(
        path="adapter", r=4, alpha=8, dropout=0.1, target_modules=["q", "v"]
    )
    config = factory.ModelFactoryConfig(
        model_name_or_path="stub",
        enable_peft=True,
        peft=peft_cfg,
    )

    _, loader_kwargs = factory.build_model(config, loader=_fake_loader)

    assert loader_kwargs["lora_enabled"] is True
    assert loader_kwargs["lora_path"] == "adapter"
    assert loader_kwargs["lora_r"] == 4
    assert loader_kwargs["lora_alpha"] == 8
    assert loader_kwargs["lora_dropout"] == pytest.approx(0.1)
    assert loader_kwargs["lora_target_modules"] == ["q", "v"]
