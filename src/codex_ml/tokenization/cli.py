from __future__ import annotations

import argparse
import json
from pathlib import Path

from codex_ml.tokenization import sentencepiece_adapter

SentencePieceAdapter = sentencepiece_adapter.SentencePieceAdapter


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
    ids = adapter.encode(
        args.text,
        padding=args.padding,
        truncation=args.truncation,
        max_length=args.max_length,
    )
    print(" ".join(str(i) for i in ids))


def _decode(args: argparse.Namespace) -> None:
    adapter = SentencePieceAdapter(Path(args.model)).load()
    ids = [int(i) for i in args.ids.split(",") if i]
    print(adapter.decode(ids))


def _stats(args: argparse.Namespace) -> None:
    adapter = SentencePieceAdapter(Path(args.model)).load()
    size = getattr(adapter.sp, "vocab_size", lambda: 0)()
    print(size)


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
    p_encode.add_argument("--max-length", type=int, default=None)
    p_encode.add_argument("--padding", default=None)
    p_encode.add_argument("--truncation", default=None)
    p_encode.set_defaults(func=_encode)

    p_decode = sub.add_parser("decode", help="decode ids with a model")
    p_decode.add_argument("model", help="path to tokenizer model")
    p_decode.add_argument("ids", help="comma-separated token ids")
    p_decode.set_defaults(func=_decode)

    p_stats = sub.add_parser("stats", help="print vocabulary size")
    p_stats.add_argument("model", help="path to tokenizer model")
    p_stats.set_defaults(func=_stats)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
