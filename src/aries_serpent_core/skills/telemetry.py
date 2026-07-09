"""Telemetry sink for Cognitive Brain Skills.

Supports two export channels:

1. **JSONL file** – appends one JSON record per invocation to
   ``logs/skill_events.jsonl`` (path configurable via
   ``CODEX_SKILL_TELEMETRY_PATH`` env var).

2. **OpenTelemetry** – emits a span when ``OTEL_EXPORTER_OTLP_ENDPOINT`` is
   set and the ``opentelemetry`` SDK is installed.  Lazy import so the module
   loads cleanly in environments without OTel.

Usage (programmatic)::

    from codex.skills.telemetry import emit_event
    emit_event(skill_id="doc.retriever.core", version="1.0.0",
               status="ok", metrics=result.metrics, trace_id="abc")

Usage (CLI push)::

    codex-skill telemetry push \\
        --from logs/skill_events.jsonl \\
        --to file|discussions|app \\
        --summary
"""

from __future__ import annotations

import contextlib
import importlib
import importlib.util
import json
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from .models import BudgetUsed, ExecutionMetrics, TelemetryEvent

logger = logging.getLogger(__name__)

_ENV_TELEMETRY_PATH = "CODEX_SKILL_TELEMETRY_PATH"
_DEFAULT_TELEMETRY_PATH = "logs/skill_events.jsonl"


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------


def _telemetry_path() -> Path:
    return Path(os.environ.get(_ENV_TELEMETRY_PATH, _DEFAULT_TELEMETRY_PATH))


def _append_jsonl(record: dict[str, Any]) -> None:
    """Append *record* as one JSON line to the telemetry file."""
    path = _telemetry_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError as exc:  # pragma: no cover
        logger.debug("Telemetry: cannot write JSONL to '%s': %s", path, exc)


def _validated_push_endpoint(endpoint: str) -> str:
    """Allow only credential-free HTTP(S) telemetry endpoints."""
    parts = urlsplit(endpoint)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError(f"Telemetry endpoint must be http(s) with host: {endpoint!r}")
    if parts.username or parts.password:
        raise ValueError("Telemetry endpoint must not contain embedded credentials")
    return endpoint


# ---------------------------------------------------------------------------
# OTel helpers
# ---------------------------------------------------------------------------

# Single-element list sentinel; mutation avoids a `global` statement and the
# associated CodeQL "unused global variable" (py/unused-global-variable) alert.
_OTLP_PROVIDER_CONFIGURED: list[bool] = [False]


def _configure_otlp_if_needed(trace_mod: Any) -> None:
    """Configure an OTLP span exporter when OTEL_EXPORTER_OTLP_ENDPOINT is set.

    Called lazily from :func:`_skill_span` on first use.  Idempotent — the
    tracer provider is set at most once per process.  Silently skips when the
    ``opentelemetry-sdk`` or ``opentelemetry-exporter-otlp`` packages are not
    installed.
    """
    if _OTLP_PROVIDER_CONFIGURED[0]:
        return
    _OTLP_PROVIDER_CONFIGURED[0] = True  # set early so we never retry on ImportError

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not endpoint:
        return

    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
        )

        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        # Register as the global provider so get_tracer() picks it up
        trace_mod.set_tracer_provider(provider)
        logger.debug("OTel OTLP exporter configured: %s", endpoint)
    except ImportError:
        logger.debug(
            "OTel OTLP SDK not installed; OTEL_EXPORTER_OTLP_ENDPOINT=%r ignored", endpoint
        )


@contextlib.contextmanager
def _skill_span(skill_id: str, version: str, trace_id: str, attrs: dict[str, Any]) -> None:
    """Yield an OTel span for a skill invocation, or yield None as a no-op."""
    if importlib.util.find_spec("opentelemetry") is None:
        yield None
        return

    try:
        trace_mod = importlib.import_module("opentelemetry.trace")
        _configure_otlp_if_needed(trace_mod)
        tracer = trace_mod.get_tracer("codex.skills")
    except (IOError, OSError):
        yield None
        return

    with tracer.start_as_current_span(
        f"skill.{skill_id}",
        attributes={
            "skill.id": skill_id,
            "skill.version": version,
            "skill.trace_id": trace_id,
            **{f"skill.{k}": v for k, v in attrs.items()},
        },
    ) as span:
        yield span


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def emit_event(
    *,
    skill_id: str,
    version: str,
    status: Literal["ok", "error"],
    metrics: ExecutionMetrics,
    trace_id: str,
    emit_jsonl: bool = True,
    emit_otel: bool = False,
) -> TelemetryEvent:
    """Emit a telemetry event for one skill execution.

    Parameters
    ----------
    skill_id:
        The skill's dotted identifier.
    version:
        Skill version string.
    status:
        ``"ok"`` or ``"error"``.
    metrics:
        :class:`ExecutionMetrics` from the execution result.
    trace_id:
        Correlation ID for the invocation.
    emit_jsonl:
        Whether to write a JSONL record.
    emit_otel:
        Whether to emit an OTel span event.

    Returns
    -------
    TelemetryEvent
        The event that was emitted.
    """
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    event = TelemetryEvent(
        ts=ts,
        skill_id=skill_id,
        version=version,
        status=status,
        latency_ms=metrics.latency_ms,
        budget_used=metrics.budget_used or BudgetUsed(),
        aais_score=metrics.aais_score,
        compression_ratio=metrics.compression_ratio,
        trace_id=trace_id,
    )

    if emit_jsonl:
        _append_jsonl(event.model_dump())

    if emit_otel:
        with _skill_span(
            skill_id, version, trace_id, {"status": status, "latency_ms": metrics.latency_ms}
        ):
            pass  # span is recorded on exit

    return event


def read_events(path: Path | None = None) -> list[TelemetryEvent]:
    """Read all :class:`TelemetryEvent` records from a JSONL file.

    Parameters
    ----------
    path:
        Override path (default: value of ``CODEX_SKILL_TELEMETRY_PATH``).
    """
    fpath = path or _telemetry_path()
    if not fpath.exists():
        return []
    events: list[TelemetryEvent] = []
    with fpath.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(TelemetryEvent.model_validate_json(line))
            except (ValueError, TypeError) as exc:
                logger.debug("Telemetry: skipping malformed line: %s", exc)
    return events


def summarise_events(events: list[TelemetryEvent]) -> dict[str, Any]:
    """Return a summary dict suitable for Discussions or app posting.

    Returns
    -------
    dict with keys: total, ok, error, skills, avg_latency_ms, avg_aais_score.
    """
    total = len(events)
    ok_count = sum(1 for e in events if e.status == "ok")
    skill_set = sorted({e.skill_id for e in events})
    latencies = [e.latency_ms for e in events if e.latency_ms is not None]
    aais_scores = [e.aais_score for e in events if e.aais_score is not None]

    return {
        "total": total,
        "ok": ok_count,
        "error": total - ok_count,
        "skills": skill_set,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0,
        "avg_aais_score": round(sum(aais_scores) / len(aais_scores), 4) if aais_scores else None,
    }


@contextlib.contextmanager
def skill_invocation_span(
    skill_name: str,
    *,
    capability_tags: list[str] | None = None,
    enforcement_tier: str = "UNSPECIFIED",
    budget_tokens: int | None = None,
    timeout_ms: int | None = None,
    doc_path: str | None = None,
    tracer_name: str = "codex.skill",
) -> None:
    """Context manager wrapping a skill execution in an OTel span.

    Compatible with the research-branch ``SkillExecutionEnvelope``; also
    accepts raw kwargs so callers need not construct the dataclass.

    Yields the span (or None when OTel is unavailable) and records
    duration + outcome on exit.

    Usage::

        with skill_invocation_span("doc.retriever.core", capability_tags=["docs"]):
            result = handler(payload)
    """
    attrs: dict[str, Any] = {
        "skill.name": skill_name,
        "skill.capability_tags": ",".join(capability_tags or []),
        "skill.enforcement_tier": enforcement_tier,
    }
    if budget_tokens is not None:
        attrs["skill.budget_tokens"] = budget_tokens
    if timeout_ms is not None:
        attrs["skill.timeout_ms"] = timeout_ms
    if doc_path is not None:
        attrs["skill.doc_path"] = doc_path

    start = time.monotonic()
    if importlib.util.find_spec("opentelemetry") is None:
        yield None
        logger.debug(
            "Skill '%s' executed without OTel (no SDK) in %.1f ms",
            skill_name,
            (time.monotonic() - start) * 1000,
        )
        return

    try:
        trace_mod = importlib.import_module("opentelemetry.trace")
        tracer = trace_mod.get_tracer(tracer_name)
    except (IOError, OSError) as exc:
        logger.debug("OTel tracer unavailable: %s", exc)
        yield None
        return

    with tracer.start_as_current_span(f"skill.{skill_name}", attributes=attrs) as span:
        outcome = {"skill.outcome": "success"}
        try:
            yield span
        except (ImportError, AttributeError) as exc:
            outcome = {"skill.outcome": "error", "skill.error": str(exc)}
            raise
        finally:
            duration_ms = (time.monotonic() - start) * 1000
            if span:
                span.set_attribute("skill.duration_ms", duration_ms)
                for k, v in outcome.items():
                    try:
                        span.set_attribute(k, v)
                    except (ImportError, AttributeError):
                        logger.debug("Suppressed exception in handler", exc_info=True)
            logger.info(
                "Skill '%s' completed (%s) in %.1f ms",
                skill_name,
                outcome.get("skill.outcome", "unknown"),
                duration_ms,
            )


def push_to_app(events: list[TelemetryEvent], endpoint: str) -> bool:
    """POST telemetry events to a Cognitive Brain app HTTP endpoint.

    Parameters
    ----------
    events:
        List of events to push.
    endpoint:
        Full URL of the ingest endpoint.

    Returns
    -------
    bool
        True if push succeeded.
    """
    if not events:
        return True

    if importlib.util.find_spec("httpx") is not None:
        httpx = importlib.import_module("httpx")
        try:
            payload = [e.model_dump() for e in events]
            resp = httpx.post(_validated_push_endpoint(endpoint), json=payload, timeout=30)
            resp.raise_for_status()
            logger.info("Telemetry: pushed %d events to %s", len(events), endpoint)
            return True
        except (ValueError, TypeError) as exc:
            logger.error("Telemetry: push to app failed: %s", exc)
            return False

    # Fallback: stdlib urllib
    import json as _json
    import urllib.error
    import urllib.request

    try:
        data = _json.dumps([e.model_dump() for e in events]).encode()
        req = urllib.request.Request(
            _validated_push_endpoint(endpoint),
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(  # nosec B310 - endpoint from env/config  # nosemgrep: semgrep.urllib-urlopen-dynamic -- endpoint is validated by _validated_push_endpoint()
            req, timeout=30
        ):
            pass
        logger.info("Telemetry: pushed %d events to %s", len(events), endpoint)
        return True
    except (urllib.error.URLError, OSError) as exc:
        logger.error("Telemetry: push to app failed: %s", exc)
        return False


__all__ = [
    "TelemetryEvent",
    "emit_event",
    "push_to_app",
    "read_events",
    "skill_invocation_span",
    "summarise_events",
]
