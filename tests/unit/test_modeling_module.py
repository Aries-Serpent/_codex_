from __future__ import annotations

from types import SimpleNamespace

import pytest

from src import modeling


class FakeModel:
    def __init__(self) -> None:
        self.received_dtype = None
        self.received_device = None

    def to(self, device: str) -> FakeModel:
        self.received_device = device
        return self

    def state_dict(self) -> dict[str, int]:  # pragma: no cover - compatibility
        return {"weights": 1}


class FakeTokenizer:
    def __init__(self) -> None:
        self.pad_token = None
        self.eos_token = "</s>"  # noqa: S105 - static tokenizer token
        self.padding_side = "left"


@pytest.fixture(autouse=True)
def reset_import_module(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(modeling, "import_module", modeling.import_module)


def test_load_model_without_lora(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_model = FakeModel()

    def fake_from_pretrained(name: str, torch_dtype) -> FakeModel:
        fake_model.received_dtype = torch_dtype
        return fake_model

    monkeypatch.setattr(
        modeling, "AutoModelForCausalLM", SimpleNamespace(from_pretrained=fake_from_pretrained)
    )
    loaded = modeling.load_model("dummy/model", dtype="bf16", device="cpu")
    assert loaded is fake_model
    assert fake_model.received_dtype == modeling.resolve_dtype("bf16")
    assert fake_model.received_device == "cpu"


def test_apply_lora_requires_peft(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        modeling, "import_module", lambda name: (_ for _ in ()).throw(ModuleNotFoundError)
    )
    with pytest.raises(RuntimeError):
        modeling.apply_lora_if_configured(FakeModel(), modeling.LoRASettings(enabled=True))


def test_load_model_and_tokenizer(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_model = FakeModel()
    fake_tokenizer = FakeTokenizer()

    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        SimpleNamespace(from_pretrained=lambda *_args, **_kwargs: fake_model),
    )
    monkeypatch.setattr(
        modeling,
        "AutoTokenizer",
        SimpleNamespace(from_pretrained=lambda *_args, **_kwargs: fake_tokenizer),
    )
    model, tokenizer = modeling.load_model_and_tokenizer({"model_name_or_path": "dummy/model"})
    assert model is fake_model
    assert tokenizer is fake_tokenizer
    assert tokenizer.pad_token == fake_tokenizer.eos_token
    assert tokenizer.padding_side == "left"
