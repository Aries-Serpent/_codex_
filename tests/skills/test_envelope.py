"""Tests for the ExecutionEnvelope."""

from __future__ import annotations

import sys
import time

import pytest

from codex.skills.envelope import ExecutionEnvelope
from codex.skills.models import (
    BudgetConfig,
    DocMeta,
    PolicyConfig,
    SkillManifest,
    TelemetryConfig,
)
from codex.skills.registry import SkillRegistry, reset_registry


@pytest.fixture(autouse=True)
def fresh_registry():
    reset_registry()
    yield
    reset_registry()


def _make_manifest(skill_id="test.skill", **kwargs) -> SkillManifest:
    defaults = dict(
        id=skill_id,
        version="1.0.0",
        name="Test",
        entrypoint="tests.skills.test_envelope:_echo_handler",
        policy=PolicyConfig(budgets=BudgetConfig(calls=100, tokens=50_000, wallclock_ms=5_000)),
        telemetry=TelemetryConfig(emit_jsonl=False, emit_otel=False),
        doc=DocMeta(doc_id="test_doc_v1", aais_score=0.9),
    )
    defaults.update(kwargs)
    return SkillManifest(**defaults)


def _echo_handler(payload: dict) -> dict:
    """Simple handler that echoes the payload."""
    return {"echo": payload}


def _error_handler(payload: dict) -> dict:
    raise ValueError("intentional error")


def _slow_handler(payload: dict) -> dict:
    time.sleep(10)
    return {}


class TestExecutionEnvelopeSuccess:
    def test_run_echo_skill(self):
        reg = SkillRegistry()
        manifest = _make_manifest(entrypoint="tests.skills.test_envelope:_echo_handler")
        reg.register(manifest)
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {"hello": "world"})
        assert result.status == "ok"
        assert result.data == {"echo": {"hello": "world"}}

    def test_result_has_trace_id(self):
        reg = SkillRegistry()
        reg.register(_make_manifest())
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {})
        assert result.trace_id
        assert len(result.trace_id) > 10

    def test_latency_ms_recorded(self):
        reg = SkillRegistry()
        reg.register(_make_manifest())
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {})
        assert result.metrics.latency_ms >= 0

    def test_budget_consumed_after_run(self):
        reg = SkillRegistry()
        reg.register(_make_manifest())
        env = ExecutionEnvelope(reg)
        env.run("test.skill", {})
        skill = reg.resolve("test.skill")
        assert skill.budget_used["calls"] == 1  # type: ignore[index]


class TestExecutionEnvelopeErrors:
    def test_skill_not_found(self):
        reg = SkillRegistry()
        env = ExecutionEnvelope(reg)
        result = env.run("nonexistent.skill", {})
        assert result.status == "error"
        assert result.error is not None
        assert result.error.type == "SkillNotFound"

    def test_handler_exception(self):
        reg = SkillRegistry()
        reg.register(_make_manifest(entrypoint="tests.skills.test_envelope:_error_handler"))
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {})
        assert result.status == "error"
        assert result.error is not None
        assert "intentional error" in result.error.message

    def test_invalid_entrypoint(self):
        reg = SkillRegistry()
        reg.register(_make_manifest(entrypoint="no_colon_format"))
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {})
        assert result.status == "error"
        assert result.error.type == "HandlerLoadError"  # type: ignore[union-attr]

    def test_missing_module(self):
        reg = SkillRegistry()
        reg.register(_make_manifest(entrypoint="nonexistent.module:handler"))
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {})
        assert result.status == "error"


class TestExecutionEnvelopePolicy:
    def test_allowlist_blocks_caller(self):
        reg = SkillRegistry()
        reg.register(_make_manifest(
            policy=PolicyConfig(
                allowlist=["allowed-agent"],
                budgets=BudgetConfig(calls=100, tokens=10_000, wallclock_ms=5_000),
            )
        ))
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {}, caller_id="unknown-agent")
        assert result.status == "error"
        assert result.error.type == "PolicyViolation"  # type: ignore[union-attr]

    def test_allowlist_star_allows_all(self):
        reg = SkillRegistry()
        reg.register(_make_manifest())
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {}, caller_id="any-agent")
        assert result.status == "ok"

    def test_budget_exhaustion_blocks(self):
        reg = SkillRegistry()
        manifest = _make_manifest(
            policy=PolicyConfig(
                budgets=BudgetConfig(calls=1, tokens=10_000, wallclock_ms=5_000),
            )
        )
        reg.register(manifest)
        # Exhaust budget
        reg.consume_budget("test.skill", calls=1)
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {})
        assert result.status == "error"
        assert result.error.type == "PolicyViolation"  # type: ignore[union-attr]


class TestExecutionEnvelopeTimeout:
    def test_timeout_fires(self):
        reg = SkillRegistry()
        reg.register(_make_manifest(entrypoint="tests.skills.test_envelope:_slow_handler"))
        env = ExecutionEnvelope(reg)
        result = env.run("test.skill", {}, timeout_ms=100)
        assert result.status == "error"
        assert result.error.type == "TimeoutError"  # type: ignore[union-attr]
        assert result.error.retryable is True  # type: ignore[union-attr]


class TestExecutionEnvelopeRetries:
    def test_retry_on_retryable_error(self):
        call_count = []

        def flaky_handler(payload: dict) -> dict:
            call_count.append(1)
            if len(call_count) < 3:
                raise RuntimeError("flaky")
            return {"ok": True}

        reg = SkillRegistry()
        reg.register(_make_manifest(entrypoint="tests.skills.test_envelope:flaky_handler"))
        # Inject the handler via module-level trick — use sys.modules to avoid self-import
        mod = sys.modules[__name__]
        original = getattr(mod, "flaky_handler", None)
        mod.flaky_handler = flaky_handler  # type: ignore[attr-defined]
        try:
            env = ExecutionEnvelope(reg)
            result = env.run("test.skill", {}, max_retries=3)
            assert result.status == "ok"
            assert len(call_count) == 3
        finally:
            if original is None:
                delattr(mod, "flaky_handler")
            else:
                mod.flaky_handler = original  # type: ignore[attr-defined]


class TestTelemetryEmission:
    def test_telemetry_emit_jsonl_called(self, tmp_path):
        import os
        os.environ["CODEX_SKILL_TELEMETRY_PATH"] = str(tmp_path / "events.jsonl")
        try:
            reg = SkillRegistry()
            manifest = _make_manifest(
                telemetry=TelemetryConfig(emit_jsonl=True, emit_otel=False)
            )
            reg.register(manifest)
            env = ExecutionEnvelope(reg)
            env.run("test.skill", {})
            log_path = tmp_path / "events.jsonl"
            assert log_path.exists()
            content = log_path.read_text()
            assert "test.skill" in content
        finally:
            del os.environ["CODEX_SKILL_TELEMETRY_PATH"]
