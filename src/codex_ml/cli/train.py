"""Hydra-powered entrypoint for the toy training loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import hydra
from codex_ml.train_loop import run_training
from hydra.utils import to_absolute_path
from omegaconf import DictConfig


def _to_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    return Path(to_absolute_path(str(value)))


@hydra.main(version_base=None, config_path="../../configs/train", config_name="default")
def main(cfg: DictConfig) -> None:
    model_cfg: Dict[str, Any] = dict(cfg.model.get("cfg", {}))
    art_dir = _to_path(cfg.artifacts_dir)
    dataset_sources = [_to_path(item) for item in cfg.dataset_sources]
    checkpoint_dir = _to_path(cfg.checkpoint.dir)
    run_training(
        epochs=int(cfg.epochs),
        grad_accum=int(cfg.grad_accum),
        learning_rate=float(cfg.learning_rate),
        batch_size=int(cfg.batch_size),
        mlflow_enable=bool(cfg.mlflow.enable),
        mlflow_uri=str(cfg.mlflow.uri),
        mlflow_experiment=str(cfg.mlflow.experiment),
        telemetry_enable=bool(cfg.telemetry.enable),
        telemetry_port=int(cfg.telemetry.port),
        seed=int(cfg.seed),
        art_dir=art_dir,
        dataset_sources=[p for p in dataset_sources if p is not None],
        model_name=str(cfg.model.name),
        model_cfg=model_cfg,
        lora=bool(cfg.lora.enabled),
        lora_cfg=dict(cfg.lora.get("cfg", {})),
        device=str(cfg.device) if cfg.device else None,
        dtype=cfg.dtype,
        amp=bool(cfg.amp.enable),
        amp_dtype=cfg.amp.dtype,
        checkpoint_dir=checkpoint_dir,
        resume=bool(cfg.checkpoint.resume),
    )


if __name__ == "__main__":  # pragma: no cover
    main()
