"""Click-based CLI for the Codex tombstone archive (enhanced with config/batch/health)."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

import click

from . import schema
from .batch import BatchManifest, BatchRestore
from .config import ArchiveAppConfig
from .logging_config import export_configuration, log_restore, setup_logging
from .service import ArchiveService
from .util import append_evidence, redact_text_credentials, redact_url_credentials

logger = logging.getLogger(__name__)


def _load_config(config_file: Path | None = None) -> ArchiveAppConfig:
    return ArchiveAppConfig.load(config_file=config_file)


def _service(
    apply_schema: bool = True,
    *,
    app_config: ArchiveAppConfig | None = None,
) -> ArchiveService:
    runtime = app_config or _load_config()
    return ArchiveService(runtime, apply_schema=apply_schema)


def _setup_logger(app_config: ArchiveAppConfig) -> logging.Logger:
    return setup_logging(app_config.logging, stream=click.get_text_stream("stderr"))


def _batch_progress_logger(
    logger: logging.Logger,
    app_config: ArchiveAppConfig,
) -> Callable[[int, int, dict[str, Any]], None]:
    interval = max(1, app_config.batch.progress_interval)

    def _callback(index: int, total: int, entry: dict[str, Any]) -> None:
        metrics = entry.get("metrics") if isinstance(entry, dict) else None
        log_restore(
            logger,
            actor=entry.get("actor", "batch"),
            tombstone=entry.get("tombstone", ""),
            status=entry.get("status", "UNKNOWN"),
            detail=entry.get("detail"),
            metrics=metrics,
            logging_config=app_config.logging,
            performance_config=app_config.performance,
        )
        if index % interval == 0 or index == total:
            status = entry.get("status", "UNKNOWN")
            tombstone = entry.get("tombstone", "")
            click.echo(f"[BATCH] {index}/{total} {status} {tombstone}", err=True)

    return _callback


def _parse_metadata(entries: Iterable[str]) -> dict[str, str]:
    """Parse metadata key=value entries."""

    payload: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise click.BadParameter(f"Metadata entry must be in key=value form: {entry}")
        key, value = entry.split("=", 1)
        payload[key.strip()] = value.strip()
    return payload


def _resolve_commit(commit: str) -> str:
    """Resolve commit SHA (support 'HEAD' keyword)."""

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


@cli.command("config-show")
@click.option(
    "--config-file",
    type=click.Path(path_type=Path, dir_okay=False, exists=True),
    help="Optional explicit path to the TOML configuration file.",
)
def config_show(config_file: Path | None) -> None:
    """Display the composed archive configuration."""

    app_config = _load_config(config_file)
    payload = app_config.to_dict()
    payload["logging"] = export_configuration(app_config.logging)
    click.echo(json.dumps(payload, indent=2))


@cli.command("init")
@click.option("--dialect", help="Optional override for backend dialect")
def init_schema(dialect: str | None) -> None:
    """Initialise or upgrade the archive schema."""

    app_config = _load_config()
    service = _service(apply_schema=False, app_config=app_config)
    if dialect:
        service.dal.backend = dialect.lower()
    service.ensure_schema()
    click.echo(f"archive schema ensured for backend={service.dal.backend}")


@cli.command("schema")
@click.option("--dialect", help="Dialect to emit (defaults to configured backend)")
def emit_schema(dialect: str | None) -> None:
    """Print the SQL schema for a backend."""

    app_config = _load_config()
    target = (dialect or app_config.backend.backend).lower()
    statements = schema.statements_for(target)
    for statement in statements:
        click.echo(statement.strip() + ";")


@cli.command("store")
@click.argument("repo")
@click.argument(
    "filepath",
    type=click.Path(path_type=Path, exists=True, dir_okay=False, readable=True),
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
    "--kind",
    default="code",
    show_default=True,
    type=click.Choice(["code", "doc", "asset"]),
)
@click.option("--language", help="Optional language identifier")
@click.option("--mime", help="Override MIME type")
@click.option("--tag", "tags", multiple=True, help="Assign tags to the archived item")
@click.option(
    "--metadata",
    "metadata_entries",
    multiple=True,
    help="Extra metadata entries key=value",
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

    app_config = _load_config()
    _setup_logger(app_config)
    service = _service(apply_schema=True, app_config=app_config)
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
        extra_metadata=extra,  # type: ignore[arg-type]
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

    app_config = _load_config()
    _setup_logger(app_config)
    service = _service(apply_schema=True, app_config=app_config)
    rows = service.list_items(repo=repo, since=since, limit=limit)
    click.echo(json.dumps(rows, indent=2))


@cli.command("show")
@click.argument("tombstone")
def show(tombstone: str) -> None:
    """Show detailed metadata for an archived item."""

    app_config = _load_config()
    _setup_logger(app_config)
    service = _service(apply_schema=True, app_config=app_config)
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
    """Restore an archived file to the local filesystem."""

    app_config = _load_config()
    logger = _setup_logger(app_config)
    service = _service(apply_schema=True, app_config=app_config)

    try:
        config = service.config
        click.echo(f"[DEBUG] Archive backend: {config.backend.backend}", err=True)
        if debug:
            click.echo(f"[DEBUG] Archive URL: {config.backend.url}", err=True)
        else:
            redacted = redact_url_credentials(config.backend.url)
            if not redacted:
                redacted_display = "<not set>"
            elif redacted != config.backend.url:
                redacted_display = f"{redacted} (credentials redacted)"
            else:
                redacted_display = redacted
            click.echo(f"[INFO] Archive URL: {redacted_display}", err=True)
        service.dal.list_items(limit=0)
        click.echo("[DEBUG] Backend validation: OK", err=True)
    except (ConnectionError, TimeoutError) as validation_err:
        logger.debug(f"Exception: {validation_err}")
        sanitized = redact_text_credentials(str(validation_err)).strip()
        detail = f"{type(validation_err).__name__}" + (f": {sanitized}" if sanitized else "")
        message = f"Archive backend validation failed: {detail}"
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
        logger.debug(f"LookupError: {lookup_err}")
        message = f"Tombstone not found in archive backend: {lookup_err}"
        click.echo(f"ERROR: {message}", err=True)
        log_restore(
            logger,
            actor=actor,
            tombstone=tombstone,
            status="FAILED",
            detail=message,
            logging_config=app_config.logging,
            performance_config=app_config.performance,
        )
        click.echo(
            "DEBUG: Verify the tombstone ID and ensure the archive backend contains "
            "the recorded entry.",
            err=True,
        )
        sys.exit(1)
    except RuntimeError as runtime_err:
        logger.debug(f"RuntimeError: {runtime_err}")
        message = f"Restore failed: {runtime_err}"
        click.echo(f"ERROR: {message}", err=True)
        log_restore(
            logger,
            actor=actor,
            tombstone=tombstone,
            status="FAILED",
            detail=message,
            logging_config=app_config.logging,
            performance_config=app_config.performance,
        )
        sys.exit(1)
    except Exception as unexpected_err:  # pragma: no cover - defensive guard
        message = f"Unexpected restore error: {type(unexpected_err).__name__}: {unexpected_err}"
        click.echo(f"ERROR: {message}", err=True)
        append_evidence(
            {
                "action": "RESTORE_FAIL",
                "actor": actor,
                "tombstone": tombstone,
                "reason": f"Unexpected error: {type(unexpected_err).__name__}",
            }
        )
        log_restore(
            logger,
            actor=actor,
            tombstone=tombstone,
            status="FAILED",
            detail=message,
            logging_config=app_config.logging,
            performance_config=app_config.performance,
        )
        sys.exit(1)

    click.echo(path.as_posix())
    log_restore(
        logger,
        actor=actor,
        tombstone=tombstone,
        status="SUCCESS",
        logging_config=app_config.logging,
        performance_config=app_config.performance,
    )


@cli.command("batch-restore")
@click.argument(
    "manifest",
    type=click.Path(path_type=Path, exists=True, dir_okay=False, readable=True),
)
@click.option("--actor", required=True, help="Default actor recorded for each restore entry")
@click.option(
    "--results",
    "results_path",
    type=click.Path(path_type=Path, dir_okay=False),
    help="Optional path to write a JSON summary of the batch results.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Load and validate the manifest without executing restores",
)
@click.option(
    "--config-file",
    type=click.Path(path_type=Path, dir_okay=False, exists=True),
    help="Optional explicit configuration file path",
)
def batch_restore(
    manifest: Path,
    actor: str,
    results_path: Path | None,
    dry_run: bool,
    config_file: Path | None,
) -> None:
    """Restore multiple tombstones from a manifest."""

    app_config = _load_config(config_file)
    logger = _setup_logger(app_config)
    manifest_obj = BatchManifest.from_path(manifest, default_actor=actor)

    if dry_run:
        click.echo(json.dumps({"total": len(manifest_obj.items)}, indent=2))
        return

    service = _service(apply_schema=True, app_config=app_config)
    runner = BatchRestore(
        service,
        retry_config=app_config.retry.to_retry_config(),
        batch_config=app_config.batch,
        performance_config=app_config.performance,
        progress_callback=_batch_progress_logger(logger, app_config),
    )
    result = runner.restore(manifest_obj)

    destination: Path | None = results_path or app_config.batch.results_path
    if destination is not None:
        saved_path = runner.save_results(destination, result)
        click.echo(f"Batch results saved to {saved_path}", err=True)

    click.echo(json.dumps(result.to_dict(), indent=2))


@cli.command("prune-request")
@click.argument("tombstone")
@click.option("--by", "actor", required=True, help="Requester")
@click.option("--reason", required=True, help="Business justification")
def prune_request(tombstone: str, actor: str, reason: str) -> None:
    """Record a prune request event."""

    app_config = _load_config()
    _setup_logger(app_config)
    service = _service(apply_schema=True, app_config=app_config)
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

    app_config = _load_config()
    _setup_logger(app_config)
    service = _service(apply_schema=True, app_config=app_config)
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
@click.option("--debug", is_flag=True, help="Show sensitive diagnostics (full URLs).")
def health_check(debug: bool) -> None:
    """Verify archive backend accessibility and health."""

    app_config = _load_config()
    logger = _setup_logger(app_config)
    service = _service(apply_schema=False, app_config=app_config)
    config = service.config

    click.echo("=== Archive Health Check ===")
    click.echo(f"Backend: {config.backend.backend}")
    if debug:
        click.echo(f"URL: {config.backend.url}")
    else:
        redacted = redact_url_credentials(config.backend.url)
        display = redacted or "<not set>"
        if redacted and redacted != config.backend.url:
            display = f"{redacted} (credentials redacted)"
        click.echo(f"URL: {display}")

    try:
        items = service.dal.list_items(limit=1)
        click.echo("Status: \N{CHECK MARK} OK")
        click.echo(f"Items Retrievable: {len(items)}")
    except (IOError, OSError) as exc:  # pragma: no cover - diagnostics path
        sanitized = redact_text_credentials(str(exc)).strip()
        detail = f"{type(exc).__name__}" + (f": {sanitized}" if sanitized else "")
        click.echo(
            f"Status: \N{BALLOT X} FAILED ({detail})",
            err=True,
        )
        log_restore(
            logger,
            actor="health-check",
            tombstone="",
            status="FAILED",
            detail=detail,
            logging_config=app_config.logging,
            performance_config=app_config.performance,
        )
        sys.exit(1)
    summary = f"Status: \N{CHECK MARK} OK (backend accessible, {len(items)} items retrievable)"
    click.echo(summary)
    log_restore(
        logger,
        actor="health-check",
        tombstone="",
        status="SUCCESS",
        detail=summary,
        logging_config=app_config.logging,
        performance_config=app_config.performance,
    )


@cli.command("show-standardization-status")
def show_standardization_status() -> None:
    """Display archive standardization compliance status."""
    try:
        from .standardization import StandardizationManager

        manager = StandardizationManager(enable_signing=False)
        report = manager.get_standardization_report()

        click.echo("\n" + "=" * 60)
        click.echo("📋 Archive Standardization Status")
        click.echo("=" * 60)
        click.echo(f"Standard Version: {report['standard_version']}")
        click.echo(f"SLSA Level: {report['slsa_level']}")
        click.echo(f"Signing Enabled: {'✅ Yes' if report['signing_enabled'] else '❌ No'}")
        click.echo(f"Schema Versions Supported: {', '.join(report['schema_versions_supported'])}")
        click.echo("\nCompliance:")
        for standard, status in report["compliance"].items():
            status_icon = "✅" if status else "❌"
            click.echo(f"  {status_icon} {standard.upper()}")
        click.echo()
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        click.echo("❌ Standardization module not available", err=True)
        sys.exit(1)


@cli.command("validate-standardization")
@click.option(
    "--check-signatures",
    is_flag=True,
    help="Verify all signatures in evidence log",
)
@click.option(
    "--check-schema-version",
    is_flag=True,
    help="Verify schema version compliance",
)
@click.option(
    "--repair",
    is_flag=True,
    help="Attempt to repair schema issues (v1→v2 migration)",
)
def validate_standardization(
    check_signatures: bool,
    check_schema_version: bool,
    repair: bool,
) -> None:
    """Validate standardization compliance of archive evidence log."""
    try:
        from .evidence_schema import EvidenceSchemaValidator
        from .standardization import StandardizationManager
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        click.echo("❌ Standardization module not available", err=True)
        sys.exit(1)

    manager = StandardizationManager(enable_signing=check_signatures, verify_only=check_signatures)
    validator = EvidenceSchemaValidator()

    evidence_file = Path(".codex/evidence/archive_ops.jsonl")
    if not evidence_file.exists():
        click.echo("❌ Evidence log not found: .codex/evidence/archive_ops.jsonl", err=True)
        sys.exit(1)

    click.echo(f"📋 Validating: {evidence_file}")
    click.echo(f"   Checks: schema={check_schema_version}, signatures={check_signatures}")

    issues = []
    warnings = []
    valid_records = 0
    repaired_records = 0

    # Read evidence log
    lines = evidence_file.read_text().splitlines()
    total_records = len(lines)

    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue

        # Parse JSON
        try:
            record = json.loads(line)
        except json.JSONDecodeError as e:
            issues.append(f"Line {line_no}: Invalid JSON: {e}")
            continue

        # Detect schema version
        version = validator.auto_detect_version(record)

        # Validate schema
        if check_schema_version:
            try:
                validator.validate(record, version=version)
                valid_records += 1
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                if repair and version == "1.0":
                    try:
                        validator.migrate_to_v2(record)
                        valid_records += 1
                        repaired_records += 1
                    except (ValueError, TypeError, RuntimeError) as repair_err:
                        logger.debug(f"Exception: {repair_err}")
                        issues.append(
                            f"Line {line_no}: Schema error: {e} (repair failed: {repair_err})"
                        )
                else:
                    issues.append(f"Line {line_no}: Schema error: {e}")

        # Verify signatures
        if check_signatures and version == "2.0":
            metadata = record.get("standardizationMetadata", {})
            if metadata.get("signature"):
                try:
                    sig_valid = manager.verify_standardization(record)
                    if not sig_valid["valid"]:
                        warnings.append(f"Line {line_no}: Signature verification failed")
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    warnings.append(f"Line {line_no}: Could not verify signature: {e}")

    # Report results
    click.echo("\n" + "=" * 60)
    click.echo(f"📊 Validation Results: {total_records} records scanned")
    click.echo(f"   ✅ Valid: {valid_records}")
    click.echo(f"   ⚠️  Warnings: {len(warnings)}")
    click.echo(f"   ❌ Errors: {len(issues)}")
    if repair:
        click.echo(f"   🔧 Repaired: {repaired_records}")

    if warnings:
        click.echo("\n⚠️  Warnings:")
        for w in warnings[:10]:  # Show first 10
            click.echo(f"   {w}")

    if issues:
        click.echo("\n❌ Errors:")
        for issue in issues[:10]:  # Show first 10
            click.echo(f"   {issue}")
        if len(issues) > 10:
            click.echo(f"   ... and {len(issues) - 10} more")
        sys.exit(1)
    else:
        click.echo("\n✅ All checks passed!")


@cli.command("migrate-evidence-to-v2")
@click.confirmation_option(
    prompt="⚠️  This will modify .codex/evidence/archive_ops.jsonl. Continue?",
)
def migrate_evidence_to_v2() -> None:
    """Migrate evidence log from v1 to v2 schema (optional, non-breaking)."""
    try:
        from .evidence_schema import EvidenceSchemaValidator
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        click.echo("❌ Standardization module not available", err=True)
        sys.exit(1)

    validator = EvidenceSchemaValidator()
    evidence_file = Path(".codex/evidence/archive_ops.jsonl")

    if not evidence_file.exists():
        click.echo("❌ Evidence log not found", err=True)
        sys.exit(1)

    click.echo("🔄 Starting migration v1 → v2...")

    migrated_records = []
    errors = []

    for line_no, line in enumerate(evidence_file.read_text().splitlines(), 1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
            version = validator.auto_detect_version(record)

            if version == "1.0":
                migrated = validator.migrate_to_v2(record)
                migrated_records.append(migrated)
            else:
                migrated_records.append(record)  # Already v2
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            errors.append(f"Line {line_no}: {e}")

    if errors:
        click.echo("❌ Errors during migration:")
        for err in errors:
            click.echo(f"   {err}")
        sys.exit(1)

    # Backup original
    backup_file = evidence_file.with_suffix(".jsonl.backup")
    evidence_file.rename(backup_file)
    click.echo(f"📦 Backed up original to: {backup_file}")

    # Write migrated log
    with evidence_file.open("w") as f:
        for record in migrated_records:
            f.write(json.dumps(record, sort_keys=True) + "\n")

    v1_count = sum(1 for r in migrated_records if validator.auto_detect_version(r) == "1.0")
    v2_count = sum(1 for r in migrated_records if validator.auto_detect_version(r) == "2.0")

    click.echo(f"✅ Migration complete: {len(migrated_records)} records converted")
    click.echo(f"   v1 records: {v1_count}")
    click.echo(f"   v2 records: {v2_count}")
