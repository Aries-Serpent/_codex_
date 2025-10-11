"""Configuration schemas and loaders for Codex ML commands."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

try:  # pragma: no cover - optional dependency
    from omegaconf import DictConfig, OmegaConf
except Exception:  # pragma: no cover - optional dependency
    DictConfig = Any  # type: ignore
    OmegaConf = None  # type: ignore

from .settings import AppSettings, EvalRow, eval_row_schema

__all__ = [
    "AppSettings",
    "ConfigError",
    "TokenizationConfig",
    "TrainingConfig",
    "OptimizerConfig",
    "SchedulerConfig",
    "EvaluationConfig",
    "ShardConfig",
    "DataConfig",
    "CodexConfig",
    "EvalRow",
    "load_app_config",
    "override_dict",
    "eval_row_schema",
    # Legacy exports
    "TrainingWeights",
    "PretrainingConfig",
    "SFTConfig",
    "RLHFConfig",
    "ValidationThresholds",
]


class ConfigError(ValueError):
    """Raised when a configuration file fails validation."""

    def __init__(self, path: str, message: str, value: Any | None = None) -> None:
        detail = f"{path}: {message}"
        if value is not None:
            detail = f"{detail} (got {value!r})"
        super().__init__(detail)
        self.path = path
        self.value = value


@dataclass
class TokenizationConfig:
    corpus_glob: str = "corpus.txt"
    model_type: str = "unigram"
    vocab_size: int = 32000
    character_coverage: float = 0.9995
    normalization_rule: Optional[str] = None
    seed: int = 42
    workers: int = 4
    out_dir: str = "artifacts/tokenizers"
    name: str = "default"
    padding: str = "max_length"
    truncation: bool = True
    max_length: Optional[int] = None
    dry_run: bool = False

    def validate(self, path: str = "tokenization") -> None:
        if not self.corpus_glob:
            raise ConfigError(f"{path}.corpus_glob", "cannot be empty")
        if not self.model_type:
            raise ConfigError(f"{path}.model_type", "cannot be empty")
        if self.vocab_size <= 0:
            raise ConfigError(f"{path}.vocab_size", "must be positive", self.vocab_size)
        if self.character_coverage <= 0 or self.character_coverage > 1:
            raise ConfigError(
                f"{path}.character_coverage",
                "must be between 0 and 1",
                self.character_coverage,
            )
        if self.workers <= 0:
            raise ConfigError(f"{path}.workers", "must be positive", self.workers)
        if not self.out_dir:
            raise ConfigError(f"{path}.out_dir", "cannot be empty")
        if not self.name:
            raise ConfigError(f"{path}.name", "cannot be empty")
        allowed_padding = {"max_length", "longest", "do_not_pad"}
        if self.padding not in allowed_padding:
            raise ConfigError(
                f"{path}.padding",
                f"must be one of {sorted(allowed_padding)}",
                self.padding,
            )
        if self.max_length is not None and self.max_length <= 0:
            raise ConfigError(f"{path}.max_length", "must be positive", self.max_length)


@dataclass
class OptimizerConfig:
    name: str = "adamw_torch"
    weight_decay: float = 0.01
    betas: Tuple[float, float] = (0.9, 0.999)
    eps: float = 1e-8

    def validate(self, path: str = "training.optimizer") -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ConfigError(path + ".name", "cannot be empty", self.name)
        if self.weight_decay < 0:
            raise ConfigError(path + ".weight_decay", "must be non-negative", self.weight_decay)
        try:
            beta1, beta2 = (float(self.betas[0]), float(self.betas[1]))
        except Exception as exc:  # pragma: no cover - defensive
            raise ConfigError(path + ".betas", "must be a pair of floats", self.betas) from exc
        if not (0.0 <= beta1 < 1 and 0.0 <= beta2 < 1):
            raise ConfigError(path + ".betas", "beta values must be in [0, 1)", self.betas)
        if self.eps <= 0:
            raise ConfigError(path + ".eps", "must be positive", self.eps)
        self.betas = (beta1, beta2)


@dataclass
class SchedulerConfig:
    name: str = "linear"
    warmup_steps: int = 0
    num_cycles: float = 1.0

    def validate(self, path: str = "training.scheduler") -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ConfigError(path + ".name", "cannot be empty")
        if self.warmup_steps < 0:
            raise ConfigError(path + ".warmup_steps", "must be non-negative", self.warmup_steps)
        if self.num_cycles <= 0:
            raise ConfigError(path + ".num_cycles", "must be positive", self.num_cycles)


@dataclass
class TrainingConfig:
    seed: int = 42
    deterministic: bool = True
    learning_rate: float = 0.0003
    batch_size: int = 32
    max_epochs: int = 5
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    warmup_steps: int = 0
    gradient_accumulation: int = 1
    tensorboard: bool = True
    mlflow_enable: bool = False
    model: str = "minilm"
    output_dir: str = "runs/default"
    checkpoint_dir: Optional[str] = None
    checkpoint_every_n_steps: int = 100
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    dataset: Dict[str, Any] = field(
        default_factory=lambda: {
            "train_path": "data/train_samples.jsonl",
            "eval_path": None,
            "format": "jsonl",
            "train_texts": [],
            "eval_texts": [],
        }
    )
    logging: Dict[str, Any] = field(
        default_factory=lambda: {
            "enable_tensorboard": True,
            "mlflow_enable": False,
        }
    )
    log_dir: str = "logs"
    log_formats: Tuple[str, ...] = ("ndjson",)

    def __post_init__(self) -> None:
        errs: List[str] = []
        if self.max_epochs < 0:
            errs.append("max_epochs must be >= 0")
        if self.batch_size < 1:
            errs.append("batch_size must be >= 1")
        if self.gradient_accumulation < 1:
            errs.append("gradient_accumulation must be >= 1")
        if not (0 <= self.seed < 2**32):
            errs.append("seed out of range")
        if errs:
            raise ValueError("; ".join(errs))

    def validate(self, path: str = "training") -> None:
        if self.learning_rate <= 0:
            raise ConfigError(f"{path}.learning_rate", "must be positive", self.learning_rate)
        if self.batch_size <= 0:
            raise ConfigError(f"{path}.batch_size", "must be positive", self.batch_size)
        if self.max_epochs <= 0:
            raise ConfigError(f"{path}.max_epochs", "must be positive", self.max_epochs)
        if self.gradient_accumulation <= 0:
            raise ConfigError(
                f"{path}.gradient_accumulation",
                "must be positive",
                self.gradient_accumulation,
            )
        if self.warmup_steps < 0:
            raise ConfigError(f"{path}.warmup_steps", "cannot be negative", self.warmup_steps)
        if self.checkpoint_every_n_steps <= 0:
            raise ConfigError(
                f"{path}.checkpoint_every_n_steps",
                "must be positive",
                self.checkpoint_every_n_steps,
            )
        if not self.output_dir:
            raise ConfigError(f"{path}.output_dir", "cannot be empty")
        self.optimizer.validate(f"{path}.optimizer")
        self.scheduler.validate(f"{path}.scheduler")
        sched_warmup = self.scheduler.warmup_steps
        warmup = self.warmup_steps
        if warmup != 0 and sched_warmup != 0 and warmup != sched_warmup:
            raise ConfigError(
                f"{path}.warmup_steps",
                "must match scheduler.warmup_steps when both are provided",
                {"warmup_steps": warmup, "scheduler.warmup_steps": sched_warmup},
            )
        if sched_warmup == 0:
            self.scheduler.warmup_steps = warmup
        else:
            self.warmup_steps = sched_warmup
        if not isinstance(self.dataset, Mapping):
            raise ConfigError(f"{path}.dataset", "must be a mapping", self.dataset)
        if "format" in self.dataset and not isinstance(self.dataset["format"], str):
            raise ConfigError(
                f"{path}.dataset.format",
                "must be a string",
                self.dataset.get("format"),
            )
        if "train_texts" in self.dataset and not isinstance(
            self.dataset.get("train_texts"), Iterable
        ):
            raise ConfigError(
                f"{path}.dataset.train_texts",
                "must be iterable",
                self.dataset.get("train_texts"),
            )


@dataclass
class EvaluationConfig:
    dataset_path: str = "data/eval_samples.jsonl"
    dataset_format: str = "jsonl"
    prediction_field: str = "prediction"
    target_field: str = "target"
    text_field: str = "text"
    metrics: List[str] = field(default_factory=lambda: ["perplexity", "accuracy"])
    output_dir: str = "runs/eval"
    max_samples: Optional[int] = None
    batch_size: int = 8
    strict: bool = True
    report_filename: str = "summary.json"
    ndjson_filename: str = "records.ndjson"
    metrics_filename: str = "metrics.ndjson"
    model_name: Optional[str] = None
    seed: Optional[int] = None
    split: str = "eval"
    run_id: Optional[str] = None

    def validate(self, path: str = "evaluation") -> None:
        if not self.dataset_path:
            raise ConfigError(f"{path}.dataset_path", "cannot be empty")
        if self.max_samples is not None and self.max_samples <= 0:
            raise ConfigError(f"{path}.max_samples", "must be positive", self.max_samples)
        if self.batch_size <= 0:
            raise ConfigError(f"{path}.batch_size", "must be positive", self.batch_size)
        if not self.metrics:
            raise ConfigError(f"{path}.metrics", "must contain at least one metric")
        if any(not isinstance(m, str) for m in self.metrics):
            raise ConfigError(f"{path}.metrics", "metric names must be strings", self.metrics)
        allowed_formats = {"jsonl", "ndjson", "text", "csv"}
        if self.dataset_format.lower() not in allowed_formats:
            raise ConfigError(
                f"{path}.dataset_format",
                f"must be one of {sorted(allowed_formats)}",
                self.dataset_format,
            )
        if not self.report_filename.endswith(".json"):
            raise ConfigError(
                f"{path}.report_filename",
                "must end with .json",
                self.report_filename,
            )
        if not self.ndjson_filename.endswith(".ndjson"):
            raise ConfigError(
                f"{path}.ndjson_filename",
                "must end with .ndjson",
                self.ndjson_filename,
            )
        if not self.metrics_filename.endswith(".ndjson"):
            raise ConfigError(
                f"{path}.metrics_filename",
                "must end with .ndjson",
                self.metrics_filename,
            )
        if not isinstance(self.split, str) or not self.split:
            raise ConfigError(f"{path}.split", "must be a non-empty string", self.split)


@dataclass
class ShardConfig:
    index: int = 0
    total: int = 1

    def validate(self, path: str = "data.shard") -> None:
        if self.total <= 0:
            raise ConfigError(f"{path}.total", "must be positive", self.total)
        if self.index < 0 or self.index >= self.total:
            raise ConfigError(
                f"{path}.index",
                "must be within [0, total)",
                {"index": self.index, "total": self.total},
            )


@dataclass
class DataConfig:
    source_path: str = "data/raw/sample.txt"
    cache_dir: str = "data/cache"
    manifest_path: Optional[str] = None
    encoding: str = "utf-8"
    fallback_encoding: Optional[str] = None
    newline_normalization: str = "unix"
    streaming: bool = True
    validate_utf8: bool = True
    shard: ShardConfig = field(default_factory=ShardConfig)
    shuffle_seed: Optional[int] = 0
    split_ratios: Dict[str, float] = field(
        default_factory=lambda: {"train": 0.9, "validation": 0.1}
    )
    max_items: Optional[int] = None
    skip_empty: bool = True
    safety_filter: bool = False
    cache_manifest_name: str = "manifest.json"

    def validate(self, path: str = "data") -> None:
        if not self.source_path:
            raise ConfigError(f"{path}.source_path", "cannot be empty")
        if self.max_items is not None and self.max_items <= 0:
            raise ConfigError(f"{path}.max_items", "must be positive", self.max_items)
        if self.shuffle_seed is not None and self.shuffle_seed < 0:
            raise ConfigError(
                f"{path}.shuffle_seed",
                "must be non-negative when provided",
                self.shuffle_seed,
            )
        allowed = {"unix", "windows", "preserve"}
        if self.newline_normalization not in allowed:
            raise ConfigError(
                f"{path}.newline_normalization",
                f"must be one of {sorted(allowed)}",
                self.newline_normalization,
            )
        if not isinstance(self.split_ratios, Mapping) or not self.split_ratios:
            raise ConfigError(f"{path}.split_ratios", "must be a non-empty mapping")
        total = float(sum(float(v) for v in self.split_ratios.values()))
        if not 0.999 <= total <= 1.001:
            raise ConfigError(
                f"{path}.split_ratios",
                "values must sum to 1.0",
                {"sum": total, "ratios": dict(self.split_ratios)},
            )
        self.shard.validate(f"{path}.shard")
        if self.cache_manifest_name and not self.cache_manifest_name.endswith(".json"):
            raise ConfigError(
                f"{path}.cache_manifest_name",
                "must end with .json",
                self.cache_manifest_name,
            )


@dataclass
class CodexConfig:
    tokenization: TokenizationConfig = field(default_factory=TokenizationConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    data: DataConfig = field(default_factory=DataConfig)

    def validate(self) -> None:
        self.tokenization.validate("tokenization")
        self.training.validate("training")
        self.evaluation.validate("evaluation")
        self.data.validate("data")


def override_dict(overrides: Sequence[str] | None) -> DictConfig:
    """Create a DictConfig representing dotlist overrides."""

    if not overrides:
        return OmegaConf.create()
    try:
        return OmegaConf.from_dotlist(list(overrides))
    except Exception as exc:  # pragma: no cover - OmegaConf raises specific errors
        raise ConfigError("overrides", f"failed to parse overrides: {exc}") from exc


def load_app_config(
    config_path: str | Path,
    overrides: Sequence[str] | None = None,
) -> tuple[CodexConfig, DictConfig]:
    """Load a configuration file and apply overrides.

    Parameters
    ----------
    config_path:
        Path to a YAML configuration file.
    overrides:
        Optional Hydra-style key=value overrides.

    Returns
    -------
    (CodexConfig, DictConfig)
        Materialised dataclass instance and the resolved DictConfig used to
        construct it. Both share the applied overrides.
    """

    schema = OmegaConf.structured(CodexConfig)
    OmegaConf.set_struct(schema, False)
    try:
        file_cfg = OmegaConf.load(str(config_path))
    except FileNotFoundError as exc:
        raise ConfigError("config", f"configuration file not found: {config_path}") from exc
    except Exception as exc:
        raise ConfigError("config", f"failed to load configuration: {exc}") from exc

    def _to_plain(mapping: Mapping[str, Any]) -> Dict[str, Any]:
        if hasattr(OmegaConf, "to_container"):
            return dict(OmegaConf.to_container(mapping, resolve=True))  # type: ignore[arg-type]
        return dict(mapping)

    if isinstance(schema, Mapping):
        cfg = OmegaConf.merge(schema, file_cfg, override_dict(overrides))
        try:
            obj = OmegaConf.to_object(cfg)
        except Exception as exc:  # pragma: no cover - defensive against OmegaConf issues
            raise ConfigError("config", f"failed to materialise dataclass: {exc}") from exc
        if not isinstance(obj, CodexConfig):  # pragma: no cover - structured config guarantees type
            raise ConfigError("config", "unexpected configuration object", type(obj).__name__)
        obj.validate()
        return obj, cfg

    # Fallback path when OmegaConf stub is active and ``structured`` returns the class.
    base: Dict[str, Any] = asdict(CodexConfig())

    def _deep_update(target: Dict[str, Any], updates: Mapping[str, Any]) -> Dict[str, Any]:
        for key, value in updates.items():
            if isinstance(key, str) and "." in key:
                head, tail = key.split(".", 1)
                child = target.get(head)
                if not isinstance(child, dict):
                    child = {}
                    target[head] = child
                if tail:
                    _deep_update(child, {tail: value})
                else:
                    if isinstance(value, Mapping):
                        child.update(value)
                    else:
                        child["value"] = value
                continue
            if isinstance(value, Mapping) and isinstance(target.get(key), dict):
                target[key] = _deep_update(target[key], value)  # type: ignore[index]
            elif isinstance(value, Mapping):
                target[key] = _deep_update({}, value)
            else:
                target[key] = value
        return target

    combined = _deep_update(base, _to_plain(file_cfg))
    overrides_cfg = override_dict(overrides)
    combined = _deep_update(combined, _to_plain(overrides_cfg))

    def _build_section(section: str, cls: type, payload: Mapping[str, Any]):
        try:
            instance = cls()
            for key, value in payload.items():
                if not hasattr(instance, key):
                    setattr(instance, key, value)
                    continue

                current_value = getattr(instance, key)

                def _coerce(current: Any, new_value: Any) -> Any:
                    if is_dataclass(current) and isinstance(new_value, Mapping):
                        for sub_key, sub_val in new_value.items():
                            setattr(
                                current,
                                sub_key,
                                _coerce(getattr(current, sub_key, None), sub_val),
                            )
                        return current
                    if isinstance(new_value, str):
                        text = new_value.strip()
                        if isinstance(current, bool):
                            lowered = text.lower()
                            if lowered in {"1", "true", "yes", "on"}:
                                return True
                            if lowered in {"0", "false", "no", "off"}:
                                return False
                        try:
                            if isinstance(current, int) and not isinstance(current, bool):
                                return int(text)
                            if isinstance(current, float):
                                return float(text)
                        except Exception:
                            pass
                    return new_value

                coerced = _coerce(current_value, value)
                setattr(instance, key, coerced)
            return instance
        except ConfigError:
            raise
        except ValueError as exc:
            parts: list[str] = []
            for chunk in str(exc).split(";"):
                chunk = chunk.strip()
                if not chunk:
                    continue
                if " " in chunk:
                    field, rest = chunk.split(" ", 1)
                    parts.append(f"{section}.{field} {rest}")
                else:
                    parts.append(f"{section}.{chunk}")
            message = "; ".join(parts) if parts else str(exc)
            raise ConfigError(section, message) from exc
        except Exception as exc:  # pragma: no cover - defensive guard
            raise ConfigError(section, f"failed to construct config: {exc}") from exc

    obj = CodexConfig(
        tokenization=_build_section(
            "tokenization", TokenizationConfig, combined.get("tokenization", {})
        ),
        training=_build_section("training", TrainingConfig, combined.get("training", {})),
        evaluation=_build_section("evaluation", EvaluationConfig, combined.get("evaluation", {})),
        data=_build_section("data", DataConfig, combined.get("data", {})),
    )
    obj.validate()
    return obj, DictConfig(combined)


# ---------------------------------------------------------------------------
# Legacy dataclasses retained for backward compatibility with existing APIs.
# ---------------------------------------------------------------------------


@dataclass
class TrainingWeights:
    """Weights controlling relative importance of training stages."""

    alpha: float
    beta: float
    gamma: float


@dataclass
class PretrainingConfig:
    """Settings for the pretraining stage."""

    model_size: str
    context_length: int


@dataclass
class SFTConfig:
    """Settings for supervised fine-tuning."""

    batch_size: int
    learning_rate: float
    epochs: int


@dataclass
class RLHFConfig:
    """Settings for the RLHF stage."""

    algorithm: str
    kl_penalty: float
    ppo_epochs: int


@dataclass
class ValidationThresholds:
    """Metrics expected from the validation step."""

    syntax_ok: float
    logic_ok: float
    security_ok: float
    perf_ok: float


from .settings import AppSettings, EvalRow, eval_row_schema, get_settings

__all__ = sorted(
    set(
        __all__
        + [
            "AppSettings",
            "EvalRow",
            "eval_row_schema",
            "get_settings",
        ]
    )
)
