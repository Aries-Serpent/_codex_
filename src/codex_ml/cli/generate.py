"""Minimal text-generation CLI for local smoke testing."""

from __future__ import annotations

import argparse
import sys
from typing import Any, List, Sequence

from codex_ml import __version__
from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora
from codex_ml.models.generate import generate
from codex_ml.safety import (
    SafetyConfig,
    SafetyFilters,
    SafetyViolation,
    sanitize_output,
    sanitize_prompt,
)
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

_ = run_cmd


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    parser = ArgparseJSONParser(description=__doc__)
    parser.add_argument("--model", default="decoder_only")
    parser.add_argument("--prompt", default="hello world")
    parser.add_argument(
        "--no-safety",
        action="store_true",
        help="Disable policy enforcement (redaction still applies)",
    )
    parser.add_argument(
        "--safety-policy",
        default=None,
        help="Path to a YAML policy overriding configs/safety/policy.yaml",
    )
    parser.add_argument(
        "--safety-bypass",
        action="store_true",
        help="Bypass blocking rules while recording audit logs",
    )
    parser.add_argument("--max-new-tokens", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--lora-r", type=int, default=0, help="LoRA rank; 0 disables")
    parser.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha")
    parser.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout probability")
    parser.add_argument("--safety", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--version", action="version", version=f"codex-generate {__version__}")
    arg_list: List[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        args = parser.parse_args(arg_list)
        log_event(logger, "cli.start", prog=parser.prog, args=arg_list)

        transformers, has_tf = optional_import("transformers")
        AutoTokenizer = None
        if has_tf and transformers is not None:
            AutoTokenizer = getattr(transformers, "AutoTokenizer", None)
            has_tf = bool(AutoTokenizer)
        if not has_tf or AutoTokenizer is None:
            raise ImportError("transformers is required for generation")
        tokenizer = load_from_pretrained(
            AutoTokenizer,
            "openai-community/gpt2",
            use_fast=True,
            revision=get_hf_revision(),
        )
        model_cfg: dict[str, Any] = {
            "vocab_size": tokenizer.vocab_size,
            "d_model": 64,
            "n_heads": 4,
            "n_layers": 2,
            "max_seq_len": 128,
        }
        lora_kwargs = {
            "lora_enabled": args.lora_r > 0,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
        }
        model = load_model_with_optional_lora(args.model, model_config=model_cfg, **lora_kwargs)
        safety_enabled = not args.no_safety
        bypass = bool(args.safety_bypass)
        policy_path = args.safety_policy
        prompt = args.prompt
        safety_cfg = SafetyConfig()
        prompt_result = sanitize_prompt(prompt, safety_cfg)
        prompt = prompt_result["text"]
        filters: SafetyFilters | None = None
        if safety_enabled or args.safety:
            filters = SafetyFilters.from_policy_file(policy_path)
            try:
                prompt = filters.enforce(prompt, stage="prompt", bypass=bypass)
            except SafetyViolation as exc:
                log_event(
                    logger,
                    "cli.finish",
                    prog=parser.prog,
                    status="error",
                    phase="prompt",
                    error_kind=exc.__class__.__name__,
                    error_message=str(exc),
                )
                raise SystemExit(f"Safety violation (prompt): {exc}") from exc
        ids = tokenizer.encode(prompt, return_tensors="pt")
        out = generate(
            model,
            tokenizer,
            ids,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            eos_id=tokenizer.eos_token_id,
            pad_id=tokenizer.pad_token_id,
        )
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        output_result = sanitize_output(text, safety_cfg)
        text = output_result["text"]
        if filters is not None and safety_enabled:
            try:
                text = filters.enforce(text, stage="output", bypass=bypass)
            except SafetyViolation as exc:
                log_event(
                    logger,
                    "cli.finish",
                    prog=parser.prog,
                    status="error",
                    phase="output",
                    error_kind=exc.__class__.__name__,
                    error_message=str(exc),
                )
                raise SystemExit(f"Safety violation (output): {exc}") from exc
        print(text)
        log_event(
            logger,
            "cli.finish",
            prog=parser.prog,
            status="ok",
            model=args.model,
            tokens_generated=len(text.split()),
        )
        return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
