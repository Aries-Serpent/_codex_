"""Minimal text-generation CLI for local smoke testing."""

from __future__ import annotations

import argparse
from typing import Any

from transformers import AutoTokenizer

from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora
from codex_ml.models.generate import generate


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="decoder_only")
    parser.add_argument("--prompt", default="hello world")
    parser.add_argument("--safety", action="store_true", help="Enable prompt/output sanitisation")
    parser.add_argument("--max-new-tokens", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--top-p", type=float, default=1.0)
    args = parser.parse_args(argv)

    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    model_cfg: dict[str, Any] = {
        "vocab_size": tokenizer.vocab_size,
        "d_model": 64,
        "n_heads": 4,
        "n_layers": 2,
        "max_seq_len": 128,
    }
    model = load_model_with_optional_lora(args.model, model_config=model_cfg)
    prompt = args.prompt
    if args.safety:
        from codex_ml.safety import SafetyConfig, sanitize_output, sanitize_prompt

        cfg = SafetyConfig()
        safe = sanitize_prompt(prompt, cfg)
        prompt = safe["text"]
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
    if args.safety:
        safe_out = sanitize_output(text, cfg)
        text = safe_out["text"]
    print(text)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
