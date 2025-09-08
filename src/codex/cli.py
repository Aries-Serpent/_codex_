"""Unified CLI for codex, using click for subcommands and input validation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import click

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
    except Exception as exc:  # noqa: BLE001
        print(f"CI failed: {exc}")


def _fix_pool() -> None:
    print("Pool fix not yet implemented; see issue #123.")


ALLOWED_TASKS = {
    "ingest": _run_ingest,
    "ci": _run_ci,
    "pool-fix": _fix_pool,
}


@click.group()
def cli() -> None:
    """Codex CLI entry point."""
    pass


@cli.group("logs")
def logs() -> None:
    """Codex logs (local SQLite data blot)."""
    pass


@logs.command("init")
@click.option("--db", default=".codex/codex.sqlite", help="DB path")
def logs_init(db: str) -> None:
    """Initialize SQLite schema for logs."""
    script = TOOLS_DIR / "codex_db.py"
    try:
        subprocess.run([sys.executable, str(script), "--init", "--db", db], check=True)
    except Exception as exc:
        click.echo(f"Failed to init logs DB: {exc}", err=True)
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
        # LoRA flags (support hyphen and underscore for backward compatibility)
        parser.add_argument("--lora-r", "--lora_r", dest="lora_r", type=int, default=0, help="LoRA rank; set >0 to enable")
        parser.add_argument("--lora-alpha", "--lora_alpha", dest="lora_alpha", type=int, default=16, help="LoRA alpha scaling")
        parser.add_argument("--lora-dropout", "--lora_dropout", dest="lora_dropout", type=float, default=0.0, help="LoRA dropout probability")
        parser.add_argument("--seed", type=int, default=0)

        args = parser.parse_args(list(engine_args))
        kw: dict[str, object] = {
            "val_texts": args.val_texts,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "precision": args.precision,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "seed": args.seed,
        }
        # Optionally forward device/dtype if parser/engine supports them
        for opt in ("device", "dtype"):
            if hasattr(args, opt):
                val = getattr(args, opt)
                if val is not None:
                    kw[opt] = val
        return run_hf_trainer(args.texts, args.output_dir, **kw)
    else:
        try:
            from training.functional_training import main as run_custom_train
        except Exception as exc:  # pragma: no cover - fallback path
            click.echo(f"[warn] custom engine unavailable, falling back to hf_trainer: {exc}")
            from training.engine_hf_trainer import run_hf_trainer

            return run_hf_trainer(*engine_args)
        argv = ["--engine", "custom", *engine_args]
        return run_custom_train(argv)


@cli.command("tasks")
def list_tasks() -> None:
    """List allowed maintenance tasks."""
    for task in ALLOWED_TASKS:
        click.echo(task)


@cli.command("run")
@click.argument("task")
def run_task(task: str) -> None:
    """Run a whitelisted maintenance task by name."""
    if task not in ALLOWED_TASKS:
        click.echo(f"Task '{task}' is not allowed.", err=True)
        sys.exit(1)
    ALLOWED_TASKS[task]()


@cli.group("tokenizer")
def tokenizer_group() -> None:
    """Tokenization utilities."""
    pass


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


@cli.group("repro")
def repro_group() -> None:
    """Reproducibility utilities."""
    pass


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


if __name__ == "__main__":
    cli()
