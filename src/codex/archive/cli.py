"""Click-based CLI for the Codex tombstone archive."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path

import click

from . import schema
from .backend import ArchiveConfig
from .service import ArchiveService
from .util import append_evidence, redact_url_credentials


def _service(apply_schema: bool = True) -> ArchiveService:
    config = ArchiveConfig.from_env()
    return ArchiveService(config, apply_schema=apply_schema)


def _parse_metadata(entries: Iterable[str]) -> dict[str, str]:
    payload: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise click.BadParameter(f"Metadata entry must be in key=value form: {entry}")
        key, value = entry.split("=", 1)
        payload[key.strip()] = value.strip()
    return payload


def _resolve_commit(commit: str) -> str:
    if commit.lower() == "head":
        from subprocess import CalledProcessError, run

        try:
            result = run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
            commit = result.stdout.strip()
        except CalledProcessError as exc:  # pragma: no cover - best effort
            raise click.BadParameter(f"Unable to resolve HEAD commit: {exc}") from exc
    return commit


@click.group(help="Codex tombstone archive workflow.")
def cli() -> None:
    """Entry point for archive operations."""


@cli.command("init")
@click.option("--dialect", help="Optional override for backend dialect")
def init_schema(dialect: str | None) -> None:
    """Initialise or upgrade the archive schema."""

    service = _service(apply_schema=False)
    if dialect:
        service.dal.backend = dialect.lower()
    service.ensure_schema()
    click.echo(f"archive schema ensured for backend={service.dal.backend}")


@cli.command("schema")
@click.option("--dialect", help="Dialect to emit (defaults to configured backend)")
def emit_schema(dialect: str | None) -> None:
    """Print the SQL schema for a backend."""

    config = ArchiveConfig.from_env()
    target = (dialect or config.backend).lower()
    statements = schema.statements_for(target)
    for statement in statements:
        click.echo(statement.strip() + ";")


@cli.command("store")
@click.argument("repo")
@click.argument(
    "filepath", type=click.Path(path_type=Path, exists=True, dir_okay=False, readable=True)
)
@click.option(
    "--reason",
    default="dead",
    show_default=True,
    type=click.Choice(["dead", "pruned", "legacy", "replaced"]),
    help="Archival reason",
)
@click.option("--by", "actor", required=True, help="Actor performing the archive")
@click.option("--commit", default="HEAD", show_default=True, help="Git commit SHA for provenance")
@click.option(
    "--kind", default="code", show_default=True, type=click.Choice(["code", "doc", "asset"])
)
@click.option("--language", help="Optional language identifier")
@click.option("--mime", help="Override MIME type")
@click.option("--tag", "tags", multiple=True, help="Assign tags to the archived item")
@click.option(
    "--metadata", "metadata_entries", multiple=True, help="Extra metadata entries key=value"
)
def store(
    repo: str,
    filepath: Path,
    reason: str,
    actor: str,
    commit: str,
    kind: str,
    language: str | None,
    mime: str | None,
    tags: tuple[str, ...],
    metadata_entries: tuple[str, ...],
) -> None:
    """Archive a file and emit tombstone metadata."""

    service = _service()
    extra = _parse_metadata(metadata_entries)
    commit_sha = _resolve_commit(commit)
    result = service.archive_path(
        repo=repo,
        path=filepath,
        reason=reason,
        archived_by=actor,
        commit_sha=commit_sha,
        kind=kind,
        language=language,
        mime_type=mime,
        tags=list(tags),
        extra_metadata=extra,
    )
    payload = {
        "tombstone": result.tombstone_id,
        "sha256": result.sha256,
        "size_bytes": result.size_bytes,
        "compressed_size": result.compressed_size,
        "repo": result.repo,
        "path": result.path,
    }
    click.echo(json.dumps(payload, indent=2))


@cli.command("list")
@click.option("--repo", help="Filter by repo")
@click.option("--since", help="ISO timestamp filter")
@click.option("--limit", default=50, show_default=True, help="Maximum number of rows")
def list_items(repo: str | None, since: str | None, limit: int) -> None:
    """List archived items."""

    service = _service()
    rows = service.list_items(repo=repo, since=since, limit=limit)
    click.echo(json.dumps(rows, indent=2))


@cli.command("show")
@click.argument("tombstone")
def show(tombstone: str) -> None:
    """Show detailed metadata for an archived item."""

    service = _service()
    payload = service.show_item(tombstone)
    click.echo(json.dumps(payload, indent=2))


@cli.command("restore")
@click.argument("tombstone")
@click.argument("output", type=click.Path(path_type=Path, dir_okay=False))
@click.option("--by", "actor", required=True, help="Actor executing restore")
@click.option(
    "--debug",
    is_flag=True,
    help="Emit verbose backend diagnostics, including full connection URLs.",
)
def restore(tombstone: str, output: Path, actor: str, debug: bool) -> None:
    """Restore an archived file to the local filesystem.

    Performs pre-flight backend validation and logs all failures to the
    evidence trail for auditability.
    """

    service = _service()

    try:
        config = service.config
        click.echo(f"[DEBUG] Archive backend: {config.backend}", err=True)
        if debug:
            click.echo(f"[DEBUG] Archive URL: {config.url}", err=True)
        else:
            redacted = redact_url_credentials(config.url)
            if not redacted:
                redacted_display = "<not set>"
            elif config.url and redacted != config.url:
                redacted_display = f"{redacted} (credentials redacted)"
            else:
                redacted_display = redacted
            click.echo(f"[INFO] Archive URL: {redacted_display}", err=True)
        service.dal.list_items(limit=0)
        click.echo("[DEBUG] Backend validation: OK", err=True)
    except Exception as validation_err:
        message = (
            f"Archive backend validation failed: {type(validation_err).__name__}: {validation_err}"
        )
        click.echo(f"ERROR: {message}", err=True)
        append_evidence(
            {
                "action": "RESTORE_FAIL",
                "actor": actor,
                "tombstone": tombstone,
                "reason": message,
            }
        )
        sys.exit(1)

    try:
        path = service.restore_to_path(tombstone, output_path=output, actor=actor)
    except LookupError as lookup_err:
        click.echo(
            f"ERROR: Tombstone not found in archive backend: {lookup_err}",
            err=True,
        )
        click.echo(
            "DEBUG: Verify the tombstone ID and ensure the archive backend contains "
            "the recorded entry.",
            err=True,
        )
        sys.exit(1)
    except RuntimeError as runtime_err:
        click.echo(f"ERROR: Restore failed: {runtime_err}", err=True)
        sys.exit(1)
    except Exception as unexpected_err:  # pragma: no cover - defensive guard
        click.echo(
            f"ERROR: Unexpected restore error: {type(unexpected_err).__name__}: {unexpected_err}",
            err=True,
        )
        append_evidence(
            {
                "action": "RESTORE_FAIL",
                "actor": actor,
                "tombstone": tombstone,
                "reason": f"Unexpected error: {type(unexpected_err).__name__}",
            }
        )
        sys.exit(1)
    click.echo(path.as_posix())


@cli.command("prune-request")
@click.argument("tombstone")
@click.option("--by", "actor", required=True, help="Requester")
@click.option("--reason", required=True, help="Business justification")
def prune_request(tombstone: str, actor: str, reason: str) -> None:
    """Record a prune request event."""

    service = _service()
    service.request_prune(tombstone, actor=actor, reason=reason)
    click.echo("recorded prune request")


@cli.command("purge")
@click.argument("tombstone")
@click.option("--by", "primary", required=True, help="Primary approver")
@click.option("--second", "secondary", required=True, help="Secondary approver")
@click.option("--reason", required=True, help="Justification for purge")
@click.option("--apply", is_flag=True, help="Scrub blob bytes after approvals")
def purge(tombstone: str, primary: str, secondary: str, reason: str, apply: bool) -> None:
    """Approve and optionally execute a purge."""

    service = _service()
    scrubbed = service.approve_delete(
        tombstone,
        primary_actor=primary,
        secondary_actor=secondary,
        reason=reason,
        apply=apply,
    )
    if apply:
        if scrubbed:
            click.echo("purge approvals recorded and blob scrubbed")
        else:
            click.echo("purge approvals recorded; blob retained (artifact still shared)")
    else:
        click.echo("purge approvals recorded")


@cli.command("health-check")
@click.option(
    "--debug",
    is_flag=True,
    help="Emit verbose backend diagnostics, including full connection URLs.",
)
def health_check(debug: bool) -> None:
    """Verify archive backend accessibility."""

    service = _service(apply_schema=False)
    config = service.config

    click.echo(f"Backend: {config.backend}")
    if debug:
        click.echo(f"URL: {config.url}")
    else:
        redacted = redact_url_credentials(config.url)
        if not redacted:
            redacted_display = "<not set>"
        elif config.url and redacted != config.url:
            redacted_display = f"{redacted} (credentials redacted)"
        else:
            redacted_display = redacted
        click.echo(f"URL: {redacted_display}")

    try:
        items = service.dal.list_items(limit=1)
    except Exception as exc:  # pragma: no cover - diagnostics path
        click.echo(
            f"Status: \N{BALLOT X} FAILED ({type(exc).__name__}: {exc})",
            err=True,
        )
        sys.exit(1)
    click.echo(f"Status: \N{CHECK MARK} OK (backend accessible, {len(items)} items retrievable)")
