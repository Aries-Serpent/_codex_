from __future__ import annotations

from typing import Tuple

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - handle missing torch lazily
    torch = None  # type: ignore[assignment]


class SimpleTrainer:
    """Minimal trainer for deterministic smoke tests."""

    def __init__(
        self, model: "torch.nn.Module", optimizer: "torch.optim.Optimizer", device: str = "cpu"
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device

    def step(self, batch: Tuple["torch.Tensor", "torch.Tensor"]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())
