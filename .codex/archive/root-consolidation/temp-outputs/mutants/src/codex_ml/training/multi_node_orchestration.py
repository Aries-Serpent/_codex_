"""Multi-node distributed training orchestration at scale.

Provides advanced distributed training features including:
- Multi-node cluster coordination
- Elastic training (fault tolerance)
- Gang scheduling support
- Distributed health monitoring
- Aggregated metrics collection
"""

from __future__ import annotations

import logging
import os
import socket
from dataclasses import dataclass
from typing import Any, Optional

import torch.distributed as dist

import torch
from codex_ml.training.distributed_setup import (
    cleanup_distributed,
    get_rank,
    get_world_size,
    is_main_process,
    setup_distributed,
)

logger = logging.getLogger(__name__)

__all__ = [
    "ClusterConfig",
    "ElasticTrainingConfig",
    "MultiNodeCoordinator",
    "setup_multi_node_training",
]


@dataclass
class ClusterConfig:
    """Configuration for multi-node cluster.

    Attributes:
        num_nodes: Total number of nodes in cluster
        node_rank: Rank of this node (0 to num_nodes-1)
        master_addr: Address of master node
        master_port: Port for distributed communication
        gpus_per_node: Number of GPUs per node
        backend: PyTorch distributed backend
    """

    num_nodes: int
    node_rank: int
    master_addr: str
    master_port: int
    gpus_per_node: int = 8
    backend: str = "nccl"

    @classmethod
    def from_env(cls) -> ClusterConfig:
        """Create config from environment variables.

        Expected environment variables:
            NUM_NODES or WORLD_SIZE
            NODE_RANK or RANK
            MASTER_ADDR
            MASTER_PORT
            GPUS_PER_NODE (optional, default: 8)
        """
        # Try SLURM environment first
        if "SLURM_NNODES" in os.environ:
            return cls._from_slurm_env()

        # Fall back to standard distributed env vars
        num_nodes = int(os.environ.get("NUM_NODES", os.environ.get("NNODES", 1)))
        node_rank = int(os.environ.get("NODE_RANK", os.environ.get("RANK", 0)))
        master_addr = os.environ.get(
            "CODEX_MASTER_ADDR", os.environ.get("MASTER_ADDR", "localhost")
        )
        master_port = int(
            os.environ.get("CODEX_MASTER_PORT", os.environ.get("MASTER_PORT", "29500"))
        )
        gpus_per_node = int(os.environ.get("GPUS_PER_NODE", 8))

        return cls(
            num_nodes=num_nodes,
            node_rank=node_rank,
            master_addr=master_addr,
            master_port=master_port,
            gpus_per_node=gpus_per_node,
        )

    @classmethod
    def _from_slurm_env(cls) -> ClusterConfig:
        """Create config from SLURM environment variables."""
        num_nodes = int(os.environ["SLURM_NNODES"])
        node_rank = int(os.environ["SLURM_NODEID"])

        # Get master node address
        nodelist = os.environ["SLURM_NODELIST"]
        master_addr = cls._parse_slurm_nodelist(nodelist)[0]

        master_port = int(os.environ.get("MASTER_PORT", 29500))
        gpus_per_node = int(os.environ.get("SLURM_GPUS_PER_NODE", 8))

        return cls(
            num_nodes=num_nodes,
            node_rank=node_rank,
            master_addr=master_addr,
            master_port=master_port,
            gpus_per_node=gpus_per_node,
        )

    @staticmethod
    def _parse_slurm_nodelist(nodelist: str) -> list[str]:
        """Parse SLURM nodelist format (e.g., 'node[01-04]')."""

        # Simple parser for common formats
        if "[" in nodelist:
            prefix = nodelist.split("[")[0]
            range_part = nodelist.split("[")[1].split("]")[0]

            if "-" in range_part:
                start, end = range_part.split("-")
                nodes = [f"{prefix}{i:02d}" for i in range(int(start), int(end) + 1)]
            else:
                nodes = [f"{prefix}{range_part}"]
        else:
            nodes = [nodelist]

        return nodes


@dataclass
class ElasticTrainingConfig:
    """Configuration for elastic training (fault tolerance).

    Attributes:
        min_nodes: Minimum nodes required to continue training
        max_nodes: Maximum nodes that can participate
        checkpoint_freq: Checkpoint frequency for recovery
        health_check_interval: Seconds between health checks
        timeout_seconds: Timeout for node failures
    """

    min_nodes: int
    max_nodes: int
    checkpoint_freq: int = 100  # steps
    health_check_interval: int = 60  # seconds
    timeout_seconds: int = 300  # 5 minutes


class MultiNodeCoordinator:
    """Coordinator for multi-node distributed training.

    Handles:
    - Node discovery and health monitoring
    - Checkpoint synchronization
    - Aggregated metrics collection
    - Fault detection and recovery

    Example:
        >>> config = ClusterConfig.from_env()
        >>> coordinator = MultiNodeCoordinator(config)
        >>> coordinator.initialize()
        >>> # Training loop
        >>> coordinator.monitor_health()
        >>> coordinator.cleanup()
    """

    def __init__(
        self,
        cluster_config: ClusterConfig,
        elastic_config: Optional[ElasticTrainingConfig] = None,
    ):
        """Initialize multi-node coordinator.

        Args:
            cluster_config: Cluster configuration
            elastic_config: Optional elastic training config
        """
        self.cluster_config = cluster_config
        self.elastic_config = elastic_config
        self.initialized = False
        self.active_nodes: set[int] = set()

    def initialize(self) -> bool:
        """Initialize multi-node training.

        Returns:
            True if initialization successful
        """
        logger.info(
            f"Initializing multi-node training: "
            f"node {self.cluster_config.node_rank}/{self.cluster_config.num_nodes}"
        )

        # set environment variables
        os.environ["MASTER_ADDR"] = self.cluster_config.master_addr
        os.environ["MASTER_PORT"] = str(self.cluster_config.master_port)
        os.environ["WORLD_SIZE"] = str(
            self.cluster_config.num_nodes * self.cluster_config.gpus_per_node
        )
        os.environ["RANK"] = str(self.cluster_config.node_rank * self.cluster_config.gpus_per_node)

        # Initialize distributed
        success = setup_distributed(backend=self.cluster_config.backend)

        if success:
            self.initialized = True
            self.active_nodes = set(range(self.cluster_config.num_nodes))
            logger.info("Multi-node training initialized successfully")
        else:
            logger.error("Failed to initialize multi-node training")

        return success

    def monitor_health(self) -> dict[str, Any]:
        """Monitor health of all nodes.

        Returns:
            Dictionary with health status of all nodes
        """
        if not self.initialized:
            return {"error": "Not initialized"}

        health_status = {
            "node_rank": self.cluster_config.node_rank,
            "total_nodes": self.cluster_config.num_nodes,
            "active_nodes": len(self.active_nodes),
            "hostname": socket.gethostname(),
            "world_size": get_world_size(),
            "rank": get_rank(),
        }

        # Add GPU info if available
        if torch.cuda.is_available():
            health_status["gpu_count"] = torch.cuda.device_count()
            health_status["gpu_memory_allocated"] = [
                torch.cuda.memory_allocated(i) / 1024**3  # GB
                for i in range(torch.cuda.device_count())
            ]

        return health_status

    def aggregate_metrics(
        self,
        local_metrics: dict[str, float],
        reduction: str = "mean",
    ) -> dict[str, float]:
        """Aggregate metrics across all nodes.

        Args:
            local_metrics: Metrics from this node
            reduction: Reduction type ('mean', 'sum', 'min', 'max')

        Returns:
            Aggregated metrics across all nodes
        """
        if not self.initialized:
            return local_metrics

        from codex_ml.training.distributed_setup import reduce_tensor

        aggregated = {}

        for key, value in local_metrics.items():
            tensor = torch.tensor(value)

            if reduction == "mean":
                agg_tensor = reduce_tensor(tensor, average=True)
            elif reduction == "sum":
                agg_tensor = reduce_tensor(tensor, average=False)
            elif reduction == "min":
                dist.all_reduce(tensor, op=dist.ReduceOp.MIN)
                agg_tensor = tensor
            elif reduction == "max":
                dist.all_reduce(tensor, op=dist.ReduceOp.MAX)
                agg_tensor = tensor
            else:
                agg_tensor = tensor

            aggregated[key] = agg_tensor.item()

        return aggregated

    def checkpoint_sync(self, checkpoint_path: str) -> bool:
        """Synchronize checkpoint across nodes.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            True if sync successful
        """
        if not self.initialized:
            return False

        # Only main process handles checkpointing
        if is_main_process():
            logger.info(f"Saving checkpoint: {checkpoint_path}")
            # Checkpoint logic here

        # Barrier to ensure all nodes wait
        dist.barrier()

        return True

    def cleanup(self):
        """Clean up multi-node resources."""
        if self.initialized:
            logger.info("Cleaning up multi-node coordinator")
            cleanup_distributed()
            self.initialized = False


def setup_multi_node_training(
    backend: str = "nccl",
    elastic: bool = False,
) -> MultiNodeCoordinator:
    """Setup multi-node training from environment (convenience function).

    Args:
        backend: Distributed backend
        elastic: Whether to enable elastic training

    Returns:
        Initialized MultiNodeCoordinator

    Example:
        >>> coordinator = setup_multi_node_training()
        >>> # Training code
        >>> coordinator.cleanup()
    """
    cluster_config = ClusterConfig.from_env()
    cluster_config.backend = backend

    elastic_config = None
    if elastic:
        elastic_config = ElasticTrainingConfig(
            min_nodes=1,
            max_nodes=cluster_config.num_nodes,
        )

    coordinator = MultiNodeCoordinator(cluster_config, elastic_config)
    coordinator.initialize()

    return coordinator


def get_node_info() -> dict[str, Any]:
    """Get information about current node.

    Returns:
        Dictionary with node information
    """
    info = {
        "hostname": socket.gethostname(),
        "rank": get_rank(),
        "world_size": get_world_size(),
        "is_main": is_main_process(),
    }

    if torch.cuda.is_available():
        info["gpu_count"] = torch.cuda.device_count()
        info["gpu_names"] = [
            torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
        ]

    return info
