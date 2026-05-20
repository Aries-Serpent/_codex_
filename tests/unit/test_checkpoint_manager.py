from __future__ import annotations

import builtins
import importlib.util
import logging
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


def _raise_runtime_error(message: str):
    raise RuntimeError(message)


def _load_training_checkpoint_manager(
    monkeypatch: pytest.MonkeyPatch,
    *,
    fake_numpy: object | None = None,
    fake_torch: object | None = None,
    fake_checkpointing: object | None = None,
    allow_checkpointing_import: bool = False,
):
    module_name = "training.checkpoint_manager_under_test"
    module_path = (
        Path(__file__).resolve().parents[2] / "training" / "checkpoint_manager.py"
    )
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        importer = (globals or {}).get("__name__", "")
        if name == "codex_ml.utils.checkpointing":
            if not allow_checkpointing_import:
                raise ImportError("forced checkpointing import failure")
            if fake_checkpointing is not None:
                return fake_checkpointing
            # Intentional passthrough for integration-like unit coverage:
            # allow real helper imports when no mock helper module is injected.
            return original_import(name, globals, locals, fromlist, level)
        if name == "numpy" and importer == module_name:
            if fake_numpy is None:
                raise ImportError("forced numpy import failure")
            return fake_numpy
        if name == "torch" and importer == module_name:
            if fake_torch is None:
                raise ImportError("forced torch import failure")
            return fake_torch
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_dump_rng_state_without_torch_uses_fallback(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    module = _load_training_checkpoint_manager(monkeypatch, fake_numpy=None, fake_torch=None)

    state = module.dump_rng_state()

    assert "python" in state
    assert "numpy" not in state
    assert "torch" not in state
    assert (
        "Failed to import build_payload_bytes/dump_rng_state "
        "from codex_ml.utils.checkpointing; using legacy local fallback."
    ) in caplog.text


def test_checkpoint_helper_import_success_uses_imported_helpers(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    fake_checkpointing = SimpleNamespace(
        build_payload_bytes=lambda *args, **kwargs: b"ok",
        dump_rng_state=lambda: {"python": [1, 2, 3]},
    )
    module = _load_training_checkpoint_manager(
        monkeypatch,
        fake_checkpointing=fake_checkpointing,
        allow_checkpointing_import=True,
    )

    assert module.build_payload_bytes is fake_checkpointing.build_payload_bytes
    assert module.dump_rng_state is fake_checkpointing.dump_rng_state
    assert module.build_payload_bytes({"k": "v"}) == b"ok"
    assert module.dump_rng_state() == {"python": [1, 2, 3]}
    assert "using legacy local fallback" not in caplog.text


def test_checkpoint_helper_import_passthrough_uses_real_module(monkeypatch):
    module = _load_training_checkpoint_manager(
        monkeypatch,
        allow_checkpointing_import=True,
    )

    assert module.build_payload_bytes.__module__ == "codex_ml.utils.checkpointing"
    try:
        payload = module.build_payload_bytes(None)
    except RuntimeError as exc:  # pragma: no cover - torch-optional environment
        assert "torch is required" in str(exc)
    else:
        assert isinstance(payload, bytes)  # pragma: no cover - torch-optional environment
    assert "python" in module.dump_rng_state()


def test_dump_rng_state_numpy_only_logs_specific_failure(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    fake_numpy = SimpleNamespace(
        random=SimpleNamespace(get_state=lambda: _raise_runtime_error("boom"))
    )
    module = _load_training_checkpoint_manager(
        monkeypatch,
        fake_numpy=fake_numpy,
        fake_torch=None,
    )

    state = module.dump_rng_state()

    assert "python" in state
    assert "numpy" not in state
    assert "torch" not in state
    assert "Failed to capture numpy random state" in caplog.text


def test_dump_rng_state_torch_cpu_without_cuda_logs_specific_failure(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    fake_torch = SimpleNamespace(
        get_rng_state=lambda: _raise_runtime_error("cpu boom"),
        cuda=SimpleNamespace(is_available=lambda: False),
    )
    module = _load_training_checkpoint_manager(
        monkeypatch,
        fake_numpy=None,
        fake_torch=fake_torch,
    )

    state = module.dump_rng_state()

    assert "python" in state
    assert "torch" not in state
    assert "Failed to capture torch CPU random state" in caplog.text


def test_dump_rng_state_cuda_failure_logs_specific_failure(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    fake_torch = SimpleNamespace(
        get_rng_state=lambda: SimpleNamespace(tolist=lambda: [1, 2, 3]),
        cuda=SimpleNamespace(
            is_available=lambda: True,
            get_rng_state_all=lambda: _raise_runtime_error("cuda boom"),
        ),
    )
    module = _load_training_checkpoint_manager(
        monkeypatch,
        fake_numpy=None,
        fake_torch=fake_torch,
    )

    state = module.dump_rng_state()

    assert state["torch"]["cpu"] == [1, 2, 3]
    assert "cuda" not in state["torch"]
    assert "Failed to capture CUDA random state" in caplog.text
