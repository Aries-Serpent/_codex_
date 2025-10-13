"""Typer application for Dynamics 365 admin scaffolds."""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer

SNAPSHOT_OUTPUT_ARGUMENT = typer.Argument(..., help="Output path for snapshot JSON")
PLAN_FILE_ARGUMENT = typer.Argument(..., help="Plan JSON file")

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
def snapshot(output: Path = SNAPSHOT_OUTPUT_ARGUMENT) -> None:
    """Export local Config-as-Data artifacts for D365."""

    base = Path("config/d365")
    data: dict[str, str] = {}
    for name in ("tables.csv", "columns.csv", "slas.csv", "routing.csv"):
        path = base / name
        if path.exists():
            data[name] = path.read_text(encoding="utf-8")
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    typer.echo(output.as_posix())


@app.command("apply")
def apply(
    plan_file: Path = PLAN_FILE_ARGUMENT,
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--no-dry-run",
        help="Simulate apply; --no-dry-run would perform outbound calls when implemented.",
    ),
) -> None:
    """Print plan operations for review (dry-run scaffold)."""

    plan_payload = json.loads(plan_file.read_text(encoding="utf-8"))
    operations = plan_payload.get("operations") if isinstance(plan_payload, dict) else None
    if operations is None and isinstance(plan_payload, list):
        operations = plan_payload
    if operations is None:
        operations = []
    typer.echo(json.dumps({"dry_run": dry_run, "ops": operations}, indent=2))
