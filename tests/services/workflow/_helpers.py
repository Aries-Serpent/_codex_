"""Shared test helpers for workflow service tests."""

from __future__ import annotations


def raise_exception(exception: Exception):
    """Return a callable that always raises the supplied exception."""

    def _raiser(*_args, **_kwargs):
        raise exception

    return _raiser
