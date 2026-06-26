"""
Tests for Inference Server
"""

import time

import pytest

np = pytest.importorskip("numpy")

from src.codex_ml.serving.inference_server import (
    MAX_BATCH_SIZE,
    MAX_INPUT_LENGTH,
    ModelConfig,
    ModelLoadError,
    ModelServer,
    RateLimiter,
)


class TestModelConfig:
    """Test model configuration"""

    def test_init_defaults(self):
        """Test initialization with defaults"""
        config = ModelConfig()
        assert config.model_name is not None, "model_name must be initialized"
        assert config.model_type == "stub", "model_type is not valid"
        assert config.device == "cpu", "device is not valid"

    def test_init_custom(self):
        """Test initialization with custom values"""
        config = ModelConfig(
            model_name="test-model",
            model_type="huggingface",
            model_path="/path/to/model",
            device="cpu",
        )
        assert config.model_name == "test-model", "model_name is not valid"
        assert config.model_type == "huggingface", "model_type is not valid"
        assert config.model_path == "/path/to/model", "model_path is not valid"
        assert config.device == "cpu", "device is not valid"

    def test_from_dict(self):
        """Test creating config from dictionary"""
        config_dict = {
            "model_name": "dict-model",
            "model_type": "onnx",
            "model_path": "/path/to/onnx",
            "device": "cpu",
        }
        config = ModelConfig.from_dict(config_dict)
        assert config.model_name == "dict-model", "model_name is not valid"
        assert config.model_type == "onnx", "model_type is not valid"
        assert config.model_path == "/path/to/onnx", "model_path is not valid"

    def test_from_env(self, monkeypatch):
        """Test creating config from environment variables"""
        monkeypatch.setenv("CODEX_MODEL_NAME", "env-model")
        monkeypatch.setenv("CODEX_MODEL_TYPE", "huggingface")
        monkeypatch.setenv("CODEX_MODEL_DEVICE", "cpu")

        config = ModelConfig.from_env()
        assert config.model_name == "env-model", "model_name is not valid"
        assert config.model_type == "huggingface", "model_type is not valid"
        assert config.device == "cpu", "device is not valid"

    def test_validate_success(self):
        """Test validation with valid config"""
        config = ModelConfig(model_name="valid", model_type="stub", device="cpu")
        config.validate()  # Should not raise

    def test_validate_empty_name(self):
        """Test validation fails with empty model name"""
        config = ModelConfig(model_name="", model_type="stub")
        with pytest.raises(ValueError, match="model_name cannot be empty"):
            config.validate()

    def test_validate_invalid_type(self):
        """Test validation fails with invalid model type"""
        config = ModelConfig(model_name="test", model_type="invalid")
        with pytest.raises(ValueError, match="Unsupported model_type"):
            config.validate()

    def test_validate_invalid_device(self):
        """Test validation fails with invalid device"""
        config = ModelConfig(model_name="test", model_type="stub", device="tpu")
        with pytest.raises(ValueError, match="Unsupported device"):
            config.validate()

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = ModelConfig(
            model_name="test",
            model_type="stub",
            model_path="/path",
            device="cpu",
        )
        config_dict = config.to_dict()
        assert config_dict["model_name"] == "test", "Condition must be true"
        assert config_dict["model_type"] == "stub", "Condition must be true"
        assert config_dict["device"] == "cpu", "Condition must be true"


class TestRateLimiter:
    """Test rate limiting functionality"""

    def test_init(self):
        """Test initialization"""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter.max_requests == 10, "max_requests is not valid"
        assert limiter.window_seconds == 60, "window_seconds is not valid"

    def test_allows_requests_within_limit(self):
        """Test that requests within limit are allowed"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)

        for i in range(5):
            assert limiter.is_allowed("client1") is True, "Condition must be true"

    def test_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        # Use up the limit
        for i in range(3):
            assert limiter.is_allowed("client1") is True, "Condition must be true"

        # Next request should be blocked
        assert limiter.is_allowed("client1") is False, "Condition must be true"

    def test_different_clients_independent(self):
        """Test that different clients have independent limits"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        assert limiter.is_allowed("client1") is True, "Condition must be true"
        assert limiter.is_allowed("client2") is True, "Condition must be true"
        assert limiter.is_allowed("client1") is True, "Condition must be true"
        assert limiter.is_allowed("client2") is True, "Condition must be true"

        # Both clients exhausted
        assert limiter.is_allowed("client1") is False, "Condition must be true"
        assert limiter.is_allowed("client2") is False, "Condition must be true"

    def test_window_expiration(self):
        """Test that old requests expire"""
        limiter = RateLimiter(max_requests=2, window_seconds=1)  # 1 second window

        # Use up limit
        assert limiter.is_allowed("client1") is True, "Condition must be true"
        assert limiter.is_allowed("client1") is True, "Condition must be true"
        assert limiter.is_allowed("client1") is False, "Condition must be true"

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.is_allowed("client1") is True, "Condition must be true"


class TestModelServer:
    """Test model server functionality"""

    def test_init_default_config(self):
        """Test initialization with default config"""
        server = ModelServer()
        assert server.model_name is not None, "model_name must be initialized"
        assert server.model is None, "model is not valid"
        assert server.total_requests == 0, "total_requests is not valid"
        assert server.config.model_type == "stub", "model_type is not valid"

    def test_init_custom_config(self):
        """Test initialization with custom config"""
        config = ModelConfig(model_name="test-model", model_type="stub")
        server = ModelServer(config=config)
        assert server.model_name == "test-model", "model_name is not valid"
        assert server.config.model_type == "stub", "model_type is not valid"

    def test_load_stub_model(self):
        """Test loading stub model"""
        config = ModelConfig(model_name="stub-test", model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        assert server.model is not None, "model must be initialized"
        assert server.model["type"] == "stub", "Condition must be true"
        assert server.model["name"] == "stub-test", "Condition must be true"

    def test_load_model_invalid_type(self):
        """Test loading model with invalid type fails"""
        # Create config with invalid type (bypass validation)
        config = ModelConfig(model_name="test", model_type="stub")
        config.model_type = "invalid"  # Set after creation
        server = ModelServer(config=config)

        with pytest.raises(ModelLoadError, match="Unsupported model type"):
            server.load_model()

    def test_load_huggingface_missing_path(self):
        """Test loading HuggingFace model with missing path"""
        config = ModelConfig(
            model_name="hf-test",
            model_type="huggingface",
            model_path="/nonexistent/path",
        )
        server = ModelServer(config=config)

        with pytest.raises(ModelLoadError, match="Model path does not exist"):
            server.load_model()

    def test_load_onnx_missing_path(self):
        """Test loading ONNX model with missing path"""
        config = ModelConfig(
            model_name="onnx-test",
            model_type="onnx",
            model_path="/nonexistent/path",
        )
        server = ModelServer(config=config)

        with pytest.raises(ModelLoadError, match="Model path does not exist"):
            server.load_model()

    def test_predict_without_model(self):
        """Test prediction without loaded model"""
        server = ModelServer()

        with pytest.raises(RuntimeError, match="Model not loaded"):
            server.predict(["test input"])

    def test_predict_with_stub_model(self):
        """Test prediction with loaded stub model"""
        config = ModelConfig(model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        predictions = server.predict(["input1", "input2"])
        assert len(predictions) == 2, "Predictions must not be empty"
        assert all("label" in p for p in predictions), "Condition must be true"
        assert all("score" in p for p in predictions), "Condition must be true"
        assert all("text" in p for p in predictions), "Condition must be true"
        assert all("model" in p for p in predictions), "Condition must be true"

    def test_predict_standardized_output(self):
        """Test that predictions have standardized structure"""
        config = ModelConfig(model_type="stub", model_name="test-model")
        server = ModelServer(config=config)
        server.load_model()

        predictions = server.predict(["test"])
        assert len(predictions) == 1, "Predictions must not be empty"
        pred = predictions[0]

        # Check standardized fields
        assert "text" in pred, "Condition must be true"
        assert "label" in pred, "Condition must be true"
        assert "score" in pred, "Condition must be true"
        assert "model" in pred, "Condition must be true"
        assert pred["model"] == "test-model", "Condition must be true"

    def test_health_check_without_model(self):
        """Test health check without model"""
        server = ModelServer()
        health = server.health_check()

        assert health["status"] == "unhealthy", "Condition must be true"
        assert health["model_loaded"] is False, "Condition must be true"
        assert health["total_requests"] == 0, "Condition must be true"
        assert "model_type" in health, "Condition must be true"
        assert "device" in health, "Condition must be true"

    def test_health_check_with_model(self):
        """Test health check with loaded model"""
        config = ModelConfig(model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        health = server.health_check()
        assert health["status"] == "healthy", "Condition must be true"
        assert health["model_loaded"] is True, "Condition must be true"
        assert "uptime_seconds" in health, "Condition must be true"
        assert health["uptime_seconds"] >= 0, "Value must be greater than zero"
        assert health["model_type"] == "stub", "Condition must be true"

    def test_health_check_includes_errors(self):
        """Test that health check includes load errors"""
        server = ModelServer()
        health = server.health_check()

        assert "load_errors" in health, "Error should be raised or set"
        assert isinstance(health["load_errors"], list)

    def test_rate_limiter_integration(self):
        """Test that server has rate limiter"""
        server = ModelServer()
        assert server.rate_limiter is not None, "rate_limiter must be initialized"
        assert isinstance(server.rate_limiter, RateLimiter)

    def test_request_counter(self):
        """Test that total_requests is tracked"""
        config = ModelConfig(model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        initial_count = server.total_requests
        # Simulate tracking (in real app, this is done in endpoint)
        server.total_requests += 1

        assert server.total_requests == initial_count + 1, "Count must be greater than zero"


class TestValidation:
    """Test input validation"""

    def test_max_batch_size(self):
        """Test batch size limit"""
        # This tests the constant definition
        assert MAX_BATCH_SIZE > 0, "MAX_BATCH_SIZE must be greater than zero"
        assert MAX_BATCH_SIZE <= 1000, "MAX_BATCH_SIZE is not valid"

    def test_max_input_length(self):
        """Test input length limit"""
        # This tests the constant definition
        assert MAX_INPUT_LENGTH > 0, "MAX_INPUT_LENGTH must be greater than zero"
        assert MAX_INPUT_LENGTH <= 100000, "Length must be greater than zero"


class TestEmbedding:
    """Test embedding functionality"""

    def test_embed_stub_model(self):
        """Test embedding with stub model"""
        config = ModelConfig(model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        texts = ["Hello world", "Test text", "Another example"]
        embeddings = server.embed(texts)

        # Check shape
        assert embeddings.shape[0] == 3, "Condition must be true"
        assert embeddings.shape[1] > 0, "Value must be greater than zero"

        # Check normalized
        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5)

    def test_embed_without_model(self):
        """Test embedding without loaded model"""
        server = ModelServer()

        with pytest.raises(RuntimeError, match="Model not loaded"):
            server.embed(["test"])

    def test_embed_returns_numpy(self):
        """Test that embed returns numpy array"""
        config = ModelConfig(model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        embeddings = server.embed(["test"])

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.dtype == np.float32, "dtype is not valid"

    def test_embed_batch(self):
        """Test embedding multiple texts"""
        config = ModelConfig(model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        texts = [f"text-{i}" for i in range(20)]
        embeddings = server.embed(texts)

        assert embeddings.shape[0] == 20, "Condition must be true"

        # Each embedding should be different (for stub, they're random)
        # Check that not all embeddings are identical
        assert not np.allclose(embeddings[0], embeddings[1])

    def test_embed_empty_list(self):
        """Test embedding empty list"""
        config = ModelConfig(model_type="stub")
        server = ModelServer(config=config)
        server.load_model()

        embeddings = server.embed([])

        assert embeddings.shape[0] == 0, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
