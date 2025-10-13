"""Offline apply stubs that emit append-only evidence JSONL."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from codex.evidence import append_evidence, utc_now

__all__ = ["apply_routing_stub", "apply_slas_stub"]


def _normalize_operations(plan: Any) -> list[dict[str, Any]]:
    if isinstance(plan, dict):
        ops = plan.get("operations", [])
        return ops if isinstance(ops, list) else []
    if isinstance(plan, list):
        return plan
    return []


def _operation_action(value: str | None) -> str:
    mapping = {
        "add": "Create",
        "create": "Create",
        "update": "Update",
        "patch": "Update",
        "remove": "Delete",
        "delete": "Delete",
    }
    if value is None:
        return "Unknown"
    return mapping.get(value.lower(), "Unknown")


def _append_record(filename: str, record: dict[str, Any]) -> None:
    append_evidence(
        filename,
        {
            "ts": utc_now(),
            **record,
        },
    )


def apply_slas_stub(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort SLA apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "sla",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_slas.jsonl",
            {
                "resource": "sla",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "sla",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def apply_routing_stub(plan: Any, dry_run: bool = True) -> dict[str, Any]:
    """Best-effort routing apply that records evidence locally."""

    operations = _normalize_operations(plan)
    summary = {
        "resource": "routingrule",
        "processed": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "dry_run": dry_run,
    }
    for entry in operations:
        action = _operation_action(entry.get("action") or entry.get("op"))
        data = entry.get("data") or entry.get("value") or {}
        target_name = entry.get("name") or _extract_target_name(entry)
        _append_record(
            "d365_routing.jsonl",
            {
                "resource": "routingrule",
                "action": action,
                "target": {
                    "name": target_name,
                    "logical_entity": "routingrule",
                },
                "dry_run": dry_run,
                "data": data,
            },
        )
        summary["processed"] += 1
        if action == "Create":
            summary["created"] += 1
        elif action == "Update":
            summary["updated"] += 1
        elif action == "Delete":
            summary["deleted"] += 1
    return summary


def _extract_target_name(entry: Mapping[str, Any]) -> str:
    path = entry.get("path") if isinstance(entry, Mapping) else None
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""
