"""Boundary regression guards for Cognitive Brain runtime.

These tests fail if future edits silently bypass the safeguards delivered in
PR #5430:

1. Session/create boundary architecture
2. Shell adversarial vector coverage
3. Entrypoint assert_loaded enforcement
4. Forensics field preservation (decision_id, turn_id, task_id)
5. Required check-name contract governance
6. Legacy quarantine schema integrity
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
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
# 1b. Negative architecture test — no new direct session.create paths
# ---------------------------------------------------------------------------


class TestNoDirectSessionCreatePaths:
    """Fail the suite if any new production path bypasses SessionGuard."""

    # Files that already legitimately create raw sessions outside SessionGuard.
    ALLOWLIST: set[str] = set()

    def test_cognitive_brain_source_has_no_unapproved_create_session(self) -> None:
        """All session.create calls must route through SessionGuard."""
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        src_dir = repo_root / "src" / "codex" / "cognitive_brain"
        violations: list[str] = []
        for py_file in sorted(src_dir.rglob("*.py")):
            text = py_file.read_text(encoding="utf-8")
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = self._call_name(node.func)
                if name.endswith(".create") or name.endswith(".create_session"):
                    rel = str(py_file.relative_to(repo_root))
                    if rel in self.ALLOWLIST:
                        continue
                    # Calls routed through a SessionGuard instance are allowed.
                    if self._is_session_guard_call(node):
                        continue
                    violations.append(f"{rel}:{node.lineno} {name}()")
        assert not violations, (
            "Direct session.create paths detected; add to SessionGuard or allowlist: "
            + "; ".join(violations)
        )

    @staticmethod
    def _is_session_guard_call(node: ast.Call) -> bool:
        """Return True if the call is on a SessionGuard attribute (e.g. guard.create_session)."""
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in ("create", "create_session"):
            receiver = func.value
            if isinstance(receiver, ast.Name):
                # Heuristic: variable name ends with _guard or is named guard.
                if receiver.id.endswith("_guard") or receiver.id == "guard":
                    return True
            if isinstance(receiver, ast.Attribute) and receiver.attr.endswith("_guard"):
                return True
        return False

    def test_session_guard_module_is_present(self) -> None:
        """The SessionGuard module must remain importable and contain the expected API."""
        from src.codex.cognitive_brain import session_guard

        assert hasattr(session_guard, "SessionGuard")
        assert hasattr(session_guard, "safe_create_session")

    @staticmethod
    def _call_name(func: ast.expr) -> str:
        if isinstance(func, ast.Attribute):
            parts: list[str] = []
            node: ast.expr = func
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
            return ".".join(reversed(parts))
        if isinstance(func, ast.Name):
            return func.id
        return ""


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
# 2b. Required check-name drift guard
# ---------------------------------------------------------------------------


class TestRequiredCheckNameContract:
    """Mirror the Phase 1 required-check contract to detect governance drift."""

    # These must match the job `name:` values in cognitive-brain-required-gate.yml.
    CONTRACT = {
        "Ruff lint (cognitive_brain)",
        "Mypy type check (cognitive_brain)",
        "Targeted pytest (cognitive_brain core)",
        "Regression guard (cognitive_brain)",
    }

    def test_required_gate_job_names_match_contract(self) -> None:
        gate = pathlib.Path(".github/workflows/cognitive-brain-required-gate.yml")
        assert gate.exists(), f"Required gate workflow missing: {gate}"
        text = gate.read_text(encoding="utf-8")
        jobs_pos = text.find("jobs:")
        assert jobs_pos != -1, "Could not locate jobs: section in required gate"
        found = set(re.findall(r"^    name: (.+)$", text[jobs_pos:], flags=re.MULTILINE))
        assert found == self.CONTRACT, (
            f"Required gate job names {sorted(found)} do not match contract {sorted(self.CONTRACT)}"
        )


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


# ---------------------------------------------------------------------------
# 5. Legacy quarantine schema integrity
# ---------------------------------------------------------------------------


class TestLegacyQuarantineSchema:
    """Validate the structure of LEGACY_TEST_DEBT_QUARANTINE.md."""

    def test_quarantine_file_exists(self) -> None:
        path = pathlib.Path("docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md")
        assert path.exists(), "Legacy debt quarantine file is missing"

    def test_quarantine_summary_table_has_expected_columns(self) -> None:
        path = pathlib.Path("docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md")
        content = path.read_text(encoding="utf-8")
        # Find the summary table.
        match = re.search(
            r"## Quarantine Summary\s*\n\s*\n\|(.+?)\|\s*\n\|[-:\s|]+\|\s*\n",
            content,
        )
        assert match, "Quarantine Summary table not found or malformed"
        header = match.group(1)
        cells = [c.strip() for c in header.split("|") if c.strip()]
        assert "Metric" in cells, "Summary table missing 'Metric' column"
        assert "Count" in cells, "Summary table missing 'Count' column"

    def test_trend_table_schema(self) -> None:
        path = pathlib.Path("docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md")
        content = path.read_text(encoding="utf-8")
        # Look for the trend table header; if present, validate columns.
        if "## Trend Table" not in content:
            pytest.skip("Trend table not yet added")
        match = re.search(
            r"## Trend Table\s*\n\s*\n\|(.+?)\|\s*\n\|[-:\s|]+\|\s*\n",
            content,
        )
        assert match, "Trend table header malformed"
        header = match.group(1)
        cells = [c.strip() for c in header.split("|") if c.strip()]
        expected = ["Snapshot Date", "Failed", "Errored", "Total", "Delta vs Previous", "Top Cause"]
        assert cells == expected, f"Trend table columns {cells} do not match expected {expected}"

    def test_detailed_failure_counts_table_integrity(self) -> None:
        path = pathlib.Path("docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md")
        content = path.read_text(encoding="utf-8")
        assert "## Detailed Failure Counts" in content, "Detailed Failure Counts section missing"
        match = re.search(
            r"## Detailed Failure Counts\s*\n\s*\n\|(.+?)\|\s*\n\|[-:\s|]+\|\s*\n",
            content,
        )
        assert match, "Detailed Failure Counts table header malformed"
        header = match.group(1)
        cells = [c.strip() for c in header.split("|") if c.strip()]
        assert "File" in cells
        assert "Failed" in cells
        assert "Errored" in cells

    def test_total_row_present(self) -> None:
        path = pathlib.Path("docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md")
        content = path.read_text(encoding="utf-8")
        assert re.search(
            r"\|\s*\*\*Total\*\*\s*\|\s*\*\*\d+\*\*\s*\|\s*\*\*\d+\*\*\s*\|",
            content,
        ), "Total row in Detailed Failure Counts table is missing or malformed"
