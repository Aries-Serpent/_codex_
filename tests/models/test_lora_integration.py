import pytest

from codex_ml.models.registry import get_model

pytestmark = pytest.mark.requires_torch

torch = pytest.importorskip("torch")
nn = torch.nn


def test_lora_integration_applies_and_marks_trainable(monkeypatch):
    class DummyModel(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.base = nn.Linear(1, 1)
            self.lora = nn.Linear(1, 1)
            for p in self.base.parameters():
                p.requires_grad = False
            for p in self.lora.parameters():
                p.requires_grad = True

    calls = {}

    def fake_apply_lora(model, cfg):  # pragma: no cover - patched
        calls["cfg"] = cfg
        return DummyModel()

    monkeypatch.setattr("codex_ml.models.registry.apply_lora", fake_apply_lora)

    cfg = {"vocab_size": 10, "lora": {"enabled": True}}
    model = get_model("MiniLM", cfg)
    assert calls["cfg"]["enabled"] is True
    trainable = [n for n, p in model.named_parameters() if p.requires_grad]
    assert trainable == ["lora.weight", "lora.bias"]
