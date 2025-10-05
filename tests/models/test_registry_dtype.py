from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("torch")

import torch

from codex_ml.models import registry


class DummyModel:
    def __init__(self) -> None:
        self.dtype_history: list[torch.dtype] = []
        self.device_history: list[str] = []

    def to(self, *args: Any, **kwargs: Any) -> "DummyModel":
        if args and isinstance(args[0], torch.dtype):
            self.dtype_history.append(args[0])
        if kwargs.get("dtype") is not None:
            self.dtype_history.append(kwargs["dtype"])
        if args and isinstance(args[0], torch.device):
            self.device_history.append(str(args[0]))
        if kwargs.get("device") is not None:
            self.device_history.append(str(kwargs["device"]))
        if isinstance(args[0], str):
            self.device_history.append(args[0])
        return self


def _build_dummy(_: dict[str, Any]) -> DummyModel:
    return DummyModel()


def test_dtype_aliases_apply() -> None:
    registry.register_model("dummy_test", override=True)(_build_dummy)
    model = registry.get_model("dummy_test", {"dtype": "fp16"})
    assert model.dtype_history[-1] == torch.float16

    model = registry.get_model("dummy_test", {"dtype": "torch.bfloat16"})
    assert model.dtype_history[-1] == torch.bfloat16

    model = registry.get_model("dummy_test", {"dtype": torch.float32})
    assert model.dtype_history[-1] == torch.float32


def test_optional_adapter_loader_invoked(monkeypatch: pytest.MonkeyPatch) -> None:
    registry.register_model("dummy_adapter", override=True)(_build_dummy)
    called: dict[str, Any] = {}

    def fake_loader(model: DummyModel, cfg: dict[str, Any]) -> DummyModel:
        called["cfg"] = cfg
        model.marked = True  # type: ignore[attr-defined]
        return model

    cfg = {"lora": {"enabled": True, "rank": 8}}
    model = registry.get_model("dummy_adapter", cfg, adapter_loader=fake_loader)
    assert getattr(model, "marked", False) is True
    assert called["cfg"] == cfg["lora"]
