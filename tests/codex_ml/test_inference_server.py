"""
Tests for Inference Server
"""
import pytest
import time

from src.codex_ml.serving.inference_server import (
    ModelServer,
    RateLimiter,
    MAX_BATCH_SIZE,
    MAX_INPUT_LENGTH,
)


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_init(self):
        """Test initialization"""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter.max_requests == 10
        assert limiter.window_seconds == 60
    
    def test_allows_requests_within_limit(self):
        """Test that requests within limit are allowed"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        for i in range(5):
            assert limiter.is_allowed("client1") is True
    
    def test_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        # Use up the limit
        for i in range(3):
            assert limiter.is_allowed("client1") is True
        
        # Next request should be blocked
        assert limiter.is_allowed("client1") is False
    
    def test_different_clients_independent(self):
        """Test that different clients have independent limits"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client2") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client2") is True
        
        # Both clients exhausted
        assert limiter.is_allowed("client1") is False
        assert limiter.is_allowed("client2") is False
    
    def test_window_expiration(self):
        """Test that old requests expire"""
        limiter = RateLimiter(max_requests=2, window_seconds=1)  # 1 second window
        
        # Use up limit
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed("client1") is True


class TestModelServer:
    """Test model server functionality"""
    
    def test_init(self):
        """Test initialization"""
        server = ModelServer(model_name="test-model")
        assert server.model_name == "test-model"
        assert server.model is None
        assert server.total_requests == 0
    
    def test_load_model(self):
        """Test model loading"""
        server = ModelServer()
        server.load_model()
        
        assert server.model is not None
        assert server.model["name"] == "default-model"
    
    def test_predict_without_model(self):
        """Test prediction without loaded model"""
        server = ModelServer()
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            server.predict(["test input"])
    
    def test_predict_with_model(self):
        """Test prediction with loaded model"""
        server = ModelServer()
        server.load_model()
        
        predictions = server.predict(["input1", "input2"])
        assert len(predictions) == 2
        assert all("label" in p for p in predictions)
        assert all("score" in p for p in predictions)
    
    def test_health_check_without_model(self):
        """Test health check without model"""
        server = ModelServer()
        health = server.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["model_loaded"] is False
        assert health["total_requests"] == 0
    
    def test_health_check_with_model(self):
        """Test health check with loaded model"""
        server = ModelServer()
        server.load_model()
        
        health = server.health_check()
        assert health["status"] == "healthy"
        assert health["model_loaded"] is True
        assert "uptime_seconds" in health
        assert health["uptime_seconds"] >= 0
    
    def test_rate_limiter_integration(self):
        """Test that server has rate limiter"""
        server = ModelServer()
        assert server.rate_limiter is not None
        assert isinstance(server.rate_limiter, RateLimiter)


class TestValidation:
    """Test input validation"""
    
    def test_max_batch_size(self):
        """Test batch size limit"""
        # This tests the constant definition
        assert MAX_BATCH_SIZE > 0
        assert MAX_BATCH_SIZE <= 1000  # Reasonable upper bound
    
    def test_max_input_length(self):
        """Test input length limit"""
        # This tests the constant definition
        assert MAX_INPUT_LENGTH > 0
        assert MAX_INPUT_LENGTH <= 100000  # Reasonable upper bound


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
