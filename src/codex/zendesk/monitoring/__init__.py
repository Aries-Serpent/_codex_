"""Monitoring hooks for Zendesk integrations."""

from __future__ import annotations

from .zendesk_metrics import register_zendesk_metrics

__all__ = ["register_zendesk_metrics"]
