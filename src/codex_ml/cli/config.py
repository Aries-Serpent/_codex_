"""Structured Hydra configuration and audit CLI for Codex training."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional, Tuple


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
    log_formats: Tuple[str, ...] = ("ndjson",)
    log_system_metrics: bool = False
    system_metrics_interval: float = 60.0
    system_metrics_path: Optional[str] = None
    keep_last_n: Optional[int] = 5


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


def register_configs() -> None:
    """Register structured configs with Hydra's ConfigStore."""

    try:
        from hydra.core.config_store import ConfigStore
    except Exception:  # pragma: no cover - hydra optional dependency
        return

    cs = ConfigStore.instance()

    if not cs.exists(name="app"):
        cs.store(name="app", node=AppConfig)
    if not cs.exists(group="experiment", name="debug"):
        cs.store(
            group="experiment",
            name="debug",
            node=AppConfig(training=TrainCfg(max_epochs=1, batch_size=2)),
        )
    if not cs.exists(group="experiment", name="fast"):
        cs.store(
            group="experiment",
            name="fast",
            node=AppConfig(training=TrainCfg(max_epochs=1, batch_size=8)),
        )


_DEFAULT_CONFIG_PATH = Path("conf/config.yaml")
_UNRESOLVED_PATTERN = re.compile(r"\$\{[^}]+\}")


def _normalize_defaults(defaults: Any) -> list[str]:
    normalized: list[str] = []
    if not isinstance(defaults, list):
        return normalized
    for entry in defaults:
        if isinstance(entry, str):
            normalized.append(entry)
        elif isinstance(entry, dict):
            normalized.extend(str(key) for key in entry.keys())
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


def _load_defaults_from_yaml(text: str) -> list[str] | None:
    try:
        import yaml  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        return None

    try:
        data = yaml.safe_load(text) or {}
    except Exception:
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
        print("[config] conf/config.yaml not found", file=sys.stderr)
        print(json.dumps({"_self_": False, "position": None, "ok": False, "unresolved_refs": True}))
        return 2

    text = cfg_path.read_text(encoding="utf-8")
    code, payload = _audit_defaults(text, args.audit)
    print(json.dumps(payload))
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex config", description="Hydra config helpers"
    )
    parser.add_argument("--path", default=str(_DEFAULT_CONFIG_PATH), help="Config file to audit")
    parser.add_argument(
        "--audit",
        choices=["present", "first", "last"],
        default="first",
        help="Check _self_ presence/position",
    )
    parser.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


__all__ = [
    "AppConfig",
    "DataCfg",
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
