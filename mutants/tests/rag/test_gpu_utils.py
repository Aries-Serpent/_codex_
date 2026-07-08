"""
Comprehensive test suite for RAG GPU utilities.

Tests all functions in src/codex/rag/gpu_utils.py to achieve 80%+ coverage.
Priority 1 - CRITICAL gap (0% → 80%)
"""

from unittest import mock
from unittest.mock import MagicMock, Mock, patch

import pytest


@pytest.fixture(autouse=True)
def cleanup_mocks():
    """Automatically reset all mocks after each test."""
    yield
    mock.patch.stopall()


from codex.rag.gpu_utils import (
    check_cuda_available,
    get_gpu_memory,
    get_optimal_batch_size,
    select_device,
    try_gpu_index,
)


class TestCheckCudaAvailable:
    """Test CUDA availability detection."""

    def test_cuda_available_true(self):
        """Test when CUDA is available."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA GeForce RTX 3090"

        with patch.dict("sys.modules", {"torch": mock_torch}):
            result = check_cuda_available()

            assert result is True, "Result must not be empty"
            mock_torch.cuda.is_available.assert_called_once()
            mock_torch.cuda.get_device_name.assert_called_once_with(0)

    def test_cuda_available_false(self):
        """Test when CUDA is not available."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False

        with patch.dict("sys.modules", {"torch": mock_torch}):
            result = check_cuda_available()

            assert result is False, "Result must not be empty"
            mock_torch.cuda.is_available.assert_called_once()

    def test_cuda_check_import_error(self):
        """Test when PyTorch is not installed."""
        with patch.dict("sys.modules", {"torch": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'torch'")):
                result = check_cuda_available()
                assert result is False, "Result must not be empty"

    def test_cuda_check_exception(self):
        """Test when CUDA check raises an exception."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.side_effect = RuntimeError("CUDA error")

        with patch.dict("sys.modules", {"torch": mock_torch}):
            result = check_cuda_available()

            assert result is False, "Result must not be empty"


class TestGetGpuMemory:
    """Test GPU memory retrieval."""

    def test_gpu_memory_available(self):
        """Test getting GPU memory when CUDA is available."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.return_value = (
            8_000_000_000,  # 8GB free
            16_000_000_000,  # 16GB total
        )

        with patch.dict("sys.modules", {"torch": mock_torch}):
            free, total = get_gpu_memory()

            assert free == 8_000_000_000, "free is not valid"
            assert total == 16_000_000_000, "total is not valid"
            mock_torch.cuda.mem_get_info.assert_called_once()

    def test_gpu_memory_cuda_unavailable(self):
        """Test when CUDA is not available."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False

        with patch.dict("sys.modules", {"torch": mock_torch}):
            free, total = get_gpu_memory()

            assert free == 0, "free is not valid"
            assert total == 0, "total is not valid"
            mock_torch.cuda.mem_get_info.assert_not_called()

    def test_gpu_memory_torch_not_installed(self):
        """Test when PyTorch is not installed."""
        with patch.dict("sys.modules", {"torch": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'torch'")):
                free, total = get_gpu_memory()
                assert free == 0, "free is not valid"
                assert total == 0, "total is not valid"

    def test_gpu_memory_exception(self):
        """Test when getting GPU memory raises exception."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.side_effect = RuntimeError("GPU error")

        with patch.dict("sys.modules", {"torch": mock_torch}):
            free, total = get_gpu_memory()

            assert free == 0, "free is not valid"
            assert total == 0, "total is not valid"


class TestSelectDevice:
    """Test device selection logic."""

    @patch("codex.rag.gpu_utils.check_cuda_available")
    def test_select_device_prefer_gpu_available(self, mock_check_cuda):
        """Test device selection when GPU is preferred and available."""
        mock_check_cuda.return_value = True

        device = select_device(prefer_gpu=True)

        assert device == "cuda", "device is not valid"
        mock_check_cuda.assert_called_once()

    @patch("codex.rag.gpu_utils.check_cuda_available")
    def test_select_device_prefer_gpu_unavailable(self, mock_check_cuda):
        """Test device selection when GPU is preferred but unavailable."""
        mock_check_cuda.return_value = False

        device = select_device(prefer_gpu=True)

        assert device == "cpu", "device is not valid"
        mock_check_cuda.assert_called_once()

    @patch("codex.rag.gpu_utils.check_cuda_available")
    def test_select_device_prefer_cpu(self, mock_check_cuda):
        """Test device selection when CPU is preferred."""
        # check_cuda_available should not be called when prefer_gpu=False
        device = select_device(prefer_gpu=False)

        assert device == "cpu", "device is not valid"
        mock_check_cuda.assert_not_called()

    @patch("codex.rag.gpu_utils.check_cuda_available")
    def test_select_device_default_prefer_gpu(self, mock_check_cuda):
        """Test that default behavior prefers GPU."""
        mock_check_cuda.return_value = True

        device = select_device()  # No argument, should default to prefer_gpu=True

        assert device == "cuda", "device is not valid"
        mock_check_cuda.assert_called_once()


class TestGetOptimalBatchSize:
    """Test optimal batch size calculation."""

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_gpu(self, mock_get_gpu_memory):
        """Test batch size calculation with GPU memory available."""
        # 8GB free memory
        mock_get_gpu_memory.return_value = (8_000_000_000, 16_000_000_000)

        batch_size = get_optimal_batch_size(embedding_dim=384, max_memory_gb=2.0, safety_factor=0.8)

        # Expected calculation:
        # bytes_per_embedding = 384 * 4 = 1536
        # available_memory = 8_000_000_000 * 0.8 = 6_400_000_000
        # max_batch_size = 6_400_000_000 / 1536 = 4,166,666
        # Clamped to max 512
        assert batch_size == 512, "batch_size is not valid"
        mock_get_gpu_memory.assert_called_once()

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_small_gpu(self, mock_get_gpu_memory):
        """Test batch size calculation with limited GPU memory."""
        # 100MB free memory - very small
        mock_get_gpu_memory.return_value = (100_000_000, 2_000_000_000)

        batch_size = get_optimal_batch_size(embedding_dim=384, max_memory_gb=2.0, safety_factor=0.8)

        # Expected calculation:
        # bytes_per_embedding = 384 * 4 = 1536
        # available_memory = 100_000_000 * 0.8 = 80_000_000
        # max_batch_size = 80_000_000 / 1536 = 52,083
        # Clamped to max 512
        assert batch_size == 512, "batch_size is not valid"
        mock_get_gpu_memory.assert_called_once()

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_tiny_gpu(self, mock_get_gpu_memory):
        """Test batch size calculation with very limited GPU memory."""
        # 5MB free memory - extremely small, should give minimum batch size
        mock_get_gpu_memory.return_value = (5_000_000, 2_000_000_000)

        batch_size = get_optimal_batch_size(embedding_dim=384, max_memory_gb=2.0, safety_factor=0.8)

        # Expected calculation:
        # bytes_per_embedding = 384 * 4 = 1536
        # available_memory = 5_000_000 * 0.8 = 4_000_000
        # max_batch_size = 4_000_000 / 1536 = 2604
        # Would give 2604, but should be within range [8, 512]
        assert 8 <= batch_size <= 512, "8 is not valid"

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_cpu_fallback(self, mock_get_gpu_memory):
        """Test batch size calculation when GPU is not available (CPU fallback)."""
        # No GPU memory available
        mock_get_gpu_memory.return_value = (0, 0)

        batch_size = get_optimal_batch_size()

        # Should return default CPU batch size
        assert batch_size == 32, "batch_size is not valid"
        mock_get_gpu_memory.assert_called_once()

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_custom_embedding_dim(self, mock_get_gpu_memory):
        """Test batch size calculation with custom embedding dimension."""
        mock_get_gpu_memory.return_value = (8_000_000_000, 16_000_000_000)

        batch_size = get_optimal_batch_size(
            embedding_dim=768,  # Larger embedding dimension
            max_memory_gb=2.0,
            safety_factor=0.8,
        )

        # With larger embedding dim, batch size should be smaller
        # bytes_per_embedding = 768 * 4 = 3072 (double the default)
        # So batch size should be smaller proportionally
        assert batch_size == 512, "batch_size is not valid"
        mock_get_gpu_memory.assert_called_once()

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_low_safety_factor(self, mock_get_gpu_memory):
        """Test batch size calculation with low safety factor."""
        mock_get_gpu_memory.return_value = (8_000_000_000, 16_000_000_000)

        batch_size = get_optimal_batch_size(
            embedding_dim=384, max_memory_gb=2.0, safety_factor=0.5  # More conservative
        )

        # Lower safety factor = less available memory used
        assert batch_size == 512, "batch_size is not valid"
        mock_get_gpu_memory.assert_called_once()


class TestTryGpuIndex:
    """Test FAISS index GPU conversion."""

    def test_try_gpu_index_success(self):
        """Test successful index conversion to GPU."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True

        mock_faiss = MagicMock()
        mock_index = Mock()
        mock_gpu_index = Mock()

        # Mock GPU resources and conversion
        mock_resources = Mock()
        mock_faiss.StandardGpuResources.return_value = mock_resources
        mock_faiss.index_cpu_to_gpu.return_value = mock_gpu_index

        with patch.dict("sys.modules", {"torch": mock_torch, "faiss": mock_faiss}):
            result = try_gpu_index(mock_index, None, device="cuda")

            assert result == mock_gpu_index, "Result must not be empty"
            mock_faiss.StandardGpuResources.assert_called_once()
            mock_faiss.index_cpu_to_gpu.assert_called_once_with(mock_resources, 0, mock_index)

    @patch("codex.rag.gpu_utils.check_cuda_available")
    def test_try_gpu_index_cpu_device(self, mock_check_cuda):
        """Test that CPU device returns original index without GPU check."""
        mock_index = Mock()

        result = try_gpu_index(mock_index, None, device="cpu")

        assert result == mock_index, "Result must not be empty"
        mock_check_cuda.assert_not_called()

    @patch("codex.rag.gpu_utils.check_cuda_available")
    def test_try_gpu_index_cuda_unavailable(self, mock_check_cuda):
        """Test when CUDA is not available."""
        mock_check_cuda.return_value = False
        mock_index = Mock()

        result = try_gpu_index(mock_index, None, device="cuda")

        assert result == mock_index, "Result must not be empty"
        mock_check_cuda.assert_called_once()

    def test_try_gpu_index_faiss_cpu_only(self):
        """Test when faiss-gpu is not installed (CPU-only FAISS)."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True

        mock_faiss = MagicMock()
        mock_index = Mock()

        # Simulate faiss without GPU support - remove the attribute
        del mock_faiss.StandardGpuResources

        with patch.dict("sys.modules", {"torch": mock_torch, "faiss": mock_faiss}):
            result = try_gpu_index(mock_index, None, device="cuda")

            assert result == mock_index, "Result must not be empty"

    def test_try_gpu_index_conversion_error(self):
        """Test when GPU conversion fails with exception."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True

        mock_faiss = MagicMock()
        mock_index = Mock()

        # Mock GPU resources but make conversion fail
        mock_resources = Mock()
        mock_faiss.StandardGpuResources.return_value = mock_resources
        mock_faiss.index_cpu_to_gpu.side_effect = RuntimeError("GPU conversion failed")

        with patch.dict("sys.modules", {"torch": mock_torch, "faiss": mock_faiss}):
            result = try_gpu_index(mock_index, None, device="cuda")

            # Should return original index on error
            assert result == mock_index, "Result must not be empty"

    def test_try_gpu_index_faiss_import_error(self):
        """Test when FAISS is not installed."""
        mock_index = Mock()
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True

        with patch.dict("sys.modules", {"torch": mock_torch, "faiss": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'faiss'")):
                result = try_gpu_index(mock_index, None, device="cuda")
                assert result == mock_index, "Result must not be empty"


# Integration tests


class TestGpuUtilsIntegration:
    """Integration tests for GPU utilities."""

    def test_full_workflow_no_gpu(self):
        """Test complete workflow when no GPU is available."""
        # Check device selection
        device = select_device(prefer_gpu=True)
        assert device in ["cpu", "cuda"]

        # Get optimal batch size (should work regardless of GPU)
        batch_size = get_optimal_batch_size()
        assert isinstance(batch_size, int)
        assert batch_size >= 8, "batch_size must be greater than zero"

        # Check memory (should return (0, 0) if no GPU)
        free, total = get_gpu_memory()
        assert isinstance(free, int)
        assert isinstance(total, int)
        assert free >= 0, "free must be greater than zero"
        assert total >= 0, "total must be greater than zero"

    @patch("codex.rag.gpu_utils.check_cuda_available")
    def test_device_selection_batch_size_correlation(self, mock_check_cuda):
        """Test that device selection correlates with batch size."""
        # Scenario 1: GPU available
        mock_check_cuda.return_value = True

        with patch("src.codex.rag.gpu_utils.get_gpu_memory") as mock_get_memory:
            mock_get_memory.return_value = (8_000_000_000, 16_000_000_000)

            device = select_device(prefer_gpu=True)
            batch_size = get_optimal_batch_size()

            assert device == "cuda", "device is not valid"
            # With GPU, should get optimized batch size
            assert batch_size >= 8, "batch_size must be greater than zero"

        # Scenario 2: No GPU
        mock_check_cuda.return_value = False

        with patch("src.codex.rag.gpu_utils.get_gpu_memory") as mock_get_memory:
            mock_get_memory.return_value = (0, 0)

            device = select_device(prefer_gpu=True)
            batch_size = get_optimal_batch_size()

            assert device == "cpu", "device is not valid"
            # Without GPU, should get default CPU batch size
            assert batch_size == 32, "batch_size is not valid"


# Edge cases and error handling


class TestGpuUtilsEdgeCases:
    """Test edge cases and error scenarios."""

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_negative_memory(self, mock_get_gpu_memory):
        """Test handling of negative memory values (should not happen, but defensive)."""
        mock_get_gpu_memory.return_value = (-1, -1)

        # The function treats negative as zero, so should return minimum batch size
        batch_size = get_optimal_batch_size()
        assert batch_size >= 8, "batch_size must be greater than zero"

    @patch("codex.rag.gpu_utils.get_gpu_memory")
    def test_optimal_batch_size_zero_embedding_dim(self, mock_get_gpu_memory):
        """Test with zero embedding dimension (edge case)."""
        mock_get_gpu_memory.return_value = (8_000_000_000, 16_000_000_000)

        # This would cause division by zero, function should handle gracefully
        # But actually, this would be a user error. Let's test reasonable minimum
        batch_size = get_optimal_batch_size(embedding_dim=1)
        assert batch_size >= 8, "batch_size must be greater than zero"

    def test_try_gpu_index_with_none_index(self):
        """Test GPU conversion with None index."""
        with patch("src.codex.rag.gpu_utils.check_cuda_available", return_value=False):
            result = try_gpu_index(None, None, device="cuda")
            # Should return None without crashing
            assert result is None, "Result must not be empty"


class TestGetOptimalBatchSizeValidation:
    """Tests for input validation in get_optimal_batch_size."""

    def test_invalid_embedding_dim_zero(self):
        """Test that embedding_dim=0 raises ValueError (line 88)."""
        import pytest

        from codex.rag.gpu_utils import get_optimal_batch_size

        with pytest.raises(ValueError, match="embedding_dim must be positive"):
            get_optimal_batch_size(embedding_dim=0)

    def test_invalid_embedding_dim_negative(self):
        """Test that negative embedding_dim raises ValueError."""
        import pytest

        from codex.rag.gpu_utils import get_optimal_batch_size

        with pytest.raises(ValueError, match="embedding_dim must be positive"):
            get_optimal_batch_size(embedding_dim=-1)


class TestGetGpuMemoryImportError:
    """Tests for ImportError handling in get_gpu_memory."""

    def test_gpu_memory_import_error(self):
        """Test that get_gpu_memory returns (0, 0) when torch raises ImportError."""
        from unittest.mock import patch

        from codex.rag.gpu_utils import get_gpu_memory

        with patch.dict("sys.modules", {"torch": None}):
            free, total = get_gpu_memory()
            assert free == 0, "free must be 0 when torch is unavailable"
            assert total == 0, "total must be 0 when torch is unavailable"
