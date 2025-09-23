# BEGIN: CODEX_PROMETHEUS
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

_FALLBACK_ACTIVE: bool = False
_FALLBACK_PATH: Optional[Path] = None
_FALLBACK_REASON: Optional[str] = None


class _FallbackSink:
    def __init__(self, destination: Path) -> None:
        if destination.suffix:
            self.path = destination
        else:
            destination.mkdir(parents=True, exist_ok=True)
            self.path = destination / "prometheus.ndjson"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, payload: Dict[str, Any]) -> None:
        record = dict(payload)
        record.setdefault("ts", datetime.now(timezone.utc).isoformat())
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


class _FallbackCounter:
    def __init__(self, name: str, description: str, sink: _FallbackSink) -> None:
        self._name = name
        self._description = description
        self._sink = sink
        self._value = 0.0

    def inc(self, amount: float = 1.0) -> None:
        self._value += float(amount)
        self._sink.write(
            {
                "metric": self._name,
                "kind": "counter",
                "delta": float(amount),
                "value": self._value,
                "description": self._description,
            }
        )


class _FallbackGauge:
    def __init__(self, name: str, description: str, sink: _FallbackSink) -> None:
        self._name = name
        self._description = description
        self._sink = sink
        self._value = 0.0

    def set(self, value: float) -> None:
        self._value = float(value)
        self._sink.write(
            {
                "metric": self._name,
                "kind": "gauge",
                "value": self._value,
                "description": self._description,
            }
        )


def maybe_export_metrics(app=None, port: int = 9000, *, fallback_dir: Path | str | None = None):
    """Start a Prometheus HTTP server or fall back to local NDJSON sinks."""

    global _FALLBACK_ACTIVE, _FALLBACK_PATH, _FALLBACK_REASON

    destination = (
        Path(fallback_dir) if fallback_dir is not None else Path("artifacts/metrics/prometheus")
    )

    try:
        from prometheus_client import Counter, Gauge, start_http_server  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        sink = _FallbackSink(destination)
        counters = {"requests_total": _FallbackCounter("requests_total", "Total requests", sink)}
        gauges = {"queue_depth": _FallbackGauge("queue_depth", "Queue depth", sink)}
        _FALLBACK_ACTIVE = True
        _FALLBACK_PATH = sink.path
        _FALLBACK_REASON = repr(exc)
        print(
            f"[prometheus] falling back to NDJSON sink at {_FALLBACK_PATH} ({_FALLBACK_REASON})",
            file=sys.stderr,
        )
        return counters, gauges

    start_http_server(port)
    _FALLBACK_ACTIVE = False
    _FALLBACK_PATH = None
    _FALLBACK_REASON = None

    counters = {"requests_total": Counter("requests_total", "Total requests")}
    gauges = {"queue_depth": Gauge("queue_depth", "Queue depth")}
    return counters, gauges


def fallback_status() -> Tuple[bool, Optional[Path], Optional[str]]:
    """Expose the state of the Prometheus fallback sink."""

    return _FALLBACK_ACTIVE, _FALLBACK_PATH, _FALLBACK_REASON


__all__ = ["maybe_export_metrics", "fallback_status"]

# END: CODEX_PROMETHEUS
