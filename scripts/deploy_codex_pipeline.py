#!/usr/bin/env python3
"""
Deploy Codex symbolic training pipeline.

This script installs dependencies (unless skipped), validates JSONL inputs, and executes
the symbolic pipeline. Outputs such as model checkpoints and training summaries
are written to the specified directory.

Supports both CLI and importable usage, with robust error handling and explicit argument parsing.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RewardModelCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
    tokenize,
)

__all__ = [
    "install_requirements",
    "load_jsonl",
    "load_corpus",
    "load_demos",
    "load_prefs",
    "persist_outputs",
    "run_pipeline",
    "build_parser",
    "main",
]


def install_requirements() -> None:
    """
    Install dependencies from requirements.txt unless skipped via CODEX_SKIP_INSTALL.
    """
    if os.environ.get("CODEX_SKIP_INSTALL"):
        return
    req = Path(__file__).resolve().parent.parent / "requirements.txt"
    if req.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=True)


def load_jsonl(path: Path) -> List[Any]:
    """
    Load newline-delimited JSON objects from `path`.
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    data: List[Any] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: line {i} is not valid JSON: {exc}") from exc
    if not data:
        raise ValueError(f"{path} is empty")
    return data


def load_corpus(path: Path) -> List[str]:
    """
    Load corpus as a list of strings. Accepts either JSONL with raw strings
    or a plaintext file with one entry per line.
    """
    try:
        # Try as JSONL of strings
        raw = load_jsonl(path)
        corpus: List[str] = []
        for i, obj in enumerate(raw, 1):
            if not isinstance(obj, str):
                raise ValueError(f"{path}: line {i} must be a JSON string")
            corpus.append(obj)
        return corpus
    except Exception:
        # Fallback: treat as plain text lines
        return [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]


def load_demos(path: Path) -> List[Dict[str, Any]]:
    """
    Load demonstrations as a list of {'prompt':..., 'completion':...} dicts.
    """
    raw = load_jsonl(path)
    demos: List[Dict[str, Any]] = []
    for i, obj in enumerate(raw, 1):
        if not isinstance(obj, dict) or "prompt" not in obj or "completion" not in obj:
            raise ValueError(
                f"{path}: line {i} must be a dict with 'prompt' and 'completion' fields"
            )
        demos.append(obj)
    return demos


def load_prefs(path: Path) -> List[Tuple[str, str, str, int]]:
    """
    Load preferences as a list of ['prompt', 'A', 'B', label] tuples.
    """
    raw = load_jsonl(path)
    prefs: List[Tuple[str, str, str, int]] = []
    for i, obj in enumerate(raw, 1):
        if (
            not isinstance(obj, list)
            or len(obj) != 4
            or not all(isinstance(obj[j], str) for j in range(3))
            or not isinstance(obj[3], int)
        ):
            raise ValueError(
                f"{path}: line {i} must be ['prompt', 'A', 'B', label (int)]"
            )
        prefs.append((obj[0], obj[1], obj[2], obj[3]))
    return prefs


def persist_outputs(summary: Dict[str, Any], demos: List[Dict[str, Any]], output_dir: Path) -> None:
    """
    Persist pipeline results: summary, model handles, token stats, metrics, and seeds.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for name, handle in summary.get("handles", {}).items():
        (output_dir / f"{name}.json").write_text(json.dumps(handle, indent=2), encoding="utf-8")
    token_counts = {
        "pretrain_tokens": summary["handles"]["M0"]["meta"].get("tokens_seen", 0),
        "sft_tokens": sum(len(tokenize(ex["completion"])) for ex in demos),
    }
    metrics = {
        "token_counts": token_counts,
        "losses": summary.get("losses", {}),
        "objective_U": summary.get("objective_U", {}),
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    seeds = {
        "pretrain": summary["handles"]["M0"]["meta"].get("seed"),
        "sft": summary["handles"]["M1"]["meta"].get("seed"),
        "reward_model": summary["handles"]["RM"]["meta"].get("cfg", {}).get("seed"),
        "rlhf": summary["handles"]["M2"]["meta"].get("seed_rlhf"),
    }
    (output_dir / "seeds.json").write_text(json.dumps(seeds, indent=2), encoding="utf-8")


def run_pipeline(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run the full symbolic pipeline given parsed CLI args.
    """
    corpus = load_corpus(Path(args.corpus))
    demos = load_demos(Path(args.demos))
    prefs = load_prefs(Path(args.prefs))

    w = Weights(alpha=args.alpha, beta=args.beta, gamma=args.gamma)
    pre_cfg = PretrainCfg(
        context_len=args.pretrain_context_len,
        lr=args.pretrain_lr,
        epochs=args.pretrain_epochs,
        seed=args.pretrain_seed,
    )
    sft_cfg = SFTCfg(
        lr=args.sft_lr,
        epochs=args.sft_epochs,
        batch_size=args.sft_batch_size,
        seed=args.sft_seed,
    )
    rm_cfg = RewardModelCfg(lr=args.rm_lr, epochs=args.rm_epochs, seed=args.rm_seed)
    rlhf_cfg = RLHFCfg(
        algo="PPO",
        ppo_clip=args.rlhf_ppo_clip,
        kl_penalty=args.rlhf_kl_penalty,
        epochs=args.rlhf_epochs,
        lr=args.rlhf_lr,
        seed=args.rlhf_seed,
    )

    summary = run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        w=w,
        pre_cfg=pre_cfg,
        sft_cfg=sft_cfg,
        rm_cfg=rm_cfg,
        rlhf_cfg=rlhf_cfg,
    )

    persist_outputs(summary, demos, Path(args.output_dir))
    return summary


def build_parser() -> argparse.ArgumentParser:
    """
    Build CLI argument parser.
    """
    p = argparse.ArgumentParser(description="Deploy Codex symbolic training pipeline")
    p.add_argument("--corpus", required=True, help="JSONL of raw code/text lines or TXT (one per line)")
    p.add_argument("--demos", required=True, help="JSONL of {'prompt':..., 'completion':...}")
    p.add_argument("--prefs", required=True, help="JSONL of ['prompt','A','B',label]")
    p.add_argument("--output-dir", required=True, help="Directory for summaries/checkpoints")

    p.add_argument("--alpha", type=float, default=1.0)
    p.add_argument("--beta", type=float, default=1.0)
    p.add_argument("--gamma", type=float, default=0.1)

    p.add_argument("--pretrain-context-len", type=int, default=4096)
    p.add_argument("--pretrain-lr", type=float, default=1e-2)
    p.add_argument("--pretrain-epochs", type=int, default=1)
    p.add_argument("--pretrain-seed", type=int, default=0)

    p.add_argument("--sft-lr", type=float, default=1e-2)
    p.add_argument("--sft-epochs", type=int, default=1)
    p.add_argument("--sft-batch-size", type=int, default=32)
    p.add_argument("--sft-seed", type=int, default=0)

    p.add_argument("--rm-lr", type=float, default=0.1)
    p.add_argument("--rm-epochs", type=int, default=5)
    p.add_argument("--rm-seed", type=int, default=0)

    p.add_argument("--rlhf-lr", type=float, default=1e-2)
    p.add_argument("--rlhf-epochs", type=int, default=1)
    p.add_argument("--rlhf-ppo-clip", type=float, default=0.2)
    p.add_argument("--rlhf-kl-penalty", type=float, default=0.1)
    p.add_argument("--rlhf-seed", type=int, default=0)
    return p


def main(argv: Optional[List[str]] = None) -> Dict[str, Any]:
    parser = build_parser()
    args = parser.parse_args(argv)
    install_requirements()
    return run_pipeline(args)


if __name__ == "__main__":
    main()
