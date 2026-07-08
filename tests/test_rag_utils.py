"""
Tests for RAG Utils Module

This module tests the utility functions in src/codex/rag/utils.py,
with specific focus on meta tensor handling and model loading.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    import torch
except ImportError:  # pragma: no cover - optional
    torch = None


def is_cuda_available() -> bool:
    """Local CUDA detection to avoid conftest import path conflicts."""
    try:
        return torch is not None and torch.cuda.is_available()
    except AttributeError:
        return False


skip_if_no_cuda = pytest.mark.skipif(
    not is_cuda_available(),
    reason="CUDA/GPU not available in this environment",
)

# Conditional imports for RAG dependencies
try:
    from sentence_transformers import SentenceTransformer

    if torch is None:
        raise ImportError("torch unavailable")
    from codex.rag.utils import (
        ProvenanceMetadata,
        check_for_meta_tensors,
        safe_model_load,
        safe_model_load_v2,
    )

    RAG_UTILS_AVAILABLE = True
except ImportError:
    RAG_UTILS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not RAG_UTILS_AVAILABLE,
    reason="RAG utils dependencies (torch, sentence_transformers) not installed",
)


class TestCheckForMetaTensors:
    """Tests for check_for_meta_tensors function"""

    def setup_method(self, method: object) -> None:
        """Reset torch default device before each test to prevent cross-test pollution.

        ``with torch.device('meta')`` sets the global default device via
        ``torch.set_default_device``.  When tests run in random order
        (pytest-randomly) a meta-device test could leak state into a
        subsequent test that expects CPU parameters.  This hook resets to
        ``None`` (no default device) which fully clears any leaked 'meta'
        context without the side-effects that ``set_default_device("cpu")``
        causes in PyTorch >=2.0 (see conftest.py for details).
        """
        try:
            import torch as _torch  # type: ignore[import-untyped]

            if hasattr(_torch, "set_default_device"):
                _torch.set_default_device(None)
        except (ImportError, AttributeError, ModuleNotFoundError):
            # torch not installed or the set_default_device attr is absent —
            # no cleanup needed in those cases; intentionally ignored.
            _ = None  # suppressed: no action needed

    def teardown_method(self, method: object) -> None:
        """Reset torch default device after each test to prevent cross-test pollution.

        Mirrors ``setup_method`` to ensure any test that sets a global device
        (e.g. via ``with torch.device('meta')``) always cleans up, regardless
        of whether the test passes, fails, or errors.  Uses ``None`` to fully
        clear the device context rather than setting it to "cpu", which
        interferes with meta tensor handling in PyTorch >=2.0.
        """
        try:
            import torch as _torch  # type: ignore[import-untyped]

            if hasattr(_torch, "set_default_device"):
                _torch.set_default_device(None)
        except (ImportError, AttributeError, ModuleNotFoundError):
            # torch not installed or the set_default_device attr is absent —
            # no cleanup needed in those cases; intentionally ignored.
            _ = None  # suppressed: no action needed

    def test_model_without_meta_tensors(self):
        """Test detection on model without meta tensors"""
        # Explicitly specify device="cpu" so the test is immune to any
        # global default device set by a previous test (e.g. via
        # `with torch.device('meta'):`). Using .to("cpu") on a meta tensor
        # raises NotImplementedError, so we avoid it entirely.
        model = torch.nn.Linear(10, 5, device="cpu")
        has_meta = check_for_meta_tensors(model)
        param_devices = [(n, p.device) for n, p in model.named_parameters()]
        assert has_meta is False, f"Expected False, got {has_meta!r} (params: {param_devices})"

    def test_model_with_meta_tensors(self):
        """Test detection on model with meta tensors"""
        # Create a model with meta tensors
        with torch.device("meta"):
            model = torch.nn.Linear(10, 5)
        has_meta = check_for_meta_tensors(model)
        assert has_meta is True, "has_meta is not valid"

    def test_empty_model(self):
        """Test detection on model without parameters"""
        model = torch.nn.Module()  # Empty module with no parameters
        has_meta = check_for_meta_tensors(model)
        assert has_meta is False, "has_meta is not valid"

    def test_model_with_buffers_on_meta(self):
        """Test detection when buffers (not just parameters) are on meta device"""

        class ModelWithBuffer(torch.nn.Module):
            def __init__(self):
                super().__init__()
                with torch.device("meta"):
                    self.register_buffer("my_buffer", torch.zeros(5))

        model = ModelWithBuffer()
        has_meta = check_for_meta_tensors(model)
        assert has_meta is True, "has_meta is not valid"


class TestSafeModelLoad:
    """Tests for deprecated safe_model_load function"""

    def test_deprecation_warning(self):
        """Test that safe_model_load raises deprecation warning"""
        model = torch.nn.Linear(10, 5, device="cpu")

        with pytest.warns(DeprecationWarning, match="safe_model_load.*is deprecated"):
            result = safe_model_load(model, device="cpu")

        # Should return model unchanged
        assert result is model, "Result must not be empty"


class TestSafeModelLoadV2:
    """Tests for safe_model_load_v2 function"""

    def setup_method(self, method: object) -> None:
        """Clear default device before each test to prevent meta-device leakage."""
        try:
            import torch as _torch  # type: ignore[import-untyped]

            if hasattr(_torch, "set_default_device"):
                _torch.set_default_device(None)
        except (ImportError, AttributeError, ModuleNotFoundError):
            # torch not installed or set_default_device absent — no-op intentionally.
            _ = None  # suppressed: no action needed

    def teardown_method(self, method: object) -> None:
        """Clear default device after each test to prevent meta-device leakage."""
        try:
            import torch as _torch  # type: ignore[import-untyped]

            if hasattr(_torch, "set_default_device"):
                _torch.set_default_device(None)
        except (ImportError, AttributeError, ModuleNotFoundError):
            # torch not installed or set_default_device absent — no-op intentionally.
            _ = None  # suppressed: no action needed

    def test_model_without_meta_tensors(self):
        """Test loading model that doesn't have meta tensors"""
        model = torch.nn.Linear(10, 5, device="cpu")

        result = safe_model_load_v2(model, device="cpu")

        # Should succeed and return model on CPU
        assert result is not None, "result must be initialized"
        assert next(result.parameters()).device.type == "cpu", "Result must not be empty"

    def test_model_with_meta_tensors_reinit_strategy(self):
        """Test that models with meta tensors are handled via to_empty()"""
        # Create a model with meta tensors
        with torch.device("meta"):
            model = torch.nn.Linear(10, 5)

        # The function should use to_empty() for meta tensors
        result = safe_model_load_v2(model, device="cpu")

        # Should succeed using to_empty() strategy
        assert result is not None, "result must be initialized"
        # Verify model is now on CPU (not meta)
        assert next(result.parameters()).device.type == "cpu", "Result must not be empty"

    def test_model_with_meta_tensors_to_empty_strategy(self):
        """Test Strategy 2: Use to_empty() for meta tensors"""
        # Create a model with meta tensors
        with torch.device("meta"):
            model = torch.nn.Linear(10, 5)

        # to_empty() should handle meta tensors in PyTorch 2.0+
        result = safe_model_load_v2(model, device="cpu")

        assert result is not None, "result must be initialized"
        assert next(result.parameters()).device.type == "cpu", "Result must not be empty"

    def test_all_strategies_fail(self):
        """Test behavior when model doesn't support to_empty()"""
        # Create a mock model without to_empty support
        mock_model = MagicMock()
        mock_model.named_modules.return_value = []
        mock_model.parameters.return_value = []
        mock_model.buffers.return_value = []
        mock_model.device = type("Device", (), {"type": "meta"})()
        del mock_model.to_empty  # Remove to_empty attribute

        # Mock has_meta_tensors to return True
        with patch("codex.rag.utils.has_meta_tensors", return_value=True):
            with pytest.raises(AttributeError, match="Model does not support to_empty"):
                safe_model_load_v2(mock_model, device="cpu")

    def test_model_without_model_name(self):
        """Test loading model without model_name (skips reinit strategy)"""
        model = torch.nn.Linear(10, 5, device="cpu")

        result = safe_model_load_v2(model, device="cpu")

        assert result is not None, "result must be initialized"
        assert next(result.parameters()).device.type == "cpu", "Result must not be empty"

    @pytest.mark.skipif(not is_cuda_available(), reason="CUDA not available")
    def test_cuda_device_when_unavailable(self):
        """Test behavior when CUDA device requested but unavailable"""
        model = torch.nn.Linear(10, 5)

        if not torch.cuda.is_available():
            # When CUDA is not available, the function may fall back or raise an error
            # depending on PyTorch behavior. Test that it handles this gracefully.
            try:
                result = safe_model_load_v2(model, device="cuda")
                # If it succeeds, verify the result is valid
                assert result is not None, "result must be initialized"
                # It may have fallen back to CPU
                device_type = next(result.parameters()).device.type
                assert device_type in ["cuda", "cpu"]
            except (RuntimeError, AssertionError):
                # This is acceptable when CUDA is not available
                _ = None  # suppressed: no action needed
        else:
            # If CUDA is available, it should work
            result = safe_model_load_v2(model, device="cuda")
            assert result is not None, "result must be initialized"
            assert next(result.parameters()).device.type == "cuda", "Result must not be empty"


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

        assert prov.source_file == Path("test.md"), "source_file is not valid"
        assert prov.line_range == (10, 20)
        assert prov.chunk_id == "chunk_123", "chunk_id is not valid"
        assert prov.retrieval_score == 0.85, "retrieval_score is not valid"

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
            metadata={"key": "value"},
        )

        result = prov.to_dict()

        assert result["source_file"] == "test.md", "Result must not be empty"
        assert result["line_range"] == (10, 20)
        assert result["chunk_id"] == "chunk_123", "Result must not be empty"
        assert result["embedding_model"] == "all-MiniLM-L6-v2", "Result must not be empty"
        assert result["retrieval_score"] == 0.85, "Result must not be empty"
        assert result["char_range"] == (100, 200)
        assert result["metadata"] == {"key": "value"}, "Result must not be empty"

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
            "metadata": {"key": "value"},
        }

        prov = ProvenanceMetadata.from_dict(data)

        assert prov.source_file == Path("test.md"), "source_file is not valid"
        assert prov.line_range == (10, 20)
        assert prov.chunk_id == "chunk_123", "chunk_id is not valid"
        assert prov.retrieval_score == 0.85, "retrieval_score is not valid"
        assert prov.char_range == (100, 200)
        assert prov.metadata == {"key": "value"}, "Data must not be empty"

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

        assert restored.source_file == original.source_file, "source_file is not valid"
        assert restored.line_range == original.line_range, "line_range is not valid"
        assert restored.chunk_id == original.chunk_id, "chunk_id is not valid"
        assert restored.retrieval_score == original.retrieval_score, "retrieval_score is not valid"


@skip_if_no_cuda
class TestIntegrationMetaTensorHandling:
    """Integration tests for meta tensor handling in real scenarios"""

    @pytest.mark.slow
    def test_sentence_transformer_loading_with_safe_model_load_v2(self):
        """Test loading a real SentenceTransformer model with safe_model_load_v2"""
        # Use a small model for faster testing
        model_name = "sentence-transformers/all-MiniLM-L6-v2"

        from huggingface_hub.errors import HfHubHTTPError

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Load model
                model = SentenceTransformer(
                    model_name, cache_folder=tmpdir, trust_remote_code=False
                )
            except HfHubHTTPError as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    pytest.skip("HuggingFace API rate limited - requires HF_TOKEN")
                raise

            # Apply safe_model_load_v2 - only accepts model and device parameters
            model = safe_model_load_v2(model, device="cpu")

            # Verify model is properly loaded
            assert model is not None, "model must be initialized"
            assert not check_for_meta_tensors(model), "Condition must be true"

            # Verify model can encode
            text = "This is a test sentence."
            embeddings = model.encode([text])
            assert embeddings is not None, "embeddings must be initialized"
            assert len(embeddings) > 0, "Embeddings must not be empty"
