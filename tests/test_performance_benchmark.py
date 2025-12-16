"""Tests for performance benchmarking suite."""

import pytest
import torch
import torch.nn as nn
from torch.optim import Adam

from codex_ml.utils.performance_benchmark import (
    BenchmarkResult,
    PerformanceBenchmark,
    BenchmarkSuite,
    benchmark_training_step,
    benchmark_inference,
    benchmark_data_loading,
)


class SimpleModel(nn.Module):
    """Simple model for testing."""

    def __init__(self, input_size=10, hidden_size=20, output_size=2):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, input_ids, **kwargs):
        x = self.fc1(input_ids)
        x = torch.relu(x)
        x = self.fc2(x)
        return {"loss": x.mean(), "logits": x}


def test_benchmark_result_creation():
    """Test BenchmarkResult creation and conversion."""
    result = BenchmarkResult(
        name="test_benchmark",
        duration_ms=100.5,
        throughput=50.0,
        memory_mb=256.0,
    )

    assert result.name == "test_benchmark"
    assert result.duration_ms == 100.5
    assert result.throughput == 50.0
    assert result.memory_mb == 256.0

    # Test to_dict
    result_dict = result.to_dict()
    assert result_dict["name"] == "test_benchmark"
    assert result_dict["duration_ms"] == 100.5

    # Test string representation
    result_str = str(result)
    assert "test_benchmark" in result_str
    assert "100.50ms" in result_str


def test_performance_benchmark_context():
    """Test PerformanceBenchmark context manager."""
    import time

    benchmark = PerformanceBenchmark("test_operation")

    with benchmark:
        time.sleep(0.1)  # Sleep for 100ms

    assert benchmark.result is not None
    assert benchmark.result.name == "test_operation"
    assert benchmark.result.duration_ms >= 100  # At least 100ms
    assert benchmark.result.duration_ms < 150  # But not too much more


def test_benchmark_training_step():
    """Test training step benchmarking."""
    model = SimpleModel()
    batch = {
        "input_ids": torch.randn(4, 10),
    }
    optimizer = Adam(model.parameters(), lr=0.001)

    result = benchmark_training_step(
        model=model,
        batch=batch,
        optimizer=optimizer,
        num_iterations=5,
        warmup_iters=1,
    )

    assert result.name == "training_step"
    assert result.duration_ms > 0
    assert result.throughput > 0
    assert result.metadata["num_iterations"] == 5
    assert result.metadata["batch_size"] == 4
    assert "avg_ms_per_step" in result.metadata


def test_benchmark_inference():
    """Test inference benchmarking."""
    model = SimpleModel()
    batch = {
        "input_ids": torch.randn(8, 10),
    }

    result = benchmark_inference(
        model=model,
        batch=batch,
        num_iterations=10,
        warmup_iters=2,
    )

    assert result.name == "inference"
    assert result.duration_ms > 0
    assert result.throughput > 0
    assert result.metadata["num_iterations"] == 10
    assert result.metadata["batch_size"] == 8
    assert "avg_ms_per_sample" in result.metadata


def test_benchmark_data_loading():
    """Test data loading benchmarking."""
    from torch.utils.data import DataLoader, TensorDataset

    # Create simple dataset
    dataset = TensorDataset(torch.randn(100, 10), torch.randint(0, 2, (100,)))
    dataloader = DataLoader(dataset, batch_size=4, num_workers=0)

    result = benchmark_data_loading(
        dataloader=dataloader,
        num_batches=10,
    )

    assert result.name == "data_loading"
    assert result.duration_ms > 0
    assert result.throughput > 0
    assert result.metadata["num_batches"] == 10
    assert "avg_ms_per_batch" in result.metadata


def test_benchmark_suite():
    """Test BenchmarkSuite functionality."""
    suite = BenchmarkSuite("test_suite")

    # Add some results
    suite.add_result(
        BenchmarkResult(
            name="operation1",
            duration_ms=100.0,
            throughput=50.0,
        )
    )
    suite.add_result(
        BenchmarkResult(
            name="operation2",
            duration_ms=200.0,
            throughput=25.0,
        )
    )

    assert len(suite.results) == 2
    assert suite.name == "test_suite"

    # Test print summary (should not raise)
    suite.print_summary()


def test_benchmark_suite_save_load(tmp_path):
    """Test saving and loading benchmark results."""
    import json

    suite = BenchmarkSuite("test_suite")
    suite.add_result(
        BenchmarkResult(
            name="test_op",
            duration_ms=150.0,
            throughput=30.0,
            memory_mb=512.0,
        )
    )

    # Save results
    output_file = tmp_path / "benchmarks.json"
    suite.save_results(str(output_file))

    assert output_file.exists()

    # Load and verify
    with open(output_file) as f:
        data = json.load(f)

    assert data["suite_name"] == "test_suite"
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "test_op"
    assert data["results"][0]["duration_ms"] == 150.0


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_benchmark_with_gpu():
    """Test benchmarking with GPU."""
    model = SimpleModel().cuda()
    batch = {
        "input_ids": torch.randn(4, 10).cuda(),
    }
    optimizer = Adam(model.parameters())

    result = benchmark_training_step(
        model=model,
        batch=batch,
        optimizer=optimizer,
        num_iterations=3,
        warmup_iters=1,
    )

    assert result.gpu_memory_mb is not None
    assert result.gpu_memory_mb > 0
