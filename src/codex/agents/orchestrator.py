"""Minimal orchestrator compatibility shim."""

from __future__ import annotations

import threading


class Orchestrator:
    """A lightweight, thread-safe compatibility orchestrator."""

    def __init__(self):
        self.state = "idle"
        self._lock = threading.RLock()

    def execute(self, command=None, **kwargs):
        if command is None or not str(command).strip():
            raise ValueError("command must be a non-empty string")
        with self._lock:
            self.state = "running"
            result = {"status": "ok", "command": str(command)}
            self.state = "idle"
            return result


__all__ = ["Orchestrator"]
