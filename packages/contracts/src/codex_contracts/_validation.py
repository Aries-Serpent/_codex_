"""Shared validation helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def freeze_json_mapping(value: Mapping[str, Any], *, field_name: str) -> Mapping[str, JsonValue]:
    """Validate and shallow-freeze a JSON-compatible mapping."""

    copied = dict(value)
    try:
        json.dumps(copied, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must contain only JSON-compatible values") from exc
    return MappingProxyType(copied)
