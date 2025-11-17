"""
AST CLI (Typer) — analyze | audit | diff

Human-readable by default; use --json for machine output.
Exit codes:
 0 success
 2 invalid args
 3 runtime error
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import typer

app = typer.Typer(help="AST tools: analyze, audit, diff.")


def _collect_py_files(path: Path) -> List[Path]:
    if path.is_file() and path.suffix == ".py":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("*.py")]
    return []


def _analyze_path(path: Path) -> Dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception:
            pass
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
    except Exception as e:
        typer.echo(f"Analyze error: {e}", err=True)
        raise typer.Exit(code=3)


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
    except Exception as e:
        typer.echo(f"Audit error: {e}", err=True)
        raise typer.Exit(code=3)


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
    except Exception as e:
        typer.echo(f"Diff error: {e}", err=True)
        raise typer.Exit(code=3)


if __name__ == "__main__":  # pragma: no cover
    app()
