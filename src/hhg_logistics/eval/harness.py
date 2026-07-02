"""
Harness Module

This module provides functionality for harness.

Usage:
    from eval.harness import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import hydra
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    import config_legacy as hydra  # type: ignore[no-redef]


from omegaconf import DictConfig  # noqa: E402

try:  # pragma: no cover - optional dependency
    from lm_eval import evaluator
except (ImportError, AttributeError):  # pragma: no cover
    evaluator = None


def _default_model_args(cfg: DictConfig) -> str:
    args: list[str] = [f"pretrained={cfg.model.pretrained}"]
    model_args_cfg = cfg.eval.model_args
    if bool(getattr(model_args_cfg, "use_accelerate", False)):
        args.append("use_accelerate=True")
    dtype_value = getattr(model_args_cfg, "dtype", None)
    if dtype_value:
        args.append(f"dtype={dtype_value}")
    return ",".join(args)


def _ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_json(payload: dict[str, Any], destination: Path) -> None:
    _ensure_output_dir(destination)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


@hydra.main(
    config_path="../../../configs/deployment/hhg_logistics",
    config_name="config",
    version_base="1.3",
)
def main(cfg: DictConfig):
    if not bool(getattr(cfg.eval, "enable", False)):
        logger.info("eval.enable is false; skipping evaluation.")
        return {}

    if evaluator is None:
        logger.warning("lm-eval is not installed; skipping evaluation.")
        return {}

    tasks = list(cfg.eval.tasks)
    model_args = _default_model_args(cfg)
    try:
        results = evaluator.simple_evaluate(
            model="hf",
            model_args=model_args,
            tasks=tasks,
            batch_size=cfg.eval.batch_size,
            num_fewshot=cfg.eval.num_fewshot,
            limit=cfg.eval.limit,
        )
    except (IOError, OSError) as exc:  # pragma: no cover
        logger.error("Evaluation failed: %s", exc)
        raise

    output_path = Path(cfg.eval.output_json)
    payload = {
        "tasks": tasks,
        "model": cfg.model.pretrained,
        "results": results,
    }
    _write_json(payload, output_path)
    logger.info("Wrote eval JSON to %s", output_path)
    return payload


if not hasattr(main, "__wrapped__"):
    main.__wrapped__ = main


if __name__ == "__main__":
    main()
