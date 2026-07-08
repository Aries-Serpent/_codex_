"""
Hydra Entry Module

This module provides functionality for hydra entry.

Usage:
    from cli.hydra_entry import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import argparse
import json
import os
import sys
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codex_ml.training.unified_training import UnifiedTrainingConfig

from codex.logging.structured_logger import logger
from codex_ml.data.reasoning_manifest import list_reasoning_corpora

_CURRICULUM_PRESETS = {
    "rehearsal": "rehearsal",
    "difficulty": "difficulty_curriculum",
    "interleaved": "interleaved_rehearsal",
}

_CORPUS_CHOICES = tuple(sorted(list_reasoning_corpora()))


def _print_missing(pkg: str) -> int:
    msg = {
        "ok": False,
        "reason": f"'{pkg}' is not installed; install to use Hydra-driven training.",
        "hint": "pip install hydra-core omegaconf",
    }
    logger.info(json.dumps(msg))
    return 0


def _cfg_to_unified(cfg: Mapping[str, Any]) -> UnifiedTrainingConfig:
    from codex_ml.training.unified_training import UnifiedTrainingConfig

    train = cfg.get("train", {}) if isinstance(cfg, Mapping) else {}
    training_cfg = cfg.get("training", {}) if isinstance(cfg, Mapping) else {}
    run = cfg.get("run", {}) if isinstance(cfg, Mapping) else {}
    model = cfg.get("model", {}) if isinstance(cfg, Mapping) else {}
    data_cfg = cfg.get("data", {}) if isinstance(cfg, Mapping) else {}
    tracking_cfg = cfg.get("tracking", {}) if isinstance(cfg, Mapping) else {}
    continual_cfg = None
    if isinstance(training_cfg, Mapping):
        continual_cfg = training_cfg.get("continual")
    if continual_cfg is None and isinstance(cfg, Mapping):
        continual_cfg = cfg.get("continual")

    return UnifiedTrainingConfig(
        epochs=int(train.get("epochs", 1) or 1),
        grad_accum=int(train.get("grad_accum", 1) or 1),
        grad_clip_norm=train.get("grad_clip_norm"),
        seed=int(run.get("seed", 42) or 42),
        dtype=str(model.get("dtype", "fp32")),
        extra={
            "data": data_cfg,
            "tracking": tracking_cfg,
        },
        continual=continual_cfg,
    )


def _inject_curriculum_flags(argv: list[str]) -> list[str]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--curriculum", choices=tuple(sorted(_CURRICULUM_PRESETS)))
    parser.add_argument("--difficulty-target", dest="curriculum_target")
    parser.add_argument("--difficulty-cap", dest="difficulty_cap")
    parser.add_argument("--rehearsal-ratio", type=float, dest="rehearsal_ratio")
    parser.add_argument("--rehearsal-buffer", type=int, dest="rehearsal_buffer")
    parser.add_argument("--interleave-every", type=int, dest="interleave_every")
    if _CORPUS_CHOICES:
        parser.add_argument("--reasoning-corpus", choices=_CORPUS_CHOICES)
    else:  # pragma: no cover - fallback when no corpora registered
        parser.add_argument("--reasoning-corpus")

    namespace, remaining = parser.parse_known_args(argv)
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

    return overrides


def main(argv=None) -> int:
    try:
        try:
            import hydra
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            import config_legacy as hydra  # type: ignore[no-redef]

        from omegaconf import DictConfig, OmegaConf
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return _print_missing("hydra-core")

    from codex_ml.training.unified_training import run_unified_training

    conf_root = Path("conf")
    hydra_path = conf_root if (conf_root / "config.yaml").is_file() else Path("configs")
    hydra_name = "config" if (hydra_path / "config.yaml").is_file() else "defaults"

    @hydra.main(config_path=str(hydra_path), config_name=hydra_name, version_base=None)
    def _entry(cfg: DictConfig) -> int:
        show_cfg = os.environ.get("CODEX_SHOW_CFG", "0")
        if show_cfg.lower() in {"1", "true", "yes"}:
            logger.info(OmegaConf.to_yaml(cfg, resolve=True))
            return 0

        cfg_dict = OmegaConf.to_container(cfg, resolve=True)
        utc = _cfg_to_unified(cfg_dict if isinstance(cfg_dict, Mapping) else {})
        ndjson_env = os.environ.get("CODEX_NDJSON_LOG") or os.environ.get("CODEX_METRICS_PATH")
        ndjson_path = Path(ndjson_env or "artifacts/metrics.ndjson")
        ndjson_path.parent.mkdir(parents=True, exist_ok=True)
        result = run_unified_training(
            utc,
            callbacks=None,
            ndjson_log_path=str(ndjson_path),
        )
        logger.info(json.dumps({"ok": True, "train_result": result, "config": asdict(utc)}))
        return 0

    overrides = _inject_curriculum_flags(list(argv or sys.argv[1:]))
    original_argv = sys.argv[:]
    prog = original_argv[0] if original_argv else "codex_ml.hydra"
    sys.argv = [prog, *overrides]
    try:
        return _entry()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    sys.exit(main())
