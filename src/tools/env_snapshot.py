"""Environment snapshot CLI used by status automation and tests."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from codex_ml.utils import environment_summary

DEFAULT_OUTPUT = Path("env_snapshot.json")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a reproducible environment snapshot.")
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="File path to write the JSON snapshot (default: env_snapshot.json).",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def capture_environment() -> dict[str, Any]:
    """Collect environment details, including variables, for serialization.

    Captures:
    - Python version and platform information (from environment_summary)
    - Python interpreter path
    - All environment variables
    - CODEX_* environment variables (highlighted separately)
    """
    info = environment_summary()

    # Add interpreter path explicitly
    info["python_executable"] = sys.executable

    # Capture all environment variables
    info["env"] = dict(os.environ)

    # Highlight CODEX_* environment variables for easy access
    codex_vars = {k: v for k, v in os.environ.items() if k.startswith("CODEX_")}
    if codex_vars:
        info["codex_env_vars"] = codex_vars

    return info


def write_snapshot(out_path: Path, data: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> Path:
    args = _parse_args(argv)
    snapshot = capture_environment()
    write_snapshot(args.out, snapshot)
    print(f"Environment snapshot written to {args.out}")
    return args.out


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
