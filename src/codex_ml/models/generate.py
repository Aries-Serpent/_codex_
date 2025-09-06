"""Simple text generation utilities for decoder-only models."""

from __future__ import annotations

from typing import Optional

import torch


def _sample(logits: torch.Tensor, temperature: float, top_k: int, top_p: float) -> torch.Tensor:
    if temperature != 1.0:
        logits = logits / temperature
    if top_k > 0:
        v, _ = torch.topk(logits, top_k)
        thresh = v[:, [-1]]
        logits = torch.where(logits < thresh, torch.full_like(logits, float("-inf")), logits)
    if 0.0 < top_p < 1.0:
        sorted_logits, sorted_idx = torch.sort(logits, descending=True)
        cumulative = torch.cumsum(sorted_logits.softmax(dim=-1), dim=-1)
        mask = cumulative > top_p
        mask[..., 1:] = mask[..., :-1].clone()
        mask[..., 0] = False
        sorted_logits[mask] = float("-inf")
        logits = torch.zeros_like(logits).scatter(-1, sorted_idx, sorted_logits)
    probs = torch.softmax(logits, dim=-1)
    return torch.multinomial(probs, 1)


def generate(
    model,
    tokenizer,
    prompt_ids: torch.Tensor,
    *,
    max_new_tokens: int = 20,
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0,
    eos_id: Optional[int] = None,
    pad_id: Optional[int] = None,
) -> torch.Tensor:
    """Generate tokens from ``model`` starting from ``prompt_ids``."""

    model.eval()
    input_ids = prompt_ids.clone()
    past = None
    for _ in range(max_new_tokens):
        out = model(input_ids[:, -1:], past_key_values=past, use_cache=True)
        logits = out["logits"][:, -1, :]
        past = out["past_key_values"]
        next_id = _sample(logits, temperature, top_k, top_p)
        input_ids = torch.cat([input_ids, next_id], dim=1)
        if eos_id is not None and next_id.item() == eos_id:
            break
    if pad_id is not None and eos_id is not None:
        # pad to fixed length for convenience
        pad_len = max_new_tokens + prompt_ids.size(1) - input_ids.size(1)
        if pad_len > 0:
            padding = torch.full((input_ids.size(0), pad_len), pad_id, device=input_ids.device)
            input_ids = torch.cat([input_ids, padding], dim=1)
    return input_ids


__all__ = ["generate"]
