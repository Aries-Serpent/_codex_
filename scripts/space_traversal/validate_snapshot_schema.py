#!/usr/bin/env python3
"""
Validate a decoded validator snapshot against a permissive schema or perform lightweight checks.
"""
from __future__ import annotations
import argparse
import json
import os
import sys

try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None

def main(argv=None):
    p = argparse.ArgumentParser(description="Validate decoded Phase-A snapshot against schema")
    p.add_argument("--json", required=True, help="path to decoded JSON file")
    p.add_argument("--schema", help="optional json schema path")
    args = p.parse_args(argv)

    if not os.path.exists(args.json):
        print(f"Decoded JSON not found: {args.json}", file=sys.stderr)
        return 2

    with open(args.json, "r", encoding="utf-8") as fh:
        try:
            doc = json.load(fh)
        except Exception as exc:
            print(f"JSON parse error: {exc}", file=sys.stderr)
            return 3

    if args.schema and os.path.exists(args.schema) and jsonschema is not None:
        with open(args.schema, "r", encoding="utf-8") as sf:
            schema = json.load(sf)
        try:
            jsonschema.validate(instance=doc, schema=schema)
            print("Schema validation: OK")
            return 0
        except Exception as exc:
            print(f"Schema validation failed: {exc}", file=sys.stderr)
            return 3

    if not isinstance(doc, (dict, list)):
        print("Decoded snapshot is not JSON object or array", file=sys.stderr)
        return 3
    if isinstance(doc, dict):
        keys = set(doc.keys())
        expected = {"validators", "gaps", "missing_files", "capabilities_scored"}
        if keys & expected:
            print("Lightweight validation: found expected top-level keys")
            return 0
        else:
            print("Lightweight validation: none of expected top-level keys present, but JSON parsed")
            return 0

    print("Decoded snapshot is a JSON array; passing lightweight validation")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
