"""Typer application for Zendesk configuration workflows."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

import typer
from codex.zendesk.model import Group, TicketField, TicketForm, Trigger
from codex.zendesk.monitoring import register_zendesk_metrics
from codex.zendesk.plan.diff_engine import diff_fields, diff_forms, diff_groups, diff_triggers

app = typer.Typer(help="Manage Zendesk admin resources with Codex.")


ResourceConfig = tuple[
    type[BaseModel], Callable[[Iterable[object], Iterable[object]], list[dict[str, Any]]]
]
_RESOURCE_CONFIG: dict[str, ResourceConfig] = {
    "triggers": (Trigger, diff_triggers),
    "fields": (TicketField, diff_fields),
    "forms": (TicketForm, diff_forms),
    "groups": (Group, diff_groups),
}


RESOURCE_ARGUMENT = typer.Argument(..., help=f"Resource type ({', '.join(_RESOURCE_CONFIG)})")
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


@app.command()
def snapshot(env: str = ENVIRONMENT_OPTION) -> None:
    """Placeholder command that will eventually export the active configuration."""

    typer.echo(f"Snapshotting Zendesk configuration for '{env}' is not yet implemented.")


@app.command()
def diff(
    resource: str = RESOURCE_ARGUMENT,
    desired_file: Path = DESIRED_FILE_OPTION,
    current_file: Path = CURRENT_FILE_OPTION,
    output: Path | None = DIFF_OUTPUT_OPTION,
) -> None:
    """Compute differences between desired and observed Zendesk resources."""

    model_cls, diff_fn = _resolve_resource(resource)
    desired_models = _load_models(desired_file, resource, model_cls)
    current_models = _load_models(current_file, resource, model_cls)
    diffs = diff_fn(desired_models, current_models)

    diff_payload = json.dumps(diffs, indent=2, sort_keys=True)
    if output is not None:
        output.write_text(diff_payload, encoding="utf-8")
        typer.echo(f"Diff written to {output}")
    else:
        typer.echo(diff_payload)


@app.command()
def plan(
    diff_file: Path = PLAN_DIFF_ARGUMENT,
    output: Path | None = PLAN_OUTPUT_OPTION,
) -> None:
    """Emit a plan from a previously generated diff."""

    payload = diff_file.read_text(encoding="utf-8")
    if output is not None:
        output.write_text(payload, encoding="utf-8")
        typer.echo(f"Plan written to {output}")
    else:
        typer.echo(payload)


@app.command()
def apply(
    plan_file: Path = PLAN_FILE_ARGUMENT,
    env: str = ENVIRONMENT_OPTION,
) -> None:
    """Placeholder for applying plans to Zendesk."""

    typer.echo(f"Apply is not yet implemented. Would apply {plan_file} to environment '{env}'.")


@app.command()
def metrics() -> None:
    """Register Zendesk metrics and list their identifiers."""

    registered = register_zendesk_metrics()
    typer.echo("Registered metrics:\n" + "\n".join(f"- {name}" for name in registered))


def _resolve_resource(resource: str) -> ResourceConfig:
    try:
        return _RESOURCE_CONFIG[resource]
    except KeyError as exc:  # pragma: no cover - CLI validation
        valid = ", ".join(sorted(_RESOURCE_CONFIG))
        raise typer.BadParameter(
            f"Unsupported resource '{resource}'. Valid options: {valid}."
        ) from exc


def _load_models(path: Path, resource: str, model_cls: type[BaseModel]) -> list[BaseModel]:
    payload = _read_structured_file(path)
    if isinstance(payload, Mapping) and resource in payload:
        payload = payload[resource]
    if not isinstance(payload, Sequence):
        raise typer.BadParameter(
            f"Expected a list of {resource} definitions in {path}.",
        )
    models: list[BaseModel] = []
    for item in payload:
        try:
            if isinstance(item, model_cls):
                models.append(item)
            else:
                models.append(model_cls.model_validate(item))
        except ValidationError as exc:
            raise typer.BadParameter(f"Invalid {resource} entry in {path}: {exc}") from exc
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


__all__ = ["app"]
