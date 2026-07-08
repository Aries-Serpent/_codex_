"""Top-level helper for `python -m codex_ml.main` or `codex_ml.main:main`.

This module provides a light wrapper that nudges callers toward the package
CLI (`python -m codex_ml.cli`).  It offers a `--version` flag and a
`--forward` option that proxies arguments to the CLI for convenience while
remaining optional so environments without Typer can still query metadata.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import argparse  # noqa: E402
import importlib  # noqa: E402
import sys  # noqa: E402
from collections.abc import Sequence  # noqa: E402

from codex.logging.structured_logger import logger

_HELP_EPILOG = "Run `python -m codex_ml.cli --help` for full subcommands."


def _resolve_version() -> str:
    try:
        mod = importlib.import_module("codex_ml")
    except (ValueError, TypeError):
        logger.warning("Exception occurred", exc_info=True)
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
        from codex_ml import cli as cli_module
    except (IOError, OSError) as exc:  # pragma: no cover - optional dependency path
        raise SystemExit(f"codex_ml.cli is unavailable: {exc}") from exc

    cli_entry = getattr(cli_module, "cli", None)
    if cli_entry is None:
        raise SystemExit("codex_ml.cli is unavailable: missing 'cli' entry point")

    forwarded = list(argv)
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]

    if hasattr(cli_entry, "main"):
        try:
            cli_entry.main(args=forwarded, prog_name="codex-ml", standalone_mode=False)
        except SystemExit as exc:
            type(exc).__name__
            logger.debug("SystemExit: <ERROR_TYPE>")
            logger.debug("Exception caught, returning", exc_info=True)
            return int(exc.code or 0)
        return 0

    # Fallback: invoke the entry callable directly for non-click environments.
    try:
        result = cli_entry(*forwarded)
    except SystemExit as exc:  # pragma: no cover - compatibility path
        return int(exc.code or 0)
    except (IOError, OSError) as exc:  # pragma: no cover - optional dependency path
        raise SystemExit(f"codex_ml.cli is unavailable: {exc}") from exc
    return int(result or 0)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    exit_code = 0
    if args.version:
        logger.info(_resolve_version())
    if args.forward is not None:
        exit_code = _forward_to_cli(args.forward)
    if not args.version and args.forward is None:
        parser.print_help(sys.stdout)
    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main(sys.argv[1:]))
