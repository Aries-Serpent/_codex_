"""Model registry built on :mod:`codex_ml.registry` primitives."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from transformers import AutoModelForCausalLM, AutoModelForMaskedLM, PreTrainedModel

import torch
from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.registry.base import Registry

model_registry = Registry("model", entry_point_group="codex_ml.models")


@model_registry.register("MiniLM")
def _build_minilm(cfg: Dict[str, Any]) -> Any:
    from codex_ml.models.minilm import MiniLM, MiniLMConfig

    return MiniLM(MiniLMConfig(vocab_size=int(cfg.get("vocab_size", 128))))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _resolve_pretrained_identifier(cfg: Dict[str, Any], default: str) -> str:
    for key in ("local_path", "path", "model_path", "pretrained_model_name_or_path", "model_id"):
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
    for key in ("local_path", "path", "model_path", "pretrained_model_name_or_path", "model_id"):
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


def _load_hf_model(task: str, cfg: Dict[str, Any], default: str) -> PreTrainedModel:
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

    kwargs: Dict[str, Any] = {"local_files_only": local_only}
    if trust_remote_code is not None:
        kwargs["trust_remote_code"] = bool(trust_remote_code)

    try:
        return loader.from_pretrained(model_id, **kwargs)
    except OSError as exc:  # pragma: no cover - network/IO errors
        raise RuntimeError(
            f"Unable to load weights for {model_id!r} from local cache. "
            "Provide a `local_path` or set `local_files_only=False` if remote downloads are permitted."
        ) from exc


@model_registry.register("bert-base-uncased")
def _build_default_bert(cfg: Dict[str, Any]) -> PreTrainedModel:
    return _load_hf_model("mlm", cfg, "bert-base-uncased")


@model_registry.register("gpt2-offline")
def _build_offline_gpt2(cfg: Dict[str, Any]) -> PreTrainedModel:
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
def _build_offline_tinyllama(cfg: Dict[str, Any]) -> PreTrainedModel:
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


def get_model(name: str, cfg: Dict[str, Any]) -> Any:
    """Instantiate a model by name and apply LoRA/device settings when requested."""

    builder = model_registry.get(name)
    model = builder(cfg) if callable(builder) else builder
    lora_cfg = cfg.get("lora", {})
    if isinstance(lora_cfg, dict) and lora_cfg.get("enabled"):
        model = apply_lora(model, lora_cfg)
    dtype = cfg.get("dtype")
    if dtype is not None:
        try:
            model = model.to(getattr(torch, str(dtype)))
        except Exception:  # pragma: no cover - invalid dtype
            pass
    device = cfg.get("device")
    if device is not None:
        try:
            model = model.to(device)
        except Exception:  # pragma: no cover - invalid device
            pass
    return model


def list_models() -> list[str]:
    """Return available model registrations."""

    return model_registry.list()


__all__ = ["model_registry", "register_model", "get_model", "list_models"]
