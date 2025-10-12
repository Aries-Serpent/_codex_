from __future__ import annotations

from common.hooks import BaseHook, HookManager


class CounterHook(BaseHook):
    def __init__(self) -> None:
        self.count = 0

    def on_step_end(self, state):  # type: ignore[override]
        self.count += 1


def test_hook_dispatch() -> None:
    hooks = [CounterHook(), CounterHook()]
    manager = HookManager(hooks)
    manager.dispatch("on_step_end", {})
    manager.dispatch("on_step_end", {})
    assert sum(h.count for h in hooks) == 4
