"""Fallback chains and auto-recovery for the Cognitive Brain runtime.

Provides composable fallback decorators and an explicit :class:`FallbackChain`
that tries successive strategies until one succeeds.  Integrates with the
:class:`~model_negotiator.ModelNegotiator` for model-level recovery and with
:class:`~telemetry.CognitiveTelemetry` for structured failure logging.

Usage::

    chain = FallbackChain(
        strategies=[primary_fn, secondary_fn, safe_default_fn],
        label="session_create",
    )
    result = chain.run(payload)
"""

from __future__ import annotations

import functools
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class FallbackAttempt:
    """Record of a single strategy attempt within a :class:`FallbackChain` run."""

    strategy_index: int
    strategy_name: str
    success: bool
    duration_ms: float
    error: Optional[str] = None
    result_summary: Optional[str] = None


@dataclass
class FallbackResult(Generic[T]):
    """Aggregate result of a :class:`FallbackChain` run."""

    value: Optional[T]
    succeeded: bool
    attempts: List[FallbackAttempt] = field(default_factory=list)
    final_strategy: Optional[str] = None
    total_duration_ms: float = 0.0

    @property
    def attempt_count(self) -> int:
        return len(self.attempts)

    @property
    def failed_attempts(self) -> int:
        return sum(1 for a in self.attempts if not a.success)


# ---------------------------------------------------------------------------
# FallbackChain
# ---------------------------------------------------------------------------


class FallbackChain(Generic[T]):
    """Try a sequence of strategies in order, returning the first success.

    Parameters
    ----------
    strategies:
        Ordered list of callables.  Each receives the same ``*args`` and
        ``**kwargs`` as :meth:`run`.
    label:
        Human-readable name used in log messages.
    max_attempts:
        Stop after this many strategies regardless of outcome.
    reraise_on_exhaustion:
        If True and all strategies fail, re-raise the last exception.
        If False, return a :class:`FallbackResult` with ``succeeded=False``.
    """

    def __init__(
        self,
        strategies: List[Callable[..., T]],
        label: str = "fallback_chain",
        max_attempts: Optional[int] = None,
        reraise_on_exhaustion: bool = False,
    ) -> None:
        if not strategies:
            raise ValueError("FallbackChain requires at least one strategy")
        self._strategies = strategies
        self._label = label
        self._max = max_attempts or len(strategies)
        self._reraise = reraise_on_exhaustion

    def run(self, *args: Any, **kwargs: Any) -> FallbackResult[T]:
        """Execute strategies in order until one succeeds."""
        chain_start = time.monotonic()
        attempts: List[FallbackAttempt] = []
        last_exc: Optional[Exception] = None

        for idx, strategy in enumerate(self._strategies[: self._max]):
            name = getattr(strategy, "__name__", f"strategy_{idx}")
            t0 = time.monotonic()
            try:
                result = strategy(*args, **kwargs)
                duration_ms = (time.monotonic() - t0) * 1000
                attempt = FallbackAttempt(
                    strategy_index=idx,
                    strategy_name=name,
                    success=True,
                    duration_ms=duration_ms,
                    result_summary=str(result)[:120],
                )
                attempts.append(attempt)
                total_ms = (time.monotonic() - chain_start) * 1000
                logger.info(
                    "FallbackChain[%s] succeeded on strategy %d/%d (%s) in %.1fms",
                    self._label,
                    idx + 1,
                    len(self._strategies),
                    name,
                    duration_ms,
                )
                return FallbackResult(
                    value=result,
                    succeeded=True,
                    attempts=attempts,
                    final_strategy=name,
                    total_duration_ms=total_ms,
                )
            except Exception as exc:  # noqa: BLE001
                duration_ms = (time.monotonic() - t0) * 1000
                last_exc = exc
                attempt = FallbackAttempt(
                    strategy_index=idx,
                    strategy_name=name,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(exc)[:200],
                )
                attempts.append(attempt)
                logger.warning(
                    "FallbackChain[%s] strategy %d/%d (%s) failed: %s",
                    self._label,
                    idx + 1,
                    len(self._strategies),
                    name,
                    exc,
                )

        total_ms = (time.monotonic() - chain_start) * 1000
        logger.error(
            "FallbackChain[%s] exhausted all %d strategies in %.1fms",
            self._label,
            len(self._strategies),
            total_ms,
        )
        if self._reraise and last_exc is not None:
            raise last_exc
        return FallbackResult(
            value=None,
            succeeded=False,
            attempts=attempts,
            final_strategy=None,
            total_duration_ms=total_ms,
        )


# ---------------------------------------------------------------------------
# Decorator API
# ---------------------------------------------------------------------------


def with_fallback(
    fallback_fn: Callable[..., T],
    *,
    label: str = "with_fallback",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that calls *fallback_fn* when the decorated function raises.

    Example::

        @with_fallback(safe_default)
        def primary_operation(...):
            ...
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "%s: primary '%s' failed (%s); invoking fallback '%s'",
                    label,
                    fn.__name__,
                    exc,
                    fallback_fn.__name__,
                )
                return fallback_fn(*args, **kwargs)

        return wrapper

    return decorator


def rate_limited_call(
    fn: Callable[..., T],
    *args: Any,
    retries: int = 3,
    base_delay_s: float = 1.0,
    label: str = "rate_limited_call",
    **kwargs: Any,
) -> T:
    """Retry *fn* up to *retries* times with exponential back-off.

    Intended for API calls that may transiently rate-limit or time out.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            delay = base_delay_s * (2**attempt)
            logger.warning(
                "%s: attempt %d/%d failed (%s); retrying in %.1fs",
                label,
                attempt + 1,
                retries,
                exc,
                delay,
            )
            time.sleep(delay)
    raise RuntimeError(f"{label}: all {retries} attempts failed") from last_exc


def import_optional(module_name: str, attr: Optional[str] = None) -> Any:
    """Import *module_name* (optionally fetch *attr*), returning None on failure.

    Allows optional dependencies to be skipped gracefully::

        mlflow = import_optional("mlflow")
        if mlflow is not None:
            mlflow.log_metric("loss", 0.5)
    """
    try:
        import importlib

        mod = importlib.import_module(module_name)
        if attr is not None:
            return getattr(mod, attr, None)
        return mod
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# Safe-default helpers
# ---------------------------------------------------------------------------


def safe_default_config(
    model_id: str = "claude-sonnet-5",
    *,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    """Return a conservative session configuration that avoids unsupported params.

    Used as the last-resort fallback when capability negotiation cannot resolve
    a working model + config pair.
    """
    return {
        "model": model_id,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
