from __future__ import annotations

import importlib
import types

import pytest

from codex_ml.training import device_strategy


def _with_stub(monkeypatch: pytest.MonkeyPatch, *, cuda: bool, bf16: bool = False):
    module = importlib.reload(device_strategy)
    stub_cuda = types.SimpleNamespace(
        is_available=lambda: cuda,
        is_bf16_supported=lambda: bf16,
    )
    stub_backends = types.SimpleNamespace(mps=types.SimpleNamespace(is_built=lambda: False))
    stub = types.SimpleNamespace(
        float32="fp32",
        float16="fp16",
        bfloat16="bf16",
        cuda=stub_cuda,
        backends=stub_backends,
    )
    monkeypatch.setattr(module, "torch", stub, raising=False)
    module.DeviceMapper._STRATEGIES.clear()
    return module


def test_auto_detect_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _with_stub(monkeypatch, cuda=False)
    cfg = module.DeviceConfig.auto_detect()
    assert cfg.device == "cpu"
    assert cfg.dtype == "fp32"
    assert not cfg.mixed_precision


def test_auto_detect_cuda_prefers_bf16(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _with_stub(monkeypatch, cuda=True, bf16=True)
    cfg = module.DeviceConfig.auto_detect()
    assert cfg.device == "cuda"
    assert cfg.dtype == "bf16"
    assert cfg.mixed_precision


@pytest.mark.requires_torch
@pytest.mark.parametrize("dtype", ["float16", "float32"])
def test_apply_to_tensor_changes_dtype(dtype: str) -> None:
    torch = pytest.importorskip("torch")
    cfg = device_strategy.DeviceConfig(device="cpu", dtype=getattr(torch, dtype))
    tensor = torch.ones(2, dtype=torch.float32)
    result = cfg.apply_to_tensor(tensor)
    assert result.dtype == getattr(torch, dtype)
    assert result.device.type == "cpu"


@pytest.mark.requires_torch
def test_apply_to_model_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    torch = pytest.importorskip("torch")

    class Dummy(torch.nn.Linear):
        def to(self, *args, **kwargs):
            target = kwargs.get("device") or (args[0] if args else None)
            if isinstance(target, torch.device) and target.type == "cuda":
                raise RuntimeError("no cuda available")
            return super().to(*args, **kwargs)

    model = Dummy(2, 2)
    cfg = device_strategy.DeviceConfig(device="cuda", dtype=torch.float32)
    result = cfg.apply_to_model(model)
    assert next(result.parameters()).device.type == "cpu"


@pytest.mark.requires_torch
def test_apply_to_model_invalid_device() -> None:
    torch = pytest.importorskip("torch")
    model = torch.nn.Linear(2, 2)
    cfg = device_strategy.DeviceConfig(device="not-a-device", dtype=torch.float32)
    with pytest.raises(ValueError):
        cfg.apply_to_model(model)
