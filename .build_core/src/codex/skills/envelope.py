"""Execution Envelope for Cognitive Brain Skills.

Wraps skill invocations with:
- Input validation (basic type/schema check)
- Policy gate (allowlist, risk tier, budget headroom)
- Timeout enforcement (per manifest wallclock_ms)
- Retry logic (configurable max_retries)
- Telemetry emission (JSONL and/or OTel)
- Structured ExecutionResult return

Usage::

    from codex.skills.envelope import ExecutionEnvelope
    from codex.skills.registry import get_registry

    registry = get_registry()
    registry.discover()

    env = ExecutionEnvelope(registry)
    result = env.run(
        skill_id="doc.retriever.core",
        payload={"query": "cognitive brain"},
        caller_id="copilot-agent",
    )
    logger.info(result.status, result.data)
"""

from __future__ import annotations

import importlib
import threading
import time
import traceback
import uuid
from typing import Any

from codex.logging.structured_logger import logger

from .models import (
    BudgetUsed,
    ExecutionError,
    ExecutionResult,
)
from .registry import SkillRegistry
from .telemetry import emit_event


class PolicyViolation(Exception):
    """Raised when a policy gate rejects an invocation."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class ExecutionEnvelope:
    """Wraps skill handler calls with policy, timeout, retries, and telemetry.

    Parameters
    ----------
    registry:
        The :class:`~codex.skills.registry.SkillRegistry` to resolve skills from.
    default_timeout_ms:
        Fallback timeout in ms when manifest does not specify one.
    default_max_retries:
        Fallback retry count.
    """

    def __init__(
        self,
        registry: SkillRegistry,
        *,
        default_timeout_ms: int = 30_000,
        default_max_retries: int = 0,
    ) -> None:
        self._registry = registry
        self._default_timeout_ms = default_timeout_ms
        self._default_max_retries = default_max_retries

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        skill_id: str,
        payload: dict[str, Any] | None = None,
        *,
        caller_id: str = "*",
        version: str | None = None,
        timeout_ms: int | None = None,
        max_retries: int | None = None,
    ) -> ExecutionResult:
        """Invoke a skill by id with full policy/envelope protection.

        Parameters
        ----------
        skill_id:
            Dotted skill identifier.
        payload:
            Input dictionary passed to the skill handler.
        caller_id:
            Identity of the calling agent for allowlist checks.
        version:
            Specific skill version; defaults to latest.
        timeout_ms:
            Override the manifest wallclock limit.
        max_retries:
            Override the default retry count.

        Returns
        -------
        ExecutionResult
        """
        trace_id = str(uuid.uuid4())
        payload = payload or {}

        skill = self._registry.resolve(skill_id, version)
        if skill is None:
            return self._error_result(
                trace_id,
                "SkillNotFound",
                f"Skill '{skill_id}' not registered",
                retryable=False,
            )

        manifest = skill.manifest
        effective_timeout_ms = (
            timeout_ms or manifest.policy.budgets.wallclock_ms or self._default_timeout_ms
        )
        effective_max_retries = (
            max_retries if max_retries is not None else self._default_max_retries
        )

        # Policy gate
        try:
            self._policy_gate(skill, caller_id, payload)
        except PolicyViolation as exc:
            return self._error_result(
                trace_id,
                "PolicyViolation",
                str(exc),
                retryable=exc.retryable,
            )

        # Load handler
        handler = self._load_handler(manifest.entrypoint)
        if handler is None:
            return self._error_result(
                trace_id,
                "HandlerLoadError",
                f"Cannot load entrypoint '{manifest.entrypoint}'",
                retryable=False,
            )

        # Execute with retries
        attempt = 0
        last_result: ExecutionResult | None = None
        while attempt <= effective_max_retries:
            attempt += 1
            start_wall = time.monotonic()
            result = self._execute_with_timeout(
                handler, payload, timeout_ms=effective_timeout_ms, trace_id=trace_id
            )
            elapsed_ms = int((time.monotonic() - start_wall) * 1000)
            result.metrics.latency_ms = elapsed_ms
            result.metrics.budget_used = BudgetUsed(
                calls=1,
                tokens=payload.get("_token_estimate", 0),
                wallclock_ms=elapsed_ms,
            )

            last_result = result
            if result.status == "ok":
                break
            if result.error and not result.error.retryable:
                break
            if attempt <= effective_max_retries:
                logger.info(
                    "Envelope: retrying skill '%s' (attempt %d/%d)",
                    skill_id,
                    attempt,
                    effective_max_retries + 1,
                )

        if (
            last_result is None
        ):  # defensive: should always be set in loop unless retry range is empty
            raise RuntimeError(
                "No result produced after retry loop (unexpected empty range)"
            )  # pragma: no cover
        result = last_result

        # Update registry budget
        self._registry.consume_budget(
            skill_id,
            version=manifest.version,
            calls=result.metrics.budget_used.calls,
            tokens=result.metrics.budget_used.tokens,
            wallclock_ms=result.metrics.budget_used.wallclock_ms,
        )

        # Emit telemetry
        if manifest.telemetry.emit_jsonl or manifest.telemetry.emit_otel:
            emit_event(
                skill_id=skill_id,
                version=manifest.version,
                status=result.status,
                metrics=result.metrics,
                trace_id=result.trace_id,
                emit_jsonl=manifest.telemetry.emit_jsonl,
                emit_otel=manifest.telemetry.emit_otel,
            )

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _policy_gate(self, skill: Any, caller_id: str, payload: dict[str, Any]) -> None:
        """Raise PolicyViolation if any policy check fails."""
        manifest = skill.manifest

        # Allowlist check
        if not skill.caller_allowed(caller_id):
            raise PolicyViolation(
                f"Caller '{caller_id}' not in allowlist for skill '{manifest.id}'"
            )

        # Budget headroom
        if not skill.has_budget_headroom(calls=1):
            raise PolicyViolation(
                f"Skill '{manifest.id}' has exhausted its call budget "
                f"({skill.budget_used['calls']}/{manifest.policy.budgets.calls})",
                retryable=False,
            )

    def _load_handler(self, entrypoint: str) -> Any | None:
        """Import and return the handler callable from 'module:function' entrypoint."""
        if ":" not in entrypoint:
            logger.error(
                "Envelope: invalid entrypoint format '%s' (expected 'module:fn')", entrypoint
            )
            return None
        module_path, fn_name = entrypoint.rsplit(":", 1)
        try:
            module = importlib.import_module(module_path)
            return getattr(module, fn_name)
        except (ImportError, AttributeError) as exc:
            logger.error("Envelope: cannot load entrypoint '%s': %s", entrypoint, exc)
            return None

    def _execute_with_timeout(
        self,
        handler: Any,
        payload: dict[str, Any],
        *,
        timeout_ms: int,
        trace_id: str,
    ) -> ExecutionResult:
        """Execute handler in a thread with a soft timeout gate.

        ``thread.join(timeout)`` does **not** forcibly terminate the underlying
        thread — Python threads cannot be killed from outside.  A timed-out
        handler continues executing in the background as a daemon thread until
        the process exits.  This is a known limitation of the thread-based
        approach; handlers MUST be designed to be side-effect-safe (idempotent,
        no critical resource holds) so background execution does no harm.

        For hard isolation (true termination on timeout) wrap the handler in a
        ``multiprocessing.Process`` instead.  That upgrade path is tracked in
        the skills roadmap.

        The handler must return a :class:`ExecutionResult` or a plain ``dict``
        (which is wrapped into ``ExecutionResult.data``).
        """
        result_holder: list[ExecutionResult | None] = [None]
        exc_holder: list[Exception | None] = [None]
        timeout_sec = timeout_ms / 1000.0

        def _target() -> None:
            try:
                raw = handler(payload)
                if isinstance(raw, ExecutionResult):
                    result_holder[0] = raw
                elif isinstance(raw, dict):
                    result_holder[0] = ExecutionResult(status="ok", data=raw, trace_id=trace_id)
                else:
                    result_holder[0] = ExecutionResult(
                        status="ok",
                        data={"result": raw},
                        trace_id=trace_id,
                    )
            except (IOError, OSError) as exc:
                exc_holder[0] = exc

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout=timeout_sec)

        if thread.is_alive():
            return self._error_result(
                trace_id,
                "TimeoutError",
                f"Skill execution exceeded {timeout_ms}ms timeout",
                retryable=True,
            )

        if exc_holder[0] is not None:
            exc = exc_holder[0]
            logger.debug("Skill execution raised exception: %s", traceback.format_exc())
            return self._error_result(
                trace_id,
                type(exc).__name__,
                str(exc),
                retryable=True,
            )

        if result_holder[0] is None:
            return self._error_result(
                trace_id,
                "ExecutionError",
                "Handler returned no result",
                retryable=False,
            )

        result = result_holder[0]
        result.trace_id = trace_id
        return result

    @staticmethod
    def _error_result(
        trace_id: str,
        error_type: str,
        message: str,
        *,
        retryable: bool = False,
    ) -> ExecutionResult:
        return ExecutionResult(
            status="error",
            error=ExecutionError(type=error_type, message=message, retryable=retryable),
            trace_id=trace_id,
        )


__all__ = ["ExecutionEnvelope", "PolicyViolation"]
