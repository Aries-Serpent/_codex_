"""Environment snapshot CLI used by status automation and tests."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Sequence

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
    """Collect environment details, including variables, for serialization."""

    info = environment_summary()
    info["env"] = dict(os.environ)
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
