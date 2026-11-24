"""Reporting CLI - Phase 3 implementation stub."""

import argparse
import html
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
                    except (IOError, OSError, ModuleNotFoundError, ImportError):
                        logger.debug("Suppressed exception in handler", exc_info=True)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
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
        header_cells = "".join(f"<th>{html.escape(str(k))}</th>" for k in keys)
        rows_html = ""
        for e in entries:
            cells = "".join(f"<td>{html.escape(str(e.get(k, '')))}</td>" for k in keys)
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


class ReportingCLI:
    """CLI interface for reporting functionality."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = dict(config or {})

    def generate_report(self, data: dict[str, Any] | None = None, format: str = "html") -> str:
        """Generate a report for text, JSON, HTML, Markdown or PDF-like output."""
        data = {} if data is None else data
        if not isinstance(data, dict):
            raise TypeError("Report data must be a mapping")

        normalized = format.lower()
        if normalized not in {"text", "json", "html", "markdown", "yaml", "pdf"}:
            raise ValueError(f"Unsupported report format: {format}")

        if normalized == "json":
            return json.dumps(data, indent=2, sort_keys=True)
        if normalized == "html":
            title = html.escape(str(data.get("title", "Codex Report")))
            summary = html.escape(str(data.get("summary", data)))
            return f"<!doctype html><html><head><title>{title}</title></head><body><h1>{title}</h1><p>{summary}</p></body></html>"
        if normalized == "text":
            lines = [f"{key}: {value}" for key, value in data.items()]
            return "\n".join(lines) if lines else "No report data"
        if normalized == "markdown":
            lines = [f"# {data.get('title', 'Codex Report')}\n"]
            for key, value in data.items():
                if key != "title":
                    lines.append(f"- **{key}:** {value}")
            return "\n".join(lines)
        if normalized == "yaml":
            return "\n".join(f"{key}: {value}" for key, value in data.items())
        return f"Report generated in {normalized} format"

    def format_metrics(self, metrics: dict[str, Any]) -> str:
        """Format a metrics mapping as readable text."""
        return "\n".join(f"{key}: {value}" for key, value in metrics.items())

    def format_percentage(self, value: float) -> str:
        """Format a numeric fraction as a percentage string."""
        return f"{float(value) * 100:.2f}%"

    def format_number(self, number: int | float) -> str:
        """Format an integer or float with thousands separators."""
        if isinstance(number, float):
            return f"{number:,.2f}"
        return f"{number:,}"

    def parse_args(self, args: list[str] | None = None) -> argparse.Namespace:
        """Parse reporting CLI arguments."""
        parser = argparse.ArgumentParser(prog="codex-report")
        parser.add_argument(
            "--format", choices=["text", "json", "html", "markdown", "yaml", "pdf"], default="html"
        )
        parser.add_argument("--output", default=None)
        return parser.parse_args(args)

    def write_report(self, report: str, output_path: str) -> None:
        """Write report text to a file or stdout."""
        if output_path == "-":
            print(report)
            return
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")

    def get_output_path(self, format: str = "html") -> str:
        """Return an output path for the selected format."""
        suffix = {"markdown": "md", "text": "txt"}.get(format.lower(), format.lower())
        return self.config.get("output") or f"report.{suffix}"
