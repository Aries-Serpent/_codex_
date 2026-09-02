"""Tests for safe model device placement."""

import sys

import pytest

pytest.importorskip("torch")


import torch
import torch.nn as nn
from codex.rag.utils import safe_model_to_device

# PyTorch 2.x (<2.2.0) has an isinstance bug with Python 3.12 union types
# that triggers when creating nn.LayerNorm or similar modules.
# DR-003: guard tightened to torch < 2.2.0; CI uses torch >= 2.2.0 so tests run.
_TORCH_312_BUG = False
try:
    _torch_ver = tuple(int(x) for x in torch.__version__.split(".")[:2])
    _TORCH_312_BUG = sys.version_info >= (3, 12) and _torch_ver < (2, 2)
except (ImportError, AttributeError, ValueError):
    _TORCH_312_BUG = False  # torch not installed; PyTorch/Python 3.12 bug cannot apply


class SimpleModel(nn.Module):

    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 10)
        self.bn = nn.BatchNorm1d(10)

    def forward(self, x):
        return self.bn(self.linear(x))

    def __call__(self, *args, **kwargs):
        """Allow model(x) syntax by delegating to forward()."""
        return self.forward(*args, **kwargs)


class TestSafeModelToDevice:
    """Test suite for safe_model_to_device function."""

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_cpu_to_cpu(self):
        """Test moving CPU model to CPU (no-op)."""
        model = SimpleModel()
        result = safe_model_to_device(model, "cpu")

        assert result is not None, "result must be initialized"
        assert all(p.device.type == "cpu" for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cpu_to_cuda(self):
        """Test moving CPU model to CUDA."""
        model = SimpleModel()
        result = safe_model_to_device(model, "cuda:0")

        assert all(p.device.type == "cuda" for p in result.parameters()), "Result must not be empty"
        assert all(p.device.index == 0 for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_to_cpu(self):
        """Test moving CUDA model to CPU."""
        model = SimpleModel().to("cuda:0")
        result = safe_model_to_device(model, "cpu")

        assert all(p.device.type == "cpu" for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_with_dtype_conversion(self):
        """Test device placement with dtype conversion."""
        model = SimpleModel()
        result = safe_model_to_device(model, "cpu", dtype=torch.float16)

        assert all(p.device.type == "cpu" for p in result.parameters()), "Result must not be empty"
        assert all(p.dtype == torch.float16 for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_meta_tensor_to_cpu(self):
        """Test meta tensor conversion to CPU."""
        # Create model with meta tensors
        with torch.device("meta"):
            model = SimpleModel()

        # Verify model has meta tensors
        assert any(p.is_meta for p in model.parameters()), "Condition must be true"

        # Should not raise NotImplementedError
        result = safe_model_to_device(model, "cpu")

        # Verify materialized on CPU
        assert all(not p.is_meta for p in result.parameters()), "Result must not be empty"
        assert all(p.device.type == "cpu" for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_meta_tensor_to_cuda(self):
        """Test meta tensor conversion to CUDA."""
        with torch.device("meta"):
            model = SimpleModel()

        result = safe_model_to_device(model, "cuda:0")

        assert all(not p.is_meta for p in result.parameters()), "Result must not be empty"
        assert all(p.device.type == "cuda" for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_meta_tensor_with_dtype(self):
        """Test meta tensor conversion with dtype."""
        with torch.device("meta"):
            model = SimpleModel()

        result = safe_model_to_device(model, "cpu", dtype=torch.float16)

        assert all(not p.is_meta for p in result.parameters()), "Result must not be empty"
        assert all(p.dtype == torch.float16 for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_non_blocking_transfer(self):
        """Test non-blocking device transfer."""
        model = SimpleModel()
        result = safe_model_to_device(model, "cpu", non_blocking=True)

        # Should complete without error
        assert result is not None, "result must be initialized"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_invalid_device_type(self):
        """Test error handling for invalid device."""
        model = SimpleModel()

        with pytest.raises((RuntimeError, ValueError)):
            safe_model_to_device(model, "invalid_device")

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_non_module_input(self):
        """Test non-Module input with .to() is handled gracefully."""
        not_a_model = torch.randn(10, 10)

        # Tensors have .to() and lack .parameters(), so safe_model_to_device
        # returns them as-is (has_meta_tensors returns None).
        result = safe_model_to_device(not_a_model, "cpu")
        assert result is not None, "result must be initialized"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_device_string_formats(self):
        """Test various device string formats."""
        model = SimpleModel()

        # Test different string formats
        for device in ["cpu", torch.device("cpu")]:
            result = safe_model_to_device(model, device)
            assert all(p.device.type == "cpu" for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_specific_gpu_selection(self):
        """Test moving to specific GPU."""
        if torch.cuda.device_count() < 2:
            pytest.skip("Multiple GPUs required")

        model = SimpleModel()
        result = safe_model_to_device(model, "cuda:1")

        assert all(p.device.index == 1 for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_batchnorm_buffers_moved(self):
        """Test that buffers (e.g., BatchNorm stats) are moved."""
        model = SimpleModel()

        # Initialize BatchNorm running stats
        x = torch.randn(32, 10)
        model.eval()
        with torch.no_grad():
            model(x)

        # Move model
        result = safe_model_to_device(model, "cpu")

        # Check buffers moved
        assert all(b.device.type == "cpu" for b in result.buffers()), "Result must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_mixed_precision_workflow(self):
        """Test typical mixed precision workflow."""
        model = SimpleModel()

        # FP32 → FP16 on CPU
        model = safe_model_to_device(model, "cpu", dtype=torch.float16)
        assert all(p.dtype == torch.float16 for p in model.parameters()), "dtype is not valid"

        # FP16 → FP32 on CPU
        model = safe_model_to_device(model, "cpu", dtype=torch.float32)
        assert all(p.dtype == torch.float32 for p in model.parameters()), "dtype is not valid"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_preserves_gradient_state(self):
        """Test that gradient state is preserved."""
        model = SimpleModel()

        # Set requires_grad
        for p in model.parameters():
            p.requires_grad = True

        result = safe_model_to_device(model, "cpu")

        # Verify requires_grad preserved
        assert all(p.requires_grad for p in result.parameters()), "Result must not be empty"

    @pytest.mark.skipif(
        _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
    )
    def test_model_training_mode_preserved(self):
        """Test that training mode is preserved."""
        model = SimpleModel()

        # Set to eval mode
        model.eval()
        result = safe_model_to_device(model, "cpu")
        assert not result.training, "Result must not be empty"

        # Set to train mode
        model.train()
        result = safe_model_to_device(model, "cpu")
        assert result.training, "Result must not be empty"


class TestRAGModuleDevicePlacement:
    """Test device placement in RAG modules."""

    def test_indexer_device_placement(self):
        """Test RAGIndexer device placement."""
        pytest.importorskip("sentence_transformers")
        from codex.rag.indexer import RAGIndexer

        indexer = RAGIndexer(device="cpu")
        assert indexer.device == "cpu", "device is not valid"
        if indexer.model is None:
            pytest.skip("SentenceTransformer model not available in this environment (offline CI)")
        # Model should be on CPU
        assert all(p.device.type == "cpu" for p in indexer.model.parameters()), "type is not valid"

    def test_embeddings_device_placement(self):
        """Test EmbeddingModel device placement."""
        pytest.importorskip("sentence_transformers")
        from codex.rag.embeddings import EmbeddingModel

        model = EmbeddingModel(device="cpu")
        assert model.device == "cpu", "device is not valid"

    def test_retriever_device_placement(self):
        """Test RAGRetriever device placement."""
        pytest.importorskip("sentence_transformers")
        from codex.rag.retriever import RAGRetriever

        retriever = RAGRetriever(device="cpu")
        assert retriever.device == "cpu", "device is not valid"

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_indexer_cuda_placement(self):
        """Test RAGIndexer CUDA placement."""
        pytest.importorskip("sentence_transformers")
        from codex.rag.indexer import RAGIndexer

        indexer = RAGIndexer(device="cuda:0")
        assert indexer.device == "cuda:0", "device is not valid"
        assert all(p.device.type == "cuda" for p in indexer.model.parameters()), "type is not valid"

    def test_dynamic_device_change(self):
        """Test dynamic device change in RAG modules."""
        pytest.importorskip("sentence_transformers")
        from codex.rag.indexer import RAGIndexer

        indexer = RAGIndexer(device="cpu")
        if indexer.model is None:
            pytest.skip("SentenceTransformer model not available in this environment (offline CI)")

        # Change device
        indexer.move_to_device("cpu")  # Stay on CPU
        assert indexer.device == "cpu", "device is not valid"
        assert all(p.device.type == "cpu" for p in indexer.model.parameters()), "type is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
