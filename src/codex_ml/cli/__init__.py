"""Codex ML command line interface."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
from codex_ml.utils.error_log import log_error
from codex_ml.utils.optional import optional_import

click, _HAS_CLICK = optional_import("click")
yaml, _HAS_YAML = optional_import("yaml")
torch, _HAS_TORCH = optional_import("torch")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex_ml")
    sub = parser.add_subparsers(dest="command")
    parser.set_defaults(func=lambda *_: parser.print_help() or 0)

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

    return parser


def _cmd_ndjson_summary(args: argparse.Namespace) -> int:
    from . import ndjson_summary

    return ndjson_summary.summarize(args)


def _cmd_metrics(args: argparse.Namespace) -> int:
    from . import metrics_cli

    metrics_args = list(args.metrics_args or [])
    return metrics_cli.main(metrics_args)


def _cmd_hydra(args: argparse.Namespace) -> int:
    from . import hydra_audit

    hydra_args = list(args.hydra_args or [])
    return hydra_audit.main(hydra_args)


def _cmd_track(args: argparse.Namespace) -> int:
    from . import offline_bootstrap

    track_args = list(args.track_args or [])
    return offline_bootstrap.main(track_args)


def package_main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    return int(args.func(args) or 0)


def _cmd_hydra_train(args):
    from .hydra_entry import main as _hydra_main

    extra = args.hydra_args or []
    return _hydra_main(extra)


def _load_training_config(path: str) -> dict[str, Any]:
    if not path or not _HAS_YAML or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return (yaml.safe_load(fh) or {}) if _HAS_YAML else {}


def main_cli(
    *,
    epochs: int = 1,
    grad_accum: int = 1,
    mlflow_enable: bool = False,
    mlflow_uri: str | None = None,  # retained for compatibility
    **_: object,
) -> None:
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

    if not _HAS_TORCH:
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
        "--mlflow-uri", default="file:./mlruns", show_default=True, help="MLflow tracking URI"
    )
    @click.option(
        "--mlflow-experiment", default="codex", show_default=True, help="MLflow experiment name"
    )
    @click.option(
        "--telemetry.enable",
        "telemetry_enable",
        is_flag=True,
        default=False,
        help="Enable Prometheus telemetry",
    )
    @click.option("--telemetry-port", default=8001, show_default=True, help="Telemetry server port")
    def train_model(**kwargs: Any) -> None:  # type: ignore[ban-all-any]
        """Train a model using the unified training pipeline."""

        _train_model_from_click(**kwargs)

    @cli.command()
    @click.option("--datasets", default="", help="Comma separated dataset names")
    @click.option(
        "--metrics", default="accuracy", show_default=True, help="Comma separated metric names"
    )
    @click.option("--output-dir", default="runs/eval", show_default=True, help="Output directory")
    def evaluate(datasets: str, metrics: str, output_dir: str) -> None:
        """Evaluate datasets with metrics."""
        ds = [d.strip() for d in datasets.split(",") if d.strip()] or []
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
except Exception:  # pragma: no cover - optional CLI wiring
    infer = cli  # type: ignore[assignment]


main = package_main

__all__ = ["cli", "main_cli", "main"]
