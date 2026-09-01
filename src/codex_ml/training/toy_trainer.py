#!/usr/bin/env python3
"""
Toy trainer loop for `_codex_`.

Purpose:
- Provide a minimal training loop to enable end-to-end tests and status reporting.
- No heavyweight ML dependencies required; simulates epochs, loss decay, and writes a perf log.

Usage:
    python -m src.codex_ml.training.toy_trainer --epochs 3 --batch-size 16 --log runs/examples/train.log
"""  # noqa: E501

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from codex.logging.adapter import get_default_logger


def train(epochs: int, batch_size: int, log_path: Path) -> None:
    rng = random.Random(42)  # nosec B311 — non-cryptographic ML sampling/shuffling
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Simulate training
    base_loss = 1.5
    steps_per_epoch = max(1, 64 // max(1, batch_size))
    t0 = time.time()

    with log_path.open("w", encoding="utf-8") as f:
        for e in range(1, epochs + 1):
            epoch_start = time.time()
            for _ in range(steps_per_epoch):
                # Simulated loss decay with small noise
                base_loss *= 0.98 + rng.random() * 0.01
                time.sleep(0.02)  # Simulated step time
            epoch_time = time.time() - epoch_start
            steps_per_sec = steps_per_epoch / max(1e-9, epoch_time)
            f.write(
                f"epoch={e} loss={base_loss:.4f} steps/s: {steps_per_sec:.2f} epoch_time_s: {epoch_time:.2f}\n"  # noqa: E501
            )

        total_time = time.time() - t0
        f.write(f"total_time_s: {total_time:.2f}\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Toy trainer loop (simulated)")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--log", type=str, default="runs/examples/train.log")
    args = ap.parse_args(argv)

    train(args.epochs, args.batch_size, Path(args.log))
    get_default_logger().info(f"[OK] Wrote training log to {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
