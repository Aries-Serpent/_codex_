import importlib
import sys
import types
import pytest


def test_bf16_require_flag_private_guard(monkeypatch):
    tl = importlib.import_module("src.codex_ml.train_loop")
    guard = getattr(tl, "_assert_bf16_capability")

    # No requirement -> no error
    guard("bf16", None, False)
    guard(None, None, False)

    # Require but no bf16 requested -> no error
    guard("fp32", None, True)

    # Simulate missing torch when bf16 is required -> raises
    fake_torch = types.SimpleNamespace(bfloat16=None)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    with pytest.raises(RuntimeError):
        guard("bf16", None, True)
