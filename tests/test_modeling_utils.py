import types

from codex_ml.utils import modeling
from tests.helpers.optional_dependencies import import_optional_dependency

import_optional_dependency("transformers")
import_optional_dependency("torch")


def test_load_model_and_tokenizer_minimal(monkeypatch):
    fake_tok = types.SimpleNamespace()
    fake_model = types.SimpleNamespace(state_dict=lambda: {})

    def fake_tok_loader(*a, **k):  # pragma: no cover - trivial
        return fake_tok

    def fake_model_loader(*a, **k):  # pragma: no cover - trivial
        return fake_model

    monkeypatch.setattr(
        modeling, "AutoTokenizer", types.SimpleNamespace(from_pretrained=fake_tok_loader)
    )
    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=fake_model_loader),
    )
    model, tok = modeling.load_model_and_tokenizer("stub", dtype="fp16")
    assert model is fake_model and tok is fake_tok


def test_load_model_and_tokenizer_requires_peft(monkeypatch):
    fake_tok = types.SimpleNamespace()
    fake_model = types.SimpleNamespace(state_dict=lambda: {})

    monkeypatch.setattr(
        modeling, "AutoTokenizer", types.SimpleNamespace(from_pretrained=lambda *a, **k: fake_tok)
    )
    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: fake_model),
    )
    monkeypatch.setattr(modeling, "get_peft_model", None)
    model, _ = modeling.load_model_and_tokenizer("stub", lora={"r": 4})
    assert model is fake_model
