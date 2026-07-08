"""
Integration Tests for Inference Serving
Tests FastAPI endpoints with TestClient
"""

import time

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

# Try to import FastAPI components
try:
    from src.codex_ml.serving.inference_server import (
        ModelServer,
        RateLimiter,
        create_app,
    )

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestInferenceServerIntegration:
    """Integration tests for inference server endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200, "Response must not be empty"
        data = response.json()
        assert "service" in data, "Data must not be empty"
        assert "version" in data, "Data must not be empty"

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200, "Response must not be empty"
        data = response.json()
        assert data["status"] == "healthy", "Data must not be empty"
        assert "uptime" in data, "Data must not be empty"
        assert isinstance(data["uptime"], (int, float))

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200, "Response must not be empty"
        data = response.json()
        assert "request_count" in data, "Data must not be empty"
        assert isinstance(data["request_count"], int)

    def test_predict_endpoint_valid(self, client):
        """Test prediction with valid input"""
        payload = {"inputs": ["test input 1", "test input 2"], "model_name": "default"}
        response = client.post("/predict", json=payload)
        assert response.status_code == 200, "Response must not be empty"
        data = response.json()
        assert "predictions" in data, "Data must not be empty"
        assert len(data["predictions"]) == 2, "Collection must not be empty"

    def test_predict_endpoint_validation(self, client):
        """Test input validation on predict endpoint"""
        # Test batch size limit
        large_batch = {"inputs": ["test"] * 101}  # MAX_BATCH_SIZE = 100
        response = client.post("/predict", json=large_batch)
        assert response.status_code == 400, "Response must not be empty"
        assert "batch size" in response.json()["detail"].lower(), "Response must not be empty"

        # Test input length limit
        long_input = {"inputs": ["x" * 10001]}  # MAX_INPUT_LENGTH = 10000
        response = client.post("/predict", json=long_input)
        assert response.status_code == 400, "Response must not be empty"
        assert "input length" in response.json()["detail"].lower(), "Response must not be empty"

    def test_rate_limiting(self, client):
        """Test rate limiting enforcement"""
        # Make many requests quickly
        responses = []
        for _ in range(10):
            response = client.post("/predict", json={"inputs": ["test"]})
            responses.append(response.status_code)

        # All should succeed (rate limit is 1000/min)
        assert all(code == 200 for code in responses), "Response must not be empty"

    def test_error_handling(self, client):
        """Test error handling for invalid requests"""
        # Missing required field
        response = client.post("/predict", json={})
        assert response.status_code == 422, "Response must not be empty"

        # Invalid JSON
        response = client.post(
            "/predict", data="invalid json", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, "Response must not be empty"

    def test_concurrent_requests(self, client):
        """Test handling multiple concurrent requests"""
        import concurrent.futures

        def make_request():
            response = client.post("/predict", json={"inputs": ["test"]})
            return response.status_code

        # Send 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(code == 200 for code in results), "Result must not be empty"

    def test_health_check_persistence(self, client):
        """Test that health check shows increasing uptime"""
        response1 = client.get("/health")
        uptime1 = response1.json()["uptime"]

        time.sleep(0.1)

        response2 = client.get("/health")
        uptime2 = response2.json()["uptime"]

        assert uptime2 > uptime1, "uptime2 must be greater than zero"

    def test_metrics_increment(self, client):
        """Test that metrics increment with requests"""
        # Get initial count
        response = client.get("/metrics")
        initial_count = response.json()["request_count"]

        # Make some requests
        for _ in range(5):
            client.post("/predict", json={"inputs": ["test"]})

        # Check count increased
        response = client.get("/metrics")
        final_count = response.json()["request_count"]

        assert final_count > initial_count, "final_count must be positive"


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestModelServerIntegration:
    """Integration tests for ModelServer"""

    def test_model_loading(self):
        """Test model server can load models"""
        server = ModelServer()

        # Load default model
        model = server.load_model()
        assert model is not None, "model must be initialized"

    def test_model_caching(self):
        """Test that models are cached"""
        server = ModelServer()

        # Load same model twice
        model1 = server.load_model()
        model2 = server.load_model()

        # Should be same instance (both reference self.model)
        assert model1 is model2, "model1 is not valid"

    def test_prediction(self):
        """Test making predictions"""
        server = ModelServer()
        server.load_model()

        predictions = server.predict(["test input"])
        assert len(predictions) == 1, "Predictions must not be empty"


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestRateLimiterIntegration:
    """Integration tests for RateLimiter"""

    def test_rate_limiter_allows_requests(self):
        """Test rate limiter allows requests under limit"""
        limiter = RateLimiter(max_requests=10, window_seconds=60)

        # Should allow multiple requests
        for _ in range(10):
            assert limiter.is_allowed("test_ip"), "Condition must be true"

    def test_rate_limiter_blocks_excess(self):
        """Test rate limiter blocks requests over limit"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)

        # Allow first 5
        for _ in range(5):
            assert limiter.is_allowed("test_ip"), "Condition must be true"

        # Block 6th
        assert not limiter.is_allowed("test_ip"), "Condition must be true"

    def test_rate_limiter_window_reset(self):
        """Test rate limiter resets after window"""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # Use up limit
        assert limiter.is_allowed("test_ip"), "Condition must be true"
        assert limiter.is_allowed("test_ip"), "Condition must be true"
        assert not limiter.is_allowed("test_ip"), "Condition must be true"

        # Wait for window to reset
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.is_allowed("test_ip"), "Condition must be true"

    def test_rate_limiter_per_ip(self):
        """Test rate limiter tracks per IP"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        # IP1 uses up limit
        assert limiter.is_allowed("ip1"), "Condition must be true"
        assert limiter.is_allowed("ip1"), "Condition must be true"
        assert not limiter.is_allowed("ip1"), "Condition must be true"

        # IP2 should still be allowed
        assert limiter.is_allowed("ip2"), "Condition must be true"
        assert limiter.is_allowed("ip2"), "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
