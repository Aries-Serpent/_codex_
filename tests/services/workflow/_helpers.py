"""Shared test helpers for workflow service tests."""

from __future__ import annotations

from unittest.mock import Mock


def raise_exception(exception: Exception):
    """Return a callable that always raises the supplied exception."""

    return Mock(side_effect=exception)
