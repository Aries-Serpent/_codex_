"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from codex_ml.cli import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Optional, Union

from codex.logging.structured_logger import logger
from codex_ml.utils.error_log import log_error
from codex_ml.utils.optional import optional_import

from . import utils

click, _HAS_CLICK = optional_import("click")
yaml, _HAS_YAML = optional_import("yaml")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex_ml")
    sub = parser.add_subparsers(dest="command")
    parser.set_defaults(func=lambda *_: parser.print_help() or 0)  # type: ignore[func-returns-value]

    ndjson = sub.add_parser("ndjson-summary", help="Summarize metrics.ndjson shards")
    ndjson.add_argument("--input", required=True, help="Path to metrics.ndjson file or directory")
    ndjson.add_argument(
        "--output",
        choices=("stdout", "csv"),
        default="stdout",
        help="Emit JSON to stdout or write a CSV summary",
    )
    ndjson.add_argument(
        "--pattern",
        default="metrics.ndjson*",
        help="Glob pattern for shard discovery when --input is a directory",
    )
    ndjson.add_argument(
        "--dest",
        help="Destination path when writing CSV output (defaults to metrics_summary.csv)",
    )
    ndjson.set_defaults(func=_cmd_ndjson_summary)

    metrics = sub.add_parser(
        "metrics",
        help="Metrics NDJSON utilities (ingest/summary)",
    )
    metrics.add_argument(
        "metrics_args",
        nargs=argparse.REMAINDER,
        help=argparse.SUPPRESS,
    )
    metrics.set_defaults(func=_cmd_metrics)

    config = sub.add_parser("config", help="Hydra config helpers")
    config.set_defaults(func=_cmd_config)

    hydra_train = sub.add_parser(
        "hydra-train",
        help="Run training via Hydra defaults (if hydra installed)",
        allow_abbrev=False,
    )
    hydra_train.add_argument(
        "hydra_args",
        nargs=argparse.REMAINDER,
        help="Additional Hydra overrides (e.g. train.epochs=2)",
    )
    hydra_train.set_defaults(func=_cmd_hydra_train)

    hydra = sub.add_parser(
        "hydra",
        help="Hydra defaults utilities",
    )
    hydra.add_argument(
        "hydra_args",
        nargs=argparse.REMAINDER,
        help=argparse.SUPPRESS,
    )
    hydra.set_defaults(func=_cmd_hydra)

    track = sub.add_parser("track", help="Experiment tracking utilities")
    track.add_argument(
        "track_args",
        nargs=argparse.REMAINDER,
        help=argparse.SUPPRESS,
    )
    track.set_defaults(func=_cmd_track)

    tracking = sub.add_parser("tracking", help="Tracking utilities (offline-friendly)")
    tracking_sub = tracking.add_subparsers(dest="tracking_cmd", required=True)
    tracking_bootstrap = tracking_sub.add_parser(
        "bootstrap",
        help="Initialize MLflow/W&B locally",
    )
    tracking_bootstrap.add_argument("--mlflow", action="store_true")
    tracking_bootstrap.add_argument("--mlflow-uri", default="file:./mlruns")
    tracking_bootstrap.add_argument("--wandb", action="store_true")
    tracking_bootstrap.add_argument("--project")
    tracking_bootstrap.add_argument(
        "--mode",
        default="offline",
        choices=["online", "offline", "disabled"],
    )
    tracking_bootstrap.set_defaults(func=_cmd_tracking_bootstrap)

    return parser


def _cmd_ndjson_summary(args: argparse.Namespace) -> int:
    import json as _json
    from pathlib import Path as _Path

    from . import ndjson_summary

    run_dir = _Path(getattr(args, "input", "."))
    fmt = getattr(args, "output", "stdout")
    dest = getattr(args, "dest", None)

    if fmt == "stdout":
        rows = ndjson_summary._load_rows(run_dir)
        metrics_agg: dict[str, dict[str, Any]] = {}
        for row in rows:
            metric_name = str(row.get("metric") or row.get("key") or "")
            if not metric_name:
                continue
            val = row.get("value")
            if val is None:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            slot = metrics_agg.setdefault(metric_name, {"count": 0, "min": None, "max": None})
            slot["count"] += 1
            slot["min"] = val if slot["min"] is None else min(slot["min"], val)
            slot["max"] = val if slot["max"] is None else max(slot["max"], val)
        logger.info(_json.dumps({"rows": len(rows), "metrics": metrics_agg}))
        return 0

    ndjson_summary.summarize(run_dir, fmt, dest)
    return 0


def _cmd_metrics(args: argparse.Namespace) -> int:
    from . import metrics_cli

    metrics_args = list(args.metrics_args or [])
    return metrics_cli.main(metrics_args)


def _cmd_config(args: argparse.Namespace) -> int:
    from . import config as _config

    config_args = list(getattr(args, "_extras", []) or [])
    return _config.main(config_args)


def _cmd_hydra(args: argparse.Namespace) -> int:
    from . import hydra_audit

    hydra_args = list(args.hydra_args or [])
    return hydra_audit.main(hydra_args)


def _cmd_track(args: argparse.Namespace) -> int:
    from . import offline_bootstrap

    track_args = list(args.track_args or [])
    return offline_bootstrap.main(track_args)


def _cmd_tracking_bootstrap(args: argparse.Namespace) -> int:
    from . import tracking_cli as _tracking

    argv = ["bootstrap"]
    if args.mlflow:
        argv.append("--mlflow")
    argv.extend(["--mlflow-uri", args.mlflow_uri])
    if args.wandb:
        argv.append("--wandb")
    if args.project:
        argv.extend(["--project", args.project])
    argv.extend(["--mode", args.mode])
    return _tracking.main(argv)


def package_main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args, extras = parser.parse_known_args(sys.argv[1:] if argv is None else argv)
    args._extras = extras
    if extras and getattr(args, "func", None) is not _cmd_config:
        parser.error(f"unrecognized arguments: {' '.join(extras)}")
    return int(args.func(args) or 0)


def _cmd_hydra_train(args: argparse.Namespace) -> int:
    from .hydra_entry import main as _hydra_main

    extra = args.hydra_args or []
    return _hydra_main(extra)


def _load_training_config(path: str) -> dict[str, Any]:
    if not path:
        return {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Training config not found: {path}")
    if not _HAS_YAML:
        message = (
            f"PyYAML is not installed; cannot load training config from '{path}'. "
            "Proceeding with default training configuration values."
        )
        log_error(
            "codex_ml.cli._load_training_config",
            message,
            f"path={path}",
        )
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main_cli(
    *,
    epochs: int = 1,
    grad_accum: int = 1,
    mlflow_enable: bool = False,
    mlflow_uri: Optional[str] = None,  # retained for compatibility
    **_: object,
) -> None:
    from codex_ml.training.unified_training import (
        UnifiedTrainingConfig,
        run_unified_training,
    )

    cfg = UnifiedTrainingConfig(
        model_name="cli-model",
        epochs=epochs,
        grad_accum=grad_accum,
        mlflow_enable=mlflow_enable,
        output_dir="runs/unified_cli",
    )
    run_unified_training(cfg)


def _train_model_from_click(
    *,
    config: str,
    mlflow_enable: bool,
    mlflow_uri: str,
    mlflow_experiment: str,
    telemetry_enable: bool,
    telemetry_port: int,
) -> None:
    del mlflow_experiment  # retained for CLI compatibility
    del telemetry_enable
    del telemetry_port

    _torch_module, has_torch = optional_import("torch")
    if not has_torch:
        message = (
            "PyTorch is required for 'train-model'. Install the optional extra via"
            " 'pip install codex_ml[torch]'"
        )
        log_error("codex_ml.cli.train_model", message, f"config={config}")
        if _HAS_CLICK:
            click.echo(f"[error] {message}", err=True)
        raise SystemExit(1)

    cfg = _load_training_config(config)
    training_cfg = cfg.get("training", cfg)
    epochs = int(training_cfg.get("epochs", training_cfg.get("num_train_epochs", 1)))
    grad_accum = int(training_cfg.get("gradient_accumulation_steps", 1))

    main_cli(
        epochs=epochs,
        grad_accum=grad_accum,
        mlflow_enable=mlflow_enable,
        mlflow_uri=mlflow_uri,
    )


if _HAS_CLICK:

    @click.group()
    def cli() -> None:
        """Codex ML tasks."""

    @cli.command("train-model")
    @click.option(
        "--config",
        default="configs/training/base.yaml",
        show_default=True,
        help="Training config path",
    )
    @click.option(
        "--mlflow-enable",
        "mlflow_enable",
        is_flag=True,
        default=False,
        help="Enable MLflow logging",
    )
    @click.option(
        "--mlflow-uri",
        default="file:./mlruns",
        show_default=True,
        help="MLflow tracking URI",
    )
    @click.option(
        "--mlflow-experiment",
        default="codex",
        show_default=True,
        help="MLflow experiment name",
    )
    @click.option(
        "--telemetry.enable",
        "telemetry_enable",
        is_flag=True,
        default=False,
        help="Enable Prometheus telemetry",
    )
    @click.option(
        "--telemetry-port",
        default=8001,
        show_default=True,
        help="Telemetry server port",
    )
    def train_model(**kwargs: Any) -> None:
        """Train a model using the unified training pipeline."""

        _train_model_from_click(**kwargs)

    @cli.command()
    @click.option("--datasets", default="", help="Comma separated dataset names")
    @click.option(
        "--metrics",
        default="accuracy",
        show_default=True,
        help="Comma separated metric names",
    )
    @click.option("--output-dir", default="runs/eval", show_default=True, help="Output directory")
    def evaluate(datasets: str, metrics: str, output_dir: str) -> None:
        """Evaluate datasets with metrics."""
        ds = [d.strip() for d in datasets.split(",") if d.strip()]
        ms = [m.strip() for m in metrics.split(",") if m.strip()]
        from codex_ml.eval.eval_runner import evaluate_datasets

        evaluate_datasets(datasets=ds, metrics=ms, output_dir=output_dir)

else:  # pragma: no cover - optional dependency path

    def cli(*_: object, **__: object) -> None:
        raise ImportError("click is required to use codex_ml.cli entry points")


if __name__ == "__main__":  # pragma: no cover
    cli()


try:
    from .codex_cli import app as infer  # type: ignore[attr-defined]
except (ImportError, AttributeError):  # pragma: no cover - optional CLI wiring
    infer = cli


main = package_main

__all__ = ["cli", "infer", "main", "main_cli"]
