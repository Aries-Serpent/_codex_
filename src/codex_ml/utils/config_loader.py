from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from codex_ml.utils.yaml_support import MissingPyYAMLError, safe_load
from omegaconf import DictConfig, OmegaConf


def _flatten_training_section(cfg: Mapping[str, Any]) -> Dict[str, Any]:
    if "training" in cfg and isinstance(cfg["training"], Mapping):
        return dict(cfg["training"])
    return dict(cfg)


try:
    from hydra import compose, initialize_config_dir  # type: ignore
    from hydra.errors import MissingConfigException
except Exception:
    try:
        from hydra_core import compose, initialize_config_dir  # type: ignore
        from hydra_core.errors import MissingConfigException  # type: ignore
    except Exception as exc:  # pragma: no cover - import guard
        raise ImportError(
            "Hydra not available. Ensure `hydra-core` is installed and no local `hydra/`"
            " package shadows the installed distribution."
        ) from exc


def _find_cfg_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "configs" / "training"
        if candidate.is_dir():
            return candidate
    # default to repo-relative path if not found
    return here.parents[4] / "configs" / "training"


_CFG_DIR = _find_cfg_dir()
_PRIMARY = "base"


@dataclass
class TrainingDefaults:
    seed: int = 42
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 3
    logging: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "training": {
                "seed": self.seed,
                "lr": self.lr,
                "batch_size": self.batch_size,
                "epochs": self.epochs,
            },
            "logging": self.logging
            or {
                "enable_tensorboard": False,
                "enable_wandb": False,
                "mlflow_enable": False,
            },
        }


def load_training_cfg(
    *, allow_fallback: bool = True, overrides: Optional[list[str]] = None
) -> DictConfig:
    """Load Hydra config from ``configs/training/base.yaml`` with fallback.

    When the config file is missing and ``allow_fallback`` is ``True`` a
    deterministic programmatic configuration is returned.
    """

    overrides = overrides or []

    cfg_dir = _CFG_DIR
    if cfg_dir.is_dir() and (cfg_dir / f"{_PRIMARY}.yaml").is_file():
        # Hydra Compose API: https://hydra.cc/docs/advanced/compose_api/
        with initialize_config_dir(version_base=None, config_dir=str(cfg_dir)):
            return compose(config_name=_PRIMARY, overrides=overrides)

    if not allow_fallback:
        raise MissingConfigException(
            missing_cfg_file=f"{_CFG_DIR}/{_PRIMARY}.yaml",
            message="Config file missing",
        )

    base = TrainingDefaults().to_dict()
    cfg = OmegaConf.create(base)
    if overrides:
        for item in overrides:
            key, value = item.split("=", 1)
            try:
                parsed = safe_load(value)
            except MissingPyYAMLError as exc:
                raise RuntimeError(
                    'YAML overrides require PyYAML. Install it via ``pip install "PyYAML>=6.0"`` '
                    "before specifying overrides."
                ) from exc
            OmegaConf.update(cfg, key, parsed, merge=True)
    return cfg


def load_config(*, config_path: str) -> DictConfig:
    """Load a YAML config file into an OmegaConf DictConfig."""

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file {config_path} not found")
    with path.open("r", encoding="utf-8") as fh:
        try:
            data = safe_load(fh) or {}
        except MissingPyYAMLError as exc:
            raise RuntimeError(
                'PyYAML is required to parse configuration files. Install it via ``pip install "PyYAML>=6.0"`` '
                f"before loading {config_path}."
            ) from exc
    cfg = OmegaConf.create(data)
    if isinstance(data, dict):
        flattened = _flatten_training_section(data)
        for key, value in flattened.items():
            if key not in cfg:
                cfg[key] = value
        training_block = cfg.get("training")
        if isinstance(training_block, Mapping) and "lr" not in training_block:
            if "learning_rate" in training_block:
                training_block["lr"] = training_block["learning_rate"]
    return cfg
