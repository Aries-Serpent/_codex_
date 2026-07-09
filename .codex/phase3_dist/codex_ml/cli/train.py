"""Hydra-powered entrypoint for the toy training loop."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional

try:
    import hydra

    to_absolute_path = hydra.utils.to_absolute_path
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    try:
        import config_legacy as hydra  # type: ignore[no-redef]

        to_absolute_path = hydra.utils.to_absolute_path
    except (ImportError, ModuleNotFoundError):
        hydra = None

        def to_absolute_path(path: str) -> str:
            return str(Path(path).resolve())


from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.plugins import load_entry_point_plugins
from codex_ml.train_loop import run_training
from codex_ml.utils import repro

try:
    from omegaconf import DictConfig, ListConfig, OmegaConf
except ImportError:  # pragma: no cover — omegaconf optional in lightweight envs
    DictConfig = Any  # type: ignore[misc,assignment]
    ListConfig = Any  # type: ignore[misc,assignment]
    OmegaConf = None  # type: ignore[misc,assignment]

_ = (ArgparseJSONParser, run_cmd)

LOGGER = logging.getLogger(__name__)


def _to_path(value: Optional[str | Path]) -> Optional[Path]:
    if value is None:
        return None
    return Path(to_absolute_path(str(value)))


def _cfg_to_dict(value: Any) -> dict[str, Any]:
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


def _coerce_sequence(value: Any) -> Optional[list[Any]]:
    """Return ``value`` as a list when it represents a textual sequence."""

    if value is None:
        return None
    if isinstance(value, ListConfig):
        return list(value)
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str):
        return [value]
    return None


def _sanitize_prompt_sequence(values: list[Any]) -> tuple[list[Any], bool]:
    """Sanitise prompt-like entries using the safety module when available."""

    try:
        from codex_ml.safety import SafetyConfig, sanitize_prompt
    except (ImportError, AttributeError):  # pragma: no cover - safety module optional
        return list(values), False

    cfg = SafetyConfig()
    sanitised: list[Any] = []
    changed = False
    for entry in values:
        if isinstance(entry, str):
            result = sanitize_prompt(entry, cfg)
            text = result.get("text", entry)
            sanitised.append(text)
            if text != entry:
                changed = True
            continue
        if isinstance(entry, dict):
            updated = dict(entry)
            mutated = False
            for key in ("prompt", "input", "text"):
                raw = updated.get(key)
                if isinstance(raw, str):
                    result = sanitize_prompt(raw, cfg)
                    text = result.get("text", raw)
                    if text != raw:
                        updated[key] = text
                        mutated = True
            sanitised.append(updated if mutated else entry)
            if mutated:
                changed = True
            continue
        sanitised.append(entry)
    return sanitised, changed


def _apply_prompt_sanitization(
    config_obj: Any,
    keys: Sequence[str],
    *,
    update_dict: Optional[dict[str, Any]] = None,
) -> int:
    """Sanitise string sequences stored under ``keys`` inside ``config_obj``."""

    if config_obj is None:
        return 0
    total = 0
    for key in keys:
        try:
            raw = config_obj.get(key) if hasattr(config_obj, "get") else getattr(config_obj, key)
        except (ValueError, TypeError, RuntimeError):
            logger.warning("Exception occurred", exc_info=True)
            raw = None
        sequence = _coerce_sequence(raw)
        if sequence is None or not sequence:
            continue
        sanitised, changed = _sanitize_prompt_sequence(sequence)
        if not changed:
            continue
        total += 1
        if update_dict is not None:
            update_dict[key] = sanitised
        try:
            if isinstance(config_obj, (DictConfig, dict)):
                config_obj[key] = sanitised
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    return total


def _run_from_cfg(cfg: DictConfig) -> tuple[int, Optional[Path]]:
    artifacts_cfg = _cfg_to_dict(cfg.get("artifacts"))
    art_dir = _to_path(cfg.get("artifacts_dir") or artifacts_cfg.get("dir"))

    dataset_cfg = cfg.get("dataset")
    dataset_cfg_dict: dict[str, Any] = {}
    dataset_sources_raw = []
    dataset_cache_dir = None
    dataset_cast_policy = None
    if isinstance(dataset_cfg, (DictConfig, dict)):
        dataset_cfg_dict = _cfg_to_dict(dataset_cfg)
        dataset_sources_raw = _cfg_to_list(dataset_cfg_dict.get("sources"))
        dataset_cache_dir = dataset_cfg_dict.get("cache_dir")
        dataset_cast_policy = dataset_cfg_dict.get("cast_policy")
    else:
        dataset_sources_raw = _cfg_to_list(cfg.get("dataset_sources"))
        dataset_cache_dir = cfg.get("dataset_cache_dir")
        dataset_cast_policy = cfg.get("dataset_cast_policy")
    dataset_sources = [p for p in (_to_path(item) for item in dataset_sources_raw) if p is not None]
    dataset_cache_path = _to_path(dataset_cache_dir)

    sanitize_flag = True
    raw_flag = cfg.get("sanitize_prompts")
    if isinstance(raw_flag, bool):
        sanitize_flag = raw_flag
    training_section = cfg.get("training")
    if isinstance(training_section, (DictConfig, dict)):
        training_dict = _cfg_to_dict(training_section)
        if "sanitize_prompts" in training_dict:
            sanitize_flag = bool(training_dict["sanitize_prompts"])

    if sanitize_flag:
        total_sanitised = 0
        if dataset_cfg_dict:
            total_sanitised += _apply_prompt_sanitization(
                dataset_cfg,
                ("train_texts", "texts", "val_texts", "eval_texts"),
                update_dict=dataset_cfg_dict,
            )
        total_sanitised += _apply_prompt_sanitization(
            cfg,
            ("texts", "train_texts", "val_texts", "eval_texts"),
        )
        if total_sanitised:
            LOGGER.info(
                "Sanitised %d prompt field(s) in training configuration",
                total_sanitised,
            )
    else:
        LOGGER.debug("Prompt sanitisation disabled via configuration")

    plugin_cfg = _cfg_to_dict(cfg.get("plugins"))
    entry_cfg = _cfg_to_dict(plugin_cfg.get("entry_points"))
    entry_enable = bool(plugin_cfg.get("enable_entry_points", entry_cfg.get("enable", False)))
    entry_groups = entry_cfg.get("groups") or plugin_cfg.get("entry_point_groups")
    groups_spec: Optional[dict[str, str] | list[str]] = None
    if isinstance(entry_groups, dict):
        groups_spec = {str(k): str(v) for k, v in entry_groups.items()}
    elif isinstance(entry_groups, (list, tuple, set)):
        groups_spec = [str(item) for item in entry_groups]
    elif isinstance(entry_groups, str):
        groups_spec = [entry_groups]
    summary = load_entry_point_plugins(
        enable=entry_enable,
        groups=groups_spec,
        logger=LOGGER,
    )
    if entry_enable and any(count for count in summary.values()):
        loaded_str = ", ".join(f"{name}={count}" for name, count in summary.items())
        LOGGER.info("Entry-point plugins loaded: %s", loaded_str)

    checkpoint_cfg = _cfg_to_dict(cfg.get("checkpoint"))
    checkpoint_dir = _to_path(checkpoint_cfg.get("dir") or checkpoint_cfg.get("path"))
    resume = bool(checkpoint_cfg.get("resume", checkpoint_cfg.get("restore", False)))
    retention_policy = _cfg_to_dict(checkpoint_cfg.get("retention")) or None

    model_cfg_container = cfg.get("model")
    model_cfg_dict: dict[str, Any] = {}
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
    metrics_enabled_cfg = telemetry_cfg.get("metrics_enable", telemetry_cfg.get("metrics_enabled"))
    if isinstance(metrics_enabled_cfg, bool) and metrics_enabled_cfg:
        os.environ.setdefault("CODEX_METRICS_ENABLED", "1")
    metrics_port_cfg = telemetry_cfg.get("metrics_port")
    if metrics_port_cfg is not None:
        os.environ["CODEX_METRICS_PORT"] = str(metrics_port_cfg)
    json_disable = telemetry_cfg.get("json_disable", telemetry_cfg.get("json_disabled"))
    if isinstance(json_disable, bool) and json_disable:
        os.environ["CODEX_TELEMETRY_JSON_DISABLE"] = "1"
    ndjson_disable = telemetry_cfg.get("ndjson_disable", telemetry_cfg.get("ndjson_disabled"))
    if isinstance(ndjson_disable, bool) and ndjson_disable:
        os.environ["CODEX_TELEMETRY_NDJSON_DISABLE"] = "1"
    max_items = telemetry_cfg.get("max_items")
    if isinstance(max_items, (int, str)) and str(max_items).strip().isdigit():
        os.environ["CODEX_TELEMETRY_MAX_ITEMS"] = str(max_items)
    max_bytes = telemetry_cfg.get("max_bytes")
    if isinstance(max_bytes, (int, str)) and str(max_bytes).strip().isdigit():
        os.environ["CODEX_TELEMETRY_MAX_BYTES"] = str(max_bytes)
    sample_rate = telemetry_cfg.get("sample_rate")
    try:
        if sample_rate is not None:
            os.environ["CODEX_TELEMETRY_SAMPLE_RATE"] = str(float(sample_rate))
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    scheduler_cfg = _cfg_to_dict(cfg.get("scheduler"))

    session_id_cfg = cfg.get("session_id") or telemetry_cfg.get("session_id")
    if session_id_cfg and not os.getenv("CODEX_SESSION_ID"):
        os.environ["CODEX_SESSION_ID"] = str(session_id_cfg)

    dp_section = cfg.get("differential_privacy")
    if not dp_section:
        dp_section = cfg.get("dp")
    dp_cfg = _cfg_to_dict(dp_section) if dp_section is not None else {}

    reproducibility_cfg = _cfg_to_dict(cfg.get("reproducibility"))
    deterministic_cudnn = bool(reproducibility_cfg.get("cudnn_deterministic", False))

    seed_override = cfg.get("seed", None)
    if seed_override is None:
        seed_override = reproducibility_cfg.get("seed")
    seed: Optional[int]
    try:
        seed = int(seed_override) if seed_override is not None else None
    except (TypeError, ValueError):
        LOGGER.warning("Ignoring non-integer seed override: %s", seed_override)
        seed = None
    if seed is None:
        seed = 0
    try:
        repro.set_seed(seed)
    except (IOError, OSError) as exc:  # pragma: no cover - defensive log path
        LOGGER.warning("Failed to set reproducibility seed %s: %s", seed, exc)
    if isinstance(cfg, DictConfig):
        cfg.seed = seed
        try:
            cfg.reproducibility["seed"] = seed
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
    reproducibility_cfg.setdefault("seed", seed)

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

    reasoning_cfg_dict: Optional[dict[str, Any]] = None
    reasoning_section = cfg.get("reasoning")
    if isinstance(reasoning_section, (DictConfig, dict)):
        candidate = _cfg_to_dict(reasoning_section)
        reasoning_cfg_dict = candidate or None
    if reasoning_cfg_dict is None and isinstance(training_section, (DictConfig, dict)):
        training_reasoning = training_section.get("reasoning")
        if isinstance(training_reasoning, (DictConfig, dict)):
            candidate = _cfg_to_dict(training_reasoning)
            reasoning_cfg_dict = candidate or None

    evaluation_cfg_dict: Optional[dict[str, Any]] = None
    evaluation_section = cfg.get("evaluation")
    if isinstance(evaluation_section, (DictConfig, dict)):
        evaluation_cfg_dict = _cfg_to_dict(evaluation_section) or None
    if evaluation_cfg_dict is None and isinstance(training_section, (DictConfig, dict)):
        training_evaluation = training_section.get("evaluation")
        if isinstance(training_evaluation, (DictConfig, dict)):
            evaluation_cfg_dict = _cfg_to_dict(training_evaluation) or None

    metadata_cfg: Optional[dict[str, Any]] = None
    metadata_section = cfg.get("metadata")
    if isinstance(metadata_section, (DictConfig, dict)):
        metadata_cfg = _cfg_to_dict(metadata_section) or None

    device_raw = cfg.get("device")
    device = str(device_raw) if device_raw not in (None, "") else None

    dtype_raw = cfg.get("dtype")
    dtype = str(dtype_raw) if dtype_raw not in (None, "") else None

    bf16_require_capability = bool(
        cfg.get("bf16_require_capability", False)
        or reproducibility_cfg.get("bf16_require_capability", False)
    )

    # Minimal verification context (non-breaking error capture hook)
    # NOTE: When constructing DataLoader, pass worker_init_fn=seed_worker from utils.torch_det
    # Placeholder for model verification if needed (no current verification step)

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
        bf16_require_capability=bf16_require_capability,
        checkpoint_dir=checkpoint_dir,
        resume=bool(resume),
        scheduler_cfg=scheduler_cfg or None,
        dp_config=dp_cfg or None,
        deterministic_cudnn=deterministic_cudnn,
        retention_policy=retention_policy,
        run_config=OmegaConf.to_container(cfg, resolve=True),
        dataset_cast_policy=dataset_cast_policy,
        reasoning=reasoning_cfg_dict,
        metadata=metadata_cfg,
        evaluation=evaluation_cfg_dict,
    )
    return int(epochs), checkpoint_dir


@hydra.main(
    version_base=None,
    config_path="../../../configs/training/profiles",
    config_name="default",
)
def main(cfg: DictConfig) -> None:
    logger = init_json_logging()
    arg_list = sys.argv[1:]
    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
        epochs, checkpoint_dir = _run_from_cfg(cfg)
        log_event(
            logger,
            "cli.finish",
            prog=sys.argv[0],
            status="ok",
            epochs=epochs,
            checkpoint_dir=str(checkpoint_dir) if checkpoint_dir else None,
        )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
