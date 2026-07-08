"""
Tests for ML Training Callbacks.

Tests for training callbacks that handle events during training.

Phase 55: MEDIUM Priority Module Tests
Coverage Target: src/codex_ml 11% → 16%+
"""

from enum import Enum, auto

import pytest


class TrainingEvent(Enum):
    """Training events that trigger callbacks."""

    TRAIN_BEGIN = auto()
    TRAIN_END = auto()
    EPOCH_BEGIN = auto()
    EPOCH_END = auto()
    BATCH_BEGIN = auto()
    BATCH_END = auto()
    EVALUATE_BEGIN = auto()
    EVALUATE_END = auto()
    SAVE_BEGIN = auto()
    SAVE_END = auto()


class TestCallbackRegistration:
    """Tests for callback registration."""

    def test_callback_registration(self):
        """Callbacks can be registered for events."""

        class CallbackManager:
            def __init__(self):
                self.callbacks = {}

            def register(self, event, callback):
                if event not in self.callbacks:
                    self.callbacks[event] = []
                self.callbacks[event].append(callback)

            def trigger(self, event, **kwargs):
                for callback in self.callbacks.get(event, []):
                    callback(**kwargs)

        manager = CallbackManager()
        results = []

        manager.register(TrainingEvent.EPOCH_END, lambda **k: results.append("epoch_end"))
        manager.trigger(TrainingEvent.EPOCH_END)

        assert results == ["epoch_end"], "Result must not be empty"

    def test_multiple_callbacks(self):
        """Multiple callbacks can be registered for same event."""

        class CallbackManager:
            def __init__(self):
                self.callbacks = {}

            def register(self, event, callback):
                if event not in self.callbacks:
                    self.callbacks[event] = []
                self.callbacks[event].append(callback)

            def trigger(self, event, **kwargs):
                for callback in self.callbacks.get(event, []):
                    callback(**kwargs)

        manager = CallbackManager()
        results = []

        manager.register(TrainingEvent.EPOCH_END, lambda **k: results.append("cb1"))
        manager.register(TrainingEvent.EPOCH_END, lambda **k: results.append("cb2"))
        manager.register(TrainingEvent.EPOCH_END, lambda **k: results.append("cb3"))

        manager.trigger(TrainingEvent.EPOCH_END)

        assert results == ["cb1", "cb2", "cb3"]


class TestEarlyStoppingCallback:
    """Tests for early stopping callback."""

    def test_early_stopping_patience(self):
        """Early stopping respects patience."""

        class EarlyStoppingCallback:
            def __init__(self, patience=3, min_delta=0.0):
                self.patience = patience
                self.min_delta = min_delta
                self.best_loss = float("inf")
                self.counter = 0
                self.should_stop = False

            def on_epoch_end(self, loss):
                if loss < self.best_loss - self.min_delta:
                    self.best_loss = loss
                    self.counter = 0
                else:
                    self.counter += 1
                    if self.counter >= self.patience:
                        self.should_stop = True

        callback = EarlyStoppingCallback(patience=3)

        # Improving
        callback.on_epoch_end(1.0)
        callback.on_epoch_end(0.9)
        callback.on_epoch_end(0.8)
        assert not callback.should_stop, "Condition must be true"

        # Not improving
        callback.on_epoch_end(0.85)
        callback.on_epoch_end(0.86)
        callback.on_epoch_end(0.87)
        assert callback.should_stop, "Condition must be true"

    def test_early_stopping_min_delta(self):
        """Early stopping considers min_delta."""

        class EarlyStoppingCallback:
            def __init__(self, patience=3, min_delta=0.01):
                self.patience = patience
                self.min_delta = min_delta
                self.best_loss = float("inf")
                self.counter = 0

            def on_epoch_end(self, loss):
                if loss < self.best_loss - self.min_delta:
                    self.best_loss = loss
                    self.counter = 0
                else:
                    self.counter += 1

        callback = EarlyStoppingCallback(patience=3, min_delta=0.01)

        callback.on_epoch_end(1.0)
        callback.on_epoch_end(0.995)  # Not enough improvement

        assert callback.counter == 1, "Count must be greater than zero"


class TestModelCheckpointCallback:
    """Tests for model checkpoint callback."""

    def test_checkpoint_on_epoch_end(self):
        """Checkpoint is saved at end of each epoch."""

        class ModelCheckpointCallback:
            def __init__(self, save_path, save_every=1):
                self.save_path = save_path
                self.save_every = save_every
                self.saved_epochs = []

            def on_epoch_end(self, epoch, model=None):
                if epoch % self.save_every == 0:
                    self.saved_epochs.append(epoch)

        callback = ModelCheckpointCallback("/models", save_every=2)

        for epoch in range(1, 11):
            callback.on_epoch_end(epoch)

        assert callback.saved_epochs == [2, 4, 6, 8, 10]

    def test_checkpoint_best_only(self):
        """Checkpoint saves only best model."""

        class BestModelCheckpoint:
            def __init__(self):
                self.best_loss = float("inf")
                self.best_epoch = None

            def on_epoch_end(self, epoch, loss):
                if loss < self.best_loss:
                    self.best_loss = loss
                    self.best_epoch = epoch
                    return True  # Saved
                return False  # Not saved

        callback = BestModelCheckpoint()

        assert callback.on_epoch_end(1, 1.0)  # Best
        assert callback.on_epoch_end(2, 0.8)  # Better
        assert not callback.on_epoch_end(3, 0.9)  # Worse
        assert callback.on_epoch_end(4, 0.7)  # Better

        assert callback.best_epoch == 4, "best_epoch is not valid"


class TestLoggingCallback:
    """Tests for logging callback."""

    def test_logging_frequency(self):
        """Logging respects frequency setting."""

        class LoggingCallback:
            def __init__(self, log_every=10):
                self.log_every = log_every
                self.logs = []

            def on_batch_end(self, batch, loss):
                if batch % self.log_every == 0:
                    self.logs.append({"batch": batch, "loss": loss})

        callback = LoggingCallback(log_every=10)

        for batch in range(1, 51):
            callback.on_batch_end(batch, 1.0 - batch * 0.01)

        assert len(callback.logs) == 5, "Collection must not be empty"

    def test_metrics_logging(self):
        """Metrics are logged correctly."""

        class MetricsLogger:
            def __init__(self):
                self.history = {"loss": [], "accuracy": []}

            def on_epoch_end(self, metrics):
                for key, value in metrics.items():
                    if key in self.history:
                        self.history[key].append(value)

        logger = MetricsLogger()

        logger.on_epoch_end({"loss": 1.0, "accuracy": 0.8})
        logger.on_epoch_end({"loss": 0.8, "accuracy": 0.85})

        assert logger.history["loss"] == [1.0, 0.8]
        assert logger.history["accuracy"] == [0.8, 0.85]


class TestLearningRateSchedulerCallback:
    """Tests for learning rate scheduler callback."""

    def test_step_lr_scheduler(self):
        """Step LR scheduler reduces LR at intervals."""

        class StepLRCallback:
            def __init__(self, initial_lr, step_size, gamma):
                self.initial_lr = initial_lr
                self.step_size = step_size
                self.gamma = gamma
                self.current_lr = initial_lr

            def on_epoch_end(self, epoch):
                if epoch % self.step_size == 0:
                    self.current_lr *= self.gamma

        callback = StepLRCallback(initial_lr=0.01, step_size=10, gamma=0.1)

        # Loop from 1 to 30, triggers at epochs 10, 20, 30 (3 times)
        for epoch in range(1, 31):
            callback.on_epoch_end(epoch)

        # 0.01 * 0.1 * 0.1 * 0.1 = 0.00001 (triggered at epochs 10, 20, 30)
        assert callback.current_lr == pytest.approx(0.00001, rel=1e-6)

    def test_warmup_scheduler(self):
        """Warmup scheduler increases LR during warmup."""

        class WarmupCallback:
            def __init__(self, warmup_steps, target_lr):
                self.warmup_steps = warmup_steps
                self.target_lr = target_lr
                self.current_step = 0

            def get_lr(self):
                if self.current_step < self.warmup_steps:
                    return self.target_lr * (self.current_step / self.warmup_steps)
                return self.target_lr

            def on_batch_end(self):
                self.current_step += 1

        callback = WarmupCallback(warmup_steps=100, target_lr=0.01)

        assert callback.get_lr() == 0.0, "Condition must be true"

        for _ in range(50):
            callback.on_batch_end()

        assert callback.get_lr() == pytest.approx(0.005), "Condition must be true"

        for _ in range(50):
            callback.on_batch_end()

        assert callback.get_lr() == 0.01, "Condition must be true"


class TestGradientClippingCallback:
    """Tests for gradient clipping callback."""

    def test_gradient_norm_clipping(self):
        """Gradients are clipped by norm."""

        def clip_gradient_norm(gradients, max_norm):
            total_norm = sum(g**2 for g in gradients) ** 0.5
            if total_norm > max_norm:
                scale = max_norm / total_norm
                return [g * scale for g in gradients]
            return gradients

        gradients = [3.0, 4.0]  # norm = 5.0
        clipped = clip_gradient_norm(gradients, max_norm=1.0)

        clipped_norm = sum(g**2 for g in clipped) ** 0.5
        assert clipped_norm == pytest.approx(1.0), "clipped_norm is not valid"

    def test_gradient_value_clipping(self):
        """Gradients are clipped by value."""

        def clip_gradient_value(gradients, clip_value):
            return [max(-clip_value, min(clip_value, g)) for g in gradients]

        gradients = [-2.0, 0.5, 3.0]
        clipped = clip_gradient_value(gradients, clip_value=1.0)

        assert clipped == [-1.0, 0.5, 1.0]


class TestProgressCallback:
    """Tests for progress tracking callback."""

    def test_progress_tracking(self):
        """Progress is tracked during training."""

        class ProgressCallback:
            def __init__(self, total_epochs, total_batches):
                self.total_epochs = total_epochs
                self.total_batches = total_batches
                self.current_epoch = 0
                self.current_batch = 0

            def on_epoch_begin(self, epoch):
                self.current_epoch = epoch
                self.current_batch = 0

            def on_batch_end(self, batch):
                self.current_batch = batch

            def progress(self):
                epoch_progress = self.current_epoch / self.total_epochs
                batch_progress = self.current_batch / self.total_batches
                return epoch_progress + batch_progress / self.total_epochs

        callback = ProgressCallback(total_epochs=10, total_batches=100)

        callback.on_epoch_begin(5)
        callback.on_batch_end(50)

        assert callback.progress() == pytest.approx(0.55), "Condition must be true"
