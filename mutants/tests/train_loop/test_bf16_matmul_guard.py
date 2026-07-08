"""
Test Bf16 Matmul Guard

Test module for bf16 matmul guard.
"""

import importlib
import sys
import types

import pytest


def test_bf16_matmul_guard_raises_on_runtime_error(monkeypatch):
    tl = importlib.import_module("src.codex_ml.train_loop")
    guard = tl._assert_bf16_capability

    # Fake a torch module with bfloat16 but matmul fails
    class FakeTensor:
        def __init__(self, *_, **__):
            pass

        def to(self, *_args, **_kwargs):
            return self

        def _raise_bf16_matmul_runtime_error(self):
            raise RuntimeError("matmul not supported for bf16")

        def __matmul__(self, _other):
            self._raise_bf16_matmul_runtime_error()

    fake_torch = types.SimpleNamespace(
        bfloat16=object(),
        ones=lambda *args, **kwargs: FakeTensor(),
        tensor=lambda *args, **kwargs: FakeTensor(),
    )

    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    with pytest.raises(RuntimeError):
        guard("bf16", fake_torch.bfloat16, True, device=None)
