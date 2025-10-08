"""Top-level helper for `python -m codex_ml.main` or `codex_ml.main:main`.

This module provides a light wrapper that nudges callers toward the package
CLI (`python -m codex_ml.cli`).  It offers a `--version` flag and a
`--forward` option that proxies arguments to the CLI for convenience while
remaining optional so environments without Typer can still query metadata.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from typing import Sequence

_HELP_EPILOG = "Run `python -m codex_ml.cli --help` for full subcommands."


def _resolve_version() -> str:
    try:
        mod = importlib.import_module("codex_ml")
    except Exception:
        return "unknown"
    return str(getattr(mod, "__version__", "unknown"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-ml",
        description="Codex ML entry point",  # short description for usage banner
        epilog=_HELP_EPILOG,
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the package version if available.",
    )
    parser.add_argument(
        "--forward",
        nargs=argparse.REMAINDER,
        metavar="CLI_ARGS",
        help="Forward remaining arguments to `codex_ml.cli`.",
    )
    return parser


def _forward_to_cli(argv: Sequence[str]) -> int:
    try:
        from codex_ml.cli.__main__ import main as cli_main
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise SystemExit(f"codex_ml.cli is unavailable: {exc}")
    return int(cli_main(list(argv)))


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    exit_code = 0
    if args.version:
        print(_resolve_version())
    if args.forward is not None:
        exit_code = _forward_to_cli(args.forward)
    if not args.version and args.forward is None:
        parser.print_help(sys.stdout)
    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main(sys.argv[1:]))
