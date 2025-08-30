import types


def test_lora_disabled(monkeypatch):
    mod = __import__("codex_ml.modeling.codex_model_loader", fromlist=["load_model_with_optional_lora"])
    fake_model = object()

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: fake_model),
    )

    model = mod.load_model_with_optional_lora("stub", lora_enabled=False)
    assert model is fake_model


def test_lora_missing_dep(monkeypatch):
    mod = __import__("codex_ml.modeling.codex_model_loader", fromlist=["load_model_with_optional_lora"])
    fake_model = object()

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: fake_model),
    )
    monkeypatch.setattr(mod, "_maybe_import_peft", lambda: (None, None))

    model = mod.load_model_with_optional_lora("stub", lora_enabled=True)
    assert model is fake_model

