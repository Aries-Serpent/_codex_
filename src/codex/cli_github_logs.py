"""CLI commands for fetching GitHub Actions logs.

Provides commands to fetch logs from GitHub Actions workflows, jobs, and check runs.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import click

logger = logging.getLogger(__name__)


def _get_github_client() -> object:
    """Get GitHub client instance."""
    try:
        from services.github.client import GitHubClientSync

        return GitHubClientSync()
    except ImportError as e:
        raise click.ClickException(
            f"GitHub client not available: {e}. Ensure httpx and pydantic are installed."
        ) from e


@click.group(name="github-logs")
def cli() -> None:
    """Fetch GitHub Actions logs via CLI.

    Examples:
        # Fetch check run logs
        codex github-logs check-run Aries-Serpent _codex_ 59990656344

        # Fetch job logs
        codex github-logs job Aries-Serpent _codex_ 12345678

        # Save to file
        codex github-logs check-run Aries-Serpent _codex_ 59990656344 -o logs.txt
    """


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
    """Fetch logs from a GitHub Actions check run.

    Args:
        owner: Repository owner (e.g., 'Aries-Serpent')
        repo: Repository name (e.g., '_codex_')
        check_run_id: Check run ID (e.g., 59990656344)

    Examples:
        # Fetch check run logs to stdout
        codex github-logs check-run Aries-Serpent _codex_ 59990656344

        # Save to file
        codex github-logs check-run Aries-Serpent _codex_ 59990656344 -o logs.txt

        # Get as JSON
        codex github-logs check-run Aries-Serpent _codex_ 59990656344 -f json
    """
    try:
        client = _get_github_client()

        click.echo(f"Fetching check run {check_run_id} logs from {owner}/{repo}...", err=True)

        # Fetch the check run details first
        check_run = client.get_check_run(owner, repo, check_run_id)  # type: ignore[attr-defined]

        # Fetch logs
        logs = client.get_check_run_logs(owner, repo, check_run_id)  # type: ignore[attr-defined]

        # Format output
        if format == "json":
            output_data = {
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
            output_text = json.dumps(output_data, indent=2)
        else:
            output_text = logs

        # Write output
        if output:
            output_path = Path(output)
            output_path.write_text(output_text, encoding="utf-8")
            click.echo(f"Logs saved to {output_path}", err=True)
        else:
            click.echo(output_text)

        click.echo(f"✓ Successfully fetched logs for check run {check_run_id}", err=True)

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.error("Failed to fetch check run logs: <ERROR_TYPE>", exc_info=True)
        raise click.ClickException(str(e)) from e


@cli.command(name="job")
@click.argument("owner")
@click.argument("repo")
@click.argument("job_id", type=int)
@click.option("--output", "-o", type=click.Path(), help="Output file path (default: stdout)")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def fetch_job_logs(
    owner: str,
    repo: str,
    job_id: int,
    output: Optional[str],
    format: str,
) -> None:
    """Fetch logs from a GitHub Actions workflow job.

    Args:
        owner: Repository owner (e.g., 'Aries-Serpent')
        repo: Repository name (e.g., '_codex_')
        job_id: Job ID

    Examples:
        # Fetch job logs to stdout
        codex github-logs job Aries-Serpent _codex_ 12345678

        # Save to file
        codex github-logs job Aries-Serpent _codex_ 12345678 -o logs.txt
    """
    try:
        client = _get_github_client()

        click.echo(f"Fetching job {job_id} logs from {owner}/{repo}...", err=True)

        # Fetch logs
        logs = client.get_job_logs(owner, repo, job_id)  # type: ignore[attr-defined]

        # Format output
        if format == "json":
            output_data = {
                "job_id": job_id,
                "owner": owner,
                "repo": repo,
                "logs": logs,
            }
            output_text = json.dumps(output_data, indent=2)
        else:
            output_text = logs

        # Write output
        if output:
            output_path = Path(output)
            output_path.write_text(output_text, encoding="utf-8")
            click.echo(f"Logs saved to {output_path}", err=True)
        else:
            click.echo(output_text)

        click.echo(f"✓ Successfully fetched logs for job {job_id}", err=True)

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.error("Failed to fetch job logs: <ERROR_TYPE>", exc_info=True)
        raise click.ClickException(str(e)) from e


@cli.command(name="list-check-runs")
@click.argument("owner")
@click.argument("repo")
@click.argument("ref")
@click.option(
    "--status",
    type=click.Choice(["queued", "in_progress", "completed"]),
    help="Filter by status",
)
@click.option("--name", help="Filter by check run name")
def list_check_runs(
    owner: str,
    repo: str,
    ref: str,
    status: Optional[str],
    name: Optional[str],
) -> None:
    """List check runs for a git reference.

    Args:
        owner: Repository owner (e.g., 'Aries-Serpent')
        repo: Repository name (e.g., '_codex_')
        ref: Git reference (commit SHA, branch, or tag)

    Examples:
        # List check runs for a commit
        codex github-logs list-check-runs Aries-Serpent _codex_ b6b52590b9551c4d29b90ea122d885ef83cd0d8d

        # List only completed check runs
        codex github-logs list-check-runs Aries-Serpent _codex_ main --status completed
    """  # noqa: E501
    try:
        client = _get_github_client()

        click.echo(f"Fetching check runs for {owner}/{repo}@{ref}...", err=True)

        check_runs = client.list_check_runs_for_ref(  # type: ignore[attr-defined]
            owner, repo, ref, check_name=name, status=status
        )

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

    except (ConnectionError, TimeoutError) as e:
        type(e).__name__
        logger.error("Failed to list check runs: <ERROR_TYPE>", exc_info=True)
        raise click.ClickException(str(e)) from e


if __name__ == "__main__":
    cli()
