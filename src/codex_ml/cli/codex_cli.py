from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

import click

from codex_ml.config import ConfigError, load_app_config
from codex_ml.telemetry import start_metrics_server
from codex_ml.tokenization import pipeline as tokenizer_pipeline
from codex_ml.utils.provenance import export_environment, load_environment_summary

DEFAULT_TOKENIZER_CONFIG = "configs/tokenization/base.yaml"
DEFAULT_TOKENIZER_JSON = "artifacts/tokenizers/default/tokenizer.json"


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
    "--stream-chunk-size",
    type=click.IntRange(min=1),
    default=None,
    help="Override the streaming chunk size in characters (defaults to 65536).",
)
@click.option("--dry-run", is_flag=True, help="Print the training plan without running.")
def tokenizer_train(config: str, stream_chunk_size: Optional[int], dry_run: bool) -> None:
    """Train a tokenizer according to the provided configuration."""
    try:
        out_dir = tokenizer_pipeline.run_train(
            config,
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
def tokenizer_encode(text: Optional[str], tokenizer_path: str) -> None:
    """Encode text with a trained tokenizer."""
    if text is None:
        text = click.get_text_stream("stdin").read()
    if text is None:
        text = ""
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
def train(config: str, overrides: Tuple[str, ...], resume: bool, seed: Optional[int]) -> None:
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

    try:
        run_functional_training(config=training_cfg, resume=resume)
        provenance_dir = Path(cfg_obj.training.output_dir) / "provenance"
        _emit_provenance_summary(provenance_dir)
        click.echo("training complete")
    except Exception as exc:  # pragma: no cover - Click handles presentation
        log_training_error("cli.train", str(exc), f"config={config} resume={resume}")
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
    click.echo("repo map not implemented")


@codex.command()
@click.option(
    "--config",
    default="configs/eval/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the evaluation configuration.",
)
@click.argument("overrides", nargs=-1)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Override the evaluation seed (best-effort determinism).",
)
def evaluate(config: str, overrides: Tuple[str, ...], seed: Optional[int]) -> None:
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

    click.echo(json.dumps(summary, indent=2, sort_keys=True))
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
def prepare_data(config: str, overrides: Tuple[str, ...], seed: Optional[int]) -> None:
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
def export_env(output_dir: Path, seed: Optional[int]) -> None:
    """Write a standalone environment snapshot."""

    export_environment(output_dir, seed=seed, command="export-env", stream=click.echo)


if __name__ == "__main__":  # pragma: no cover
    codex()
