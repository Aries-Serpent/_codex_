"""Manifest CLI helpers (hashing, validation, scaffolding)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import typer
except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency path
    raise ImportError("typer is required for codex_ml.cli.manifest") from exc

if not hasattr(typer, "Typer"):  # pragma: no cover - optional dependency path
    raise ImportError("typer.Typer is required for codex_ml.cli.manifest")

from codex_ml.checkpointing.schema_v2 import (
    SCHEMA_ID,
    canonical_json as _canon,
    manifest_digest_from_path,
    validate_manifest as _validate,
)


app = typer.Typer(no_args_is_help=True, add_completion=False)


def compute_digest(path: Path) -> str:
    return manifest_digest_from_path(path)


@app.command("hash")
def hash_cmd(
    path: Path = typer.Option(..., "--path", "-p", help="Path to manifest JSON"),
    update_readme: Path | None = typer.Option(None, "--update-readme", help="README to update"),
    start_marker: str = typer.Option("<!-- manifest-digest:start -->"),
    end_marker: str = typer.Option("<!-- manifest-digest:end -->"),
) -> None:
    """
    Compute SHA256 digest of a JSON manifest and optionally update README with a badge.
    """

    digest = compute_digest(path)
    typer.echo(digest)
    if update_readme:
        rd = update_readme.read_text(encoding="utf-8")
        badge = f"[![Manifest SHA256](https://img.shields.io/badge/manifest-{digest[:12]}-blue)](#)"
        block = f"{start_marker}\n{badge}\n{end_marker}"
        if start_marker in rd and end_marker in rd:
            rd2 = re.sub(
                f"{re.escape(start_marker)}[\\s\\S]*?{re.escape(end_marker)}",
                block,
                rd,
                flags=re.M,
            )
        else:
            lines = rd.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("#"):
                    lines[i : i + 1] = [line, "", block]
                    rd2 = "\n".join(lines)
                    break
            else:
                rd2 = rd + "\n\n" + block + "\n"
        update_readme.write_text(rd2, encoding="utf-8")


@app.command("validate")
def validate_cmd(
    path: Path = typer.Option(..., "--path", "-p", help="Path to manifest JSON"),
    strict: bool = typer.Option(False, "--strict", help="Fail on unknown top-level keys"),
) -> None:
    """
    Validate a manifest's minimal structure. Exit codes:
      0 = valid, 2 = invalid schema, 1 = other error
    """

    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            typer.echo("invalid: manifest must be a JSON object")
            raise typer.Exit(code=2)
        schema = raw.get("schema")
        if schema != SCHEMA_ID:
            typer.echo(f"invalid schema: expected '{SCHEMA_ID}' but found '{schema}'")
            raise typer.Exit(code=2)
        _validate(raw)
        if strict:
            allowed = {"schema", "run", "weights", "optimizer", "scheduler", "rng", "notes"}
            unknown = set(raw.keys()) - allowed
            if unknown:
                typer.echo(f"unknown keys: {sorted(unknown)}")
                raise typer.Exit(code=2)
        typer.echo(_canon(raw))
        raise typer.Exit(code=0)
    except typer.Exit:
        raise
    except ValueError as ve:
        typer.echo(f"invalid: {ve}")
        raise typer.Exit(code=2)
    except Exception as exc:  # pragma: no cover - unexpected path
        typer.echo(f"error: {exc}")
        raise typer.Exit(code=1)


@app.command("init")
def init_cmd(
    out: Path = typer.Option(..., "--out", "-o", help="Output manifest path (.json)"),
    run_id: str = typer.Option("unknown", "--run-id"),
) -> None:
    """
    Write a minimal, valid v2 manifest template to --out.
    """

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest = {
        "schema": SCHEMA_ID,
        "run": {
            "id": run_id,
            "created_at": now,
            "framework": "pytorch",
            "codex_version": None,
        },
        "weights": {
            "format": "pt",
            "bytes": 0,
            "dtype": "float32",
            "sharded": False,
        },
        "optimizer": None,
        "scheduler": None,
        "rng": None,
        "notes": None,
    }
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    typer.echo(str(out))


if __name__ == "__main__":  # pragma: no cover
    app()
