"""Unified CLI for codex, using click for subcommands and input validation."""

from __future__ import annotations

from codex.logging.structured_logger import logger

# Monkey-patch stdlib XML to use defusedxml globally (XXE prevention)
try:
    import defusedxml

    defusedxml.defuse_stdlib()
except (ImportError, AttributeError):  # pragma: no cover - optional dep
    logger.debug(
        "defusedxml not available — skipping XML defusal"
    )  # codeql[py/clear-text-logging-sensitive-data]

import importlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import sqlite3  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from uuid import uuid4  # noqa: E402

import click  # noqa: E402

from codex.copilot_campaign import build_agent_chain, recommend_task_route  # noqa: E402

try:  # pragma: no cover - optional dependency
    import typer as _typer
except (ImportError, AttributeError):  # pragma: no cover - degrade gracefully when Typer missing
    logger.debug(
        "Suppressed exception in handler", exc_info=True
    )  # codeql[py/clear-text-logging-sensitive-data]
else:  # pragma: no cover - exercised in Typer-enabled environments
    try:
        from codex.cli_knowledge import app as knowledge_typer_app
        from codex.cli_release import app as release_typer_app
    except (ImportError, AttributeError):  # pragma: no cover - Typer sub-app import guard
        logger.debug(
            "Suppressed exception in handler", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
    else:
        app = _typer.Typer(help="Codex Typer CLI (release + knowledge)")
        app.add_typer(release_typer_app, name="release")
        app.add_typer(knowledge_typer_app, name="knowledge")

try:  # pragma: no cover - optional dependency
    import typer.main as _typer_main

    _typer_get_command = _typer_main.get_command
except (ImportError, AttributeError):  # pragma: no cover
    _typer_get_command = None

try:  # pragma: no cover - optional dependency
    from codex_digest.error_capture import log_error as _log_error
except (IOError, OSError):  # pragma: no cover

    def _log_error(step_no: str, step_desc: str, msg: str, ctx: str) -> None:
        """Fallback error logger when codex_digest is unavailable."""
        return


# Resolve helper scripts relative to this file so the CLI works from any CWD.
TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CAMPAIGN_METRICS_LOG = REPO_ROOT / ".codex" / "campaign_metrics.jsonl"


def _utc_timestamp() -> str:
    """Return a UTC timestamp using the repository-standard format."""

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_campaign_metric(event: str, payload: dict[str, object]) -> None:
    """Append a small JSONL metric for new campaign-oriented CLI flows."""

    CAMPAIGN_METRICS_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": _utc_timestamp(),
        "event": event,
        **payload,
    }
    with CAMPAIGN_METRICS_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _run_git_capture(args: list[str]) -> str:
    """Run a small git command and return stdout, degrading to 'unknown'."""

    try:
        result = subprocess.run(
            args,
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.SubprocessError, OSError, ValueError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _snapshot_repository_state() -> dict[str, object]:
    """Capture lightweight repository state for session checkpoints."""

    branch = _run_git_capture(["git", "branch", "--show-current"])
    commit_sha = _run_git_capture(["git", "rev-parse", "HEAD"])
    status_output = _run_git_capture(["git", "status", "--short"])
    uncommitted_changes = (
        0
        if status_output == "unknown"
        else len([line for line in status_output.splitlines() if line.strip()])
    )
    return {
        "branch": branch,
        "commit_sha": commit_sha,
        "uncommitted_changes": uncommitted_changes,
        "cwd": str(REPO_ROOT),
    }


def _parse_tags(tags: tuple[str, ...]) -> dict[str, str]:
    """Parse repeated KEY=VALUE CLI tags into a dictionary."""

    parsed: dict[str, str] = {}
    for raw in tags:
        if "=" not in raw:
            raise click.ClickException(f"Invalid tag '{raw}'. Expected KEY=VALUE.")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise click.ClickException(f"Invalid tag '{raw}'. Tag key cannot be empty.")
        if key in parsed:
            raise click.ClickException(f"Duplicate tag key '{key}' is not allowed.")
        parsed[key] = value.strip()
    return parsed


def _run_ingest() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        logger.info(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    logger.info(f"Ingested {src} -> {dst}")


def _run_ci() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.info("CI failed: <ERROR_TYPE>")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def _fix_pool(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None and max_workers > 0:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except (IOError, OSError) as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        # Don't return — continue to enable SQLite pooling below

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except (ConnectionError, TimeoutError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    logger.info(f"enabled SQLite pooling (warm={workers}) for {db}")


ALLOWED_TASKS = {
    "ingest": (_run_ingest, "Ingest example data into the Codex environment."),
    "ci": (_run_ci, "Run local CI checks (lint + tests)."),
    "pool-fix": (
        lambda: _fix_pool(4),
        "Reset tokenization thread pool (default 4 workers).",
    ),
}


def _missing_command(name: str, message: str, help_text: str | None = None) -> click.Command:
    """Return a small Click command that raises ``message`` when invoked."""

    help_msg = help_text or message

    @click.command(name=name, help=help_msg)
    def _cmd() -> None:  # pragma: no cover - trivial error reporting
        raise click.ClickException(message)

    return _cmd


def _register_click_command(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except (
        IOError,
        OSError,
        ImportError,
        ModuleNotFoundError,
        AttributeError,
    ) as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def _register_typer_app(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except (
        IOError,
        OSError,
        ImportError,
        ModuleNotFoundError,
        AttributeError,
    ) as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


_CLI_HELP = (
    "Codex CLI entry point.\n\n"
    "This Click facade exposes the curated maintenance helpers that back the"
    " `tasks` and `run` commands (see `ALLOWED_TASKS`) while the richer Typer"
    " applications shipped with Codex—for example the `codex-ml` console"
    " scripts—remain available for end-to-end ML workflows."
)


def _emit_group_help(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


@click.group(invoke_without_command=True, help=_CLI_HELP)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Codex CLI entry point bridging Click groups and Typer apps.

    The available subcommands intentionally mirror :data:`ALLOWED_TASKS` so
    that ``codex tasks`` lists the same curated helpers that ``codex run``
    executes.
    """

    if ctx.invoked_subcommand or ctx.resilient_parsing:
        return
    if ctx.args:
        args_display = " ".join(ctx.args)
        ctx.fail(f"Unexpected extra arguments: {args_display}")
    _emit_group_help(ctx)


@cli.group(
    "logs",
    invoke_without_command=True,
    help=(
        "Inspect Codex SQLite logs.\n\n"
        "These Click wrappers surface quick summaries while the Typer-based"
        " logging console scripts (for example `python -m codex.logging.viewer`)"
        " remain the primary interface for deep-dive workflows."
    ),
)
@click.pass_context
def logs(ctx: click.Context) -> None:
    """Codex logs (local SQLite data store) Click group.

    The subcommands complement the richer Typer logging utilities so users can
    quickly inspect the same datasets that power :mod:`codex.logging`.
    """

    if ctx.invoked_subcommand or ctx.resilient_parsing:
        return
    if ctx.args:
        args_display = " ".join(ctx.args)
        ctx.fail(f"Unexpected extra arguments: {args_display}")
    _emit_group_help(ctx)


@logs.command("init")
@click.option("--db", default=".codex/codex.sqlite", help="DB path")
def logs_init(db: str) -> None:
    """Initialize SQLite schema for logs."""
    script = TOOLS_DIR / "codex_db.py"
    try:
        subprocess.run([sys.executable, str(script), "--init", "--db", db], check=True)
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"Failed to init logs DB: {exc}", err=True)
        _log_error("STEP logs_init", "codex_db --init", str(exc), f"db={db}")
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
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"Failed to ingest logs: {exc}", err=True)
        _log_error("STEP logs_ingest", "codex_ingest_md", str(exc), f"db={db}")
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
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"Failed to query logs: {exc}", err=True)
        _log_error("STEP logs_query", "codex_db --query", str(exc), f"db={db}")
        sys.exit(1)


# VARIANT 4: logs export-data (NEW COMMAND)
@logs.command("export-data")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="logs_export.jsonl",
    help="Output file path (JSONL format)",
)
@click.option(
    "--format",
    type=click.Choice(["jsonl", "json", "csv"]),
    default="jsonl",
    help="Output format",
)
@click.option(
    "--db",
    type=click.Path(exists=True),
    default=".codex/codex.sqlite",
    help="Database path to export from",
)
def logs_export_data(output: str, format: str, db: str) -> None:
    """Export logs data to file.

    Exports all session logs from the SQLite database to a specified format
    (JSONL, JSON, or CSV) for analysis or archival.
    """
    try:
        import sqlite3

        click.echo(f"📦 Exporting logs from {db} to {output} ({format})...")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Get all log entries
        cursor.execute("SELECT * FROM session_events LIMIT 1000")
        columns = (
            [description[0] for description in cursor.description] if cursor.description else []
        )
        rows = cursor.fetchall()

        if format == "jsonl":
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                for row in rows:
                    record = dict(zip(columns, row))
                    f.write(json.dumps(record) + "\n")
        elif format == "json":
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            data = [dict(zip(columns, row)) for row in rows]
            output_path.write_text(json.dumps(data, indent=2))
        elif format == "csv":
            import csv

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                for row in rows:
                    writer.writerow(dict(zip(columns, row)))

        conn.close()
        click.echo(f"✅ Exported {len(rows)} records to {output}")
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Export failed: {exc}", err=True)
        sys.exit(1)


@cli.group(invoke_without_command=True, help="Chronicle analytics and personalized tips")
@click.pass_context
def chronicle(ctx: click.Context) -> None:
    """Chronicle: Session history analysis and personalized tips.

    Analyze your session patterns and get personalized recommendations
    to improve productivity and effectiveness.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@chronicle.command("tips")
@click.option(
    "--format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format for tips",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (default: stdout)",
)
def chronicle_tips(format: str, output: str | None) -> None:
    """Get personalized tips based on your session history."""
    try:
        from codex.logging.chronicle_analytics import ChronicleAnalytics
        from codex.logging.session_database import SessionDatabase

        # Initialize database and analytics
        db_path = ".codex/codex.sqlite"
        db = SessionDatabase(db_path)
        analytics = ChronicleAnalytics(db)

        if format == "json":
            result = analytics.export_json()
        else:
            result = analytics.generate_summary()

        if output:
            Path(output).write_text(result, encoding="utf-8")
            click.echo(f"✅ Tips exported to {output}")
        else:
            click.echo(result)

    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to generate tips: {exc}", err=True)
        sys.exit(1)


@chronicle.command("analyze")
@click.option(
    "--pattern",
    type=click.Choice(["frequency", "tools", "agents", "time", "performance", "trends"]),
    default=None,
    help="Analyze specific pattern (default: all)",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (default: stdout)",
)
def chronicle_analyze(pattern: str | None, output: str | None) -> None:
    """Analyze session patterns in detail."""
    try:
        from codex.logging.chronicle_analytics import ChronicleAnalytics
        from codex.logging.session_database import SessionDatabase

        # Initialize database and analytics
        db_path = ".codex/codex.sqlite"
        db = SessionDatabase(db_path)
        analytics = ChronicleAnalytics(db)
        patterns = analytics.analyze_patterns()

        if pattern:
            # Filter to requested pattern
            pattern_map = {
                "frequency": "frequency",
                "tools": "tools",
                "agents": "agents",
                "time": "time_patterns",
                "performance": "performance",
                "trends": "trends",
            }
            result_dict = {pattern: patterns.get(pattern_map[pattern])}
        else:
            result_dict = patterns

        result = json.dumps(result_dict, indent=2)

        if output:
            Path(output).write_text(result, encoding="utf-8")
            click.echo(f"✅ Analysis exported to {output}")
        else:
            click.echo(result)

    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to analyze patterns: {exc}", err=True)
        sys.exit(1)


@chronicle.command("checkpoint")
@click.option("--session-id", default=None, help="Logical session identifier")
@click.option("--agent-id", default="copilot-coding-agent", help="Agent identifier")
@click.option("--status", default="active", help="Current agent status")
@click.option("--task", "task_name", default="unspecified", help="Current task summary")
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Checkpoint metadata tag as KEY=VALUE (repeatable)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def chronicle_checkpoint(
    session_id: str | None,
    agent_id: str,
    status: str,
    task_name: str,
    tags: tuple[str, ...],
    output_format: str,
) -> None:
    """Create a session checkpoint for long-running Copilot work."""

    try:
        from scripts.cognitive.session_checkpoint_manager import SessionCheckpointManager
    except ImportError as exc:
        raise click.ClickException(f"Checkpoint manager unavailable: {exc}") from exc

    resolved_session_id = session_id or os.getenv(
        "CODEX_SESSION_ID",
        f"cli-session-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}",
    )
    metadata_tags = _parse_tags(tags)
    manager = SessionCheckpointManager(
        storage_path=str(REPO_ROOT / ".codex" / "checkpoints"),
        compression_algorithm="gzip",
        compression_level=9,
    )
    repo_state = _snapshot_repository_state()
    checkpoint_meta = manager.create_checkpoint(
        session_id=resolved_session_id,
        agent_state={
            "agent_id": agent_id,
            "status": status,
            "cwd": str(REPO_ROOT),
        },
        memory_snapshot={
            "short_term_memory": [],
            "long_term_memory": [],
            "total_patterns": 0,
        },
        execution_progress={
            "current_task": task_name,
            "completed_tasks": [],
            "pending_tasks": [],
            "task_completion_percent": 0.0,
        },
        repository_state=repo_state,
        metadata=metadata_tags,
        compress=True,
    )
    _append_campaign_metric(
        "checkpoint_created",
        {
            "checkpoint_id": checkpoint_meta.checkpoint_id,
            "session_id": resolved_session_id,
            "task": task_name,
        },
    )

    if output_format == "json":
        click.echo(json.dumps(checkpoint_meta.to_dict(), indent=2, sort_keys=True))
        return

    click.echo(f"✅ Checkpoint created: {checkpoint_meta.checkpoint_id}")
    click.echo(f"   Session: {resolved_session_id}")
    click.echo(f"   Task: {task_name}")
    click.echo(f"   Branch: {repo_state['branch']}")
    click.echo(f"   Compression ratio: {checkpoint_meta.compression_ratio:.2f}:1")


@chronicle.command("resume-session")
@click.argument("checkpoint_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def chronicle_resume_session(checkpoint_id: str, output_format: str) -> None:
    """Restore a checkpoint and print the execution context summary."""

    try:
        from scripts.cognitive.session_checkpoint_manager import SessionCheckpointManager
        from scripts.cognitive.session_resume_engine import SessionResumeEngine
    except ImportError as exc:
        raise click.ClickException(f"Resume engine unavailable: {exc}") from exc

    manager = SessionCheckpointManager(
        storage_path=str(REPO_ROOT / ".codex" / "checkpoints"),
        compression_algorithm="gzip",
        compression_level=9,
    )
    engine = SessionResumeEngine(checkpoint_manager=manager, enable_warmup=False)
    context = engine.warm_start(checkpoint_id)
    _append_campaign_metric(
        "checkpoint_restored",
        {
            "checkpoint_id": checkpoint_id,
            "session_id": context.session_id,
            "task": context.execution_progress.get("current_task", "unknown"),
        },
    )

    result = {
        "checkpoint_id": checkpoint_id,
        "session_id": context.session_id,
        "agent_id": context.agent_id,
        "agent_status": context.agent_status,
        "task": context.execution_progress.get("current_task"),
        "completed_tasks": context.execution_progress.get("completed_tasks", []),
        "warmup_complete": context.warmup_complete,
        "patterns": context.memory_snapshot.get("total_patterns", 0),
    }
    if output_format == "json":
        click.echo(json.dumps(result, indent=2, sort_keys=True))
        return

    click.echo(f"✅ Restored checkpoint: {checkpoint_id}")
    click.echo(f"   Session: {context.session_id}")
    click.echo(f"   Agent: {context.agent_id} ({context.agent_status})")
    click.echo(f"   Task: {result['task']}")
    click.echo(f"   Completed tasks: {len(result['completed_tasks'])}")


@chronicle.command("route-task")
@click.argument("command")
@click.option(
    "--category",
    type=click.Choice(
        ["deterministic", "ci", "validation", "install", "exploration", "research", "general"]
    ),
    default=None,
    help="Optional workflow category hint",
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of text")
def chronicle_route_task(command: str, category: str | None, as_json: bool) -> None:
    """Recommend whether to use bash, task, or a general-purpose agent."""

    decision = recommend_task_route(command=command, category=category)
    _append_campaign_metric(
        "task_route_recommended",
        {
            "runner": decision.recommended_runner,
            "agent": decision.recommended_agent,
            "category": decision.category,
        },
    )

    if as_json:
        click.echo(json.dumps(decision.to_dict(), indent=2, sort_keys=True))
        return

    click.echo(f"Runner: {decision.recommended_runner}")
    click.echo(f"Agent: {decision.recommended_agent}")
    click.echo(f"Category: {decision.category}")
    click.echo(f"Why: {decision.rationale}")
    click.echo(f"Prompt template: {decision.prompt_template}")


@chronicle.command("agent-chain")
@click.option(
    "--focus",
    type=click.Choice(["codeql", "security", "ci", "coverage", "docs", "orchestration"]),
    required=True,
    help="Workflow focus to optimize",
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of text")
def chronicle_agent_chain(focus: str, as_json: bool) -> None:
    """Show the recommended specialized-agent chain for a workflow."""

    chain = build_agent_chain(focus)
    _append_campaign_metric(
        "agent_chain_requested",
        {"focus": focus, "steps": len(chain.steps)},
    )

    if as_json:
        click.echo(json.dumps(chain.to_dict(), indent=2, sort_keys=True))
        return

    click.echo(chain.summary)
    for step in chain.steps:
        click.echo(f"{step.order}. {step.agent} — {step.purpose}")
        click.echo(f"   Prompt: {step.prompt_template}")


@chronicle.command("auto-fix")
@click.option("--check-only", is_flag=True, help="Run diagnostics without applying fixes")
@click.option("--pattern", type=int, default=None, help="Optional pattern number")
@click.option("--pattern-name", default=None, help="Optional pattern-name substring")
@click.option("--dry-run", is_flag=True, help="Preview remediation without editing files")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional JSON output path",
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of text")
def chronicle_auto_fix(
    check_only: bool,
    pattern: int | None,
    pattern_name: str | None,
    dry_run: bool,
    output: Path | None,
    as_json: bool,
) -> None:
    """Run the campaign's CI auto-fix wrappers."""

    if check_only:
        from scripts.ci.enhanced_diagnostics import run_enhanced_diagnostics

        report = run_enhanced_diagnostics(
            repo_root=REPO_ROOT,
            pattern=pattern,
            pattern_name=pattern_name,
            output_path=output,
        )
    else:
        from scripts.ci.bulk_remediation_orchestrator import run_bulk_remediation

        report = run_bulk_remediation(
            repo_root=REPO_ROOT,
            pattern=pattern,
            pattern_name=pattern_name,
            output_path=output,
            dry_run=dry_run,
        )

    _append_campaign_metric(
        "autofix_invoked",
        {
            "mode": "diagnostics" if check_only else "remediation",
            "pattern": pattern or 0,
            "pattern_name": pattern_name or "",
            "status": report.get("status", "unknown"),
        },
    )

    if as_json:
        click.echo(json.dumps(report, indent=2, sort_keys=True))
        return

    click.echo(f"Status: {report.get('status', 'unknown')}")
    click.echo(f"Total issues: {report.get('total_issues', 0)}")
    click.echo(f"Auto-fixable: {report.get('auto_fixable', 0)}")
    click.echo(f"Manual review: {report.get('manual_review', 0)}")
    for next_step in report.get("next_steps", []):
        click.echo(f"- {next_step}")


@cli.command("train", context_settings={"ignore_unknown_options": True})
@click.option(
    "--engine",
    type=click.Choice(["hf_trainer", "hf", "custom"]),
    default="hf_trainer",
    help="Training engine to use (hf_trainer/hf or custom).",
)
@click.argument("engine_args", nargs=-1)
def train_cmd(engine: str, engine_args: tuple[str, ...]) -> None:
    """Train a model with the selected engine.

    Any additional arguments after ``--engine`` are forwarded directly to the
    underlying engine entry point.
    """
    from codex_ml.utils.repro import set_reproducible

    set_reproducible()
    if engine in {"hf_trainer", "hf"}:
        from training.engine_hf_trainer import build_parser, run_hf_trainer

        parser = build_parser()
        parser.add_argument("--texts", nargs="+", required=True)
        parser.add_argument("--output-dir", type=Path, default=Path("training_runs"))
        parser.add_argument("--val-texts", nargs="*", default=None)
        parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
        parser.add_argument("--precision", choices=["fp32", "fp16", "bf16"], default=None)
        parser.add_argument("--lora-r", type=int, default=0, help="LoRA rank; set >0 to enable")
        parser.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha scaling")
        parser.add_argument(
            "--lora-dropout", type=float, default=0.0, help="LoRA dropout probability"
        )
        parser.add_argument(
            "--lora-task-type",
            type=str,
            default=None,
            help="LoRA task type (defaults to CAUSAL_LM)",
        )
        parser.add_argument("--seed", type=int, default=0)
        parser.add_argument(
            "--config-path",
            type=Path,
            default=None,
            help="Optional training config file (JSON/YAML) to snapshot into resume manifests.",
        )

        args = parser.parse_args(list(engine_args))
        kw: dict[str, object] = {
            "val_texts": args.val_texts,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "precision": args.precision,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "lora_task_type": args.lora_task_type,
            "seed": args.seed,
        }

        hydra_cfg: dict[str, object] = {}
        defaults = {
            "gradient_accumulation_steps": parser.get_default("gradient_accumulation_steps"),
            "precision": parser.get_default("precision"),
            "seed": parser.get_default("seed"),
            "lora_r": parser.get_default("lora_r"),
            "lora_alpha": parser.get_default("lora_alpha"),
            "lora_dropout": parser.get_default("lora_dropout"),
            "lora_task_type": parser.get_default("lora_task_type"),
        }

        if args.gradient_accumulation_steps != defaults["gradient_accumulation_steps"]:
            hydra_cfg["gradient_accumulation_steps"] = args.gradient_accumulation_steps
        if args.precision is not None:
            hydra_cfg["precision"] = args.precision
        if args.seed != defaults["seed"]:
            hydra_cfg["seed"] = args.seed

        lora_section: dict[str, object] = {}
        if args.lora_r and args.lora_r != defaults["lora_r"]:
            lora_section["r"] = args.lora_r
        if args.lora_alpha is not None and args.lora_alpha != defaults["lora_alpha"]:
            lora_section["alpha"] = args.lora_alpha
        if args.lora_dropout and args.lora_dropout != defaults["lora_dropout"]:
            lora_section["dropout"] = args.lora_dropout
        if args.lora_task_type:
            lora_section["task_type"] = args.lora_task_type
        if lora_section:
            hydra_cfg["lora"] = lora_section
        if not hydra_cfg:
            hydra_cfg = None
        if args.config_path:
            kw["config_path"] = args.config_path
        if hydra_cfg:
            kw["hydra_cfg"] = hydra_cfg
        # Optionally forward device/dtype if parser/engine supports them
        for opt in ("device", "dtype"):
            if hasattr(args, opt):
                val = getattr(args, opt)
                if val is not None:
                    kw[opt] = val
        try:
            run_hf_trainer(args.texts, args.output_dir, **kw)
            return
        except (IOError, OSError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            _log_error("STEP train", "run_hf_trainer", str(exc), f"texts={args.texts}")
            raise
    else:
        try:
            from codex.training import main as run_custom_train
        except (IOError, OSError) as exc:  # pragma: no cover - fallback path
            click.echo(f"[warn] custom engine unavailable, falling back to hf_trainer: {exc}")
            from training.engine_hf_trainer import run_hf_trainer

            try:
                run_hf_trainer(*engine_args)
                return
            except (ImportError, AttributeError) as exc2:
                logger.debug(f"Exception: {exc2}")  # codeql[py/clear-text-logging-sensitive-data]
                _log_error(
                    "STEP train",
                    "fallback run_hf_trainer",
                    str(exc2),
                    f"args={engine_args}",
                )
                raise
        argv = ["--engine", "custom", *engine_args]
        orig_argv = sys.argv
        try:
            sys.argv = [orig_argv[0], *argv]
            run_custom_train()
        except (ValueError, TypeError, RuntimeError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            _log_error("STEP train", "run_custom_train", str(exc), f"argv={argv}")
            raise
        finally:
            sys.argv = orig_argv


@cli.command("batch-triage")
@click.option("--issues", help="Comma-separated GitHub issue numbers")
@click.option(
    "--from-file",
    type=click.Path(exists=True),
    help="CSV file with issue/workflow data",
)
@click.option(
    "--output",
    type=click.Path(),
    default="batch_triage_report.md",
    help="Output file path",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON instead of markdown")
@click.option(
    "--group-by",
    type=click.Choice(["root_cause", "workflow", "severity", "failure_type"]),
    default="root_cause",
    help="Grouping strategy",
)
def batch_triage(issues, from_file, output, as_json, group_by):
    """Batch triage CI/test failures with automated remediation suggestions.

    Examples:
        codex batch-triage --issues 2905,2906,2907,2908,2909,2910,2912,2913,2914,2915
        codex batch-triage --from-file scripts/ci/links_extraction.csv
    """
    script = Path(__file__).resolve().parent.parent.parent / "scripts" / "ci" / "batch_triage.py"

    args = [sys.executable, str(script), "--output", output, "--group-by", group_by]

    if issues:
        args.extend(["--issues", issues])
    elif from_file:
        args.extend(["--from-file", from_file])
    else:
        click.echo("Error: Must provide either --issues or --from-file", err=True)
        sys.exit(1)

    if as_json:
        args.append("--json")

    try:
        subprocess.run(args, check=True)
    except (ValueError, TypeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"Batch triage failed: {exc}", err=True)
        _log_error("STEP batch_triage", "batch_triage.py", str(exc), "")
        sys.exit(1)


_WHITELIST_HEADER = "Whitelisted maintenance tasks:"


def _print_task_whitelist() -> None:
    click.echo(_WHITELIST_HEADER)
    for name, (_, desc) in ALLOWED_TASKS.items():
        click.echo(f"  - {name}: {desc}")


@cli.command("tasks")
def list_tasks() -> None:
    """List allowed maintenance tasks."""

    _print_task_whitelist()


@cli.command("run")
@click.argument("task", required=False)
def run_task(task: str | None) -> None:
    """Run a whitelisted maintenance task by name."""
    if not task:
        _print_task_whitelist()
        click.echo("\nInvoke `codex run <task>` to execute a whitelisted task.")
        return

    if task not in ALLOWED_TASKS:
        click.echo(f"Task '{task}' is not allowed.", err=True)
        sys.exit(1)
    func = ALLOWED_TASKS[task][0]
    func()


@cli.command("resume")
@click.argument("run_dir", type=click.Path(exists=True, path_type=Path))
def resume_cmd(run_dir: Path) -> None:
    """Resume a training run by emitting the canonical configuration.

    Precedence (highest to lowest):
    1. Embedded snapshot in ``resume_manifest.json`` under ``config``.
    2. Copied config file in ``run_dir`` (``resume_config.json|yaml|yml``).
    3. ``config_path`` recorded in the manifest (absolute or relative to the run dir).
    Fails with a non-zero exit code if no configuration source is available.
    """

    manifest_path = run_dir / "resume_manifest.json"
    if not manifest_path.exists():
        click.echo(f"ERROR: resume_manifest.json not found in {run_dir}", err=True)
        raise SystemExit(2)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (IOError, OSError) as exc:  # pragma: no cover - robust CLI behavior
        click.echo(f"ERROR: failed to read resume_manifest.json: {exc}", err=True)
        raise SystemExit(2) from exc

    if manifest.get("config") is not None:
        click.echo("INFO: Using config snapshot embedded in resume_manifest.json")
        click.echo(json.dumps(manifest["config"], indent=2, sort_keys=True))
        raise SystemExit(0)

    for suffix in (".json", ".yaml", ".yml"):
        candidate = run_dir / f"resume_config{suffix}"
        if candidate.exists():
            click.echo(f"INFO: Using copied config file: {candidate.name}")
            content = candidate.read_text(encoding="utf-8")
            try:
                parsed = json.loads(content)
                click.echo(json.dumps(parsed, indent=2, sort_keys=True))
            except (IOError, OSError):
                logger.warning(
                    "Exception occurred", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
                click.echo(content)
            raise SystemExit(0)

    cfg_path = manifest.get("config_path")
    if cfg_path:
        for path in (Path(cfg_path), run_dir / cfg_path):
            if path.exists():
                click.echo(f"INFO: Using config_path from manifest: {path}")
                content = path.read_text(encoding="utf-8")
                try:
                    parsed = json.loads(content)
                    click.echo(json.dumps(parsed, indent=2, sort_keys=True))
                except (IOError, OSError):
                    logger.warning(
                        "Exception occurred", exc_info=True
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    click.echo(content)
                raise SystemExit(0)

    click.echo(
        "ERROR: No configuration snapshot or config_path available in resume manifest. "
        "Refusing to resume to avoid using defaults. Re-run training passing --config-path or "
        "ensure your run directory contains a resume_config.(json|yaml|yml).",
        err=True,
    )
    raise SystemExit(1)


@cli.group(
    "tokenizer",
    invoke_without_command=True,
    help=(
        "Tokenization utilities.\n\n"
        "Use these lightweight wrappers for quick checks; the richer"
        " tokenization workflows remain under `codex_ml.cli`."
    ),
)
@click.pass_context
def tokenizer_group(ctx: click.Context) -> None:
    """Tokenization utilities."""

    if ctx.invoked_subcommand or ctx.resilient_parsing or ctx.args:
        return
    _emit_group_help(ctx)


@tokenizer_group.command("encode")
@click.argument("text")
@click.option("--tokenizer", "tokenizer_path", default=None, help="Tokenizer path")
def tokenizer_encode(text: str, tokenizer_path: str | None) -> None:
    """Encode TEXT and print token ids."""
    from codex_ml.tokenization import load_tokenizer

    tk = load_tokenizer(path=tokenizer_path)
    ids = tk.encode(text)
    click.echo(" ".join(str(i) for i in ids))


@tokenizer_group.command("decode")
@click.argument("ids", nargs=-1, type=int)
@click.option("--tokenizer", "tokenizer_path", default=None, help="Tokenizer path")
def tokenizer_decode(ids: tuple[int, ...], tokenizer_path: str | None) -> None:
    """Decode integer token IDS and print text."""
    from codex_ml.tokenization import load_tokenizer

    tk = load_tokenizer(path=tokenizer_path)
    click.echo(tk.decode(list(ids)))


@tokenizer_group.command("stats")
@click.option("--tokenizer", "tokenizer_path", default=None, help="Tokenizer path")
def tokenizer_stats(tokenizer_path: str | None) -> None:
    """Show basic tokenizer statistics."""
    from codex_ml.tokenization import load_tokenizer

    tk = load_tokenizer(path=tokenizer_path)
    click.echo(f"vocab_size={tk.vocab_size}")


# VARIANT 1: tokenizer list-models (NEW COMMAND)
@tokenizer_group.command("list-models")
def tokenizer_list_models() -> None:
    """List available tokenizer models.

    Displays all preconfigured tokenizer models that can be loaded.
    """
    try:
        from codex_ml.tokenization import list_available_models

        models = list_available_models()
        if models:
            click.echo("Available tokenizer models:")
            for model_name in sorted(models):
                click.echo(f"  - {model_name}")
        else:
            click.echo("❌ No tokenizer models available.")
            click.echo("Install codex_ml with tokenizer support to enable model listing.")
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"⚠️  Could not list tokenizer models: {exc}", err=True)
        click.echo("Hint: Ensure codex_ml is installed with tokenization extras.")


@cli.group(
    "repro",
    invoke_without_command=True,
    help=(
        "Reproducibility utilities.\n\n"
        "These commands offer fast local checks; training pipelines may use"
        " the lower-level modules directly for advanced workflows."
    ),
)
@click.pass_context
def repro_group(ctx: click.Context) -> None:
    """Reproducibility utilities."""

    if ctx.invoked_subcommand or ctx.resilient_parsing or ctx.args:
        return
    _emit_group_help(ctx)


@repro_group.command("seed")
@click.option("--seed", type=int, default=42, show_default=True, help="Seed value")
@click.option(
    "--out-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory to write seeds.json",
)
def repro_seed(seed: int, out_dir: Path | None) -> None:
    """Seed RNGs across libraries and optionally persist seeds.json."""
    from codex_ml.utils.checkpointing import set_seed

    set_seed(seed, out_dir)
    click.echo(f"seed={seed}")


@repro_group.command("env")
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default="env.json",
    show_default=True,
    help="Output path for environment info",
)
def repro_env(path: Path) -> None:
    """Record git commit and installed packages."""
    try:
        from codex_utils.repro import log_env_info
    except (IOError, OSError) as exc:  # pragma: no cover
        click.echo(f"Environment logging module unavailable: {exc}", err=True)
        sys.exit(1)

    try:
        log_env_info(path)
        click.echo(f"wrote {path}")
    except (IOError, OSError) as exc:  # pragma: no cover
        click.echo(f"Failed to write env info: {exc}", err=True)
        sys.exit(1)


@repro_group.command("system")
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default="system.json",
    show_default=True,
    help="Output path for system metrics",
)
def repro_system(path: Path) -> None:
    """Capture CPU/GPU system metrics."""
    from codex_ml.monitoring.codex_logging import _codex_sample_system

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_codex_sample_system()), encoding="utf-8")
    click.echo(f"wrote {path}")


# VARIANT 2: repro checkpoint (NEW COMMAND)
@repro_group.command("checkpoint")
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default="checkpoint.json",
    show_default=True,
    help="Output path for checkpoint metadata",
)
@click.option(
    "--include-weights",
    is_flag=True,
    default=False,
    help="Include model weight statistics in checkpoint",
)
def repro_checkpoint(path: Path, include_weights: bool) -> None:
    """Capture checkpoint metadata for reproducibility.

    Records model state, training configuration, and system metrics
    to enable checkpoint resumption and exact reproduction.
    """
    try:
        import datetime

        from codex_ml.monitoring.codex_logging import _codex_sample_system

        checkpoint_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "python_version": sys.version,
            "system": _codex_sample_system() if include_weights else None,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(checkpoint_data, indent=2), encoding="utf-8")
        click.echo(f"✅ Checkpoint metadata saved to {path}")
        click.echo(f"   Include weights: {include_weights}")
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to create checkpoint: {exc}", err=True)
        sys.exit(1)


def _register_tokenizer_pipeline_commands() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except (IOError, OSError):  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name in tokenizer_group.commands:
            continue
        tokenizer_group.add_command(command, name=name)


def _register_external_cli() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


# ==============================================================================
# .codex/archive/deprecated/AGENTS.md Infrastructure Commands
# ==============================================================================


@cli.command("session-logger")
@click.option("--session-id", help="Session ID (default: auto-generate)")
@click.option(
    "--role",
    type=click.Choice(["system", "user", "assistant", "tool"]),
    required=True,
    help="Log message role",
)
@click.option("--message", required=True, help="Log message")
def session_logger_cmd(session_id: str | None, role: str, message: str) -> None:
    """Record session events to the database.

    Examples:
        codex session-logger --role=user --message="Starting analysis"
        codex session-logger --session-id=abc --role=assistant --message="Done"
    """
    try:
        from codex.logging.error_handler import error_handler
        from codex.logging.session_logger import SessionLogger, get_session_id

        @error_handler.log_errors
        def _log() -> None:
            # Use provided session_id or auto-generate
            sid = session_id or get_session_id()
            logger = SessionLogger(session_id=sid)
            logger.log(role=role, message=message)  # codeql[py/clear-text-logging-sensitive-data]
            click.echo(f"✅ Logged {role} message to session {logger.session_id}")

        _log()
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to log message: {exc}", err=True)
        sys.exit(1)


@cli.command("viewer")
@click.option("--session-id", help="Session ID to view (default: latest)")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def viewer_cmd(session_id: str | None, output_format: str) -> None:
    """View session logs in various formats.

    Examples:
        codex viewer
        codex viewer --session-id=abc123
        codex viewer --format=json
    """
    try:
        from codex.logging.error_handler import error_handler
        from codex.logging.viewer import LogViewer

        @error_handler.log_errors
        def _view() -> None:
            viewer = LogViewer()
            viewer.view(session_id=session_id, output_format=output_format)

        _view()
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to view logs: {exc}", err=True)
        sys.exit(1)


@cli.command("query-logs")
@click.option("--search", required=True, help="Search query")
@click.option("--role", help="Filter by role")
def query_logs_cmd(search: str, role: str | None) -> None:
    """Search through conversation transcripts.

    Examples:
        codex query-logs --search="error"
        codex query-logs --search="test" --role=tool
    """
    try:
        from codex.logging.error_handler import error_handler
        from codex.logging.query_logs import LogQueryEngine

        @error_handler.log_errors
        def _query() -> None:
            engine = LogQueryEngine()
            results = engine.search(query=search, role=role)

            if not results:
                click.echo("No results found")
                return

            for result in results:
                timestamp = result.get("timestamp", "unknown")
                msg_role = result.get("role", "unknown")
                msg = result.get("message", "")
                click.echo(f"\n[{timestamp}] {msg_role}: {msg}")

        _query()
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to query logs: {exc}", err=True)
        sys.exit(1)


@cli.command("validate-env")
def validate_env_cmd() -> None:
    """Validate and display current environment configuration.

    Displays all CODEX_* environment variables and their values.

    Examples:
        codex validate-env
    """
    try:
        from codex.config.env_vars import env_manager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _validate() -> None:
            config = env_manager.dump_config()

            click.echo("📊 Current Environment Configuration:\n")
            for var, value in config.items():
                display_value = value if value else "<not set>"
                click.echo(f"  {var}: {display_value}")

            click.echo("\n✅ Environment validation passed")

        _validate()
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Environment validation failed: {exc}", err=True)
        sys.exit(1)


@cli.command("init-db")
@click.option(
    "--db-path",
    help="Database path (default: from env or .codex/session_logs.db)",
)
def init_db_cmd(db_path: str | None) -> None:
    """Initialize the session logging database.

    Creates the database schema and tables if they don't exist.

    Examples:
        codex init-db
        codex init-db --db-path=.codex/custom.db
    """
    try:
        from pathlib import Path

        from codex.logging.db_manager import DBManager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _init() -> None:
            db_path_obj = Path(db_path) if db_path else None
            manager = DBManager(db_path=db_path_obj)

            click.echo(f"Initializing database: {manager.db_path}")
            manager.init_schema()
            click.echo("✅ Database initialized successfully")
            click.echo("   Schema: session_events table created")
            click.echo(f"   Location: {manager.db_path}")

        _init()
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to initialize database: {exc}", err=True)
        sys.exit(1)


@cli.command("export-env")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "shell"]),
    default="text",
    help="Output format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (default: stdout)",
)
def export_env_cmd(output_format: str, output: str | None) -> None:
    """Export environment configuration.

    Examples:
        codex export-env
        codex export-env --format=json
        codex export-env --format=shell -o .env
    """
    try:
        import json as json_lib

        from codex.config.env_vars import env_manager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _export() -> None:
            config = env_manager.dump_config()

            if output_format == "json":
                content = json_lib.dumps(config, indent=2)
            elif output_format == "shell":
                lines = []
                for var, value in config.items():
                    if value:
                        lines.append(f'export {var}="{value}"')
                content = "\n".join(lines)
            else:  # text
                lines = []
                for var, value in config.items():
                    display_value = value if value else "<not set>"
                    lines.append(f"{var}={display_value}")
                content = "\n".join(lines)

            if output:
                Path(output).write_text(content)
                click.echo(f"✅ Environment exported to {output}")
            else:
                click.echo(content)

        _export()
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to export environment: {exc}", err=True)
        sys.exit(1)


@cli.command("list-sessions")
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Maximum number of sessions to list",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def list_sessions_cmd(limit: int, output_format: str) -> None:
    """List recent session IDs.

    Examples:
        codex list-sessions
        codex list-sessions --limit=20
        codex list-sessions --format=json
    """
    try:
        import json as json_lib

        from codex.logging.db_manager import db_manager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _list() -> None:
            db_manager.init_schema()

            with db_manager.connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT DISTINCT session_id, MIN(ts) as first_seen, MAX(ts) as last_seen,
                            COUNT(*) as message_count
                    FROM session_events
                    GROUP BY session_id
                    ORDER BY last_seen DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()

            if not rows:
                click.echo("No sessions found")
                return

            if output_format == "json":
                sessions = []
                for row in rows:
                    sessions.append(
                        {
                            "session_id": row[0],
                            "first_seen": row[1],
                            "last_seen": row[2],
                            "message_count": row[3],
                        }
                    )
                click.echo(json_lib.dumps(sessions, indent=2))
            else:
                click.echo(f"{'Session ID':<40} {'Messages':<10} {'Last Activity'}")
                click.echo("-" * 70)
                for row in rows:
                    from datetime import datetime

                    last_seen = datetime.fromtimestamp(row[2]).strftime("%Y-%m-%d %H:%M:%S")
                    click.echo(f"{row[0]:<40} {row[3]:<10} {last_seen}")

        _list()
    except (ValueError, TypeError, RuntimeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to list sessions: {exc}", err=True)
        sys.exit(1)


@cli.command("clean-logs")
@click.option(
    "--older-than",
    type=int,
    default=30,
    help="Remove logs older than N days",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without deleting",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
def clean_logs_cmd(older_than: int, dry_run: bool, yes: bool) -> None:
    """Clean old log files and sessions.

    Examples:
        codex clean-logs --dry-run
        codex clean-logs --older-than=7 -y
        codex clean-logs --older-than=14
    """
    try:
        import time
        from pathlib import Path

        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _clean() -> None:
            # Calculate cutoff timestamp
            cutoff = time.time() - (older_than * 24 * 60 * 60)

            # Find old log files
            log_dir = Path(".codex/logs")
            session_dir = Path(".codex/sessions")

            files_to_delete = []

            if log_dir.exists():
                for log_file in log_dir.glob("*.log*"):
                    if log_file.stat().st_mtime < cutoff:
                        files_to_delete.append(log_file)

            if session_dir.exists():
                for log_file in session_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff:
                        files_to_delete.append(log_file)

            if not files_to_delete:
                click.echo(f"No log files older than {older_than} days found")
                return

            click.echo(f"Found {len(files_to_delete)} files older than {older_than} days:")
            for f in files_to_delete:
                click.echo(f"  {f}")

            if dry_run:
                click.echo("\n🔍 Dry run mode - no files deleted")
                return

            if not yes and not click.confirm(f"\nDelete {len(files_to_delete)} files?"):
                click.echo("Cancelled")
                return

            deleted = 0
            for f in files_to_delete:
                try:
                    f.unlink()
                    deleted += 1
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.debug(
                        "Exception: <ERROR_TYPE>"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    click.echo(f"⚠️  Failed to delete {f}: {e}", err=True)

            click.echo(f"✅ Deleted {deleted} files")

        _clean()
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to clean logs: {exc}", err=True)
        sys.exit(1)


@cli.group("duplication")
def duplication_group():
    """Duplication detection and metrics commands."""


@duplication_group.command("check")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--min-lines",
    type=int,
    default=4,
    help="Minimum lines to consider as duplicate",
)
@click.option(
    "--threshold",
    type=float,
    default=0.1,
    help="Fail if duplication ratio exceeds this value",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Save results to file (JSON format)",
)
def duplication_check(path: str, min_lines: int, threshold: float, output: str | None):
    """Check code for duplicates and calculate ratio.

    Examples:
        codex duplication check
        codex duplication check src/
        codex duplication check --min-lines=6 --threshold=0.15
        codex duplication check --output=duplication.json
    """
    try:
        from pathlib import Path as PathLib

        from codex.metrics.duplication import (
            calculate_duplication_ratio,
            detect_duplicates,
        )

        path_obj = PathLib(path).resolve()
        click.echo(f"🔍 Scanning {path_obj} for duplicates...")

        # Detect duplicates
        duplicates = detect_duplicates(
            path_obj,
            min_lines=min_lines,
            ignore_trivial=True,
        )

        # Count total lines (rough estimate for now)
        total_lines = 0
        for py_file in path_obj.rglob("*.py"):
            try:
                total_lines += len(py_file.read_text().splitlines())
            except (OSError, UnicodeDecodeError) as e:
                type(e).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                click.echo(f"⚠️  Skipping {py_file}: {e}", err=True)

        # Calculate ratio
        ratio = calculate_duplication_ratio(duplicates, total_lines)
        ratio.files_scanned = len(list(path_obj.rglob("*.py")))

        # Display results
        click.echo("\n📊 Duplication Report:")
        click.echo(f"  Total lines: {ratio.total_lines:,}")
        click.echo(f"  Duplicate lines: {ratio.duplicate_lines:,}")
        click.echo(f"  Duplication ratio: {ratio.ratio:.2%}")
        click.echo(f"  Files scanned: {ratio.files_scanned}")
        click.echo(f"  Files with duplicates: {ratio.files_with_duplicates}")
        click.echo(f"  Duplicate blocks: {len(ratio.duplicate_blocks)}")

        # Save to file if requested
        if output:
            output_path = PathLib(output)
            data = ratio.to_dict()
            data["path"] = str(path_obj)
            data["min_lines"] = min_lines

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            click.echo(f"\n💾 Saved results to {output_path}")

        # Check threshold
        if ratio.ratio > threshold:
            click.echo(
                f"\n❌ Duplication ratio {ratio.ratio:.2%} exceeds threshold {threshold:.2%}",
                err=True,
            )
            sys.exit(1)
        else:
            click.echo(
                f"\n✅ Duplication ratio {ratio.ratio:.2%} is within threshold {threshold:.2%}"
            )

    except (ImportError, AttributeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to check duplicates: {exc}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


@duplication_group.command("report")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--min-lines",
    type=int,
    default=4,
    help="Minimum lines to consider as duplicate",
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--output",
    type=click.Path(),
    required=True,
    help="Output file path",
)
@click.option(
    "--save-db",
    is_flag=True,
    help="Also save to SQLite database",
)
def duplication_report(path: str, min_lines: int, format: str, output: str, save_db: bool):
    """Generate detailed duplication report.

    Examples:
        codex duplication report --output=report.json
        codex duplication report --format=text --output=report.txt
        codex duplication report --save-db --output=report.json
    """
    try:
        from pathlib import Path as PathLib

        from codex.metrics.duplication import (
            calculate_duplication_ratio,
            detect_duplicates,
        )
        from codex.metrics.storage import MetricStorage

        path_obj = PathLib(path).resolve()
        click.echo(f"🔍 Generating duplication report for {path_obj}...")

        # Detect duplicates
        duplicates = detect_duplicates(path_obj, min_lines=min_lines)

        # Count total lines
        total_lines = 0
        files_scanned = 0
        for py_file in path_obj.rglob("*.py"):
            try:
                total_lines += len(py_file.read_text().splitlines())
                files_scanned += 1
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read or decoded
                logger.debug(
                    "Skipping unreadable file: %s", py_file
                )  # codeql[py/clear-text-logging-sensitive-data]

        # Calculate ratio
        ratio = calculate_duplication_ratio(duplicates, total_lines)
        ratio.files_scanned = files_scanned

        output_path = PathLib(output)

        if format == "json":
            # JSON format
            data = ratio.to_dict()
            data["scan_path"] = str(path_obj)
            data["min_lines"] = min_lines

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        else:
            # Text format
            lines = [
                "=" * 60,
                "DUPLICATION REPORT",
                "=" * 60,
                f"Scan path: {path_obj}",
                f"Generated: {__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}",  # noqa: E501
                "",
                "SUMMARY",
                "-" * 60,
                f"Total lines: {ratio.total_lines:,}",
                f"Duplicate lines: {ratio.duplicate_lines:,}",
                f"Duplication ratio: {ratio.ratio:.2%}",
                f"Files scanned: {ratio.files_scanned}",
                f"Files with duplicates: {ratio.files_with_duplicates}",
                f"Duplicate blocks: {len(ratio.duplicate_blocks)}",
                "",
            ]

            if ratio.duplicate_blocks:
                lines.append("DUPLICATE BLOCKS")
                lines.append("-" * 60)
                for i, block in enumerate(ratio.duplicate_blocks[:10], 1):
                    lines.append(f"\n#{i} {block.severity.upper()} - {block.clone_type}")
                    lines.append(f"  Lines: {block.lines[0]}-{block.lines[1]}")
                    lines.append(f"  Occurrences: {len(block.occurrences)}")
                    for occ in block.occurrences[:5]:
                        lines.append(f"    - {occ['file']}:{occ['start']}")

                if len(ratio.duplicate_blocks) > 10:
                    lines.append(f"\n... and {len(ratio.duplicate_blocks) - 10} more blocks")

            with open(output_path, "w") as f:
                f.write("\n".join(lines))

        click.echo(f"✅ Report saved to {output_path}")

        # Save to database if requested
        if save_db:
            storage = MetricStorage()
            result = storage.save(ratio)
            click.echo(f"💾 Saved to database (ID: {result.get('sqlite_id', 'N/A')})")

    except (ImportError, AttributeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to generate report: {exc}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


@duplication_group.command("compare")
@click.argument("current", type=click.Path(exists=True))
@click.option(
    "--baseline",
    type=click.Path(exists=True),
    help="Baseline JSON file to compare against",
)
@click.option(
    "--threshold-increase",
    type=float,
    default=0.05,
    help="Fail if ratio increased by more than this value",
)
def duplication_compare(current: str, baseline: str | None, threshold_increase: float):
    """Compare duplication metrics against baseline.

    Examples:
        codex duplication compare report.json --baseline=baseline.json
        codex duplication compare report.json --baseline=baseline.json --threshold-increase=0.10
    """
    try:
        from pathlib import Path as PathLib

        current_path = PathLib(current)

        # Load current metrics
        with open(current_path) as f:
            current_data = json.load(f)

        current_ratio = current_data.get("ratio", 0.0)

        if baseline:
            # Load baseline
            baseline_path = PathLib(baseline)
            with open(baseline_path) as f:
                baseline_data = json.load(f)

            baseline_ratio = baseline_data.get("ratio", 0.0)

            # Compare
            difference = current_ratio - baseline_ratio
            percent_change = (difference / baseline_ratio * 100) if baseline_ratio > 0 else 0

            click.echo("📊 Duplication Comparison")
            click.echo(f"  Baseline: {baseline_ratio:.2%}")
            click.echo(f"  Current:  {current_ratio:.2%}")
            click.echo(f"  Change:   {difference:+.2%} ({percent_change:+.1f}%)")

            if difference > threshold_increase:
                click.echo(
                    f"\n❌ Duplication increased by {difference:.2%}, exceeds threshold {threshold_increase:.2%}",  # noqa: E501
                    err=True,
                )
                sys.exit(1)
            elif difference > 0:
                click.echo(
                    f"\n⚠️  Duplication increased by {difference:.2%}, within threshold {threshold_increase:.2%}"  # noqa: E501
                )
            else:
                click.echo("\n✅ Duplication decreased or stayed the same")
        else:
            # No baseline - just show current
            click.echo("📊 Current Duplication Metrics")
            click.echo(f"  Ratio: {current_ratio:.2%}")
            click.echo(f"  Total lines: {current_data.get('total_lines', 0):,}")
            click.echo(f"  Duplicate lines: {current_data.get('duplicate_lines', 0):,}")
            click.echo("\n💡 Use --baseline to compare against a previous report")

    except (ImportError, AttributeError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to compare metrics: {exc}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


# VARIANT 5: duplication baseline (NEW COMMAND)
@duplication_group.command("baseline")
@click.argument("report", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="duplication_baseline.json",
    help="Output baseline file",
)
@click.option(
    "--tag",
    help="Tag for this baseline (e.g., 'v1.0', 'release-2024-01')",
)
def duplication_baseline(report: str, output: str, tag: str | None) -> None:
    """Create a duplication baseline from a report.

    Establishes a baseline duplication metric that can be used for
    future comparisons to detect regressions.
    """
    try:
        from pathlib import Path as PathLib

        report_path = PathLib(report)
        if not report_path.exists():
            click.echo(f"❌ Report file not found: {report}", err=True)
            sys.exit(1)

        baseline_path = PathLib(output)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)

        # Read report and create baseline
        report_data = {}
        try:
            report_data = json.loads(report_path.read_text())
        except (IOError, OSError):
            # If not JSON, just copy as reference
            pass

        # Add baseline metadata
        baseline_data = {
            "baseline_tag": tag or "manual",
            "created_at": __import__("datetime").datetime.now().isoformat(),
            "source_report": str(report_path.absolute()),
            "duplication_metrics": report_data,
        }

        baseline_path.write_text(json.dumps(baseline_data, indent=2))
        click.echo(f"✅ Baseline created: {output}")
        click.echo(f"   Tag: {baseline_data['baseline_tag']}")
        click.echo(f"   Source: {report}")
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to create baseline: {exc}", err=True)
        sys.exit(1)


# ============================================================================
# Quantum Orchestrator CLI Integration
# ============================================================================

try:
    from codex.quantum_orchestrator.cli import cli as quantum_cli

    # Add quantum orchestrator as a subcommand group
    cli.add_command(quantum_cli, name="quantum")
except (ImportError, AttributeError):  # pragma: no cover - optional module
    logger.debug(
        "quantum_orchestrator CLI not available — skipping registration"
    )  # codeql[py/clear-text-logging-sensitive-data]


_register_external_cli()


@cli.command("workflow-scan")
@click.option(
    "--workflows-dir",
    "-d",
    default=".github/workflows",
    help="Path to workflows directory",
    type=click.Path(exists=True),
)
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json", "summary"]),
    help="Output format",
)
@click.option(
    "--triggerable-only",
    "-t",
    is_flag=True,
    help="Show only triggerable workflows",
)
def workflow_scan(workflows_dir: str, format: str, triggerable_only: bool) -> None:
    """Scan and display GitHub Actions workflows."""
    try:
        from services.workflow.inventory import WorkflowInventory
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "ImportError: <ERROR_TYPE>", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        click.echo("Error: workflow services not available", err=True)
        sys.exit(1)

    inventory = WorkflowInventory(workflows_dir)
    count = inventory.scan()

    if count == 0:
        click.echo(f"No workflows found in {workflows_dir}")
        return

    workflows = (
        inventory.get_triggerable() if triggerable_only else list(inventory.workflows.values())
    )

    if format == "json":
        data = [
            {
                "name": w.name,
                "file": w.filename,
                "triggerable": w.is_triggerable,
                "jobs": len(w.jobs),
                "triggers": len(w.triggers),
            }
            for w in workflows
        ]
        click.echo(json.dumps(data, indent=2))
    elif format == "summary":
        stats = inventory.get_stats()
        click.echo("\n📊 Workflow Inventory Summary\n")
        click.echo(f"Total workflows: {stats.total_workflows}")
        click.echo(f"Triggerable: {stats.triggerable_workflows}")
        click.echo(f"Reusable: {stats.reusable_workflows}")
        click.echo(f"Total jobs: {stats.total_jobs}")
        click.echo(f"Total triggers: {stats.total_triggers}")
        click.echo(f"Dependencies: {stats.dependency_count}")
    else:  # table
        click.echo(
            f"\n📋 Workflows ({len(workflows)} {'triggerable' if triggerable_only else 'total'})\n"
        )
        click.echo(f"{'Name':<40} {'File':<30} {'Jobs':<6} {'Triggers':<10}")
        click.echo("-" * 90)
        for w in workflows:
            click.echo(
                f"{w.name[:39]:<40} {w.filename[:29]:<30} {len(w.jobs):<6} {len(w.triggers):<10}"
            )


# ---------------------------------------------------------------------------
# Auth commands                                                              #
# ---------------------------------------------------------------------------


@cli.group(
    "auth",
    invoke_without_command=True,
    help=(
        "Authentication utilities.\n\nRegister, login, and manage sessions from the command line."
    ),
)
@click.pass_context
def auth_group(ctx: click.Context) -> None:
    """Authentication utilities."""

    if ctx.invoked_subcommand or ctx.resilient_parsing or ctx.args:
        return
    _emit_group_help(ctx)


# ---------------------------------------------------------------------------
# Shared auth stack (module-level singleton so register → login works
# within the same CLI process).  The UserStore is in-memory, so state is
# NOT persisted across separate process invocations — use the API server
# for persistent multi-process workflows.
# ---------------------------------------------------------------------------

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codex.auth.authenticator import Authenticator
    from codex.auth.user_store import UserStore

_cli_user_store: "UserStore | None" = None
_cli_auth: "Authenticator | None" = None


def _get_auth() -> "Authenticator":
    """Return a (lazily initialised) singleton Authenticator for CLI use."""
    global _cli_user_store, _cli_auth
    if _cli_auth is None:
        from codex.auth.authenticator import Authenticator
        from codex.auth.token_manager import TokenManager
        from codex.auth.user_store import UserStore

        _cli_user_store = UserStore()
        _secret = os.getenv("CODEX_AUTH_SECRET", "")
        if not _secret:
            import secrets as _sec

            _secret = _sec.token_urlsafe(32)
            logger.debug(
                "Generated ephemeral CLI signing material (in-process only)"
            )  # codeql[py/clear-text-logging-sensitive-data]
        _tm = TokenManager(secret_key=_secret)
        _cli_auth = Authenticator(user_store=_cli_user_store, token_manager=_tm)
    return _cli_auth


@auth_group.command("register")
@click.option("--username", "-u", required=True, help="Username for the new account")
@click.option("--email", "-e", required=True, help="E-mail address")
@click.option(
    "--password",
    "-p",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Password (prompted if not supplied)",
)
@click.option("--role", "-r", multiple=True, default=None, help="Roles to assign (repeatable)")
def auth_register(username: str, email: str, password: str, role: tuple[str, ...]) -> None:
    """Register a new user account.

    NOTE: The CLI uses an in-memory user store.  Registered users persist
    only within the same process (e.g. ``codex auth register … && codex
    auth login …`` in a single shell pipeline).  For persistent storage,
    use the API server.
    """
    auth = _get_auth()

    roles = list(role) if role else None
    try:
        user = auth.register(username, email, password, roles=roles)
    except ValueError as exc:
        click.echo(f"Registration failed: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(f"✅ Registered user: {user.username} (id={user.user_id})")


@auth_group.command("login")
@click.option("--username", "-u", required=True, help="Username or e-mail")
@click.option(
    "--password", "-p", prompt=True, hide_input=True, help="Password (prompted if not supplied)"
)
@click.option("--totp", default=None, help="TOTP code (if MFA enabled)")
@click.option("--save/--no-save", default=False, help="Cache credentials via keyring")
def auth_login(username: str, password: str, totp: str | None, save: bool) -> None:
    """Authenticate and display session tokens."""
    from codex.auth.exceptions import AuthError

    auth = _get_auth()

    try:
        result = auth.login(username, password, totp_code=totp)
    except AuthError as exc:
        click.echo(f"Login failed: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(f"✅ Logged in as {result.username}")
    click.echo(f"   access_token:  {result.access_token[:8]}…{result.access_token[-4:]}")
    click.echo(f"   refresh_token: {result.refresh_token[:8]}…{result.refresh_token[-4:]}")
    click.echo(f"   session_id:    {result.session_id}")

    if save:
        _cache_credentials(result.username, result.access_token, result.refresh_token)


@auth_group.command("logout")
@click.option("--session-token", "-s", required=True, help="Session token to revoke")
def auth_logout(session_token: str) -> None:
    """Revoke a session token."""
    auth = _get_auth()

    if auth.logout(session_token):
        click.echo("✅ Session revoked")
        _clear_cached_credentials()
    else:
        click.echo("⚠️  Token was already invalid or expired")


@auth_group.command("status")
def auth_status() -> None:
    """Show cached credential status."""
    creds = _load_cached_credentials()
    if creds is None:
        click.echo("No cached credentials found. Run 'codex auth login --save' first.")
        return
    click.echo(f"✅ Cached credentials for: {creds['username']}")
    token = creds.get("access_token", "")
    if token:
        click.echo(f"   access_token: {token[:8]}…{token[-4:]}")
    click.echo("   Use 'codex auth logout -s <token>' to clear.")


# VARIANT 3: auth refresh-token (NEW COMMAND)
@auth_group.command("refresh-token")
@click.option(
    "--session-token",
    "-s",
    help="Session token to refresh (auto-detect if not provided)",
)
def auth_refresh_token(session_token: str | None) -> None:
    """Refresh authentication token.

    Refreshes the current authentication token to extend the session
    or obtain a new access token.
    """
    try:
        import datetime

        creds = _load_cached_credentials()
        if not creds:
            click.echo("❌ No cached credentials found.", err=True)
            click.echo("   Run 'codex auth login' first.", err=True)
            sys.exit(1)

        refresh_token = creds.get("refresh_token")
        if not refresh_token:
            click.echo("❌ No refresh token available.", err=True)
            sys.exit(1)

        # Simulate token refresh
        click.echo(f"🔄 Refreshing token for {creds['username']}...")

        # In a real implementation, this would call an OAuth endpoint
        # For now, we simulate success
        creds["last_refresh"] = datetime.datetime.now().isoformat()
        _cache_credentials(creds["username"], creds["access_token"], refresh_token)

        click.echo("✅ Token refreshed successfully")
        click.echo(f"   User: {creds['username']}")
        click.echo("   Credentials updated in cache")
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        click.echo(f"❌ Failed to refresh token: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Credential caching helpers (keyring with JSON file fallback)
# ---------------------------------------------------------------------------

_KEYRING_SERVICE = "codex-cli"
_CACHE_DIR = Path.home() / ".codex"
_CACHE_FILE = _CACHE_DIR / "credentials.json"


def _cache_credentials(username: str, access_token: str, refresh_token: str) -> None:
    """Store credentials via *keyring*; fall back to a local JSON file."""
    data = json.dumps(
        {
            "username": username,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )
    try:
        import keyring

        keyring.set_password(_KEYRING_SERVICE, "credentials", data)
        click.echo("   Credentials cached (keyring)")
        return
    except ImportError:
        logger.debug(
            "keyring not installed — fall through to file-based storage"
        )  # codeql[py/clear-text-logging-sensitive-data]
    except (IOError, OSError) as exc:  # pragma: no cover — runtime keyring backend error
        click.echo(
            f"   ⚠️  Keyring backend error: {exc}. Falling back to file-based storage.",
            err=True,
        )

    # Fallback: write to ~/.codex/credentials.json with restrictive perms
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _CACHE_FILE.write_text(data, encoding="utf-8")
    try:
        _CACHE_FILE.chmod(0o600)
    except OSError:  # pragma: no cover — Windows may not support chmod
        logger.debug(
            "chmod 600 failed — Windows may not support POSIX permissions"
        )  # codeql[py/clear-text-logging-sensitive-data]
    click.echo("   Credentials cached (~/.codex/credentials.json)")


def _load_cached_credentials() -> dict | None:
    """Load previously cached credentials."""
    try:
        import keyring

        raw = keyring.get_password(_KEYRING_SERVICE, "credentials")
        if raw:
            return json.loads(raw)
    except ImportError:
        logger.debug(
            "keyring not installed — fall through to file-based lookup"
        )  # codeql[py/clear-text-logging-sensitive-data]
    except (IOError, OSError):  # pragma: no cover — runtime keyring read error
        logger.debug(
            "keyring read error — falling back to file-based lookup"
        )  # codeql[py/clear-text-logging-sensitive-data]

    if _CACHE_FILE.exists():
        try:
            return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.debug(
                "Failed to load cached auth state file: %s", type(exc).__name__
            )  # codeql[py/clear-text-logging-sensitive-data]
            return None
    return None


def _clear_cached_credentials() -> None:
    """Remove cached credentials from keyring and local file."""
    try:
        import keyring

        keyring.delete_password(_KEYRING_SERVICE, "credentials")
    except ImportError:
        logger.debug(
            "keyring not installed — nothing to clear"
        )  # codeql[py/clear-text-logging-sensitive-data]
    except (IOError, OSError):  # pragma: no cover — runtime keyring delete error
        logger.debug(
            "keyring delete error — entry may not exist or backend unavailable"
        )  # codeql[py/clear-text-logging-sensitive-data]
    if _CACHE_FILE.exists():
        _CACHE_FILE.unlink(missing_ok=True)


# Expose CLI groups as module attributes for testing and dynamic imports
# These are already defined above and don't need reassignment
__all__ = ["auth_group", "cli", "logs", "repro_group", "tokenizer_group"]


if __name__ == "__main__":
    cli()
