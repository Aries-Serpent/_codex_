"""Minimal inference CLI for loading a model and generating text."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, List, Sequence

from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

torch, _HAS_TORCH = optional_import("torch")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")


_ = run_cmd


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    parser = ArgparseJSONParser(description=__doc__)
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
    parser.add_argument("--lora-r", type=int, default=0, help="LoRA rank; 0 disables")
    parser.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha")
    parser.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout probability")
    arg_list: List[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        args = parser.parse_args(arg_list)
        log_event(logger, "cli.start", prog=parser.prog, args=arg_list)
        if not (_HAS_TORCH and _HAS_TRANSFORMERS):
            raise ImportError("torch and transformers are required for inference")
        AutoTokenizer = transformers.AutoTokenizer  # type: ignore[attr-defined]
        tok_name = args.tokenizer or args.checkpoint
        tokenizer = load_from_pretrained(AutoTokenizer, tok_name, revision=get_hf_revision())

        lora_kwargs = {
            "lora_enabled": args.lora_r > 0,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
        }
        if args.model_name == "decoder_only":
            model_cfg: dict[str, Any] = {
                "vocab_size": tokenizer.vocab_size,
                "d_model": 64,
                "n_heads": 4,
                "n_layers": 2,
                "max_seq_len": 128,
            }
            model = load_model_with_optional_lora(
                "decoder_only", model_config=model_cfg, **lora_kwargs
            )
        else:
            model = load_model_with_optional_lora(args.checkpoint, **lora_kwargs)

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

        art_root = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
        art_dir = art_root / "infer"
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
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "version": pkg_version,
        }
        (art_dir / f"{ts}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        log_event(
            logger,
            "cli.finish",
            prog=parser.prog,
            status="ok",
            checkpoint=args.checkpoint,
            device=args.device,
            output_path=str(art_dir / f"{ts}.txt"),
        )
        return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
