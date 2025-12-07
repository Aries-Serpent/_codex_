"""
Tests for Model Loader

Tests model loading with caching, device placement, and validation
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.codex_ml.serving.model_loader import (
    DeviceType,
    ModelConfig,
    ModelLoader,
    QuantizationType,
)


class TestModelConfig:
    """Test ModelConfig"""

    def test_init_defaults(self):
        """Test initialization with defaults"""
        config = ModelConfig(model_name_or_path="test-model")
        assert config.model_name_or_path == "test-model"
        assert config.revision is None
        assert config.device == "cpu"
        assert config.quantization == "none"
        assert config.torch_dtype == "auto"
        assert config.low_cpu_mem_usage is True

    def test_init_custom(self):
        """Test initialization with custom values"""
        config = ModelConfig(
            model_name_or_path="gpt2",
            revision="main",
            device="cuda",
            quantization="int8",
            cache_dir="/tmp/cache",
            trust_remote_code=True,
            torch_dtype="float16",
        )
        assert config.model_name_or_path == "gpt2"
        assert config.revision == "main"
        assert config.device == "cuda"
        assert config.quantization == "int8"
        assert config.cache_dir == "/tmp/cache"
        assert config.trust_remote_code is True
        assert config.torch_dtype == "float16"

    def test_validate_invalid_device(self):
        """Test validation fails with invalid device"""
        with pytest.raises(ValueError, match="Invalid device"):
            ModelConfig(model_name_or_path="test", device="tpu")

    def test_validate_invalid_quantization(self):
        """Test validation fails with invalid quantization"""
        with pytest.raises(ValueError, match="Invalid quantization"):
            ModelConfig(model_name_or_path="test", quantization="int4")

    def test_validate_invalid_dtype(self):
        """Test validation fails with invalid torch_dtype"""
        with pytest.raises(ValueError, match="Invalid torch_dtype"):
            ModelConfig(model_name_or_path="test", torch_dtype="float64")

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = ModelConfig(
            model_name_or_path="test-model", revision="v1.0", device="cpu", quantization="fp16"
        )
        config_dict = config.to_dict()
        assert config_dict["model_name_or_path"] == "test-model"
        assert config_dict["revision"] == "v1.0"
        assert config_dict["device"] == "cpu"
        assert config_dict["quantization"] == "fp16"

    def test_get_cache_key(self):
        """Test cache key generation"""
        config1 = ModelConfig(model_name_or_path="test", device="cpu")
        config2 = ModelConfig(model_name_or_path="test", device="cpu")
        config3 = ModelConfig(model_name_or_path="test", device="cuda")

        # Same configs should have same key
        assert config1.get_cache_key() == config2.get_cache_key()
        # Different device should have different key
        assert config1.get_cache_key() != config3.get_cache_key()

    def test_get_cache_key_with_revision(self):
        """Test cache key includes revision"""
        config1 = ModelConfig(model_name_or_path="test", revision="v1.0")
        config2 = ModelConfig(model_name_or_path="test", revision="v2.0")

        assert config1.get_cache_key() != config2.get_cache_key()


class TestModelLoader:
    """Test ModelLoader"""

    def test_init(self):
        """Test initialization"""
        loader = ModelLoader(cache_size=5)
        assert loader.cache_size == 5
        assert len(loader.cache) == 0
        assert len(loader.cache_order) == 0

    def test_cache_hit(self):
        """Test cache hit returns cached model"""
        loader = ModelLoader(cache_size=2)

        # Load model first time
        config = ModelConfig(model_name_or_path="test-model")
        with patch.object(loader, "_load_from_source") as mock_load:
            mock_load.return_value = {"type": "stub", "model": "test"}
            result1 = loader.load_model(config)

        assert mock_load.call_count == 1

        # Load same model again - should hit cache
        with patch.object(loader, "_load_from_source") as mock_load:
            mock_load.return_value = {"type": "stub", "model": "test"}
            result2 = loader.load_model(config)

        # Should not call _load_from_source again
        assert mock_load.call_count == 0
        # Should return same data
        assert result1 == result2

    def test_cache_eviction(self):
        """Test LRU cache eviction"""
        loader = ModelLoader(cache_size=2)

        # Load 3 models - third should evict first
        configs = [
            ModelConfig(model_name_or_path=f"model-{i}") for i in range(3)
        ]

        for i, config in enumerate(configs):
            with patch.object(loader, "_load_from_source") as mock_load:
                mock_load.return_value = {"type": "stub", "model": f"model-{i}"}
                loader.load_model(config)

        # Cache should have 2 models (last two)
        assert len(loader.cache) == 2
        # First model should be evicted
        cache_key_0 = configs[0].get_cache_key()
        assert cache_key_0 not in loader.cache

    def test_load_from_dict_config(self):
        """Test loading with dict config"""
        loader = ModelLoader()
        config_dict = {"model_name_or_path": "test-model", "device": "cpu"}

        with patch.object(loader, "_load_from_source") as mock_load:
            mock_load.return_value = {"type": "stub"}
            result = loader.load_model(config_dict)

        assert mock_load.called
        assert result["type"] == "stub"

    def test_clear_cache(self):
        """Test clearing cache"""
        loader = ModelLoader()

        # Load a model
        config = ModelConfig(model_name_or_path="test-model")
        with patch.object(loader, "_load_from_source") as mock_load:
            mock_load.return_value = {"type": "stub"}
            loader.load_model(config)

        assert len(loader.cache) == 1

        # Clear cache
        loader.clear_cache()
        assert len(loader.cache) == 0
        assert len(loader.cache_order) == 0
        assert len(loader.load_times) == 0

    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        loader = ModelLoader(cache_size=5)

        # Load a model
        config = ModelConfig(model_name_or_path="test-model")
        with patch.object(loader, "_load_from_source") as mock_load:
            mock_load.return_value = {"type": "stub"}
            loader.load_model(config)

        stats = loader.get_cache_stats()
        assert stats["cache_size"] == 1
        assert stats["max_size"] == 5
        assert len(stats["cached_models"]) == 1
        assert len(stats["load_times"]) == 1

    def test_load_local_nonexistent(self):
        """Test loading from nonexistent local path"""
        loader = ModelLoader()
        config = ModelConfig(model_name_or_path="/nonexistent/path")

        with pytest.raises(RuntimeError, match="Model loading failed"):
            loader.load_model(config)

    def test_load_local_existing(self):
        """Test loading from existing local path"""
        loader = ModelLoader()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a model directory
            model_dir = Path(tmpdir) / "model"
            model_dir.mkdir()
            (model_dir / "config.json").write_text("{}")

            config = ModelConfig(model_name_or_path=str(model_dir))
            result = loader.load_model(config)

            assert result["type"] == "local"
            assert result["path"] == str(model_dir)
            assert result["device"] == "cpu"

    def test_validate_checkpoint_dir_valid(self):
        """Test checkpoint validation with valid directory"""
        loader = ModelLoader()

        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "model"
            model_dir.mkdir()
            (model_dir / "config.json").write_text("{}")

            assert loader.validate_checkpoint(model_dir) is True

    def test_validate_checkpoint_dir_missing_config(self):
        """Test checkpoint validation with missing config.json"""
        loader = ModelLoader()

        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "model"
            model_dir.mkdir()

            assert loader.validate_checkpoint(model_dir) is False

    def test_validate_checkpoint_file_valid(self):
        """Test checkpoint validation with valid file"""
        loader = ModelLoader()

        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmpfile:
            tmpfile.write(b"test")
            tmpfile.flush()
            path = Path(tmpfile.name)

        try:
            assert loader.validate_checkpoint(path) is True
        finally:
            path.unlink()

    def test_validate_checkpoint_file_invalid_extension(self):
        """Test checkpoint validation with invalid file extension"""
        loader = ModelLoader()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmpfile:
            tmpfile.write(b"test")
            tmpfile.flush()
            path = Path(tmpfile.name)

        try:
            assert loader.validate_checkpoint(path) is False
        finally:
            path.unlink()

    def test_validate_checkpoint_nonexistent(self):
        """Test checkpoint validation with nonexistent path"""
        loader = ModelLoader()
        assert loader.validate_checkpoint("/nonexistent/path") is False

    def test_load_huggingface_stub(self):
        """Test loading HuggingFace model (stub)"""
        pytest.importorskip("transformers")

        loader = ModelLoader()

        with patch("transformers.AutoConfig") as mock_auto_config:
            # Mock AutoConfig
            mock_config = Mock()
            mock_config.to_dict.return_value = {"hidden_size": 768}
            mock_auto_config.from_pretrained.return_value = mock_config

            config = ModelConfig(model_name_or_path="bert-base-uncased", revision="main")
            result = loader.load_model(config)

            assert result["type"] == "huggingface"
            assert result["model_name"] == "bert-base-uncased"
            assert result["revision"] == "main"
            assert "model_config" in result

    def test_get_torch_dtype_auto(self):
        """Test getting torch dtype for auto"""
        loader = ModelLoader()
        dtype = loader._get_torch_dtype("auto")
        assert dtype is None

    def test_get_torch_dtype_float16(self):
        """Test getting torch dtype for float16"""
        pytest.importorskip("torch")

        loader = ModelLoader()
        import torch

        dtype = loader._get_torch_dtype("float16")
        assert dtype == torch.float16


class TestEnums:
    """Test enum definitions"""

    def test_device_type_enum(self):
        """Test DeviceType enum"""
        assert DeviceType.CPU.value == "cpu"
        assert DeviceType.CUDA.value == "cuda"
        assert DeviceType.MPS.value == "mps"

    def test_quantization_type_enum(self):
        """Test QuantizationType enum"""
        assert QuantizationType.NONE.value == "none"
        assert QuantizationType.INT8.value == "int8"
        assert QuantizationType.FP16.value == "fp16"
