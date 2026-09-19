"""Regression tests for RAG meta tensor handling and safe device moves.

These checks ensure CPU-default allocations remain intact after meta tensor fixes.
"""

from __future__ import annotations

import builtins
import sys
import types
from collections.abc import Callable
from types import SimpleNamespace

import pytest

from codex.rag import utils


@pytest.fixture()
def device_factory() -> Callable[[str], SimpleNamespace]:
    """Provide a factory for creating lightweight device markers."""

    def _factory(device_type: str) -> SimpleNamespace:
        return SimpleNamespace(type=device_type)

    return _factory


@pytest.fixture()
def meta_param(device_factory: Callable[[str], SimpleNamespace]) -> SimpleNamespace:
    """Provide a fake parameter that lives on the meta device."""

    return SimpleNamespace(device=device_factory("meta"))


@pytest.fixture()
def cpu_param(device_factory: Callable[[str], SimpleNamespace]) -> SimpleNamespace:
    """Provide a fake parameter that lives on the CPU device."""

    return SimpleNamespace(device=device_factory("cpu"))


@pytest.fixture()
def fake_model_factory() -> Callable[..., object]:
    """Build fake models with optional named modules, parameters, and buffers."""

    class FakeModule:
        def __init__(self, parameters: list[object]):
            self._parameters = parameters

        def named_parameters(self):
            return [(f"p{idx}", param) for idx, param in enumerate(self._parameters)]

    def _factory(
        *,
        modules: list[object] | None = None,
        parameters: list[object] | None = None,
        buffers: list[object] | None = None,
        device: SimpleNamespace | None = None,
        to_empty: Callable[..., object] | None = None,
        to: Callable[..., object] | None = None,
    ) -> object:
        class FakeModel:
            def __init__(self):
                self._modules = modules or []
                self._parameters = parameters or []
                self._buffers = buffers or []
                self.device = device
                if to_empty is not None:
                    self.to_empty = to_empty
                if to is not None:
                    self.to = to

            def named_modules(self):
                return [("module", FakeModule(self._modules))] if self._modules else []

            def parameters(self):
                return self._parameters

            def buffers(self):
                return self._buffers

        return FakeModel()

    return _factory


@pytest.mark.timeout(30)
def test_has_meta_tensors_detects_module_parameters(
    fake_model_factory: Callable[..., object],
    meta_param: SimpleNamespace,
) -> None:
    """Ensure meta parameters inside named modules are detected."""
    model = fake_model_factory(modules=[meta_param])
    assert utils.has_meta_tensors(model) is True, "Condition must be true"


@pytest.mark.timeout(30)
@pytest.mark.parametrize(
    "attribute_name",
    ["parameters", "buffers", "device"],
)
def test_has_meta_tensors_detects_meta_locations(
    fake_model_factory: Callable[..., object],
    meta_param: SimpleNamespace,
    attribute_name: str,
    device_factory: Callable[[str], SimpleNamespace],
) -> None:
    """Confirm meta tensors are detected across parameters, buffers, or device."""
    kwargs: dict[str, object] = {}
    if attribute_name == "parameters":
        kwargs["parameters"] = [meta_param]
    elif attribute_name == "buffers":
        kwargs["buffers"] = [meta_param]
    else:
        kwargs["device"] = device_factory("meta")

    model = fake_model_factory(**kwargs)
    assert utils.has_meta_tensors(model) is True, "Condition must be true"


@pytest.mark.timeout(30)
def test_has_meta_tensors_false_for_cpu_only(
    fake_model_factory: Callable[..., object],
    cpu_param: SimpleNamespace,
    device_factory: Callable[[str], SimpleNamespace],
) -> None:
    """Verify CPU-only fake models are not flagged as meta tensors."""
    model = fake_model_factory(
        modules=[cpu_param],
        parameters=[cpu_param],
        buffers=[cpu_param],
        device=device_factory("cpu"),
    )
    assert utils.has_meta_tensors(model) is False, "Condition must be true"


@pytest.mark.timeout(30)
def test_safe_model_to_device_uses_to_empty_for_meta(
    fake_model_factory: Callable[..., object],
    meta_param: SimpleNamespace,
) -> None:
    """Ensure meta tensors trigger to_empty and return the moved model."""
    call_state: dict[str, str] = {}

    def to_empty(device: str) -> str:
        call_state["device"] = device
        return "moved"

    model = fake_model_factory(parameters=[meta_param], to_empty=to_empty)
    assert utils.safe_model_to_device(model, device="cpu") == "moved"
    assert call_state["device"] == "cpu", "Condition must be true"


@pytest.mark.timeout(30)
def test_safe_model_to_device_raises_without_to_empty(
    fake_model_factory: Callable[..., object],
    meta_param: SimpleNamespace,
) -> None:
    """Confirm meta tensors raise when to_empty is not available."""
    model = fake_model_factory(parameters=[meta_param])
    with pytest.raises(AttributeError, match="to_empty"):
        utils.safe_model_to_device(model, device="cpu")


@pytest.mark.timeout(30)
def test_safe_model_to_device_uses_torch_module_to(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validate that torch.nn.Module instances use their .to method."""
    moved: dict[str, str] = {}

    class FakeTorchModule:
        def to(self, device: str, **kwargs):
            moved["device"] = device
            return "torch-moved"

    torch_module = types.SimpleNamespace(nn=types.SimpleNamespace(Module=FakeTorchModule))
    monkeypatch.setitem(sys.modules, "torch", torch_module)

    class FakeModel(FakeTorchModule):
        def parameters(self):
            return []

        def buffers(self):
            return []

    model = FakeModel()
    assert utils.safe_model_to_device(model, device="cpu") == "torch-moved"
    assert moved["device"] == "cpu", "Condition must be true"


@pytest.mark.timeout(30)
def test_safe_model_to_device_fallbacks_when_torch_missing(
    monkeypatch: pytest.MonkeyPatch,
    fake_model_factory: Callable[..., object],
) -> None:
    """Verify the fallback .to path is used if torch import fails."""
    moved: dict[str, str] = {}

    original_import = builtins.__import__

    def fake_import(name: str, *args, **kwargs):
        if name == "torch":
            raise ImportError("torch unavailable")
        return original_import(name, *args, **kwargs)

    def to(device: str) -> str:
        moved["device"] = device
        return "fallback-moved"

    monkeypatch.setattr(builtins, "__import__", fake_import)

    model = fake_model_factory(to=to)
    assert utils.safe_model_to_device(model, device="cpu") == "fallback-moved"
    assert moved["device"] == "cpu", "Condition must be true"
