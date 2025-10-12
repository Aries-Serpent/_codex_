"""
Monitoring hooks for Zendesk integrations.

This package defines metrics collectors for API calls, diff operations,
and apply outcomes.  These are registered with the core monitoring
framework via the plugin registry.
"""

from .zendesk_metrics import register_zendesk_metrics

__all__ = ["register_zendesk_metrics"]
