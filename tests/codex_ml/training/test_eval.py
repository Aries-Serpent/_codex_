"""
Test Eval

Test module for eval.
"""

import pytest


class TestSafeFloat:
    """Test _safe_float helper function."""

    def test_safe_float_from_number(self):
        """Test converting number to float."""
        try:
            from codex_ml.training.eval import _safe_float

            assert _safe_float(42) == 42.0, "Condition must be true"
            assert _safe_float(3.14) == 3.14, "Condition must be true"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_safe_float_from_invalid(self):
        """Test safe_float with invalid input returns 0.0."""
        try:
            from codex_ml.training.eval import _safe_float

            result = _safe_float(object())
            assert result == 0.0, "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestMoveBatchToDevice:
    """Test _move_batch_to_device helper function."""

    def test_move_batch_none_device(self):
        """Test move_batch with None device returns same batch."""
        try:
            from codex_ml.training.eval import _move_batch_to_device

            batch = {"input": [1, 2, 3], "target": [4, 5, 6]}
            result = _move_batch_to_device(batch, None)
            assert result == batch, "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_move_batch_without_to_method(self):
        """Test move_batch with values without .to() method."""
        try:
            from codex_ml.training.eval import _move_batch_to_device

            batch = {"value": 42}
            result = _move_batch_to_device(batch, "cpu")
            assert result["value"] == 42, "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestEvaluate:
    """Test evaluate function."""

    def test_evaluate_empty_dataloader(self):
        """Test evaluate with empty dataloader."""
        try:
            from codex_ml.training.eval import evaluate

            def dummy_loss(outputs, batch):
                return 0.0

            class DummyModel:
                training = True

                def eval(self):
                    self.training = False

                def train(self, mode):
                    self.training = mode

                def __call__(self, **kwargs):
                    return {}

            model = DummyModel()
            result = evaluate(model, [], loss_fn=dummy_loss)
            assert isinstance(result, dict)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_evaluate_single_batch(self):
        """Test evaluate with single batch."""
        try:
            from codex_ml.training.eval import evaluate

            def dummy_loss(outputs, batch):
                return 1.0

            class DummyModel:
                training = True

                def eval(self):
                    self.training = False

                def train(self, mode):
                    self.training = mode

                def __call__(self, **kwargs):
                    return {"logits": [0.5]}

            model = DummyModel()
            dataloader = [{"input": [1, 2, 3]}]
            result = evaluate(model, dataloader, loss_fn=dummy_loss)
            assert "eval_loss" in result, "Result must not be empty"
            assert result["eval_loss"] == 1.0, "Result must not be empty"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")
