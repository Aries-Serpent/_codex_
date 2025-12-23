"""
Benchmarks for AST parsing performance.
"""
import pytest
from pathlib import Path

from codex.ast import parse_python

# Sample code of varying sizes for benchmarking
SMALL_CODE = """
def hello():
    return "world"
"""

MEDIUM_CODE = """
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        results = []
        for item in self.data:
            if item.is_valid():
                processed = self.transform(item)
                results.append(processed)
        return results
    
    def transform(self, item):
        return item.value * 2
"""

LARGE_CODE = """
class ComplexSystem:
    def __init__(self):
        self.cache = {}
        self.handlers = []
    
""" + "\n".join([
    f"    def method_{i}(self, x):\n        return x + {i}"
    for i in range(100)
])


class TestParsingBenchmarks:
    """Benchmark AST parsing performance."""
    
    def test_parse_small_file(self, benchmark):
        """Benchmark parsing small file."""
        result = benchmark(parse_python, SMALL_CODE, "small.py")
        assert result is not None
    
    def test_parse_medium_file(self, benchmark):
        """Benchmark parsing medium file."""
        result = benchmark(parse_python, MEDIUM_CODE, "medium.py")
        assert result is not None
    
    def test_parse_large_file(self, benchmark):
        """Benchmark parsing large file."""
        result = benchmark(parse_python, LARGE_CODE, "large.py")
        assert result is not None
    
    def test_parse_multiple_files(self, benchmark):
        """Benchmark parsing multiple files."""
        codes = [SMALL_CODE, MEDIUM_CODE, LARGE_CODE]
        
        def parse_all():
            results = []
            for i, code in enumerate(codes):
                node = parse_python(code, f"file_{i}.py")
                results.append(node)
            return results
        
        results = benchmark(parse_all)
        assert len(results) == 3
