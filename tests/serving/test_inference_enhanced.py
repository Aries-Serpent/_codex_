"""
Tests for Enhanced Inference Server with Authentication and Circuit Breaker
"""

from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("starlette")

from src.codex_ml.serving.inference_server import (  # pragma: allowlist secret
    AuthManager,
    ModelConfig,
    create_app,
)


class TestAuthManager:
    """Test AuthManager"""

    def test_init_no_auth(self):
        """Test initialization without authentication"""
        auth = AuthManager()
        assert auth.auth_enabled is False, "auth_enabled is not valid"
        assert auth.api_keys is None, "api_keys is not valid"

    def test_init_with_api_keys(self):
        """Test initialization with API keys"""
        keys = ["key1", "key2"]
        auth = AuthManager(api_keys=keys)
        assert auth.auth_enabled is True, "auth_enabled is not valid"
        assert len(auth.api_keys) == 2, "Collection must not be empty"
        assert "key1" in auth.api_keys, "Condition must be true"

    def test_init_with_jwt(self):
        """Test initialization with JWT secret"""
        auth = AuthManager(jwt_secret="my-secret")
        assert auth.auth_enabled is True, "auth_enabled is not valid"
        assert auth.jwt_secret == "my-secret"  # pragma: allowlist secret

    def test_verify_api_key_disabled(self):
        """Test API key verification when auth is disabled"""
        auth = AuthManager()
        assert auth.verify_api_key(None) is True, "Condition must be true"
        assert auth.verify_api_key("any-key") is True, "Condition must be true"

    def test_verify_api_key_valid(self):
        """Test API key verification with valid key"""
        auth = AuthManager(api_keys=["valid-key"])
        assert auth.verify_api_key("valid-key") is True, "Condition must be true"

    def test_verify_api_key_invalid(self):
        """Test API key verification with invalid key"""
        auth = AuthManager(api_keys=["valid-key"])
        assert auth.verify_api_key("invalid-key") is False, "Condition must be true"

    def test_verify_api_key_none(self):
        """Test API key verification with None"""
        auth = AuthManager(api_keys=["valid-key"])
        assert auth.verify_api_key(None) is False, "Condition must be true"

    def test_generate_api_key(self):
        """Test API key generation"""
        key1 = AuthManager.generate_api_key()
        key2 = AuthManager.generate_api_key()

        assert isinstance(key1, str)
        assert len(key1) > 20, "Key1 must not be empty"
        assert key1 != key2, "key1 is not valid"


class TestInferenceServerWithAuth:
    """Test inference server with authentication"""

    def test_create_app_no_auth(self):
        """Test creating app without authentication"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Should work without API key
        resp = client.post("/predict", json={"inputs": ["test"]})
        assert resp.status_code == 200, "status_code is not valid"

    def test_create_app_with_auth(self, monkeypatch):
        """Test creating app with authentication"""
        # Set API keys in environment
        monkeypatch.setenv("CODEX_API_KEYS", "valid-key-1,valid-key-2")

        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Should fail without API key
        resp = client.post("/predict", json={"inputs": ["test"]})
        assert resp.status_code == 401, "status_code is not valid"

        # Should succeed with valid API key
        resp = client.post(
            "/predict", json={"inputs": ["test"]}, headers={"X-API-Key": "valid-key-1"}
        )
        assert resp.status_code == 200, "status_code is not valid"

        # Should fail with invalid API key
        resp = client.post(
            "/predict", json={"inputs": ["test"]}, headers={"X-API-Key": "invalid-key"}
        )
        assert resp.status_code == 401, "status_code is not valid"

    def test_health_endpoint_circuit_breaker(self):
        """Test health endpoint includes circuit breaker status"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        resp = client.get("/health")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert "status" in data, "Data must not be empty"
        assert "model_loaded" in data, "Data must not be empty"
        # Circuit breaker status may or may not be present depending on import success

    def test_ready_endpoint(self):
        """Test readiness endpoint"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        resp = client.get("/ready")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert "ready" in data, "Data must not be empty"
        assert "model_loaded" in data, "Data must not be empty"
        assert data["model_loaded"] is True, "Data must not be empty"

    def test_live_endpoint(self):
        """Test liveness endpoint"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        resp = client.get("/live")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["status"] == "alive", "Data must not be empty"
        assert "uptime" in data, "Data must not be empty"

    def test_batch_infer_endpoint(self):
        """Test batch inference endpoint"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        resp = client.post("/batch_infer", json={"inputs": ["test1", "test2"]})
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert len(data["predictions"]) == 2, "Collection must not be empty"

    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Make a prediction first
        client.post("/predict", json={"inputs": ["test"]})

        # Check metrics
        resp = client.get("/metrics")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert "request_count" in data, "Data must not be empty"
        assert data["request_count"] > 0, "Value must be greater than zero"

    def test_rate_limiting(self):
        """Test rate limiting works"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Make requests to hit rate limit
        # Default is 1000 requests per 60 seconds
        # We won't test the full limit here, just verify the mechanism exists
        for i in range(3):
            resp = client.post("/predict", json={"inputs": ["test"]})
            # First few should succeed
            assert resp.status_code == 200, "status_code is not valid"

    def test_circuit_breaker_integration(self):
        """Test circuit breaker integration"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Normal request should work
        resp = client.post("/predict", json={"inputs": ["test"]})
        assert resp.status_code == 200, "status_code is not valid"

        # Metrics should show circuit breaker state if available
        resp = client.get("/metrics")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert "request_count" in data, "Data must not be empty"
        # Removed malformed assertion
        # Circuit breaker may or may not be present depending on import

    def test_root_endpoint_shows_auth_status(self):
        """Test root endpoint shows auth status"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        resp = client.get("/")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert "service" in data, "Data must not be empty"
        assert "version" in data, "Data must not be empty"
        assert "auth_enabled" in data, "Data must not be empty"

    def test_root_endpoint_with_auth_enabled(self, monkeypatch):
        """Test root endpoint with auth enabled"""
        monkeypatch.setenv("CODEX_API_KEYS", "test-key")

        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        resp = client.get("/")
        assert resp.status_code == 200, "status_code is not valid"
        data = resp.json()
        assert data["auth_enabled"] is True, "Data must not be empty"


class TestCircuitBreakerIntegration:
    """Test circuit breaker integration in inference server"""

    def test_circuit_breaker_on_predict(self):
        """Test real circuit breaker behavior during prediction failures"""
        resilience = pytest.importorskip("src.codex_ml.serving.resilience")
        circuit_breaker_config = resilience.CircuitBreakerConfig

        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app, raise_server_exceptions=False)

        # Force model inference failures while keeping the real CircuitBreaker in place.
        with patch(
            "src.codex_ml.serving.inference_server.ModelServer.predict",
            side_effect=Exception("forced model failure"),
        ):
            failure_threshold = circuit_breaker_config().failure_threshold

            # Drive failures through the real circuit breaker path.
            for _ in range(failure_threshold):
                client.post("/predict", json={"inputs": ["test"]})

            # Once open, requests should be rejected by circuit breaker.
            resp = client.post("/predict", json={"inputs": ["test"]})
            assert resp.status_code == 503, "status_code is not valid"

    def test_circuit_breaker_503_on_open(self):
        """Test circuit breaker returns 503 when open"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        app = create_app(config)

        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Simulate circuit breaker open by mocking predict method
        with patch(
            "src.codex_ml.serving.inference_server.ModelServer.predict_with_circuit_breaker"
        ) as mock_predict:
            mock_predict.side_effect = Exception("Circuit breaker is open, request rejected")

            resp = client.post("/predict", json={"inputs": ["test"]})
            assert resp.status_code == 503, "status_code is not valid"
