"""
Test Peft Hooks

Test module for peft hooks.
"""

import importlib
import sys
import types

import pytest


def test_peft_hooks_missing_dependency(monkeypatch):
    monkeypatch.delitem(sys.modules, "codex_ml.interfaces.peft_hooks", raising=False)
    fake_missing = types.ModuleType("peft_missing")
    monkeypatch.setitem(sys.modules, "peft", fake_missing)
    module = importlib.import_module("codex_ml.interfaces.peft_hooks")
    with pytest.raises(module.PeftUnavailable):
        module.build_peft_config()


def test_peft_hooks_with_stub(monkeypatch):
    monkeypatch.delitem(sys.modules, "codex_ml.interfaces.peft_hooks", raising=False)

    class _TaskType:
        CAUSAL_LM = "CAUSAL_LM"

    class _FakeConfig:
        def __init__(self, **kwargs):
            self.params = kwargs

    class _FakePeftModel:
        @classmethod
        def from_pretrained(cls, model, path):
            model.loaded = path
            return model

    def _fake_get_peft_model(model, cfg, adapter_name="lora"):
        model.adapter_name = adapter_name
        model.cfg = cfg
        return model

    fake_module = types.SimpleNamespace(
        LoraConfig=lambda **kwargs: _FakeConfig(**kwargs),
        TaskType=_TaskType,
        get_peft_model=_fake_get_peft_model,
        PeftModel=_FakePeftModel,
    )
    monkeypatch.setitem(sys.modules, "peft", fake_module)
    module = importlib.import_module("codex_ml.interfaces.peft_hooks")

    cfg = module.build_peft_config()
    assert isinstance(cfg, _FakeConfig)

    model = types.SimpleNamespace()
    adapted = module.enable_peft(model, cfg, adapter_name="stub")
    assert adapted.adapter_name == "stub", "adapter_name is not valid"
    assert adapted.cfg is cfg, "cfg is not valid"

    loaded = module.load_adapter_for_inference(model, "adapter-path")
    assert loaded.loaded == "adapter-path", "loaded is not valid"
