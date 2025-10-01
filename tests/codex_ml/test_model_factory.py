from __future__ import annotations

import types

import pytest

import codex_ml.models.factory as factory


class _DType(str):
    def __new__(cls, name: str) -> "_DType":
        return str.__new__(cls, name)


class _Device:
    def __init__(self, kind: str) -> None:
        self.type = kind

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Device({self.type})"


class TorchStub:
    dtype = _DType
    float32 = _DType("float32")
    float16 = _DType("float16")
    bfloat16 = _DType("bfloat16")
    device = _Device

    class cuda:
        @staticmethod
        def is_available() -> bool:
            return False


class DummyModule:
    def __init__(self) -> None:
        self.current_dtype: object = TorchStub.float32
        self.current_device: object = TorchStub.device("cpu")
        self.calls: list[tuple[str, object]] = []

    def to(self, *, dtype: object | None = None, device: object | None = None):
        if dtype is not None:
            self.current_dtype = dtype
            self.calls.append(("dtype", dtype))
        if device is not None:
            if isinstance(device, str):
                device = TorchStub.device(device)
            self.current_device = device
            self.calls.append(("device", device))
        return self


@pytest.fixture(autouse=True)
def patch_torch(monkeypatch):
    monkeypatch.setattr(factory, "torch", TorchStub(), raising=False)
    yield
    monkeypatch.setattr(factory, "torch", None, raising=False)


def _builder_with_kwargs(**kwargs: object) -> DummyModule:
    marker = kwargs.pop("marker", None)
    if marker is not None:
        marker["seen"] = dict(kwargs)
    return DummyModule()


def test_factory_applies_dtype_and_device():
    marker: dict[str, object] = {}
    model = factory.create_model(
        _builder_with_kwargs,
        config={"marker": marker},
        dtype="float16",
        device="auto",
    )
    assert isinstance(model, DummyModule)
    assert marker["seen"] == {}
    assert model.current_dtype == TorchStub.float16
    assert isinstance(model.current_device, _Device)
    assert model.current_device.type == "cpu"


def test_factory_lora_env_guard(monkeypatch):
    base_model = DummyModule()
    calls: list[tuple[object, factory.LoraBuildCfg | None]] = []

    def fake_builder(**_: object) -> DummyModule:
        return base_model

    def fake_build_lora(model: object, cfg: factory.LoraBuildCfg | None = None) -> object:
        calls.append((model, cfg))
        return types.SimpleNamespace(model=model, cfg=cfg)

    monkeypatch.setattr(factory, "build_lora", fake_build_lora)
    monkeypatch.delenv(factory.ENV_ENABLE_PEFT, raising=False)

    result = factory.create_model(fake_builder, lora_cfg={"r": 2}, enable_peft=False)
    assert result is base_model
    assert calls == []

    monkeypatch.setenv(factory.ENV_ENABLE_PEFT, "1")
    calls.clear()
    wrapped = factory.create_model(fake_builder, lora_cfg={"r": 4})
    assert len(calls) == 1
    model, cfg = calls[0]
    assert model is base_model
    assert isinstance(cfg, factory.LoraBuildCfg)
    assert cfg.r == 4
    assert getattr(wrapped, "cfg", None) == cfg

    calls.clear()
    wrapped = factory.create_model(fake_builder, config={"lora": {"r": 8}}, enable_peft=True)
    assert len(calls) == 1
    _, cfg = calls[0]
    assert cfg.r == 8
    assert getattr(wrapped, "cfg", None) == cfg


def test_factory_skips_lora_when_no_config(monkeypatch):
    calls: list[tuple[object, factory.LoraBuildCfg | None]] = []

    def fake_build_lora(model: object, cfg: factory.LoraBuildCfg | None = None) -> object:
        calls.append((model, cfg))
        return model

    monkeypatch.setattr(factory, "build_lora", fake_build_lora)
    monkeypatch.setenv(factory.ENV_ENABLE_PEFT, "1")

    model = factory.create_model(_builder_with_kwargs)
    assert isinstance(model, DummyModule)
    assert calls == []
