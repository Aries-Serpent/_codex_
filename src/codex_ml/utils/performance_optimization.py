"""Advanced performance optimization utilities.
from codex.logging.adapter import LoggerAdapter, NullLogger, get_default_logger

Provides tools for:
- Profiling with PyTorch Profiler
- Memory optimization
- Gradient checkpointing
- Mixed precision optimization
- Kernel fusion hints
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn

from aries_serpent_core.logging.adapter import get_default_logger

logger = logging.getLogger(__name__)

__all__ = [
    "MemoryOptimizer",
    "TorchProfiler",
    "enable_gradient_checkpointing",
    "optimize_model",
    "profile_model",
]


class TorchProfiler:
    """PyTorch Profiler wrapper with enhanced features.

    Example:
        >>> profiler = TorchProfiler("training_profile")
        >>> with profiler:
        ...     # Training code
        ...     pass
        >>> profiler.export_chrome_trace("profile.json")
    """

    def __init__(
        self,
        name: str = "profile",
        activities: Optional[list] = None,
        record_shapes: bool = True,
        profile_memory: bool = True,
        with_stack: bool = False,
    ):
        """Initialize profiler.

        Args:
            name: Profile name
            activities: List of activities to profile
            record_shapes: Whether to record tensor shapes
            profile_memory: Whether to profile memory
            with_stack: Whether to record stack traces
        """
        self.name = name

        if activities is None and torch.cuda.is_available():
            activities = [
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA,
            ]
        elif activities is None:
            activities = [torch.profiler.ProfilerActivity.CPU]

        self.profiler = torch.profiler.profile(
            activities=activities,
            record_shapes=record_shapes,
            profile_memory=profile_memory,
            with_stack=with_stack,
        )

    def __enter__(self):
        """Start profiling."""
        self.profiler.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop profiling."""
        self.profiler.__exit__(exc_type, exc_val, exc_tb)

        # Print summary
        print(
            self.profiler.key_averages().table(
                sort_by="cuda_time_total" if torch.cuda.is_available() else "cpu_time_total",
                row_limit=10,
            )
        )

    def export_chrome_trace(self, path: str):
        """Export Chrome trace for visualization.

        Args:
            path: Output path for trace file
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.profiler.export_chrome_trace(path)
        get_default_logger().info(f"Chrome trace exported to: {path}")

    def export_stacks(self, path: str):
        """Export stack traces.

        Args:
            path: Output path for stacks file
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.profiler.export_stacks(path, "self_cuda_time_total")
        get_default_logger().info(f"Stack traces exported to: {path}")


class MemoryOptimizer:
    """Memory optimization utilities.

    Example:
        >>> optimizer = MemoryOptimizer()
        >>> optimizer.optimize_model(model)
        >>> optimizer.print_memory_summary()
    """

    @staticmethod
    def optimize_model(model: nn.Module, aggressive: bool = False):
        """Apply memory optimizations to model.

        Args:
            model: PyTorch model
            aggressive: Whether to apply aggressive optimizations
        """
        # Enable gradient checkpointing for compatible modules
        for module in model.modules():
            if hasattr(module, "gradient_checkpointing_enable"):
                module.gradient_checkpointing_enable()
                get_default_logger().info(
                    f"Enabled gradient checkpointing for {type(module).__name__}"
                )

        # Set model to channels_last memory format (if compatible)
        if aggressive and torch.cuda.is_available():
            try:
                model = model.to(memory_format=torch.channels_last)
                get_default_logger().info("Converted model to channels_last memory format")
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                get_default_logger().debug("Exception: <ERROR_TYPE>")
                get_default_logger().debug("Could not convert to channels_last: <ERROR_TYPE>")

        # Enable TF32 for faster matmul on Ampere GPUs
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            get_default_logger().info("Enabled TF32 for faster computation")

        return model

    @staticmethod
    def print_memory_summary():
        """Print CUDA memory summary."""
        if torch.cuda.is_available():
            get_default_logger().info(torch.cuda.memory_summary())

    @staticmethod
    def clear_cache():
        """Clear CUDA cache."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            get_default_logger().info("Cleared CUDA cache")

    @staticmethod
    def set_memory_fraction(fraction: float, device: int = 0):
        """Set maximum memory fraction for CUDA device.

        Args:
            fraction: Fraction of memory to use (0.0 to 1.0)
            device: CUDA device index
        """
        if torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(fraction, device)
            get_default_logger().info(f"Set memory fraction to {fraction} for device {device}")


def enable_gradient_checkpointing(model: nn.Module) -> nn.Module:
    """Enable gradient checkpointing for model.

    Trades compute for memory by recomputing activations during backward pass.

    Args:
        model: PyTorch model

    Returns:
        Model with gradient checkpointing enabled

    Example:
        >>> model = MyModel()
        >>> model = enable_gradient_checkpointing(model)
    """
    for module in model.modules():
        if hasattr(module, "gradient_checkpointing_enable"):
            module.gradient_checkpointing_enable()

    get_default_logger().info("Gradient checkpointing enabled")
    return model


def optimize_model(
    model: nn.Module,
    compile: bool = True,
    channels_last: bool = True,
    gradient_checkpointing: bool = False,
) -> nn.Module:
    """Apply comprehensive optimizations to model.

    Args:
        model: PyTorch model
        compile: Whether to compile with torch.compile (PyTorch 2.0+)
        channels_last: Whether to use channels_last memory format
        gradient_checkpointing: Whether to enable gradient checkpointing

    Returns:
        Optimized model

    Example:
        >>> model = MyModel()
        >>> model = optimize_model(model, compile=True)
    """
    # Enable gradient checkpointing
    if gradient_checkpointing:
        model = enable_gradient_checkpointing(model)

    # Convert to channels_last
    if channels_last and torch.cuda.is_available():
        try:
            model = model.to(memory_format=torch.channels_last)
            get_default_logger().info("Converted to channels_last memory format")
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            get_default_logger().debug("Exception: <ERROR_TYPE>")
            get_default_logger().debug("Could not convert to channels_last: <ERROR_TYPE>")

    # Compile with torch.compile (PyTorch 2.0+)
    if compile and hasattr(torch, "compile"):
        try:
            model = torch.compile(model)
            get_default_logger().info("Model compiled with torch.compile")
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            get_default_logger().debug("Exception: <ERROR_TYPE>")
            get_default_logger().warning("Could not compile model: <ERROR_TYPE>")

    # Enable performance optimizations
    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        get_default_logger().info("Enabled CUDA performance optimizations")

    return model


@contextmanager
def profile_model(
    name: str = "model_profile",
    export_chrome: bool = True,
    export_path: Optional[str] = None,
):
    """Context manager for profiling model operations.

    Args:
        name: Profile name
        export_chrome: Whether to export Chrome trace
        export_path: Path for exports (default: ./profiling/{name})

    Example:
        >>> with profile_model("forward_pass"):
        ...     output = model(input)
    """
    if export_path is None:
        export_path = f"./profiling/{name}"

    Path(export_path).mkdir(parents=True, exist_ok=True)

    profiler = TorchProfiler(name)

    with profiler:
        yield profiler

    if export_chrome:
        profiler.export_chrome_trace(f"{export_path}/trace.json")


class AsyncDataPrefetcher:
    """Asynchronous data prefetcher for faster data loading.

    Prefetches next batch to GPU while current batch is processing.

    Example:
        >>> prefetcher = AsyncDataPrefetcher(dataloader, device="cuda")
        >>> for batch in prefetcher:
        ...     # Process batch
        ...     pass
    """

    def __init__(self, dataloader, device: str = "cuda"):
        """Initialize prefetcher.

        Args:
            dataloader: PyTorch DataLoader
            device: Target device for prefetching
        """
        self.dataloader = dataloader
        self.device = torch.device(device)
        self.stream = torch.cuda.Stream() if device.startswith("cuda") else None

    def __iter__(self):
        """Iterate with prefetching."""
        loader_iter = iter(self.dataloader)

        # Prefetch first batch
        try:
            batch = next(loader_iter)
            if self.stream is not None:
                with torch.cuda.stream(self.stream):
                    batch = self._to_device(batch)
        except StopIteration:
            return

        # Main loop with prefetching
        for next_batch in loader_iter:
            # Wait for prefetch
            if self.stream is not None:
                torch.cuda.current_stream().wait_stream(self.stream)

            yield batch

            # Prefetch next batch
            if self.stream is not None:
                with torch.cuda.stream(self.stream):
                    batch = self._to_device(next_batch)
            else:
                batch = self._to_device(next_batch)

        # Yield last batch
        if self.stream is not None:
            torch.cuda.current_stream().wait_stream(self.stream)
        yield batch

    def _to_device(self, batch):
        """Move batch to device."""
        if isinstance(batch, torch.Tensor):
            return batch.to(self.device, non_blocking=True)
        if isinstance(batch, dict):
            return {k: self._to_device(v) for k, v in batch.items()}
        if isinstance(batch, (list, tuple)):
            return type(batch)(self._to_device(item) for item in batch)
        return batch
