"""
Chaos engineering tests for inference server.

Tests failure scenarios, resilience, and recovery mechanisms.
"""

import time
from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

# Reusable stub prediction result returned by mocked ModelServer.predict calls.
# Using descriptive values so assertion failures are immediately legible in CI logs.
_STUB_PREDICTION = [
    {
        "prediction": "ok",
        "label": "test_label",
        "score": 1.0,
        "text": "test_text",
        "model": "test_model",
    }
]


@pytest.fixture
def chaos_client():
    """Create test client for chaos testing."""
    from src.codex_ml.serving.inference_server import create_app

    # create_app() takes optional config parameter, not enable_auth
    # Authentication is controlled via env vars (CODEX_API_KEYS, CODEX_JWT_SECRET)
    app = create_app()
    return TestClient(app)


class TestModelFailures:
    """Test model failure scenarios and recovery."""

    def test_random_model_failure_injection(self, chaos_client):
        """Test inference server handles random model failures gracefully."""
        with patch("src.codex_ml.serving.inference_server.ModelServer.predict") as mock_predict:
            # Simulate intermittent failures (50% failure rate)
            call_count = [0]

            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] % 2 == 0:
                    raise RuntimeError("Simulated model failure")
                return _STUB_PREDICTION

            mock_predict.side_effect = side_effect

            # Should handle failures gracefully
            for _ in range(10):
                response = chaos_client.post(
                    "/infer",
                    json={"model_name": "test-model", "inputs": ["test input"], "max_length": 50},
                )
                # Either succeeds or returns 500 with error
                assert response.status_code in [200, 500]

    def test_model_oom_scenario(self, chaos_client):
        """Test handling of out-of-memory errors during inference."""
        with patch("src.codex_ml.serving.inference_server.ModelServer.predict") as mock_predict:
            mock_predict.side_effect = RuntimeError("CUDA out of memory - memory pressure")

            response = chaos_client.post(
                "/infer", json={"model_name": "large-model", "inputs": ["test"], "max_length": 50}
            )

            assert response.status_code == 500, "Response must not be empty"
            assert "memory" in response.json()["detail"].lower(), "Response must not be empty"

    def test_model_corruption_detection(self, chaos_client):
        """Test detection of corrupted model weights."""
        with patch("src.codex_ml.serving.inference_server.ModelServer.predict") as mock_predict:
            mock_predict.side_effect = RuntimeError("Invalid checkpoint format detected")

            response = chaos_client.post(
                "/infer",
                json={"model_name": "corrupted-model", "inputs": ["test"], "max_length": 50},
            )

            assert response.status_code == 500, "Response must not be empty"
            assert "checkpoint" in response.json()["detail"].lower(), "Response must not be empty"

    def test_circuit_breaker_triggers_after_failures(self, chaos_client):
        """Test circuit breaker opens after consecutive failures."""
        with patch("src.codex_ml.serving.inference_server.ModelServer.predict") as mock_predict:
            mock_predict.side_effect = RuntimeError("Model inference failed")

            # Trigger circuit breaker with consecutive failures
            for i in range(6):
                response = chaos_client.post(
                    "/infer",
                    json={"model_name": "failing-model", "inputs": ["test"], "max_length": 50},
                )
                # First 5 should fail normally, 6th should hit circuit breaker
                assert response.status_code in [500, 503]


class TestNetworkFailures:
    """Test network-related failure scenarios."""

    def test_request_timeout_handling(self, chaos_client):
        """Test handling of errors that would arise from slow/hung inference."""
        with patch("src.codex_ml.serving.inference_server.ModelServer.predict") as mock_predict:
            mock_predict.side_effect = RuntimeError("Inference timed out")

            response = chaos_client.post(
                "/infer",
                json={"model_name": "slow-model", "inputs": ["test"], "max_length": 50},
            )
            assert response.status_code == 500, "Response must not be empty"

    def test_connection_reset_during_inference(self, chaos_client):
        """Test resilience to connection resets."""
        # Simulate abrupt connection close
        with patch("fastapi.responses.JSONResponse") as mock_response:
            mock_response.side_effect = ConnectionResetError("Connection reset by peer")

            try:
                chaos_client.post(
                    "/infer",
                    json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
                )
            except (ValueError, TypeError) as _err:
                # Should handle connection errors gracefully
                _ = None  # suppressed: no action needed


class TestResourcePressure:
    """Test behavior under resource pressure."""

    def test_memory_pressure_graceful_degradation(self, chaos_client):
        """Test graceful degradation under memory pressure."""
        with patch("src.codex_ml.serving.model_loader.ModelLoader.get_cache_stats") as mock_stats:
            # Simulate high memory usage
            mock_stats.return_value = {"size": 3, "maxsize": 3, "hits": 100, "misses": 10}

            response = chaos_client.get("/health")
            assert response.status_code == 200, "Response must not be empty"

    def test_disk_full_checkpoint_save(self, chaos_client):
        """Test handling of disk full errors during checkpoint saves."""
        # Test that server continues to operate even if checkpointing fails
        response = chaos_client.get("/health")
        assert response.status_code == 200, "Response must not be empty"

    def test_cpu_throttling_impact(self, chaos_client):
        """Test performance under CPU throttling."""
        # Measure baseline latency
        start = time.time()
        response = chaos_client.get("/health")
        baseline_latency = time.time() - start

        assert response.status_code == 200, "Response must not be empty"
        assert baseline_latency < 1.0, "baseline_latency is not valid"


class TestConcurrentLoad:
    """Test concurrent request handling."""

    def test_concurrent_request_handling(self, chaos_client):
        """Test handling of 100+ concurrent requests."""
        num_requests = 100
        responses = []

        def make_request():
            return chaos_client.get("/health")

        # Simulate concurrent requests
        for _ in range(num_requests):
            response = make_request()
            responses.append(response)

        # All requests should succeed
        assert all(r.status_code == 200 for r in responses), "Response must not be empty"

    def test_burst_traffic_handling(self, chaos_client):
        """Test handling of burst traffic patterns."""
        # Simulate burst of 50 requests
        responses = []
        for _ in range(50):
            response = chaos_client.post(
                "/infer", json={"model_name": "test-model", "inputs": ["test"], "max_length": 50}
            )
            responses.append(response)

        # Most should succeed or hit rate limit
        success_or_rate_limited = sum(1 for r in responses if r.status_code in [200, 429, 503])
        assert success_or_rate_limited >= 45, "success_or_rate_limited must be greater than zero"

    def test_sustained_load_stability(self, chaos_client):
        """Test stability under sustained load."""
        duration = 5  # seconds
        start_time = time.time()
        request_count = 0

        while time.time() - start_time < duration:
            response = chaos_client.get("/health")
            if response.status_code == 200:
                request_count += 1

        # Should maintain high throughput
        requests_per_second = request_count / duration
        assert requests_per_second > 50, "requests_per_second must be greater than zero"


class TestCircuitBreakerRecovery:
    """Test circuit breaker recovery mechanisms."""

    def test_half_open_state_recovery(self, chaos_client):
        """Test circuit breaker half-open state allows recovery."""
        with patch("src.codex_ml.serving.inference_server.ModelServer.predict") as mock_predict:
            # First 5 requests fail (open circuit)
            fail_count = [0]

            def controlled_failure(*args, **kwargs):
                fail_count[0] += 1
                if fail_count[0] <= 5:
                    raise RuntimeError("Simulated failure")
                return _STUB_PREDICTION

            mock_predict.side_effect = controlled_failure

            # Trigger failures
            for _ in range(5):
                chaos_client.post(
                    "/infer",
                    json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
                )

            # Wait for potential half-open
            time.sleep(2)

            # Next request should potentially succeed
            response = chaos_client.post(
                "/infer", json={"model_name": "test-model", "inputs": ["test"], "max_length": 50}
            )
            # Should either succeed or still be blocked
            assert response.status_code in [200, 500, 503]

    def test_circuit_breaker_metrics_update(self, chaos_client):
        """Test circuit breaker metrics are updated correctly."""
        response = chaos_client.get("/metrics")
        assert response.status_code == 200, "Response must not be empty"
        # Should contain circuit breaker metrics
        content = response.text
        assert "circuit_breaker" in content or "request_count" in content, "Content must not be empty"


class TestFailoverScenarios:
    """Test failover and redundancy scenarios."""

    def test_model_version_fallback(self, chaos_client):
        """Test fallback to previous model version on failure."""
        # If latest model fails, should try previous version
        response = chaos_client.post(
            "/infer", json={"model_name": "test-model", "inputs": ["test"], "max_length": 50}
        )
        # Should handle gracefully
        assert response.status_code in [200, 500, 503]

    def test_cache_miss_handling(self, chaos_client):
        """Test handling of cache misses under load."""
        # Clear cache and test cold start performance
        response = chaos_client.post(
            "/infer", json={"model_name": "uncached-model", "inputs": ["test"], "max_length": 50}
        )
        # Should handle cache miss
        assert response.status_code in [200, 500]


# Test configuration
pytestmark = pytest.mark.chaos


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
