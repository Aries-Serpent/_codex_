#!/usr/bin/env python3
"""
Validate Snapshot Schema

Purpose:
    Validates snapshot_schema

Usage:
    python scripts/space_traversal/validate_snapshot_schema.py [options]
    
    Examples:
    $ python scripts/space_traversal/validate_snapshot_schema.py --help

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

import logging
logger = logging.getLogger(__name__)
"""
Validate a decoded validator snapshot against a permissive schema or perform lightweight checks.

Features:
- Validates decoded Phase-A snapshot JSON against a schema (if provided and jsonschema installed).
- Falls back to lightweight structure validation if jsonschema is unavailable.
- Supports both CLI and import as a module.
"""
import argparse
import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA = Path("scripts/space_traversal/schemas/validate_report_schema.json")


class ValidationError(Exception):
    """Raised when the snapshot does not conform to the schema."""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonschema():
    spec = importlib.util.find_spec("jsonschema")
    if spec is None:
        return None
    return importlib.import_module("jsonschema")


def validate_snapshot(payload: dict[str, Any], schema_path: Path | None = None) -> None:
    schema_source = schema_path or DEFAULT_SCHEMA
    schema = _load_json(schema_source)
    jsonschema = _load_jsonschema()

    if jsonschema is None:
        # Fallback lightweight validation
        if not isinstance(payload, dict):
            raise ValidationError("Decoded payload must be a JSON object")
        expected_keys = {"validators", "gaps", "missing_files", "capabilities_scored", "report"}
        if not (expected_keys & set(payload.keys())):
            raise ValidationError(
                f"Decoded payload missing required keys. Got: {list(payload.keys())}"
            )
        return

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        message = "; ".join(error.message for error in errors)
        raise ValidationError(message)


def parse_args(argv=None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        argv: Optional argument list (for testing)
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Validate decoded Phase-A snapshot against a schema"
    )
    parser.add_argument("--json", type=Path, required=True, help="Path to decoded JSON file")
    parser.add_argument("--schema", type=Path, help="Optional JSON schema path")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    """Main entry point for snapshot schema validation.
    
    Args:
        argv: Optional argument list (for testing)
    
    Returns:
        Exit code (0 = success, non-zero = error)
    """
    args = parse_args(argv)
    if not args.json.exists():
        print(f"Decoded JSON not found: {args.json}", file=sys.stderr)
        return 2
    try:
        payload = _load_json(args.json)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"JSON parse error: {exc}", file=sys.stderr)
        return 3

    try:
        validate_snapshot(payload, args.schema)
    except ValidationError as exc:
        logger.debug(f"ValidationError: {exc}")
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print("Snapshot validated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
