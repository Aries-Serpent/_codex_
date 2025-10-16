"""Typer application for Dynamics 365 admin scaffolds."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated

import typer
from codex.dynamics.apply_logging import apply_routing_stub, apply_slas_stub
from codex.dynamics.solution_xml import emit_solution_xml, load_solution_manifest

SNAPSHOT_OUTPUT_ARGUMENT = typer.Argument(..., help="Output path for snapshot JSON")
PLAN_FILE_ARGUMENT = typer.Argument(..., help="Plan JSON file")
DEFAULT_SOLUTION_XML = Path("artifacts/Solution.xml")
DEFAULT_CONFIG_DIR = Path("config/d365")
EMIT_OUT_OPTION = typer.Option(DEFAULT_SOLUTION_XML, "--out", help="Output file")
EMIT_NAME_OPTION = typer.Option(None, "--name", help="Override solution unique name")
EMIT_VERSION_OPTION = typer.Option(None, "--version", help="Override solution version")
EMIT_CONFIG_DIR_OPTION = typer.Option(DEFAULT_CONFIG_DIR, "--config-dir", help="Config directory")

app = typer.Typer(help="Dynamics 365 admin utilities (offline-first).")


@app.command("env-check")
def env_check() -> None:
    """Validate presence of expected Dynamics environment variables."""

    required = ["D365_URL", "D365_TENANT_ID", "D365_CLIENT_ID", "D365_CLIENT_SECRET"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        typer.echo(json.dumps({"ok": False, "missing": missing}, indent=2))
        raise SystemExit(2)
    typer.echo(json.dumps({"ok": True}, indent=2))


@app.command("snapshot")
def snapshot(output: Annotated[Path, SNAPSHOT_OUTPUT_ARGUMENT]) -> None:
    """Export local Config-as-Data artifacts for D365."""

    base = Path("config/d365")
    data: dict[str, str] = {}
    for name in ("tables.csv", "columns.csv", "slas.csv", "routing.csv", "solution_manifest.json"):
        path = base / name
        if path.exists():
            data[name] = path.read_text(encoding="utf-8")
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    typer.echo(output.as_posix())


@app.command("apply")
def apply(
    plan_file: Annotated[Path, PLAN_FILE_ARGUMENT],
    dry_run: Annotated[
        bool,
        typer.Option(
            True,
            "--dry-run/--no-dry-run",
            help="Simulate apply; --no-dry-run would perform outbound calls when implemented.",
        ),
    ] = True,
) -> None:
    """Print plan operations for review and emit routing/SLA evidence."""

    plan_payload = json.loads(plan_file.read_text(encoding="utf-8"))
    operations = plan_payload.get("operations") if isinstance(plan_payload, dict) else None
    if operations is None and isinstance(plan_payload, list):
        operations = plan_payload
    if operations is None:
        operations = []

    routing_ops = [entry for entry in operations if entry.get("resource") == "routing"]
    sla_ops = [entry for entry in operations if entry.get("resource") == "sla"]

    summaries: dict[str, dict[str, object]] = {}
    if routing_ops:
        summaries["routing"] = apply_routing_stub({"operations": routing_ops}, dry_run=dry_run)
    if sla_ops:
        summaries["sla"] = apply_slas_stub({"operations": sla_ops}, dry_run=dry_run)

    typer.echo(
        json.dumps(
            {
                "dry_run": dry_run,
                "ops": operations,
                "summaries": summaries,
            },
            indent=2,
        )
    )


@app.command("apply-routing")
def apply_routing(
    plan_file: Annotated[Path, PLAN_FILE_ARGUMENT],
    dry_run: Annotated[
        bool,
        typer.Option(
            True,
            "--dry-run/--no-dry-run",
            help=(
                "Simulate routing apply; --no-dry-run would perform outbound "
                "calls when implemented."
            ),
        ),
    ] = True,
) -> None:
    """Apply routing operations (stub) and emit evidence."""

    plan_payload = json.loads(plan_file.read_text(encoding="utf-8"))
    summary = apply_routing_stub(plan_payload, dry_run=dry_run)
    typer.echo(json.dumps(summary, indent=2))


@app.command("apply-slas")
def apply_slas(
    plan_file: Annotated[Path, PLAN_FILE_ARGUMENT],
    dry_run: Annotated[
        bool,
        typer.Option(
            True,
            "--dry-run/--no-dry-run",
            help=(
                "Simulate SLA apply; --no-dry-run would perform outbound calls " "when implemented."
            ),
        ),
    ] = True,
) -> None:
    """Apply SLA operations (stub) and emit evidence."""

    plan_payload = json.loads(plan_file.read_text(encoding="utf-8"))
    summary = apply_slas_stub(plan_payload, dry_run=dry_run)
    typer.echo(json.dumps(summary, indent=2))


@app.command("emit-solution-xml")
def emit_solution_xml_command(
    out: Annotated[Path, EMIT_OUT_OPTION] = DEFAULT_SOLUTION_XML,
    name: Annotated[str | None, EMIT_NAME_OPTION] = None,
    version: Annotated[str | None, EMIT_VERSION_OPTION] = None,
    config_dir: Annotated[Path, EMIT_CONFIG_DIR_OPTION] = DEFAULT_CONFIG_DIR,
) -> None:
    """Emit the unmanaged Solution XML using config-as-data."""

    manifest = load_solution_manifest(config_dir)
    manifest = manifest.with_overrides(name=name, version=version)
    xml = emit_solution_xml(manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml, encoding="utf-8")
    typer.echo(out.as_posix())
