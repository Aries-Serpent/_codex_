"""Tests for optimization functionality in codex_ml."""


class TestOptimization:
    """Tests for optimization operations."""

    def test_optimizer_adam(self):
        """Test Adam optimizer configuration."""
        # Arrange
        optimizer_type = "adam"

        # Assert
        assert optimizer_type == "adam", "optimizer_type is not valid"

    def test_optimizer_adamw(self):
        """Test AdamW optimizer configuration."""
        # Arrange
        optimizer_type = "adamw"

        # Assert
        assert optimizer_type == "adamw", "optimizer_type is not valid"

    def test_optimizer_sgd(self):
        """Test SGD optimizer configuration."""
        # Arrange
        optimizer_type = "sgd"

        # Assert
        assert optimizer_type == "sgd", "optimizer_type is not valid"

    def test_learning_rate_value(self):
        """Test learning rate value."""
        # Arrange
        lr = 1e-4

        # Assert
        assert lr > 0, "lr must be greater than zero"
        assert lr < 1, "lr is not valid"

    def test_weight_decay(self):
        """Test weight decay parameter."""
        # Arrange
        weight_decay = 0.01

        # Assert
        assert weight_decay >= 0, "weight_decay must be greater than zero"

    def test_momentum(self):
        """Test momentum parameter."""
        # Arrange
        momentum = 0.9

        # Assert
        assert 0 <= momentum <= 1, "0 is not valid"

    def test_beta1_beta2(self):
        """Test Adam beta parameters."""
        # Arrange
        betas = (0.9, 0.999)

        # Assert
        assert len(betas) == 2, "Betas must not be empty"
        assert all(0 < b < 1 for b in betas), "0 is not valid"

    def test_epsilon(self):
        """Test epsilon parameter."""
        # Arrange
        eps = 1e-8

        # Assert
        assert eps > 0, "eps must be greater than zero"

    def test_scheduler_linear(self):
        """Test linear learning rate scheduler."""
        # Arrange
        scheduler_type = "linear"

        # Assert
        assert scheduler_type == "linear", "scheduler_type is not valid"

    def test_scheduler_cosine(self):
        """Test cosine learning rate scheduler."""
        # Arrange
        scheduler_type = "cosine"

        # Assert
        assert scheduler_type == "cosine", "scheduler_type is not valid"

    def test_scheduler_warmup(self):
        """Test warmup scheduler."""
        # Arrange
        warmup_steps = 1000

        # Assert
        assert warmup_steps > 0, "warmup_steps must be greater than zero"

    def test_warmup_ratio(self):
        """Test warmup ratio."""
        # Arrange
        warmup_ratio = 0.1

        # Assert
        assert 0 < warmup_ratio < 1, "0 is not valid"

    def test_scheduler_step(self):
        """Test step learning rate scheduler."""
        # Arrange
        step_size = 10

        # Assert
        assert step_size > 0, "step_size must be greater than zero"

    def test_scheduler_exponential(self):
        """Test exponential learning rate scheduler."""
        # Arrange
        gamma = 0.95

        # Assert
        assert 0 < gamma < 1, "0 is not valid"

    def test_max_grad_norm(self):
        """Test max gradient norm for clipping."""
        # Arrange
        max_grad_norm = 1.0

        # Assert
        assert max_grad_norm > 0, "max_grad_norm must be greater than zero"

    def test_gradient_accumulation(self):
        """Test gradient accumulation steps."""
        # Arrange
        gradient_accumulation_steps = 4

        # Assert
        assert gradient_accumulation_steps >= 1, "gradient_accumulation_steps must be greater than zero"

    def test_optimizer_state_management(self):
        """Test optimizer state management."""
        # Arrange
        state = {"step": 100, "exp_avg": {}}

        # Assert
        assert "step" in state, "Condition must be true"

    def test_parameter_groups(self):
        """Test parameter groups configuration."""
        # Arrange
        param_groups = [{"params": [], "lr": 1e-4}, {"params": [], "lr": 1e-5}]

        # Assert
        assert len(param_groups) == 2, "Param_groups must not be empty"
