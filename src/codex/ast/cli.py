"""
AST CLI (Typer) — analyze | audit | diff

Human-readable by default; use --json for machine output.
Exit codes:
 0 success
 2 invalid args
 3 runtime error
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import typer  # noqa: E402

app = typer.Typer(help="AST tools: analyze, audit, diff.")


def _collect_py_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".py":
        return [path]
    if path.is_dir():
        return list(path.rglob("*.py"))
    return []


def _analyze_path(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


@app.command("analyze")
def analyze(
    target: Path = typer.Argument(..., exists=True, readable=True),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
):
    try:
        res = _analyze_path(target)
        if json_output:
            typer.echo(json.dumps(res, indent=2))
        else:
            typer.echo(f"Analyze {target}: files={res['files']} lines={res['total_lines']}")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        typer.echo(f"Analyze error: {e}", err=True)
        raise typer.Exit(code=3) from e


@app.command("audit")
def audit(
    target: Path = typer.Argument(".", help="Root to audit"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
):
    try:
        res = _analyze_path(target)
        # For now, reuse analyze summary as audit-lite
        if json_output:
            typer.echo(json.dumps({"summary": res}, indent=2))
        else:
            typer.echo(f"Audit {target}: files={res['files']} lines={res['total_lines']}")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        typer.echo(f"Audit error: {e}", err=True)
        raise typer.Exit(code=3) from e


@app.command("diff")
def diff(
    a: Path = typer.Argument(..., exists=True, readable=True),
    b: Path = typer.Argument(..., exists=True, readable=True),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
):
    try:
        ra = _analyze_path(a)
        rb = _analyze_path(b)
        delta_files = rb["files"] - ra["files"]
        delta_lines = rb["total_lines"] - ra["total_lines"]
        res = {
            "a": ra,
            "b": rb,
            "delta_files": delta_files,
            "delta_lines": delta_lines,
        }
        if json_output:
            typer.echo(json.dumps(res, indent=2))
        else:
            typer.echo(f"Diff files={delta_files:+} lines={delta_lines:+}")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        typer.echo(f"Diff error: {e}", err=True)
        raise typer.Exit(code=3) from e


if __name__ == "__main__":  # pragma: no cover
    app()
