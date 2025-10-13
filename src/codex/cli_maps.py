"""Typer CLI to inspect mapping CSVs using typed loaders."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from codex.mapping.load import load_all_mappings

MAPPINGS_DIR_ARGUMENT = typer.Argument(Path("config/mapping"))

app = typer.Typer(help="Inspect and validate Codex mapping tables.")


@app.command("inspect")
def inspect(mappings_dir: Path = MAPPINGS_DIR_ARGUMENT) -> None:
    """Emit JSON describing the validated mapping tables."""

    payload = load_all_mappings(mappings_dir)
    typer.echo(json.dumps(payload, indent=2))
