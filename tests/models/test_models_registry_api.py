import pytest

from codex_ml.models.registry import get_model

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")
PretrainedConfig = transformers.PretrainedConfig
PreTrainedModel = transformers.PreTrainedModel


def test_get_minilm() -> None:
    cfg = {"vocab_size": 10, "lora": {"enabled": False}}
    model = get_model("MiniLM", cfg)
    inp = torch.randint(0, 10, (1, 4))
    out = model(inp)
    assert out.shape[0] == 1


def test_get_hf_masked_lm(monkeypatch) -> None:
    class DummyModel(PreTrainedModel):
        config_class = PretrainedConfig

        def __init__(self) -> None:
            super().__init__(PretrainedConfig())

        def forward(self, *args, **kwargs):  # pragma: no cover - dummy
            return None

    def fake_from_pretrained(name, **kwargs):  # pragma: no cover - patched
        assert kwargs.get("local_files_only") is True
        assert "trust_remote_code" not in kwargs
        assert name == "bert-base-uncased"
        return DummyModel()

    monkeypatch.setattr(
        "codex_ml.models.registry.AutoModelForMaskedLM.from_pretrained",
        fake_from_pretrained,
    )
    model = get_model("bert-base-uncased", {"lora": {"enabled": False}})
    assert isinstance(model, DummyModel)


def test_hf_model_prefers_local_path(monkeypatch, tmp_path) -> None:
    class DummyModel(PreTrainedModel):
        config_class = PretrainedConfig

        def __init__(self) -> None:
            super().__init__(PretrainedConfig())

        def forward(self, *args, **kwargs):  # pragma: no cover - dummy
            return None

    expected_path = tmp_path / "weights"

    def fake_from_pretrained(name, **kwargs):  # pragma: no cover - patched
        assert name == str(expected_path)
        return DummyModel()

    monkeypatch.setattr(
        "codex_ml.models.registry.AutoModelForMaskedLM.from_pretrained",
        fake_from_pretrained,
    )
    model = get_model(
        "bert-base-uncased",
        {"lora": {"enabled": False}, "local_path": expected_path},
    )
    assert isinstance(model, DummyModel)


def test_hf_model_raises_when_weights_missing(monkeypatch) -> None:
    def fake_from_pretrained(name, **kwargs):  # pragma: no cover - patched
        raise OSError("not found")

    monkeypatch.setattr(
        "codex_ml.models.registry.AutoModelForMaskedLM.from_pretrained",
        fake_from_pretrained,
    )

    with pytest.raises(RuntimeError, match="Unable to load weights"):
        get_model("bert-base-uncased", {"lora": {"enabled": False}})
