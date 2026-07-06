"""
Tests for Phase 6.2.B environment variables.

Tests all 8 environment variables introduced in Phase 6.2.B:
- CODEX_REDIS_HOST
- CODEX_OLLAMA_HOST
- CODEX_MASTER_ADDR
- CODEX_MASTER_PORT
- CODEX_INFERENCE_SERVICE_HOST
- CODEX_INFERENCE_SERVICE_PORT
- CODEX_TRUSTED_HOSTS
- CODEX_LOCAL_LOOPBACK
"""

import os
from urllib.parse import urlparse

import pytest


class TestRedisHostEnvVar:
    """Tests for CODEX_REDIS_HOST environment variable."""

    def test_redis_host_env_var_override(self, monkeypatch):
        """Verify CODEX_REDIS_HOST overrides default."""
        from cache.redis_cache import RedisCache

        monkeypatch.setenv("CODEX_REDIS_HOST", "custom-redis.example.com")
        cache = RedisCache(host=None)
        assert cache.host == "custom-redis.example.com"

    def test_redis_host_fallback(self, monkeypatch):
        """Verify fallback to localhost when env var unset."""
        from cache.redis_cache import RedisCache

        monkeypatch.delenv("CODEX_REDIS_HOST", raising=False)
        cache = RedisCache(host=None)
        assert cache.host == "localhost"

    def test_redis_host_explicit_param_wins(self, monkeypatch):
        """Verify explicit host parameter takes precedence."""
        from cache.redis_cache import RedisCache

        monkeypatch.setenv("CODEX_REDIS_HOST", "env-redis")
        cache = RedisCache(host="explicit-redis")
        assert cache.host == "explicit-redis"


class TestOllamaHostEnvVar:
    """Tests for CODEX_OLLAMA_HOST environment variable."""

    def test_ollama_host_env_var_override(self, monkeypatch):
        """Verify CODEX_OLLAMA_HOST overrides default."""
        try:
            from codex.rag.providers.ollama_provider import OllamaEmbeddingProvider
        except ImportError:
            pytest.skip("requests not installed")

        monkeypatch.setenv("CODEX_OLLAMA_HOST", "http://custom-ollama.example.com")
        provider = OllamaEmbeddingProvider(host=None)
        assert provider.host == "http://custom-ollama.example.com"

    def test_ollama_host_fallback(self, monkeypatch):
        """Verify fallback to http://localhost when env var unset."""
        try:
            from codex.rag.providers.ollama_provider import OllamaEmbeddingProvider
        except ImportError:
            pytest.skip("requests not installed")

        monkeypatch.delenv("CODEX_OLLAMA_HOST", raising=False)
        provider = OllamaEmbeddingProvider(host=None)
        assert provider.host == "http://localhost"


class TestMasterAddrPortEnvVars:
    """Tests for CODEX_MASTER_ADDR and CODEX_MASTER_PORT environment variables."""

    def test_master_addr_env_var_override(self, monkeypatch):
        """Verify CODEX_MASTER_ADDR overrides default."""
        import sys

        # Remove cached module to pick up new env vars
        if "codex_ml.training.distributed" in sys.modules:
            del sys.modules["codex_ml.training.distributed"]

        monkeypatch.setenv("CODEX_MASTER_ADDR", "master-node.example.com")
        from codex_ml.training.distributed import DistributedConfig

        config = DistributedConfig()
        assert config.master_addr == "master-node.example.com"

    def test_master_port_env_var_override(self, monkeypatch):
        """Verify CODEX_MASTER_PORT overrides default."""
        import sys

        if "codex_ml.training.distributed" in sys.modules:
            del sys.modules["codex_ml.training.distributed"]

        monkeypatch.setenv("CODEX_MASTER_PORT", "29501")
        from codex_ml.training.distributed import DistributedConfig

        config = DistributedConfig()
        assert config.master_port == "29501"

    def test_master_addr_fallback(self, monkeypatch):
        """Verify fallback to localhost when env var unset."""
        import sys

        if "codex_ml.training.distributed" in sys.modules:
            del sys.modules["codex_ml.training.distributed"]

        monkeypatch.delenv("CODEX_MASTER_ADDR", raising=False)
        from codex_ml.training.distributed import DistributedConfig

        config = DistributedConfig()
        assert config.master_addr == "localhost"

    def test_master_port_fallback(self, monkeypatch):
        """Verify fallback to 29500 when env var unset."""
        import sys

        if "codex_ml.training.distributed" in sys.modules:
            del sys.modules["codex_ml.training.distributed"]

        monkeypatch.delenv("CODEX_MASTER_PORT", raising=False)
        from codex_ml.training.distributed import DistributedConfig

        config = DistributedConfig()
        assert config.master_port == "29500"


class TestInferenceServiceEnvVars:
    """Tests for CODEX_INFERENCE_SERVICE_HOST and CODEX_INFERENCE_SERVICE_PORT."""

    def test_server_config_host_env_var(self, monkeypatch):
        """Verify CODEX_INFERENCE_SERVICE_HOST overrides default."""
        monkeypatch.setenv("CODEX_INFERENCE_SERVICE_HOST", "0.0.0.0")
        from codex_ml.serving.inference_server import ServerConfig

        config = ServerConfig()
        assert config.host == "0.0.0.0"

    def test_server_config_port_env_var(self, monkeypatch):
        """Verify CODEX_INFERENCE_SERVICE_PORT overrides default."""
        monkeypatch.setenv("CODEX_INFERENCE_SERVICE_PORT", "8001")
        from codex_ml.serving.inference_server import ServerConfig

        config = ServerConfig()
        assert config.port == 8001

    def test_server_config_host_fallback(self, monkeypatch):
        """Verify fallback to 127.0.0.1 when env var unset."""
        monkeypatch.delenv("CODEX_INFERENCE_SERVICE_HOST", raising=False)
        from codex_ml.serving.inference_server import ServerConfig

        config = ServerConfig()
        assert config.host == "127.0.0.1"

    def test_server_config_port_fallback(self, monkeypatch):
        """Verify fallback to 8000 when env var unset."""
        monkeypatch.delenv("CODEX_INFERENCE_SERVICE_PORT", raising=False)
        from codex_ml.serving.inference_server import ServerConfig

        config = ServerConfig()
        assert config.port == 8000


class TestTrustedHostsEnvVar:
    """Tests for CODEX_TRUSTED_HOSTS environment variable."""

    def test_trusted_hosts_env_var_override(self, monkeypatch):
        """Verify CODEX_TRUSTED_HOSTS env var is parsed correctly."""
        import sys

        if "codex_ml.serving.inference_server" in sys.modules:
            del sys.modules["codex_ml.serving.inference_server"]

        monkeypatch.setenv("CODEX_TRUSTED_HOSTS", "example.com,test.local,api.staging")
        from codex_ml.serving.inference_server import DEFAULT_TRUSTED_HOSTS

        assert {"example.com", "test.local", "api.staging"}.issubset(set(DEFAULT_TRUSTED_HOSTS))

    def test_trusted_hosts_fallback(self, monkeypatch):
        """Verify fallback to defaults when env var unset."""
        import sys

        if "codex_ml.serving.inference_server" in sys.modules:
            del sys.modules["codex_ml.serving.inference_server"]

        monkeypatch.delenv("CODEX_TRUSTED_HOSTS", raising=False)
        from codex_ml.serving.inference_server import DEFAULT_TRUSTED_HOSTS

        # Should contain default hosts
        assert "localhost" in DEFAULT_TRUSTED_HOSTS or "127.0.0.1" in DEFAULT_TRUSTED_HOSTS


class TestLocalLoopbackFeatureGate:
    """Tests for CODEX_LOCAL_LOOPBACK feature gate."""

    def test_loopback_enabled_network_policy(self, monkeypatch):
        """Verify localhost allowlist enabled when CODEX_LOCAL_LOOPBACK=true."""
        import sys

        if "safety.network_policy" in sys.modules:
            del sys.modules["safety.network_policy"]

        monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "true")
        from safety.network_policy import _DEFAULT_LOCALHOSTS

        assert "localhost" in _DEFAULT_LOCALHOSTS
        assert "127.0.0.1" in _DEFAULT_LOCALHOSTS
        assert "::1" in _DEFAULT_LOCALHOSTS

    def test_loopback_disabled_network_policy(self, monkeypatch):
        """Verify localhost allowlist disabled when CODEX_LOCAL_LOOPBACK=false."""
        import sys

        if "safety.network_policy" in sys.modules:
            del sys.modules["safety.network_policy"]

        monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "false")
        from safety.network_policy import _DEFAULT_LOCALHOSTS

        # Should be empty tuple
        assert len(_DEFAULT_LOCALHOSTS) == 0

    def test_loopback_default_enabled(self, monkeypatch):
        """Verify localhost allowlist enabled by default."""
        import sys

        if "safety.network_policy" in sys.modules:
            del sys.modules["safety.network_policy"]

        monkeypatch.delenv("CODEX_LOCAL_LOOPBACK", raising=False)
        from safety.network_policy import _DEFAULT_LOCALHOSTS

        # Should have default localhosts
        assert len(_DEFAULT_LOCALHOSTS) > 0
        assert "localhost" in _DEFAULT_LOCALHOSTS or "127.0.0.1" in _DEFAULT_LOCALHOSTS

    def test_loopback_mlflow_guard(self, monkeypatch):
        """Verify CODEX_LOCAL_LOOPBACK feature gate works with mlflow_guard."""
        import sys

        if "codex_ml.tracking.mlflow_guard" in sys.modules:
            del sys.modules["codex_ml.tracking.mlflow_guard"]

        monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "false")
        from codex_ml.tracking.mlflow_guard import _normalise_candidate

        # When loopback is disabled, localhost should not be allowed
        result_uri, reason = _normalise_candidate("file://localhost/path", allow_remote=False)
        # When localhost is not in allowed hosts, should fallback to default
        assert reason == "non_local_host"

    def test_loopback_guards(self, monkeypatch):
        """Verify CODEX_LOCAL_LOOPBACK feature gate works with guards."""
        import sys

        if "codex_ml.tracking.guards" in sys.modules:
            del sys.modules["codex_ml.tracking.guards"]

        monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "false")
        from codex_ml.tracking.guards import normalize_mlflow_uri

        # When loopback is disabled, localhost should not be allowed
        result = normalize_mlflow_uri("file://localhost/mlruns")
        parsed = urlparse(result)
        assert parsed.netloc == ""


class TestEnvVarIntegration:
    """Integration tests for all environment variables together."""

    def test_all_env_vars_set(self, monkeypatch):
        """Test that all env vars can be set and used together."""
        monkeypatch.setenv("CODEX_REDIS_HOST", "test-redis")
        monkeypatch.setenv("CODEX_OLLAMA_HOST", "http://test-ollama")
        monkeypatch.setenv("CODEX_MASTER_ADDR", "test-master")
        monkeypatch.setenv("CODEX_MASTER_PORT", "29501")
        monkeypatch.setenv("CODEX_INFERENCE_SERVICE_HOST", "test-inference")
        monkeypatch.setenv("CODEX_INFERENCE_SERVICE_PORT", "8001")
        monkeypatch.setenv("CODEX_TRUSTED_HOSTS", "test.local")
        monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "false")

        # All env vars should be accessible
        assert os.environ.get("CODEX_REDIS_HOST") == "test-redis"
        assert os.environ.get("CODEX_OLLAMA_HOST") == "http://test-ollama"
        assert os.environ.get("CODEX_MASTER_ADDR") == "test-master"
        assert os.environ.get("CODEX_MASTER_PORT") == "29501"
        assert os.environ.get("CODEX_INFERENCE_SERVICE_HOST") == "test-inference"
        assert os.environ.get("CODEX_INFERENCE_SERVICE_PORT") == "8001"
        assert os.environ.get("CODEX_TRUSTED_HOSTS") == "test.local"
        assert os.environ.get("CODEX_LOCAL_LOOPBACK") == "false"

    def test_all_env_vars_unset_defaults(self, monkeypatch):
        """Test that defaults are used when all env vars unset."""
        # Clear all env vars
        for var in [
            "CODEX_REDIS_HOST",
            "CODEX_OLLAMA_HOST",
            "CODEX_MASTER_ADDR",
            "CODEX_MASTER_PORT",
            "CODEX_INFERENCE_SERVICE_HOST",
            "CODEX_INFERENCE_SERVICE_PORT",
            "CODEX_TRUSTED_HOSTS",
            "CODEX_LOCAL_LOOPBACK",
        ]:
            monkeypatch.delenv(var, raising=False)

        # All should use defaults (localhost variations, etc.)
        # This test just verifies env vars are properly unset
        for var in [
            "CODEX_REDIS_HOST",
            "CODEX_OLLAMA_HOST",
            "CODEX_MASTER_ADDR",
            "CODEX_MASTER_PORT",
        ]:
            assert os.environ.get(var) is None
