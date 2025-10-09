"""Model registry built on :mod:`codex_ml.registry` primitives."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, cast

import torch
from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.registry.base import Registry
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.optional import optional_import

if TYPE_CHECKING:  # pragma: no cover - typing only
    from transformers import PreTrainedModel as HF_PreTrainedModel  # type: ignore
else:  # pragma: no cover - runtime fallback when transformers missing
    HF_PreTrainedModel = Any  # type: ignore


transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if _HAS_TRANSFORMERS and transformers is not None:
    AutoModelForCausalLM = cast(
        "type[HF_PreTrainedModel]", getattr(transformers, "AutoModelForCausalLM", None)
    )
    AutoModelForMaskedLM = cast(
        "type[HF_PreTrainedModel]", getattr(transformers, "AutoModelForMaskedLM", None)
    )
    _HAS_TRANSFORMERS = bool(AutoModelForCausalLM) and bool(AutoModelForMaskedLM)
else:  # pragma: no cover - optional dependency unavailable
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoModelForMaskedLM = None  # type: ignore[assignment]
    _HAS_TRANSFORMERS = False

TRANSFORMERS_AVAILABLE = _HAS_TRANSFORMERS

model_registry = Registry("model", entry_point_group="codex_ml.models")


@model_registry.register("MiniLM")
def _build_minilm(cfg: Dict[str, Any]) -> Any:
    from codex_ml.models.minilm import MiniLM, MiniLMConfig

    return MiniLM(MiniLMConfig(vocab_size=int(cfg.get("vocab_size", 128))))


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return parent

    fallback_index = min(3, len(current.parents) - 1)
    return current.parents[fallback_index]


def _resolve_pretrained_identifier(cfg: Dict[str, Any], default: str) -> str:
    for key in (
        "local_path",
        "path",
        "model_path",
        "pretrained_model_name_or_path",
        "model_id",
    ):
        value = cfg.get(key)
        if value:
            return str(value)
    return default


def _resolve_offline_checkpoint(
    alias: str,
    cfg: Dict[str, Any],
    *,
    default_remote: str,
    default_subdir: str,
    specific_env: str | None = None,
) -> str:
    """Resolve a checkpoint path respecting offline-first semantics."""

    local_only = bool(cfg.get("local_files_only", True))
    explicit_value = None
    for key in (
        "local_path",
        "path",
        "model_path",
        "pretrained_model_name_or_path",
        "model_id",
    ):
        value = cfg.get(key)
        if value:
            explicit_value = str(value)
            candidate = Path(explicit_value).expanduser()
            if candidate.exists():
                return str(candidate)
            if not local_only:
                return explicit_value
            raise FileNotFoundError(
                f"Checkpoint for '{alias}' expected at {candidate}. Provide a valid path or set "
                "`local_files_only=false` to allow fetching '{default_remote}'."
            )

    hints: list[str] = []

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            hints.append(f"${specific_env} -> {env_path}")
            if env_path.exists():
                return str(env_path)
            if not local_only:
                return str(env_path)
            raise FileNotFoundError(
                f"Environment variable {specific_env} points to {env_path}, but no checkpoint was found."
            )

    offline_root = os.environ.get("CODEX_ML_OFFLINE_MODELS_DIR")
    candidates: list[Path] = []
    if offline_root:
        candidates.append(Path(offline_root).expanduser() / default_subdir)
    candidates.append(_repo_root() / "artifacts" / "models" / default_subdir)

    checked = []
    for candidate in candidates:
        checked.append(str(candidate))
        if candidate.exists():
            return str(candidate)

    if local_only:
        details = ", ".join(hints + checked) if (hints or checked) else "<no candidates>"
        raise FileNotFoundError(
            f"Local checkpoint for '{alias}' not found. Checked: {details}. Provide `local_path` "
            f"or place weights under CODEX_ML_OFFLINE_MODELS_DIR/{default_subdir}, or disable offline "
            f"mode with `local_files_only=false` to fallback to '{default_remote}'."
        )

    return default_remote


def _load_hf_model(task: str, cfg: Dict[str, Any], default: str) -> HF_PreTrainedModel:
    """Load a transformers model with offline-first semantics."""

    model_id = _resolve_pretrained_identifier(cfg, default)
    local_only = bool(cfg.get("local_files_only", True))
    trust_remote_code = cfg.get("trust_remote_code")

    if task == "causal":
        loader = AutoModelForCausalLM
    elif task == "mlm":
        loader = AutoModelForMaskedLM
    else:
        raise ValueError(f"Unsupported task for registry entry: {task}")

    if not TRANSFORMERS_AVAILABLE or loader is None:
        raise ImportError("transformers is required to load registry models")

    kwargs: Dict[str, Any] = {"local_files_only": local_only}
    if trust_remote_code is not None:
        kwargs["trust_remote_code"] = bool(trust_remote_code)

    try:
        return load_from_pretrained(loader, model_id, **kwargs)
    except OSError as exc:  # pragma: no cover - network/IO errors
        raise RuntimeError(
            f"Unable to load weights for {model_id!r} from local cache. "
            "Provide a `local_path` or set `local_files_only=False` if remote downloads are permitted."
        ) from exc


@model_registry.register("bert-base-uncased")
def _build_default_bert(cfg: Dict[str, Any]) -> HF_PreTrainedModel:
    return _load_hf_model("mlm", cfg, "bert-base-uncased")


@model_registry.register("gpt2-offline")
def _build_offline_gpt2(cfg: Dict[str, Any]) -> HF_PreTrainedModel:
    resolved = _resolve_offline_checkpoint(
        "gpt2-offline",
        cfg,
        default_remote="gpt2",
        default_subdir="gpt2",
        specific_env="CODEX_ML_GPT2_PATH",
    )
    cfg = dict(cfg)
    cfg.setdefault("local_files_only", True)
    cfg["pretrained_model_name_or_path"] = resolved
    return _load_hf_model("causal", cfg, "gpt2")


@model_registry.register("tinyllama-offline")
def _build_offline_tinyllama(cfg: Dict[str, Any]) -> HF_PreTrainedModel:
    resolved = _resolve_offline_checkpoint(
        "tinyllama-offline",
        cfg,
        default_remote="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        default_subdir="tinyllama",
        specific_env="CODEX_ML_TINYLLAMA_PATH",
    )
    cfg = dict(cfg)
    cfg.setdefault("local_files_only", True)
    cfg["pretrained_model_name_or_path"] = resolved
    return _load_hf_model("causal", cfg, "TinyLlama/TinyLlama-1.1B-Chat-v1.0")


def register_model(name: str, obj: Any | None = None, *, override: bool = False) -> Any:
    """Register a model constructor under ``name``."""

    return model_registry.register(name, obj, override=override)


def _normalise_device(device: Any | None) -> Any | None:
    if device in {None, "cpu", "cuda"}:
        if device is None:
            return "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda" and not torch.cuda.is_available():
            return "cpu"
        return device
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


_DTYPE_ALIASES = {
    "fp32": "float32",
    "float": "float32",
    "float32": "float32",
    "torch.float32": "float32",
    "fp16": "float16",
    "float16": "float16",
    "half": "float16",
    "torch.float16": "float16",
    "bf16": "bfloat16",
    "bfloat16": "bfloat16",
    "torch.bfloat16": "bfloat16",
}


def _resolve_torch_dtype(value: Any | None) -> torch.dtype | None:
    """Best-effort conversion of ``value`` to a ``torch.dtype``."""

    if value is None:
        return None
    if isinstance(value, torch.dtype):
        return value
    text = str(value).strip().lower()
    if not text:
        return None
    alias = _DTYPE_ALIASES.get(text, text)
    attr = alias.split(".")[-1]
    torch_value = getattr(torch, attr, None)
    if isinstance(torch_value, torch.dtype):
        return torch_value
    return None


def get_model(
    name: str,
    cfg: Dict[str, Any] | None = None,
    *,
    device: Any | None = None,
    dtype: Any | None = None,
    adapter_loader: Any | None = None,
) -> Any:
    """Instantiate a model by name with optional device/dtype overrides."""

    config = dict(cfg or {})
    if device is not None:
        config.setdefault("device", device)
    if dtype is not None:
        config.setdefault("dtype", dtype)
    builder = model_registry.get(name)
    model = builder(config) if callable(builder) else builder
    lora_cfg = config.get("lora", {})
    adapter = adapter_loader or apply_lora
    if isinstance(lora_cfg, dict) and lora_cfg.get("enabled") and adapter is not None:
        try:
            model = adapter(model, lora_cfg)
        except Exception:  # pragma: no cover - adapter failure should not crash load
            pass
    dtype_value = _resolve_torch_dtype(config.get("dtype"))
    if dtype_value is not None:
        try:
            model = model.to(dtype_value)
        except Exception:  # pragma: no cover - invalid dtype/device combination
            pass
    device_value = _normalise_device(config.get("device"))
    if device_value is not None:
        try:
            model = model.to(device_value)
        except Exception:  # pragma: no cover - invalid device
            pass
    return model


def list_models() -> list[str]:
    """Return available model registrations."""

    return model_registry.list()


__all__ = ["model_registry", "register_model", "get_model", "list_models"]
