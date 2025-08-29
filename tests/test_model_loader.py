from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora


def test_load_model_without_lora(monkeypatch):
    # Monkeypatch AutoModelForCausalLM to avoid network
    called = {}

    class Dummy:
        @staticmethod
        def from_pretrained(name_or_path, **kw):
            called["args"] = (name_or_path, kw)
            return object()

    monkeypatch.setattr("codex_ml.modeling.codex_model_loader.AutoModelForCausalLM", Dummy)
    model = load_model_with_optional_lora("gpt2", lora_enabled=False)
    assert isinstance(model, object)
    assert called["args"][0] == "gpt2"
