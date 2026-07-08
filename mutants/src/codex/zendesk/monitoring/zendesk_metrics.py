"""Metric definitions for Zendesk adapters."""

from __future__ import annotations

from collections.abc import Iterable

from codex.monitoring import Counter, Histogram, metrics

_api_calls = Counter(
    name="zendesk_api_calls_total",
    description="Total number of Zendesk API calls made by Codex.",
    unit="calls",
)
_rate_limit_retries = Counter(
    name="zendesk_rate_limit_retries_total",
    description="Number of rate limited Zendesk requests that were retried.",
)
_diff_size = Histogram(
    name="zendesk_diff_operations",
    description="Histogram of patch operations generated per diff run.",
    unit="operations",
)
_apply_success = Counter(
    name="zendesk_apply_success_total",
    description="Successful Zendesk apply operations.",
)
_apply_failure = Counter(
    name="zendesk_apply_failure_total",
    description="Failed Zendesk apply operations.",
)


def register_zendesk_metrics() -> Iterable[str]:
    """Register Zendesk metrics with the shared registry.

    Returns
    -------
    Iterable[str]
        Names of the metrics that were registered.  The function is idempotent
        because the underlying registry simply replaces existing entries.
    """

    registered = []
    for instrument in (
        _api_calls,
        _rate_limit_retries,
        _diff_size,
        _apply_success,
        _apply_failure,
    ):
        metrics.register(instrument)
        registered.append(instrument.name)
    return registered


__all__ = ["register_zendesk_metrics"]
