"""Multi-node distributed training setup with PyTorch DDP.

Provides utilities for distributed training across multiple nodes,
including environment setup, process group initialization, and
distributed data loading.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import torch.distributed as dist

import torch
from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

__all__ = [
    "barrier",
    "cleanup_distributed",
    "get_rank",
    "get_world_size",
    "is_distributed",
    "is_main_process",
    "setup_distributed",
]


def setup_distributed(
    backend: str = "nccl",
    init_method: Optional[str] = None,
    timeout_minutes: int = 30,
) -> bool:
    """Initialize distributed training environment.

    Args:
        backend: Backend to use ('nccl', 'gloo', 'mpi')
        init_method: Initialization method (auto-detected if None)
        timeout_minutes: Timeout for initialization

    Returns:
        True if distributed mode enabled, False otherwise

    Environment Variables:
        RANK: Global rank of the process
        LOCAL_RANK: Local rank on the node
        WORLD_SIZE: Total number of processes
        MASTER_ADDR: Master node address
        MASTER_PORT: Master node port

    Example:
        >>> if setup_distributed():
        ...     model = DistributedDataParallel(model)
        ...     # Training code
        ...     cleanup_distributed()
    """
    # Check if already initialized
    if dist.is_initialized():
        logger.info("Distributed already initialized")
        return True

    # Check if distributed environment variables are set
    rank = int(os.environ.get("RANK", -1))
    local_rank = int(os.environ.get("LOCAL_RANK", -1))
    world_size = int(os.environ.get("WORLD_SIZE", -1))

    if rank == -1 or world_size == -1:
        logger.info("Not running in distributed mode")
        return False

    # Set device for this process
    if backend == "nccl" and torch.cuda.is_available():
        torch.cuda.set_device(local_rank)
        device = f"cuda:{local_rank}"
    else:
        device = "cpu"

    logger.info(
        f"Initializing distributed: rank={rank}, "
        f"local_rank={local_rank}, world_size={world_size}, "
        f"backend={backend}, device={device}"
    )

    # Initialize process group
    try:
        dist.init_process_group(
            backend=backend,
            init_method=init_method,
            rank=rank,
            world_size=world_size,
            timeout=torch.distributed.timedelta(minutes=timeout_minutes),
        )

        logger.info(f"Distributed initialization successful (rank {rank}/{world_size})")
        return True

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.error("Failed to initialize distributed: <ERROR_TYPE>")
        return False


def cleanup_distributed():
    """Clean up distributed training environment."""
    if dist.is_initialized():
        logger.info("Cleaning up distributed process group")
        dist.destroy_process_group()


def is_distributed() -> bool:
    """Check if running in distributed mode."""
    return dist.is_available() and dist.is_initialized()


def get_rank() -> int:
    """Get global rank of current process.

    Returns:
        Global rank (0 if not distributed)
    """
    if not is_distributed():
        return 0
    return dist.get_rank()


def get_world_size() -> int:
    """Get total number of processes.

    Returns:
        World size (1 if not distributed)
    """
    if not is_distributed():
        return 1
    return dist.get_world_size()


def is_main_process() -> bool:
    """Check if this is the main process (rank 0).

    Returns:
        True if main process
    """
    return get_rank() == 0


def barrier() -> None:
    """Synchronize all processes."""
    if is_distributed():
        dist.barrier()


def setup_ddp_model(
    model: torch.nn.Module,
    device_ids: Optional[list] = None,
    find_unused_parameters: bool = False,
) -> torch.nn.Module:
    """Wrap model with DistributedDataParallel.

    Args:
        model: Model to wrap
        device_ids: Device IDs for this process
        find_unused_parameters: Whether to find unused parameters

    Returns:
        Wrapped model (or original if not distributed)

    Example:
        >>> model = MyModel()
        >>> if setup_distributed():
        ...     model = setup_ddp_model(model)
    """
    if not is_distributed():
        return model

    local_rank = int(os.environ.get("LOCAL_RANK", 0))

    if device_ids is None and torch.cuda.is_available():
        device_ids = [local_rank]

    logger.info(f"Wrapping model with DDP (device_ids={device_ids})")

    return torch.nn.parallel.DistributedDataParallel(
        model,
        device_ids=device_ids,
        find_unused_parameters=find_unused_parameters,
    )


def get_distributed_sampler(
    dataset,
    shuffle: bool = True,
    seed: int = 0,
    drop_last: bool = False,
):
    """Create a DistributedSampler for the dataset.

    Args:
        dataset: PyTorch Dataset
        shuffle: Whether to shuffle
        seed: Random seed
        drop_last: Whether to drop last incomplete batch

    Returns:
        DistributedSampler (or None if not distributed)

    Example:
        >>> sampler = get_distributed_sampler(dataset, shuffle=True)
        >>> dataloader = DataLoader(dataset, sampler=sampler)
    """
    if not is_distributed():
        return None

    return torch.utils.data.DistributedSampler(
        dataset,
        num_replicas=get_world_size(),
        rank=get_rank(),
        shuffle=shuffle,
        seed=seed,
        drop_last=drop_last,
    )


def reduce_tensor(tensor: torch.Tensor, average: bool = True) -> torch.Tensor:
    """Reduce tensor across all processes.

    Args:
        tensor: Tensor to reduce
        average: Whether to average (vs sum)

    Returns:
        Reduced tensor

    Example:
        >>> loss_tensor = torch.tensor(loss)
        >>> avg_loss = reduce_tensor(loss_tensor, average=True)
    """
    if not is_distributed():
        return tensor

    rt = tensor.clone()
    dist.all_reduce(rt, op=dist.ReduceOp.SUM)

    if average:
        rt /= get_world_size()

    return rt


def gather_tensor(tensor: torch.Tensor, dst: int = 0):
    """Gather tensor from all processes to destination rank.

    Args:
        tensor: Tensor to gather
        dst: Destination rank

    Returns:
        List of tensors (on dst rank), None on other ranks

    Example:
        >>> predictions = torch.tensor([1, 2, 3])
        >>> all_preds = gather_tensor(predictions, dst=0)
        >>> if is_main_process():
        ...     logger.info(all_preds)  # List of tensors from all ranks
    """
    if not is_distributed():
        return [tensor]

    world_size = get_world_size()

    if get_rank() == dst:
        tensor_list = [torch.zeros_like(tensor) for _ in range(world_size)]
        dist.gather(tensor, gather_list=tensor_list, dst=dst)
        return tensor_list
    dist.gather(tensor, dst=dst)
    return None


def print_once(message: str, rank: int = 0):
    """Print message only on specified rank.

    Args:
        message: Message to print
        rank: Rank to print on (default: 0)
    """
    if get_rank() == rank:
        logger.info(message)


def log_once(message: str, level: str = "info", rank: int = 0):
    """Log message only on specified rank.

    Args:
        message: Message to log
        level: Log level ('info', 'warning', 'error')
        rank: Rank to log on (default: 0)
    """
    if get_rank() == rank:
        getattr(logger, level)(message)
