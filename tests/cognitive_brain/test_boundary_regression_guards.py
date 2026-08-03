"""Boundary regression guards for Cognitive Brain runtime.

These tests fail if future edits silently bypass the safeguards delivered in
PR #5430:

1. Session/create boundary architecture
2. Shell adversarial vector coverage
3. Entrypoint assert_loaded enforcement
4. Forensics field preservation (decision_id, turn_id, task_id)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.codex.cognitive_brain.kernel import (
    CognitiveBrainKernel,
    KernelConfig,
    assert_loaded,
    get_kernel,
    reset_kernel,
)
from src.codex.cognitive_brain.session_guard import (
    SessionCreateResult,
    SessionGuard,
    safe_create_session,
)
from src.codex.cognitive_brain.shell_policy import (
    _SHELL_METACHARACTERS,
    PolicyVerdict,
    ShellPolicy,
)
from src.codex.cognitive_brain.telemetry import (
    CognitiveTelemetry,
    InMemoryTelemetryBackend,
    NDJSONTelemetryBackend,
    TelemetryEvent,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def telemetry() -> CognitiveTelemetry:
    return CognitiveTelemetry(backends=[InMemoryTelemetryBackend()])


@pytest.fixture()
def guard(telemetry: CognitiveTelemetry) -> SessionGuard:
    return SessionGuard(telemetry=telemetry)


@pytest.fixture()
def shell_policy() -> ShellPolicy:
    return ShellPolicy(default_shell_enabled=True)


@pytest.fixture(autouse=True)
def _reset_kernel() -> None:
    """Ensure each test starts with a clean kernel singleton."""
    reset_kernel()
    yield
    reset_kernel()


# ---------------------------------------------------------------------------
# 1. Session/create boundary architecture
# ---------------------------------------------------------------------------


class TestSessionCreateBoundary:
    def test_safe_config_always_contains_model_key(self, guard: SessionGuard) -> None:
        """Every SessionGuard result must inject the resolved model key."""
        result = guard.create_session("claude-haiku-4.5", {"max_tokens": 512})
        assert isinstance(result, SessionCreateResult)
        assert "model" in result.safe_config
        assert result.safe_config["model"] == result.resolved_model

    def test_decision_id_unique_per_call(self, guard: SessionGuard) -> None:
        """Each create_session invocation must receive a unique decision_id."""
        decision_ids = {guard.create_session("claude-haiku-4.5", {}).decision_id for _ in range(50)}
        assert len(decision_ids) == 50

    def test_turn_id_and_task_id_roundtrip(self, guard: SessionGuard) -> None:
        """Caller-supplied turn/task identifiers must be preserved exactly."""
        result = guard.create_session(
            "claude-haiku-4.5",
            {},
            turn_id="turn-42",
            task_id="task-5430",
        )
        assert result.turn_id == "turn-42"
        assert result.task_id == "task-5430"

    def test_unsupported_params_stripped(self, guard: SessionGuard) -> None:
        """Unsupported params must be removed from safe_config and reported."""
        result = guard.create_session(
            "claude-haiku-4.5",
            {"reasoning_effort": "high", "max_tokens": 256},
        )
        assert "reasoning_effort" not in result.safe_config
        assert "reasoning_effort" in result.params_stripped

    def test_convenience_wrapper_uses_session_guard(self) -> None:
        """safe_create_session must produce a SessionCreateResult, not a raw dict."""
        result = safe_create_session("claude-haiku-4.5", {"max_tokens": 128})
        assert isinstance(result, SessionCreateResult)
        assert "model" in result.safe_config


# ---------------------------------------------------------------------------
# 2. Shell adversarial vector coverage
# ---------------------------------------------------------------------------


class TestShellAdversarialCoverage:
    @pytest.mark.parametrize(
        "command",
        [
            "git status; rm -rf /",
            "git status && cat /etc/passwd",
            "git status || malicious",
            "echo $(rm -rf /)",
            "echo `rm -rf /`",
            "cat file | sh",
            "echo hello > /tmp/pwned",
            "cat < /etc/passwd",
            "echo err 2> /tmp/pwned",
            "echo bg & malicious",
            "echo subshell (rm -rf /)",
            "echo brace {rm,-rf,/}",
            'echo "multi\nline"',
            "echo redirect\r\n",
        ],
    )
    def test_all_metachar_vectors_denied(
        self, shell_policy: ShellPolicy, command: str
    ) -> None:
        """Every documented shell metacharacter vector must be denied."""
        decision = shell_policy.gate(command)
        assert decision.verdict == PolicyVerdict.DENY
        assert "shell metacharacter" in decision.reason.lower()
        assert "shell_metacharacter_detected" in decision.risk_flags

    def test_deny_pattern_overrides_allow_pattern(self, shell_policy: ShellPolicy) -> None:
        """Deny patterns must take precedence over matching allow patterns."""
        decision = shell_policy.gate("sudo git status")
        assert decision.verdict == PolicyVerdict.DENY
        assert "sudo" in decision.reason.lower()

    def test_metacharacter_list_is_non_empty(self) -> None:
        """The metacharacter inventory must never be accidentally emptied."""
        assert len(_SHELL_METACHARACTERS) >= 10


# ---------------------------------------------------------------------------
# 3. Entrypoint assert_loaded enforcement
# ---------------------------------------------------------------------------


class TestAssertLoadedEnforcement:
    def test_unbooted_kernel_blocks_reasoning_with_failsafe_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Reasoning-critical methods must fail on an unbooted kernel when auto-boot is disabled."""
        monkeypatch.setenv("COGNITIVE_BRAIN_FAILSAFE_OFF", "true")
        monkeypatch.setenv("COGNITIVE_BRAIN_AUTO_LOAD", "false")
        kernel = CognitiveBrainKernel(config=KernelConfig())
        assert not kernel.is_loaded
        with pytest.raises(RuntimeError, match="not yet booted"):
            kernel.negotiate_model("claude-haiku-4.5", {})

    def test_assert_loaded_module_level_enforces_loaded_kernel(self) -> None:
        """Module-level assert_loaded must operate on an already-loaded kernel singleton."""
        # When get_kernel() auto-boots, assert_loaded() must succeed without raising.
        assert_loaded()
        assert get_kernel().is_loaded

    def test_get_kernel_returns_booted_instance(self) -> None:
        """get_kernel() must always return an initialized (loaded) kernel."""
        kernel = get_kernel()
        assert kernel.is_loaded
        # Idempotent repeated calls
        assert get_kernel() is kernel

    def test_kernel_initializes_session_guard_on_boot(self) -> None:
        """Booting the kernel must create the session guard."""
        kernel = CognitiveBrainKernel(config=KernelConfig())
        kernel.boot()
        assert kernel.is_loaded
        assert kernel._session_guard is not None


# ---------------------------------------------------------------------------
# 4. Forensics field preservation
# ---------------------------------------------------------------------------


class TestForensicsFieldPreservation:
    def test_telemetry_event_preserves_forensics_fields(self) -> None:
        """TelemetryEvent must carry decision_id, turn_id, task_id through serialization."""
        event = TelemetryEvent(
            event_type="test",
            decision_id="d-001",
            turn_id="t-42",
            task_id="task-5430",
        )
        data = event.to_dict()
        assert data["decision_id"] == "d-001"
        assert data["turn_id"] == "t-42"
        assert data["task_id"] == "task-5430"

        reloaded = json.loads(event.to_json())
        assert reloaded["decision_id"] == "d-001"
        assert reloaded["turn_id"] == "t-42"
        assert reloaded["task_id"] == "task-5430"

    def test_session_guard_telemetry_includes_forensics(
        self, guard: SessionGuard, telemetry: CognitiveTelemetry
    ) -> None:
        """SessionGuard telemetry events must include decision_id, turn_id, task_id."""
        result = guard.create_session(
            "claude-haiku-4.5",
            {},
            turn_id="t-7",
            task_id="task-5",
        )
        events = telemetry.query(event_type="session_guard")
        assert len(events) == 1
        event = events[0]
        assert event.decision_id == result.decision_id
        assert event.turn_id == "t-7"
        assert event.task_id == "task-5"

    def test_ndjson_backend_preserves_forensics(self, tmp_path: Path) -> None:
        """NDJSON serialization must not silently drop forensics fields."""
        path = tmp_path / "events.ndjson"
        backend = NDJSONTelemetryBackend(path)
        event = TelemetryEvent(
            event_type="forensics",
            decision_id="d-123",
            turn_id="t-1",
            task_id="task-1",
        )
        backend.write(event)
        reloaded = backend.read_all()[-1]
        assert reloaded.decision_id == "d-123"
        assert reloaded.turn_id == "t-1"
        assert reloaded.task_id == "task-1"

    def test_kernel_plan_tools_emits_forensics(self) -> None:
        """plan_tools must emit a forensics event with decision_id, turn_id, task_id."""
        kernel = get_kernel()
        kernel.plan_tools("repo_introspection", turn_id="t-001", task_id="pr-42")
        events = kernel.telemetry.query(event_type="forensics")
        assert len(events) >= 1
        last = events[-1]
        assert last.decision_id is not None
        assert last.turn_id == "t-001"
        assert last.task_id == "pr-42"
        assert "selected_toolchain" in last.payload
        assert "rejected_alternatives" in last.payload
