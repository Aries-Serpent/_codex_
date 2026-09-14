from __future__ import annotations

import math
import time
from pathlib import Path

import pytest

from codex_ml.plugins.plugin_sandbox import (
    Plugin,
    PluginContract,
    PluginSandbox,
    PluginStatus,
)


class _TimedPlugin(Plugin):
    def __init__(
        self,
        *,
        timeout: float,
        delay: float = 0,
        marker: Path | None = None,
    ) -> None:
        super().__init__()
        self.timeout = timeout
        self.delay = delay
        self.marker = marker

    def initialize(self) -> bool:
        return True

    def execute(self, value: object = None) -> object:
        time.sleep(self.delay)
        if self.marker is not None:
            self.marker.write_text("completed", encoding="utf-8")
        return value

    def cleanup(self) -> None:
        return None

    def get_contract(self) -> PluginContract:
        return PluginContract(
            required_methods=["initialize", "execute", "cleanup"],
            max_execution_time=self.timeout,
        )


def test_execute_sandboxed_returns_result_before_contract_timeout() -> None:
    plugin = _TimedPlugin(timeout=1)
    sandbox = PluginSandbox()

    assert sandbox.execute_sandboxed(plugin, "execute", {"ok": True}) == {"ok": True}

    health = sandbox.get_health_status(plugin.name)
    assert health is not None
    assert health.status is PluginStatus.ENABLED
    assert health.failure_count == 0
    assert health.last_success is not None


@pytest.mark.parametrize("timeout", [0, -1, math.inf, math.nan, True])
def test_plugin_contract_rejects_invalid_execution_timeout(timeout: object) -> None:
    with pytest.raises(ValueError, match="finite positive number"):
        PluginContract(max_execution_time=timeout)  # type: ignore[arg-type]


def test_timeout_terminates_execution_and_quarantines_plugin(tmp_path: Path) -> None:
    marker = tmp_path / "completed"
    plugin = _TimedPlugin(timeout=0.05, delay=0.5, marker=marker)
    sandbox = PluginSandbox()

    started = time.monotonic()
    assert sandbox.execute_sandboxed(plugin) is None
    elapsed = time.monotonic() - started

    health = sandbox.get_health_status(plugin.name)
    assert elapsed < 0.4
    assert health is not None
    assert health.status is PluginStatus.QUARANTINED
    assert health.failure_count == 1
    assert health.last_error == "TimeoutError"

    time.sleep(0.55)
    assert not marker.exists(), "timed-out plugin code must not continue in the background"


def test_quarantined_plugin_is_not_reexecuted(tmp_path: Path) -> None:
    marker = tmp_path / "completed"
    plugin = _TimedPlugin(timeout=0.05, delay=0.5, marker=marker)
    sandbox = PluginSandbox(quarantine_duration=60)

    assert sandbox.execute_sandboxed(plugin) is None
    plugin.delay = 0
    assert sandbox.execute_sandboxed(plugin) is None
    assert not marker.exists()

    health = sandbox.get_health_status(plugin.name)
    assert health is not None
    assert health.failure_count == 1
    assert health.status is PluginStatus.QUARANTINED


def test_manual_enable_clears_quarantine_metadata(tmp_path: Path) -> None:
    plugin = _TimedPlugin(timeout=0.05, delay=0.5, marker=tmp_path / "completed")
    sandbox = PluginSandbox()

    assert sandbox.execute_sandboxed(plugin) is None
    quarantined_health = sandbox.get_health_status(plugin.name)
    assert quarantined_health is not None
    assert quarantined_health.quarantined_at is not None

    sandbox.enable_plugin(plugin.name)

    health = sandbox.get_health_status(plugin.name)
    assert health is not None
    assert health.status is PluginStatus.ENABLED
    assert health.failure_count == 0
    assert health.quarantined_at is None
