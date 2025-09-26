from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from codex_ml.utils.yaml_support import MissingPyYAMLError, safe_load

try:  # pragma: no cover - optional dependency
    from hydra import compose, initialize_config_dir  # type: ignore
    from hydra.errors import MissingConfigException

    _HYDRA_AVAILABLE = True
except Exception:  # pragma: no cover - import guard
    try:
        from hydra_core import compose, initialize_config_dir  # type: ignore
        from hydra_core.errors import MissingConfigException  # type: ignore

        _HYDRA_AVAILABLE = True
    except Exception:  # pragma: no cover - import guard
        compose = None  # type: ignore[assignment]
        initialize_config_dir = None  # type: ignore[assignment]

        class MissingConfigException(RuntimeError):
            """Fallback error used when Hydra is unavailable."""

            def __init__(self, *, missing_cfg_file: str, message: str) -> None:
                super().__init__(message)
                self.missing_cfg_file = missing_cfg_file

        _HYDRA_AVAILABLE = False
from omegaconf import DictConfig, OmegaConf


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


def _normalize_training_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    data = dict(payload)
    training = data.get("training")
    if isinstance(training, Mapping):
        training_map = dict(training)
        lr_value = training_map.get("lr", training_map.get("learning_rate"))
        if lr_value is not None:
            training_map.setdefault("lr", lr_value)
            training_map.setdefault("learning_rate", lr_value)
        epochs_value = training_map.get("epochs", training_map.get("max_epochs"))
        if epochs_value is not None:
            training_map.setdefault("epochs", epochs_value)
            training_map.setdefault("max_epochs", epochs_value)
        data["training"] = training_map

        alias_map = {
            "seed": "seed",
            "lr": "lr",
            "batch_size": "batch_size",
            "epochs": "epochs",
            "max_epochs": "epochs",
            "gradient_accumulation": "grad_accum",
            "grad_accum": "grad_accum",
            "device": "device",
            "dtype": "dtype",
            "model": "model",
            "model_name": "model_name",
        }
        for source_key, target_key in alias_map.items():
            if target_key in data and data[target_key] is not None:
                continue
            if source_key in training_map and training_map[source_key] is not None:
                data[target_key] = training_map[source_key]

        if "logging" not in data and "logging" in training_map:
            data["logging"] = training_map["logging"]
    return data


try:  # pragma: no cover - runtime capability detection
    _TEST_CFG = OmegaConf.create({"training": {}})
    _ = _TEST_CFG.training  # type: ignore[attr-defined]
except Exception:  # AttributeError when attribute access unsupported
    _DICTCONFIG_SUPPORTS_ATTR = False
else:
    _DICTCONFIG_SUPPORTS_ATTR = True
finally:  # pragma: no cover - cleanup guard
    try:
        del _TEST_CFG
    except Exception:
        pass


class _AttrDictConfig(DictConfig):  # type: ignore[misc]
    """DictConfig compatible object offering attribute access for mappings."""

    def __init__(self, initial: Mapping[str, Any] | None = None) -> None:
        super().__init__()
        if initial:
            for key, value in initial.items():
                dict.__setitem__(self, key, self._wrap(value))

    @staticmethod
    def _wrap(value: Any) -> Any:
        if isinstance(value, Mapping) and not isinstance(value, DictConfig):
            return _AttrDictConfig(value)
        if isinstance(value, list):
            return [_AttrDictConfig._wrap(item) for item in value]
        if isinstance(value, tuple):
            return tuple(_AttrDictConfig._wrap(item) for item in value)
        return value

    def __getattr__(self, name: str) -> Any:
        if name in self:
            value = dict.__getitem__(self, name)
            wrapped = self._wrap(value)
            dict.__setitem__(self, name, wrapped)
            return wrapped
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            dict.__setitem__(self, name, self._wrap(value))

    def __setitem__(self, key: Any, value: Any) -> None:  # type: ignore[override]
        dict.__setitem__(self, key, self._wrap(value))


def _to_config_object(mapping: Mapping[str, Any]) -> DictConfig:
    normalized = _normalize_training_payload(mapping)
    if _DICTCONFIG_SUPPORTS_ATTR:
        return OmegaConf.create(normalized)
    return _AttrDictConfig(normalized)


def _read_yaml_mapping(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        try:
            data = safe_load(fh) or {}
        except MissingPyYAMLError as exc:
            raise RuntimeError(
                'PyYAML is required to parse configuration files. Install it via ``pip install "PyYAML>=6.0"`` '
                f"before loading {path}."
            ) from exc
    if not isinstance(data, Mapping):
        raise TypeError(f"Expected mapping at {path}, found {type(data).__name__}")
    return dict(data)


def _apply_overrides_to_mapping(
    mapping: Dict[str, Any], overrides: Sequence[str]
) -> Dict[str, Any]:
    for item in overrides:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        try:
            parsed = safe_load(value)
        except MissingPyYAMLError as exc:
            raise RuntimeError(
                'YAML overrides require PyYAML. Install it via ``pip install "PyYAML>=6.0"`` '
                "before specifying overrides."
            ) from exc
        target: Dict[str, Any] = mapping
        parts = [part for part in key.split(".") if part]
        if not parts:
            continue
        for part in parts[:-1]:
            next_val = target.get(part)
            if not isinstance(next_val, dict):
                if isinstance(next_val, Mapping):
                    next_val = dict(next_val)
                else:
                    next_val = {}
            target[part] = next_val
            target = target[part]
        target[parts[-1]] = parsed
    return mapping


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
    config_file = cfg_dir / f"{_PRIMARY}.yaml"
    hydra_ready = bool(_HYDRA_AVAILABLE and compose and initialize_config_dir)
    if hydra_ready and cfg_dir.is_dir() and config_file.is_file():
        # Hydra Compose API: https://hydra.cc/docs/advanced/compose_api/
        with initialize_config_dir(version_base=None, config_dir=str(cfg_dir)):
            hydra_cfg = compose(config_name=_PRIMARY, overrides=overrides)
        container = OmegaConf.to_container(hydra_cfg, resolve=True)  # type: ignore[arg-type]
        if not isinstance(container, Mapping):
            raise TypeError("Hydra compose did not return a mapping configuration")
        return _to_config_object(container)

    if config_file.is_file():
        mapping = _read_yaml_mapping(config_file)
        if overrides:
            mapping = _apply_overrides_to_mapping(mapping, overrides)
        return _to_config_object(mapping)

    if not allow_fallback:
        raise MissingConfigException(
            missing_cfg_file=f"{_CFG_DIR}/{_PRIMARY}.yaml",
            message="Config file missing",
        )

    base = TrainingDefaults().to_dict()
    if overrides:
        base = _apply_overrides_to_mapping(base, overrides)
    return _to_config_object(base)


def load_config(*, config_path: str) -> DictConfig:
    """Load a YAML config file into an OmegaConf DictConfig."""

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file {config_path} not found")
    mapping = _read_yaml_mapping(path)
    return _to_config_object(mapping)
