"""Utility functions to apply Zendesk plans."""

from __future__ import annotations

import importlib
import logging
import os
from collections.abc import Iterable, Mapping, Sequence
from types import ModuleType
from typing import Any

from codex.zendesk.monitoring.zendesk_metrics import metrics as _metrics

LOGGER = logging.getLogger(__name__)

PlanOperations = Iterable[Mapping[str, Any]]

_API_OBJECTS_MODULE: ModuleType | None = None

_RESOURCE_ENDPOINTS: dict[str, tuple[str, str]] = {
    "triggers": ("triggers", "Trigger"),
    "fields": ("ticket_fields", "TicketField"),
    "forms": ("ticket_forms", "TicketForm"),
    "groups": ("groups", "Group"),
    "macros": ("macros", "Macro"),
    "views": ("views", "View"),
    "webhooks": ("webhooks", "Webhook"),
    "slas": ("sla_policies", "SLAPolicy"),
}

_RESOURCE_NAME_FIELDS: dict[str, tuple[str, ...]] = {
    "triggers": ("title", "name", "id"),
    "fields": ("title", "name", "id"),
    "forms": ("name", "title", "id"),
    "groups": ("name", "id"),
    "macros": ("title", "name", "id"),
    "views": ("title", "name", "id"),
    "webhooks": ("name", "id"),
    "slas": ("title", "name", "id"),
}


def _get_client(env: str):
    module_spec = importlib.util.find_spec("zenpy")
    if module_spec is None:
        LOGGER.error("Zenpy package is not installed; cannot apply changes.")
        return None
    zenpy_module = importlib.import_module("zenpy")
    zenpy_client = getattr(zenpy_module, "Zenpy", None)
    if zenpy_client is None:
        LOGGER.error("Zenpy client class is unavailable; cannot apply changes.")
        return None

    prefix = f"ZENDESK_{env.upper()}_"
    subdomain = os.getenv(f"{prefix}SUBDOMAIN")
    email = os.getenv(f"{prefix}EMAIL")
    token = os.getenv(f"{prefix}TOKEN")
    if not subdomain or not email or not token:
        LOGGER.error("Missing Zendesk credentials for environment '%s'.", env)
        return None

    return zenpy_client(subdomain=subdomain, email=email, token=token)


def _load_api_objects_module() -> ModuleType | None:
    global _API_OBJECTS_MODULE
    if _API_OBJECTS_MODULE is None:
        module_spec = importlib.util.find_spec("zenpy.lib.api_objects")
        if module_spec is None:
            return None
        _API_OBJECTS_MODULE = importlib.import_module("zenpy.lib.api_objects")
    return _API_OBJECTS_MODULE


def _get_api_class(class_name: str):
    module = _load_api_objects_module()
    if module is None:
        return None
    return getattr(module, class_name, None)


def _list_existing(endpoint: Any) -> list[Any]:
    if endpoint is None:
        return []
    try:
        if callable(endpoint):
            result = endpoint()
        elif hasattr(endpoint, "list") and callable(endpoint.list):
            result = endpoint.list()
        else:
            return []
        if result is None:
            return []
        if isinstance(result, list):
            return result
        return list(result)
    except Exception as exc:  # pragma: no cover - network interactions mocked in tests
        LOGGER.debug("Unable to enumerate existing resources: %s", exc)
        return []


def _operation_name(resource: str, entry: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    name = entry.get("name")
    if isinstance(name, str) and name:
        return name
    for field in _RESOURCE_NAME_FIELDS.get(resource, ("name", "title", "id")):
        value = data.get(field)
        if isinstance(value, str) and value:
            return value
        if value is not None:
            return str(value)
    path = entry.get("path")
    if isinstance(path, str) and path:
        segment = path.rstrip("/").split("/")[-1]
        if segment:
            return segment
    return ""


def _find_existing(existing: list[Any], resource: str, name: str):
    if not name:
        return None
    for item in existing:
        for field in _RESOURCE_NAME_FIELDS.get(resource, ("name", "title", "id")):
            value = getattr(item, field, None)
            if value is None:
                continue
            if str(value) == name:
                return item
    return None


def _apply_patch_set(target: Any, patches: Sequence[Mapping[str, Any]]) -> None:
    for patch in patches:
        path = patch.get("path")
        if not isinstance(path, str):
            continue
        attr = path.lstrip("/").split("/", 1)[0]
        if not attr:
            continue
        if "value" in patch:
            setattr(target, attr, patch.get("value"))


def _apply_named_resource(
    resource: str,
    plan_data: Any,
    env: str,
    dry_run: bool,
) -> None:
    endpoint_attr, class_name = _RESOURCE_ENDPOINTS[resource]
    operations = _extract_operations(plan_data, resource)
    _log_pending(resource, operations, env)
    if not operations:
        return
    if dry_run:
        LOGGER.info("Dry-run enabled; skipping apply for resource '%s'.", resource)
        return

    client = _get_client(env)
    if client is None:
        return
    endpoint = getattr(client, endpoint_attr, None)
    if endpoint is None:
        LOGGER.error(
            "Zendesk client does not expose endpoint '%s' for resource '%s'.",
            endpoint_attr,
            resource,
        )
        return

    api_class = _get_api_class(class_name)
    if api_class is None:
        LOGGER.error("Zenpy API object '%s' not found; cannot apply %s.", class_name, resource)
        return

    existing_items = _list_existing(endpoint)
    create_fn = getattr(endpoint, "create", None)
    update_fn = getattr(endpoint, "update", None)
    delete_fn = getattr(endpoint, "delete", None)

    for entry in operations:
        action = entry.get("action") or entry.get("op")
        payload = entry.get("data") or entry.get("value") or {}
        if hasattr(payload, "model_dump"):
            payload = payload.model_dump()
        if not isinstance(payload, Mapping):
            payload = {}
        name = _operation_name(resource, entry, payload)

        if action in {"add", "create"}:
            if not callable(create_fn):
                LOGGER.error("Create operation not supported for resource '%s'.", resource)
                continue
            instance = api_class(**payload)
            create_fn(instance)
        elif action in {"remove", "delete"}:
            if not callable(delete_fn):
                LOGGER.error("Delete operation not supported for resource '%s'.", resource)
                continue
            target = _find_existing(existing_items, resource, name)
            if target is None:
                LOGGER.warning("Resource '%s' named '%s' not found for deletion.", resource, name)
                continue
            delete_fn(target)
        elif action in {"patch", "update"}:
            if not callable(update_fn):
                LOGGER.error("Update operation not supported for resource '%s'.", resource)
                continue
            target = _find_existing(existing_items, resource, name)
            if target is None:
                LOGGER.warning("Resource '%s' named '%s' not found for update.", resource, name)
                continue
            changes = entry.get("changes") or entry.get("patches") or []
            if isinstance(changes, Sequence):
                _apply_patch_set(target, changes)
            update_fn(target)


def _extract_operations(plan_data: Any, resource: str) -> list[Mapping[str, Any]]:
    """Normalize various plan payload structures into a list of operations."""

    candidate: Any
    if isinstance(plan_data, Mapping):
        if resource in plan_data:
            candidate = plan_data[resource]
        elif "operations" in plan_data:
            candidate = plan_data["operations"]
        else:
            candidate = [plan_data]
    else:
        candidate = plan_data

    if isinstance(candidate, str | bytes | bytearray):
        raise ValueError(
            f"Plan for {resource} must be a sequence of operation mappings, not a scalar."
        )
    if not isinstance(candidate, Sequence):
        raise ValueError(f"Plan for {resource} must be a sequence of operation mappings.")

    operations: list[Mapping[str, Any]] = []
    for index, entry in enumerate(candidate):
        if not isinstance(entry, Mapping):
            entry_type = type(entry).__name__
            raise ValueError(
                f"Plan for {resource} must contain mapping entries; item {index} is "
                f"{entry_type}."
            )
        entry_resource = entry.get("resource")
        if entry_resource is not None and entry_resource != resource:
            continue
        operations.append(entry)
    return operations


def _log_pending(resource: str, operations: PlanOperations, env: str) -> None:
    ops = list(operations)
    LOGGER.info(
        "Prepared %s operation(s) for %s in environment '%s'.",
        len(ops),
        resource,
        env,
    )
    if not ops:
        LOGGER.info("No changes required for resource '%s'.", resource)
    try:
        _metrics.emit_counter("zendesk_diff_operations", len(ops))
    except Exception:  # pragma: no cover - metrics are best effort in offline runs
        LOGGER.debug("Skipping metrics emission for resource '%s'.", resource)

    try:
        metric = _metrics.get("zendesk_diff_operations")
        if metric is not None and hasattr(metric, "observe"):
            metric.observe(float(len(ops)))
    except Exception:  # pragma: no cover - metrics are best-effort offline
        LOGGER.debug("Metrics emit skipped for resource '%s'.", resource)


def apply_triggers(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply trigger operations to the given Zendesk environment."""

    _apply_named_resource("triggers", plan_data, env, dry_run)


def apply_fields(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply ticket field operations to the given Zendesk environment."""

    _apply_named_resource("fields", plan_data, env, dry_run)


def apply_forms(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply ticket form operations to the given Zendesk environment."""

    _apply_named_resource("forms", plan_data, env, dry_run)


def apply_groups(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply group operations to the given Zendesk environment."""

    _apply_named_resource("groups", plan_data, env, dry_run)


def apply_macros(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply macro operations to the given Zendesk environment."""

    _apply_named_resource("macros", plan_data, env, dry_run)


def apply_views(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply view operations to the given Zendesk environment."""

    _apply_named_resource("views", plan_data, env, dry_run)


def apply_webhooks(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply webhook operations to the given Zendesk environment."""

    _apply_named_resource("webhooks", plan_data, env, dry_run)


def apply_apps(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply app operations to the given Zendesk environment."""

    operations = _extract_operations(plan_data, "apps")
    _log_pending("apps", operations, env)
    if dry_run:
        LOGGER.info("Dry-run enabled; skipping apply for resource 'apps'.")
        return
    LOGGER.info("App apply logic is not yet implemented; operations logged only.")


def apply_guide(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply guide (themes/templates) operations to the given Zendesk environment."""

    operations = _extract_operations(plan_data, "guide")
    _log_pending("guide", operations, env)
    if dry_run:
        LOGGER.info("Dry-run enabled; skipping apply for resource 'guide'.")
        return
    LOGGER.info("Guide apply logic is not yet implemented; operations logged only.")


def apply_talk(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply Talk (IVR, greetings, number bindings) operations to the given environment."""

    operations = _extract_operations(plan_data, "talk")
    _log_pending("talk", operations, env)
    if dry_run:
        LOGGER.info("Dry-run enabled; skipping apply for resource 'talk'.")
        return
    LOGGER.info("Talk apply logic is not yet implemented; operations logged only.")


def apply_routing(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply skills-based routing operations to the given environment."""

    operations = _extract_operations(plan_data, "routing")
    _log_pending("routing", operations, env)
    if dry_run:
        LOGGER.info("Dry-run enabled; skipping apply for resource 'routing'.")
        return
    LOGGER.info("Routing apply logic is not yet implemented; operations logged only.")


def apply_widgets(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply web widget operations to the given Zendesk environment."""

    operations = _extract_operations(plan_data, "widgets")
    _log_pending("widgets", operations, env)
    if dry_run:
        LOGGER.info("Dry-run enabled; skipping apply for resource 'widgets'.")
        return
    LOGGER.info("Widget apply logic is not yet implemented; operations logged only.")


def apply_slas(plan_data: Any, env: str, dry_run: bool = False) -> None:
    """Apply SLA policy operations to the given Zendesk environment."""

    _apply_named_resource("slas", plan_data, env, dry_run)


__all__ = [
    "apply_apps",
    "apply_fields",
    "apply_forms",
    "apply_groups",
    "apply_guide",
    "apply_macros",
    "apply_slas",
    "apply_routing",
    "apply_talk",
    "apply_triggers",
    "apply_views",
    "apply_webhooks",
    "apply_widgets",
]
