"""
Cli Module

This module provides functionality for cli.

Usage:
    from tokenization.cli import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from codex.logging.structured_logger import logger
from codex_ml.tokenization import sentencepiece_adapter

SentencePieceAdapter = sentencepiece_adapter.SentencePieceAdapter


def _resolve_model_path(model: str | Path | None) -> Path:
    candidate = model or os.getenv("CODEX_TOKENIZER_MODEL")
    if not candidate:
        raise ValueError(
            "Tokenization model path required; set CODEX_TOKENIZER_MODEL or pass `model`."
        )
    return Path(candidate)


def _train(args: argparse.Namespace) -> None:
    adapter = SentencePieceAdapter(Path(args.model_prefix).with_suffix(".model"))
    adapter.train_or_load(args.corpus, vocab_size=args.vocab_size)
    tok_json = adapter.model_prefix.with_suffix(".tokenizer.json")
    tok_json.write_text(
        json.dumps({"model_file": str(adapter.model_path)}, indent=2),
        encoding="utf-8",
    )


def _encode(args: argparse.Namespace) -> None:
    adapter = SentencePieceAdapter(Path(args.model)).load()
    ids = adapter.encode(args.text)
    logger.info(" ".join(str(i) for i in ids))


def _decode(args: argparse.Namespace) -> None:
    adapter = SentencePieceAdapter(Path(args.model)).load()
    ids = [int(i) for i in args.ids.split(",") if i]
    logger.info(adapter.decode(ids))


def _stats(args: argparse.Namespace) -> None:
    adapter = SentencePieceAdapter(Path(args.model)).load()
    size = getattr(adapter.sp, "vocab_size", lambda: 0)()
    logger.info(size)


def _refresh(args: argparse.Namespace) -> None:
    model = Path(args.model)
    manifest = {
        "model": str(model),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if args.notes:
        manifest["notes"] = args.notes
    special = model.with_suffix(".special_tokens.json")
    if special.exists():
        manifest["special_tokens"] = json.loads(special.read_text(encoding="utf-8"))
    output = Path(args.output) if args.output else model.with_suffix(".provenance.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def encode(
    text: str,
    *,
    model: str | Path | None = None,
    max_len: int | None = None,
    pad: bool = False,
    trunc: bool = False,
    pad_id: int = 0,
) -> list[int]:
    """Encode ``text`` using a SentencePiece model with optional padding/truncation."""

    adapter = SentencePieceAdapter(_resolve_model_path(model)).load()
    ids = list(adapter.encode(text))
    if max_len is not None:
        if trunc and len(ids) > max_len:
            ids = ids[:max_len]
        if pad and len(ids) < max_len:
            ids = ids + [pad_id] * (max_len - len(ids))
    return ids


def decode(ids: Sequence[int], *, model: str | Path | None = None) -> str:
    """Decode ``ids`` using a SentencePiece model resolved from ``model`` or env."""

    adapter = SentencePieceAdapter(_resolve_model_path(model)).load()
    return adapter.decode(list(ids))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Tokenization utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_train = sub.add_parser("train", help="train a SentencePiece tokenizer")
    p_train.add_argument("corpus", help="path to training corpus")
    p_train.add_argument("model_prefix", help="output model prefix")
    p_train.add_argument("--vocab-size", type=int, default=32000)
    p_train.set_defaults(func=_train)

    p_encode = sub.add_parser("encode", help="encode text with a model")
    p_encode.add_argument("model", help="path to tokenizer model")
    p_encode.add_argument("text", help="text to encode")
    p_encode.set_defaults(func=_encode)

    p_decode = sub.add_parser("decode", help="decode ids with a model")
    p_decode.add_argument("model", help="path to tokenizer model")
    p_decode.add_argument("ids", help="comma-separated token ids")
    p_decode.set_defaults(func=_decode)

    p_stats = sub.add_parser("stats", help="print vocabulary size")
    p_stats.add_argument("model", help="path to tokenizer model")
    p_stats.set_defaults(func=_stats)

    p_refresh = sub.add_parser("refresh", help="emit a provenance manifest for a tokenizer model")
    p_refresh.add_argument("model", help="path to tokenizer model")
    p_refresh.add_argument("--output", help="optional output manifest path")
    p_refresh.add_argument("--notes", default="", help="free-form notes recorded in the manifest")
    p_refresh.set_defaults(func=_refresh)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()


__all__ = [
    "SentencePieceAdapter",
    "decode",
    "encode",
    "main",
]
