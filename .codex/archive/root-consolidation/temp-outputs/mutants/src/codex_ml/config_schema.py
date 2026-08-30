"""
Minimal Pydantic-based config schema and validation helpers.
Extend/replace with rich Hydra Structured Configs as needed.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Mapping, Sequence  # noqa: E402
from dataclasses import asdict, dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

from pydantic import (  # noqa: E402
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    ValidationError,
    field_validator,
)

from codex_ml.utils.yaml_support import MissingPyYAMLError, safe_load  # noqa: E402


class LoraConfig(BaseModel):
    """Subset of LoRA hyper-parameters accepted by the training stack."""

    model_config = ConfigDict(extra="forbid")

    enable: bool = False
    r: PositiveInt = Field(default=8, description="LoRA rank")
    lora_alpha: PositiveInt = Field(default=16, description="LoRA alpha scaling")
    lora_dropout: float = Field(default=0.05, ge=0.0, le=1.0)
    task_type: str = Field(default="CAUSAL_LM")
    target_modules: Optional[list[str]] = Field(
        default=None,
        description="Optional list of module names to which the adapter should apply.",
    )


class TrainConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    config_version: int = Field(default=1, ge=1)
    model_name: str = Field(default="tiny", description="Model identifier or profile name.")
    learning_rate: float = Field(default=1e-3, gt=0.0)
    batch_size: PositiveInt = Field(default=8, description="Training batch size")
    epochs: PositiveInt = Field(default=1)
    max_samples: PositiveInt = Field(default=32)
    data_path: Optional[str] = Field(
        default=None, description="Optional local dataset path (offline safe)."
    )
    seed: int = Field(default=42, description="Random seed for reproducible runs")
    device: str = Field(default="cpu", description="Preferred training device")
    dtype: str = Field(default="float32", description="Torch dtype for model weights")
    grad_accum: PositiveInt = Field(default=1, description="Gradient accumulation steps")
    lora: Optional[LoraConfig] = Field(default=None, description="Optional LoRA overrides")
    eval_split: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fraction of data reserved for evaluation",
    )
    checkpoint_keep: PositiveInt = Field(default=1, description="Number of checkpoints to keep")
    bf16_require_capability: bool = Field(
        default=False,
        description="When true and dtype requests bf16, assert bf16 capability and fail fast.",
    )
    dataset_cast_policy: Optional[str] = Field(
        default=None,
        description="Optional dataset casting policy: 'to_model_dtype', 'to_fp32', or None",
    )

    @field_validator("data_path")
    @classmethod
    def _path_exists_if_provided(cls, v) -> None:
        if v:
            p = Path(v)
            if not p.exists():
                raise ValueError(f"data_path does not exist: {p}")
        return v


def load_yaml(path: str | Path) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as f:
            return safe_load(f) or {}
    except MissingPyYAMLError as exc:
        type(exc).__name__
        logger.debug("MissingPyYAMLError: <ERROR_TYPE>")
        raise RuntimeError(
            'PyYAML is required to validate configuration files. Install it via ``pip install "PyYAML>=6.0"`` '  # noqa: E501
            f"before loading {path}."
        ) from exc


def _as_train_config_payload(cfg: Mapping[str, Any]) -> dict[str, Any]:
    """Return a mapping compatible with :class:`TrainConfig`.

    Historical configs often nest training options under a top-level ``training``
    key.  This helper preserves backward compatibility by extracting that block
    when present while still permitting flattened dictionaries.
    """

    if "training" in cfg and isinstance(cfg["training"], Mapping):
        return dict(cfg["training"])
    return dict(cfg)


def validate_config_file(path: str | Path) -> TrainConfig:
    data = load_yaml(path)
    return TrainConfig.model_validate(_as_train_config_payload(data))


def validate_config_dict(cfg: Mapping[str, Any]) -> TrainConfig:
    """Validate a config provided as a dictionary-like object."""

    return TrainConfig.model_validate(_as_train_config_payload(cfg))


@dataclass(slots=True)
class TokenizerSettings:
    """Lightweight dataclass for tokenizer defaults used in quickstarts."""

    vocab_size: int
    model_type: str = "bpe"
    max_length: int = 1024


@dataclass(slots=True)
class LoraSettings:
    """Dataclass wrapper mirroring :class:`LoraConfig` for ergonomic consumption."""

    enabled: bool = False
    rank: int = 8
    alpha: int = 16
    dropout: float = 0.05
    task_type: str = "CAUSAL_LM"
    target_modules: Optional[Sequence[str]] = None

    def to_payload(self) -> dict[str, Any]:
        """Return a dictionary compatible with :class:`LoraConfig`."""

        if not self.enabled:
            return {"enable": False}
        payload: dict[str, Any] = {
            "enable": True,
            "r": int(self.rank),
            "lora_alpha": int(self.alpha),
            "lora_dropout": float(self.dropout),
            "task_type": self.task_type,
        }
        if self.target_modules is not None:
            payload["target_modules"] = [str(item) for item in self.target_modules]
        return payload

    @classmethod
    def from_model(cls, cfg: LoraConfig | None) -> LoraSettings:
        if cfg is None:
            return cls()
        return cls(
            enabled=bool(cfg.enable),
            rank=int(cfg.r),
            alpha=int(cfg.lora_alpha),
            dropout=float(cfg.lora_dropout),
            task_type=str(cfg.task_type),
            target_modules=list(cfg.target_modules) if cfg.target_modules is not None else None,
        )


@dataclass(slots=True)
class TrainingSettings:
    """Minimal training configuration for scripts/tests without Hydra."""

    model_name: str
    epochs: int = 1
    batch_size: int = 8
    learning_rate: float = 1e-3
    use_amp: bool = False
    seed: int = 42
    device: str = "cpu"
    dtype: str = "float32"
    grad_accum: int = 1
    lora: LoraSettings = field(default_factory=LoraSettings)

    def to_train_config(self) -> TrainConfig:
        """Convert the dataclass into a validated :class:`TrainConfig` instance."""

        lora_settings = self.lora
        payload = asdict(self)
        payload.pop("lora")
        payload.pop("use_amp", None)
        payload["grad_accum"] = int(payload.get("grad_accum", 1))
        payload["learning_rate"] = float(payload["learning_rate"])
        if lora_settings.enabled:
            payload["lora"] = lora_settings.to_payload()
        else:
            payload["lora"] = None
        payload.setdefault("max_samples", TrainConfig.model_fields["max_samples"].default)
        payload.setdefault("checkpoint_keep", TrainConfig.model_fields["checkpoint_keep"].default)
        payload.setdefault(
            "bf16_require_capability",
            TrainConfig.model_fields["bf16_require_capability"].default,
        )
        payload.setdefault(
            "dataset_cast_policy",
            TrainConfig.model_fields["dataset_cast_policy"].default,
        )
        return TrainConfig.model_validate(payload)

    @classmethod
    def from_train_config(cls, cfg: TrainConfig) -> TrainingSettings:
        data = cfg.model_dump()
        lora_settings = (
            LoraSettings.from_model(cfg.lora) if cfg.lora is not None else LoraSettings()
        )
        return cls(
            model_name=str(data["model_name"]),
            epochs=int(data["epochs"]),
            batch_size=int(data.get("batch_size", data.get("per_device_train_batch_size", 8))),
            learning_rate=float(data["learning_rate"]),
            use_amp=bool(data.get("use_amp", False)),
            seed=int(data.get("seed", 42)),
            device=str(data.get("device", "cpu")),
            dtype=str(data.get("dtype", "float32")),
            grad_accum=int(data.get("grad_accum", data.get("gradient_accumulation", 1))),
            lora=lora_settings,
        )


# --- Back-compat shim -------------------------------------------------------
# Existing callers import `validate_config` and may pass either a mapping or a path.


def validate_config(cfg: str | Path | Mapping[str, Any], *args: Any, **kwargs: Any) -> TrainConfig:
    """Backward-compatible wrapper around the new validators."""
    if isinstance(cfg, Mapping):
        return validate_config_dict(cfg)
    # treat as path-like
    return validate_config_file(Path(cfg))


__all__ = [
    "LoraConfig",
    "LoraSettings",
    "TokenizerSettings",
    "TrainConfig",
    "TrainingSettings",
    "ValidationError",
    "load_yaml",
    "validate_config",
    "validate_config_dict",
    "validate_config_file",
]
