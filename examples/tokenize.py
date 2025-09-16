"""Minimal tokenizer example using the registry system."""

from __future__ import annotations

import json

from codex_ml.registry import get_tokenizer, register_tokenizer
from examples.plugins.toy_tokenizer import build as toy_tokenizer


def main() -> None:
    register_tokenizer("toy", toy_tokenizer, override=True)
    tokenizer = get_tokenizer("toy", vocab={})
    text = "Codex makes registries fun!"
    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)
    print(json.dumps({"text": text, "encoded": encoded, "decoded": decoded}, indent=2))


if __name__ == "__main__":
    main()
