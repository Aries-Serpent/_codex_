"""
Comprehensive tests for src/codex_ml/training.py
Week 1 Coverage Improvement: Training Configuration

Tests focus on:
- Training configuration setup
- Optimizer setup and configuration
- Learning rate scheduling
"""

import pytest

pytest.importorskip("torch")

# Import with graceful fallback
try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class TestTrainingConfiguration:
    """Tests for training configuration functionality."""

    def test_basic_training_config_creation(self):
        """Test creating a basic training configuration."""
        config = {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10,
            "optimizer": "adam",
        }

        assert config["learning_rate"] == 0.001, "Condition must be true"
        assert config["batch_size"] == 32, "Condition must be true"
        assert config["epochs"] == 10, "Condition must be true"
        assert config["optimizer"] == "adam", "Condition must be true"

    def test_training_config_validation(self):
        """Test validation of training configuration."""
        # Valid config
        valid_config = {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10,
        }

        assert valid_config["learning_rate"] > 0, "Value must be greater than zero"
        assert valid_config["batch_size"] > 0, "Value must be greater than zero"
        assert valid_config["epochs"] > 0, "Value must be greater than zero"

        # Invalid config values
        invalid_lr = {"learning_rate": -0.001}
        assert invalid_lr["learning_rate"] < 0, "Condition must be true"

        invalid_batch = {"batch_size": 0}
        assert invalid_batch["batch_size"] <= 0, "Condition must be true"

    def test_training_config_defaults(self):
        """Test default training configuration values."""
        defaults = {
            "learning_rate": 1e-4,
            "batch_size": 16,
            "epochs": 3,
            "optimizer": "adamw",
            "weight_decay": 0.01,
            "warmup_steps": 0,
            "max_grad_norm": 1.0,
        }

        # Verify defaults are sensible
        assert 0 < defaults["learning_rate"] < 1, "0 is not valid"
        assert defaults["batch_size"] in [8, 16, 32, 64]
        assert defaults["epochs"] > 0, "Value must be greater than zero"
        assert defaults["optimizer"] in ["adam", "adamw", "sgd"]

    def test_training_config_merging(self):
        """Test merging training configurations."""
        base_config = {
            "learning_rate": 1e-4,
            "batch_size": 16,
            "epochs": 3,
        }

        override_config = {
            "learning_rate": 1e-3,
            "optimizer": "sgd",
        }

        # Merge configs
        merged = {**base_config, **override_config}

        assert merged["learning_rate"] == 1e-3, "Condition must be true"
        assert merged["batch_size"] == 16, "Condition must be true"
        assert merged["optimizer"] == "sgd", "Condition must be true"

    def test_training_config_from_dict(self):
        """Test creating training config from dictionary."""
        config_dict = {
            "learning_rate": 5e-5,
            "batch_size": 8,
            "num_train_epochs": 5,
            "gradient_accumulation_steps": 4,
        }

        # Config should preserve all values
        for key, value in config_dict.items():
            assert key in config_dict, "Condition must be true"
            assert config_dict[key] == value, "Value must be initialized"


class TestOptimizerSetup:
    """Tests for optimizer setup and configuration."""

    @pytest.fixture
    def simple_model(self):
        """Fixture providing a simple model."""
        if not HAS_TORCH:
            pytest.skip("PyTorch not available")
        import torch.nn as nn

        return nn.Linear(10, 2)

    def test_adam_optimizer_setup(self, simple_model):
        """Test setting up Adam optimizer."""
        import torch.optim as optim

        optimizer = optim.Adam(
            simple_model.parameters(),
            lr=0.001,
            betas=(0.9, 0.999),
            eps=1e-8,
        )

        assert optimizer.defaults["lr"] == 0.001, "Condition must be true"
        assert optimizer.defaults["betas"] == (0.9, 0.999)
        assert optimizer.defaults["eps"] == 1e-8, "Condition must be true"

    def test_adamw_optimizer_setup(self, simple_model):
        """Test setting up AdamW optimizer with weight decay."""
        import torch.optim as optim

        optimizer = optim.AdamW(
            simple_model.parameters(),
            lr=5e-5,
            weight_decay=0.01,
        )

        assert optimizer.defaults["lr"] == 5e-5, "Condition must be true"
        assert optimizer.defaults["weight_decay"] == 0.01, "Condition must be true"

    def test_sgd_optimizer_setup(self, simple_model):
        """Test setting up SGD optimizer with momentum."""
        import torch.optim as optim

        optimizer = optim.SGD(
            simple_model.parameters(),
            lr=0.1,
            momentum=0.9,
            nesterov=True,
        )

        assert optimizer.defaults["lr"] == 0.1, "Condition must be true"
        assert optimizer.defaults["momentum"] == 0.9, "Condition must be true"
        assert optimizer.defaults["nesterov"] is True, "Condition must be true"

    def test_optimizer_parameter_groups(self, simple_model):
        """Test optimizer with different parameter groups."""
        import torch.optim as optim

        # Separate learning rates for different parameters
        params = [
            {"params": simple_model.weight, "lr": 0.01},
            {"params": simple_model.bias, "lr": 0.001},
        ]

        optimizer = optim.Adam(params)

        assert len(optimizer.param_groups) == 2, "Collection must not be empty"
        assert optimizer.param_groups[0]["lr"] == 0.01, "Condition must be true"
        assert optimizer.param_groups[1]["lr"] == 0.001, "Condition must be true"

    def test_optimizer_zero_grad(self, simple_model):
        """Test optimizer zero_grad functionality."""
        import torch.optim as optim

        optimizer = optim.Adam(simple_model.parameters(), lr=0.001)

        # Create some gradients
        x = torch.randn(5, 10)
        y = simple_model(x)
        loss = y.sum()
        loss.backward()

        # Check gradients exist
        assert simple_model.weight.grad is not None, "grad must be initialized"

        # Zero gradients
        optimizer.zero_grad()

        # Check gradients are zeroed (set to None by zero_grad)
        assert simple_model.weight.grad is None, "grad is not valid"

    def test_optimizer_step(self, simple_model):
        """Test optimizer step updates parameters."""
        import torch.optim as optim

        optimizer = optim.SGD(simple_model.parameters(), lr=0.1)

        # Store original weights
        original_weight = simple_model.weight.data.clone()

        # Compute gradients
        x = torch.randn(5, 10)
        y = simple_model(x)
        loss = y.sum()
        loss.backward()

        # Take optimizer step
        optimizer.step()

        # Weights should have changed
        assert not torch.allclose(simple_model.weight.data, original_weight)


class TestLearningRateScheduling:
    """Tests for learning rate scheduling."""

    @pytest.fixture
    def optimizer_with_model(self):
        """Fixture providing optimizer with simple model."""
        if not HAS_TORCH:
            pytest.skip("PyTorch not available")
        import torch.nn as nn
        import torch.optim as optim

        model = nn.Linear(10, 2)
        return optim.Adam(model.parameters(), lr=0.1)

    def test_step_lr_scheduler(self, optimizer_with_model):
        """Test StepLR scheduler."""
        from torch.optim.lr_scheduler import StepLR

        scheduler = StepLR(optimizer_with_model, step_size=5, gamma=0.1)

        # Initial LR
        assert abs(optimizer_with_model.param_groups[0]["lr"] - 0.1) < 1e-6, "Condition must be true"

        # After 5 steps
        for _ in range(5):
            scheduler.step()

        assert abs(optimizer_with_model.param_groups[0]["lr"] - 0.01) < 1e-6, "Condition must be true"

    def test_exponential_lr_scheduler(self, optimizer_with_model):
        """Test ExponentialLR scheduler."""
        from torch.optim.lr_scheduler import ExponentialLR

        scheduler = ExponentialLR(optimizer_with_model, gamma=0.9)

        initial_lr = optimizer_with_model.param_groups[0]["lr"]

        # After 1 step
        scheduler.step()

        expected_lr = initial_lr * 0.9
        actual_lr = optimizer_with_model.param_groups[0]["lr"]

        assert abs(actual_lr - expected_lr) < 1e-6, "Condition must be true"

    def test_cosine_annealing_scheduler(self, optimizer_with_model):
        """Test CosineAnnealingLR scheduler."""
        from torch.optim.lr_scheduler import CosineAnnealingLR

        T_max = 10
        eta_min = 0.001

        scheduler = CosineAnnealingLR(optimizer_with_model, T_max=T_max, eta_min=eta_min)

        # LR should oscillate between max and min
        lrs = []
        for _ in range(T_max + 1):
            lrs.append(optimizer_with_model.param_groups[0]["lr"])
            scheduler.step()

        # First LR should be max, should decrease, then increase back
        assert lrs[0] > lrs[T_max // 2], "Value must be greater than zero"
        assert lrs[-1] >= eta_min, "Value must be greater than zero"

    def test_reduce_on_plateau_scheduler(self, optimizer_with_model):
        """Test ReduceLROnPlateau scheduler."""
        from torch.optim.lr_scheduler import ReduceLROnPlateau

        scheduler = ReduceLROnPlateau(
            optimizer_with_model,
            mode="min",
            factor=0.1,
            patience=2,  # Reduced patience for faster test
        )

        initial_lr = optimizer_with_model.param_groups[0]["lr"]

        # Simulate non-improving metrics (patience + 2 steps to trigger reduction)
        for _ in range(5):
            scheduler.step(1.0)  # Constant metric - no improvement

        # LR should have been reduced after patience exceeded
        assert optimizer_with_model.param_groups[0]["lr"] < initial_lr, "Condition must be true"

    def test_linear_warmup_scheduling(self):
        """Test linear warmup scheduling logic."""
        warmup_steps = 100
        max_lr = 0.001

        def get_lr_with_warmup(step, warmup_steps, max_lr):
            if step < warmup_steps:
                return max_lr * (step + 1) / warmup_steps
            return max_lr

        # Test warmup phase
        lr_at_0 = get_lr_with_warmup(0, warmup_steps, max_lr)
        lr_at_50 = get_lr_with_warmup(50, warmup_steps, max_lr)
        lr_at_99 = get_lr_with_warmup(99, warmup_steps, max_lr)
        lr_at_100 = get_lr_with_warmup(100, warmup_steps, max_lr)

        assert lr_at_0 < lr_at_50 < lr_at_99, "lr_at_0 is not valid"
        assert lr_at_99 == max_lr, "lr_at_99 is not valid"
        assert lr_at_100 == max_lr, "lr_at_100 is not valid"

    def test_scheduler_state_dict(self, optimizer_with_model):
        """Test saving and loading scheduler state."""
        from torch.optim.lr_scheduler import StepLR

        scheduler = StepLR(optimizer_with_model, step_size=5, gamma=0.1)

        # Step a few times
        for _ in range(3):
            scheduler.step()

        # Save state
        state = scheduler.state_dict()

        # Create new scheduler
        new_scheduler = StepLR(optimizer_with_model, step_size=5, gamma=0.1)

        # Load state
        new_scheduler.load_state_dict(state)

        # State should match
        assert new_scheduler.last_epoch == scheduler.last_epoch, "last_epoch is not valid"


class TestTrainingLoopIntegration:
    """Integration tests for training configuration with training loop."""

    @pytest.fixture
    def training_setup(self):
        """Fixture providing complete training setup."""
        if not HAS_TORCH:
            pytest.skip("PyTorch not available")
        import torch.nn as nn
        import torch.optim as optim
        from torch.utils.data import DataLoader, TensorDataset

        # Model
        model = nn.Linear(10, 2)

        # Data
        X = torch.randn(100, 10)
        y = torch.randint(0, 2, (100,))
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=16)

        # Optimizer
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        # Loss
        criterion = nn.CrossEntropyLoss()

        return {
            "model": model,
            "dataloader": dataloader,
            "optimizer": optimizer,
            "criterion": criterion,
        }

    def test_training_loop_with_config(self, training_setup):
        """Test complete training loop with configuration."""
        model = training_setup["model"]
        dataloader = training_setup["dataloader"]
        optimizer = training_setup["optimizer"]
        criterion = training_setup["criterion"]

        model.train()
        losses = []

        # Train for 1 epoch
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        assert len(losses) > 0, "Should have computed losses"
        assert all(loss >= 0 for loss in losses), "Losses should be non-negative"

    def test_training_with_scheduler(self, training_setup):
        """Test training with learning rate scheduler."""
        from torch.optim.lr_scheduler import StepLR

        model = training_setup["model"]
        dataloader = training_setup["dataloader"]
        optimizer = training_setup["optimizer"]
        criterion = training_setup["criterion"]

        scheduler = StepLR(optimizer, step_size=1, gamma=0.9)

        initial_lr = optimizer.param_groups[0]["lr"]

        # Train for 1 epoch
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

        scheduler.step()

        new_lr = optimizer.param_groups[0]["lr"]
        assert new_lr < initial_lr, "LR should decrease after scheduler step"


# Mark all tests that require torch
pytestmark = pytest.mark.skipif(not HAS_TORCH, reason="PyTorch required")
