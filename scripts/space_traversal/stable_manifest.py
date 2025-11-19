from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _stable_list(values: list[Any]) -> list[Any]:
    normalized: list[Any] = []
    for item in values:
        if isinstance(item, dict):
            normalized.append(_stable_dict(item))
        elif isinstance(item, list):
            normalized.append(_stable_list(item))
        else:
            normalized.append(item)
    try:
        return sorted(normalized, key=lambda value: json.dumps(value, sort_keys=True))
    except TypeError:
        return normalized


def _stable_dict(value: dict[str, Any]) -> dict[str, Any]:
    stable: dict[str, Any] = {}
    for key in sorted(value):
        entry = value[key]
        if isinstance(entry, dict):
            stable[key] = _stable_dict(entry)
        elif isinstance(entry, list):
            stable[key] = _stable_list(entry)
        else:
            stable[key] = entry
    return stable


def normalize_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        return _stable_dict(payload)
    if isinstance(payload, list):
        return _stable_list(payload)
    return payload


def stable_dumps(payload: Any) -> str:
    normalized = normalize_payload(payload)
    return json.dumps(normalized, indent=2, sort_keys=True, ensure_ascii=False)


def write_stable_json(payload: Any, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(stable_dumps(payload), encoding="utf-8")
    return destination
