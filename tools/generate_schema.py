#!/usr/bin/env python3
"""Generate a lightweight JSON Schema from a sample YAML/JSON config.

This script is intended as a helper for iterating on new configuration
families. It infers basic types from an example config and writes a JSON
Schema (Draft 2020-12) to stdout or a file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml

SCHEMA_URI = "https://json-schema.org/draft/2020-12/schema"


def _merge_schemas(schemas: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    seen = []
    for schema in schemas:
        if schema not in seen:
            seen.append(schema)
    if not seen:
        return {"type": "array"}
    if len(seen) == 1:
        merged["items"] = seen[0]
    else:
        merged["items"] = {"anyOf": seen}
    merged["type"] = "array"
    return merged


def infer_schema(value: Any) -> Dict[str, Any]:
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if value is None:
        return {"type": "null"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, list):
        return _merge_schemas(infer_schema(item) for item in value)
    if isinstance(value, dict):
        properties: Dict[str, Any] = {}
        required = []
        for key, item in value.items():
            properties[key] = infer_schema(item)
            required.append(key)
        schema: Dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": True}
        if required:
            schema["required"] = required
        return schema
    return {"type": "string"}


def build_schema(instance: Any, *, title: str) -> Dict[str, Any]:
    inferred = infer_schema(instance)
    schema: Dict[str, Any] = {"$schema": SCHEMA_URI, "title": title}
    if inferred.get("type") == "object":
        schema.update(inferred)
    else:
        schema.update({"type": "object", "properties": {"value": inferred}, "required": ["value"]})
    return schema


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a JSON Schema from a sample config")
    parser.add_argument("config", type=Path, help="Path to YAML/JSON config file to inspect")
    parser.add_argument("--output", type=Path, help="Optional path to write the generated schema", default=None)
    parser.add_argument("--title", type=str, help="Schema title", default="GeneratedConfigSchema")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.config.exists():
        raise SystemExit(f"config not found: {args.config}")

    instance = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    schema = build_schema(instance, title=args.title)
    output = json.dumps(schema, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
