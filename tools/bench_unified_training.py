"""Benchmark a minimal training loop using ``UnifiedTrainingConfig`` defaults.

This helper mirrors the configuration surface of
:mod:`codex_ml.training.unified_training` but executes a lightweight
synthetic PyTorch regression loop so it can run without the heavy functional
backend dependencies.
"""

from __future__ import annotations

import argparse
import statistics
import time
from dataclasses import dataclass
from typing import Iterable, List

try:
    import torch
except Exception as exc:  # pragma: no cover - optional dependency path
    raise SystemExit(f"PyTorch is required for this benchmark: {exc}")

from codex_ml.training.unified_training import UnifiedTrainingConfig


@dataclass
class BenchmarkResult:
    rounds: int
    mean_s: float
    median_s: float
    min_s: float
    max_s: float


def _make_loader(cfg: UnifiedTrainingConfig) -> Iterable[tuple[torch.Tensor, torch.Tensor]]:
    g = torch.Generator().manual_seed(cfg.seed)
    x = torch.randn(cfg.batch_size * 4, 16, generator=g)
    true_w = torch.randn(16, 4, generator=g)
    y = x @ true_w
    ds = torch.utils.data.TensorDataset(x, y)
    return torch.utils.data.DataLoader(ds, batch_size=cfg.batch_size, shuffle=True)


def _train_once(cfg: UnifiedTrainingConfig) -> float:
    loader = _make_loader(cfg)
    model = torch.nn.Linear(16, 4)
    opt = torch.optim.SGD(model.parameters(), lr=cfg.learning_rate)
    loss_fn = torch.nn.MSELoss()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    start = time.perf_counter()
    for _ in range(cfg.epochs):
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad(set_to_none=True)
            preds = model(xb)
            loss = loss_fn(preds, yb)
            loss.backward()
            if cfg.grad_clip_norm:
                torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip_norm)
            opt.step()
    return time.perf_counter() - start


def bench(rounds: int, epochs: int, batch_size: int, grad_clip: float | None) -> BenchmarkResult:
    durations: List[float] = []
    for _ in range(rounds):
        cfg = UnifiedTrainingConfig(
            model_name="bench",
            epochs=epochs,
            batch_size=batch_size,
            grad_clip_norm=grad_clip,
        )
        durations.append(_train_once(cfg))
    return BenchmarkResult(
        rounds=rounds,
        mean_s=statistics.mean(durations),
        median_s=statistics.median(durations),
        min_s=min(durations),
        max_s=max(durations),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=3, help="Number of repetitions (default: 3).")
    parser.add_argument("--epochs", type=int, default=1, help="Epochs per run (default: 1).")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (default: 32).")
    parser.add_argument("--grad-clip", type=float, help="Optional gradient clip norm.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = bench(
        max(1, args.rounds), max(1, args.epochs), max(1, args.batch_size), args.grad_clip
    )
    for field in ("rounds", "mean_s", "median_s", "min_s", "max_s"):
        print(f"{field}: {getattr(result, field)}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
