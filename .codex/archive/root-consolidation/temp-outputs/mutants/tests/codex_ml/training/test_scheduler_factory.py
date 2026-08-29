"""
Test Scheduler Factory

Test module for scheduler factory.
"""

import pytest


class TestSchedulerTypeConstant:
    """Test scheduler type constant."""

    def test_scheduler_type_available(self):
        """Test SchedulerType is available."""
        try:
            from codex_ml.training.scheduler_factory import SchedulerType

            assert SchedulerType is not None, "SchedulerType must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestCreateScheduler:
    """Test create_scheduler function."""

    def test_create_scheduler_constant(self):
        """Test creating constant scheduler."""
        try:
            import torch
            from codex_ml.training.scheduler_factory import create_scheduler

            # Use a real PyTorch optimizer with a tensor parameter
            param = torch.tensor([0.01], requires_grad=True)
            optimizer = torch.optim.SGD([param], lr=0.01)
            scheduler = create_scheduler(optimizer, scheduler_type="constant")
            assert scheduler is not None, "scheduler must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_create_scheduler_with_warmup(self):
        """Test creating scheduler with warmup steps."""
        try:
            import torch
            from codex_ml.training.scheduler_factory import create_scheduler

            # Use a real PyTorch optimizer with a tensor parameter
            param = torch.tensor([0.01], requires_grad=True)
            optimizer = torch.optim.SGD([param], lr=0.01)
            scheduler = create_scheduler(
                optimizer,
                scheduler_type="constant_with_warmup",
                num_warmup_steps=100,
                num_training_steps=1000,
            )
            assert scheduler is not None, "scheduler must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_create_scheduler_linear(self):
        """Test creating linear scheduler."""
        try:
            import torch
            from codex_ml.training.scheduler_factory import create_scheduler

            # Use a real PyTorch optimizer with a tensor parameter
            param = torch.tensor([0.01], requires_grad=True)
            optimizer = torch.optim.SGD([param], lr=0.01)
            scheduler = create_scheduler(
                optimizer, scheduler_type="linear", num_training_steps=1000
            )
            assert scheduler is not None, "scheduler must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_create_scheduler_cosine(self):
        """Test creating cosine scheduler."""
        try:
            import torch
            from codex_ml.training.scheduler_factory import create_scheduler

            # Use a real PyTorch optimizer with a tensor parameter
            param = torch.tensor([0.01], requires_grad=True)
            optimizer = torch.optim.SGD([param], lr=0.01)
            scheduler = create_scheduler(
                optimizer, scheduler_type="cosine", num_training_steps=1000
            )
            assert scheduler is not None, "scheduler must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")
