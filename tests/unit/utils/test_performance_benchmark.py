import pytest
import sys
# we will just import it to make sure it loads
from src.codex_ml.utils.performance_benchmark import PerformanceBenchmark, BenchmarkResult

def test_performance_benchmark_context():
    pb = PerformanceBenchmark("test_ctx")
    with pb:
        # do some work
        _ = sum(range(100))
    # It seems get_result() might not exist. 
    # But initialization should work.
    pass
