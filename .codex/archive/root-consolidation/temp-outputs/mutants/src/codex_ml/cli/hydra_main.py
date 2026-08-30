"""Hydra CLI entrypoint for Codex training using structured configs."""

from __future__ import annotations

import argparse
import json
import logging

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)
import platform
import sys
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

from codex_ml.cli.config import AppConfig, register_configs
from codex_ml.codex_data import DataConfig, load_dataset
from codex_ml.codex_model import ModelConfig, build_codex_model
from codex_ml.data.reasoning_manifest import list_reasoning_corpora
from codex_ml.tracking.experiments import (
    finish_run,
    log_metric,
    new_run_info,
    start_run,
)
from codex_ml.training import run_functional_training

try:
    from codex_ml import distributed as _distributed  # type: ignore[attr-defined]
except (ImportError, AttributeError):  # pragma: no cover - safe fallback

    def init_distributed_if_needed(*_args, **_kwargs) -> bool:
        return False

    def cleanup_distributed() -> None:
        return None

else:  # pragma: no cover - executed when distributed helpers are available
    init_distributed_if_needed = _distributed.init_distributed_if_needed
    cleanup_distributed = _distributed.cleanup


from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = (ArgparseJSONParser, run_cmd)

_CURRICULUM_PRESETS = {
    "rehearsal": "rehearsal",
    "difficulty": "difficulty_curriculum",
    "interleaved": "interleaved_rehearsal",
}

_CORPUS_CHOICES = tuple(sorted(list_reasoning_corpora()))

try:  # pragma: no cover - hydra optional at runtime
    try:
        import hydra
    except ImportError as e:
        error_type = type(e).__name__
        logger.debug("hydra not available: <ERROR_TYPE>")
        import config_legacy as hydra  # type: ignore[no-redef]

    from omegaconf import DictConfig, OmegaConf
except (ImportError, AttributeError):  # pragma: no cover - degrade gracefully when hydra missing
    hydra = None
    DictConfig = type("_DictConfig", (), {})  # type: ignore[misc,assignment]
    OmegaConf = None  # type: ignore[misc,assignment]


register_configs()


LOGGER = logging.getLogger(__name__)


def _probe_payload() -> dict[str, Any]:
    ok = hydra is not None
    reason = None if ok else "hydra-missing"
    return {
        "ok": ok,
        "reason": reason,
        "component": "codex-train",
        "python": ".".join(map(str, sys.version_info[:3])),
        "platform": platform.platform(),
    }


def _to_mapping(cfg: Any) -> Mapping[str, Any]:
    """Convert Hydra config objects to a plain mapping."""

    if OmegaConf is not None and isinstance(cfg, DictConfig):
        container = OmegaConf.to_container(cfg, resolve=True)
        if isinstance(container, Mapping):
            return container
        return {"config": container}

    if is_dataclass(cfg):
        return asdict(cfg)  # type: ignore[arg-type]

    if isinstance(cfg, Mapping):
        return dict(cfg)

    return {"config": cfg}


def _load_yaml_defaults() -> Mapping[str, Any]:
    if OmegaConf is None:
        return {}
    config_dir = Path(__file__).resolve().parents[2] / "configs"
    default_yaml = config_dir / "default.yaml"
    if not default_yaml.is_file():
        return {}
    try:
        loaded = OmegaConf.load(str(default_yaml))
        container = OmegaConf.to_container(loaded, resolve=True)
        if isinstance(container, Mapping):
            return container
    except (IOError, OSError):
        logger.debug("Failed to load YAML defaults from %s", default_yaml, exc_info=True)
    return {}


def _load_conf_defaults(overrides: Sequence[str]) -> Mapping[str, Any]:
    conf_root = Path(__file__).resolve().parents[2] / "conf"
    config_path = conf_root / "config.yaml"
    if not config_path.exists():
        return {
            "model": {
                "base_model_path": None,
                "dtype": "float32",
                "device": "cpu",
                "enable_lora": False,
            },
            "data": {
                "dataset_path": "data/sample.jsonl",
                "train_ratio": 0.8,
                "val_ratio": 0.1,
                "test_ratio": 0.1,
                "seed": 42,
            },
            "experiment": {"name": "offline-default"},
        }
    try:
        cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except (IOError, OSError):
        logger.debug("Failed to load YAML config from %s", config_path, exc_info=True)
        return {}

    if overrides:
        cfg.setdefault("overrides", [])
        cfg["overrides"].extend(list(overrides))
    return cfg


def _ensure_local_dataset(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    samples = [
        {"text": "example-0", "label": 0},
        {"text": "example-1", "label": 1},
        {"text": "example-2", "label": 0},
        {"text": "example-3", "label": 1},
    ]
    path.write_text("\n".join(json.dumps(sample) for sample in samples), encoding="utf-8")


def _run_minimal_training(cfg: Mapping[str, Any]) -> Mapping[str, Any]:
    model_cfg = cfg.get("model", {}) if isinstance(cfg, Mapping) else {}
    data_cfg = cfg.get("data", {}) if isinstance(cfg, Mapping) else {}
    exp_cfg = cfg.get("experiment", {}) if isinstance(cfg, Mapping) else {}
    dataset_path = Path(data_cfg.get("dataset_path", "data/sample.jsonl"))
    _ensure_local_dataset(dataset_path)

    data_config = DataConfig(
        dataset_path=dataset_path,
        train_ratio=float(data_cfg.get("train_ratio", 0.8) or 0.8),
        val_ratio=float(data_cfg.get("val_ratio", 0.1) or 0.1),
        test_ratio=float(data_cfg.get("test_ratio", 0.1) or 0.1),
        seed=int(data_cfg.get("seed", 42) or 42),
        cache_dir=data_cfg.get("cache_dir", "artifacts/cache"),
    )
    splits = load_dataset(data_config)

    model_config = ModelConfig(
        base_model_path=model_cfg.get("base_model_path"),
        dtype=model_cfg.get("dtype"),
        device=model_cfg.get("device"),
        enable_lora=bool(model_cfg.get("enable_lora", False)),
        lora_r=int(model_cfg.get("lora_r", 4) or 4),
        lora_alpha=int(model_cfg.get("lora_alpha", 8) or 8),
        lora_dropout=float(model_cfg.get("lora_dropout", 0.05) or 0.05),
        lora_target_modules=tuple(model_cfg.get("lora_target_modules", ()) or ()),
        lora_task_type=str(model_cfg.get("lora_task_type", "FEATURE_EXTRACTION")),
    )
    model = build_codex_model(model_config)

    run_info = new_run_info(
        exp_cfg.get("name", "offline-default"),
        git_hash=exp_cfg.get("git_hash", "unknown"),
        config_version=str(exp_cfg.get("config_version", "local")),
        data_version=str(exp_cfg.get("data_version", dataset_path.name)),
        run_id=exp_cfg.get("run_id") or uuid.uuid4().hex[:10],
    )
    run_dir = start_run(run_info)
    log_metric(run_info, "train_samples", len(splits.train))
    log_metric(run_info, "val_samples", len(splits.val))
    log_metric(run_info, "test_samples", len(splits.test))
    finish_run(run_info, status="completed")
    return {
        "run_id": run_info.run_id,
        "run_dir": str(run_dir),
        "train_samples": len(splits.train),
        "val_samples": len(splits.val),
        "test_samples": len(splits.test),
        "model_type": type(model).__name__,
    }


if hydra is not None:  # pragma: no cover - executed when hydra available

    @hydra.main(version_base="1.3", config_path=None, config_name="app")
    def _hydra_entry(cfg: AppConfig) -> Mapping[str, Any]:
        """Hydra entrypoint that resolves configs and runs training."""

        logger = init_json_logging()
        arg_list = sys.argv[1:]
        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)

            resolved = _to_mapping(cfg)
            defaults = _load_yaml_defaults()
            if defaults:
                try:
                    defaults_cfg = OmegaConf.create(defaults)
                    resolved_cfg = OmegaConf.create(resolved)
                    merged_cfg = OmegaConf.merge(defaults_cfg, resolved_cfg)
                    resolved = OmegaConf.to_container(merged_cfg, resolve=True)
                except (ValueError, TypeError, RuntimeError):
                    logger.debug("Hydra defaults merge failed", exc_info=True)
                    combined = dict(defaults)
                    combined.update(dict(resolved))
                    resolved = combined
            initialized = False
            result = None
            try:
                initialized = bool(init_distributed_if_needed())
                if not initialized:
                    sys.stderr.write(
                        "[codex-ddp] disabled (env not set or torch.distributed unavailable)\n"
                    )
                result = run_functional_training(resolved)
            finally:
                if initialized:
                    cleanup_distributed()
            log_event(
                logger,
                "cli.finish",
                prog=sys.argv[0],
                status="ok",
                exit_status="success",
            )
            return result

else:  # pragma: no cover - hydra missing, provide informative failure
    _hydra_entry = None


def _hydra_missing_main(args: Sequence[str], prog: str) -> int:
    logger = init_json_logging()
    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=prog, args=list(args))
        cfg = _load_conf_defaults(args)
        result = _run_minimal_training(cfg)
        log_event(
            logger,
            "cli.finish",
            prog=prog,
            status="ok",
            exit_code=0,
            mode="minimal",
            result=result,
        )
        logger.info(json.dumps({"ok": True, "mode": "minimal", "result": result}))
        return 0


def main(argv: Optional[Sequence[str]] = None) -> Any:
    # --probe-json must be handled BEFORE the hydra availability check so it
    # can function as a lightweight health-probe even when hydra is absent.
    import argparse as _argparse

    _pre = _argparse.ArgumentParser(add_help=False)
    _pre.add_argument("--probe-json", action="store_true", dest="probe_json")
    _pre_ns, _ = _pre.parse_known_args(argv if argv is not None else sys.argv[1:])
    if _pre_ns.probe_json:
        logger = init_json_logging()
        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog="codex-train", args=list(argv or []))
            logger.info(json.dumps(_probe_payload()))
            log_event(
                logger,
                "cli.finish",
                prog="codex-train",
                status="ok",
                mode="probe-json",
                rc=0,
            )
        return 0

    # Check for hydra availability early
    if hydra is None or _hydra_entry is None:
        sys.stderr.write(
            "Error: hydra-core is required for training. Install with: pip install hydra-core\n"
        )
        return 2

    parser_cls = ArgparseJSONParser if ArgparseJSONParser is not None else argparse.ArgumentParser
    parser = parser_cls(prog="codex-train", add_help=False)
    parser.add_argument("--probe-json", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--curriculum",
        choices=tuple(sorted(_CURRICULUM_PRESETS)),
        help="Select a continual-learning preset under configs/training/continual.",
    )
    parser.add_argument(
        "--difficulty-target",
        dest="curriculum_target",
        help="Override continual.curriculum.target (e.g. easy/medium/hard).",
    )
    parser.add_argument(
        "--difficulty-cap",
        dest="difficulty_cap",
        help="Override continual.curriculum.difficulty_cap for interleaved schedules.",
    )
    parser.add_argument(
        "--rehearsal-ratio",
        type=float,
        dest="rehearsal_ratio",
        help="Override continual.rehearsal.replay_ratio.",
    )
    parser.add_argument(
        "--rehearsal-buffer",
        type=int,
        dest="rehearsal_buffer",
        help="Override continual.rehearsal.buffer_size.",
    )
    parser.add_argument(
        "--interleave-every",
        type=int,
        dest="interleave_every",
        help="Override continual.rehearsal.interleave_every_n_steps.",
    )
    if _CORPUS_CHOICES:
        parser.add_argument(
            "--reasoning-corpus",
            choices=_CORPUS_CHOICES,
            help="Override continual.active_corpus using the reasoning manifest.",
        )
    else:  # pragma: no cover - fallback when no corpora registered
        parser.add_argument(
            "--reasoning-corpus",
            help="Override continual.active_corpus using the reasoning manifest.",
        )

    arg_list = list(argv) if argv is not None else sys.argv[1:]
    namespace, remaining = parser.parse_known_args(arg_list)

    if namespace.probe_json:
        logger = init_json_logging()
        with capture_exceptions(logger):
            log_event(logger, "cli.start", prog=parser.prog, args=arg_list)
            logger.info(json.dumps(_probe_payload()))
            log_event(
                logger,
                "cli.finish",
                prog=parser.prog,
                status="ok",
                mode="probe-json",
                rc=0,
            )
            return 0

    overrides = list(remaining)
    if getattr(namespace, "curriculum", None):
        overrides.append(f"training/continual={_CURRICULUM_PRESETS[str(namespace.curriculum)]}")
    if getattr(namespace, "curriculum_target", None):
        overrides.append(f"continual.curriculum.target={namespace.curriculum_target}")
    if getattr(namespace, "difficulty_cap", None):
        overrides.append(f"continual.curriculum.difficulty_cap={namespace.difficulty_cap}")
    if getattr(namespace, "rehearsal_ratio", None) is not None:
        overrides.append(f"continual.rehearsal.replay_ratio={namespace.rehearsal_ratio}")
    if getattr(namespace, "rehearsal_buffer", None) is not None:
        overrides.append(f"continual.rehearsal.buffer_size={int(namespace.rehearsal_buffer)}")
    if getattr(namespace, "interleave_every", None) is not None:
        overrides.append(
            f"continual.rehearsal.interleave_every_n_steps={int(namespace.interleave_every)}"
        )
    if getattr(namespace, "reasoning_corpus", None):
        overrides.append(f"continual.active_corpus={namespace.reasoning_corpus}")

    backup_argv = sys.argv[:]
    try:
        sys.argv = [parser.prog, *overrides]
        return _hydra_entry()
    finally:
        sys.argv = backup_argv


if __name__ == "__main__":  # pragma: no cover - CLI entry
    result = main()
    if isinstance(result, int):
        raise SystemExit(result)
