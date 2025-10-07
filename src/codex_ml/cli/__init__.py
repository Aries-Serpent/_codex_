"""CLI entry updated to route via unified training orchestrator."""

from __future__ import annotations

from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training


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


__all__ = ["main_cli"]
