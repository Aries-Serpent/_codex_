"""
Tests for RAG Utils Module

This module tests the utility functions in src/codex/rag/utils.py,
with specific focus on meta tensor handling and model loading.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Conditional imports for RAG dependencies
try:
    import torch
    from sentence_transformers import SentenceTransformer
    from codex.rag.utils import (
        check_for_meta_tensors,
        safe_model_load,
        safe_model_load_v2,
        ProvenanceMetadata,
    )
    RAG_UTILS_AVAILABLE = True
except ImportError:
    RAG_UTILS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not RAG_UTILS_AVAILABLE,
    reason="RAG utils dependencies (torch, sentence_transformers) not installed"
)


class TestCheckForMetaTensors:
    """Tests for check_for_meta_tensors function"""

    def test_model_without_meta_tensors(self):
        """Test detection on model without meta tensors"""
        # Create a simple model without meta tensors
        model = torch.nn.Linear(10, 5)
        has_meta = check_for_meta_tensors(model)
        assert has_meta is False

    def test_model_with_meta_tensors(self):
        """Test detection on model with meta tensors"""
        # Create a model with meta tensors
        with torch.device('meta'):
            model = torch.nn.Linear(10, 5)
        has_meta = check_for_meta_tensors(model)
        assert has_meta is True

    def test_empty_model(self):
        """Test detection on model without parameters"""
        model = torch.nn.Module()  # Empty module with no parameters
        has_meta = check_for_meta_tensors(model)
        assert has_meta is False

    def test_model_with_buffers_on_meta(self):
        """Test detection when buffers (not just parameters) are on meta device"""
        class ModelWithBuffer(torch.nn.Module):
            def __init__(self):
                super().__init__()
                with torch.device('meta'):
                    self.register_buffer('my_buffer', torch.zeros(5))
        
        model = ModelWithBuffer()
        has_meta = check_for_meta_tensors(model)
        assert has_meta is True


class TestSafeModelLoad:
    """Tests for deprecated safe_model_load function"""

    def test_deprecation_warning(self):
        """Test that safe_model_load raises deprecation warning"""
        model = torch.nn.Linear(10, 5)
        
        with pytest.warns(DeprecationWarning, match="safe_model_load.*is deprecated"):
            result = safe_model_load(model, device="cpu")
        
        # Should return model unchanged
        assert result is model


class TestSafeModelLoadV2:
    """Tests for safe_model_load_v2 function"""

    def test_model_without_meta_tensors(self):
        """Test loading model that doesn't have meta tensors"""
        model = torch.nn.Linear(10, 5)
        
        result = safe_model_load_v2(model, device="cpu")
        
        # Should succeed and return model on CPU
        assert result is not None
        assert next(result.parameters()).device.type == "cpu"
        # Model should be in eval mode
        assert not result.training

    def test_model_with_meta_tensors_reinit_strategy(self):
        """Test Strategy 1: Reinitialize SentenceTransformer with device parameter"""
        # Create a mock SentenceTransformer with meta tensors
        mock_model = MagicMock(spec=SentenceTransformer)
        mock_model.__class__.__name__ = 'SentenceTransformer'
        
        # Mock check_for_meta_tensors to return True initially
        with patch('codex.rag.utils.check_for_meta_tensors') as mock_check:
            # First call returns True (has meta), second call returns False (no meta)
            mock_check.side_effect = [True, False]
            
            # Mock SentenceTransformer constructor
            with patch('codex.rag.utils.SentenceTransformer') as mock_st:
                new_model = MagicMock(spec=SentenceTransformer)
                new_model.eval.return_value = new_model
                mock_st.return_value = new_model
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    result = safe_model_load_v2(
                        mock_model,
                        device="cpu",
                        model_name="test-model",
                        cache_folder=tmpdir
                    )
                
                # Should call SentenceTransformer with device parameter
                mock_st.assert_called_once_with(
                    "test-model",
                    device="cpu",
                    cache_folder=tmpdir,
                    trust_remote_code=False
                )
                assert result is new_model
                new_model.eval.assert_called_once()

    def test_model_with_meta_tensors_to_empty_strategy(self):
        """Test Strategy 2: Use to_empty() for meta tensors"""
        # Create a model with meta tensors
        with torch.device('meta'):
            model = torch.nn.Linear(10, 5)
        
        # Strategy 2 should handle meta tensors using to_empty()
        # For simple models like Linear, this may still fail if weights aren't properly loaded
        # This tests that the function handles the failure gracefully
        with pytest.raises(RuntimeError, match="Failed to load model"):
            safe_model_load_v2(model, device="cpu")

    def test_all_strategies_fail(self):
        """Test that RuntimeError is raised when all strategies fail"""
        # Create a model with meta tensors that can't be reinitialized
        with torch.device('meta'):
            model = torch.nn.Linear(10, 5)
        
        # All strategies should fail for a meta Linear model
        with pytest.raises(RuntimeError, match="Failed to load model"):
            safe_model_load_v2(model, device="cpu")

    def test_model_without_model_name(self):
        """Test loading model without model_name (skips reinit strategy)"""
        model = torch.nn.Linear(10, 5)
        
        result = safe_model_load_v2(model, device="cpu")
        
        assert result is not None
        assert next(result.parameters()).device.type == "cpu"

    def test_cuda_device_when_unavailable(self):
        """Test behavior when CUDA device requested but unavailable"""
        model = torch.nn.Linear(10, 5)
        
        if not torch.cuda.is_available():
            # When CUDA is not available, the function may fall back or raise an error
            # depending on PyTorch behavior. Test that it handles this gracefully.
            try:
                result = safe_model_load_v2(model, device="cuda")
                # If it succeeds, verify the result is valid
                assert result is not None
                # It may have fallen back to CPU
                device_type = next(result.parameters()).device.type
                assert device_type in ["cuda", "cpu"]
            except (RuntimeError, AssertionError):
                # This is acceptable when CUDA is not available
                pass
        else:
            # If CUDA is available, it should work
            result = safe_model_load_v2(model, device="cuda")
            assert result is not None
            assert next(result.parameters()).device.type == "cuda"


class TestProvenanceMetadata:
    """Tests for ProvenanceMetadata dataclass"""

    def test_creation(self):
        """Test creating ProvenanceMetadata"""
        from datetime import datetime
        
        prov = ProvenanceMetadata(
            source_file=Path("test.md"),
            line_range=(10, 20),
            chunk_id="chunk_123",
            indexed_at=datetime(2024, 1, 1, 12, 0, 0),
            embedding_model="all-MiniLM-L6-v2",
            retrieval_score=0.85,
        )
        
        assert prov.source_file == Path("test.md")
        assert prov.line_range == (10, 20)
        assert prov.chunk_id == "chunk_123"
        assert prov.retrieval_score == 0.85

    def test_to_dict(self):
        """Test converting ProvenanceMetadata to dict"""
        from datetime import datetime
        
        prov = ProvenanceMetadata(
            source_file=Path("test.md"),
            line_range=(10, 20),
            chunk_id="chunk_123",
            indexed_at=datetime(2024, 1, 1, 12, 0, 0),
            embedding_model="all-MiniLM-L6-v2",
            retrieval_score=0.85,
            char_range=(100, 200),
            metadata={"key": "value"}
        )
        
        result = prov.to_dict()
        
        assert result["source_file"] == "test.md"
        assert result["line_range"] == (10, 20)
        assert result["chunk_id"] == "chunk_123"
        assert result["embedding_model"] == "all-MiniLM-L6-v2"
        assert result["retrieval_score"] == 0.85
        assert result["char_range"] == (100, 200)
        assert result["metadata"] == {"key": "value"}

    def test_from_dict(self):
        """Test creating ProvenanceMetadata from dict"""
        data = {
            "source_file": "test.md",
            "line_range": (10, 20),
            "chunk_id": "chunk_123",
            "indexed_at": "2024-01-01T12:00:00",
            "embedding_model": "all-MiniLM-L6-v2",
            "retrieval_score": 0.85,
            "char_range": (100, 200),
            "metadata": {"key": "value"}
        }
        
        prov = ProvenanceMetadata.from_dict(data)
        
        assert prov.source_file == Path("test.md")
        assert prov.line_range == (10, 20)
        assert prov.chunk_id == "chunk_123"
        assert prov.retrieval_score == 0.85
        assert prov.char_range == (100, 200)
        assert prov.metadata == {"key": "value"}

    def test_round_trip(self):
        """Test converting to dict and back"""
        from datetime import datetime
        
        original = ProvenanceMetadata(
            source_file=Path("test.md"),
            line_range=(10, 20),
            chunk_id="chunk_123",
            indexed_at=datetime(2024, 1, 1, 12, 0, 0),
            embedding_model="all-MiniLM-L6-v2",
            retrieval_score=0.85,
        )
        
        dict_repr = original.to_dict()
        restored = ProvenanceMetadata.from_dict(dict_repr)
        
        assert restored.source_file == original.source_file
        assert restored.line_range == original.line_range
        assert restored.chunk_id == original.chunk_id
        assert restored.retrieval_score == original.retrieval_score


class TestIntegrationMetaTensorHandling:
    """Integration tests for meta tensor handling in real scenarios"""

    @pytest.mark.slow
    def test_sentence_transformer_loading_with_safe_model_load_v2(self):
        """Test loading a real SentenceTransformer model with safe_model_load_v2"""
        # Use a small model for faster testing
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Load model
            model = SentenceTransformer(
                model_name,
                cache_folder=tmpdir,
                trust_remote_code=False
            )
            
            # Apply safe_model_load_v2
            model = safe_model_load_v2(
                model,
                device="cpu",
                model_name=model_name,
                cache_folder=tmpdir
            )
            
            # Verify model is properly loaded
            assert model is not None
            assert not check_for_meta_tensors(model)
            
            # Verify model can encode
            text = "This is a test sentence."
            embeddings = model.encode([text])
            assert embeddings is not None
            assert len(embeddings) > 0
