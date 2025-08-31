"""
Unified CLI for codex, using click for subcommands and input validation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click


def _run_ingest() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def _run_ci() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:  # noqa: BLE001
        print(f"CI failed: {exc}")


def _fix_pool() -> None:
    print("Pool fix not yet implemented; see issue #123.")


ALLOWED_TASKS = {
    "ingest": _run_ingest,
    "ci": _run_ci,
    "pool-fix": _fix_pool,
}


@click.group()
def cli() -> None:
    """Codex CLI entry point."""
    pass


@cli.command("tasks")
def list_tasks() -> None:
    """List allowed maintenance tasks."""
    for task in ALLOWED_TASKS:
        click.echo(task)


@cli.command("run")
@click.argument("task")
def run_task(task: str) -> None:
    """Run a whitelisted maintenance task by name."""
    if task not in ALLOWED_TASKS:
        click.echo(f"Task '{task}' is not allowed.", err=True)
        sys.exit(1)
    ALLOWED_TASKS[task]()
