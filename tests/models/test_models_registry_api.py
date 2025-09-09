import torch
from transformers import PretrainedConfig, PreTrainedModel

from codex_ml.models.registry import get_model


def test_get_minilm() -> None:
    cfg = {"vocab_size": 10, "lora": {"enabled": False}}
    model = get_model("MiniLM", cfg)
    inp = torch.randint(0, 10, (1, 4))
    out = model(inp)
    assert out.shape[0] == 1


def test_get_hf_model(monkeypatch) -> None:
    class DummyModel(PreTrainedModel):
        config_class = PretrainedConfig

        def __init__(self) -> None:
            super().__init__(PretrainedConfig())

        def forward(self, *args, **kwargs):  # pragma: no cover - dummy
            return None

    def fake_from_pretrained(name, **kwargs):  # pragma: no cover - patched
        assert kwargs.get("local_files_only") is True
        return DummyModel()

    monkeypatch.setattr(
        "codex_ml.models.registry.AutoModelForCausalLM.from_pretrained",
        fake_from_pretrained,
    )
    model = get_model("bert-base-uncased", {"lora": {"enabled": False}})
    assert isinstance(model, DummyModel)
