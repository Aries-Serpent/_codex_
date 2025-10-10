"""Data loading helpers with integrated input validation."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from src.security import validate_input


def safe_line_loader(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def validate_records(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated
