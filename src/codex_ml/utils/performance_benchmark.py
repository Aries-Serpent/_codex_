"""Performance benchmarking suite for ML training.
from codex.logging.adapter import LoggerAdapter, NullLogger, get_default_logger

Provides comprehensive performance profiling and benchmarking tools
for training pipelines, model inference, and data loading.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import torch

from aries_serpent_core.logging.adapter import get_default_logger

logger = logging.getLogger(__name__)

__all__ = [
    "BenchmarkResult",
    "PerformanceBenchmark",
    "benchmark_data_loading",
    "benchmark_inference",
    "benchmark_training_step",
]


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark.

    Attributes:
        name: Benchmark name
        duration_ms: Total duration in milliseconds
        throughput: Items per second (if applicable)
        memory_mb: Peak memory usage in MB
        gpu_memory_mb: Peak GPU memory in MB (if available)
        metadata: Additional metadata
    """

    name: str
    duration_ms: float
    throughput: Optional[float] = None
    memory_mb: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        parts = [
            f"{self.name}:",
            f"  Duration: {self.duration_ms:.2f}ms",
        ]
        if self.throughput:
            parts.append(f"  Throughput: {self.throughput:.2f} items/sec")
        if self.memory_mb:
            parts.append(f"  Memory: {self.memory_mb:.2f}MB")
        if self.gpu_memory_mb:
            parts.append(f"  GPU Memory: {self.gpu_memory_mb:.2f}MB")
        return "\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "throughput": self.throughput,
            "memory_mb": self.memory_mb,
            "gpu_memory_mb": self.gpu_memory_mb,
            "metadata": self.metadata,
        }


class PerformanceBenchmark:
    """Performance benchmarking context manager.

    Example:
        >>> benchmark = PerformanceBenchmark("training_step")
        >>> with benchmark:
        ...     # Training code here
        ...     pass
        >>> get_default_logger().info(benchmark.result)
    """

    def __init__(self, name: str, warmup_iters: int = 0):
        """Initialize benchmark.

        Args:
            name: Benchmark name
            warmup_iters: Number of warmup iterations before timing
        """
        self.name = name
        self.warmup_iters = warmup_iters
        self.result: Optional[BenchmarkResult] = None
        self._start_time = 0.0
        self._start_memory = 0.0
        self._start_gpu_memory = 0.0

    def __enter__(self):
        """Start benchmark."""
        # Record initial memory
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            self._start_gpu_memory = torch.cuda.memory_allocated() / 1024**2

        # Start timing
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End benchmark and record results."""
        # End timing
        duration_s = time.perf_counter() - self._start_time
        duration_ms = duration_s * 1000

        # Record peak memory
        gpu_memory_mb = None
        if torch.cuda.is_available():
            gpu_memory_mb = torch.cuda.max_memory_allocated() / 1024**2

        self.result = BenchmarkResult(
            name=self.name,
            duration_ms=duration_ms,
            gpu_memory_mb=gpu_memory_mb,
        )

        get_default_logger().info(f"Benchmark '{self.name}': {duration_ms:.2f}ms")

        return False


def benchmark_training_step(
    model: torch.nn.Module,
    batch: dict[str, torch.Tensor],
    optimizer: torch.optim.Optimizer,
    num_iterations: int = 10,
    warmup_iters: int = 2,
) -> BenchmarkResult:
    """Benchmark a training step.

    Args:
        model: PyTorch model
        batch: Input batch
        optimizer: Optimizer
        num_iterations: Number of iterations to run
        warmup_iters: Warmup iterations

    Returns:
        BenchmarkResult with timing and throughput
    """
    model.train()

    def _get_loss(outputs):
        """Extract loss from model outputs (handles dict, tuple, or object with .loss)."""
        if hasattr(outputs, "loss"):
            return outputs.loss
        if isinstance(outputs, dict) and "loss" in outputs:
            return outputs["loss"]
        if isinstance(outputs, (tuple, list)) and len(outputs) > 0:
            return outputs[0]
        raise ValueError(f"Cannot extract loss from outputs: {type(outputs)}")

    # Warmup
    for _ in range(warmup_iters):
        optimizer.zero_grad()
        outputs = model(**batch)
        loss = _get_loss(outputs)
        loss.backward()
        optimizer.step()

    # Benchmark
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

    start_time = time.perf_counter()

    for _ in range(num_iterations):
        optimizer.zero_grad()
        outputs = model(**batch)
        loss = _get_loss(outputs)
        loss.backward()
        optimizer.step()

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    duration_s = time.perf_counter() - start_time
    duration_ms = duration_s * 1000
    throughput = num_iterations / duration_s

    gpu_memory_mb = None
    if torch.cuda.is_available():
        gpu_memory_mb = torch.cuda.max_memory_allocated() / 1024**2

    batch_size = next(iter(batch.values())).shape[0]

    return BenchmarkResult(
        name="training_step",
        duration_ms=duration_ms,
        throughput=throughput,
        gpu_memory_mb=gpu_memory_mb,
        metadata={
            "num_iterations": num_iterations,
            "batch_size": batch_size,
            "avg_ms_per_step": duration_ms / num_iterations,
        },
    )


def benchmark_inference(
    model: torch.nn.Module,
    batch: dict[str, torch.Tensor],
    num_iterations: int = 100,
    warmup_iters: int = 10,
) -> BenchmarkResult:
    """Benchmark model inference.

    Args:
        model: PyTorch model
        batch: Input batch
        num_iterations: Number of iterations
        warmup_iters: Warmup iterations

    Returns:
        BenchmarkResult with timing and throughput
    """
    model.eval()

    # Warmup
    with torch.no_grad():
        for _ in range(warmup_iters):
            _ = model(**batch)

    # Benchmark
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

    start_time = time.perf_counter()

    with torch.no_grad():
        for _ in range(num_iterations):
            _ = model(**batch)

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    duration_s = time.perf_counter() - start_time
    duration_ms = duration_s * 1000
    throughput = num_iterations / duration_s

    gpu_memory_mb = None
    if torch.cuda.is_available():
        gpu_memory_mb = torch.cuda.max_memory_allocated() / 1024**2

    batch_size = next(iter(batch.values())).shape[0]

    return BenchmarkResult(
        name="inference",
        duration_ms=duration_ms,
        throughput=throughput,
        gpu_memory_mb=gpu_memory_mb,
        metadata={
            "num_iterations": num_iterations,
            "batch_size": batch_size,
            "avg_ms_per_sample": duration_ms / (num_iterations * batch_size),
        },
    )


def benchmark_data_loading(
    dataloader,
    num_batches: int = 100,
) -> BenchmarkResult:
    """Benchmark data loading speed.

    Args:
        dataloader: PyTorch DataLoader
        num_batches: Number of batches to load

    Returns:
        BenchmarkResult with timing and throughput
    """
    start_time = time.perf_counter()

    count = 0
    for _ in dataloader:
        count += 1
        if count >= num_batches:
            break

    duration_s = time.perf_counter() - start_time
    duration_ms = duration_s * 1000
    throughput = count / duration_s

    return BenchmarkResult(
        name="data_loading",
        duration_ms=duration_ms,
        throughput=throughput,
        metadata={
            "num_batches": count,
            "avg_ms_per_batch": duration_ms / count,
        },
    )


class BenchmarkSuite:
    """Suite of benchmarks for comprehensive performance testing.

    Example:
        >>> suite = BenchmarkSuite("training_pipeline")
        >>> suite.add_result(benchmark_training_step(model, batch, optimizer))
        >>> suite.add_result(benchmark_inference(model, batch))
        >>> suite.save_results("benchmarks.json")
        >>> suite.print_summary()
    """

    def __init__(self, name: str):
        """Initialize benchmark suite.

        Args:
            name: Suite name
        """
        self.name = name
        self.results: list[BenchmarkResult] = []

    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result.

        Args:
            result: BenchmarkResult to add
        """
        self.results.append(result)
        get_default_logger().info(f"Added benchmark: {result.name}")

    def print_summary(self):
        """Print summary of all benchmarks."""
        get_default_logger().info(f"\n{'=' * 60}")
        get_default_logger().info(f"Benchmark Suite: {self.name}")
        get_default_logger().info(f"{'=' * 60}")

        for result in self.results:
            get_default_logger().info(f"\n{result}")

        get_default_logger().info(f"\n{'=' * 60}")
        get_default_logger().info(f"Total benchmarks: {len(self.results)}")
        get_default_logger().info(f"{'=' * 60}\n")

    def save_results(self, path: str):
        """Save results to JSON file.

        Args:
            path: Output file path
        """
        import json

        output = {
            "suite_name": self.name,
            "results": [r.to_dict() for r in self.results],
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(output, f, indent=2)

        get_default_logger().info(f"Saved benchmark results to: {path}")
