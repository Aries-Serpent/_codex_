"""Data loading helpers with integrated input validation."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import cast

from security import SecurityError, validate_input


def safe_line_loader(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def _validate_json_value(value: object) -> object:
    """Validate string leaves and keys while preserving JSON scalar types."""
    if isinstance(value, str):
        return validate_input(value, input_type="json")
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, dict):
        return {
            validate_input(key, input_type="text"): _validate_json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_validate_json_value(item) for item in value]
    raise SecurityError(f"Unsupported JSON value type: {type(value)}")


def validate_records(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        if not isinstance(record, dict):
            raise SecurityError(f"Expected dict record, got {type(record)}")
        validated.append(cast(dict, _validate_json_value(record)))
    return validated
