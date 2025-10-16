from __future__ import annotations

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - handle missing torch lazily
    torch = None  # type: ignore[assignment]


class SimpleTrainer:
    """Minimal trainer for deterministic smoke tests."""

    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def step(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
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

    def save_if_better(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric
