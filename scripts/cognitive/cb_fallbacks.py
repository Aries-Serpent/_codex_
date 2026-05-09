"""
Cognitive Brain — Shared Fallback Helpers
==========================================
Cross-cutting utility belt used by all CB components (PerceptionLayer,
DecisionEngine, ActionExecutor, AfterMathEvaluator) to:

  1. Gracefully degrade when optional dependencies (torch, psutil, mlflow …)
     are unavailable in stripped-down environments.
  2. Wrap GitHub API calls with the rate-limit guard from
     ``scripts/ci/github_api_trickle.py`` so no CB orchestration step
     exhausts the REST quota unexpectedly.

Usage
-----
>>> from scripts.cognitive.cb_fallbacks import import_optional, with_fallback, rate_limited_call

>>> torch = import_optional("torch")           # None if torch is absent
>>> val = with_fallback(lambda: expensive(), default=0.0)
>>> data = rate_limited_call(fetch_pr_data, pr_number=42)
"""

from __future__ import annotations

import importlib
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Optional-import helper
# ---------------------------------------------------------------------------

def import_optional(module_name: str, attr: str | None = None) -> Any:
    """Import *module_name* and return it (or *attr* from it).

    Returns ``None`` without raising if the module is absent.  This is the
    canonical way for CB components to declare soft dependencies.

    Args:
        module_name: Fully-qualified module name, e.g. ``"torch"`` or ``"mlflow"``.
        attr: Optional attribute to return from the module, e.g. ``"no_grad"``.

    Returns:
        The module (or attribute) if available, otherwise ``None``.
    """
    try:
        mod = importlib.import_module(module_name)
        if attr is not None:
            return getattr(mod, attr, None)
        return mod
    except ImportError:
        logger.debug("Optional dependency %r unavailable — using fallback.", module_name)
        return None


# ---------------------------------------------------------------------------
# Exception-swallowing fallback wrapper
# ---------------------------------------------------------------------------

def with_fallback(
    func: Callable[[], T],
    default: T,
    exc_types: tuple[type[BaseException], ...] = (Exception,),
    *,
    log_level: int = logging.DEBUG,
) -> T:
    """Call *func* and return *default* if any *exc_types* are raised.

    This prevents a single optional-feature failure from crashing the entire
    PDA cycle.  Failures are logged at *log_level* (DEBUG by default) so the
    noise stays low in production logs.

    Args:
        func: Zero-argument callable to attempt.
        default: Value to return on failure.
        exc_types: Exception types to catch (default: all ``Exception``).
        log_level: Logging level for the caught exception message.

    Returns:
        Return value of *func* on success, *default* on failure.
    """
    try:
        return func()
    except exc_types as exc:  # noqa: BLE001 (broad except is intentional here)
        logger.log(log_level, "with_fallback: %s → using default %r", exc, default)
        return default


# ---------------------------------------------------------------------------
# Rate-limit-aware GitHub API wrapper
# ---------------------------------------------------------------------------

_MIN_REMAINING: int = 10       # mirror GH_TRICKLE_MIN_REMAINING default
_POLITE_SLEEP: float = 0.5    # mirror GH_TRICKLE_POLITE_SLEEP default
_MAX_RETRIES: int = 3
_RETRY_BACKOFF: float = 2.0   # exponential backoff multiplier


def _get_trickle_status() -> dict[str, Any]:
    """Return current rate-limit status from github_api_trickle, or an empty
    dict if the module is unavailable (e.g. no token in env)."""
    trickle = import_optional("scripts.ci.github_api_trickle")
    if trickle is None:
        return {}
    try:
        return trickle.status(write_state=False)  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001
        logger.debug("rate-limit status unavailable: %s", exc)
        return {}


def rate_limited_call(
    func: Callable[..., T],
    *args: Any,
    resource: str = "core",
    min_remaining: int = _MIN_REMAINING,
    max_retries: int = _MAX_RETRIES,
    **kwargs: Any,
) -> T:
    """Execute *func* with GitHub API rate-limit awareness.

    Before each attempt the function checks the current REST quota via
    ``github_api_trickle.status()``.  If ``remaining < min_remaining`` it
    waits until the reset window passes before retrying (up to *max_retries*
    times with exponential back-off).

    If ``github_api_trickle`` is unavailable (no token, offline environment)
    the call proceeds immediately — degrading gracefully to the caller's own
    error handling.

    Args:
        func: The GitHub-API-calling function to execute.
        *args: Positional arguments forwarded to *func*.
        resource: Rate-limit resource bucket (``"core"``, ``"search"``, …).
        min_remaining: Minimum remaining calls required before attempting.
        max_retries: Maximum number of quota-wait retries before giving up.
        **kwargs: Keyword arguments forwarded to *func*.

    Returns:
        The return value of *func*.

    Raises:
        RuntimeError: If the quota remains exhausted after *max_retries*.
        Any exception raised by *func* itself is propagated unchanged.
    """
    for attempt in range(max_retries + 1):
        status = _get_trickle_status()
        resources = status.get("resources", {})
        bucket = resources.get(resource, {})
        remaining = bucket.get("remaining", min_remaining)  # optimistic if unknown
        reset_at = bucket.get("reset", int(time.time()))

        if remaining < min_remaining:
            wait_secs = max(0, reset_at - int(time.time())) + 1
            if attempt >= max_retries:
                raise RuntimeError(
                    f"GitHub API rate limit exhausted (resource={resource!r}, "
                    f"remaining={remaining}, reset_at={reset_at}).  "
                    f"Giving up after {max_retries} retries."
                )
            logger.warning(
                "rate_limited_call: quota low (remaining=%d, resource=%r) — "
                "waiting %ds (attempt %d/%d).",
                remaining, resource, wait_secs, attempt + 1, max_retries,
            )
            time.sleep(min(wait_secs, 60))  # cap single sleep at 60 s
            continue

        # Polite inter-call sleep to avoid burst exhaustion
        if attempt > 0:
            time.sleep(_POLITE_SLEEP * (_RETRY_BACKOFF ** attempt))

        return func(*args, **kwargs)

    # Unreachable — loop always returns or raises — but satisfies type checkers
    raise RuntimeError("rate_limited_call: unexpected exit from retry loop")
