"""
Diff engine for Zendesk resources.

This module provides helper functions that take desired and actual resources
and produce JSON Patch lists.  The diff functions delegate to the models'
``diff`` methods and add context such as resource identifiers.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from codex.zendesk.model import Group, TicketField, TicketForm, Trigger

ResourcePayload = dict[str, Any]


def _ensure_sequence(items: Iterable[Any]) -> list[Any]:
    if isinstance(items, list):
        return items
    return list(items)


def _coerce_triggers(triggers: Sequence[Any]) -> list[Trigger]:
    coerced: list[Trigger] = []
    for item in triggers:
        if isinstance(item, Trigger):
            coerced.append(item)
        else:
            coerced.append(Trigger.parse_obj(item))
    return coerced


def _coerce_ticket_fields(fields: Sequence[Any]) -> list[TicketField]:
    coerced: list[TicketField] = []
    for item in fields:
        if isinstance(item, TicketField):
            coerced.append(item)
        else:
            coerced.append(TicketField.parse_obj(item))
    return coerced


def _coerce_ticket_forms(forms: Sequence[Any]) -> list[TicketForm]:
    coerced: list[TicketForm] = []
    for item in forms:
        if isinstance(item, TicketForm):
            coerced.append(item)
        else:
            coerced.append(TicketForm.parse_obj(item))
    return coerced


def _coerce_groups(groups: Sequence[Any]) -> list[Group]:
    coerced: list[Group] = []
    for item in groups:
        if isinstance(item, Group):
            coerced.append(item)
        else:
            coerced.append(Group.parse_obj(item))
    return coerced


def diff_triggers(desired: Sequence[Any], actual: Sequence[Any]) -> list[ResourcePayload]:
    """Compute diffs for a list of triggers."""

    desired_models = _coerce_triggers(_ensure_sequence(desired))
    actual_models = _coerce_triggers(_ensure_sequence(actual))

    diffs: list[ResourcePayload] = []
    actual_map: dict[str, Trigger] = {trigger.name: trigger for trigger in actual_models}
    for trigger in desired_models:
        other = actual_map.get(trigger.name)
        if other is None:
            diffs.append(
                {
                    "op": "add",
                    "path": f"/triggers/{trigger.name}",
                    "value": trigger.dict(),
                }
            )
        else:
            patches = trigger.diff(other)
            if patches:
                diffs.append({"op": "patch", "name": trigger.name, "patches": patches})
    return diffs


def diff_fields(
    desired_fields: Sequence[Any], actual_fields: Sequence[Any]
) -> list[ResourcePayload]:
    desired_models = _coerce_ticket_fields(_ensure_sequence(desired_fields))
    actual_models = _coerce_ticket_fields(_ensure_sequence(actual_fields))

    diffs: list[ResourcePayload] = []
    actual_map: dict[str, TicketField] = {field.name: field for field in actual_models}
    for field in desired_models:
        other = actual_map.get(field.name)
        if other is None:
            diffs.append(
                {
                    "op": "add",
                    "path": f"/fields/{field.name}",
                    "value": field.dict(),
                }
            )
        else:
            patches = field.diff(other)
            if patches:
                diffs.append({"op": "patch", "name": field.name, "patches": patches})
    return diffs


def diff_forms(desired_forms: Sequence[Any], actual_forms: Sequence[Any]) -> list[ResourcePayload]:
    desired_models = _coerce_ticket_forms(_ensure_sequence(desired_forms))
    actual_models = _coerce_ticket_forms(_ensure_sequence(actual_forms))

    diffs: list[ResourcePayload] = []
    actual_map: dict[str, TicketForm] = {form.name: form for form in actual_models}
    for form in desired_models:
        other = actual_map.get(form.name)
        if other is None:
            diffs.append(
                {
                    "op": "add",
                    "path": f"/forms/{form.name}",
                    "value": form.dict(),
                }
            )
        else:
            patches = form.diff(other)
            if patches:
                diffs.append({"op": "patch", "name": form.name, "patches": patches})
    return diffs


def diff_groups(
    desired_groups: Sequence[Any], actual_groups: Sequence[Any]
) -> list[ResourcePayload]:
    desired_models = _coerce_groups(_ensure_sequence(desired_groups))
    actual_models = _coerce_groups(_ensure_sequence(actual_groups))

    diffs: list[ResourcePayload] = []
    actual_map: dict[str, Group] = {group.name: group for group in actual_models}
    for group in desired_models:
        other = actual_map.get(group.name)
        if other is None:
            diffs.append(
                {
                    "op": "add",
                    "path": f"/groups/{group.name}",
                    "value": group.dict(),
                }
            )
        else:
            patches = group.diff(other)
            if patches:
                diffs.append({"op": "patch", "name": group.name, "patches": patches})
    return diffs
