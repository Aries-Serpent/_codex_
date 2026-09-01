#!/usr/bin/env python3
"""
Generate Baseline

Purpose:
    Generates baseline

Usage:
    python scripts/space_traversal/generate_baseline.py [options]

    Examples:
    $ python scripts/space_traversal/generate_baseline.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

import importlib.util
import logging

logger = logging.getLogger(__name__)

# Generate baseline file from decoded Phase-A snapshot input.
#
# This script can:
#  - Generate a baseline from a base64+gz Phase-A snapshot.
#  - Accept both raw snapshots and fully decoded reports.
#  - Provide output in a deterministic/stable format if requested.
#  - Integrate with stable_manifest if present.
#
# Supports both legacy (capabilities_scored) and summary (gap_count/report) structures.

import argparse
import base64
import gzip
import json
import os
import sys
from pathlib import Path
from typing import Any

stable_manifest: Any | None
if importlib.util.find_spec("scripts.space_traversal.stable_manifest"):
    from scripts.space_traversal import stable_manifest as stable_manifest_module
    stable_manifest = stable_manifest_module
else:
    stable_manifest = None

DEFAULT_MAX_BYTES = 200 * 1024 * 1024
DEFAULT_OUTPUT = Path("audit_artifacts/baseline_summary.json")

__all__ = [
    "decode_b64_gz_bytes",
    "load_from_local",
    "write_baseline",
    "build_baseline",
    "main",
]


def decode_b64_gz_bytes(b64_bytes: bytes) -> bytes:
    decoded = base64.b64decode(b64_bytes)
    return gzip.decompress(decoded)


def load_from_local(path: str, max_bytes: int) -> Any:
    with open(path, "rb") as fh:
        b64 = fh.read()
    if len(b64) > max_bytes:
        raise RuntimeError("input exceeds max_bytes")
    decoded_bytes = decode_b64_gz_bytes(b64)
    try:
        return json.loads(decoded_bytes)
    except Exception:
        # Attempt as UTF-8 text (could be doubly-encoded)
        return json.loads(decoded_bytes.decode("utf-8"))


def _load_decoded(path: Path) -> dict[str, Any]:
    # Path can be binary (b64+gz) or decoded json
    if path.suffix in {".b64", ".gz", ".gz.b64"} or path.name.endswith(".b64"):
        return load_from_local(str(path), DEFAULT_MAX_BYTES)
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(decoded: dict[str, Any]) -> dict[str, Any]:
    report = decoded.get("report", {})
    if not isinstance(report, dict):
        return {}
    return {
        "id": report.get("id", ""),
        "generated_at": report.get("generated_at", ""),
    }


def write_baseline(baseline_path: str, data: Any, stable_output: bool = False) -> str:
    d = os.path.dirname(baseline_path)
    if d:
        os.makedirs(d, exist_ok=True)
    content = data
    if stable_output and stable_manifest is not None:
        stable_manifest.write_stable_json(data, Path(baseline_path))
    else:
        with open(baseline_path, "w", encoding="utf-8") as fh:
            json.dump(content, fh, indent=2, ensure_ascii=False)
    return baseline_path


def build_baseline(
    decoded: dict[str, Any], stable_output: bool = False, output_path: Path | None = None
) -> Path:
    # Prefer "capabilities_scored" array if available, else produce summary format
    if isinstance(decoded, dict) and "capabilities_scored" in decoded:
        baseline = decoded["capabilities_scored"]
    else:
        baseline = {
            "report": _ensure_report(decoded),
            "gap_count": len(decoded.get("gaps", [])),
        }
    destination = output_path or DEFAULT_OUTPUT
    write_baseline(str(destination), baseline, stable_output)
    return destination


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate baseline from base64+gz Phase-A snapshot or decoded report"
    )
    parser.add_argument(
        "--input", type=str, required=True, help="local b64+gz path or decoded JSON file"
    )
    parser.add_argument("--baseline-path", type=str, help="output baseline path (file)")
    parser.add_argument(
        "--stable-output", action="store_true", help="write deterministic/stable JSON output"
    )
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args() if argv is None else parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.baseline_path) if args.baseline_path else DEFAULT_OUTPUT
    stable_output = getattr(args, "stable_output", False)
    getattr(args, "max_bytes", DEFAULT_MAX_BYTES)

    if not input_path.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2

    try:
        decoded = _load_decoded(input_path)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"Decode error: {exc}", file=sys.stderr)
        return 3

    try:
        build_baseline(decoded, stable_output=stable_output, output_path=output_path)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"Write baseline error: {exc}", file=sys.stderr)
        return 4

    print(f"Wrote baseline to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
