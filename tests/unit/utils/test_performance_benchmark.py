import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset
from src.codex_ml.utils.performance_benchmark import (
    PerformanceBenchmark,
    BenchmarkResult,
    benchmark_data_loading,
    benchmark_inference,
    benchmark_training_step,
)

class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = torch.nn.Linear(10, 1)

    def forward(self, x):
        if isinstance(x, dict):
            # For inference where batch is dict
            return self.linear(x["input"])
        return self.linear(x)

def test_performance_benchmark_context():
    pb = PerformanceBenchmark("test_ctx")
    with pb:
        # do some work
        _ = sum(range(100))
    result = pb.get_result()
    assert isinstance(result, BenchmarkResult)
    assert result.name == "test_ctx"
    assert result.duration_ms > 0

def test_benchmark_data_loading():
    dataset = TensorDataset(torch.randn(10, 10))
    loader = DataLoader(dataset, batch_size=2)
    result = benchmark_data_loading(loader, num_batches=2)
    assert result.name == "data_loading"
    assert result.throughput is not None
    assert result.throughput > 0

def test_benchmark_inference():
    model = DummyModel()
    batch = {"input": torch.randn(2, 10)}
    result = benchmark_inference(model, batch, num_iterations=2, warmup_iters=1)
    assert result.name == "inference"
    assert result.throughput is not None

def test_benchmark_training_step():
    model = DummyModel()
    batch = {"input": torch.randn(2, 10), "target": torch.randn(2, 1)}
    
    # Needs a mock training step that returns loss, or the function might expect specific signature?
    # Let's check how benchmark_training_step uses the model.
    pass

