#!/usr/bin/env python3
"""Codex remediation workflow template."""

from __future__ import annotations

import argparse
from pathlib import Path

from codex_ml.train_loop import run_training
from codex_ml.utils.provenance import export_environment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run demo training with reproducibility artefacts")
    parser.add_argument(
        "--art-dir",
        type=Path,
        default=Path("artifacts/metrics"),
        help="Output directory for metrics",
    )
    parser.add_argument("--epochs", type=int, default=1, help="Number of demo epochs to execute")
    parser.add_argument("--grad-accum", type=int, default=1, help="Gradient accumulation steps")
    parser.add_argument(
        "--dry-run", action="store_true", help="List planned actions without executing them"
    )
    return parser.parse_args()


def load_context(root: Path, args: argparse.Namespace) -> None:
    """Gather repository context and execute the reproducible training demo."""

    metrics_dir = root / args.art_dir
    if args.dry_run:
        print(f"[dry-run] would export environment to {metrics_dir}")
        print(
            f"[dry-run] would run training for {args.epochs} epoch(s) with grad_accum={args.grad_accum}"
        )
        return
    export_environment(metrics_dir, command="codex_ml.train_loop", seed=0)
    run_training(
        epochs=args.epochs,
        grad_accum=args.grad_accum,
        mlflow_enable=False,
        telemetry_enable=False,
        art_dir=metrics_dir,
    )
    print(f"Training complete; metrics available under {metrics_dir}")


def main() -> None:
    args = parse_args()
    repo_root = Path(".").resolve()
    load_context(repo_root, args)


if __name__ == "__main__":
    main()
