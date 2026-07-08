"""
Codex Cli Module

This module provides functionality for codex cli.

Usage:
    from cli.codex_cli import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Sequence
from contextlib import nullcontext
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import click
import yaml

from codex_ml.cli.status_report import build_status_report
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.config import ConfigError, load_app_config
from codex_ml.monitoring.system_metrics import SystemMetricsLogger
from codex_ml.telemetry import start_metrics_server
from codex_ml.utils.provenance import export_environment, load_environment_summary
from codex_utils.ndjson import NDJSONLogger
from omegaconf import OmegaConf

_ = (ArgparseJSONParser, run_cmd)

DEFAULT_TOKENIZER_CONFIG = "configs/training/tokenization/base.yaml"
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


def _csv_list(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def _update_path(target: object, dotted_path: str, value: object) -> None:
    parts = dotted_path.split(".")
    current: object = target
    for part in parts[:-1]:
        next_obj: Optional[object] = None
        if isinstance(current, dict):
            next_obj = current.get(part)
            if next_obj is None:
                next_obj = {}
                current[part] = next_obj
        else:
            next_obj = getattr(current, part, None)
            if next_obj is None:
                next_obj = SimpleNamespace()
                setattr(current, part, next_obj)
        current = next_obj
    final_key = parts[-1]
    if isinstance(current, dict):
        current[final_key] = value
    else:
        setattr(current, final_key, value)


@click.group()
def codex() -> None:
    """Codex command line interface."""


def _emit_provenance_summary(provenance_dir: Path) -> None:
    summary = load_environment_summary(provenance_dir)
    if summary:
        click.echo(json.dumps(summary, sort_keys=True), err=True)


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
    config: str,
    streaming: Optional[bool],
    stream_chunk_size: Optional[int],
    dry_run: bool,
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
def tokenizer_encode(text: Optional[str], tokenizer_path: str) -> None:
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


def _hash_dataset(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@codex.command("config-sweep")
@click.option(
    "--base-config",
    default="configs/training/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Base config to seed the sweep metadata.",
)
@click.option(
    "--output",
    default="configs/training/sweeps/generated.yaml",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Path for the generated Hydra sweep file.",
)
@click.option(
    "--seeds",
    default="42",
    show_default=True,
    help="Comma-separated integer seeds for reproducibility sweeps.",
)
@click.option(
    "--dataset-version",
    default=None,
    help="Optional dataset version string recorded in the sweep metadata.",
)
@click.option(
    "--dataset-path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Optional dataset file to fingerprint for reproducibility metadata.",
)
@click.option(
    "--param",
    multiple=True,
    help="Additional sweep parameter in key=csvlist form (e.g. training.batch_size=4,8).",
)
@click.option(
    "--locked-override",
    multiple=True,
    help="Key=value pairs recorded under locked_overrides to document fixed settings.",
)
def config_sweep(
    base_config: Path,
    output: Path,
    seeds: str,
    dataset_version: Optional[str],
    dataset_path: Optional[Path],
    param: tuple[str, ...],
    locked_override: tuple[str, ...],
) -> None:
    """Generate a Hydra-friendly sweep config with reproducibility metadata."""

    try:
        seeds_list = [int(s) for s in _csv_list(seeds)]
    except ValueError as exc:  # pragma: no cover - Click shows context
        raise click.ClickException(f"invalid seed list: {seeds}") from exc

    sweeper_params: dict[str, str] = {"training.seed": ",".join(str(s) for s in seeds_list)}
    for item in param:
        if "=" not in item:
            raise click.ClickException("--param entries must look like key=csvlist")
        key, value = item.split("=", 1)
        sweeper_params[key.strip()] = value.strip()

    locked_overrides: dict[str, str] = {}
    for item in locked_override:
        if "=" not in item:
            raise click.ClickException("--locked-override entries must look like key=value")
        key, value = item.split("=", 1)
        locked_overrides[key.strip()] = value.strip()

    dataset_hash = None
    resolved_dataset_path = dataset_path
    if resolved_dataset_path is None:
        try:
            loaded = OmegaConf.load(base_config)
            maybe_path = loaded.get("training", {}).get("dataset", {}).get("train_path")
            if maybe_path:
                resolved_dataset_path = Path(maybe_path)
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
            resolved_dataset_path = None
    if resolved_dataset_path is not None and resolved_dataset_path.exists():
        dataset_hash = _hash_dataset(resolved_dataset_path)

    hydra_block = {
        "job": {"chdir": False},
        "run": {"dir": ".codex/hydra/runs/${now:%Y-%m-%d_%H-%M-%S}"},
        "sweep": {
            "dir": ".codex/hydra/multirun/${now:%Y-%m-%d_%H-%M-%S}",
            "subdir": "${hydra.job.override_dirname}",
        },
        "sweeper": {"params": sweeper_params},
    }

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_config": str(base_config),
        "dataset_version": dataset_version,
        "dataset_hash": dataset_hash,
        "seeds": seeds_list,
    }
    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        git_sha = ""
    if git_sha:
        metadata["git_sha"] = git_sha

    payload = {
        "defaults": ["_self_"],
        "hydra": hydra_block,
        "reproducibility": metadata,
        "locked_overrides": locked_overrides,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(payload), encoding="utf-8")
    click.echo(f"sweep config written to {output}")


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
@click.option(
    "--enable-peft",
    is_flag=True,
    help="Enable PEFT/LoRA hooks (requires CODEX_ENABLE_PEFT).",
)
@click.option(
    "--mlflow/--no-mlflow",
    "mlflow_toggle",
    default=None,
    help="Enable or disable MLflow logging regardless of config defaults.",
)
@click.option(
    "--system-metrics/--no-system-metrics",
    "system_metrics",
    default=False,
    help="Enable system metrics logging during training.",
)
@click.option(
    "--mlflow-tracking-uri",
    default=None,
    help="Tracking URI to forward MLflow runs (e.g., file:mlruns or http URL).",
)
@click.option(
    "--mlflow-run-name",
    default=None,
    help="Optional MLflow run name override.",
)
@click.option(
    "--mlflow-experiment",
    default=None,
    help="Optional MLflow experiment name override.",
)
def train(
    config: str,
    overrides: tuple[str, ...],
    resume: bool,
    seed: Optional[int],
    resume_from: Optional[str],
    enable_peft: bool,
    mlflow_toggle: Optional[bool],
    system_metrics: bool,
    mlflow_tracking_uri: Optional[str],
    mlflow_run_name: Optional[str],
    mlflow_experiment: Optional[str],
) -> None:
    """Train a language model using the Codex functional trainer."""
    from codex_ml.training import run_functional_training
    from codex_ml.utils.error_log import log_error as log_training_error

    try:
        cfg_obj, raw_cfg = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    training_cfg = getattr(raw_cfg, "training", raw_cfg)

    if seed is not None:
        if hasattr(raw_cfg, "training") and hasattr(raw_cfg.training, "seed"):
            raw_cfg.training.seed = seed
        else:
            raw_cfg.seed = seed
        cfg_obj.training.seed = seed

    if enable_peft:
        os.environ["CODEX_ENABLE_PEFT"] = "1"
        os.environ["CODEX_ML_ENABLE_PEFT"] = "1"
        if hasattr(cfg_obj.training, "enable_peft"):
            cfg_obj.training.enable_peft = True
        if hasattr(raw_cfg, "training") and hasattr(raw_cfg.training, "enable_peft"):
            raw_cfg.training.enable_peft = True
    else:
        os.environ.pop("CODEX_ENABLE_PEFT", None)
        os.environ.pop("CODEX_ML_ENABLE_PEFT", None)

    if mlflow_toggle is not None:
        for target in (cfg_obj.training, training_cfg):
            _update_path(target, "logging.mlflow_enable", mlflow_toggle)
            _update_path(target, "mlflow_enable", mlflow_toggle)

    if mlflow_tracking_uri:
        for target in (cfg_obj.training, training_cfg):
            _update_path(target, "logging.mlflow_tracking_uri", mlflow_tracking_uri)
            _update_path(target, "mlflow_tracking_uri", mlflow_tracking_uri)

    if mlflow_run_name:
        _update_path(training_cfg, "logging.mlflow_run_name", mlflow_run_name)

    if mlflow_experiment:
        _update_path(training_cfg, "logging.mlflow_experiment", mlflow_experiment)

    if resume_from:
        if hasattr(cfg_obj.training, "resume_from"):
            cfg_obj.training.resume_from = resume_from
        training_cfg.resume_from = resume_from
        resume = True

    metrics_logger: Optional[SystemMetricsLogger] = None
    if system_metrics:
        metrics_path = Path(cfg_obj.training.output_dir) / "logs" / "system_metrics.ndjson"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_logger = SystemMetricsLogger(metrics_path)

    try:
        with metrics_logger if metrics_logger else nullcontext():
            run_functional_training(config=training_cfg, resume=resume)
        provenance_dir = Path(cfg_obj.training.output_dir) / "provenance"
        _emit_provenance_summary(provenance_dir)
        click.echo("Training complete")
    except (IOError, OSError) as exc:  # pragma: no cover - Click handles presentation
        log_training_error(
            "cli.train",
            str(exc),
            f"config={config} resume={resume} resume_from={resume_from}",
        )
        raise click.ClickException(str(exc)) from exc


@codex.command()
@click.argument("manifest", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option(
    "--mlflow/--no-mlflow",
    "mlflow_toggle",
    default=None,
    help="Enable or disable MLflow logging when resuming from a manifest.",
)
@click.option("--mlflow-tracking-uri", default=None, help="Optional MLflow tracking URI override.")
@click.option("--mlflow-run-name", default=None, help="Optional MLflow run name override.")
@click.option("--mlflow-experiment", default=None, help="Optional MLflow experiment override.")
def resume(
    manifest: str,
    mlflow_toggle: Optional[bool],
    mlflow_tracking_uri: Optional[str],
    mlflow_run_name: Optional[str],
    mlflow_experiment: Optional[str],
) -> None:
    """Resume training from a manifest emitted by the HF trainer."""
    from codex_ml.training import run_functional_training

    manifest_path = Path(manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    checkpoint = (
        data.get("best_checkpoint") or data.get("last_checkpoint") or data.get("resume_from")
    )
    config_path = data.get("config_path") or "configs/training/base.yaml"
    if not checkpoint:
        raise click.ClickException("manifest missing checkpoint information")

    try:
        cfg_obj, raw_cfg = load_app_config(config_path, tuple())
    except ConfigError as exc:
        type(exc).__name__
        logger.debug("ConfigError: <ERROR_TYPE>")
        raise click.ClickException(str(exc)) from exc

    training_cfg = getattr(raw_cfg, "training", raw_cfg)
    if hasattr(training_cfg, "resume_from"):
        training_cfg.resume_from = checkpoint

    if mlflow_toggle is not None:
        _update_path(training_cfg, "logging.mlflow_enable", mlflow_toggle)
        _update_path(training_cfg, "mlflow_enable", mlflow_toggle)
    if mlflow_tracking_uri:
        _update_path(training_cfg, "logging.mlflow_tracking_uri", mlflow_tracking_uri)
        _update_path(training_cfg, "mlflow_tracking_uri", mlflow_tracking_uri)
    if mlflow_run_name:
        _update_path(training_cfg, "logging.mlflow_run_name", mlflow_run_name)
    if mlflow_experiment:
        _update_path(training_cfg, "logging.mlflow_experiment", mlflow_experiment)
    try:
        run_functional_training(config=training_cfg, resume=True)
        provenance_dir = Path(cfg_obj.training.output_dir) / "provenance"
        _emit_provenance_summary(provenance_dir)
        click.echo(f"resumed training from {checkpoint}")
    except (IOError, OSError) as exc:  # pragma: no cover - Click handles presentation
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
@click.option(
    "--reasoning",
    is_flag=True,
    help=(
        "Emit reasoning-specific control surface entries (curriculum preset, "
        "trace_mode, rollout ring, evaluation preset, deployment preset)."
    ),
)
def repo_map(reasoning: bool) -> None:
    """Print a repository summary (optionally including reasoning knobs)."""

    from codex_ml.cli.repo_map import render_repo_map

    try:
        click.echo(render_repo_map(reasoning=reasoning))
    except TypeError as e:
        type(e).__name__
        logger.debug("TypeError: <ERROR_TYPE>")
        logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
        # Back-compat with older render_repo_map signatures lacking the flag.
        click.echo(render_repo_map())


@codex.command()
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to deployment preset YAML (e.g. configs/deploy/reasoning_pod.yaml).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Required flag. Perform offline validation only; never touch live infra.",
)
@click.option(
    "--run-metadata-dir",
    default=Path("runs/train_loop"),
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory containing run_metadata.json from the latest TrainLoop run.",
)
def deploy(config: Path, dry_run: bool, run_metadata_dir: Path) -> None:
    """Validate reasoning pod deployment readiness in dry-run mode."""

    from codex_ml.cli.deploy import run_deploy_dry_run

    if not dry_run:
        click.secho(
            "DEPLOYMENT BLOCKED: --dry-run is required in this rollout ring.",
            err=True,
        )
        raise SystemExit(1)

    try:
        summary = run_deploy_dry_run(
            config_path=config,
            dry_run=dry_run,
            run_metadata_dir=run_metadata_dir,
        )
    except RuntimeError as exc:
        type(exc).__name__
        logger.debug("RuntimeError: <ERROR_TYPE>")
        click.secho(f"DEPLOYMENT BLOCKED: {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(json.dumps(summary, indent=2))


@codex.command("status-report")
@click.option(
    "--run-metadata-dir",
    default=Path("runs/train_loop"),
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help=(
        "Directory containing run_metadata.json / evaluation.json / reasoning.json "
        "from the most recent TrainLoop run."
    ),
)
def status_report(run_metadata_dir: Path) -> None:
    """Summarize offline promotion readiness for `0D_base_` → `main`."""

    summary = build_status_report(run_metadata_dir)
    click.echo(json.dumps(summary, indent=2))


@codex.command()
@click.option(
    "--config",
    default="configs/evaluation/base.yaml",
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
    "--metrics-sink",
    type=str,
    default="ndjson",
    show_default=True,
    help="Comma-separated metrics sinks to emit (choices: none,ndjson,csv).",
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
@click.option(
    "--metrics-path",
    type=click.Path(dir_okay=False, path_type=str),
    default=None,
    help="Path for the secondary metrics sink when enabled.",
)
def evaluate(
    config: str,
    overrides: tuple[str, ...],
    metrics_only: bool,
    metrics_sink: str,
    seed: Optional[int],
    log_metrics: Optional[str],
    run_id: Optional[str],
    metrics_path: Optional[str],
) -> None:
    from codex_ml.eval.runner import EvaluationError, run_evaluation

    try:
        cfg_obj, _ = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    if seed is not None:
        cfg_obj.evaluation.seed = seed
    if metrics_sink:
        cfg_obj.evaluation.metrics_sink = metrics_sink

    if hasattr(cfg_obj.evaluation, "metrics_sink"):
        cfg_obj.evaluation.metrics_sink = metrics_sink
    if metrics_path and hasattr(cfg_obj.evaluation, "metrics_sink_path"):
        cfg_obj.evaluation.metrics_sink_path = metrics_path

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
        except (IOError, OSError) as exc:  # pragma: no cover - Click handles presentation
            raise click.ClickException(f"failed to append metrics NDJSON: {exc}") from exc

    provenance_dir = Path(cfg_obj.evaluation.output_dir) / "provenance"
    _emit_provenance_summary(provenance_dir)


@codex.command("prepare-data")
@click.option(
    "--config",
    default="configs/training/data/base.yaml",
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
def prepare_data(config: str, overrides: tuple[str, ...], seed: Optional[int]) -> None:
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


def main(argv: Optional[Sequence[str]] = None) -> int:
    logger = init_json_logging()
    arg_list = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
        exit_code = 0
        try:
            codex.main(prog_name=sys.argv[0], args=arg_list, standalone_mode=False)
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
