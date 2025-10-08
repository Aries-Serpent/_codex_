"""Validate a Codex ML checkpoint directory for basic integrity."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def _load_metadata(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing metadata: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"metadata is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"metadata must be a JSON object: {path}")
    return data


def validate_checkpoint_dir(directory: Path, expect_schema: str | None = None) -> Dict[str, Any]:
    if not directory.is_dir():
        raise SystemExit(f"not a directory: {directory}")
    weights = directory / "weights.pt"
    metadata = directory / "metadata.json"
    if not weights.exists():
        raise SystemExit(f"missing weights: {weights}")
    info = _load_metadata(metadata)
    schema = str(info.get("schema_version", "unknown"))
    if expect_schema and schema != expect_schema:
        raise SystemExit(f"schema mismatch: expected {expect_schema!r} but found {schema!r}")
    return info


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        type=Path,
        help="Checkpoint directory to validate.",
    )
    parser.add_argument(
        "--schema-version",
        help="Optional schema version to enforce (e.g. '1').",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Print metadata JSON on success.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    info = validate_checkpoint_dir(args.path, args.schema_version)
    if args.show:
        json.dump(info, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
