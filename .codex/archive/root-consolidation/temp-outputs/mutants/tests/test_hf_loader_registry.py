"""
Test Hf Loader Registry

Test module for hf loader registry.
"""

from __future__ import annotations

import pytest

pytest.importorskip("transformers")

from codex_ml.hf_loader import (
    get_registered_causal_lm,
    load_causal_lm,
    register_causal_lm,
    unregister_causal_lm,
)


def test_register_causal_lm_decorator_roundtrip():
    calls = {}

    @register_causal_lm("dummy")
    def _build_dummy(*, device=None, dtype=None, peft_cfg=None):
        calls["device"] = device
        calls["dtype"] = dtype
        calls["peft_cfg"] = peft_cfg

        class _Dummy:
            def __init__(self) -> None:
                self.moves = []

            def to(
                self, target
            ):  # pragma: no cover - user supplied constructors may handle devices
                self.moves.append(target)
                return self

        instance = _Dummy()
        calls["model"] = instance
        return instance

    assert get_registered_causal_lm("dummy") is not None, "Value must be initialized"

    try:
        result = load_causal_lm("dummy", device="cpu", dtype="bf16", peft_cfg={"r": 8})
    finally:
        unregister_causal_lm("dummy")

    assert result is calls["model"], "Result must not be empty"
    assert calls["device"] == "cpu", "Condition must be true"
    assert calls["dtype"] == "bf16", "Condition must be true"
    assert calls["peft_cfg"] == {"r": 8}, "Condition must be true"
    assert get_registered_causal_lm("dummy") is None, "Condition must be true"
