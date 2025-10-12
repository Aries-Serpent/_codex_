"""Diff helpers for Zendesk administrative resources."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypeVar

from pydantic import BaseModel

from codex.zendesk.model import Group, TicketField, TicketForm, Trigger

ModelT = TypeVar("ModelT", bound=BaseModel)
ModelInput = ModelT | Mapping[str, Any]


def diff_triggers(
    desired: Iterable[ModelInput],
    actual: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    """Compute JSON patches describing trigger differences."""

    return _diff_named_resources(desired, actual, Trigger, base_path="/triggers")


def diff_fields(
    desired_fields: Iterable[ModelInput],
    actual_fields: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    return _diff_named_resources(desired_fields, actual_fields, TicketField, base_path="/fields")


def diff_forms(
    desired_forms: Iterable[ModelInput],
    actual_forms: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    return _diff_named_resources(desired_forms, actual_forms, TicketForm, base_path="/forms")


def diff_groups(
    desired_groups: Iterable[ModelInput],
    actual_groups: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    return _diff_named_resources(desired_groups, actual_groups, Group, base_path="/groups")


def _diff_named_resources(
    desired: Iterable[ModelInput],
    actual: Iterable[ModelInput],
    model_cls: type[ModelT],
    *,
    base_path: str,
) -> list[dict[str, Any]]:
    desired_models = _coerce_models(desired, model_cls)
    actual_models = _coerce_models(actual, model_cls)
    diffs: list[dict[str, Any]] = []

    desired_map = {item.name: item for item in desired_models}
    actual_map = {item.name: item for item in actual_models}

    for name, desired_item in desired_map.items():
        current_item = actual_map.get(name)
        if current_item is None:
            diffs.append(
                {
                    "op": "add",
                    "path": f"{base_path}/{_escape_json_pointer_token(name)}",
                    "value": _dump_model(desired_item),
                }
            )
            continue
        patches = _call_diff(desired_item, current_item)
        if patches:
            diffs.append(
                {
                    "op": "patch",
                    "name": name,
                    "patches": patches,
                }
            )

    for name in sorted(actual_map.keys() - desired_map.keys()):
        diffs.append(
            {
                "op": "remove",
                "path": f"{base_path}/{_escape_json_pointer_token(name)}",
            }
        )

    return diffs


def _coerce_models(
    values: Iterable[ModelInput] | None,
    model_cls: type[ModelT],
) -> list[ModelT]:
    if values is None:
        return []
    models: list[ModelT] = []
    for value in values:
        if isinstance(value, model_cls):
            models.append(value)
        elif isinstance(value, BaseModel):
            models.append(model_cls.model_validate(value.model_dump()))
        else:
            if not isinstance(value, Mapping):
                expected = model_cls.__name__
                raise TypeError(
                    f"Expected mapping or {expected} instance, received {type(value)!r}"
                )
            models.append(model_cls.model_validate(value))
    return models


def _dump_model(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", exclude_none=True)


def _call_diff(new_item: ModelT, old_item: ModelT) -> list[dict[str, Any]]:
    diff_method = getattr(new_item, "diff", None)
    if callable(diff_method):
        return diff_method(old_item)
    return []


def _escape_json_pointer_token(value: str) -> str:
    """Escape `/` and `~` in JSON Pointer token names per RFC 6901."""

    return value.replace("~", "~0").replace("/", "~1")


__all__ = [
    "diff_fields",
    "diff_forms",
    "diff_groups",
    "diff_triggers",
]
