"""
Comprehensive ML Model Performance Benchmarking Suite.

This module provides benchmarking tools for key ML operations:
- Model initialization
- Forward passes
- Backward passes (training steps)
- Inference throughput
- Memory usage
- Checkpoint save/load operations

All benchmarks are run multiple times to establish statistical baselines.
"""

from __future__ import annotations

import json
import logging
import os
import statistics
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

# Ensure we can import the local codex_ml module
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import torch
    import torch.nn as nn
    from torch.optim import Adam
except ImportError:
    print("ERROR: PyTorch not installed")
    sys.exit(1)

from src.codex_ml.models.minilm import MiniLM, MiniLMConfig
from src.codex_ml.models.decoder_only import DecoderOnlyLM, ModelConfig

logger = logging.getLogger(__name__)

__all__ = [
    "BenchmarkResult",
    "PerformanceAnalysis",
    "ModelBenchmarkSuite",
    "run_ml_benchmarks",
]


@dataclass
class BenchmarkResult:
    """Single benchmark run result."""

    name: str
    duration_ms: float
    throughput: Optional[float] = None
    memory_peak_mb: Optional[float] = None
    gpu_memory_peak_mb: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "throughput": self.throughput,
            "memory_peak_mb": self.memory_peak_mb,
            "gpu_memory_peak_mb": self.gpu_memory_peak_mb,
            "metadata": self.metadata,
        }


@dataclass
class PerformanceAnalysis:
    """Statistical analysis of multiple benchmark runs."""

    name: str
    runs: list[float] = field(default_factory=list)
    unit: str = "ms"

    @property
    def mean(self) -> float:
        return statistics.mean(self.runs) if self.runs else 0.0

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.runs) if len(self.runs) > 1 else 0.0

    @property
    def min(self) -> float:
        return min(self.runs) if self.runs else 0.0

    @property
    def max(self) -> float:
        return max(self.runs) if self.runs else 0.0

    @property
    def p50(self) -> float:
        if not self.runs:
            return 0.0
        sorted_runs = sorted(self.runs)
        return sorted_runs[int(0.50 * len(sorted_runs))]

    @property
    def p95(self) -> float:
        if not self.runs:
            return 0.0
        sorted_runs = sorted(self.runs)
        return sorted_runs[int(0.95 * len(sorted_runs))]

    @property
    def p99(self) -> float:
        if not self.runs:
            return 0.0
        sorted_runs = sorted(self.runs)
        return sorted_runs[int(0.99 * len(sorted_runs))]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "unit": self.unit,
            "n_runs": len(self.runs),
            "mean": round(self.mean, 4),
            "stdev": round(self.stdev, 4),
            "min": round(self.min, 4),
            "max": round(self.max, 4),
            "p50": round(self.p50, 4),
            "p95": round(self.p95, 4),
            "p99": round(self.p99, 4),
        }


class ModelBenchmarkSuite:
    """Comprehensive benchmark suite for ML models."""

    def __init__(
        self,
        name: str = "ml_model_benchmarks",
        device: str = "cpu",
        num_repeats: int = 10,
        warmup_iters: int = 2,
    ):
        """Initialize the benchmark suite.

        Args:
            name: Suite name
            device: Device to run on ('cpu' or 'cuda')
            num_repeats: Number of times to repeat each benchmark
            warmup_iters: Number of warmup iterations before timing
        """
        self.name = name
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.num_repeats = num_repeats
        self.warmup_iters = warmup_iters
        self.results: dict[str, PerformanceAnalysis] = {}

    def benchmark_model_init(
        self,
        model_fn: Callable[[], nn.Module],
        model_name: str = "model_init",
    ) -> PerformanceAnalysis:
        """Benchmark model initialization.

        Args:
            model_fn: Function that returns a model instance
            model_name: Name for this benchmark

        Returns:
            PerformanceAnalysis with timing statistics
        """
        analysis = PerformanceAnalysis(f"{model_name}_init", unit="ms")

        for _ in range(self.num_repeats):
            start = time.perf_counter()
            model = model_fn()
            model = model.to(self.device)
            elapsed_ms = (time.perf_counter() - start) * 1000
            analysis.runs.append(elapsed_ms)

        self.results[analysis.name] = analysis
        return analysis

    def benchmark_forward_pass(
        self,
        model: nn.Module,
        batch: dict[str, torch.Tensor],
        model_name: str = "model_forward",
    ) -> PerformanceAnalysis:
        """Benchmark forward pass performance.

        Args:
            model: PyTorch model
            batch: Input batch (dict of tensors)
            model_name: Name for this benchmark

        Returns:
            PerformanceAnalysis with timing statistics
        """
        model.eval()
        analysis = PerformanceAnalysis(f"{model_name}_forward", unit="ms")

        # Warmup
        with torch.no_grad():
            for _ in range(self.warmup_iters):
                _ = model(**batch)

        # Benchmark
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()

        for _ in range(self.num_repeats):
            start = time.perf_counter()
            with torch.no_grad():
                _ = model(**batch)
            elapsed_ms = (time.perf_counter() - start) * 1000
            analysis.runs.append(elapsed_ms)

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        self.results[analysis.name] = analysis
        return analysis

    def benchmark_backward_pass(
        self,
        model: nn.Module,
        batch: dict[str, torch.Tensor],
        optimizer: Optional[torch.optim.Optimizer] = None,
        model_name: str = "model_backward",
    ) -> PerformanceAnalysis:
        """Benchmark backward pass (training step) performance.

        Args:
            model: PyTorch model
            batch: Input batch (dict of tensors)
            optimizer: Optional optimizer for gradient updates
            model_name: Name for this benchmark

        Returns:
            PerformanceAnalysis with timing statistics
        """
        model.train()

        if optimizer is None:
            optimizer = Adam(model.parameters(), lr=0.001)

        analysis = PerformanceAnalysis(f"{model_name}_backward", unit="ms")

        # Warmup
        for _ in range(self.warmup_iters):
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = self._get_loss(outputs)
            loss.backward()
            optimizer.step()

        # Benchmark
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()

        for _ in range(self.num_repeats):
            start = time.perf_counter()
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = self._get_loss(outputs)
            loss.backward()
            optimizer.step()
            elapsed_ms = (time.perf_counter() - start) * 1000
            analysis.runs.append(elapsed_ms)

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        self.results[analysis.name] = analysis
        return analysis

    def benchmark_memory_usage(
        self,
        model: nn.Module,
        batch: dict[str, torch.Tensor],
        model_name: str = "model_memory",
        num_forward_passes: int = 10,
    ) -> dict[str, float]:
        """Benchmark memory usage during forward/backward passes.

        Args:
            model: PyTorch model
            batch: Input batch (dict of tensors)
            model_name: Name for this benchmark
            num_forward_passes: Number of forward passes to measure

        Returns:
            Dictionary with memory metrics
        """
        model.train()

        if not torch.cuda.is_available():
            return {
                "gpu_available": False,
                "cpu_memory_mb": 0.0,
                "gpu_memory_mb": 0.0,
            }

        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()

        optimizer = Adam(model.parameters(), lr=0.001)

        # Run training steps
        for _ in range(num_forward_passes):
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = self._get_loss(outputs)
            loss.backward()
            optimizer.step()

        torch.cuda.synchronize()
        peak_memory_bytes = torch.cuda.max_memory_allocated()
        peak_memory_mb = peak_memory_bytes / (1024**2)

        return {
            "gpu_available": True,
            "peak_memory_mb": round(peak_memory_mb, 2),
            "device": str(self.device),
        }

    def benchmark_checkpoint_io(
        self,
        model: nn.Module,
        model_name: str = "model_checkpoint",
    ) -> dict[str, float]:
        """Benchmark checkpoint save/load performance.

        Args:
            model: PyTorch model
            model_name: Name for this benchmark

        Returns:
            Dictionary with save/load timing
        """
        analysis_save = PerformanceAnalysis(f"{model_name}_checkpoint_save", unit="ms")
        analysis_load = PerformanceAnalysis(f"{model_name}_checkpoint_load", unit="ms")

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.pt"

            # Benchmark save
            for _ in range(self.num_repeats):
                start = time.perf_counter()
                torch.save(model.state_dict(), checkpoint_path)
                elapsed_ms = (time.perf_counter() - start) * 1000
                analysis_save.runs.append(elapsed_ms)

            # Benchmark load
            for _ in range(self.num_repeats):
                start = time.perf_counter()
                state_dict = torch.load(checkpoint_path)
                model.load_state_dict(state_dict)
                elapsed_ms = (time.perf_counter() - start) * 1000
                analysis_load.runs.append(elapsed_ms)

            file_size_mb = checkpoint_path.stat().st_size / (1024**2)

        self.results[analysis_save.name] = analysis_save
        self.results[analysis_load.name] = analysis_load

        return {
            "checkpoint_size_mb": round(file_size_mb, 2),
            "save_ms_mean": round(analysis_save.mean, 4),
            "save_ms_stdev": round(analysis_save.stdev, 4),
            "load_ms_mean": round(analysis_load.mean, 4),
            "load_ms_stdev": round(analysis_load.stdev, 4),
        }

    @staticmethod
    def _get_loss(outputs: Any) -> torch.Tensor:
        """Extract loss from model outputs."""
        if hasattr(outputs, "loss"):
            return outputs.loss
        if isinstance(outputs, dict) and "loss" in outputs:
            return outputs["loss"]
        if isinstance(outputs, (tuple, list)) and len(outputs) > 0:
            if isinstance(outputs[0], torch.Tensor):
                return outputs[0]
        # Fallback: create a loss from logits
        if isinstance(outputs, torch.Tensor):
            return outputs.sum() / outputs.numel()
        raise ValueError(f"Cannot extract loss from outputs: {type(outputs)}")

    def print_summary(self) -> None:
        """Print summary of all benchmarks."""
        print("\n" + "=" * 80)
        print(f"PERFORMANCE BENCHMARK SUMMARY: {self.name}")
        print("=" * 80)

        for name, analysis in sorted(self.results.items()):
            print(f"\n{name}:")
            print(f"  Mean:  {analysis.mean:.4f} {analysis.unit}")
            print(f"  Stdev: {analysis.stdev:.4f} {analysis.unit}")
            print(f"  Min:   {analysis.min:.4f} {analysis.unit}")
            print(f"  Max:   {analysis.max:.4f} {analysis.unit}")
            print(f"  P50:   {analysis.p50:.4f} {analysis.unit}")
            print(f"  P95:   {analysis.p95:.4f} {analysis.unit}")
            print(f"  P99:   {analysis.p99:.4f} {analysis.unit}")
            print(f"  Runs:  {len(analysis.runs)}")

        print("\n" + "=" * 80)

    def save_results(self, output_path: Path) -> None:
        """Save benchmark results to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        results_dict = {
            "suite_name": self.name,
            "device": str(self.device),
            "num_repeats": self.num_repeats,
            "results": {name: analysis.to_dict() for name, analysis in self.results.items()},
        }

        with open(output_path, "w") as f:
            json.dump(results_dict, f, indent=2)

        print(f"\nResults saved to: {output_path}")


def run_ml_benchmarks(
    output_dir: Optional[Path] = None,
    device: str = "cpu",
    num_repeats: int = 10,
) -> ModelBenchmarkSuite:
    """Run comprehensive ML model benchmarks.

    Args:
        output_dir: Directory to save results
        device: Device to run on
        num_repeats: Number of benchmark repeats

    Returns:
        ModelBenchmarkSuite with completed benchmarks
    """
    suite = ModelBenchmarkSuite(
        name="ml_model_benchmarks",
        device=device,
        num_repeats=num_repeats,
        warmup_iters=2,
    )

    print(f"\n{'='*80}")
    print("STARTING ML MODEL PERFORMANCE BENCHMARKS")
    print(f"{'='*80}")
    print(f"Device: {suite.device}")
    print(f"Repeats per benchmark: {num_repeats}")
    print(f"Warmup iterations: 2")

    # =========================================================================
    # Benchmark 1: MiniLM Model Initialization
    # =========================================================================
    print("\n[1/10] Benchmarking MiniLM model initialization...")
    minilm_cfg = MiniLMConfig(vocab_size=1000, d_model=64, n_heads=4, n_layers=3)

    def create_minilm():
        return MiniLM(minilm_cfg)

    result = suite.benchmark_model_init(create_minilm, "minilm")
    print(f"      Mean init time: {result.mean:.2f} ms")

    # =========================================================================
    # Benchmark 2: MiniLM Forward Pass
    # =========================================================================
    print("[2/10] Benchmarking MiniLM forward pass...")
    minilm_model = create_minilm().to(suite.device)
    batch_size, seq_len = 8, 16
    minilm_batch = {
        "input_ids": torch.randint(0, minilm_cfg.vocab_size, (batch_size, seq_len)).to(
            suite.device
        )
    }

    result = suite.benchmark_forward_pass(minilm_model, minilm_batch, "minilm")
    print(f"      Mean forward time: {result.mean:.2f} ms")

    # =========================================================================
    # Benchmark 3: MiniLM Backward Pass
    # =========================================================================
    print("[3/10] Benchmarking MiniLM backward pass...")
    minilm_model = create_minilm().to(suite.device)
    optimizer = Adam(minilm_model.parameters(), lr=0.001)

    result = suite.benchmark_backward_pass(minilm_model, minilm_batch, optimizer, "minilm")
    print(f"      Mean backward time: {result.mean:.2f} ms")

    # =========================================================================
    # Benchmark 4: DecoderOnlyLM Model Initialization
    # =========================================================================
    print("[4/10] Benchmarking DecoderOnlyLM model initialization...")
    decoder_cfg = ModelConfig(vocab_size=2000, d_model=128, n_heads=8, n_layers=6)

    def create_decoder():
        return DecoderOnlyLM(decoder_cfg)

    result = suite.benchmark_model_init(create_decoder, "decoder_only")
    print(f"      Mean init time: {result.mean:.2f} ms")

    # =========================================================================
    # Benchmark 5: DecoderOnlyLM Forward Pass
    # =========================================================================
    print("[5/10] Benchmarking DecoderOnlyLM forward pass...")
    decoder_model = create_decoder().to(suite.device)
    batch_size, seq_len = 4, 32
    decoder_batch = {
        "input_ids": torch.randint(0, decoder_cfg.vocab_size, (batch_size, seq_len)).to(
            suite.device
        )
    }

    result = suite.benchmark_forward_pass(decoder_model, decoder_batch, "decoder_only")
    print(f"      Mean forward time: {result.mean:.2f} ms")

    # =========================================================================
    # Benchmark 6: DecoderOnlyLM Backward Pass
    # =========================================================================
    print("[6/10] Benchmarking DecoderOnlyLM backward pass...")
    decoder_model = create_decoder().to(suite.device)
    optimizer = Adam(decoder_model.parameters(), lr=0.001)

    result = suite.benchmark_backward_pass(
        decoder_model, decoder_batch, optimizer, "decoder_only"
    )
    print(f"      Mean backward time: {result.mean:.2f} ms")

    # =========================================================================
    # Benchmark 7: Memory Usage - MiniLM
    # =========================================================================
    print("[7/10] Benchmarking MiniLM memory usage...")
    minilm_model = create_minilm().to(suite.device)
    memory_result = suite.benchmark_memory_usage(minilm_model, minilm_batch, "minilm")
    if memory_result["gpu_available"]:
        print(f"      Peak GPU memory: {memory_result['peak_memory_mb']:.2f} MB")

    # =========================================================================
    # Benchmark 8: Memory Usage - DecoderOnlyLM
    # =========================================================================
    print("[8/10] Benchmarking DecoderOnlyLM memory usage...")
    decoder_model = create_decoder().to(suite.device)
    memory_result = suite.benchmark_memory_usage(decoder_model, decoder_batch, "decoder_only")
    if memory_result["gpu_available"]:
        print(f"      Peak GPU memory: {memory_result['peak_memory_mb']:.2f} MB")

    # =========================================================================
    # Benchmark 9: Checkpoint I/O - MiniLM
    # =========================================================================
    print("[9/10] Benchmarking MiniLM checkpoint save/load...")
    minilm_model = create_minilm().to(suite.device)
    checkpoint_result = suite.benchmark_checkpoint_io(minilm_model, "minilm")
    print(f"      Checkpoint size: {checkpoint_result['checkpoint_size_mb']:.2f} MB")
    print(f"      Save time: {checkpoint_result['save_ms_mean']:.2f} ms")
    print(f"      Load time: {checkpoint_result['load_ms_mean']:.2f} ms")

    # =========================================================================
    # Benchmark 10: Checkpoint I/O - DecoderOnlyLM
    # =========================================================================
    print("[10/10] Benchmarking DecoderOnlyLM checkpoint save/load...")
    decoder_model = create_decoder().to(suite.device)
    checkpoint_result = suite.benchmark_checkpoint_io(decoder_model, "decoder_only")
    print(f"      Checkpoint size: {checkpoint_result['checkpoint_size_mb']:.2f} MB")
    print(f"      Save time: {checkpoint_result['save_ms_mean']:.2f} ms")
    print(f"      Load time: {checkpoint_result['load_ms_mean']:.2f} ms")

    # =========================================================================
    # Print Summary and Save Results
    # =========================================================================
    suite.print_summary()

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        suite.save_results(output_dir / "ml_benchmarks.json")

    return suite


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ML Model Performance Benchmarks")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "results",
        help="Output directory for benchmark results",
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="Device to run benchmarks on",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=10,
        help="Number of times to repeat each benchmark",
    )

    args = parser.parse_args()

    suite = run_ml_benchmarks(
        output_dir=args.output_dir,
        device=args.device,
        num_repeats=args.repeats,
    )
