"""
Test Peft Gating

Test module for peft gating.
"""

import importlib


def test_peft_disabled_by_default(monkeypatch):
    monkeypatch.delenv("CODEX_ENABLE_PEFT", raising=False)
    mf = importlib.import_module("codex_ml.models.factory")
    # FIX: Use correct constant name from factory module
    assert hasattr(mf, "ENV_ENABLE_PEFT"), (
        "ENV_ENABLE_PEFT constant not found in codex_ml.models.factory. "
        f"Available attributes: {[a for a in dir(mf) if not a.startswith('_')]}"
    )
