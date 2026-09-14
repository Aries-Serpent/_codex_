"""Compatibility import for Prometheus rendering.

The implementation lives with the HTTP exporter so optional Prometheus
discovery and rendering behavior have one owner.
"""

from .server import render_prometheus

__all__ = ["render_prometheus"]
