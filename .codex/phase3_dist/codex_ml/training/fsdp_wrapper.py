"""
Fully Sharded Data Parallel (FSDP) Training Wrapper

This module provides production-ready FSDP training capabilities with:
- Flexible sharding strategies (FULL_SHARD, SHARD_GRAD_OP, NO_SHARD)
- Mixed precision support (FP16, BF16)
- CPU/NVMe offloading for large models
- Activation checkpointing
- Efficient checkpoint management

Author: Codex ML Team
Version: 1.0.0
"""

import functools
import logging
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from torch.distributed.fsdp import (
        BackwardPrefetch,
        CPUOffload,
        FullStateDictConfig,
        MixedPrecision,
        ShardedStateDictConfig,
        ShardingStrategy,
        StateDictType,
    )
    from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

    from torch import nn
else:
    nn = None
    BackwardPrefetch = None
    CPUOffload = None
    FullStateDictConfig = None
    MixedPrecision = None
    ShardedStateDictConfig = None
    ShardingStrategy = None
    StateDictType = None
    FSDP = None

try:
    import torch.distributed.algorithms._checkpoint.checkpoint_wrapper as _ckpt_wrap
    import torch.distributed.fsdp as _fsdp
    import torch.distributed.fsdp.wrap as _fsdp_wrap

    import torch

    nn = torch.nn
    CheckpointImpl = _ckpt_wrap.CheckpointImpl
    apply_activation_checkpointing = _ckpt_wrap.apply_activation_checkpointing
    checkpoint_wrapper = _ckpt_wrap.checkpoint_wrapper
    BackwardPrefetch = _fsdp.BackwardPrefetch

    CPUOffload = _fsdp.CPUOffload

    FullStateDictConfig = _fsdp.FullStateDictConfig

    MixedPrecision = _fsdp.MixedPrecision

    ShardedStateDictConfig = _fsdp.ShardedStateDictConfig

    ShardingStrategy = _fsdp.ShardingStrategy

    StateDictType = _fsdp.StateDictType

    FSDP = _fsdp.FullyShardedDataParallel

    size_based_auto_wrap_policy = _fsdp_wrap.size_based_auto_wrap_policy
    transformer_auto_wrap_policy = _fsdp_wrap.transformer_auto_wrap_policy

    # Verify torch is functional
    _ = torch.Tensor
    TORCH_AVAILABLE = True
except (ImportError, AttributeError) as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    TORCH_AVAILABLE = False
    # Define mock classes for offline/testing
    FSDP = None

    ShardingStrategy = None


class FSDPShardingStrategy(Enum):
    """FSDP sharding strategies."""

    FULL_SHARD = "FULL_SHARD"  # Shard parameters, gradients, and optimizer states
    SHARD_GRAD_OP = "SHARD_GRAD_OP"  # Shard gradients and optimizer states only
    NO_SHARD = "NO_SHARD"  # No sharding (DDP equivalent)
    HYBRID_SHARD = "HYBRID_SHARD"  # Shard within node, replicate across nodes


class FSDPConfig:
    """Configuration for FSDP training."""

    def __init__(
        self,
        sharding_strategy: str = "FULL_SHARD",
        min_num_params: int = 1e8,  # type: ignore[assignment]  # 100M parameters
        use_cpu_offload: bool = False,
        offload_params: bool = True,
        offload_optimizer: bool = True,
        mixed_precision: str = "fp16",  # fp16, bf16, or None
        activation_checkpointing: bool = False,
        checkpoint_transformer_blocks: bool = True,
        forward_prefetch: bool = True,
        backward_prefetch: str = "BACKWARD_PRE",
        limit_all_gathers: bool = True,
        use_orig_params: bool = False,
    ):
        """
        Initialize FSDP configuration.

        Args:
            sharding_strategy: Sharding strategy (FULL_SHARD, SHARD_GRAD_OP, NO_SHARD, HYBRID_SHARD)
            min_num_params: Minimum number of parameters for auto-wrapping
            use_cpu_offload: Enable CPU offloading for parameters/optimizer
            offload_params: Offload parameters to CPU (if use_cpu_offload=True)
            offload_optimizer: Offload optimizer states to CPU (if use_cpu_offload=True)
            mixed_precision: Mixed precision mode (fp16, bf16, or None)
            activation_checkpointing: Enable activation checkpointing
            checkpoint_transformer_blocks: Checkpoint transformer blocks specifically
            forward_prefetch: Enable forward prefetching
            backward_prefetch: Backward prefetch mode (BACKWARD_PRE or BACKWARD_POST)
            limit_all_gathers: Limit all-gather operations
            use_orig_params: Use original parameters (required for some optimizers)
        """
        self.sharding_strategy = sharding_strategy
        self.min_num_params = min_num_params
        self.use_cpu_offload = use_cpu_offload
        self.offload_params = offload_params
        self.offload_optimizer = offload_optimizer
        self.mixed_precision = mixed_precision
        self.activation_checkpointing = activation_checkpointing
        self.checkpoint_transformer_blocks = checkpoint_transformer_blocks
        self.forward_prefetch = forward_prefetch
        self.backward_prefetch = backward_prefetch
        self.limit_all_gathers = limit_all_gathers
        self.use_orig_params = use_orig_params

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "sharding_strategy": self.sharding_strategy,
            "min_num_params": self.min_num_params,
            "use_cpu_offload": self.use_cpu_offload,
            "offload_params": self.offload_params,
            "offload_optimizer": self.offload_optimizer,
            "mixed_precision": self.mixed_precision,
            "activation_checkpointing": self.activation_checkpointing,
            "checkpoint_transformer_blocks": self.checkpoint_transformer_blocks,
            "forward_prefetch": self.forward_prefetch,
            "backward_prefetch": self.backward_prefetch,
            "limit_all_gathers": self.limit_all_gathers,
            "use_orig_params": self.use_orig_params,
        }


class FSDPTrainer:
    """
    Production-ready FSDP trainer with comprehensive features.

    Features:
    - Auto-wrap policies for efficient sharding
    - Mixed precision training
    - CPU offloading for memory efficiency
    - Activation checkpointing
    - Efficient checkpoint management

    Example:
        >>> config = FSDPConfig(sharding_strategy="FULL_SHARD", mixed_precision="bf16")
        >>> trainer = FSDPTrainer(model, config)
        >>> fsdp_model = trainer.wrap_model()
        >>> # Train model with FSDP
    """

    def __init__(
        self,
        model: Optional["nn.Module"] = None,
        config: Optional[FSDPConfig] = None,
    ):
        """
        Initialize FSDP trainer.

        Args:
            model: PyTorch model to wrap with FSDP
            config: FSDP configuration
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is not available. Install with: pip install torch>=2.0.0")

        self.model = model
        self.config = config or FSDPConfig()
        self.fsdp_model: Optional[Any] = None

    def _get_sharding_strategy(self) -> "ShardingStrategy":
        """Get PyTorch FSDP sharding strategy from config."""
        strategy_map = {
            "FULL_SHARD": ShardingStrategy.FULL_SHARD,
            "SHARD_GRAD_OP": ShardingStrategy.SHARD_GRAD_OP,
            "NO_SHARD": ShardingStrategy.NO_SHARD,
            "HYBRID_SHARD": ShardingStrategy.HYBRID_SHARD,
        }
        return strategy_map.get(self.config.sharding_strategy, ShardingStrategy.FULL_SHARD)

    def _get_mixed_precision_policy(self) -> Optional["MixedPrecision"]:
        """Get mixed precision policy from config."""
        if not self.config.mixed_precision:
            return None

        if self.config.mixed_precision == "fp16":
            return MixedPrecision(
                param_dtype=torch.float16,
                reduce_dtype=torch.float16,
                buffer_dtype=torch.float16,
            )
        if self.config.mixed_precision == "bf16":
            return MixedPrecision(
                param_dtype=torch.bfloat16,
                reduce_dtype=torch.bfloat16,
                buffer_dtype=torch.bfloat16,
            )
        return None

    def _get_cpu_offload(self) -> Optional["CPUOffload"]:
        """Get CPU offload configuration."""
        if not self.config.use_cpu_offload:
            return None

        return CPUOffload(offload_params=self.config.offload_params)

    def _get_auto_wrap_policy(
        self,
        transformer_layer_cls: Optional[list[type]] = None,
    ) -> Optional[Callable]:
        """
        Get auto-wrap policy for FSDP.

        Args:
            transformer_layer_cls: list of transformer layer classes to wrap

        Returns:
            Auto-wrap policy function
        """
        if transformer_layer_cls:
            # Transformer-specific wrapping
            return functools.partial(
                transformer_auto_wrap_policy,
                transformer_layer_cls=set(transformer_layer_cls),
            )
        # Size-based wrapping
        return functools.partial(
            size_based_auto_wrap_policy,
            min_num_params=self.config.min_num_params,
        )

    def wrap_model(
        self,
        model: Optional["nn.Module"] = None,
        transformer_layer_cls: Optional[list[type]] = None,
    ) -> "FSDP":
        """
        Wrap model with FSDP.

        Args:
            model: Model to wrap (uses self.model if not provided)
            transformer_layer_cls: list of transformer layer classes for auto-wrapping

        Returns:
            FSDP-wrapped model
        """
        model = model or self.model
        if model is None:
            raise ValueError("Model must be provided either in __init__ or wrap_model")

        # Apply activation checkpointing if requested
        if self.config.activation_checkpointing:
            self._apply_activation_checkpointing(model, transformer_layer_cls)

        # Wrap model with FSDP
        fsdp_model = FSDP(
            model,
            sharding_strategy=self._get_sharding_strategy(),
            mixed_precision=self._get_mixed_precision_policy(),
            cpu_offload=self._get_cpu_offload(),
            auto_wrap_policy=self._get_auto_wrap_policy(transformer_layer_cls),
            backward_prefetch=(
                BackwardPrefetch.BACKWARD_PRE
                if self.config.backward_prefetch == "BACKWARD_PRE"
                else BackwardPrefetch.BACKWARD_POST
            ),
            forward_prefetch=self.config.forward_prefetch,
            limit_all_gathers=self.config.limit_all_gathers,
            use_orig_params=self.config.use_orig_params,
        )

        self.fsdp_model = fsdp_model
        return fsdp_model

    def _apply_activation_checkpointing(
        self,
        model: "nn.Module",
        transformer_layer_cls: Optional[list[type]] = None,
    ):
        """
        Apply activation checkpointing to model.

        Args:
            model: Model to apply checkpointing to
            transformer_layer_cls: list of transformer layer classes to checkpoint
        """
        if not transformer_layer_cls:
            return

        def check_fn(submodule):
            return isinstance(submodule, tuple(transformer_layer_cls))

        apply_activation_checkpointing(
            model,
            checkpoint_wrapper_fn=functools.partial(
                checkpoint_wrapper,
                checkpoint_impl=CheckpointImpl.NO_REENTRANT,
            ),
            check_fn=check_fn,
        )


class FSDPCheckpointManager:
    """
    Efficient checkpoint management for FSDP models.

    Features:
    - Full state dict consolidation
    - Sharded checkpoint save/load
    - Optimizer state management
    - Streaming checkpoint loading

    Example:
        >>> manager = FSDPCheckpointManager()
        >>> manager.save_checkpoint(fsdp_model, optimizer, "checkpoint.pt")
        >>> fsdp_model, optimizer = manager.load_checkpoint("checkpoint.pt", model, optimizer)
    """

    def __init__(self, use_sharded_checkpoint: bool = False):
        """
        Initialize checkpoint manager.

        Args:
            use_sharded_checkpoint: Use sharded checkpoints (more memory efficient)
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is not available.")

        self.use_sharded_checkpoint = use_sharded_checkpoint

    def save_checkpoint(
        self,
        fsdp_model: "FSDP",
        optimizer: Optional["torch.optim.Optimizer"] = None,
        checkpoint_path: str | Path = "checkpoint.pt",
        epoch: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
        rank: int = 0,
    ):
        """
        Save FSDP model checkpoint.

        Args:
            fsdp_model: FSDP-wrapped model
            optimizer: Optimizer (optional)
            checkpoint_path: Path to save checkpoint
            epoch: Training epoch number
            metadata: Additional metadata to save
            rank: Process rank (only rank 0 saves in full state dict mode)
        """
        checkpoint_path = Path(checkpoint_path)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        if self.use_sharded_checkpoint:
            # Save sharded checkpoint (each rank saves its shard)
            self._save_sharded_checkpoint(fsdp_model, optimizer, checkpoint_path, epoch, metadata)
        else:
            # Save full state dict (only rank 0)
            if rank == 0:
                self._save_full_checkpoint(fsdp_model, optimizer, checkpoint_path, epoch, metadata)

    def _save_full_checkpoint(
        self,
        fsdp_model: "FSDP",
        optimizer: Optional["torch.optim.Optimizer"],
        checkpoint_path: Path,
        epoch: Optional[int],
        metadata: Optional[dict[str, Any]],
    ):
        """Save full consolidated checkpoint."""
        with FSDP.state_dict_type(
            fsdp_model,
            StateDictType.FULL_STATE_DICT,
            FullStateDictConfig(offload_to_cpu=True, rank0_only=True),
        ):
            state_dict = fsdp_model.state_dict()

        checkpoint = {
            "model": state_dict,
            "epoch": epoch,
            "metadata": metadata or {},
        }

        if optimizer is not None:
            with FSDP.state_dict_type(
                fsdp_model,
                StateDictType.FULL_STATE_DICT,
                FullStateDictConfig(offload_to_cpu=True, rank0_only=True),
            ):
                checkpoint["optimizer"] = optimizer.state_dict()

        torch.save(checkpoint, checkpoint_path)

    def _save_sharded_checkpoint(
        self,
        fsdp_model: "FSDP",
        optimizer: Optional["torch.optim.Optimizer"],
        checkpoint_path: Path,
        epoch: Optional[int],
        metadata: Optional[dict[str, Any]],
    ):
        """Save sharded checkpoint (each rank saves its shard)."""
        with FSDP.state_dict_type(
            fsdp_model,
            StateDictType.SHARDED_STATE_DICT,
            ShardedStateDictConfig(),
        ):
            state_dict = fsdp_model.state_dict()

        # Each rank saves its shard
        rank = torch.distributed.get_rank()
        shard_path = checkpoint_path.parent / f"{checkpoint_path.stem}_rank{rank}.pt"

        checkpoint = {
            "model": state_dict,
            "epoch": epoch,
            "rank": rank,
            "metadata": metadata or {},
        }

        if optimizer is not None:
            checkpoint["optimizer"] = optimizer.state_dict()

        torch.save(checkpoint, shard_path)

    def load_checkpoint(
        self,
        checkpoint_path: str | Path,
        fsdp_model: "FSDP",
        optimizer: Optional["torch.optim.Optimizer"] = None,
        rank: int = 0,
    ) -> tuple:
        """
        Load FSDP model checkpoint.

        Args:
            checkpoint_path: Path to checkpoint
            fsdp_model: FSDP-wrapped model
            optimizer: Optimizer (optional)
            rank: Process rank

        Returns:
            tuple of (fsdp_model, optimizer, epoch, metadata)
        """
        checkpoint_path = Path(checkpoint_path)

        if self.use_sharded_checkpoint:
            return self._load_sharded_checkpoint(checkpoint_path, fsdp_model, optimizer, rank)
        return self._load_full_checkpoint(checkpoint_path, fsdp_model, optimizer)

    def _load_full_checkpoint(
        self,
        checkpoint_path: Path,
        fsdp_model: "FSDP",
        optimizer: Optional["torch.optim.Optimizer"],
    ) -> tuple:
        """Load full consolidated checkpoint.

        Security note: Checkpoint files should only be loaded from trusted sources.
        """
        checkpoint = torch.load(
            checkpoint_path, map_location="cpu", weights_only=False
        )  # nosec B614 - Checkpoint contains optimizer state

        with FSDP.state_dict_type(
            fsdp_model,
            StateDictType.FULL_STATE_DICT,
            FullStateDictConfig(offload_to_cpu=True, rank0_only=True),
        ):
            fsdp_model.load_state_dict(checkpoint["model"])

        if optimizer is not None and "optimizer" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer"])

        return (
            fsdp_model,
            optimizer,
            checkpoint.get("epoch"),
            checkpoint.get("metadata", {}),
        )

    def _load_sharded_checkpoint(
        self,
        checkpoint_path: Path,
        fsdp_model: "FSDP",
        optimizer: Optional["torch.optim.Optimizer"],
        rank: int,
    ) -> tuple:
        """Load sharded checkpoint (each rank loads its shard).

        Security note: Checkpoint files should only be loaded from trusted sources.
        """
        shard_path = checkpoint_path.parent / f"{checkpoint_path.stem}_rank{rank}.pt"
        checkpoint = torch.load(
            shard_path, map_location="cpu", weights_only=False
        )  # nosec B614 - Checkpoint contains optimizer state

        with FSDP.state_dict_type(
            fsdp_model,
            StateDictType.SHARDED_STATE_DICT,
            ShardedStateDictConfig(),
        ):
            fsdp_model.load_state_dict(checkpoint["model"])

        if optimizer is not None and "optimizer" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer"])

        return (
            fsdp_model,
            optimizer,
            checkpoint.get("epoch"),
            checkpoint.get("metadata", {}),
        )


# Convenience function for quick FSDP setup
def wrap_model_with_fsdp(
    model: "nn.Module",
    sharding_strategy: str = "FULL_SHARD",
    mixed_precision: str = "fp16",
    use_cpu_offload: bool = False,
    activation_checkpointing: bool = False,
    transformer_layer_cls: Optional[list[type]] = None,
) -> "FSDP":
    """
    Convenience function to wrap model with FSDP.

    Args:
        model: PyTorch model
        sharding_strategy: Sharding strategy
        mixed_precision: Mixed precision mode
        use_cpu_offload: Enable CPU offloading
        activation_checkpointing: Enable activation checkpointing
        transformer_layer_cls: Transformer layer classes for auto-wrapping

    Returns:
        FSDP-wrapped model

    Example:
        >>> from transformers import AutoModelForCausalLM
        >>> model = AutoModelForCausalLM.from_pretrained("gpt2")
        >>> fsdp_model = wrap_model_with_fsdp(
        ...     model,
        ...     sharding_strategy="FULL_SHARD",
        ...     mixed_precision="bf16",
        ...     activation_checkpointing=True,
        ... )
    """
    config = FSDPConfig(
        sharding_strategy=sharding_strategy,
        mixed_precision=mixed_precision,
        use_cpu_offload=use_cpu_offload,
        activation_checkpointing=activation_checkpointing,
    )

    trainer = FSDPTrainer(model, config)
    return trainer.wrap_model(transformer_layer_cls=transformer_layer_cls)
