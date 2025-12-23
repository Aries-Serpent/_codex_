"""
Benchmarks for code smell detection.
"""
import pytest
from codex.ast import CodeSmellDetector, parse_python

# Test code with various complexity levels
COMPLEX_CODE = """
def complex_function(a, b, c, d):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    for i in range(a):
                        for j in range(b):
                            if i == j:
                                return i + j
    return 0
"""


class TestSmellDetectionBenchmarks:
    """Benchmark code smell detection."""
    
    def test_detect_smells_single_file(self, benchmark):
        """Benchmark smell detection on single file."""
        detector = CodeSmellDetector()
        node = parse_python(COMPLEX_CODE, "test.py")
        
        result = benchmark(detector.detect, node)
        assert len(result) > 0
    
    def test_detect_smells_batch(self, benchmark):
        """Benchmark smell detection on batch of nodes."""
        detector = CodeSmellDetector()
        nodes = [
            parse_python(COMPLEX_CODE, f"file_{i}.py")
            for i in range(10)
        ]
        
        def detect_all():
            results = []
            for node in nodes:
                smells = detector.detect(node)
                results.extend(smells)
            return results
        
        results = benchmark(detect_all)
        assert len(results) > 0
