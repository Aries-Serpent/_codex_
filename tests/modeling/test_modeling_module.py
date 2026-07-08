"""
Test Modeling Module

Test module for modeling module.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

torch = pytest.importorskip("torch")
import modeling

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
    assert recorded["name"] == "demo-model", "rec is not valid"
    assert recorded["low_cpu"] is True, "rec is not valid"
    assert model.received_device == "cpu", "received_device is not valid"
    expected_dtype = modeling._DTYPE_MAP.get(dtype.lower(), torch.float32)
    assert recorded["dtype"] == expected_dtype, "rec is not valid"


@pytest.mark.skipif(TORCH_STUB, reason="modeling tests require the real torch package")
def test_load_model_applies_lora(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_from_pretrained(
        name: str, torch_dtype: torch.dtype, low_cpu_mem_usage: bool
    ) -> _DummyModel:
        return _DummyModel()

    applied: dict[str, object] = {}

    def fake_apply_lora(model: _DummyModel, cfg: modeling.LoRASettings) -> _DummyModel:
        applied["model"] = model
        applied["lora"] = cfg
        # Record the config parameters for assertion
        applied["config"] = {
            "r": cfg.r,
            "lora_alpha": cfg.alpha,
            "lora_dropout": cfg.dropout,
            "target_modules": list(cfg.target_modules),
            "bias": cfg.bias,
            "task_type": cfg.task_type,
        }
        return model

    monkeypatch.setattr(
        modeling, "AutoModelForCausalLM", SimpleNamespace(from_pretrained=fake_from_pretrained)
    )
    monkeypatch.setattr(modeling, "apply_lora_if_configured", fake_apply_lora)

    cfg = modeling.ModelConfig(
        model_name="demo",
        device="cpu",
        lora=modeling.LoRASettings(
            enabled=True, r=4, alpha=32, dropout=0.1, target_modules=("linear",)
        ),
    )
    model = modeling.load_model(cfg)

    assert isinstance(model, _DummyModel)
    assert applied["model"] is model, "Condition must be true"
    params = applied["config"]
    assert params["r"] == 4, "Condition must be true"
    assert params["lora_alpha"] == 32, "Condition must be true"
    assert params["target_modules"] == ["linear"], "Condition must be true"


@pytest.mark.skipif(TORCH_STUB, reason="modeling tests require the real torch package")
def test_load_tokenizer_prefers_configured_name(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class DummyTokenizer:
        pad_token = None
        eos_token = "</s>"

    def fake_from_pretrained(name: str) -> DummyTokenizer:
        captured["name"] = name
        return DummyTokenizer()

    monkeypatch.setattr(
        modeling, "AutoTokenizer", SimpleNamespace(from_pretrained=fake_from_pretrained)
    )

    cfg = modeling.ModelConfig(model_name="base", tokenizer_name="tokenizer")
    tok = modeling.load_tokenizer(cfg)

    assert isinstance(tok, DummyTokenizer)
    assert captured["name"] == "tokenizer", "Condition must be true"
    assert tok.pad_token == "</s>", "pad_token is not valid"
