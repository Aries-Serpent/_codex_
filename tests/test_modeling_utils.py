import types

import pytest

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


def test_bf16_guard_called_during_model_load(monkeypatch):
    calls: list[tuple[str | None, object, str, bool]] = []

    def fake_assert(dtype_name, dtype_obj, device, require):
        calls.append((dtype_name, dtype_obj, device, require))

    fake_model = types.SimpleNamespace(to=lambda *_a, **_k: fake_model)

    monkeypatch.setattr(modeling, "_assert_bf16_capability", fake_assert)
    monkeypatch.setattr(modeling, "_ensure_torch", lambda: None)
    monkeypatch.setattr(modeling, "_resolve_dtype", lambda _: "bf16")
    monkeypatch.setattr(modeling, "_resolve_device", lambda _: "cuda")
    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: fake_model),
    )

    config = {"model_name": "stub", "bf16_require_capability": True}
    modeling.load_model(config)
    assert calls and calls[0][3] is True


def test_assert_bf16_capability_raises_without_support(monkeypatch):
    class _FakeTensor:
        def to(self, *_a, **_k):
            return self

        def __matmul__(self, _other):  # pragma: no cover - invoked in guard
            raise RuntimeError("no bf16 support")

    class _FakeTorch:
        bfloat16 = object()

        def __init__(self):
            self.cuda = types.SimpleNamespace(is_available=lambda: False)

        def device(self, name):
            return name

        def ones(self, *_a, **_k):
            return _FakeTensor()

    fake_torch = _FakeTorch()
    monkeypatch.setattr(modeling, "torch", fake_torch)

    with pytest.raises(RuntimeError):
        modeling._assert_bf16_capability("bf16", fake_torch.bfloat16, "cpu", True)
