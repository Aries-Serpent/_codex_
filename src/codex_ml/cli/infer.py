"""Minimal inference CLI for loading a model and generating text."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import torch
from transformers import AutoTokenizer

from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default="hf", help="model loader name (hf or decoder_only)")
    parser.add_argument(
        "--checkpoint",
        default="sshleifer/tiny-gpt2",
        help="model checkpoint path or HuggingFace identifier",
    )
    parser.add_argument(
        "--tokenizer",
        default=None,
        help="tokenizer path or name; defaults to checkpoint",
    )
    parser.add_argument("--prompt", default="hello world")
    parser.add_argument("--max-new-tokens", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)

    tok_name = args.tokenizer or args.checkpoint
    tokenizer = AutoTokenizer.from_pretrained(tok_name)

    if args.model_name == "decoder_only":
        model_cfg: dict[str, Any] = {
            "vocab_size": tokenizer.vocab_size,
            "d_model": 64,
            "n_heads": 4,
            "n_layers": 2,
            "max_seq_len": 128,
        }
        model = load_model_with_optional_lora("decoder_only", model_config=model_cfg)
    else:
        model = load_model_with_optional_lora(args.checkpoint)

    model = model.to(args.device)
    torch.manual_seed(args.seed)
    ids = tokenizer.encode(args.prompt, return_tensors="pt").to(args.device)
    out_ids = model.generate(
        ids,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k if args.top_k > 0 else None,
        top_p=args.top_p,
    )
    text = tokenizer.decode(out_ids[0], skip_special_tokens=True)
    print(text)

    art_dir = Path("artifacts/infer")
    art_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    (art_dir / f"{ts}.txt").write_text(text, encoding="utf-8")
    try:
        pkg_version = version("codex")
    except PackageNotFoundError:
        pkg_version = "0.0"
    manifest = {
        "prompt": args.prompt,
        "checkpoint": args.checkpoint,
        "tokenizer": tok_name,
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_k": args.top_k,
        "top_p": args.top_p,
        "seed": args.seed,
        "device": args.device,
        "version": pkg_version,
    }
    (art_dir / f"{ts}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
