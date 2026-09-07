"""Compatibility pipeline shim for `codex.cli.pipeline`."""

from __future__ import annotations


class Pipeline:
    """Simple sequential pipeline compatibility wrapper."""

    def __init__(self, steps=None):
        if steps is None:
            raise TypeError("steps cannot be None")
        self.steps = list(steps)

    def execute(self):
        results = []
        for step in self.steps:
            if callable(step):
                results.append(step())
            else:
                results.append(step)
        return results


__all__ = ["Pipeline"]
