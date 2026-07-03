"""Structured Hydra configuration and audit CLI for Codex training."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger


@dataclass
class ModelCfg:
    """Model-related hyperparameters."""

    name: str = "gpt2"
    dtype: str = "float32"
    lora_enable: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05


@dataclass
class OptimCfg:
    """Optimizer parameters."""

    learning_rate: float = 3e-4
    weight_decay: float = 0.0


@dataclass
class DataCfg:
    """Dataset configuration."""

    format: str = "jsonl"
    train_path: str = "data/train.jsonl"
    eval_path: Optional[str] = "data/eval.jsonl"
    val_fraction: float = 0.0
    pad_to_max: bool = False
    truncation: bool = True


@dataclass
class TrainCfg:
    """Training loop parameters."""

    seed: int = 42
    deterministic: bool = True
    batch_size: int = 8
    max_epochs: int = 1
    gradient_accumulation: int = 1
    amp_enable: bool = False
    amp_dtype: Optional[str] = None
    eval_every_epochs: int = 1
    metrics_out: str = ".codex/metrics.ndjson"
    log_dir: str = "logs"
    log_formats: tuple[str, ...] = ("ndjson",)
    log_system_metrics: bool = False
    system_metrics_interval: float = 60.0
    system_metrics_path: Optional[str] = None
    keep_last_n: Optional[int] = 5


@dataclass
class ExperimentConfig:
    """Configuration for experiment settings.

    This class defines experimental configurations for training runs,
    testing scenarios, and deployment environments. It controls resource
    allocation, logging behavior, and checkpoint management.

    Attributes:
        name: Experiment identifier (e.g., "debug", "production", "benchmark")
        type: Experiment category (e.g., "unit_test", "integration", "performance")
        description: Human-readable explanation of experiment purpose
        seed: Random seed for reproducibility (default: 42)
        deterministic: Enable deterministic mode for reproducible results
        max_iterations: Maximum training/evaluation iterations allowed
        batch_size: Number of samples per batch (1-512 typical range)
        num_workers: Number of parallel data loading workers (0 disables parallelism)
        enable_logging: Enable logging to files and tracking systems
        save_checkpoints: Enable checkpoint saving during training
        eval_frequency: Evaluation frequency in iterations (0 disables)
    """

    name: str = "default"
    type: str = "default"
    description: str = ""
    seed: int = 42
    deterministic: bool = True
    max_iterations: int = 1000
    batch_size: int = 32
    num_workers: int = 4
    enable_logging: bool = True
    save_checkpoints: bool = True
    eval_frequency: int = 100


@dataclass
class LogCfg:
    """Logging integrations."""

    tensorboard: bool = False
    tensorboard_dir: str = ".codex/tb"
    wandb_enable: bool = False
    mlflow_enable: bool = False
    mlflow_tracking_uri: Optional[str] = None


@dataclass
class AppConfig:
    """Root structured config for Codex training."""

    model: ModelCfg = field(default_factory=ModelCfg)
    optim: OptimCfg = field(default_factory=OptimCfg)
    data: DataCfg = field(default_factory=DataCfg)
    training: TrainCfg = field(default_factory=TrainCfg)
    logging: LogCfg = field(default_factory=LogCfg)
    experiment: Optional[ExperimentConfig] = None


def register_configs() -> None:
    """Register structured configs with Hydra's ConfigStore."""

    try:
        try:
            from hydra.core.config_store import ConfigStore
        except ImportError as e:
            type(e).__name__
            logger.debug("hydra not available: <ERROR_TYPE>")
            from config_legacy.core.config_store import ConfigStore  # type: ignore[no-redef]

        from codex_ml.utils.hydra_cs import safe_exists
    except (ImportError, AttributeError):  # pragma: no cover - hydra optional dependency
        return

    cs = ConfigStore.instance()

    if not safe_exists(cs, name="app"):
        cs.store(name="app", node=AppConfig)
    if not safe_exists(cs, group="experiment", name="debug"):
        cs.store(
            group="experiment",
            name="debug",
            node=AppConfig(training=TrainCfg(max_epochs=1, batch_size=2)),
        )
    if not safe_exists(cs, group="experiment", name="fast"):
        cs.store(
            group="experiment",
            name="fast",
            node=AppConfig(training=TrainCfg(max_epochs=1, batch_size=8)),
        )


_DEFAULT_CONFIG_PATH = Path("configs/base/hydra.yaml")
_UNRESOLVED_PATTERN = re.compile(r"\$\{[^}]+\}")


def _normalize_defaults(defaults: Any) -> list[str]:
    normalized: list[str] = []
    if not isinstance(defaults, list):
        return normalized
    for entry in defaults:
        if isinstance(entry, str):
            normalized.append(entry)
        elif isinstance(entry, dict):
            normalized.extend(str(key) for key in entry)
    return normalized


def _extract_defaults_from_text(text: str) -> list[str]:
    entries: list[str] = []
    in_defaults = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("defaults:"):
            in_defaults = True
            continue
        if not in_defaults:
            continue
        if stripped.startswith("-"):
            entry = stripped.lstrip("- ")
            key = entry.split(":", 1)[0].strip()
            if key:
                entries.append(key)
        elif raw_line and not raw_line[0].isspace():
            break
    return entries


def _load_defaults_from_yaml(text: str) -> Optional[list[str]]:
    try:
        import yaml
    except (ImportError, AttributeError):  # pragma: no cover - optional dependency
        return None

    try:
        data = yaml.safe_load(text) or {}
    except (ValueError, TypeError, RuntimeError):
        logger.debug("yaml.safe_load failed; skipping defaults", exc_info=True)
        return None

    if not isinstance(data, dict):
        return []
    defaults = data.get("defaults")
    return _normalize_defaults(defaults)


def _audit_defaults(text: str, mode: str) -> tuple[int, dict[str, Any]]:
    defaults = _load_defaults_from_yaml(text)
    unresolved = bool(_UNRESOLVED_PATTERN.search(text))

    if defaults is None:
        entries = _extract_defaults_from_text(text)
        has_self = "_self_" in entries or "_self_" in text
        position = entries.index("_self_") if "_self_" in entries else None
        order_ok = True
        if position is not None:
            if mode == "first":
                order_ok = position == 0
            elif mode == "last" and entries:
                order_ok = position == len(entries) - 1
        payload = {
            "_self_": has_self,
            "position": position,
            "ok": bool(has_self and order_ok and not unresolved),
            "unresolved_refs": unresolved,
        }
        if payload["ok"]:
            return 0, payload
        return (3 if not has_self else 4), payload

    if "_self_" not in defaults:
        payload = {
            "_self_": False,
            "position": None,
            "ok": False,
            "unresolved_refs": unresolved,
        }
        return 3, payload

    index = defaults.index("_self_")
    order_ok = True
    if mode == "first":
        order_ok = index == 0
    elif mode == "last":
        order_ok = index == len(defaults) - 1

    ok = bool(order_ok and not unresolved)
    payload = {
        "_self_": True,
        "position": index,
        "ok": ok,
        "unresolved_refs": unresolved,
    }
    return (0 if ok else 4), payload


def cmd_audit(args: argparse.Namespace) -> int:
    cfg_path = Path(args.path or _DEFAULT_CONFIG_PATH).expanduser().resolve()
    if not cfg_path.exists():
        logger.error("[config] configs/base/hydra.yaml not found")
        print(
            json.dumps(
                {
                    "_self_": False,
                    "position": None,
                    "ok": False,
                    "unresolved_refs": True,
                }
            )
        )
        return 2

    text = cfg_path.read_text(encoding="utf-8")
    code, payload = _audit_defaults(text, args.audit)
    logger.info(json.dumps(payload))
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex config", description="Hydra config helpers")
    parser.add_argument("--path", default=str(_DEFAULT_CONFIG_PATH), help="Config file to audit")
    parser.add_argument(
        "--audit",
        choices=["present", "first", "last"],
        default="first",
        help="Check _self_ presence/position",
    )
    parser.set_defaults(func=cmd_audit)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


__all__ = [
    "AppConfig",
    "DataCfg",
    "ExperimentConfig",
    "LogCfg",
    "ModelCfg",
    "OptimCfg",
    "TrainCfg",
    "cmd_audit",
    "main",
    "register_configs",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
