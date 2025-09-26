"""Utility to list registered Codex ML plugins."""

from __future__ import annotations

import argparse
from typing import Iterable

from codex_ml.data.registry import list_datasets
from codex_ml.registry import (
    list_models,
    list_tokenizers,
)


def _print_lines(header: str, items: Iterable[str]) -> None:
    print(f"{header}:")
    for item in sorted(set(items)):
        print(f"  - {item}")


def main() -> None:
    parser = argparse.ArgumentParser(description="List Codex ML plugin registries")
    parser.add_argument(
        "--section", choices=["models", "tokenizers", "datasets", "all"], default="all"
    )
    args = parser.parse_args()
    if args.section in {"models", "all"}:
        _print_lines("Models", list_models())
    if args.section in {"tokenizers", "all"}:
        _print_lines("Tokenizers", list_tokenizers())
    if args.section in {"datasets", "all"}:
        _print_lines("Datasets", list_datasets())


if __name__ == "__main__":  # pragma: no cover
    main()
