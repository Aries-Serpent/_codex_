"""Compatibility package for the legacy `codex.cli` import contract."""

from __future__ import annotations

import argparse


class CLI:
    """Very small compatibility CLI wrapper used by legacy tests."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def execute(self, command=None, **kwargs):
        if command is None:
            raise ValueError("command is required")
        return {"status": "ok", "command": str(command)}


def parse_arguments(argv=None):
    if argv is None:
        raise TypeError("argv cannot be None")
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--value", default=None)
    args, _ = parser.parse_known_args(list(argv))
    return args


__all__ = ["CLI", "parse_arguments"]
