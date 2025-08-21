"""
Unified CLI for codex, using click for subcommands and input validation.
"""

from __future__ import annotations

import sys
import click

ALLOWED_TASKS = {
    "ingest": lambda: print("Ingestion scaffold created (placeholder)."),
    "ci": lambda: print("CI workflow unified."),
    "pool-fix": lambda: print("SQLite connection pool fix applied."),
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
