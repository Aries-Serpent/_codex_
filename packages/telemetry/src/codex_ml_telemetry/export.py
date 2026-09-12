"""Prometheus text export without framework coupling."""

from __future__ import annotations

from typing import Any

try:
    from prometheus_client import REGISTRY, generate_latest
except ImportError:  # pragma: no cover - exercised in minimal installations
    REGISTRY = None
    generate_latest = None


def render_prometheus(registry: Any = None) -> str:
    """Render a registry using the Prometheus text exposition format."""

    if generate_latest is None:
        return "# prometheus_client not installed\n"

    payload = generate_latest(registry or REGISTRY)
    return payload.decode("utf-8")


__all__ = ["render_prometheus"]
