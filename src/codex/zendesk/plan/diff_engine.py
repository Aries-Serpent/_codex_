"""Diff helpers for Zendesk administrative resources."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypeVar

from pydantic import BaseModel

from codex.zendesk.model import (
    App,
    Group,
    GuideThemeRef,
    Macro,
    TemplatePatch,
    TicketField,
    TicketForm,
    Trigger,
    View,
    Webhook,
)

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


def diff_macros(
    desired_macros: Iterable[ModelInput],
    actual_macros: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    return _diff_named_resources(desired_macros, actual_macros, Macro, base_path="/macros")


def diff_views(
    desired_views: Iterable[ModelInput],
    actual_views: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    return _diff_named_resources(desired_views, actual_views, View, base_path="/views")


def diff_webhooks(
    desired_webhooks: Iterable[ModelInput],
    actual_webhooks: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    return _diff_named_resources(desired_webhooks, actual_webhooks, Webhook, base_path="/webhooks")


def diff_apps(
    desired_apps: Iterable[ModelInput],
    actual_apps: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    return _diff_named_resources(desired_apps, actual_apps, App, base_path="/apps")


def diff_guide(
    desired_refs: Iterable[ModelInput],
    actual_refs: Iterable[ModelInput],
    desired_templates: Iterable[ModelInput],
    actual_templates: Iterable[ModelInput],
) -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []
    diffs.extend(
        _diff_named_resources(desired_refs, actual_refs, GuideThemeRef, base_path="/guide/themes")
    )
    diffs.extend(
        _diff_named_resources(
            desired_templates,
            actual_templates,
            TemplatePatch,
            base_path="/guide/templates",
            key_attr="path",
        )
    )
    return diffs


def _diff_named_resources(
    desired: Iterable[ModelInput],
    actual: Iterable[ModelInput],
    model_cls: type[ModelT],
    *,
    base_path: str,
    key_attr: str = "name",
) -> list[dict[str, Any]]:
    desired_models = _coerce_models(desired, model_cls)
    actual_models = _coerce_models(actual, model_cls)
    diffs: list[dict[str, Any]] = []

    desired_map = {getattr(item, key_attr): item for item in desired_models}
    actual_map = {getattr(item, key_attr): item for item in actual_models}

    for key, desired_item in desired_map.items():
        current_item = actual_map.get(key)
        key_str = str(key)
        if current_item is None:
            diffs.append(
                {
                    "op": "add",
                    "path": f"{base_path}/{_escape_json_pointer_token(key_str)}",
                    "value": _dump_model(desired_item),
                }
            )
            continue
        patches = _call_diff(desired_item, current_item)
        if patches:
            diffs.append(
                {
                    "op": "patch",
                    "name": key_str,
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


def _escape_json_pointer(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


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
    "diff_apps",
    "diff_fields",
    "diff_forms",
    "diff_guide",
    "diff_groups",
    "diff_macros",
    "diff_triggers",
    "diff_views",
    "diff_webhooks",
]
