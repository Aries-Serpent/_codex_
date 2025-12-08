"""
Optional Ray Train integration for cluster-scale distributed training.

Requires: pip install "ray[train]"
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "RAY_AVAILABLE",
    "check_ray_available",
    "RayDistributedTrainer",
    "ray_train_loop",
]

# Check Ray availability
try:
    import ray
    from ray import train
    from ray.train.torch import TorchTrainer
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    logger.debug("Ray not installed, Ray-based distributed training unavailable")


def check_ray_available() -> bool:
    """Check if Ray is available."""
    return RAY_AVAILABLE


class RayDistributedTrainer:
    """Ray-based distributed trainer for cluster-scale training."""
    
    def __init__(
        self,
        train_fn: Callable,
        num_workers: int = 2,
        use_gpu: bool = True,
        resources_per_worker: Optional[Dict[str, float]] = None,
    ):
        if not RAY_AVAILABLE:
            raise ImportError(
                "Ray is not installed. Install with: pip install 'ray[train]'"
            )
        
        self.train_fn = train_fn
        self.num_workers = num_workers
        self.use_gpu = use_gpu
        self.resources_per_worker = resources_per_worker or {}
        
        if use_gpu and "GPU" not in self.resources_per_worker:
            self.resources_per_worker["GPU"] = 1
    
    def train(
        self,
        train_config: Dict[str, Any],
        num_epochs: int = 10,
    ) -> Any:
        """Run distributed training.
        
        Args:
            train_config: Training configuration
            num_epochs: Number of epochs
            
        Returns:
            Training result
        """
        from ray.train import ScalingConfig
        
        scaling_config = ScalingConfig(
            num_workers=self.num_workers,
            use_gpu=self.use_gpu,
            resources_per_worker=self.resources_per_worker,
        )
        
        trainer = TorchTrainer(
            train_loop_per_worker=self.train_fn,
            train_loop_config=train_config,
            scaling_config=scaling_config,
        )
        
        result = trainer.fit()
        return result


def ray_train_loop(config: Dict[str, Any]) -> None:
    """Example Ray training loop.
    
    This function runs on each worker.
    """
    if not RAY_AVAILABLE:
        raise ImportError("Ray is not installed")
    
    from ray.train.torch import prepare_model, prepare_data_loader
    
    # Get distributed info
    world_size = train.get_context().get_world_size()
    rank = train.get_context().get_world_rank()
    
    logger.info(f"Worker {rank}/{world_size} starting training")
    
    # Create model and dataloader
    model = config["model_fn"]()
    dataloader = config["dataloader_fn"]()
    
    # Prepare for distributed training
    model = prepare_model(model)
    dataloader = prepare_data_loader(dataloader)
    
    # Training loop
    for epoch in range(config.get("num_epochs", 10)):
        for batch in dataloader:
            # ... training step ...
            pass
        
        # Report metrics
        train.report({"epoch": epoch, "loss": 0.0})
