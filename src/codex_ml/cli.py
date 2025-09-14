"""Codex ML command line interface."""

from __future__ import annotations

import os

import click

try:  # optional dependency
    import yaml  # type: ignore

    _HAS_YAML = True
except Exception:  # pragma: no cover - optional
    yaml = None  # type: ignore
    _HAS_YAML = False

from codex_ml.eval.eval_runner import evaluate_datasets
from codex_ml.train_loop import run_training


@click.group()
def cli() -> None:
    """Codex ML tasks."""


@cli.command("train-model")
@click.option(
    "--config", default="configs/training/base.yaml", show_default=True, help="Training config path"
)
@click.option(
    "--mlflow.enable", "mlflow_enable", is_flag=True, default=False, help="Enable MLflow logging"
)
@click.option(
    "--mlflow.uri", default="file:./mlruns", show_default=True, help="MLflow tracking URI"
)
@click.option(
    "--mlflow.experiment", default="codex", show_default=True, help="MLflow experiment name"
)
@click.option(
    "--telemetry.enable",
    "telemetry_enable",
    is_flag=True,
    default=False,
    help="Enable Prometheus telemetry",
)
@click.option("--telemetry.port", default=8001, show_default=True, help="Telemetry server port")
def train_model(
    config: str,
    mlflow_enable: bool,
    mlflow_uri: str,
    mlflow_experiment: str,
    telemetry_enable: bool,
    telemetry_port: int,
) -> None:
    """Train a small model using demo loop."""
    if _HAS_YAML and os.path.exists(config):
        with open(config, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
    else:
        cfg = {}
    training_cfg = cfg.get("training", cfg)
    epochs = int(training_cfg.get("epochs", training_cfg.get("num_train_epochs", 1)))
    grad_accum = int(training_cfg.get("gradient_accumulation_steps", 1))
    run_training(
        epochs=epochs,
        grad_accum=grad_accum,
        mlflow_enable=mlflow_enable,
        mlflow_uri=mlflow_uri,
        mlflow_experiment=mlflow_experiment,
        telemetry_enable=telemetry_enable,
        telemetry_port=telemetry_port,
    )


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
    evaluate_datasets(datasets=ds, metrics=ms, output_dir=output_dir)


if __name__ == "__main__":  # pragma: no cover
    cli()
