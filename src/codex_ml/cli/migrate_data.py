"""
Migrate Data Module

This module provides functionality for migrate data.

Usage:
    from cli.migrate_data import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import json
import tempfile
from pathlib import Path
from typing import Optional

import typer

from codex_ml.data.migration import AssignmentMappingMigration

app = typer.Typer(help="Migrate assignment mapping files between versions")


@app.command()
def migrate(
    input_path: Path = typer.Argument(..., help="Input assignment mapping file"),
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    from_version: str = typer.Option("auto", "--from", help="Source version (auto, 1.0, 2.0)"),
    to_version: str = typer.Option("3.0", "--to", help="Target version (2.0, 3.0)"),
) -> None:
    """Migrate assignment mapping files between versions.

    Examples:
        # Auto-detect version and migrate to v3
        python -m codex_ml.cli.migrate_data migrate data/old_mappings.json

        # Explicitly migrate from v1 to v3
        python -m codex_ml.cli.migrate_data migrate data/v1.json --from 1.0 --to 3.0

        # Migrate and specify output path
        python -m codex_ml.cli.migrate_data migrate data/old.json -o data/new.json
    """
    if not input_path.exists():
        typer.echo(f"Error: Input file not found: {input_path}", err=True)
        raise typer.Exit(1)

    # Auto-detect version if needed
    if from_version == "auto":
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
            detected_version = data.get("version", "1.0")
            # Ensure comparisons are reliable even if the version was encoded as a number
            from_version = str(detected_version)
        typer.echo(f"Auto-detected source version: {from_version}")

    # Perform migration
    try:
        if from_version == "1.0" and to_version == "2.0":
            result = AssignmentMappingMigration.migrate_v1_to_v2(input_path)

        elif from_version == "2.0" and to_version == "3.0":
            result = AssignmentMappingMigration.migrate_v2_to_v3(input_path)

        elif from_version == "1.0" and to_version == "3.0":
            # Two-step migration: v1 -> v2 -> v3
            v2_data = AssignmentMappingMigration.migrate_v1_to_v2(input_path)

            # Save v2 to temp file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as tf:
                json.dump(v2_data, tf)
                temp_path = Path(tf.name)

            try:
                result = AssignmentMappingMigration.migrate_v2_to_v3(temp_path)
            finally:
                temp_path.unlink()

        else:
            typer.echo(
                f"Error: Migration from {from_version} to {to_version} not supported",
                err=True,
            )
            raise typer.Exit(1)

    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        typer.echo(f"Error during migration: {e}", err=True)
        raise typer.Exit(1) from e

    # Determine output path
    output = output_path or input_path.with_suffix(".migrated.json")

    # Write result
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    typer.echo(f"✓ Successfully migrated {input_path} → {output}")
    typer.echo(f"  Source version: {from_version}")
    typer.echo(f"  Target version: {to_version}")


if __name__ == "__main__":
    app()
