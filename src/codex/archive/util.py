"""Compatibility helpers for legacy `codex.archive.util` imports."""

from __future__ import annotations

import json


def parse_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return value


def format_data(data):
    seen = set()

    def _detect(obj):
        obj_id = id(obj)
        if obj_id in seen:
            raise RecursionError("Circular reference detected")
        seen.add(obj_id)
        try:
            if isinstance(obj, dict):
                for value in obj.values():
                    _detect(value)
            elif isinstance(obj, (list, tuple, set)):
                for value in obj:
                    _detect(value)
        finally:
            seen.discard(obj_id)

    _detect(data)
    return json.dumps(data, sort_keys=True, default=str)


__all__ = ["parse_value", "format_data"]
