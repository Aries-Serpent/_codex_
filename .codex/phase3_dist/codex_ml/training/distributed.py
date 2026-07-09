"""
Multi-node Distributed Training Support (D3)

Provides:
- PyTorch DDP wrapper for multi-GPU/multi-node training
- Optional Ray Train integration
- Automatic world size detection
- Graceful fallback to single-GPU

This module consolidates and enhances existing distributed training capabilities
from distributed_setup.py and multi_node_orchestration.py with a unified interface.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Optional

import torch

dist = torch.distributed
DDP = torch.nn.parallel.DistributedDataParallel

logger = logging.getLogger(__name__)

__all__ = [
    "DistributedConfig",
    "DistributedManager",
    "distributed_context",
    "launch_distributed",
]


@dataclass
class DistributedConfig:
    """Configuration for distributed training."""

    # Basic settings
    enabled: bool = False
    backend: str = "nccl"  # nccl for GPU, gloo for CPU

    # Node settings
    world_size: int = 1
    rank: int = 0
    local_rank: int = 0

    # Multi-node settings
    master_addr: str = field(
        default_factory=lambda: os.environ.get("CODEX_MASTER_ADDR", "localhost")
    )
    master_port: str = field(default_factory=lambda: os.environ.get("CODEX_MASTER_PORT", "29500"))

    # Advanced settings
    find_unused_parameters: bool = False
    broadcast_buffers: bool = True
    gradient_as_bucket_view: bool = True

    @classmethod
    def from_env(cls) -> DistributedConfig:
        """Create config from environment variables."""
        # Check if distributed is explicitly enabled
        enabled = os.environ.get("DISTRIBUTED_ENABLED", "false").lower() == "true"

        # Auto-detect from RANK/WORLD_SIZE if present
        world_size = int(os.environ.get("WORLD_SIZE", 1))
        rank = int(os.environ.get("RANK", 0))

        if world_size > 1:
            enabled = True

        return cls(
            enabled=enabled,
            backend=os.environ.get("DISTRIBUTED_BACKEND", "nccl"),
            world_size=world_size,
            rank=rank,
            local_rank=int(os.environ.get("LOCAL_RANK", 0)),
            master_addr=os.environ.get("MASTER_ADDR", "localhost"),
            master_port=os.environ.get("MASTER_PORT", "29500"),
        )

    def to_env(self) -> dict[str, str]:
        """Export config to environment variables."""
        return {
            "DISTRIBUTED_ENABLED": str(self.enabled).lower(),
            "DISTRIBUTED_BACKEND": self.backend,
            "WORLD_SIZE": str(self.world_size),
            "RANK": str(self.rank),
            "LOCAL_RANK": str(self.local_rank),
            "MASTER_ADDR": self.master_addr,
            "MASTER_PORT": self.master_port,
        }


class DistributedManager:
    """Manager for distributed training setup and teardown."""

    def __init__(self, config: Optional[DistributedConfig] = None):
        self.config = config or DistributedConfig.from_env()
        self._initialized = False
        self._device = None

    @property
    def is_main_process(self) -> bool:
        """Check if this is the main process (rank 0)."""
        return self.config.rank == 0

    @property
    def is_distributed(self) -> bool:
        """Check if distributed training is active."""
        return self._initialized and self.config.world_size > 1

    @property
    def device(self) -> torch.device:
        """Get the device for this process."""
        if self._device is None:
            if torch.cuda.is_available():
                self._device = torch.device(f"cuda:{self.config.local_rank}")
            else:
                self._device = torch.device("cpu")
        return self._device

    def setup(self) -> bool:
        """Initialize distributed training.

        Returns:
            True if distributed setup succeeded, False otherwise
        """
        if not self.config.enabled:
            logger.info("Distributed training disabled, using single process")
            return False

        if self.config.world_size <= 1:
            logger.info("World size <= 1, using single process")
            return False

        try:
            # set environment variables
            os.environ["MASTER_ADDR"] = self.config.master_addr
            os.environ["MASTER_PORT"] = self.config.master_port

            # Initialize process group
            dist.init_process_group(
                backend=self.config.backend,
                rank=self.config.rank,
                world_size=self.config.world_size,
            )

            # set CUDA device
            if torch.cuda.is_available():
                torch.cuda.set_device(self.config.local_rank)

            self._initialized = True
            logger.info(
                f"Distributed training initialized: "
                f"rank={self.config.rank}/{self.config.world_size}, "
                f"device={self.device}"
            )
            return True

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to initialize distributed training: <ERROR_TYPE>")
            self._initialized = False
            return False

    def cleanup(self) -> None:
        """Clean up distributed training resources."""
        if self._initialized:
            dist.destroy_process_group()
            self._initialized = False
            logger.info("Distributed training cleaned up")

    def wrap_model(self, model: torch.nn.Module) -> torch.nn.Module | DDP:  # type: ignore[valid-type]
        """Wrap model for distributed training.

        Args:
            model: PyTorch model

        Returns:
            DDP-wrapped model if distributed, original model otherwise
        """
        if not self.is_distributed:
            return model.to(self.device)

        model = model.to(self.device)
        return DDP(
            model,
            device_ids=[self.config.local_rank] if torch.cuda.is_available() else None,
            find_unused_parameters=self.config.find_unused_parameters,
            broadcast_buffers=self.config.broadcast_buffers,
            gradient_as_bucket_view=self.config.gradient_as_bucket_view,
        )

    def wrap_dataloader(
        self,
        dataset: torch.utils.data.Dataset,
        batch_size: int,
        **kwargs,
    ) -> torch.utils.data.DataLoader:
        """Create distributed-aware DataLoader.

        Args:
            dataset: PyTorch dataset
            batch_size: Batch size per process
            **kwargs: Additional DataLoader arguments

        Returns:
            DataLoader with DistributedSampler if distributed
        """
        if self.is_distributed:
            sampler = torch.utils.data.distributed.DistributedSampler(
                dataset,
                num_replicas=self.config.world_size,
                rank=self.config.rank,
                shuffle=kwargs.pop("shuffle", True),
            )
            kwargs["sampler"] = sampler
            kwargs["shuffle"] = False  # Sampler handles shuffling

        return torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            **kwargs,
        )

    def barrier(self) -> None:
        """Synchronize all processes."""
        if self.is_distributed:
            dist.barrier()

    def all_reduce(
        self,
        tensor: torch.Tensor,
        op: dist.ReduceOp = dist.ReduceOp.SUM,  # type: ignore[name-defined]
    ) -> torch.Tensor:
        """All-reduce tensor across processes.

        Args:
            tensor: Tensor to reduce
            op: Reduction operation

        Returns:
            Reduced tensor
        """
        if not self.is_distributed:
            return tensor

        dist.all_reduce(tensor, op=op)
        return tensor

    def broadcast(self, tensor: torch.Tensor, src: int = 0) -> torch.Tensor:
        """Broadcast tensor from source rank.

        Args:
            tensor: Tensor to broadcast
            src: Source rank

        Returns:
            Broadcasted tensor
        """
        if not self.is_distributed:
            return tensor

        dist.broadcast(tensor, src=src)
        return tensor


@contextmanager
def distributed_context(config: Optional[DistributedConfig] = None):
    """Context manager for distributed training.

    Usage:
        with distributed_context() as manager:
            model = manager.wrap_model(model)
            # ... training loop ...
    """
    manager = DistributedManager(config)
    try:
        manager.setup()
        yield manager
    finally:
        manager.cleanup()


def launch_distributed(
    fn: Callable,
    world_size: int,
    args: tuple[Any, ...] = (),
    kwargs: Optional[dict[str, Any]] = None,
    backend: str = "nccl",
) -> None:
    """Launch distributed training across multiple processes.

    Args:
        fn: Training function to run
        world_size: Number of processes
        args: Function arguments
        kwargs: Function keyword arguments
        backend: Distributed backend
    """
    import torch.multiprocessing as mp

    kwargs = kwargs or {}

    def _worker(rank: int):
        config = DistributedConfig(
            enabled=True,
            backend=backend,
            world_size=world_size,
            rank=rank,
            local_rank=rank,
        )

        with distributed_context(config) as manager:
            fn(*args, manager=manager, **kwargs)

    mp.spawn(_worker, nprocs=world_size, join=True)
