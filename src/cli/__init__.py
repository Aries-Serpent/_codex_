# src/cli package
"""CLI package — exposes main() entry point for the Codex training CLI."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import Optional

# Import train_codex for backward compatibility
from cli import train_codex

__all__ = ["main", "train_codex"]


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point: validate required arguments for Codex training.

    Parses the command-line arguments and raises ``SystemExit`` (via argparse)
    when required arguments are missing.  This package-level shim satisfies
    ``import src.cli as cli; cli.main()`` callers; the full training
    implementation lives in ``src/cli.py`` (the standalone module).

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]`` when *None*).

    Returns:
        Exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument(
        "--config-path",
        required=True,
        help="Directory containing Hydra configs",
    )
    parser.add_argument(
        "--config-name",
        default="train",
        help="Config file name inside the directory",
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    # parse_args raises SystemExit on missing required args
    parser.parse_args(argv)
    return 0
