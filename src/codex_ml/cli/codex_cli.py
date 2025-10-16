from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import click

from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.config import ConfigError, load_app_config
from codex_ml.telemetry import start_metrics_server
from codex_ml.utils.provenance import export_environment, load_environment_summary
from codex_utils.ndjson import NDJSONLogger

_ = (ArgparseJSONParser, run_cmd)

DEFAULT_TOKENIZER_CONFIG = "configs/tokenization/base.yaml"
DEFAULT_TOKENIZER_JSON = "artifacts/tokenizers/default/default/tokenizer.json"


@lru_cache(maxsize=1)
def _get_tokenizer_pipeline():
    try:
        from codex_ml.tokenization import pipeline as tokenizer_pipeline
    except ModuleNotFoundError as exc:  # pragma: no cover - surfaced via Click
        missing = (exc.name or "").split(".", 1)[0]
        if missing == "tokenizers":
            raise click.ClickException(
                "Tokenizer commands require the optional 'tokenizers' dependency. "
                "Install it to enable tokenizer CLI functionality."
            ) from exc
        raise
    return tokenizer_pipeline


@click.group()
def codex() -> None:
    """Codex command line interface."""


def _emit_provenance_summary(provenance_dir: Path) -> None:
    summary = load_environment_summary(provenance_dir)
    if summary:
        click.echo(json.dumps(summary, sort_keys=True))


@codex.group()
def tokenizer() -> None:
    """Tokenizer pipeline utilities."""


@tokenizer.command("train")
@click.option(
    "--config",
    default=DEFAULT_TOKENIZER_CONFIG,
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the tokenizer pipeline configuration file.",
)
@click.option(
    "--streaming/--no-streaming",
    default=None,
    help="Enable or disable streaming ingestion (defaults to the config value).",
)
@click.option(
    "--stream-chunk-size",
    type=click.IntRange(min=1),
    default=None,
    help=(
        "Override the streaming chunk size in characters "
        "(defaults to 1 MiB when streaming is enabled)."
    ),
)
@click.option("--dry-run", is_flag=True, help="Print the training plan without running.")
def tokenizer_train(
    config: str, streaming: bool | None, stream_chunk_size: int | None, dry_run: bool
) -> None:
    """Train a tokenizer according to the provided configuration."""
    tokenizer_pipeline = _get_tokenizer_pipeline()
    try:
        out_dir = tokenizer_pipeline.run_train(
            config,
            streaming=streaming,
            stream_chunk_size=stream_chunk_size,
            dry_run=dry_run,
        )
    except tokenizer_pipeline.TokenizerPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
    if dry_run:
        click.echo("dry run complete")
        return
    click.echo(f"tokenizer artifacts written to {out_dir}")


@tokenizer.command("validate")
@click.option(
    "--config",
    default=DEFAULT_TOKENIZER_CONFIG,
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the tokenizer pipeline configuration file.",
)
def tokenizer_validate(config: str) -> None:
    """Validate dataset manifests and cached tokenizer artifacts."""
    tokenizer_pipeline = _get_tokenizer_pipeline()
    try:
        report = tokenizer_pipeline.run_validate(config)
    except tokenizer_pipeline.TokenizerPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(report, indent=2, sort_keys=True))


@tokenizer.command("encode")
@click.argument("text", required=False)
@click.option(
    "--tokenizer-path",
    default=DEFAULT_TOKENIZER_JSON,
    show_default=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to the serialized tokenizer JSON file to use for encoding.",
)
def tokenizer_encode(text: str | None, tokenizer_path: str) -> None:
    """Encode text with a trained tokenizer."""
    if text is None:
        text = click.get_text_stream("stdin").read()
    if text is None:
        text = ""
    tokenizer_pipeline = _get_tokenizer_pipeline()
    try:
        token_ids = tokenizer_pipeline.run_encode(tokenizer_path, text)
    except tokenizer_pipeline.TokenizerPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(" ".join(str(tid) for tid in token_ids))


@tokenizer.command("decode")
@click.argument("token_ids", nargs=-1, type=int)
@click.option(
    "--tokenizer-path",
    default=DEFAULT_TOKENIZER_JSON,
    show_default=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to the serialized tokenizer JSON file to use for decoding.",
)
def tokenizer_decode(token_ids: tuple[int, ...], tokenizer_path: str) -> None:
    """Decode token IDs with a trained tokenizer."""
    if not token_ids:
        raw = click.get_text_stream("stdin").read().strip()
        token_ids = tuple(int(part) for part in raw.split()) if raw else ()
    tokenizer_pipeline = _get_tokenizer_pipeline()
    try:
        text = tokenizer_pipeline.run_decode(tokenizer_path, token_ids)
    except tokenizer_pipeline.TokenizerPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(text)


@codex.command()
@click.option(
    "--config",
    default="configs/training/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the training YAML configuration.",
)
@click.argument("overrides", nargs=-1)
@click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Override the random seed from the config (best-effort determinism).",
)
@click.option(
    "--resume-from",
    type=click.Path(file_okay=False, path_type=str),
    default=None,
    help="Optional checkpoint directory or file to resume from.",
)
def train(
    config: str,
    overrides: tuple[str, ...],
    resume: bool,
    seed: int | None,
    resume_from: str | None,
) -> None:
    """Train a language model using the Codex functional trainer."""
    from codex_ml.training import run_functional_training
    from codex_ml.utils.error_log import log_error as log_training_error

    try:
        cfg_obj, raw_cfg = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    if seed is not None:
        if hasattr(raw_cfg, "training") and hasattr(raw_cfg.training, "seed"):
            raw_cfg.training.seed = seed
        else:
            raw_cfg.seed = seed
        cfg_obj.training.seed = seed

    training_cfg = getattr(raw_cfg, "training", raw_cfg)

    if resume_from:
        if hasattr(cfg_obj.training, "resume_from"):
            cfg_obj.training.resume_from = resume_from
        training_cfg.resume_from = resume_from  # type: ignore[attr-defined]
        resume = True

    try:
        run_functional_training(config=training_cfg, resume=resume)
        provenance_dir = Path(cfg_obj.training.output_dir) / "provenance"
        _emit_provenance_summary(provenance_dir)
        click.echo("training complete")
    except Exception as exc:  # pragma: no cover - Click handles presentation
        log_training_error(
            "cli.train",
            str(exc),
            f"config={config} resume={resume} resume_from={resume_from}",
        )
        raise click.ClickException(str(exc)) from exc


@codex.command("metrics-server")
@click.option("--port", default=8000, show_default=True)
def metrics_server(port: int) -> None:
    if start_metrics_server(port=port):
        click.echo(f"metrics server running on {port}")
    else:
        click.echo("prometheus_client missing", err=True)


@codex.command()
@click.argument("text")
def tokenize(text: str) -> None:
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    tok = HFTokenizerAdapter.load()
    ids = tok.encode(text)
    click.echo(str(ids))


@codex.command()
def repo_map() -> None:
    """Print a simple summary of top-level directories and key files."""

    repo_root = Path(__file__).resolve().parents[3]
    entries: list[str] = []
    for item in sorted(repo_root.iterdir()):
        name = item.name
        # Skip hidden files and directories (e.g. .git, .cache)
        if name.startswith("."):
            continue
        if item.is_dir():
            entries.append(f"[dir] {name}/")
        else:
            entries.append(f" {name}")

    click.echo("\n".join(entries))


@codex.command()
@click.option(
    "--config",
    default="configs/eval/base.yaml",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to the evaluation configuration.",
)
@click.argument("overrides", nargs=-1)
@click.option(
    "--metrics-only",
    is_flag=True,
    help="Print only the `metrics` mapping to stdout (machine-readable).",
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Override the evaluation seed (best-effort determinism).",
)
@click.option(
    "--log-metrics",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Optional NDJSON file to append the aggregated metrics record.",
)
@click.option(
    "--run-id",
    type=str,
    default=None,
    help="Optional run identifier to attach to NDJSON records.",
)
def evaluate(
    config: str,
    overrides: tuple[str, ...],
    metrics_only: bool,
    seed: int | None,
    log_metrics: str | None,
    run_id: str | None,
) -> None:
    from codex_ml.eval.runner import EvaluationError, run_evaluation

    try:
        cfg_obj, _ = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    if seed is not None:
        cfg_obj.evaluation.seed = seed

    try:
        summary = run_evaluation(cfg_obj.evaluation, data_cfg=cfg_obj.data)
    except EvaluationError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    # Output behavior
    if metrics_only:
        click.echo(json.dumps(summary.get("metrics", {}), indent=2, sort_keys=True))
    else:
        click.echo(json.dumps(summary, indent=2, sort_keys=True))

    if log_metrics:
        out_path = Path(log_metrics)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            dataset_cfg_path = getattr(cfg_obj.evaluation, "dataset_path", None)
            record_run_id = run_id or summary.get("run_id")
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config_path": str(Path(config).resolve()),
                "dataset_path": (
                    str(Path(dataset_cfg_path).resolve()) if dataset_cfg_path else None
                ),
                "metrics": summary.get("metrics", {}),
                "num_records": summary.get("num_records", 0),
                "run_id": record_run_id,
            }
            # Prefer explicit run_id flag; fall back to summary's run_id if present.
            NDJSONLogger(out_path, run_id=record_run_id).log(record)
        except Exception as exc:  # pragma: no cover - Click handles presentation
            raise click.ClickException(f"failed to append metrics NDJSON: {exc}") from exc

    provenance_dir = Path(cfg_obj.evaluation.output_dir) / "provenance"
    _emit_provenance_summary(provenance_dir)


@codex.command("prepare-data")
@click.option(
    "--config",
    default="configs/data/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the data preparation configuration.",
)
@click.argument("overrides", nargs=-1)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Override the shuffle seed (best-effort determinism).",
)
def prepare_data(config: str, overrides: tuple[str, ...], seed: int | None) -> None:
    from codex_ml.data.loader import DataPreparationError, prepare_data_from_config

    try:
        cfg_obj, _ = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    if seed is not None:
        cfg_obj.data.shuffle_seed = seed

    try:
        result = prepare_data_from_config(cfg_obj.data)
    except DataPreparationError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    click.echo(json.dumps(result, indent=2, sort_keys=True))
    provenance_dir = Path(cfg_obj.data.cache_dir) / "provenance"
    _emit_provenance_summary(provenance_dir)


@codex.command("export-env")
@click.option(
    "--output",
    "output_dir",
    default="artifacts/environment",
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to write the environment snapshot.",
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Optional seed value to record with the snapshot.",
)
def export_env(output_dir: Path, seed: int | None) -> None:
    """Write a standalone environment snapshot."""

    export_environment(output_dir, seed=seed, command="export-env", stream=click.echo)


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    arg_list = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
        exit_code = 0
        try:
            codex(prog_name=sys.argv[0], args=arg_list, standalone_mode=False)
        except click.exceptions.Exit as exc:
            exit_code = exc.exit_code
        log_event(
            logger,
            "cli.finish",
            prog=sys.argv[0],
            status="ok" if exit_code == 0 else "error",
            exit_code=exit_code,
        )
        return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
