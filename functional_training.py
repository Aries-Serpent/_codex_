"""Convenience wrapper around the symbolic pipeline with optional tokenization."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_

from codex_ml.models import MiniLM, MiniLMConfig
from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RewardModelCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
)
from codex_ml.tokenization import TokenizerAdapter, load_tokenizer


def run_functional_training(
    corpus: List[str],
    demos: List[Dict[str, Any]],
    prefs: List[tuple[str, str, str, int]],
    *,
    tokenizer_name: Optional[str] = None,
    tokenizer_path: Optional[str] = None,
    tokenizer: Optional[TokenizerAdapter] = None,
    weights: Weights = Weights(),
    pre_cfg: PretrainCfg = PretrainCfg(),
    sft_cfg: SFTCfg = SFTCfg(),
    rm_cfg: RewardModelCfg = RewardModelCfg(),
    rlhf_cfg: RLHFCfg = RLHFCfg(),
    use_deeplearning: bool = False,
    device: Optional[str] = None,
    checkpoint_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run training pipeline, optionally using a tiny Torch model."""

    if tokenizer is None and (tokenizer_name or tokenizer_path):
        tokenizer = load_tokenizer(tokenizer_name, tokenizer_path)

    if use_deeplearning:
        return _run_minilm_training(
            corpus,
            tokenizer,
            device=device,
            checkpoint_dir=checkpoint_dir,
        )

    return run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        w=weights,
        pre_cfg=pre_cfg,
        sft_cfg=sft_cfg,
        rm_cfg=rm_cfg,
        rlhf_cfg=rlhf_cfg,
        tokenizer=tokenizer,
    )


def _run_minilm_training(
    corpus: List[str],
    tokenizer: Optional[TokenizerAdapter],
    *,
    device: Optional[str] = None,
    checkpoint_dir: Optional[str] = None,
) -> Dict[str, Any]:
    if not corpus:
        raise ValueError("corpus required for deep learning mode")

    if tokenizer is None:
        vocab = sorted({ch for text in corpus for ch in text})
        stoi = {ch: i for i, ch in enumerate(vocab)}
        vocab_size = len(vocab)

        def encode(s: str) -> List[int]:
            return [stoi[c] for c in s]

    else:
        vocab_size = tokenizer.vocab_size

        def encode(s: str) -> List[int]:
            return tokenizer.encode(s)

    tokens = [tid for text in corpus for tid in encode(text)]
    data = torch.tensor(tokens, dtype=torch.long).unsqueeze(0)

    cfg = MiniLMConfig(
        vocab_size=vocab_size,
        n_layers=1,
        d_model=32,
        n_heads=4,
        max_seq_len=data.size(1),
    )
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Using device: {dev}")
    model = MiniLM(cfg).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=10, gamma=0.9)

    inputs = data[:, :-1].to(dev)
    targets = data[:, 1:].to(dev)
    losses: List[float] = []
    for epoch in range(3):
        opt.zero_grad()
        logits = model(inputs)
        loss = F.cross_entropy(logits.reshape(-1, cfg.vocab_size), targets.reshape(-1))
        loss.backward()
        clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if checkpoint_dir:
            model.save_pretrained(Path(checkpoint_dir) / f"epoch{epoch}")
        losses.append(float(loss.item()))

    return {"losses": losses}


__all__ = ["run_functional_training"]
