"""Unit tests for training callback system.

Tests early stopping callback registration, metric tracking,
and plateau detection with various patience and delta configurations.
"""

from __future__ import annotations

import pytest


class TestEarlyStoppingBasics:
    """Test basic early stopping callback functionality."""

    def test_early_stopping_initialization(self):
        """Verify EarlyStopping initializes with correct default values."""
        # Arrange & Act
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping()

        # Assert
        assert es.patience == 3, "Default patience should be 3"
        assert es.min_delta == 0.0, "Default min_delta should be 0.0"
        assert es.mode == "min", "Default mode should be 'min'"
        assert es.best is None, "Initial best should be None"
        assert es.bad == 0, "Initial bad counter should be 0"

    def test_early_stopping_custom_parameters(self):
        """Verify EarlyStopping accepts custom parameters."""
        # Arrange & Act
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=5, min_delta=0.01, mode="max")

        # Assert
        assert es.patience == 5, "Custom patience not set"
        assert es.min_delta == 0.01, "Custom min_delta not set"
        assert es.mode == "max", "Custom mode not set"

    def test_early_stopping_first_metric_never_stops(self):
        """Verify first metric never triggers stop condition."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2)
        first_metric = 0.5

        # Act
        should_stop = es.step(first_metric)

        # Assert
        assert should_stop is False, "First metric should never stop training"
        assert es.best == 0.5, "Best metric should be set to first value"

    def test_early_stopping_detects_improvement_min_mode(self):
        """Verify improvement detection works in min mode."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2, min_delta=0.0, mode="min")
        metrics = [0.5, 0.4, 0.3]  # Decreasing (improving in min mode)

        # Act & Assert
        for i, metric in enumerate(metrics):
            should_stop = es.step(metric)
            assert should_stop is False, f"Should not stop on improving metric {metric} at step {i}"
            assert es.bad == 0, "Bad counter should reset on improvement"

    def test_early_stopping_detects_improvement_max_mode(self):
        """Verify improvement detection works in max mode."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2, min_delta=0.0, mode="max")
        metrics = [0.3, 0.4, 0.5]  # Increasing (improving in max mode)

        # Act & Assert
        for i, metric in enumerate(metrics):
            should_stop = es.step(metric)
            assert should_stop is False, f"Should not stop on improving metric {metric} at step {i}"
            assert es.bad == 0, "Bad counter should reset on improvement"

    def test_early_stopping_with_min_delta_threshold(self):
        """Verify min_delta threshold is respected for improvements."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=1, min_delta=0.1, mode="min")

        # Act & Assert
        es.step(1.0)  # Set best to 1.0

        # Small improvement (< min_delta) should not reset bad counter
        should_stop = es.step(0.95)
        assert should_stop is False, "Small improvement should not stop yet"
        assert es.bad == 1, "Bad counter should increment for small improvement"

        # Large improvement (>= min_delta) should reset bad counter
        should_stop = es.step(0.85)
        assert should_stop is False, "Large improvement should continue training"
        assert es.bad == 0, "Bad counter should reset for significant improvement"


class TestEarlyStoppingPlateauDetection:
    """Test plateau detection and stopping condition."""

    def test_early_stopping_stops_after_patience_exceeded(self):
        """Verify training stops when patience is exceeded."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2, min_delta=0.0, mode="min")
        metrics = [0.5]  # First metric (no stop)
        metrics.extend([0.5, 0.5, 0.5])  # No improvement for 3 steps

        # Act & Assert
        for i, metric in enumerate(metrics):
            should_stop = es.step(metric)

            if i == 0:
                # First metric
                assert should_stop is False, "Should not stop on first metric"
            elif i < 3:
                # Not yet at patience limit
                assert should_stop is False, f"Should not stop before patience at step {i}"
                assert es.bad < es.patience, "Bad counter should be less than patience"
            else:
                # Exceeded patience
                assert should_stop is True, f"Should stop after patience exceeded at step {i}"

    def test_early_stopping_resets_counter_on_improvement(self):
        """Verify bad counter resets when improvement occurs."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2, min_delta=0.0, mode="min")

        # Act: No improvement sequence
        es.step(0.5)  # Set best
        es.step(0.6)  # No improvement
        es.step(0.7)  # No improvement
        assert es.bad == 2, "Bad counter should be 2 after no improvements"

        # Reset with improvement
        es.step(0.4)  # Improvement
        assert es.bad == 0, "Bad counter should reset to 0 on improvement"
        assert es.best == 0.4, "Best should update to new lower value"

    def test_early_stopping_max_mode_plateau_detection(self):
        """Verify plateau detection works in max mode (increasing metrics)."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=1, min_delta=0.01, mode="max")

        # Act & Assert
        es.step(0.5)  # Set best = 0.5
        assert es.bad == 0, "Should initialize with bad = 0"

        should_stop = es.step(0.55)  # Improvement (>= 0.5 + 0.01)
        assert should_stop is False, "Should continue on improvement"
        assert es.bad == 0, "Bad counter should remain 0 after improvement"

        should_stop = es.step(0.54)  # No improvement
        assert should_stop is False, "Should not stop yet"
        assert es.bad == 1, "Bad counter should be 1"

        should_stop = es.step(0.54)  # Still no improvement
        assert should_stop is True, "Should stop when patience exhausted"


class TestEarlyStoppingEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_early_stopping_with_zero_patience(self):
        """Verify behavior with patience=0 (immediate stop on plateau)."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=0, min_delta=0.0, mode="min")

        # Act & Assert
        es.step(0.5)  # First metric, no stop
        assert es.bad == 0, "Initial step should not increment bad counter"

        should_stop = es.step(0.5)  # No improvement
        assert should_stop is True, "Should stop immediately on any plateau with patience=0"

    def test_early_stopping_with_large_patience(self):
        """Verify behavior with large patience value."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=100, min_delta=0.0, mode="min")

        # Act: Generate plateau
        es.step(0.5)
        for _ in range(50):
            should_stop = es.step(0.5)
            if should_stop:
                break

        # Assert
        assert es.bad == 50, "Bad counter should be 50 after 50 no-improvement steps"
        assert should_stop is False, "Should not stop with 50 bad steps when patience=100"

    def test_early_stopping_with_very_small_min_delta(self):
        """Verify min_delta discrimination with tiny threshold."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=1, min_delta=1e-10, mode="min")

        # Act & Assert
        es.step(0.5)  # Set best

        # Improvement by 1e-11 (less than min_delta)
        should_stop = es.step(0.5 - 1e-11)
        assert should_stop is False, "Should not stop yet"
        assert es.bad == 1, "Should count as no improvement when delta < min_delta"

        # Improvement by 1e-9 (more than min_delta)
        should_stop = es.step(0.5 - 1e-9)
        assert should_stop is False, "Should continue on valid improvement"
        assert es.bad == 0, "Should reset bad counter for improvement > min_delta"

    def test_early_stopping_negative_metrics(self):
        """Verify handling of negative metric values."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=1, min_delta=0.0, mode="min")

        # Act & Assert
        es.step(-0.5)  # Set best to negative
        assert es.best == -0.5, "Should handle negative metrics"

        should_stop = es.step(-0.6)  # Better (more negative)
        assert should_stop is False, "Should detect improvement with negative metrics"
        assert es.bad == 0, "Bad counter should reset"

    def test_early_stopping_with_identical_consecutive_metrics(self):
        """Verify handling of identical consecutive metric values."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2, min_delta=0.0, mode="min")

        # Act & Assert
        metrics = [0.5, 0.5, 0.5, 0.5]
        for i, metric in enumerate(metrics):
            should_stop = es.step(metric)

            if i == 0:
                assert es.bad == 0, "First step should have bad=0"
            elif i <= 2:
                # Not yet at patience (patience=2, so stop when bad >= 2)
                assert should_stop is False, f"Should not stop at step {i} (bad={es.bad})"
            else:
                assert should_stop is True, "Should stop when plateau reaches patience"


class TestEarlyStoppingIntegration:
    """Test integration with training loop simulation."""

    def test_early_stopping_in_training_loop_min_mode(self):
        """Simulate training loop with decreasing loss and early stopping."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=2, min_delta=0.05, mode="min")

        # Simulated training losses
        losses = [
            0.5,  # Step 0: initial
            0.45,  # Step 1: improvement (0.05)
            0.44,  # Step 2: small improvement (<0.05)
            0.445,  # Step 3: degradation
            0.446,  # Step 4: degradation
            0.447,  # Step 5: degradation (should stop)
        ]

        stopped_at = None

        # Act
        for step, loss in enumerate(losses):
            if es.step(loss):
                stopped_at = step
                break

        # Assert
        assert stopped_at is not None, "Training should have stopped"
        assert stopped_at == 5, f"Should have stopped after patience exhausted at step {stopped_at}"

    def test_early_stopping_recovery_sequence(self):
        """Test that significant improvements reset stop counter."""
        # Arrange
        from src.codex_ml.training.callbacks import EarlyStopping

        es = EarlyStopping(patience=1, min_delta=0.1, mode="min")

        # Act & Assert
        es.step(1.0)  # Set baseline

        # Plateau
        es.step(1.0)
        assert es.bad == 1, "Should count plateau"

        # Significant improvement
        es.step(0.8)
        assert es.bad == 0, "Bad counter should reset on improvement"
        assert es.best == 0.8, "Best should update to new value"

        # Resume plateau
        es.step(0.8)
        assert es.bad == 1, "Should count plateau again"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
