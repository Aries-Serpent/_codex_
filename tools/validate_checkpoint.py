"""Validate checkpoint directories written by ``codex_ml.utils.checkpoint_core``."""

from __future__ import annotations

import argparse
import hashlib
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_checkpoint_dir(directory: Path, expect_schema: str | None = None) -> Dict[str, Any]:
    if not directory.is_dir():
        raise SystemExit(f"not a directory: {directory}")
    state_file = directory / "state.pt"
    metadata = directory / "metadata.json"
    digest_file = directory / "state.sha256"
    if not state_file.exists():
        raise SystemExit(f"missing checkpoint payload: {state_file}")
    info = _load_metadata(metadata)
    schema = str(info.get("schema_version", "unknown"))
    if expect_schema and schema != expect_schema:
        raise SystemExit(f"schema mismatch: expected {expect_schema!r} but found {schema!r}")

    digest_value = info.get("digest_sha256")
    if digest_value:
        recorded = None
        if digest_file.exists():
            recorded = digest_file.read_text(encoding="utf-8").strip()
            if recorded != digest_value:
                raise SystemExit(
                    f"state.sha256 mismatch: expected {digest_value!r} but found {recorded!r}"
                )
        computed = _sha256(state_file)
        if computed != digest_value:
            raise SystemExit(
                f"payload digest mismatch: expected {digest_value!r} but computed {computed!r}"
            )
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
