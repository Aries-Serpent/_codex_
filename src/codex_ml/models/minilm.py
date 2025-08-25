from __future__ import annotations

"""A tiny Transformer language model used for tests."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Optional

import torch
from torch import nn
import torch.nn.functional as F


@dataclass
class MiniLMConfig:
    vocab_size: int
    d_model: int = 32
    n_heads: int = 4
    n_layers: int = 2
    max_seq_len: int = 64
    tie_embeddings: bool = True


class _Block(nn.Module):
    def __init__(self, cfg: MiniLMConfig) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d_model)
        self.attn = nn.MultiheadAttention(cfg.d_model, cfg.n_heads, batch_first=True)
        self.ln2 = nn.LayerNorm(cfg.d_model)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.d_model, 4 * cfg.d_model),
            nn.GELU(),
            nn.Linear(4 * cfg.d_model, cfg.d_model),
        )

    def forward(self, x: torch.Tensor, attn_mask: torch.Tensor) -> torch.Tensor:
        h, _ = self.attn(x, x, x, attn_mask=attn_mask)
        x = self.ln1(x + h)
        h = self.mlp(x)
        x = self.ln2(x + h)
        return x


class MiniLM(nn.Module):
    """A minimal Transformer-style language model."""

    def __init__(self, cfg: MiniLMConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos_emb = nn.Embedding(cfg.max_seq_len, cfg.d_model)
        self.blocks = nn.ModuleList([_Block(cfg) for _ in range(cfg.n_layers)])
        self.ln_f = nn.LayerNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        if cfg.tie_embeddings:
            self.head.weight = self.tok_emb.weight

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        bsz, seq_len = input_ids.shape
        device = input_ids.device
        pos = torch.arange(seq_len, device=device).unsqueeze(0)
        x = self.tok_emb(input_ids) + self.pos_emb(pos)
        mask = torch.full((seq_len, seq_len), float("-inf"), device=device)
        mask = torch.triu(mask, diagonal=1)
        for block in self.blocks:
            x = block(x, mask)
        x = self.ln_f(x)
        logits = self.head(x)
        return logits

    # checkpoint helpers -------------------------------------------------
    def save_pretrained(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "config.json").open("w") as f:
            json.dump(asdict(self.cfg), f)
        torch.save(self.state_dict(), path / "pytorch_model.bin")

    @classmethod
    def from_pretrained(cls, path: str | Path, *, device: Optional[str] = None) -> "MiniLM":
        path = Path(path)
        with (path / "config.json").open() as f:
            cfg = MiniLMConfig(**json.load(f))
        model = cls(cfg)
        state = torch.load(path / "pytorch_model.bin", map_location=device or "cpu")
        model.load_state_dict(state)
        return model


__all__ = ["MiniLM", "MiniLMConfig"]
