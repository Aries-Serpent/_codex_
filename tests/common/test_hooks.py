"""Smoke tests for :mod:`common.hooks`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


class _RecorderHook:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def on_init(self, state: dict[str, Any]) -> None:  # pragma: no cover - simple recorder
        self.events.append(("on_init", dict(state)))

    def on_step_end(self, state: dict[str, Any]) -> None:
        self.events.append(("on_step_end", dict(state)))


@pytest.mark.parametrize("method", ["on_init", "on_step_end"])
def test_hook_manager_dispatch(method: str) -> None:
    from common.hooks import HookManager

    hook = _RecorderHook()
    manager = HookManager([hook])
    manager.dispatch(method, {"foo": "bar"})

    assert hook.events and hook.events[0][0] == method, "Condition must be true"


def test_ndjson_log_hook(tmp_path: Path) -> None:
    from common.hooks import NDJSONLogHook

    target = tmp_path / "logs" / "events.jsonl"
    hook = NDJSONLogHook(target)

    hook.on_step_end({"loss": 0.1, "step": 5})
    hook.on_step_end({"loss": 0.2, "step": 6})

    content = target.read_text().strip().splitlines()
    assert len(content) == 2, "Content must not be empty"
    for line in content:
        data = json.loads(line)
        assert "loss" in data, "Data must not be empty"
        assert "step" in data, "Data must not be empty"
