from __future__ import annotations

from pathlib import Path

import torch
from codex_ml.cli import infer


def test_infer_passes_lora_args(monkeypatch, tmp_path: Path) -> None:
    called: dict[str, object] = {}

    class DummyModel:
        def to(self, device: str) -> "DummyModel":
            return self

        def generate(self, *args, **kwargs):
            return torch.zeros((1, 1), dtype=torch.int64)

    def fake_loader(name_or_path: str, **kw):
        called.update(kw)
        return DummyModel()

    class DummyTokenizer:
        vocab_size = 10
        eos_token_id = 0
        pad_token_id = 0

        def encode(self, text: str, return_tensors: str = "pt"):
            return torch.ones((1, 1), dtype=torch.int64)

        def decode(self, ids, skip_special_tokens: bool = True) -> str:
            return "hi"

    class DummyAutoTokenizer:
        @staticmethod
        def from_pretrained(name: str) -> DummyTokenizer:  # pragma: no cover - simple stub
            return DummyTokenizer()

    monkeypatch.setattr(infer, "AutoTokenizer", DummyAutoTokenizer)
    monkeypatch.setattr(infer, "load_model_with_optional_lora", fake_loader)
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path))

    infer.main(
        [
            "--lora-r",
            "4",
            "--lora-alpha",
            "32",
            "--lora-dropout",
            "0.1",
        ]
    )

    assert called["lora_enabled"] is True
    assert called["lora_r"] == 4
    assert called["lora_alpha"] == 32
    assert called["lora_dropout"] == 0.1
