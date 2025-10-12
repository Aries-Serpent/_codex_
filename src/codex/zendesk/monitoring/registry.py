"""
Plugin registry for Zendesk monitoring hooks.

This module exposes a registration function that can be discovered by the
`_codex_` extensibility framework.  At runtime, the core framework will
call ``register_plugins()`` to register Zendesk metrics.
"""

from codex.zendesk.monitoring.zendesk_metrics import register_zendesk_metrics


def register_plugins() -> None:
    """Entry point for the `_codex_` plugin loader."""

    register_zendesk_metrics()
