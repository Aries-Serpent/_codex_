"""
Metrics Module

This module provides functionality for metrics.

Usage:
    from observability.metrics import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Minimal in-memory metrics facade. Replace with Prometheus/OTel exporter in later plans.
import time

_counters: dict[str, int] = {}
_timers: dict[str, float] = {}


def increment(name: str, amount: int = 1):
    _counters[name] = _counters.get(name, 0) + amount


def get_counter(name: str) -> int:
    return _counters.get(name, 0)


def get_metric(name: str) -> int:
    return _counters.get(name, 0)


class Timer:
    def __init__(self, name: str):
        self.name = name
        self._start = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.time() - (self._start or time.time())
        _timers[self.name] = _timers.get(self.name, 0.0) + elapsed
        increment(f"{self.name}_count", 1)


def snapshot() -> dict:
    return {"counters": dict(_counters), "timers": dict(_timers)}
