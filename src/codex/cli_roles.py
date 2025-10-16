"""Typer CLI to export cross-platform role matrices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from codex.dynamics.model.role import DynamicsRole
from codex.dynamics.role_matrix import build_role_matrix
from codex.zendesk.model.role import Role as ZendeskRole

app = typer.Typer(help="Role matrix and permission harmonization.")


def _load_jsonl_or_json(path: Path):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


InputArg = Annotated[Path, typer.Argument(..., exists=True, readable=True)]
OutputArg = Annotated[Path, typer.Argument(...)]


@app.command("export-matrix")
def export_matrix(
    zendesk_roles_file: InputArg,
    dynamics_roles_file: InputArg,
    output_json: OutputArg,
) -> None:
    zendesk_raw = _load_jsonl_or_json(zendesk_roles_file)
    dynamics_raw = _load_jsonl_or_json(dynamics_roles_file)

    zendesk_roles = [ZendeskRole.model_validate(item) for item in zendesk_raw]
    dynamics_roles = [DynamicsRole.model_validate(item) for item in dynamics_raw]

    matrix = build_role_matrix(zendesk_roles, dynamics_roles)
    output_json.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    typer.echo(output_json.as_posix())
