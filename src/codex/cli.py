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
        "archive",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow.",
    )
    _register_typer_app(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive tombstone workflow commands.",
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


_register_external_cli()


if __name__ == "__main__":
    cli()
