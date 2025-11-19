from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
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
        if not isinstance(payload, dict):
            raise ValidationError("Decoded payload must be a JSON object")
        if "report" not in payload or "gaps" not in payload:
            raise ValidationError("Decoded payload missing required keys: report, gaps")
        return

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        message = "; ".join(error.message for error in errors)
        raise ValidationError(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate decoded snapshot against schema")
    parser.add_argument("path", type=Path, help="Path to decoded JSON file")
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Optional schema path (defaults to bundled schema)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = _load_json(args.path)
    try:
        validate_snapshot(payload, args.schema)
    except ValidationError as exc:
        print(f"Validation failed: {exc}")
        return 1
    print("Snapshot validated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
