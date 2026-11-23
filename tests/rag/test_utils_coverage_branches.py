"""Coverage tests for RAG model/device utility boundary branches."""

from __future__ import annotations

import builtins
import sys
from types import SimpleNamespace

import pytest

from aries_serpent_core.rag import utils


def test_has_meta_tensors_covers_submodule_fallbacks(monkeypatch) -> None:
    real_import = builtins.__import__

    def without_torch(name, *args, **kwargs):
        if name == "torch":
            raise ImportError("missing torch")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_torch)

    meta_param = SimpleNamespace(is_meta=True, shape=(1,))

    class Submodule:
        @staticmethod
        def named_parameters(*_args, **kwargs):
            if kwargs:
                raise TypeError("recurse unsupported")
            return [("weight", meta_param)]

        @staticmethod
        def named_buffers(*_args, **kwargs):
            return []

    submodule = Submodule()
    model = SimpleNamespace(
        parameters=lambda: [],
        buffers=lambda: [],
        named_modules=lambda: [("", object()), ("layer", submodule)],
    )
    assert utils.has_meta_tensors(model) is True

    buffer_meta = SimpleNamespace(is_meta=False, device=SimpleNamespace(type="meta"))
    model.named_modules = lambda: [
        ("", object()),
        (
            "layer",
            SimpleNamespace(
                named_parameters=lambda **_kwargs: [],
                named_buffers=lambda **kwargs: (
                    (_ for _ in ()).throw(TypeError("unsupported"))
                    if kwargs
                    else [("cache", buffer_meta)]
                ),
            ),
        ),
    ]
    assert utils.has_meta_tensors(model) is True


def test_has_meta_tensors_checks_model_device_and_error_fallback(monkeypatch) -> None:
    model = SimpleNamespace(
        parameters=lambda: [],
        buffers=lambda: [],
        named_modules=lambda: [],
        device=SimpleNamespace(type="meta"),
    )
    assert utils.has_meta_tensors(model) is True

    broken = SimpleNamespace(parameters=lambda: (_ for _ in ()).throw(RuntimeError("broken")))
    assert utils.has_meta_tensors(broken) is None


def test_safe_model_to_device_handles_meta_materialization(monkeypatch) -> None:
    class Module:
        @staticmethod
        def reset_parameters() -> None:
            raise RuntimeError("cannot reset")

    class MetaModel:
        def __init__(self) -> None:
            self.dtype = None

        @staticmethod
        def parameters():
            return [SimpleNamespace(is_meta=True, shape=(1,))]

        @staticmethod
        def buffers():
            return []

        @staticmethod
        def named_modules():
            return []

        def to_empty(self, *, device):
            assert device == "cpu"
            return self

        @staticmethod
        def modules():
            return [Module()]

        def to(self, *, dtype):
            self.dtype = dtype
            return self

    model = MetaModel()
    moved = utils.safe_model_to_device(model, dtype="float16")
    assert moved is model
    assert moved.dtype == "float16"


def test_safe_model_to_device_rejects_non_materializable_meta_model(monkeypatch) -> None:
    model = SimpleNamespace(
        parameters=lambda: [SimpleNamespace(is_meta=True, shape=(1,))],
        buffers=lambda: [],
        named_modules=lambda: [],
    )
    with pytest.raises(AttributeError, match="requires to_empty"):
        utils.safe_model_to_device(model)

    class BrokenMetaModel:
        @staticmethod
        def parameters():
            return [SimpleNamespace(is_meta=True, shape=(1,))]

        @staticmethod
        def buffers():
            return []

        @staticmethod
        def named_modules():
            return []

        @staticmethod
        def to_empty(**_kwargs):
            raise NotImplementedError("unsupported")

    with pytest.raises(AttributeError, match="requires to_empty"):
        utils.safe_model_to_device(BrokenMetaModel())


def test_safe_model_to_device_handles_unknown_inspection_and_missing_torch(monkeypatch) -> None:
    model = SimpleNamespace(to=lambda *_args, **_kwargs: model)
    monkeypatch.setattr(utils, "has_meta_tensors", lambda _model: None)
    assert utils.safe_model_to_device(model) is model

    monkeypatch.setattr(utils, "has_meta_tensors", lambda _model: False)
    real_import = builtins.__import__

    def without_torch(name, *args, **kwargs):
        if name == "torch":
            raise ImportError("missing torch")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_torch)
    assert utils.safe_model_to_device(model, non_blocking=True) is model


def test_try_model_to_falls_back_after_keyword_and_positional_failures() -> None:
    calls = []

    class BrokenMove:
        def to(self, *args, **kwargs):
            calls.append((args, kwargs))
            if kwargs:
                raise TypeError("keyword arguments unsupported")
            raise RuntimeError("cannot move")

    model = BrokenMove()
    assert utils._try_model_to(model, "cpu") is model
    assert len(calls) == 2

    with pytest.deprecated_call():
        assert utils.safe_model_load(model) is model
