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
            assert SchedulerType is not None
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestCreateScheduler:
    """Test create_scheduler function."""

    def test_create_scheduler_constant(self):
        """Test creating constant scheduler."""
        try:
            from codex_ml.training.scheduler_factory import create_scheduler
            
            class DummyOptimizer:
                pass
            
            optimizer = DummyOptimizer()
            scheduler = create_scheduler(optimizer, scheduler_type="constant")
            assert scheduler is not None
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_create_scheduler_with_warmup(self):
        """Test creating scheduler with warmup steps."""
        try:
            from codex_ml.training.scheduler_factory import create_scheduler
            
            class DummyOptimizer:
                pass
            
            optimizer = DummyOptimizer()
            scheduler = create_scheduler(
                optimizer,
                scheduler_type="constant_with_warmup",
                num_warmup_steps=100
            )
            assert scheduler is not None
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_create_scheduler_linear(self):
        """Test creating linear scheduler."""
        try:
            from codex_ml.training.scheduler_factory import create_scheduler
            
            class DummyOptimizer:
                pass
            
            optimizer = DummyOptimizer()
            scheduler = create_scheduler(
                optimizer,
                scheduler_type="linear",
                num_training_steps=1000
            )
            assert scheduler is not None
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_create_scheduler_cosine(self):
        """Test creating cosine scheduler."""
        try:
            from codex_ml.training.scheduler_factory import create_scheduler
            
            class DummyOptimizer:
                pass
            
            optimizer = DummyOptimizer()
            scheduler = create_scheduler(
                optimizer,
                scheduler_type="cosine",
                num_training_steps=1000
            )
            assert scheduler is not None
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")
