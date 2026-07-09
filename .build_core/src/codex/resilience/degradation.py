"""Graceful degradation utilities.

Provides :class:`GracefulDegradation`, which can be used both as a *decorator*
and as a *context manager* to wrap any code that may fail and substitute a
safe fallback value instead of propagating the exception.

Usage as a decorator::

    from codex.resilience import GracefulDegradation

    @GracefulDegradation(fallback=0)
    def risky_metric() -> int:
        return fetch_from_remote()

Usage as a context manager::

    from codex.resilience import GracefulDegradation, DegradationError

    with GracefulDegradation(fallback="default") as dg:
        dg.result = compute_value()

    logger.info(dg.result)

Usage without a fallback (re-raises as DegradationError)::

    with GracefulDegradation() as dg:
        dg.result = dangerous_call()   # DegradationError raised on failure
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from codex.logging.structured_logger import logger

_SENTINEL = object()  # marks "no fallback provided"


class DegradationError(Exception):
    """Raised when a :class:`GracefulDegradation` block fails and no fallback is set.

    Args:
        message: Human-readable description.
        original: The original exception that caused the degradation.
    """

    def __init__(
        self,
        message: str = "Unrecoverable failure — no fallback provided",
        original: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.original = original


class GracefulDegradation:
    """Wrap a callable or a ``with`` block so that failures return a fallback value.

    When used as a **decorator**:
        The wrapped function is called; if it raises any :class:`Exception`,
        *fallback* is returned instead (or :exc:`DegradationError` if no
        fallback was given).

    When used as a **context manager**:
        Assign the value you want to capture to ``<ctx>.result`` inside the
        ``with`` block.  On success, ``<ctx>.result`` holds that value.  On
        failure, ``<ctx>.result`` is set to *fallback* (or
        :exc:`DegradationError` is raised if no fallback was given).

    Args:
        fallback: Value to return / set on failure.  May be a plain value or a
            zero-argument callable whose return value is used.  If omitted,
            failures raise :exc:`DegradationError`.
        exceptions: Tuple of exception types to catch.  Defaults to
            ``(Exception,)`` — catches all non-system-exit exceptions.
        logger_name: Name used when emitting degradation log messages.
            Defaults to the module logger.

    Thread safety:
        Each :class:`GracefulDegradation` instance is **not** thread-safe when
        used as a context manager (``result`` is stored on the instance).  Use
        separate instances per thread/coroutine.
    """

    def __init__(
        self,
        fallback: Any = _SENTINEL,
        *,
        exceptions: tuple[type[BaseException], ...] = (Exception,),
        logger_name: str | None = None,
    ) -> None:
        self._fallback = fallback
        self._exceptions = exceptions
        self._log = logging.getLogger(logger_name) if logger_name else logger
        self.result: Any = None  # populated by context-manager usage

    # ------------------------------------------------------------------
    # Decorator interface
    # ------------------------------------------------------------------

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Return a wrapper that applies graceful degradation to *fn*."""

        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except self._exceptions as exc:
                return self._handle_failure(exc, context=fn.__qualname__)  # type: ignore[arg-type]

        _wrapper.__name__ = getattr(fn, "__name__", "_wrapper")
        _wrapper.__qualname__ = getattr(fn, "__qualname__", "_wrapper")
        _wrapper.__doc__ = fn.__doc__
        return _wrapper

    # ------------------------------------------------------------------
    # Context manager interface
    # ------------------------------------------------------------------

    def __enter__(self) -> "GracefulDegradation":
        self.result = None
        return self

    def __exit__(
        self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object
    ) -> bool:
        if exc_type is None:
            return False  # no exception — nothing to do
        if not issubclass(exc_type, self._exceptions):
            return False  # not one we handle — propagate
        self.result = self._handle_failure(exc_val, context="context_manager")  # type: ignore[arg-type]
        return True  # suppress the exception

    # ------------------------------------------------------------------
    # Shared failure handling
    # ------------------------------------------------------------------

    def _handle_failure(self, exc: Exception, *, context: str = "") -> Any:
        """Log the failure and return the fallback (or raise DegradationError)."""
        ctx_label = f" [{context}]" if context else ""
        self._log.warning(
            "GracefulDegradation%s: caught %s(%s) — %s",
            ctx_label,
            type(exc).__name__,
            exc,
            (
                "using fallback"
                if self._fallback is not _SENTINEL
                else "no fallback, raising DegradationError"
            ),
        )
        if self._fallback is _SENTINEL:
            raise DegradationError(
                f"Unrecoverable failure in{ctx_label}: {exc!r}",
                original=exc,
            ) from exc
        if callable(self._fallback):
            return self._fallback()
        return self._fallback

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        fb = "<no fallback>" if self._fallback is _SENTINEL else repr(self._fallback)
        return f"GracefulDegradation(fallback={fb})"
