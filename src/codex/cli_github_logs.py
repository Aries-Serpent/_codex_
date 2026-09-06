"""CLI commands for fetching GitHub Actions logs."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import click

logger = logging.getLogger(__name__)


def _get_github_client():
    """Get a GitHub sync client."""
    try:
        from src.services.github.client import GitHubClientSync
    except ImportError:
        from services.github.client import GitHubClientSync

    return GitHubClientSync()


@click.group(name="github-logs")
def cli() -> None:
    """Fetch GitHub Actions logs via CLI."""


@cli.command(name="check-run")
@click.argument("owner")
@click.argument("repo")
@click.argument("check_run_id", type=int)
@click.option("--output", "-o", type=click.Path(), help="Output file path (default: stdout)")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def fetch_check_run_logs(
    owner: str,
    repo: str,
    check_run_id: int,
    output: Optional[str],
    format: str,
) -> None:
    """Fetch logs from a GitHub Actions check run."""
    try:
        client = _get_github_client()
        click.echo(f"Fetching check run {check_run_id} logs from {owner}/{repo}...", err=True)
        check_run = client.get_check_run(owner, repo, check_run_id)
        logs = client.get_check_run_logs(owner, repo, check_run_id)
        if format == "json":
            payload = {
                "check_run_id": check_run_id,
                "owner": owner,
                "repo": repo,
                "check_run": {
                    "id": check_run.id,
                    "name": check_run.name,
                    "status": check_run.status,
                    "conclusion": check_run.conclusion,
                    "html_url": check_run.html_url,
                },
                "logs": logs,
            }
            output_text = json.dumps(payload, indent=2)
        else:
            output_text = logs

        if output:
            Path(output).write_text(output_text, encoding="utf-8")
            click.echo(f"Logs saved to {output}", err=True)
        else:
            click.echo(output_text)
        click.echo(f"✓ Successfully fetched logs for check run {check_run_id}", err=True)
    except Exception as exc:
        logger.error("Failed to fetch check run logs: %s", exc, exc_info=True)
        raise click.ClickException(str(exc)) from exc


@cli.command(name="list-check-runs")
@click.argument("owner")
@click.argument("repo")
@click.argument("ref")
@click.option("--status", type=click.Choice(["queued", "in_progress", "completed"]))
@click.option("--name", help="Filter by check run name")
def list_check_runs(owner: str, repo: str, ref: str, status: Optional[str], name: Optional[str]) -> None:
    """List check runs for a git reference."""
    try:
        client = _get_github_client()
        click.echo(f"Fetching check runs for {owner}/{repo}@{ref}...", err=True)
        check_runs = client.list_check_runs_for_ref(owner, repo, ref, check_name=name, status=status)
        if not check_runs:
            click.echo("No check runs found.", err=True)
            return
        click.echo(f"\nFound {len(check_runs)} check run(s):\n")
        for run in check_runs:
            click.echo(f"  ID: {run.id}")
            click.echo(f"  Name: {run.name}")
            click.echo(f"  Status: {run.status}")
            click.echo(f"  Conclusion: {run.conclusion or 'N/A'}")
            click.echo(f"  URL: {run.html_url}")
            click.echo()
    except Exception as exc:
        logger.error("Failed to list check runs: %s", exc, exc_info=True)
        raise click.ClickException(str(exc)) from exc


if __name__.startswith("src."):
    import sys

    sys.modules.setdefault("codex.cli_github_logs", sys.modules[__name__])
else:
    import sys

    sys.modules.setdefault("src.codex.cli_github_logs", sys.modules[__name__])


if __name__ == "__main__":
    cli()
