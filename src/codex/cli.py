"""
Unified CLI for codex, using click for subcommands and input validation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

# Resolve helper scripts relative to this file so the CLI works from any CWD.
TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools"


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


@cli.group("logs")
def logs() -> None:
    """Codex logs (local SQLite data blot)."""
    pass


@logs.command("init")
@click.option("--db", default=".codex/codex.sqlite", help="DB path")
def logs_init(db: str) -> None:
    """Initialize SQLite schema for logs."""
    script = TOOLS_DIR / "codex_db.py"
    try:
        subprocess.run([sys.executable, str(script), "--init", "--db", db], check=True)
    except Exception as exc:
        click.echo(f"Failed to init logs DB: {exc}", err=True)
        sys.exit(1)


@logs.command("ingest")
@click.option("--changes", type=click.Path(exists=True), help=".codex/change_log.md")
@click.option("--results", type=click.Path(exists=True), help=".codex/results.md")
@click.option("--branch", default="unknown")
@click.option("--db", default=".codex/codex.sqlite")
def logs_ingest(changes, results, branch: str, db: str) -> None:
    """Ingest markdown logs into SQLite."""
    script = TOOLS_DIR / "codex_ingest_md.py"
    args = [sys.executable, str(script), "--db", db]
    if changes:
        args += ["--changes", changes, "--branch", branch]
    if results:
        args += ["--results", results]
    try:
        subprocess.run(args, check=True)
    except Exception as exc:
        click.echo(f"Failed to ingest logs: {exc}", err=True)
        sys.exit(1)


@logs.command("query")
@click.option("--sql", required=True, help="SQL query to run")
@click.option("--db", default=".codex/codex.sqlite")
def logs_query(sql: str, db: str) -> None:
    """Query the SQLite logs database."""
    script = TOOLS_DIR / "codex_db.py"
    args = [sys.executable, str(script), "--db", db, "--query", sql]
    try:
        subprocess.run(args, check=True)
    except Exception as exc:
        click.echo(f"Failed to query logs: {exc}", err=True)
        sys.exit(1)


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


@cli.command("train")
@click.option(
    "--engine", type=click.Choice(["custom", "hf"]), default="custom", help="Training engine to use"
)
def train_cmd(engine: str) -> None:
    """Train a model using the selected engine."""
    if engine == "hf":
        from training.engine_hf_trainer import train as hf_train

        hf_train()
    else:
        from codex_ml.train_loop import train as custom_train

        custom_train()


if __name__ == "__main__":
    cli()
