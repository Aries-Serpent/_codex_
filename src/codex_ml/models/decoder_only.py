"""Minimal decoder-only Transformer model with optional rotary embeddings and LoRA hooks."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for :class:`DecoderOnlyLM`."""

    vocab_size: int
    d_model: int
    n_heads: int
    n_layers: int
    ffn_mult: float = 4.0
    max_seq_len: int = 2048
    dropout: float = 0.0
    rotary_theta: float = 10000.0
    tie_embeddings: bool = True
    bias: bool = False
    layer_norm_eps: float = 1e-5
    init_std: float = 0.02


def _build_rope_cache(
    max_seq: int, head_dim: int, base: float, device: torch.device
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Precompute rotary position embedding frequencies."""

    inv_freq = 1.0 / (base ** (torch.arange(0, head_dim, 2, device=device).float() / head_dim))
    t = torch.arange(max_seq, device=device).float()
    freqs = torch.einsum("i,j->ij", t, inv_freq)
    emb = torch.cat((freqs, freqs), dim=-1)
    return emb.sin()[None, None, :, :], emb.cos()[None, None, :, :]


def _apply_rope(x: torch.Tensor, sin: torch.Tensor, cos: torch.Tensor) -> torch.Tensor:
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    x_rot = torch.cat((-x2, x1), dim=-1)
    return (x * cos) + (x_rot * sin)


class MultiHeadAttention(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        assert cfg.d_model % cfg.n_heads == 0, "d_model must be divisible by n_heads"
        self.cfg = cfg
        self.qkv = nn.Linear(cfg.d_model, 3 * cfg.d_model, bias=cfg.bias)
        self.proj = nn.Linear(cfg.d_model, cfg.d_model, bias=cfg.bias)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        past: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        *,
        use_cache: bool = True,
        sin: Optional[torch.Tensor] = None,
        cos: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        bsz, seq, _ = x.shape
        h = self.cfg.n_heads
        head_dim = self.cfg.d_model // h
        qkv = self.qkv(x)
        qkv = qkv.view(bsz, seq, 3, h, head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        if sin is not None and cos is not None:
            q = _apply_rope(q, sin[:, :, :seq, :], cos[:, :, :seq, :])
            k = _apply_rope(k, sin[:, :, :seq, :], cos[:, :, :seq, :])
        if past is not None:
            pk, pv = past
            k = torch.cat([pk, k], dim=2)
            v = torch.cat([pv, v], dim=2)
        att = (q @ k.transpose(-2, -1)) / math.sqrt(head_dim)
        att = att.masked_fill(mask == 0, float("-inf"))
        probs = F.softmax(att, dim=-1)
        probs = self.dropout(probs)
        out = probs @ v
        out = out.transpose(1, 2).contiguous().view(bsz, seq, h * head_dim)
        out = self.proj(out)
        out = self.dropout(out)
        return (out, (k, v)) if use_cache else (out, None)


class FeedForward(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        inner = int(cfg.ffn_mult * cfg.d_model)
        self.fc1 = nn.Linear(cfg.d_model, inner, bias=cfg.bias)
        self.fc2 = nn.Linear(inner, cfg.d_model, bias=cfg.bias)
        self.act = nn.GELU()
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class Block(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d_model, eps=cfg.layer_norm_eps)
        self.attn = MultiHeadAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.d_model, eps=cfg.layer_norm_eps)
        self.mlp = FeedForward(cfg)

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        past: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        *,
        use_cache: bool = True,
        sin: Optional[torch.Tensor] = None,
        cos: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        offset = past[0].size(2) if past is not None else 0
        sin_slice = sin[:, :, offset : offset + x.size(1), :] if sin is not None else None
        cos_slice = cos[:, :, offset : offset + x.size(1), :] if cos is not None else None
        h, pkv = self.attn(
            self.ln1(x), mask, past, use_cache=use_cache, sin=sin_slice, cos=cos_slice
        )
        x = x + h
        h = self.mlp(self.ln2(x))
        x = x + h
        return x, pkv


class DecoderOnlyLM(nn.Module):
    """A minimal GPT-style language model."""

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)
        head_dim = cfg.d_model // cfg.n_heads
        if cfg.rotary_theta:
            sin, cos = _build_rope_cache(
                cfg.max_seq_len, head_dim, cfg.rotary_theta, torch.device("cpu")
            )
            self.register_buffer("rope_sin", sin, persistent=False)
            self.register_buffer("rope_cos", cos, persistent=False)
            self.pos_emb = None
        else:
            self.pos_emb = nn.Embedding(cfg.max_seq_len, cfg.d_model)
            self.rope_sin = None
            self.rope_cos = None
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layers)])
        self.ln_f = nn.LayerNorm(cfg.d_model, eps=cfg.layer_norm_eps)
        self.head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        if cfg.tie_embeddings:
            self.head.weight = self.tok_emb.weight
        self.gradient_checkpointing = False
        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:  # pragma: no cover - simple init
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=self.cfg.init_std)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=self.cfg.init_std)

    def enable_gradient_checkpointing(self, enable: bool = True) -> None:
        self.gradient_checkpointing = enable

    def _causal_mask(self, x: torch.Tensor, past_len: int = 0) -> torch.Tensor:
        _, seq = x.shape
        total = seq + past_len
        mask = torch.ones(total, total, device=x.device, dtype=torch.bool)
        mask = torch.tril(mask)
        return mask[-seq:, :]

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        *,
        use_cache: bool = True,
        labels: Optional[torch.Tensor] = None,
    ) -> dict:
        bsz, seq = input_ids.shape
        device = input_ids.device
        pos = torch.arange(seq, device=device)
        x = self.tok_emb(input_ids)
        if self.pos_emb is not None:
            x = x + self.pos_emb(pos)[None, :, :]
        x = self.drop(x)
        past_len = past_key_values[0][0].size(2) if past_key_values else 0
        mask = self._causal_mask(input_ids, past_len=past_len)
        mask = mask.unsqueeze(0).unsqueeze(0)
        pkv_out = []
        sin = self.rope_sin[:, :, : past_len + seq, :] if self.rope_sin is not None else None
        cos = self.rope_cos[:, :, : past_len + seq, :] if self.rope_cos is not None else None
        for i, block in enumerate(self.blocks):
            past = past_key_values[i] if past_key_values is not None else None
            if self.gradient_checkpointing and self.training:

                def fn(x):
                    return block(x, mask, past, use_cache=use_cache, sin=sin, cos=cos)

                x, pkv = torch.utils.checkpoint.checkpoint(fn, x)
            else:
                x, pkv = block(x, mask, past, use_cache=use_cache, sin=sin, cos=cos)
            if use_cache:
                pkv_out.append(pkv)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if labels is not None:
            loss = F.cross_entropy(
                logits[:, :-1].contiguous().view(-1, logits.size(-1)),
                labels[:, 1:].contiguous().view(-1),
            )
        return {
            "logits": logits,
            "loss": loss,
            "past_key_values": tuple(pkv_out) if use_cache else None,
        }


__all__ = ["ModelConfig", "DecoderOnlyLM"]
