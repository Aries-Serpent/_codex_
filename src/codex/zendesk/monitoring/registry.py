"""Plugin registration entry point for Zendesk metrics."""

from __future__ import annotations

from .zendesk_metrics import register_zendesk_metrics


def register_plugins() -> None:
    """Register Zendesk-specific monitoring instruments."""

    register_zendesk_metrics()


__all__ = ["register_plugins"]
