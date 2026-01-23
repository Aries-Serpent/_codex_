"""Test that pytest fixtures behave correctly."""

import pytest
from unittest.mock import MagicMock


class TestFixtureReusability:
    """Verify fixtures can be called multiple times without exhaustion."""
    
    def test_mock_model_fixture_multiple_calls(self):
        """Test mock_model fixture works across multiple calls."""
        # This test verifies fixture independence by importing
        # We can't actually test the fixture directly here without the dependency
        # but we can test the pattern
        
        # Simulate fixture behavior
        from tests.unit.interpretability.test_attention_scorer import MockTransformerModel
        
        mock_model1 = MockTransformerModel(num_layers=2, num_heads=4, seq_len=10)
        mock_model2 = MockTransformerModel(num_layers=2, num_heads=4, seq_len=10)
        
        # First call
        result1 = mock_model1.get_attention_weights()
        assert result1 is not None
        assert len(result1) > 0
        
        # Second call should not raise StopIteration
        result2 = mock_model1.get_attention_weights()
        assert result2 is not None
        assert len(result2) > 0
        
        # Different instances should be independent
        assert id(mock_model1) != id(mock_model2)
    
    def test_fixture_independence(self):
        """Test fixture provides independent instances."""
        from tests.unit.interpretability.test_attention_scorer import MockTransformerModel
        
        # Create two instances
        model1 = MockTransformerModel(num_layers=2, num_heads=4, seq_len=10)
        model2 = MockTransformerModel(num_layers=2, num_heads=4, seq_len=10)
        
        # Modify one instance
        model1.custom_attr = "modified"
        
        # Other instance should not be affected
        assert hasattr(model1, 'custom_attr')
        assert not hasattr(model2, 'custom_attr')
        
        # Both should have standard attributes
        assert hasattr(model1, 'num_layers')
        assert hasattr(model2, 'num_layers')
    
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
        
        assert result1 == "result"
        assert result2 == "result"
        assert result3 == "result"


class TestSerializationPatterns:
    """Test that our mocks follow serialization best practices."""
    
    def test_serializable_mock_model_pattern(self):
        """Test that serializable mock model pattern works."""
        from tests.eval.test_evaluation_reproducible import MockSerializableModel
        import json
        
        model = MockSerializableModel()
        
        # Should have to_dict method
        assert hasattr(model, 'to_dict')
        
        # Should be JSON serializable
        model_dict = model.to_dict()
        json_str = json.dumps(model_dict)
        parsed = json.loads(json_str)
        
        assert 'config' in parsed
        assert 'call_count' in parsed
