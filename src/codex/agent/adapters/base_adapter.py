"""Minimal compatibility adapter for legacy `codex.agent.adapters` imports."""

from __future__ import annotations

from copy import deepcopy


class BaseAdapter:
    """Small compatibility adapter used by legacy edge-case tests."""

    def __init__(self, config=None, **kwargs):
        if config is None:
            raise ValueError("config is required")
        if not isinstance(config, dict):
            raise TypeError("config must be a dict")
        self.config = deepcopy(config)
        self.name = self.config.get("name", "adapter")
        if self.name is None or self.name == "":
            raise ValueError("adapter name cannot be empty")
        self.state = "initialized"

    def execute(self, task=None, **kwargs):
        raise NotImplementedError("BaseAdapter.execute() must be implemented by subclasses")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


__all__ = ["BaseAdapter"]
