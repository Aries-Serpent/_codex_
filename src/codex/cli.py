"""Unified CLI for codex, using click for subcommands and input validation."""

from __future__ import annotations

import importlib
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import click

try:  # pragma: no cover - optional dependency
    import typer
except Exception:  # pragma: no cover - degrade gracefully when Typer missing
    typer = None  # type: ignore[assignment]
else:  # pragma: no cover - exercised in Typer-enabled environments
    try:
        from codex.cli_knowledge import app as knowledge_app
        from codex.cli_release import app as release_app
    except Exception:  # pragma: no cover - Typer sub-app import guard
        knowledge_app = None  # type: ignore[assignment]
        release_app = None  # type: ignore[assignment]
    else:
        app = typer.Typer(help="Codex Typer CLI (release + knowledge)")
        app.add_typer(release_app, name="release")
        app.add_typer(knowledge_app, name="knowledge")

try:  # pragma: no cover - optional dependency
    from typer.main import get_command as _typer_get_command
except Exception:  # pragma: no cover
    _typer_get_command = None

try:  # pragma: no cover - optional dependency
    from codex_digest.error_capture import log_error as _log_error
except Exception:  # pragma: no cover

    def _log_error(step_no: str, step_desc: str, msg: str, ctx: str) -> None:  # type: ignore[func-returns-value]
        """Fallback error logger when codex_digest is unavailable."""
        return None


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
    except Exception as exc:
        print(f"CI failed: {exc}")
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

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

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
        except Exception as exc:
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


ALLOWED_TASKS = {
    "ingest": (_run_ingest, "Ingest example data into the Codex environment."),
    "ci": (_run_ci, "Run local CI checks (lint + tests)."),
    "pool-fix": (lambda: _fix_pool(4), "Reset tokenization thread pool (default 4 workers)."),
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
    except Exception as exc:  # pragma: no cover - optional dependency path
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
    except Exception as exc:  # pragma: no cover - optional dependency path
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
    except Exception as exc:
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
    except Exception as exc:
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
    except Exception as exc:
        click.echo(f"Failed to query logs: {exc}", err=True)
        _log_error("STEP logs_query", "codex_db --query", str(exc), f"db={db}")
        sys.exit(1)


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
        hydra_cfg: dict[str, object] = {
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "precision": args.precision,
            "seed": args.seed,
        }
        lora_section: dict[str, object] = {}
        if args.lora_r:
            lora_section["r"] = args.lora_r
        if args.lora_alpha is not None:
            lora_section["alpha"] = args.lora_alpha
        if args.lora_dropout:
            lora_section["dropout"] = args.lora_dropout
        if args.lora_task_type:
            lora_section["task_type"] = args.lora_task_type
        if lora_section:
            hydra_cfg["lora"] = lora_section
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
        except Exception as exc:
            _log_error("STEP train", "run_hf_trainer", str(exc), f"texts={args.texts}")
            raise
    else:
        try:
            from codex.training import main as run_custom_train
        except Exception as exc:  # pragma: no cover - fallback path
            click.echo(f"[warn] custom engine unavailable, falling back to hf_trainer: {exc}")
            from training.engine_hf_trainer import run_hf_trainer

            try:
                run_hf_trainer(*engine_args)
                return
            except Exception as exc2:
                _log_error(
                    "STEP train", "fallback run_hf_trainer", str(exc2), f"args={engine_args}"
                )
                raise
        argv = ["--engine", "custom", *engine_args]
        orig_argv = sys.argv
        try:
            sys.argv = [orig_argv[0], *argv]
            run_custom_train()
        except Exception as exc:
            _log_error("STEP train", "run_custom_train", str(exc), f"argv={argv}")
            raise
        finally:
            sys.argv = orig_argv


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
    except Exception as exc:  # pragma: no cover - robust CLI behavior
        click.echo(f"ERROR: failed to read resume_manifest.json: {exc}", err=True)
        raise SystemExit(2)

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
            except Exception:
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
                except Exception:
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
    except Exception as exc:  # pragma: no cover
        click.echo(f"Environment logging module unavailable: {exc}", err=True)
        sys.exit(1)

    try:
        log_env_info(path)
        click.echo(f"wrote {path}")
    except Exception as exc:  # pragma: no cover
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


def _register_tokenizer_pipeline_commands() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
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
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
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
# AGENTS.md Infrastructure Commands
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
            logger.log(role=role, message=message)
            click.echo(f"✅ Logged {role} message to session {logger.session_id}")

        _log()
    except Exception as exc:
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
    except Exception as exc:
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
    except Exception as exc:
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
    except Exception as exc:
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
    except Exception as exc:
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
    except Exception as exc:
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
    except Exception as exc:
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

            if not yes:
                if not click.confirm(f"\nDelete {len(files_to_delete)} files?"):
                    click.echo("Cancelled")
                    return

            deleted = 0
            for f in files_to_delete:
                try:
                    f.unlink()
                    deleted += 1
                except Exception as e:
                    click.echo(f"⚠️  Failed to delete {f}: {e}", err=True)

            click.echo(f"✅ Deleted {deleted} files")

        _clean()
    except Exception as exc:
        click.echo(f"❌ Failed to clean logs: {exc}", err=True)
        sys.exit(1)


@cli.group("duplication")
def duplication_group():
    """Duplication detection and metrics commands."""
    pass


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
                click.echo(f"⚠️  Skipping {py_file}: {e}", err=True)
                pass

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

    except Exception as exc:
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
            except:
                pass

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
                f"Generated: {__import__('datetime').datetime.now().isoformat()}",
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

    except Exception as exc:
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
                    f"\n❌ Duplication increased by {difference:.2%}, exceeds threshold {threshold_increase:.2%}",
                    err=True,
                )
                sys.exit(1)
            elif difference > 0:
                click.echo(
                    f"\n⚠️  Duplication increased by {difference:.2%}, within threshold {threshold_increase:.2%}"
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

    except Exception as exc:
        click.echo(f"❌ Failed to compare metrics: {exc}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


_register_external_cli()


if __name__ == "__main__":
    cli()
