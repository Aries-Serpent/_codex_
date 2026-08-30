"""Minimal training CLI for _codex_."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger
from codex_ml.cli import utils as cli_utils  # type: ignore[attr-defined]
from codex_ml.logging.experiment import ExperimentTracker


def _import_training_loop() -> object:
    from codex_ml.training import loop as training_loop

    return training_loop


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal training CLI for _codex_.")
    parser.add_argument(
        "--config",
        type=str,
        default="conf/minimal_train.yaml",
        help="Path to YAML config (default: conf/minimal_train.yaml).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=123,
        help="Global seed to use (default: 123).",
    )
    parser.add_argument(
        "--runs-dir",
        type=str,
        default="runs",
        help="Base directory for run outputs (default: runs).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=10,
        help="Maximum training steps for this minimal run (default: 10).",
    )
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="",
        help="Optional experiment name for tracking (default: empty).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_argparser()
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config: dict[str, Any] = cli_utils.load_yaml_config(config_path)

    base_runs = Path(args.runs_dir)
    ctx = cli_utils.create_run_dir(base_runs, mode="train", seed=args.seed)
    ctx.config_path = str(config_path)
    cli_utils.write_run_manifest(ctx, config)

    tracker = ExperimentTracker(run_dir=ctx.run_dir, mode="train", run_id=ctx.run_id)
    tracker.log_experiment(
        experiment_name=args.experiment_name,
        labels={
            "source": "train_minimal",
            "config_path": str(config_path),
        },
    )

    training_loop = _import_training_loop()
    training_loop.run_minimal_training(  # type: ignore[attr-defined]
        config=config,
        max_steps=args.max_steps,
        run_dir=ctx.run_dir,
    )

    logger.info(f"[train_minimal] Completed run in {ctx.run_dir}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
