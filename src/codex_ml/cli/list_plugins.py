"""Utility to list registered Codex ML plugins."""

from __future__ import annotations

import sys
from typing import Iterable, List, Sequence

from codex_ml.data.registry import list_datasets
from codex_ml.registry import (
    list_models,
    list_tokenizers,
)
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = run_cmd


def _print_lines(header: str, items: Iterable[str]) -> None:
    print(f"{header}:")
    for item in sorted(set(items)):
        print(f"  - {item}")


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    parser = ArgparseJSONParser(description="List Codex ML plugin registries")
    parser.add_argument(
        "--section", choices=["models", "tokenizers", "datasets", "all"], default="all"
    )
    arg_list: List[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        args = parser.parse_args(arg_list)
        log_event(logger, "cli.start", prog=parser.prog, args=arg_list)
        if args.section in {"models", "all"}:
            _print_lines("Models", list_models())
        if args.section in {"tokenizers", "all"}:
            _print_lines("Tokenizers", list_tokenizers())
        if args.section in {"datasets", "all"}:
            _print_lines("Datasets", list_datasets())
        log_event(logger, "cli.finish", prog=parser.prog, status="ok", section=args.section)
        return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
