"""Shared test helpers for workflow service tests."""

from __future__ import annotations

from unittest.mock import Mock


def raise_exception(exception: Exception):
    """Return a callable that always raises the supplied exception.

    Designed for monkeypatch.setattr scenarios where a method or function
    should be replaced with one that always raises.

    Args:
        exception: Exception instance to raise when called.

    Returns:
        Mock: Mock configured to raise the exception when called.
    """

    return Mock(side_effect=exception)
