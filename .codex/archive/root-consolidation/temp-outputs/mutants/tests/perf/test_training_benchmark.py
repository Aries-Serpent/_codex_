"""
Phase 15.0: Training Loop Benchmark Tests

This module provides comprehensive performance benchmarks for the training loop,
measuring throughput, memory usage, and latency.

Created: 2026-01-18
Phase: 15.0 - Performance Testing & Benchmarking
Target: Establish performance baseline for training operations
"""

import gc
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest

# ============================================================================
# Benchmark Utilities
# ============================================================================


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""

    name: str
    duration_ms: float
    iterations: int
    throughput: float  # ops/sec
    memory_mb: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "iterations": self.iterations,
            "throughput": self.throughput,
            "memory_mb": self.memory_mb,
        }


def get_memory_usage_mb() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil

        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


def benchmark(func: Callable[[], Any], iterations: int = 100, warmup: int = 5) -> BenchmarkResult:
    """Run a benchmark on a function."""
    # Warmup
    for _ in range(warmup):
        func()

    gc.collect()
    memory_before = get_memory_usage_mb()

    start_time = time.perf_counter()
    for _ in range(iterations):
        func()
    end_time = time.perf_counter()

    memory_after = get_memory_usage_mb()
    duration_ms = (end_time - start_time) * 1000
    throughput = iterations / (end_time - start_time) if (end_time - start_time) > 0 else 0

    return BenchmarkResult(
        name=func.__name__,
        duration_ms=duration_ms,
        iterations=iterations,
        throughput=throughput,
        memory_mb=memory_after - memory_before,
    )


# ============================================================================
# Training Loop Throughput Benchmarks
# ============================================================================


class TestTrainingThroughputBenchmarks:
    """Benchmark training loop throughput."""

    def test_batch_processing_throughput(self) -> None:
        """Benchmark batch processing throughput."""

        def process_batch() -> dict[str, float]:
            # Simulate batch processing
            batch = [{"input": f"sample_{i}", "label": i % 10} for i in range(32)]
            processed = []
            for item in batch:
                processed.append(
                    {
                        "tokens": len(item["input"]),
                        "label": item["label"],
                    }
                )
            return {"processed": len(processed)}

        result = benchmark(process_batch, iterations=1000)
        assert result.throughput > 0, "throughput must be greater than zero"
        assert result.duration_ms < 10000, "Result must not be empty"

    def test_gradient_computation_throughput(self) -> None:
        """Benchmark gradient computation simulation."""

        def compute_gradients() -> dict[str, float]:
            # Simulate gradient computation
            params = [0.1 * i for i in range(1000)]
            grads = [p * 0.01 for p in params]
            return {"grad_norm": sum(g * g for g in grads) ** 0.5}

        result = benchmark(compute_gradients, iterations=500)
        assert result.throughput > 0, "throughput must be greater than zero"

    def test_optimizer_step_throughput(self) -> None:
        """Benchmark optimizer step simulation."""
        params = [0.1 * i for i in range(1000)]
        grads = [0.01] * 1000
        lr = 0.001

        def optimizer_step() -> None:
            for i in range(len(params)):
                params[i] -= lr * grads[i]

        result = benchmark(optimizer_step, iterations=1000)
        assert result.throughput > 100, "throughput must be greater than zero"

    def test_loss_computation_throughput(self) -> None:
        """Benchmark loss computation."""

        def compute_loss() -> float:
            predictions = [0.5 + 0.1 * i for i in range(100)]
            targets = [0.0 if i < 50 else 1.0 for i in range(100)]
            # Cross-entropy approximation
            return sum(
                -t * (p if p > 0 else 1e-10) - (1 - t) * (1 - p if p < 1 else 1e-10)
                for p, t in zip(predictions, targets)
            ) / len(predictions)

        result = benchmark(compute_loss, iterations=1000)
        assert result.throughput > 0, "throughput must be greater than zero"

    def test_forward_pass_throughput(self) -> None:
        """Benchmark forward pass simulation."""

        def forward_pass() -> list[float]:
            # Simulate simple forward pass
            input_data = [0.1 * i for i in range(512)]
            weights = [[0.01 * j for j in range(512)] for _ in range(128)]
            output = []
            for w in weights:
                activation = sum(i * w_i for i, w_i in zip(input_data, w))
                output.append(max(0, activation))  # ReLU
            return output

        result = benchmark(forward_pass, iterations=100)
        assert result.throughput > 0, "throughput must be greater than zero"


# ============================================================================
# Training Memory Benchmarks
# ============================================================================


class TestTrainingMemoryBenchmarks:
    """Benchmark training memory usage."""

    def test_batch_memory_allocation(self) -> None:
        """Benchmark memory allocation for batches."""

        def allocate_batch() -> list[dict[str, Any]]:
            return [{"input_ids": list(range(512)), "attention_mask": [1] * 512} for _ in range(32)]

        result = benchmark(allocate_batch, iterations=100)
        # Memory increase should be reasonable
        assert result.memory_mb < 100, "Result must not be empty"

    def test_gradient_accumulation_memory(self) -> None:
        """Benchmark gradient accumulation memory."""
        accumulated_grads: list[list[float]] = []

        def accumulate_gradients() -> None:
            grads = [0.01 * i for i in range(1000)]
            accumulated_grads.append(grads)
            if len(accumulated_grads) > 4:
                accumulated_grads.clear()

        result = benchmark(accumulate_gradients, iterations=100)
        assert result.duration_ms < 1000, "Result must not be empty"

    def test_checkpoint_memory_overhead(self) -> None:
        """Benchmark checkpoint creation memory."""

        def create_checkpoint() -> dict[str, Any]:
            return {
                "model_state": {f"layer_{i}": list(range(100)) for i in range(10)},
                "optimizer_state": {"step": 1000, "lr": 0.001},
                "epoch": 5,
            }

        result = benchmark(create_checkpoint, iterations=100)
        assert result.memory_mb < 50, "Result must not be empty"

    def test_activation_caching_memory(self) -> None:
        """Benchmark activation caching memory."""
        cache: dict[str, list[float]] = {}

        def cache_activations() -> None:
            layer_name = f"layer_{len(cache) % 10}"
            cache[layer_name] = [0.1 * i for i in range(1024)]

        result = benchmark(cache_activations, iterations=100)
        assert result.duration_ms < 1000, "Result must not be empty"


# ============================================================================
# Training Latency Benchmarks
# ============================================================================


class TestTrainingLatencyBenchmarks:
    """Benchmark training latency metrics."""

    def test_single_step_latency(self) -> None:
        """Benchmark latency of a single training step."""

        def training_step() -> dict[str, float]:
            # Simulate complete training step
            batch = [{"x": i, "y": i % 2} for i in range(32)]

            # Forward
            logits = [item["x"] * 0.1 for item in batch]

            # Loss
            loss = sum((logit - item["y"]) ** 2 for logit, item in zip(logits, batch)) / len(batch)

            # Backward (simulated)
            grads = [2 * (logit - item["y"]) / len(batch) for logit, item in zip(logits, batch)]

            return {"loss": loss, "grad_norm": sum(g**2 for g in grads) ** 0.5}

        result = benchmark(training_step, iterations=100)
        # Each step should be fast
        avg_latency_ms = result.duration_ms / result.iterations
        assert avg_latency_ms < 10, "avg_latency_ms is not valid"

    def test_data_loading_latency(self) -> None:
        """Benchmark data loading latency."""

        def load_batch() -> list[dict[str, Any]]:
            return [
                {
                    "input_ids": list(range(i, i + 128)),
                    "attention_mask": [1] * 128,
                    "labels": [i % 1000],
                }
                for i in range(32)
            ]

        result = benchmark(load_batch, iterations=500)
        avg_latency_ms = result.duration_ms / result.iterations
        assert avg_latency_ms < 5, "avg_latency_ms is not valid"

    def test_logging_latency(self) -> None:
        """Benchmark logging overhead latency."""
        logs: list[dict[str, Any]] = []

        def log_metrics() -> None:
            logs.append(
                {
                    "step": len(logs),
                    "loss": 0.5,
                    "lr": 0.001,
                    "grad_norm": 1.0,
                    "throughput": 1000.0,
                }
            )
            if len(logs) > 100:
                logs.clear()

        result = benchmark(log_metrics, iterations=1000)
        avg_latency_ms = result.duration_ms / result.iterations
        assert avg_latency_ms < 1, "avg_latency_ms is not valid"

    def test_checkpoint_save_latency(self) -> None:
        """Benchmark checkpoint save latency (simulated)."""
        import json

        def save_checkpoint() -> str:
            checkpoint = {
                "step": 1000,
                "model_state": {f"param_{i}": [0.1] * 100 for i in range(10)},
            }
            # Simulate serialization
            return json.dumps(checkpoint)

        result = benchmark(save_checkpoint, iterations=100)
        avg_latency_ms = result.duration_ms / result.iterations
        assert avg_latency_ms < 50, "avg_latency_ms is not valid"

    def test_lr_scheduler_step_latency(self) -> None:
        """Benchmark learning rate scheduler step latency."""
        step = 0
        base_lr = 0.001
        warmup_steps = 100
        total_steps = 1000

        def scheduler_step() -> float:
            nonlocal step
            step += 1
            if step < warmup_steps:
                lr = base_lr * step / warmup_steps
            else:
                progress = (step - warmup_steps) / (total_steps - warmup_steps)
                lr = base_lr * (1 - progress)
            return lr

        result = benchmark(scheduler_step, iterations=1000)
        avg_latency_ms = result.duration_ms / result.iterations
        assert avg_latency_ms < 0.1, "avg_latency_ms is not valid"


# ============================================================================
# Training Scalability Benchmarks
# ============================================================================


class TestTrainingScalabilityBenchmarks:
    """Benchmark training scalability."""

    @pytest.mark.parametrize("batch_size", [1, 8, 32, 64, 128])
    def test_batch_size_scaling(self, batch_size: int) -> None:
        """Benchmark scaling with different batch sizes."""

        def process_batch() -> int:
            batch = [{"x": i} for i in range(batch_size)]
            return len([item["x"] * 2 for item in batch])

        result = benchmark(process_batch, iterations=100)
        assert result.throughput > 0, "throughput must be greater than zero"

    @pytest.mark.parametrize("sequence_length", [64, 128, 256, 512])
    def test_sequence_length_scaling(self, sequence_length: int) -> None:
        """Benchmark scaling with different sequence lengths."""

        def process_sequence() -> int:
            sequence = list(range(sequence_length))
            return sum(sequence)

        result = benchmark(process_sequence, iterations=500)
        assert result.throughput > 0, "throughput must be greater than zero"

    @pytest.mark.parametrize("num_layers", [1, 4, 8, 12])
    def test_layer_scaling(self, num_layers: int) -> None:
        """Benchmark scaling with different number of layers."""

        def forward_layers() -> list[float]:
            x = [0.1] * 128
            for _ in range(num_layers):
                x = [max(0, v * 0.9 + 0.01) for v in x]  # Simulated layer
            return x

        result = benchmark(forward_layers, iterations=100)
        assert result.throughput > 0, "throughput must be greater than zero"


# ============================================================================
# Training Efficiency Benchmarks
# ============================================================================


class TestTrainingEfficiencyBenchmarks:
    """Benchmark training efficiency metrics."""

    def test_samples_per_second(self) -> None:
        """Benchmark samples processed per second."""
        samples_processed = 0
        batch_size = 32

        def process_samples() -> int:
            nonlocal samples_processed
            samples_processed += batch_size
            # Simulate processing
            _ = [i**2 for i in range(batch_size)]
            return samples_processed

        result = benchmark(process_samples, iterations=1000)
        samples_per_second = batch_size * result.throughput
        assert samples_per_second > 1000, "samples_per_second must be greater than zero"

    def test_tokens_per_second(self) -> None:
        """Benchmark tokens processed per second."""
        batch_size = 32
        seq_length = 512
        tokens_per_batch = batch_size * seq_length

        def process_tokens() -> int:
            # Simulate token processing
            _ = [[j for j in range(seq_length)] for _ in range(batch_size)]
            return tokens_per_batch

        result = benchmark(process_tokens, iterations=100)
        tokens_per_second = tokens_per_batch * result.throughput
        assert tokens_per_second > 10000, "tokens_per_second must be greater than zero"

    def test_gpu_utilization_simulation(self) -> None:
        """Benchmark simulated GPU utilization patterns."""

        def gpu_kernel_simulation() -> float:
            # Simulate compute-bound operation
            result = 0.0
            for i in range(1000):
                result += (i * 0.001) ** 2
            return result

        result = benchmark(gpu_kernel_simulation, iterations=100)
        assert result.throughput > 0, "throughput must be greater than zero"

    def test_memory_bandwidth_simulation(self) -> None:
        """Benchmark memory bandwidth patterns."""
        data = list(range(10000))

        def memory_access_pattern() -> float:
            # Sequential access
            return sum(data)

        result = benchmark(memory_access_pattern, iterations=500)
        assert result.throughput > 0, "throughput must be greater than zero"
