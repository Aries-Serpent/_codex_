"""Shared validation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
FrozenJsonValue = (
    None
    | bool
    | int
    | float
    | str
    | tuple["FrozenJsonValue", ...]
    | Mapping[str, "FrozenJsonValue"]
)

DEFAULT_MAX_DEPTH = 16
DEFAULT_MAX_ITEMS = 10_000
DEFAULT_MAX_STRING_LENGTH = 16_384


def freeze_json_mapping(
    value: Mapping[str, Any],
    *,
    field_name: str,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_items: int = DEFAULT_MAX_ITEMS,
    max_string_length: int = DEFAULT_MAX_STRING_LENGTH,
) -> Mapping[str, FrozenJsonValue]:
    """Validate, bound, copy, and recursively freeze a JSON-compatible mapping."""

    item_count = 0

    def freeze(item: Any, depth: int) -> FrozenJsonValue:
        nonlocal item_count
        if depth > max_depth:
            raise ValueError(f"{field_name} exceeds maximum nesting depth")
        if isinstance(item, str):
            if len(item) > max_string_length:
                raise ValueError(f"{field_name} contains an oversized string")
            return item
        if item is None or isinstance(item, (bool, int)):
            return item
        if isinstance(item, float):
            if not (-float("inf") < item < float("inf")):
                raise ValueError(f"{field_name} contains a non-finite number")
            return item
        if isinstance(item, Mapping):
            item_count += len(item)
            if item_count > max_items:
                raise ValueError(f"{field_name} contains too many items")
            frozen: dict[str, FrozenJsonValue] = {}
            for key, nested in item.items():
                if not isinstance(key, str):
                    raise ValueError(f"{field_name} keys must be strings")
                if len(key) > max_string_length:
                    raise ValueError(f"{field_name} contains an oversized string")
                frozen[key] = freeze(nested, depth + 1)
            return MappingProxyType(frozen)
        if isinstance(item, (list, tuple)):
            item_count += len(item)
            if item_count > max_items:
                raise ValueError(f"{field_name} contains too many items")
            return tuple(freeze(nested, depth + 1) for nested in item)
        raise ValueError(f"{field_name} must contain only JSON-compatible values")

    try:
        frozen = freeze(value, 0)
    except RecursionError as exc:
        raise ValueError(f"{field_name} must contain only JSON-compatible values") from exc
    if not isinstance(frozen, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return frozen


def thaw_json_mapping(value: Mapping[str, FrozenJsonValue]) -> dict[str, JsonValue]:
    """Return a mutable JSON-compatible copy of a frozen mapping."""

    def thaw(item: FrozenJsonValue) -> JsonValue:
        if isinstance(item, Mapping):
            return {key: thaw(nested) for key, nested in item.items()}
        if isinstance(item, tuple):
            return [thaw(nested) for nested in item]
        return item

    return {key: thaw(item) for key, item in value.items()}
