"""Typer CLI to export cross-platform role matrices."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from codex.dynamics.model.role import DynamicsRole
from codex.dynamics.role_matrix import build_role_matrix
from codex.zendesk.model.role import Role as ZendeskRole

app = typer.Typer(help="Role matrix and permission harmonization.")


def _load_jsonl_or_json(path: Path) -> list[object] | object:
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


@app.command("export-matrix")
def export_matrix(
    zendesk_roles_file: Path = typer.Argument(..., exists=True, readable=True),
    dynamics_roles_file: Path = typer.Argument(..., exists=True, readable=True),
    output_json: Path = typer.Argument(...),
) -> None:
    """Export cross-platform role matrices for Zendesk and Dynamics.

    Loads role definitions from both Zendesk and Dynamics systems, builds
    a unified role matrix showing cross-platform relationships, and exports
    to JSON for use in access control and permission harmonization.

    Args:
        zendesk_roles_file: Zendesk roles file (JSON or JSONL)
        dynamics_roles_file: Dynamics roles file (JSON or JSONL)
        output_json: Output matrix JSON file

    Input Formats:
        - JSON: Single object or array of objects
        - JSONL: One role object per line

    Output:
        JSON matrix with:
        - Zendesk roles
        - Dynamics roles
        - Role mappings and relationships

    Examples:
        # Export role matrices
        codex roles export-matrix zendesk_roles.json dynamics_roles.json matrix.json

        # From JSONL files
        codex roles export-matrix zendesk_roles.jsonl dynamics_roles.jsonl matrix.json

        # Mixed formats
        codex roles export-matrix zendesk.json dynamics.jsonl output_matrix.json

    See Also:
        codex zendesk snapshot - Export Zendesk configuration
    """
    zendesk_raw = _load_jsonl_or_json(zendesk_roles_file)
    dynamics_raw = _load_jsonl_or_json(dynamics_roles_file)

    zendesk_roles = [ZendeskRole.model_validate(item) for item in zendesk_raw]  # type: ignore[attr-defined]
    dynamics_roles = [DynamicsRole.model_validate(item) for item in dynamics_raw]  # type: ignore[attr-defined]

    matrix = build_role_matrix(zendesk_roles, dynamics_roles)
    output_json.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    typer.echo(output_json.as_posix())
