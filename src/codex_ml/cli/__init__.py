"""CLI entry updated to route via unified training orchestrator."""

from __future__ import annotations

import os
import sys
from typing import Sequence

from codex_ml.utils.optional import optional_import
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = (ArgparseJSONParser, run_cmd)

click, _HAS_CLICK = optional_import("click")
yaml, _HAS_YAML = optional_import("yaml")
torch, _HAS_TORCH = optional_import("torch")


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
    def train_model(
        config: str,
        mlflow_enable: bool,
        mlflow_uri: str,
        mlflow_experiment: str,
        telemetry_enable: bool,
        telemetry_port: int,
    ) -> None:
        """Train a small model using demo loop."""
        if not _HAS_TORCH:
            from codex_ml.utils.error_log import log_error

            message = (
                "PyTorch is required for 'train-model'. Install the optional extra via"
                " 'pip install codex_ml[torch]'"
            )
            log_error("codex_ml.cli.train_model", message, f"config={config}")
            click.echo(f"[error] {message}", err=True)
            raise SystemExit(1)
        if _HAS_YAML and os.path.exists(config):
            with open(config, "r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
        else:
            cfg = {}
        training_cfg = cfg.get("training", cfg)
        epochs = int(training_cfg.get("epochs", training_cfg.get("num_train_epochs", 1)))
        grad_accum = int(training_cfg.get("gradient_accumulation_steps", 1))
        from codex_ml.train_loop import run_training

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
        from codex_ml.eval.eval_runner import evaluate_datasets

        evaluate_datasets(datasets=ds, metrics=ms, output_dir=output_dir)

else:  # pragma: no cover - optional dependency path

    def cli(*_: object, **__: object) -> None:
        raise ImportError("click is required to use codex_ml.cli entry points")


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    arg_list = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
        exit_code = 0
        if _HAS_CLICK:
            try:
                cli(prog_name=sys.argv[0], args=arg_list, standalone_mode=False)
            except click.exceptions.Exit as exc:  # type: ignore[name-defined]
                exit_code = exc.exit_code
        else:
            try:
                cli(*arg_list)
            except SystemExit as exc:
                exit_code = exc.code if isinstance(exc.code, int) else 1
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


__all__ = ["main_cli"]
