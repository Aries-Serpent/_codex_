"""Distributed tracing stub.

See docs/adr/ADR-0001-distributed-tracing.md for the deferred decision.
Activate real OTEL tracing by setting CODEX_TRACING_NOOP=0 and providing
OTEL_EXPORTER_OTLP_ENDPOINT in the environment.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator

_NOOP: bool = os.getenv("CODEX_TRACING_NOOP", "1") == "1"


@contextmanager
def trace_span(name: str, **attributes: Any) -> Generator[None, None, None]:
    """Context manager that creates a trace span (no-op until OTEL is wired)."""
    if not _NOOP:
        # Future: replace with opentelemetry.trace.get_tracer(__name__).start_as_current_span
        pass
    yield


def get_tracer(name: str = "codex") -> "_NoopTracer":
    """Return a tracer instance (no-op stub until OTEL infrastructure is available)."""
    return _NoopTracer()


class _NoopTracer:
    """No-op tracer that silently discards all spans."""

    @contextmanager
    def start_as_current_span(
        self, name: str, **kwargs: Any
    ) -> Generator["_NoopTracer", None, None]:
        yield self

    def set_attribute(self, key: str, value: Any) -> None:
        pass
