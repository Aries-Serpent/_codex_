"""Typer application for Zendesk configuration workflows."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

import typer
from codex.versioning import update_artifact_version
from codex.zendesk import apply as apply_module
from codex.zendesk.model import (
    App,
    Group,
    GuideThemeRef,
    Macro,
    RoutingRule,
    SLAPolicy,
    TemplatePatch,
    TicketField,
    TicketForm,
    Trigger,
    View,
    Webhook,
)
from codex.zendesk.monitoring import register_zendesk_metrics
from codex.zendesk.plan.diff_engine import (
    diff_apps,
    diff_fields,
    diff_forms,
    diff_groups,
    diff_guide,
    diff_macros,
    diff_routing,
    diff_slas,
    diff_triggers,
    diff_views,
    diff_webhooks,
)
from codex.zendesk.plan.validators import validate_plan

app = typer.Typer(help="Manage Zendesk admin resources with Codex.")


ResourceConfig = tuple[
    type[BaseModel], Callable[[Iterable[object], Iterable[object]], list[dict[str, Any]]]
]
_RESOURCE_CONFIG: dict[str, ResourceConfig] = {
    "triggers": (Trigger, diff_triggers),
    "fields": (TicketField, diff_fields),
    "forms": (TicketForm, diff_forms),
    "groups": (Group, diff_groups),
    "macros": (Macro, diff_macros),
    "views": (View, diff_views),
    "webhooks": (Webhook, diff_webhooks),
    "apps": (App, diff_apps),
    "routing": (RoutingRule, diff_routing),
    "slas": (SLAPolicy, diff_slas),
}
RESOURCE_TYPES = (
    "apps",
    "fields",
    "forms",
    "groups",
    "guide",
    "macros",
    "routing",
    "slas",
    "talk",
    "triggers",
    "views",
    "webhooks",
    "widgets",
)
APPLY_RESOURCE_HELP = "Resource type of the plan (" + ", ".join(RESOURCE_TYPES) + ")"
SUPPORTED_RESOURCES = tuple(sorted((*_RESOURCE_CONFIG.keys(), "guide")))

_APPLY_HANDLERS: dict[str, Callable[[Any, str, bool], None]] = {
    "apps": apply_module.apply_apps,
    "fields": apply_module.apply_fields,
    "forms": apply_module.apply_forms,
    "groups": apply_module.apply_groups,
    "guide": apply_module.apply_guide,
    "macros": apply_module.apply_macros,
    "routing": apply_module.apply_routing,
    "slas": apply_module.apply_slas,
    "talk": apply_module.apply_talk,
    "triggers": apply_module.apply_triggers,
    "views": apply_module.apply_views,
    "webhooks": apply_module.apply_webhooks,
    "widgets": apply_module.apply_widgets,
}


RESOURCE_ARGUMENT = typer.Argument(
    ...,
    help=f"Resource type ({', '.join(SUPPORTED_RESOURCES)})",
)
DESIRED_FILE_OPTION = typer.Option(
    ..., exists=True, readable=True, help="Desired state file (JSON or TOML)."
)
CURRENT_FILE_OPTION = typer.Option(
    ..., exists=True, readable=True, help="Observed state file (JSON or TOML)."
)
DIFF_OUTPUT_OPTION = typer.Option(None, help="Optional file path to store the diff JSON.")
PLAN_DIFF_ARGUMENT = typer.Argument(
    ..., exists=True, readable=True, help="Diff JSON produced by the diff command."
)
PLAN_OUTPUT_OPTION = typer.Option(None, help="Optional file path to store the plan JSON.")
PLAN_FILE_ARGUMENT = typer.Argument(..., exists=True, readable=True, help="Plan JSON to apply.")
ENVIRONMENT_OPTION = typer.Option(..., help="Zendesk environment identifier.")
SNAPSHOT_OUTPUT_OPTION = typer.Option(
    None, "--output", "-o", help="Output file path for snapshot JSON"
)


@app.command("env-check")
def env_check(env: str = ENVIRONMENT_OPTION) -> None:
    """Validate Zendesk credentials and required libraries for the environment."""

    prefix = f"ZENDESK_{env.upper()}_"
    missing = [key for key in ("SUBDOMAIN", "EMAIL", "TOKEN") if not os.getenv(f"{prefix}{key}")]
    if missing:
        typer.echo(
            f"Missing Zendesk credentials: {', '.join(missing)} for env '{env}'",
            err=True,
        )
        raise SystemExit(2)

    try:
        zenpy_spec = importlib.util.find_spec("zenpy")
    except Exception:  # pragma: no cover - defensive guard
        zenpy_spec = None
    if zenpy_spec is None:
        typer.echo("Zenpy is not installed. `pip install zenpy`", err=True)
        raise SystemExit(3)

    typer.echo("ok")


@app.command("deps-check")
def deps_check() -> None:
    """Report availability of optional dependencies (zenpy, torch)."""

    modules = []
    for name in ("zenpy", "torch"):
        available = importlib.util.find_spec(name) is not None
        modules.append({"module": name, "available": available})
    typer.echo(json.dumps(modules, indent=2))


@app.command("docs-sync")
def docs_sync(dry_run: bool = typer.Option(False, help="List URLs only, do not download")) -> None:
    """Fetch and snapshot Zendesk developer docs under docs/vendors/zendesk/YYYY-MM-DD/..."""

    script = Path(__file__).resolve().parents[2] / "scripts" / "zendesk_docs_fetch.py"
    cmd = [sys.executable, script.as_posix()]
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        typer.echo(result.stdout.rstrip())
    if result.stderr:
        typer.echo(result.stderr.rstrip(), err=True)
    raise SystemExit(result.returncode)


@app.command("docs-catalog")
def docs_catalog() -> None:
    """Regenerate Markdown catalog index from the docs manifest."""

    script = Path(__file__).resolve().parents[2] / "scripts" / "zendesk_docs_catalog.py"
    result = subprocess.run(
        [sys.executable, script.as_posix()],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        typer.echo(result.stdout.rstrip())
    if result.stderr:
        typer.echo(result.stderr.rstrip(), err=True)
    raise SystemExit(result.returncode)


@app.command()
def snapshot(
    env: str = ENVIRONMENT_OPTION,
    output: Path | None = SNAPSHOT_OUTPUT_OPTION,
) -> None:
    """Export the active Zendesk configuration for the given environment."""

    try:
        data = _export_zendesk_config(env)
    except Exception as exc:  # pragma: no cover - depends on Zenpy availability
        data = {
            "error": f"{exc}",
            "triggers": [],
            "fields": [],
            "forms": [],
            "groups": [],
            "macros": [],
            "views": [],
            "webhooks": [],
        }

    snapshot_json = json.dumps(data, indent=2)
    if output:
        output.write_text(snapshot_json, encoding="utf-8")
        typer.echo(f"Snapshot written to {output}")
    else:
        typer.echo(snapshot_json)


@app.command()
def diff(
    resource: str = RESOURCE_ARGUMENT,
    desired_file: Path = DESIRED_FILE_OPTION,
    current_file: Path = CURRENT_FILE_OPTION,
    output: Path | None = DIFF_OUTPUT_OPTION,
) -> None:
    """Compute differences between desired and observed Zendesk resources."""

    if resource == "guide":
        diffs = _diff_guide_resources(desired_file, current_file)
    else:
        model_cls, diff_fn = _resolve_resource(resource)
        desired_models = _load_models(desired_file, resource, model_cls)
        current_models = _load_models(current_file, resource, model_cls)
        diffs = diff_fn(desired_models, current_models)

    result = {resource: diffs}
    diff_text = json.dumps(result, indent=2, sort_keys=True)
    if output is not None:
        output.write_text(diff_text, encoding="utf-8")
        typer.echo(f"Diff written to {output}")
    else:
        adds = sum(1 for d in diffs if isinstance(d, Mapping) and d.get("op") == "add")
        updates = sum(
            1 for d in diffs if isinstance(d, Mapping) and d.get("op") in {"patch", "update"}
        )
        removes = sum(1 for d in diffs if isinstance(d, Mapping) and d.get("op") == "remove")
        typer.echo(
            f"{resource.capitalize()} diff: {adds} additions, {updates} changes, {removes} removals"
        )
        typer.echo(diff_text)


@app.command()
def plan(
    diff_file: Path = PLAN_DIFF_ARGUMENT,
    output: Path | None = PLAN_OUTPUT_OPTION,
) -> None:
    """Emit a plan from a previously generated diff."""

    diff_data = _read_structured_file(diff_file)

    plan_ops: list[dict[str, Any]] = []
    if isinstance(diff_data, Mapping):
        for resource_name, changes in diff_data.items():
            if not isinstance(changes, Sequence):
                continue
            for entry in changes:
                if not isinstance(entry, Mapping):
                    continue
                plan_ops.extend(_plan_operations_from_entry(resource_name, entry))
    elif isinstance(diff_data, Sequence):
        inferred_resource = _infer_resource_from_entries(diff_data)
        for entry in diff_data:
            if not isinstance(entry, Mapping):
                continue
            plan_ops.extend(_plan_operations_from_entry(inferred_resource, entry))

    plan_payload = {"operations": plan_ops}
    plan_json = json.dumps(plan_payload, indent=2)
    if output is not None:
        output.write_text(plan_json, encoding="utf-8")
        typer.echo(f"Plan written to {output}")
    else:
        typer.echo(plan_json)


@app.command()
def apply(
    resource: str = typer.Argument(..., help=APPLY_RESOURCE_HELP),
    plan_file: Path = PLAN_FILE_ARGUMENT,
    env: str = ENVIRONMENT_OPTION,
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate apply without making changes"),
) -> None:
    """Apply a previously generated plan for a specific Zendesk resource."""

    try:
        plan_payload = json.loads(plan_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Plan file '{plan_file}' is not valid JSON: {exc}") from exc

    candidate: Any = plan_payload
    if isinstance(plan_payload, Mapping):
        operations = plan_payload.get("operations")
        if operations is None:
            operations = plan_payload.get(resource, plan_payload)
        candidate = operations

    if isinstance(candidate, (str | bytes | bytearray)):
        raise typer.BadParameter(
            "Plan payload must be a sequence of operations, not a scalar value."
        )
    if not isinstance(candidate, Sequence):
        raise typer.BadParameter("Plan payload must be a sequence of operations.")
    operations_list = list(candidate)
    try:
        validate_plan({"resource": resource, "operations": operations_list})
    except ValidationError as exc:
        raise typer.BadParameter(f"Invalid plan for resource '{resource}': {exc}") from exc

    handlers = _APPLY_HANDLERS
    if resource not in handlers:
        valid = ", ".join(RESOURCE_TYPES)
        message = f"Unsupported resource '{resource}'. Valid options: {valid}."
        raise typer.BadParameter(message)

    try:
        handlers[resource](plan_payload, env, dry_run=dry_run)
        if not dry_run:
            update_artifact_version(f"zendesk/{resource}", operations_list)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ImportError as exc:
        if dry_run:
            typer.echo(f"SDK missing but continuing due to --dry-run: {exc}", err=True)
        else:
            raise

    typer.echo("ok")


def _plan_operations_from_entry(resource: str, entry: Mapping[str, Any]) -> list[dict[str, Any]]:
    op_type = entry.get("op") or entry.get("action")
    name = _extract_name(entry)
    operations: list[dict[str, Any]] = []
    if op_type in {"add", "create"}:
        value = entry.get("value") if "value" in entry else entry.get("data", {})
        if value is None:
            value = entry.get("data", {})
        operations.append(
            {
                "action": "create",
                "resource": resource,
                "name": name,
                "data": value,
            }
        )
    elif op_type in {"remove", "delete"}:
        operations.append(
            {
                "action": "delete",
                "resource": resource,
                "name": name,
            }
        )
    elif op_type in {"patch", "update"}:
        changes = entry.get("patches") if "patches" in entry else entry.get("changes", [])
        operations.append(
            {
                "action": "update",
                "resource": resource,
                "name": name,
                "changes": changes,
            }
        )
    return operations


def _extract_name(entry: Mapping[str, Any]) -> str:
    path = entry.get("path", "")
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    name = entry.get("name")
    if isinstance(name, str):
        return name
    return ""


def _infer_resource_from_entries(entries: Sequence[object]) -> str:
    for entry in entries:
        if isinstance(entry, Mapping):
            resource = entry.get("resource")
            if isinstance(resource, str) and resource:
                return resource
            path = entry.get("path")
            if isinstance(path, str) and path:
                stripped = path.lstrip("/")
                if stripped:
                    return stripped.split("/", 1)[0]
    return "resource"


@app.command()
def metrics() -> None:
    """Register Zendesk metrics and list their identifiers."""

    registered = register_zendesk_metrics()
    typer.echo("Registered metrics:\n" + "\n".join(f"- {name}" for name in registered))


def _resolve_resource(resource: str) -> ResourceConfig:
    try:
        return _RESOURCE_CONFIG[resource]
    except KeyError as exc:  # pragma: no cover - CLI validation
        valid = ", ".join(sorted(SUPPORTED_RESOURCES))
        raise typer.BadParameter(
            f"Unsupported resource '{resource}'. Valid options: {valid}."
        ) from exc


def _diff_guide_resources(desired_file: Path, current_file: Path) -> list[dict[str, Any]]:
    desired_payload = _read_structured_file(desired_file)
    current_payload = _read_structured_file(current_file)
    if not isinstance(desired_payload, Mapping) or not isinstance(current_payload, Mapping):
        raise typer.BadParameter(
            "Guide files must contain a mapping with 'themes' and 'templates' lists."
        )

    desired_themes = _coerce_model_sequence(
        desired_payload.get("themes"),
        "guide themes",
        GuideThemeRef,
        desired_file,
    )
    current_themes = _coerce_model_sequence(
        current_payload.get("themes"),
        "guide themes",
        GuideThemeRef,
        current_file,
    )
    desired_templates = _coerce_model_sequence(
        desired_payload.get("templates"),
        "guide templates",
        TemplatePatch,
        desired_file,
    )
    current_templates = _coerce_model_sequence(
        current_payload.get("templates"),
        "guide templates",
        TemplatePatch,
        current_file,
    )
    return diff_guide(desired_themes, current_themes, desired_templates, current_templates)


def _load_models(
    path: Path,
    resource: str,
    model_cls: type[BaseModel],
) -> list[BaseModel]:
    payload = _read_structured_file(path)
    if isinstance(payload, Mapping) and resource in payload:
        payload = payload[resource]
    return _coerce_model_sequence(payload, resource, model_cls, path)


def _coerce_model_sequence(
    payload: object,
    resource: str,
    model_cls: type[BaseModel],
    source: Path,
) -> list[BaseModel]:
    if payload is None:
        return []
    if not isinstance(payload, Sequence):
        raise typer.BadParameter(
            f"Expected a list of {resource} definitions in {source}.",
        )
    if isinstance(payload, (str, bytes, bytearray)):  # noqa: UP038
        raise typer.BadParameter(
            f"Expected a list of {resource} definitions in {source}.",
        )
    models: list[BaseModel] = []
    for item in payload:
        try:
            if isinstance(item, model_cls):
                models.append(item)
            else:
                models.append(model_cls.model_validate(item))
        except ValidationError as exc:
            raise typer.BadParameter(f"Invalid {resource} entry in {source}: {exc}") from exc
    return models


def _read_structured_file(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".toml", ".tml"}:
        try:
            import tomllib
        except ModuleNotFoundError as exc:  # pragma: no cover - Python <3.11 guard
            raise typer.BadParameter("TOML support requires Python 3.11 or newer.") from exc
        return tomllib.loads(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Failed to parse {path}: {exc}") from exc


def _get_zendesk_client(env: str):
    module_spec = importlib.util.find_spec("zenpy")
    if module_spec is None:
        raise RuntimeError("Zenpy is required to connect to Zendesk.")
    zenpy_module = importlib.import_module("zenpy")
    zenpy_client = getattr(zenpy_module, "Zenpy", None)
    if zenpy_client is None:
        raise RuntimeError("Zenpy client is unavailable.")

    prefix = f"ZENDESK_{env.upper()}_"
    subdomain = os.getenv(f"{prefix}SUBDOMAIN")
    email = os.getenv(f"{prefix}EMAIL")
    token = os.getenv(f"{prefix}TOKEN")
    if not subdomain or not email or not token:
        raise RuntimeError(f"Missing Zendesk credentials for environment '{env}'.")

    return zenpy_client(subdomain=subdomain, email=email, token=token)


def _collect_objects(client: object, attribute: str) -> list[Any]:
    collection = getattr(client, attribute, None)
    if collection is None:
        return []
    result = collection() if callable(collection) else collection
    if result is None:
        return []
    if isinstance(result, list):
        return result
    try:
        return list(result)
    except TypeError:
        return []


def _export_zendesk_config(env: str) -> dict[str, Any]:
    client = _get_zendesk_client(env)
    snapshot: dict[str, Any] = {}

    snapshot["triggers"] = [
        (
            trigger.to_dict()
            if hasattr(trigger, "to_dict")
            else {
                "name": getattr(trigger, "title", None)
                or getattr(trigger, "name", None)
                or getattr(trigger, "id", None),
                "active": getattr(trigger, "active", None),
                "category": getattr(trigger, "category", None),
                "conditions": getattr(trigger, "conditions", None),
                "actions": getattr(trigger, "actions", None),
                "position": getattr(trigger, "position", None),
            }
        )
        for trigger in _collect_objects(client, "triggers")
    ]

    snapshot["fields"] = [
        {
            "name": getattr(field, "title", None) or getattr(field, "id", None),
            "type": getattr(field, "type", None),
            "options": [
                getattr(opt, "value", opt)
                for opt in getattr(field, "custom_field_options", []) or []
            ],
            "active": getattr(field, "active", None),
            "description": getattr(field, "description", None),
        }
        for field in _collect_objects(client, "ticket_fields")
    ]

    snapshot["forms"] = [
        {
            "name": getattr(form, "name", None) or getattr(form, "id", None),
            "fields": list(getattr(form, "ticket_field_ids", []) or []),
            "active": getattr(form, "active", None),
        }
        for form in _collect_objects(client, "ticket_forms")
    ]

    snapshot["groups"] = [
        {
            "name": getattr(group, "name", None) or getattr(group, "id", None),
            "description": getattr(group, "description", None),
            "memberships": [],
        }
        for group in _collect_objects(client, "groups")
    ]

    snapshot["macros"] = [
        {
            "name": getattr(macro, "title", None)
            or getattr(macro, "name", None)
            or getattr(macro, "id", None),
            "actions": [
                {"field": getattr(action, "field", None), "value": getattr(action, "value", None)}
                for action in getattr(macro, "actions", []) or []
            ],
            "active": getattr(macro, "active", None),
        }
        for macro in _collect_objects(client, "macros")
    ]

    snapshot["views"] = [
        {
            "name": getattr(view, "title", None)
            or getattr(view, "name", None)
            or getattr(view, "id", None),
            "filters": getattr(view, "conditions", None) or {},
            "columns": list(getattr(view, "columns", []) or []),
            "sort": getattr(view, "execution", None) or {},
        }
        for view in _collect_objects(client, "views")
    ]

    snapshot["webhooks"] = [
        {
            "name": getattr(webhook, "name", None) or getattr(webhook, "id", None),
            "endpoint": getattr(webhook, "endpoint", None),
            "status": getattr(webhook, "status", None),
        }
        for webhook in _collect_objects(client, "webhooks")
    ]

    return snapshot


__all__ = ["app"]


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    app()
