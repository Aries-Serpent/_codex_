"""
from __future__ import annotations

Infer Module

This module provides functionality for infer.

Usage:
    from cli.infer import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging

logger = logging.getLogger(__name__)


import json
import os
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Optional

from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora
from codex_ml.safety import ModerationAdapter, ModerationRejection, ModerationSettings
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

torch, _HAS_TORCH = optional_import("torch")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")

# Module-level sentinel so tests can monkeypatch `infer.AutoTokenizer`
AutoTokenizer = (
    transformers.AutoTokenizer if _HAS_TRANSFORMERS and transformers is not None else None
)


_ = run_cmd


def main(argv: Optional[Sequence[str]] = None) -> int:
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
    parser.add_argument(
        "--moderation",
        action="store_true",
        help="Enable moderation checks on prompts and outputs before execution.",
    )
    parser.add_argument(
        "--moderation-provider",
        default="offline",
        help="Optional moderation provider in module:function form (defaults to offline rules).",
    )
    parser.add_argument(
        "--moderation-policy",
        default=None,
        help="Override the default moderation policy path (uses configs/base/safety/policy.yaml by default).",  # noqa: E501
    )
    parser.add_argument(
        "--moderation-fail-open",
        action="store_true",
        help="Allow prompts/outputs to proceed even if moderation vetoes them (event is logged).",
    )
    parser.add_argument(
        "--moderation-audit-log",
        default=None,
        help="Optional NDJSON file to capture moderation decisions for auditing.",
    )
    arg_list: list[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        args = parser.parse_args(arg_list)
        log_event(logger, "cli.start", prog=parser.prog, args=arg_list)
        if not (_HAS_TORCH and _HAS_TRANSFORMERS):
            raise ImportError("torch and transformers are required for inference")
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
        moderation_adapter: Optional[ModerationAdapter] = None
        prompt_decision = None
        output_decision = None
        moderation_enabled = bool(
            args.moderation
            or args.moderation_provider.lower() != "offline"
            or args.moderation_policy
            or args.moderation_audit_log
        )
        prompt_text = args.prompt
        if moderation_enabled:
            moderation_settings = ModerationSettings(
                enabled=True,
                provider=args.moderation_provider or "offline",
                rules_path=args.moderation_policy,
                fail_open=args.moderation_fail_open,
                audit_log=args.moderation_audit_log,
                label="cli.infer",
            )
            moderation_adapter = ModerationAdapter.from_settings(moderation_settings)
            try:
                prompt_decision = moderation_adapter.enforce(prompt_text, stage="prompt")
            except ModerationRejection as exc:
                type(exc).__name__
                logger.debug("ModerationRejection: <ERROR_TYPE>")
                log_event(
                    logger,
                    "moderation.block",
                    stage="prompt",
                    provider=moderation_adapter.provider_name,
                    matches=list(exc.decision.matches),
                    reasons=list(exc.decision.reasons),
                )
                raise SystemExit(f"Prompt blocked by moderation: {exc}") from exc
            if prompt_decision and prompt_decision.sanitized_text is not None:
                prompt_text = prompt_decision.sanitized_text

        ids = tokenizer.encode(prompt_text, return_tensors="pt").to(args.device)
        out_ids = model.generate(
            ids,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_k=args.top_k if args.top_k > 0 else None,
            top_p=args.top_p,
        )
        text = tokenizer.decode(out_ids[0], skip_special_tokens=True)
        if moderation_adapter:
            try:
                output_decision = moderation_adapter.enforce(text, stage="output")
            except ModerationRejection as exc:
                type(exc).__name__
                logger.debug("ModerationRejection: <ERROR_TYPE>")
                log_event(
                    logger,
                    "moderation.block",
                    stage="output",
                    provider=moderation_adapter.provider_name,
                    matches=list(exc.decision.matches),
                    reasons=list(exc.decision.reasons),
                )
                raise SystemExit(f"Output blocked by moderation: {exc}") from exc
            if output_decision and output_decision.sanitized_text is not None:
                text = output_decision.sanitized_text
        logger.info(text)

        art_root = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
        art_dir = art_root / "infer"
        art_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        (art_dir / f"{ts}.txt").write_text(text, encoding="utf-8")
        try:
            pkg_version = version("codex")
        except PackageNotFoundError as e:
            type(e).__name__
            logger.debug("PackageNotFoundError: <ERROR_TYPE>")
            logger.warning("PackageNotFoundError: <ERROR_TYPE>", exc_info=True)
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
        if moderation_adapter:
            manifest["prompt_moderated"] = prompt_text
            manifest["moderation"] = {
                "provider": moderation_adapter.provider_name,
                "fail_open": moderation_adapter.settings.fail_open,
                "prompt": prompt_decision.to_dict() if prompt_decision else None,
                "output": output_decision.to_dict() if output_decision else None,
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
