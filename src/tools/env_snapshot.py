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
_SENSITIVE_ENV_KEYS = {
    "CODEX_MASTER_KEY",
    "CODEX_BACKUP_KEY",
    "CODEX_RUNNER_TOKEN",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "TOKEN",
    "SECRET_KEY",
    "SECRET",
    "API_KEY",
    "PASSWORD",
    "SESSION_TOKEN",
}


def _safe_env() -> dict[str, str]:
    """Return a redacted environment map with secrets stripped."""
    sanitized: dict[str, str] = {}
    for key, value in os.environ.items():
        upper_key = key.upper()
        if upper_key in _SENSITIVE_ENV_KEYS or any(
            marker in upper_key for marker in ("TOKEN", "SECRET", "PASSWORD", "API_KEY")
        ):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = value
    return sanitized


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
    info["python_executable"] = sys.executable
    info["env"] = _safe_env()
    codex_vars = {
        key: "[REDACTED]" if key.upper() in _SENSITIVE_ENV_KEYS or "TOKEN" in key.upper() else value
        for key, value in os.environ.items()
        if key.startswith("CODEX_")
    }
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
