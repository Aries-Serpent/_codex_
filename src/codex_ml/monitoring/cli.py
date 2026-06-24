"""
Cli Module

This module provides functionality for cli.

Usage:
    from monitoring.cli import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import csv  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

try:  # Optional dependency: Typer preferred when present
    import typer
except ModuleNotFoundError:  # pragma: no cover - Typer absent
    typer = None
else:  # pragma: no cover - namespace stub
    if not hasattr(typer, "Typer"):
        typer = None

from .schema import LogRecord  # noqa: E402


def _inspect_file(path: str, *, echo) -> None:
    p = Path(path)
    count = sum(1 for _ in p.open()) if p.exists() else 0
    echo({"path": str(p), "lines": count})


def _export_file(src: str, dst: str, fmt: str, *, echo, bad_param_exc) -> None:
    records = [json.loads(line) for line in Path(src).read_text().splitlines()]
    rows = []
    for r in records:
        try:
            rows.append(
                LogRecord(**{k: r.get(k) for k in LogRecord.__dataclass_fields__ if k in r}).dict()
            )
        except (ValueError, TypeError, RuntimeError):
            logger.warning("Exception occurred", exc_info=True)
            rows.append(r)
    if fmt == "csv":
        keys = [
            "version",
            "ts",
            "run_id",
            "phase",
            "step",
            "split",
            "dataset",
            "metric",
            "value",
            "meta",
        ]
        with Path(dst).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        return
    raise bad_param_exc("unsupported format")


if typer is not None:  # pragma: no cover - Typer-driven CLI
    app = typer.Typer(help="Utilities for NDJSON telemetry logs")

    @app.command()
    def inspect(path: str) -> None:
        """Print a short summary of ``path``."""

        _inspect_file(path, echo=typer.echo)

    @app.command()
    def export(src: str, dst: str, fmt: str = "csv") -> None:
        """Export NDJSON ``src`` to ``dst`` in ``fmt`` format."""

        _export_file(src, dst, fmt, echo=typer.echo, bad_param_exc=typer.BadParameter)

else:
    import click

    @click.group(help="Utilities for NDJSON telemetry logs")
    def app() -> None:
        """Entry point for the Click fallback CLI."""

    @app.command()
    @click.argument("path")
    def inspect(path: str) -> None:
        """Print a short summary of ``path``."""

        _inspect_file(path, echo=click.echo)

    @app.command()
    @click.argument("src")
    @click.argument("dst")
    @click.option("--fmt", default="csv", show_default=True)
    def export(src: str, dst: str, fmt: str) -> None:
        """Export NDJSON ``src`` to ``dst`` in ``fmt`` format."""

        _export_file(src, dst, fmt, echo=click.echo, bad_param_exc=click.BadParameter)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
