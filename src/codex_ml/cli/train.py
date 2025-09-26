"""Hydra-powered entrypoint for the toy training loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import hydra
from codex_ml.train_loop import run_training
from hydra.utils import to_absolute_path
from omegaconf import DictConfig, ListConfig, OmegaConf


def _to_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    return Path(to_absolute_path(str(value)))


def _cfg_to_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, DictConfig):
        container = OmegaConf.to_container(value, resolve=True)
        if isinstance(container, dict):
            return dict(container)
        return {}
    if isinstance(value, dict):
        return dict(value)
    return {}


def _cfg_to_list(value: Any) -> list[Any]:
    if isinstance(value, ListConfig):
        return list(value)
    if isinstance(value, list):
        return list(value)
    if value is None:
        return []
    return [value]


@hydra.main(version_base=None, config_path="../../../configs/train", config_name="default")
def main(cfg: DictConfig) -> None:
    artifacts_cfg = _cfg_to_dict(cfg.get("artifacts"))
    art_dir = _to_path(cfg.get("artifacts_dir") or artifacts_cfg.get("dir"))

    dataset_cfg = cfg.get("dataset")
    dataset_sources_raw = []
    dataset_cache_dir = None
    if isinstance(dataset_cfg, (DictConfig, dict)):
        dataset_cfg_dict = _cfg_to_dict(dataset_cfg)
        dataset_sources_raw = _cfg_to_list(dataset_cfg_dict.get("sources"))
        dataset_cache_dir = dataset_cfg_dict.get("cache_dir")
    else:
        dataset_sources_raw = _cfg_to_list(cfg.get("dataset_sources"))
        dataset_cache_dir = cfg.get("dataset_cache_dir")
    dataset_sources = [p for p in (_to_path(item) for item in dataset_sources_raw) if p is not None]
    dataset_cache_path = _to_path(dataset_cache_dir)

    checkpoint_cfg = _cfg_to_dict(cfg.get("checkpoint"))
    checkpoint_dir = _to_path(checkpoint_cfg.get("dir") or checkpoint_cfg.get("path"))
    resume = bool(checkpoint_cfg.get("resume", checkpoint_cfg.get("restore", False)))
    retention_policy = _cfg_to_dict(checkpoint_cfg.get("retention")) or None

    model_cfg_container = cfg.get("model")
    model_cfg_dict: Dict[str, Any] = {}
    model_name = cfg.get("model_name")
    if isinstance(model_cfg_container, (DictConfig, dict)):
        model_container_dict = _cfg_to_dict(model_cfg_container)
        model_name = model_name or model_container_dict.get("name")
        model_cfg_dict = _cfg_to_dict(model_container_dict.get("cfg"))
    else:
        model_cfg_dict = _cfg_to_dict(cfg.get("model_cfg"))

    amp_cfg = cfg.get("amp")
    amp_enabled = False
    amp_dtype = None
    if isinstance(amp_cfg, (DictConfig, dict)):
        amp_cfg_dict = _cfg_to_dict(amp_cfg)
        amp_enabled = bool(amp_cfg_dict.get("enable", amp_cfg_dict.get("enabled", False)))
        amp_dtype = amp_cfg_dict.get("dtype")
    elif amp_cfg is not None:
        amp_enabled = bool(amp_cfg)
        amp_dtype = cfg.get("amp_dtype")

    lora_cfg_container = cfg.get("lora")
    lora_cfg_dict = (
        _cfg_to_dict(lora_cfg_container)
        if isinstance(lora_cfg_container, (DictConfig, dict))
        else {}
    )
    lora_enabled = bool(lora_cfg_dict.get("enabled", lora_cfg_dict.get("enable", False)))
    lora_cfg = _cfg_to_dict(lora_cfg_dict.get("cfg")) or {
        k: v for k, v in lora_cfg_dict.items() if k not in {"enabled", "enable"}
    }

    mlflow_cfg = _cfg_to_dict(cfg.get("mlflow"))
    telemetry_cfg = _cfg_to_dict(cfg.get("telemetry"))
    telemetry_port = telemetry_cfg.get("port")
    if telemetry_port is not None:
        telemetry_port = int(telemetry_port)

    scheduler_cfg = _cfg_to_dict(cfg.get("scheduler"))

    reproducibility_cfg = _cfg_to_dict(cfg.get("reproducibility"))
    deterministic_cudnn = bool(reproducibility_cfg.get("cudnn_deterministic", False))

    seed = cfg.get("seed", None)
    grad_accum = cfg.get("grad_accum", 1)
    steps_per_epoch = cfg.get("steps_per_epoch", 4)
    epochs = cfg.get("epochs", 1)

    learning_rate = cfg.get("learning_rate")
    optimizer_cfg = _cfg_to_dict(cfg.get("optimizer"))
    if learning_rate is None:
        learning_rate = optimizer_cfg.get("learning_rate")
    learning_rate = float(learning_rate) if learning_rate is not None else 1e-3

    batch_size = cfg.get("batch_size")
    if batch_size is None:
        batch_size = optimizer_cfg.get("batch_size")

    device_raw = cfg.get("device")
    device = str(device_raw) if device_raw not in (None, "") else None

    dtype_raw = cfg.get("dtype")
    dtype = str(dtype_raw) if dtype_raw not in (None, "") else None

    run_training(
        epochs=int(epochs),
        grad_accum=int(grad_accum),
        steps_per_epoch=int(steps_per_epoch),
        learning_rate=float(learning_rate),
        batch_size=int(batch_size) if batch_size is not None else None,
        mlflow_enable=bool(mlflow_cfg.get("enable", mlflow_cfg.get("enabled", False))),
        mlflow_uri=mlflow_cfg.get("uri"),
        mlflow_experiment=mlflow_cfg.get("experiment"),
        telemetry_enable=bool(telemetry_cfg.get("enable", telemetry_cfg.get("enabled", False))),
        telemetry_port=telemetry_port,
        seed=int(seed) if seed is not None else None,
        art_dir=art_dir,
        dataset_sources=dataset_sources,
        dataset_cache_dir=dataset_cache_path,
        model_name=model_name,
        model_cfg=model_cfg_dict,
        lora=lora_enabled,
        lora_cfg=lora_cfg,
        device=device,
        dtype=dtype,
        amp=amp_enabled,
        amp_dtype=amp_dtype,
        checkpoint_dir=checkpoint_dir,
        resume=bool(resume),
        scheduler_cfg=scheduler_cfg or None,
        deterministic_cudnn=deterministic_cudnn,
        retention_policy=retention_policy,
        run_config=OmegaConf.to_container(cfg, resolve=True),
    )


if __name__ == "__main__":  # pragma: no cover
    main()
