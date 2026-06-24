"""
Codex Exec Module

This module provides functionality for codex exec.

Usage:
    from exec.codex_exec import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


class CodexExecutor:
    """Minimal task runner wiring common Codex entry points."""

    TASKS = {
        "validate-dataset": "Validate dataset manifest",
        "train": "Run training pipeline",
        "evaluate": "Run evaluation",
        "export": "Export model artifacts",
        "audit": "Run codebase audit",
    }

    def __init__(self, offline_mode: bool = False) -> None:
        self.offline_mode = offline_mode

    def validate_dataset(self, manifest_path: Path, *, check_splits: bool = False) -> bool:
        from codex_ml.data.validator import DatasetValidator

        LOGGER.info("[codex] validating manifest %s", manifest_path)
        valid = DatasetValidator.validate_manifest(manifest_path)
        if check_splits:
            valid = valid and DatasetValidator.validate_splits(manifest_path)
        return valid

    def train(self, config_name: str | None = None, **kwargs: Any) -> bool:
        LOGGER.info("[codex] starting training (config=%s)", config_name or "default")
        try:
            from codex_ml.training.unified_training import (
                UnifiedTrainingConfig,
                run_unified_training,
            )

            cfg = UnifiedTrainingConfig()
            if config_name:
                cfg.extra.setdefault("config_name", config_name)
            run_unified_training(cfg)
        except (IOError, OSError) as exc:  # pragma: no cover - defensive fallback
            LOGGER.error("Training failed: %s", exc)
            return False
        return True

    def evaluate(self, checkpoint_path: Path, **_: Any) -> bool:
        LOGGER.info("[codex] evaluation placeholder for %s", checkpoint_path)
        return checkpoint_path.exists()

    def export(self, output_dir: Path | None = None, **_: Any) -> bool:
        target = output_dir or Path("artifacts/export")
        target.mkdir(parents=True, exist_ok=True)
        LOGGER.info("[codex] export staged at %s", target)
        return True

    def audit(self, **_: Any) -> bool:
        LOGGER.info("[codex] audit placeholder")
        return True

    def run_task(self, task_name: str, **kwargs: Any) -> bool:
        normalised = task_name.replace("-", "_")
        if normalised not in {name.replace("-", "_") for name in self.TASKS}:
            LOGGER.error("Unknown task: %s", task_name)
            return False
        method = getattr(self, normalised)
        return bool(method(**kwargs))


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex unified executor")
    parser.add_argument("task", choices=CodexExecutor.TASKS.keys())
    parser.add_argument("--offline", action="store_true", help="Run in offline mode")
    parser.add_argument("--config", type=str, help="Config name for training")
    parser.add_argument("--manifest", type=Path, help="Dataset manifest path")
    parser.add_argument("--check-splits", action="store_true", help="Check dataset split files")
    parser.add_argument("--checkpoint", type=Path, help="Checkpoint for evaluation")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    executor = CodexExecutor(offline_mode=args.offline)

    kwargs: dict[str, Any] = {}
    if args.task == "validate-dataset":
        if args.manifest is None:
            parser.error("--manifest is required for validate-dataset")
        kwargs["manifest_path"] = args.manifest
        kwargs["check_splits"] = args.check_splits
    elif args.task == "train":
        kwargs["config_name"] = args.config
    elif args.task == "evaluate":
        if args.checkpoint is None:
            parser.error("--checkpoint is required for evaluate")
        kwargs["checkpoint_path"] = args.checkpoint
    elif args.task == "export":
        kwargs["output_dir"] = Path("artifacts/export")

    success = executor.run_task(args.task, **kwargs)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
