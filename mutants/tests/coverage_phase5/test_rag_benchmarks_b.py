"""Test RAG benchmark fixtures 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class BenchmarkResult:
    metric_name: str
    value: float
    unit: str


class BenchmarkFixture:
    def __init__(self, name: str):
        self.name = name
        self.results: List[BenchmarkResult] = []

    def record_metric(self, metric_name: str, value: float, unit: str = "ms"):
        result = BenchmarkResult(metric_name, value, unit)
        self.results.append(result)

    def get_metric(self, metric_name: str) -> float:
        for r in self.results:
            if r.metric_name == metric_name:
                return r.value
        return -1.0


def test_benchmark_fixture_1_init():
    """Test benchmark fixture initialization."""
    fixture = BenchmarkFixture("bench1")
    assert fixture.name == "bench1", "name is not valid"


def test_benchmark_fixture_1_record():
    """Test recording benchmark metrics."""
    fixture = BenchmarkFixture("bench1")
    fixture.record_metric("latency", 42.5, "ms")

    assert len(fixture.results) == 1, "Collection must not be empty"
    assert fixture.results[0].value == 42.5, "Result must not be empty"


def test_benchmark_fixture_1_retrieve():
    """Test retrieving benchmark metrics."""
    fixture = BenchmarkFixture("bench1")
    fixture.record_metric("throughput", 1000.0, "ops/sec")

    value = fixture.get_metric("throughput")
    assert value == 1000.0, "Value must be initialized"


def test_benchmark_fixture_1_missing():
    """Test missing metric retrieval."""
    fixture = BenchmarkFixture("bench1")
    value = fixture.get_metric("nonexistent")

    assert value == -1.0, "Value must be initialized"
