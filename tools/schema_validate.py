#!/usr/bin/env python
"""Validate JSON files against JSON Schemas (local-only).

Usage examples:
  python tools/schema_validate.py --data manifests/selection_guard_rules.json --schema schemas/selection_guard_rules.schema.json
  python tools/schema_validate.py --data manifests/codex_eval_rules.v3.json --schema schemas/codex_eval_rules.v3.schema.json

Notes:
  - If `jsonschema` is not installed, this tool prints an info message and exits 0 (graceful).
  - Designed for local use; do not wire into CI.
"""
from __future__ import annotations

import argparse
import json
import sys


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _validate_pair(data_path: str, schema_path: str) -> bool:
    try:
        import jsonschema  # type: ignore
    except Exception:
        print("[info] jsonschema not installed; skipping validation.", file=sys.stderr)
        return True
    data = _load_json(data_path)
    schema = _load_json(schema_path)
    try:
        jsonschema.validate(instance=data, schema=schema)  # type: ignore
        print(f"[PASS] {data_path} OK {schema_path}")
        return True
    except Exception as e:
        print(f"[fail] {data_path} ! {schema_path}: {e}", file=sys.stderr)
        return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate JSON data with JSON Schema")
    p.add_argument(
        "--data",
        action="append",
        default=[],
        help="Path to JSON data (can repeat; pairs with --schema)",
    )
    p.add_argument(
        "--schema",
        action="append",
        default=[],
        help="Path to JSON schema (repeat; pairs with --data)",
    )
    args = p.parse_args(argv)

    if not args.data or not args.schema or len(args.data) != len(args.schema):
        print("[usage] provide equal counts of --data and --schema", file=sys.stderr)
        return 2

    ok_all = True
    for data_path, schema_path in zip(args.data, args.schema):
        ok = _validate_pair(data_path, schema_path)
        ok_all = ok_all and ok
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
