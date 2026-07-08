"""
Test HF Loader Module

Integration tests for the HuggingFace loader module.
Tests model/tokenizer loading, registry, and revision handling.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("torch")


# Import the module under test
from codex_ml import hf_loader


class TestCausalLMRegistry:
    """Tests for the causal LM registry functions."""

    def test_register_and_get(self) -> None:
        """Test registering and retrieving a custom loader."""

        # Create a mock loader
        def custom_loader(**kwargs: Any) -> MagicMock:
            return MagicMock(name="custom_model")

        # Register it
        decorated = hf_loader.register_causal_lm("test_model")(custom_loader)

        # Should be same function
        assert decorated is custom_loader, "decorated is not valid"

        # Should be retrievable
        retrieved = hf_loader.get_registered_causal_lm("test_model")
        assert retrieved is custom_loader, "retrieved is not valid"

        # Clean up
        hf_loader.unregister_causal_lm("test_model")
        assert hf_loader.get_registered_causal_lm("test_model") is None, "Condition must be true"

    def test_unregister_nonexistent(self) -> None:
        """Unregistering non-existent name should not raise."""
        # Should not raise
        hf_loader.unregister_causal_lm("nonexistent_model_xyz")

    def test_get_nonexistent(self) -> None:
        """Getting non-existent name should return None."""
        result = hf_loader.get_registered_causal_lm("nonexistent_model_abc")
        assert result is None, "Result must not be empty"

    def test_registry_decorator_pattern(self) -> None:
        """Test the decorator pattern for registration."""

        @hf_loader.register_causal_lm("decorated_model")
        def my_loader(**kwargs: Any) -> str:
            return "loaded"

        assert hf_loader.get_registered_causal_lm("decorated_model") is my_loader, "Condition must be true"

        # Clean up
        hf_loader.unregister_causal_lm("decorated_model")


class TestLocalIdentifier:
    """Tests for _is_local_identifier function."""

    def test_existing_path(self, tmp_path: Path) -> None:
        """Test detection of existing local path."""
        # Create a temporary file
        test_file = tmp_path / "model_config.json"
        test_file.write_text("{}")

        assert hf_loader._is_local_identifier(tmp_path) is True, "Condition must be true"
        assert hf_loader._is_local_identifier(str(tmp_path)) is True, "Condition must be true"

    def test_nonexistent_path(self) -> None:
        """Test detection of non-existent path."""
        result = hf_loader._is_local_identifier("/nonexistent/path/to/model")
        assert result is False, "Result must not be empty"

    def test_hub_identifier(self) -> None:
        """Test that hub identifiers are not local."""
        assert hf_loader._is_local_identifier("gpt2") is False, "Condition must be true"
        assert hf_loader._is_local_identifier("facebook/opt-125m") is False, "Condition must be true"

    def test_file_uri(self, tmp_path: Path) -> None:
        """Test file:// URI handling."""
        # File URI for existing path
        file_uri = f"file://{tmp_path}"
        assert hf_loader._is_local_identifier(file_uri) is True, "Condition must be true"

    def test_pathlike_object(self, tmp_path: Path) -> None:
        """Test PathLike object handling."""
        # Path object is PathLike
        assert hf_loader._is_local_identifier(tmp_path) is True, "Condition must be true"


class TestAmpDtypeMapping:
    """Tests for _map_amp_dtype function."""

    @pytest.fixture
    def skip_without_torch(self) -> None:
        """Skip test if torch not available or is a stub."""
        try:
            import torch

            # Check if it's the real torch or a stub
            if not hasattr(torch, "float16") or not hasattr(torch, "bfloat16"):
                pytest.skip("torch is a stub, not the real library")
        except (ImportError, AttributeError):
            pytest.skip("torch not installed")

    def test_bf16_mapping(self, skip_without_torch: None) -> None:
        """Test bfloat16 dtype mapping."""
        import torch

        # Ensure hf_loader module uses real torch, not stub
        hf_loader.torch = torch

        assert hf_loader._map_amp_dtype("bf16") == torch.bfloat16, "Condition must be true"
        assert hf_loader._map_amp_dtype("bfloat16") == torch.bfloat16, "Condition must be true"
        assert hf_loader._map_amp_dtype("BF16") == torch.bfloat16, "Condition must be true"

    def test_fp16_mapping(self, skip_without_torch: None) -> None:
        """Test float16 dtype mapping."""
        import torch

        # Ensure hf_loader module uses real torch, not stub
        hf_loader.torch = torch

        assert hf_loader._map_amp_dtype("fp16") == torch.float16, "Condition must be true"
        assert hf_loader._map_amp_dtype("float16") == torch.float16, "Condition must be true"
        assert hf_loader._map_amp_dtype("half") == torch.float16, "Condition must be true"

    def test_none_dtype(self) -> None:
        """Test None input returns None."""
        assert hf_loader._map_amp_dtype(None) is None, "Condition must be true"

    def test_unknown_dtype(self, skip_without_torch: None) -> None:
        """Test unknown dtype returns None."""
        assert hf_loader._map_amp_dtype("unknown") is None, "Condition must be true"


class TestRequiredRevision:
    """Tests for _required_revision function."""

    def test_explicit_revision(self, tmp_path: Path) -> None:
        """Test explicit revision is used."""
        # For local path, explicit revision is returned
        result = hf_loader._required_revision(tmp_path, "v1.0.0")
        assert result == "v1.0.0", "Result must not be empty"

    def test_local_path_no_revision_needed(self, tmp_path: Path) -> None:
        """Test local paths don't require revision."""
        result = hf_loader._required_revision(tmp_path, None)
        assert result is None, "Result must not be empty"

    def test_env_revision(self) -> None:
        """Test environment variable revision."""
        with patch.dict(os.environ, {"HUGGINGFACE_REVISION": "main"}):
            # Mock _is_local_identifier to return False
            with patch.object(hf_loader, "_is_local_identifier", return_value=False):
                result = hf_loader._required_revision("facebook/opt-125m", None)
                assert result == "main", "Result must not be empty"

    def test_missing_revision_raises(self) -> None:
        """Test missing revision for remote model raises."""
        # Clear all revision env vars
        env_patch = {
            "HUGGINGFACE_REVISION": "",
            "HF_REVISION": "",
            "HF_MODEL_REVISION": "",
            "CODEX_HF_REVISION": "",
        }

        with patch.dict(os.environ, env_patch, clear=False):
            with patch.object(hf_loader, "_is_local_identifier", return_value=False):
                with patch("codex_ml.hf_loader.get_hf_revision", return_value=None):
                    with pytest.raises(RuntimeError, match="revision.*required"):
                        hf_loader._required_revision("facebook/opt-125m", None)


class TestTransformersAvailability:
    """Tests for transformers availability checking."""

    def test_transformers_available_flag(self) -> None:
        """Test TRANSFORMERS_AVAILABLE flag is set correctly."""
        # Should be a boolean
        assert isinstance(hf_loader.TRANSFORMERS_AVAILABLE, bool)

    def test_load_tokenizer_without_transformers(self) -> None:
        """Test load_tokenizer raises when transformers not available."""
        with patch.object(hf_loader, "TRANSFORMERS_AVAILABLE", False):
            with pytest.raises(ImportError, match="transformers.*required"):
                hf_loader.load_tokenizer("gpt2", revision="main")

    def test_load_model_without_transformers(self) -> None:
        """Test load_model raises when transformers not available."""
        with patch.object(hf_loader, "TRANSFORMERS_AVAILABLE", False):
            with pytest.raises(ImportError, match="transformers.*required"):
                hf_loader.load_model("gpt2", revision="main")


class TestRepoIdTypes:
    """Tests for different repo_id types."""

    def test_string_repo_id(self) -> None:
        """Test string repo_id handling."""
        # Hub-style identifiers
        assert hf_loader._is_local_identifier("gpt2") is False, "Condition must be true"
        assert hf_loader._is_local_identifier("facebook/opt-125m") is False, "Condition must be true"
        assert hf_loader._is_local_identifier("EleutherAI/gpt-neo-125m") is False, "Condition must be true"

    def test_path_repo_id(self, tmp_path: Path) -> None:
        """Test Path repo_id handling."""
        # Create a model directory
        model_dir = tmp_path / "my_model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text("{}")

        assert hf_loader._is_local_identifier(model_dir) is True, "Condition must be true"


class TestIntegration:
    """Integration tests (require optional dependencies)."""

    def test_registry_integration(self) -> None:
        """Test registry works with real usage pattern."""
        call_count = 0

        @hf_loader.register_causal_lm("integration_test_model")
        def loader(**kwargs: Any) -> dict:
            nonlocal call_count
            call_count += 1
            return {"loaded": True, "kwargs": kwargs}

        # Retrieve and call
        fn = hf_loader.get_registered_causal_lm("integration_test_model")
        assert fn is not None, "fn must be initialized"

        result = fn(device="cpu", dtype="float32")
        assert result["loaded"] is True, "Result must not be empty"
        assert result["kwargs"]["device"] == "cpu", "Result must not be empty"
        assert call_count == 1, "Count must be greater than zero"

        # Clean up
        hf_loader.unregister_causal_lm("integration_test_model")
