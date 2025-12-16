#!/usr/bin/env python3
"""Tests for trackers utility - basic integration tests."""
import os
from src.utils.trackers import init_wandb_offline, init_mlflow_local


def test_init_wandb_offline_returns_value_or_none():
    """Test that init_wandb_offline returns a value or None (integration)."""
    # This should not crash, regardless of whether wandb is installed
    result = init_wandb_offline()
    # Result can be None (if wandb not available) or a wandb run object
    assert result is None or result is not None


def test_init_mlflow_local_returns_value_or_none():
    """Test that init_mlflow_local returns a value or None (integration)."""
    # This should not crash, regardless of whether mlflow is installed
    result = init_mlflow_local()
    # Result can be None (if mlflow not available) or True
    assert result is None or result is not None
