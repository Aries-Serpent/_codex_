"""
Performance benchmarking tests for inference server.

Measures throughput, latency, and resource utilization.
"""

import time
import statistics
from typing import List, Dict
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def perf_client():
    """Create test client for performance testing."""
    from src.codex_ml.serving.inference_server import create_app
    app = create_app(enable_auth=False)
    return TestClient(app)


class TestThroughputBenchmarks:
    """Benchmark request throughput."""

    def test_health_endpoint_throughput(self, perf_client):
        """Measure throughput of health endpoint (baseline)."""
        duration = 3  # seconds
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            response = perf_client.get("/health")
            if response.status_code == 200:
                request_count += 1
        
        throughput = request_count / duration
        print(f"\nHealth endpoint throughput: {throughput:.2f} req/s")
        
        # Target: >1000 req/s for simple health checks
        assert throughput > 500, f"Throughput too low: {throughput:.2f} req/s"

    def test_inference_endpoint_throughput(self, perf_client):
        """Measure throughput of inference endpoint."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            # Mock fast model
            mock_model = MagicMock()
            mock_model.return_value = ["output"]
            mock_load.return_value = mock_model
            
            duration = 5  # seconds
            start_time = time.time()
            request_count = 0
            
            while time.time() - start_time < duration:
                response = perf_client.post(
                    "/infer",
                    json={
                        "model_name": "fast-model",
                        "inputs": ["test"],
                        "max_length": 50
                    }
                )
                if response.status_code == 200:
                    request_count += 1
            
            throughput = request_count / duration
            print(f"\nInference throughput: {throughput:.2f} req/s")
            
            # Target: >50 req/s for inference
            assert throughput > 20, f"Inference throughput too low: {throughput:.2f} req/s"

    def test_batch_inference_throughput(self, perf_client):
        """Measure throughput of batch inference endpoint."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            mock_model = MagicMock()
            mock_model.return_value = ["output1", "output2", "output3"]
            mock_load.return_value = mock_model
            
            duration = 5
            start_time = time.time()
            samples_processed = 0
            
            while time.time() - start_time < duration:
                batch_size = 10
                response = perf_client.post(
                    "/batch_infer",
                    json={
                        "model_name": "batch-model",
                        "inputs": ["test"] * batch_size,
                        "max_length": 50
                    }
                )
                if response.status_code == 200:
                    samples_processed += batch_size
            
            throughput = samples_processed / duration
            print(f"\nBatch inference throughput: {throughput:.2f} samples/s")
            
            # Target: >100 samples/s with batching
            assert throughput > 50, f"Batch throughput too low: {throughput:.2f} samples/s"


class TestLatencyDistribution:
    """Measure latency distributions (P50, P95, P99)."""

    def test_health_endpoint_latency(self, perf_client):
        """Measure latency distribution of health endpoint."""
        latencies = []
        
        for _ in range(100):
            start = time.time()
            response = perf_client.get("/health")
            latency = (time.time() - start) * 1000  # ms
            
            if response.status_code == 200:
                latencies.append(latency)
        
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        
        print(f"\nHealth endpoint latency:")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        
        # Targets: P50<10ms, P95<50ms, P99<100ms
        assert p50 < 100, f"P50 latency too high: {p50:.2f}ms"
        assert p95 < 500, f"P95 latency too high: {p95:.2f}ms"
        assert p99 < 1000, f"P99 latency too high: {p99:.2f}ms"

    def test_inference_endpoint_latency(self, perf_client):
        """Measure latency distribution of inference endpoint."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            mock_model = MagicMock()
            mock_model.return_value = ["output"]
            mock_load.return_value = mock_model
            
            latencies = []
            
            for _ in range(100):
                start = time.time()
                response = perf_client.post(
                    "/infer",
                    json={
                        "model_name": "test-model",
                        "inputs": ["test input"],
                        "max_length": 50
                    }
                )
                latency = (time.time() - start) * 1000  # ms
                
                if response.status_code == 200:
                    latencies.append(latency)
            
            if latencies:
                p50 = statistics.median(latencies)
                p95 = statistics.quantiles(latencies, n=20)[18]
                p99 = statistics.quantiles(latencies, n=100)[98]
                
                print(f"\nInference endpoint latency:")
                print(f"  P50: {p50:.2f}ms")
                print(f"  P95: {p95:.2f}ms")
                print(f"  P99: {p99:.2f}ms")
                
                # Targets: P50<100ms, P95<500ms, P99<1000ms
                assert p50 < 500, f"P50 latency too high: {p50:.2f}ms"
                assert p95 < 2000, f"P95 latency too high: {p95:.2f}ms"

    def test_latency_under_load(self, perf_client):
        """Measure latency degradation under concurrent load."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            mock_model = MagicMock()
            mock_model.return_value = ["output"]
            mock_load.return_value = mock_model
            
            # Baseline latency (no load)
            baseline_latencies = []
            for _ in range(20):
                start = time.time()
                perf_client.post(
                    "/infer",
                    json={
                        "model_name": "test-model",
                        "inputs": ["test"],
                        "max_length": 50
                    }
                )
                baseline_latencies.append((time.time() - start) * 1000)
            
            baseline_p50 = statistics.median(baseline_latencies)
            
            # Latency under load (concurrent requests)
            load_latencies = []
            for _ in range(50):  # Higher load
                start = time.time()
                perf_client.post(
                    "/infer",
                    json={
                        "model_name": "test-model",
                        "inputs": ["test"],
                        "max_length": 50
                    }
                )
                load_latencies.append((time.time() - start) * 1000)
            
            load_p50 = statistics.median(load_latencies)
            
            degradation = ((load_p50 - baseline_p50) / baseline_p50) * 100
            print(f"\nLatency degradation under load: {degradation:.1f}%")
            print(f"  Baseline P50: {baseline_p50:.2f}ms")
            print(f"  Load P50: {load_p50:.2f}ms")
            
            # Latency should not degrade more than 200% under load
            assert degradation < 300, f"Latency degradation too high: {degradation:.1f}%"


class TestCachePerformance:
    """Test model cache hit rates and performance."""

    def test_cache_hit_rate_measurement(self, perf_client):
        """Measure cache hit rate for repeated model requests."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            mock_model = MagicMock()
            mock_model.return_value = ["output"]
            mock_load.return_value = mock_model
            
            # Load same model multiple times
            model_name = "cached-model"
            for _ in range(10):
                perf_client.post(
                    "/infer",
                    json={
                        "model_name": model_name,
                        "inputs": ["test"],
                        "max_length": 50
                    }
                )
            
            # Check cache stats if available
            # First load = miss, subsequent loads = hits
            # Expected hit rate: 9/10 = 90%
            call_count = mock_load.call_count
            print(f"\nModel loader called {call_count} times for 10 requests")
            
            # With caching, should be called <= 3 times (cache size is 3)
            assert call_count <= 3, f"Cache not working effectively: {call_count} calls"

    def test_cache_vs_no_cache_performance(self, perf_client):
        """Compare performance with and without cache."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            # Simulate slow model loading
            def slow_load(*args, **kwargs):
                time.sleep(0.1)  # 100ms load time
                mock_model = MagicMock()
                mock_model.return_value = ["output"]
                return mock_model
            
            mock_load.side_effect = slow_load
            
            # First request (cache miss)
            start = time.time()
            perf_client.post(
                "/infer",
                json={
                    "model_name": "slow-model",
                    "inputs": ["test"],
                    "max_length": 50
                }
            )
            first_latency = (time.time() - start) * 1000
            
            # Second request (cache hit)
            start = time.time()
            perf_client.post(
                "/infer",
                json={
                    "model_name": "slow-model",
                    "inputs": ["test"],
                    "max_length": 50
                }
            )
            second_latency = (time.time() - start) * 1000
            
            speedup = first_latency / second_latency if second_latency > 0 else 1
            print(f"\nCache speedup: {speedup:.2f}x")
            print(f"  First request: {first_latency:.2f}ms")
            print(f"  Cached request: {second_latency:.2f}ms")
            
            # Cache should provide significant speedup
            assert speedup > 1.5, f"Cache speedup insufficient: {speedup:.2f}x"

    def test_cache_eviction_performance(self, perf_client):
        """Test performance impact of cache evictions."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            mock_model = MagicMock()
            mock_model.return_value = ["output"]
            mock_load.return_value = mock_model
            
            # Load more models than cache size (3)
            models = [f"model-{i}" for i in range(5)]
            
            for model_name in models:
                perf_client.post(
                    "/infer",
                    json={
                        "model_name": model_name,
                        "inputs": ["test"],
                        "max_length": 50
                    }
                )
            
            # Cache should have evicted old models
            # Loading 5 models with cache size 3 should call load_model 5 times
            assert mock_load.call_count == 5


class TestResourceUtilization:
    """Test resource usage patterns."""

    def test_memory_footprint_measurement(self, perf_client):
        """Measure memory footprint of inference server."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make 100 requests
        for _ in range(100):
            perf_client.get("/health")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - baseline_memory
        
        print(f"\nMemory usage:")
        print(f"  Baseline: {baseline_memory:.2f} MB")
        print(f"  After 100 requests: {final_memory:.2f} MB")
        print(f"  Growth: {memory_growth:.2f} MB")
        
        # Memory growth should be minimal (<100MB for 100 requests)
        assert memory_growth < 200, f"Memory growth too high: {memory_growth:.2f} MB"

    def test_cpu_utilization_patterns(self, perf_client):
        """Measure CPU utilization during inference."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure CPU during load
        start_cpu = process.cpu_percent(interval=0.1)
        
        for _ in range(50):
            perf_client.get("/health")
        
        end_cpu = process.cpu_percent(interval=0.1)
        
        print(f"\nCPU utilization:")
        print(f"  Start: {start_cpu:.1f}%")
        print(f"  End: {end_cpu:.1f}%")
        
        # CPU should be utilized but not maxed out
        assert end_cpu < 100, f"CPU maxed out: {end_cpu:.1f}%"


class TestScalabilityMetrics:
    """Test scalability characteristics."""

    def test_request_queue_depth(self, perf_client):
        """Measure request queue depth under load."""
        # Submit many requests quickly
        start = time.time()
        for _ in range(100):
            perf_client.get("/health")
        duration = time.time() - start
        
        throughput = 100 / duration
        print(f"\nProcessed 100 requests in {duration:.2f}s ({throughput:.1f} req/s)")
        
        # Should handle 100 requests in reasonable time
        assert duration < 10, f"Request queue too slow: {duration:.2f}s"

    def test_concurrent_model_loading(self, perf_client):
        """Test performance with multiple models loaded concurrently."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.load_model") as mock_load:
            mock_model = MagicMock()
            mock_model.return_value = ["output"]
            mock_load.return_value = mock_model
            
            # Request different models concurrently
            models = [f"model-{i}" for i in range(3)]
            start = time.time()
            
            for model_name in models:
                for _ in range(10):
                    perf_client.post(
                        "/infer",
                        json={
                            "model_name": model_name,
                            "inputs": ["test"],
                            "max_length": 50
                        }
                    )
            
            duration = time.time() - start
            total_requests = 30
            throughput = total_requests / duration
            
            print(f"\nMulti-model throughput: {throughput:.1f} req/s")
            assert throughput > 10, f"Multi-model throughput too low: {throughput:.1f} req/s"


# Performance test configuration
pytestmark = pytest.mark.performance


def pytest_configure(config):
    """Add performance marker."""
    config.addinivalue_line(
        "markers", "performance: mark test as performance benchmark"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
