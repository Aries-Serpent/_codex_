"""Small registry providing toy models for the training demos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import torch
from torch import nn

__all__ = ["get_model"]


class _ToyCausalLM(nn.Module):
    def __init__(self, vocab_size: int = 128, hidden_size: int = 64) -> None:
        super().__init__()
        self.embed = nn.Embedding(vocab_size, hidden_size)
        self.linear = nn.Linear(hidden_size, vocab_size)

    def forward(self, input_ids=None, labels=None, **kwargs):  # type: ignore[override]
        if input_ids is None:
            raise ValueError("input_ids required")
        embeddings = self.embed(input_ids)
        logits = self.linear(embeddings)
        loss = None
        if labels is not None:
            shift_logits = logits.view(-1, logits.size(-1))
            shift_labels = labels.view(-1)
            loss = nn.functional.cross_entropy(shift_logits, shift_labels, ignore_index=-100)
        return {"logits": logits, "loss": loss}


def get_model(name: str, config: Mapping[str, Any] | None = None) -> nn.Module:
    """Return a lightweight model suitable for unit tests and demos."""

    cfg = dict(config or {})
    vocab_size = int(cfg.get("vocab_size", 128))
    hidden_size = int(cfg.get("hidden_size", 64))
    return _ToyCausalLM(vocab_size=vocab_size, hidden_size=hidden_size)
