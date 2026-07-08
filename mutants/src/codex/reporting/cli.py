"""Reporting CLI - Phase 3 implementation stub."""

import json
import logging
from pathlib import Path
from typing import Any

import click

logger = logging.getLogger(__name__)

_METRICS_FILE = Path(".codex/metrics.ndjson")


def _load_metrics(n: int = 10) -> list[dict[str, Any]]:
    """Load last n entries from .codex/metrics.ndjson."""
    entries: list[dict[str, Any]] = []
    if _METRICS_FILE.exists():
        try:
            lines = _METRICS_FILE.read_text().splitlines()
            for line in lines[-n:]:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except (IOError, OSError):
                        logger.debug("Suppressed exception in handler", exc_info=True)
        except (IOError, OSError) as exc:
            click.echo(f"Warning: could not read metrics file: {exc}", err=True)
    return entries


@click.command()
@click.option("--format", type=click.Choice(["json", "yaml", "html", "pdf"]), default="html")
@click.option("--output", type=click.Path(), required=False, default=None, help="Output file")
@click.option(
    "--type",
    "report_type",
    type=click.Choice(["summary", "detail", "trend"]),
    default="summary",
)
def report_main(format: str, output: str, _report_type: str) -> None:
    """Generate code quality reports.

    Examples:
        codex-report --format html --output report.html
        codex-report --format json --type trend --output trend.json
    """
    entries = _load_metrics(10)

    if not entries:
        md = "# Codex Metrics Report\n\n_No metrics data found in `.codex/metrics.ndjson`._\n"
    else:
        keys = sorted({k for e in entries for k in e})
        header = "| " + " | ".join(keys) + " |"
        sep = "| " + " | ".join("---" for _ in keys) + " |"
        rows = []
        for e in entries:
            row = "| " + " | ".join(str(e.get(k, "")) for k in keys) + " |"
            rows.append(row)
        md = "# Codex Metrics Report\n\n" + "\n".join([header, sep] + rows) + "\n"

    if output:
        Path(output).write_text(md)
        click.echo(f"Report written to {output}")
    else:
        click.echo(md)


@click.command()
@click.option("--output", type=click.Path(), default=None)
@click.option("--open", "open_browser", is_flag=True, help="Open in browser after generation")
def dashboard_main(output: str, open_browser: bool) -> None:
    """Generate interactive quality dashboard.

    Examples:
        codex-dashboard --output dashboard.html --open
    """
    entries = _load_metrics(10)

    if not entries:
        body = "<p><em>No metrics data found in <code>.codex/metrics.ndjson</code>.</em></p>"
    else:
        keys = sorted({k for e in entries for k in e})
        header_cells = "".join(f"<th>{k}</th>" for k in keys)
        rows_html = ""
        for e in entries:
            cells = "".join(f"<td>{e.get(k, '')}</td>" for k in keys)
            rows_html += f"<tr>{cells}</tr>\n"
        body = (
            f"<table border='1'><thead><tr>{header_cells}</tr></thead>"
            f"<tbody>{rows_html}</tbody></table>"
        )

    html = (
        "<!DOCTYPE html><html><head><title>Codex Dashboard</title></head>"
        f"<body><h1>Codex Metrics Dashboard</h1>{body}</body></html>"
    )

    if output:
        Path(output).write_text(html)
        click.echo(f"Dashboard written to {output}")
        if open_browser:
            import webbrowser

            webbrowser.open(f"file://{Path(output).resolve()}")
    else:
        click.echo(html)


if __name__ == "__main__":
    report_main()
