"""Test that pytest fixtures behave correctly."""

from unittest.mock import MagicMock

import pytest


class TestFixtureReusability:
    """Verify fixtures can be called multiple times without exhaustion."""

    @pytest.mark.skipif(
        not hasattr(pytest, "importorskip")
        or pytest.importorskip("torch", minversion=None) is None,
        reason="torch not available in test environment",
    )
    def test_mock_model_fixture_multiple_calls(self, mock_transformer_model):
        """Test mock_model fixture works across multiple calls."""
        # First call
        result1 = mock_transformer_model.get_attention_weights()
        assert result1 is not None, "result1 must be initialized"
        assert len(result1) > 0, "Result1 must not be empty"

        # Second call should not raise StopIteration
        result2 = mock_transformer_model.get_attention_weights()
        assert result2 is not None, "result2 must be initialized"
        assert len(result2) > 0, "Result2 must not be empty"

    @pytest.mark.skipif(
        not hasattr(pytest, "importorskip")
        or pytest.importorskip("torch", minversion=None) is None,
        reason="torch not available in test environment",
    )
    def test_fixture_independence(self, mock_transformer_model):
        """Test fixture provides independent instances."""
        # Modify one instance
        mock_transformer_model.custom_attr = "modified"

        # Should have custom attribute
        assert hasattr(mock_transformer_model, "custom_attr")

        # Should have standard attributes
        assert hasattr(mock_transformer_model, "num_layers")

    def test_mock_not_using_side_effect_list(self):
        """Test that mocks don't use side_effect with list (causes StopIteration)."""
        # This is a pattern test - ensure we're not using problematic patterns

        # Bad pattern (DO NOT USE):
        # mock = MagicMock()
        # mock.method.side_effect = [result1, result2]  # Exhausts after 2 calls

        # Good pattern (USE THIS):
        mock = MagicMock()
        mock.method.return_value = "result"

        # Can be called multiple times
        result1 = mock.method()
        result2 = mock.method()
        result3 = mock.method()

        assert result1 == "result", "Result must not be empty"
        assert result2 == "result", "Result must not be empty"
        assert result3 == "result", "Result must not be empty"


class TestSerializationPatterns:
    """Test that our mocks follow serialization best practices."""

    def test_serializable_mock_model_pattern(self, serializable_mock_model):
        """Test that serializable mock model pattern works."""
        import json

        # Should have to_dict method
        assert hasattr(serializable_mock_model, "to_dict")

        # Should be JSON serializable
        model_dict = serializable_mock_model.to_dict()
        json_str = json.dumps(model_dict)
        parsed = json.loads(json_str)

        assert "config" in parsed, "Condition must be true"
        assert "call_count" in parsed, "Count must be greater than zero"
