from __future__ import annotations

import logging
import sys

import pytest

pytest.importorskip("transformers")

import codex_ml.hf_loader as hf_loader


def test_load_causal_lm_handles_missing_peft(monkeypatch, caplog):
    torch = pytest.importorskip("torch")

    class DummyModel:
        def __init__(self) -> None:
            self.moves: list[str] = []

        def to(self, target):
            self.moves.append(target)
            return self

    captured = {}

    class StubLoader:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            return DummyModel()

    monkeypatch.setattr(hf_loader, "AutoModelForCausalLM", StubLoader)
    monkeypatch.setattr(hf_loader, "_required_revision", lambda repo_id, revision: "rev")
    monkeypatch.setitem(sys.modules, "peft", object(), raising=False)

    caplog.set_level(logging.INFO)
    model = hf_loader.load_causal_lm(
        "gpt2",
        dtype="fp16",
        device="cuda:0",
        peft_cfg={"r": 4},
    )

    assert isinstance(model, DummyModel)
    assert captured["kwargs"].get("torch_dtype") == torch.float16
    assert model.moves == ["cuda:0"]
    assert any("LoRA not applied" in record.getMessage() for record in caplog.records)
