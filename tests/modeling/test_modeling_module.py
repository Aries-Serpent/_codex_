import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest  # noqa: E402

import modeling  # noqa: E402

torch = pytest.importorskip("torch")
TORCH_STUB = getattr(torch, "__version__", "").endswith("stub")

if TORCH_STUB:

    class _DummyModel:  # pragma: no cover - placeholder when torch is stubbed
        def __init__(self) -> None:
            self.received_device: str | None = None

        def to(self, device: str) -> "_DummyModel":
            self.received_device = device
            return self

else:

    class _DummyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.linear = torch.nn.Linear(2, 2)
            self.received_device: str | None = None

        def to(self, device: str) -> "_DummyModel":  # type: ignore[override]
            self.received_device = device
            return self

        def forward(
            self, inputs: torch.Tensor
        ) -> torch.Tensor:  # pragma: no cover - not used in tests
            return self.linear(inputs)


@pytest.mark.skipif(TORCH_STUB, reason="modeling tests require the real torch package")
@pytest.mark.parametrize("dtype", ["float32", "fp16", "bf16"])
def test_load_model_respects_dtype(monkeypatch: pytest.MonkeyPatch, dtype: str) -> None:
    recorded: dict[str, object] = {}

    def fake_from_pretrained(
        name: str, torch_dtype: torch.dtype, low_cpu_mem_usage: bool
    ) -> _DummyModel:
        recorded["name"] = name
        recorded["dtype"] = torch_dtype
        recorded["low_cpu"] = low_cpu_mem_usage
        return _DummyModel()

    monkeypatch.setattr(
        modeling, "AutoModelForCausalLM", SimpleNamespace(from_pretrained=fake_from_pretrained)
    )
    monkeypatch.setattr(modeling, "LoraConfig", None)
    monkeypatch.setattr(modeling, "get_peft_model", None)

    cfg = modeling.ModelConfig(model_name="demo-model", dtype=dtype, device="cpu")
    model = modeling.load_model(cfg)

    assert isinstance(model, _DummyModel)
    assert recorded["name"] == "demo-model"
    assert recorded["low_cpu"] is True
    assert model.received_device == "cpu"
    expected_dtype = modeling._DTYPE_MAP.get(dtype.lower(), torch.float32)
    assert recorded["dtype"] == expected_dtype


@pytest.mark.skipif(TORCH_STUB, reason="modeling tests require the real torch package")
def test_load_model_applies_lora(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_from_pretrained(
        name: str, torch_dtype: torch.dtype, low_cpu_mem_usage: bool
    ) -> _DummyModel:
        return _DummyModel()

    applied: dict[str, object] = {}

    class FakeLoraConfig:
        def __init__(self, **kwargs: object) -> None:
            applied["config"] = kwargs

    def fake_get_peft_model(model: _DummyModel, cfg: FakeLoraConfig) -> _DummyModel:
        applied["model"] = model
        applied["lora"] = cfg
        return model

    monkeypatch.setattr(
        modeling, "AutoModelForCausalLM", SimpleNamespace(from_pretrained=fake_from_pretrained)
    )
    monkeypatch.setattr(modeling, "LoraConfig", FakeLoraConfig)
    monkeypatch.setattr(modeling, "get_peft_model", fake_get_peft_model)

    cfg = modeling.ModelConfig(
        model_name="demo",
        device="cpu",
        lora=modeling.LoRASettings(enabled=True, r=4, alpha=32, dropout=0.1, target_modules=("x",)),
    )
    model = modeling.load_model(cfg)

    assert isinstance(model, _DummyModel)
    assert applied["model"] is model
    params = applied["config"]
    assert params["r"] == 4
    assert params["lora_alpha"] == 32
    assert params["target_modules"] == ["x"]


@pytest.mark.skipif(TORCH_STUB, reason="modeling tests require the real torch package")
def test_load_tokenizer_prefers_configured_name(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class DummyTokenizer:
        pad_token = None
        eos_token = "</s>"  # noqa: S105

    def fake_from_pretrained(name: str) -> DummyTokenizer:
        captured["name"] = name
        return DummyTokenizer()

    monkeypatch.setattr(
        modeling, "AutoTokenizer", SimpleNamespace(from_pretrained=fake_from_pretrained)
    )

    cfg = modeling.ModelConfig(model_name="base", tokenizer_name="tokenizer")
    tok = modeling.load_tokenizer(cfg)

    assert isinstance(tok, DummyTokenizer)
    assert captured["name"] == "tokenizer"
    assert tok.pad_token == "</s>"  # noqa: S105
