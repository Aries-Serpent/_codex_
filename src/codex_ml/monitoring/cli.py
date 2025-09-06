from __future__ import annotations

import csv
import json
from pathlib import Path

import typer

from .schema import LogRecord

app = typer.Typer(help="Utilities for NDJSON telemetry logs")


@app.command()
def inspect(path: str) -> None:
    """Print a short summary of ``path``."""

    p = Path(path)
    count = sum(1 for _ in p.open()) if p.exists() else 0
    typer.echo({"path": str(p), "lines": count})


@app.command()
def export(src: str, dst: str, fmt: str = "csv") -> None:
    """Export NDJSON ``src`` to ``dst`` in ``fmt`` format."""

    records = [json.loads(line) for line in Path(src).read_text().splitlines()]
    rows = []
    for r in records:
        try:
            rows.append(
                LogRecord(
                    **{k: r.get(k) for k in LogRecord.__dataclass_fields__.keys() if k in r}
                ).dict()
            )
        except Exception:
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
    else:
        raise typer.BadParameter("unsupported format")


if __name__ == "__main__":
    app()
