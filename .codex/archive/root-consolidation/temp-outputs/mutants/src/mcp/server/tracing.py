"""
Tracing Module

This module provides functionality for tracing.

Usage:
    from server.tracing import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import contextlib
import importlib
import importlib.util
import logging
import os
import uuid
from collections.abc import Generator
from typing import Any

from starlette.requests import Request

logger = logging.getLogger(__name__)


def init_tracing(service_name: str = "mcp"):
    """
    Lazy OpenTelemetry bootstrap. If OTEL_EXPORTER_OTLP_ENDPOINT is set and OTel
    packages are available, initialize provider. Silently no-ops otherwise.
    """
    otlp = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otlp:
        return
    if importlib.util.find_spec("opentelemetry") is None:
        return
    if importlib.util.find_spec("opentelemetry.sdk") is None:
        return
    if importlib.util.find_spec("opentelemetry.exporter.otlp.proto.grpc.trace_exporter") is None:
        return

    trace = importlib.import_module("opentelemetry.trace")
    resource_mod = importlib.import_module("opentelemetry.sdk.resources")
    tracer_mod = importlib.import_module("opentelemetry.sdk.trace")
    export_mod = importlib.import_module("opentelemetry.sdk.trace.export")
    otlp_mod = importlib.import_module("opentelemetry.exporter.otlp.proto.grpc.trace_exporter")

    resource = resource_mod.Resource.create({"service.name": service_name})
    provider = tracer_mod.TracerProvider(resource=resource)
    provider.add_span_processor(
        export_mod.BatchSpanProcessor(otlp_mod.OTLPSpanExporter(endpoint=otlp))
    )
    trace.set_tracer_provider(provider)


def ensure_request_id(request: Request) -> str:
    """
    Ensure request has X-Request-Id (generate if missing) and attach to request.state for downstream use.
    """  # noqa: E501
    rid = request.headers.get("x-request-id")
    if not rid:
        rid = str(uuid.uuid4())
        # Note: we don't mutate headers immutable mapping; handler may read request.state.request_id
    request.state.request_id = rid
    return rid


@contextlib.contextmanager
def drift_span(
    tracer_name: str = "codex.drift",
    span_name: str = "drift.detection",
    *,
    drift_type: str = "data_drift",
    features: list[str] | None = None,
    magnitude: float | None = None,
    is_critical: bool = False,
    p_value: float | None = None,
    detector: str = "unknown",
    extra_attrs: dict[str, Any] | None = None,
) -> Generator[Any, None, None]:
    """Context manager that wraps a code block in an OTel span annotated with
    multivariate drift attributes.  If the OTel SDK is not available or
    ``OTEL_EXPORTER_OTLP_ENDPOINT`` is empty, the context manager is a no-op.

    SAR-G05: Adds multivariate drift attributes to every span so that Jaeger /
    Tempo can surface per-feature drift timelines and correlate drift events
    across the feature store, training pipeline, and serving layer.

    Span attributes set (all under the ``drift.*`` namespace):

    +---------------------------------+-------------------------------------------+
    | Attribute                       | Meaning                                   |
    +=================================+===========================================+
    | ``drift.type``                  | ``"data_drift"`` / ``"model_drift"`` /    |
    |                                 | ``"config_drift"`` etc.                   |
    +---------------------------------+-------------------------------------------+
    | ``drift.features``              | Comma-separated list of feature names     |
    |                                 | included in this drift evaluation.        |
    +---------------------------------+-------------------------------------------+
    | ``drift.features_count``        | Number of features evaluated.             |
    +---------------------------------+-------------------------------------------+
    | ``drift.magnitude``             | Aggregate drift magnitude (float 0-1).    |
    +---------------------------------+-------------------------------------------+
    | ``drift.is_critical``           | ``True`` if threshold exceeded.           |
    +---------------------------------+-------------------------------------------+
    | ``drift.p_value``               | Statistical p-value (if computed).        |
    +---------------------------------+-------------------------------------------+
    | ``drift.detector``              | Detector name / class that flagged drift. |
    +---------------------------------+-------------------------------------------+

    Additional caller-supplied attributes can be passed via *extra_attrs*.

    Args:
        tracer_name:  OTel instrumentation scope (default: ``"codex.drift"``).
        span_name:    OTel span name (default: ``"drift.detection"``).
        drift_type:   Semantic drift category.
        features:     List of feature names being evaluated.
        magnitude:    Aggregate drift magnitude (0.0–1.0).
        is_critical:  Whether the drift exceeds the critical threshold.
        p_value:      Statistical p-value, if available.
        detector:     Name of the detector class that produced this result.
        extra_attrs:  Any additional span attributes to set.

    Example::

        with drift_span(
            drift_type="data_drift",
            features=["age", "income", "credit_score"],
            magnitude=0.35,
            is_critical=True,
            p_value=0.01,
            detector="KolmogorovSmirnovDrift",
        ):
            result = detector.detect(current_stats, baseline_stats)
    """
    if importlib.util.find_spec("opentelemetry") is None:
        yield None
        return

    try:
        trace_mod = importlib.import_module("opentelemetry.trace")
        tracer = trace_mod.get_tracer(tracer_name)
    except (IOError, OSError):
        yield None
        return

    feat_list = features or []
    attrs: dict[str, Any] = {
        "drift.type": drift_type,
        "drift.features": ",".join(feat_list),
        "drift.features_count": len(feat_list),
        "drift.is_critical": is_critical,
        "drift.detector": detector,
    }
    if magnitude is not None:
        attrs["drift.magnitude"] = round(float(magnitude), 6)
    if p_value is not None:
        attrs["drift.p_value"] = round(float(p_value), 6)
    if extra_attrs:
        attrs.update(extra_attrs)

    with tracer.start_as_current_span(span_name, attributes=attrs) as span:
        yield span


def record_drift_event(
    drift_type: str,
    features: list[str],
    *,
    magnitude: float | None = None,
    is_critical: bool = False,
    p_value: float | None = None,
    detector: str = "unknown",
    extra_attrs: dict[str, Any] | None = None,
) -> None:
    """Fire-and-forget helper: add a drift span event to the *current* OTel span.

    Unlike ``drift_span()``, this does not create a new span — it adds
    structured attributes as a *span event* on whatever span is currently
    active.  If no span is active or OTel is unavailable, this is a no-op.

    Args:
        drift_type:   Semantic drift category (e.g. ``"data_drift"``).
        features:     Feature names involved in this drift event.
        magnitude:    Drift magnitude score (0.0–1.0).
        is_critical:  ``True`` if the event exceeds the critical threshold.
        p_value:      Statistical p-value, if computed.
        detector:     Detector class / name that raised this event.
        extra_attrs:  Additional event attributes.

    Example::

        record_drift_event(
            drift_type="data_drift",
            features=["age", "income"],
            magnitude=0.42,
            is_critical=True,
            p_value=0.003,
            detector="PSIDrift",
        )
    """
    if importlib.util.find_spec("opentelemetry") is None:
        return

    try:
        trace_mod = importlib.import_module("opentelemetry.trace")
        span = trace_mod.get_current_span()
    except (IOError, OSError):
        return

    attrs: dict[str, Any] = {
        "drift.type": drift_type,
        "drift.features": ",".join(features),
        "drift.features_count": len(features),
        "drift.is_critical": is_critical,
        "drift.detector": detector,
    }
    if magnitude is not None:
        attrs["drift.magnitude"] = round(float(magnitude), 6)
    if p_value is not None:
        attrs["drift.p_value"] = round(float(p_value), 6)
    if extra_attrs:
        attrs.update(extra_attrs)

    try:
        span.add_event("drift.detected", attributes=attrs)
    except (ImportError, AttributeError):
        logger.debug("Suppressed exception in handler", exc_info=True)
