"""Codex ML command line interface."""

from __future__ import annotations

import os
from typing import Any

from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
from codex_ml.utils.error_log import log_error
from codex_ml.utils.optional import optional_import

click, _HAS_CLICK = optional_import("click")
yaml, _HAS_YAML = optional_import("yaml")
torch, _HAS_TORCH = optional_import("torch")


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


main = main_cli

__all__ = ["cli", "main_cli", "main"]
