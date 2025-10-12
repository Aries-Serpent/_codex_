"""
Metrics collection for Zendesk integrations.

Defines counters, histograms, and gauges for tracking API usage, rate limits,
diff sizes, and apply outcomes.  Uses a generic monitoring interface provided
by `_codex_` core.
"""

from codex.monitoring import metrics

api_calls = metrics.Counter(
    name="zendesk_api_calls_total",
    description="Total number of Zendesk API calls made",
    unit="calls",
)
rate_limit_retries = metrics.Counter(
    name="zendesk_rate_limit_retries_total",
    description="Number of times a rate-limit retry was executed",
)
diff_size = metrics.Histogram(
    name="zendesk_diff_size",
    description="Number of patch operations generated per diff",
    unit="operations",
)
apply_success = metrics.Counter(
    name="zendesk_apply_success_total",
    description="Number of successful apply operations",
)
apply_failure = metrics.Counter(
    name="zendesk_apply_failure_total",
    description="Number of failed apply operations",
)


def register_zendesk_metrics() -> None:
    """Register all Zendesk metrics with the global metrics registry."""

    metrics.register(api_calls)
    metrics.register(rate_limit_retries)
    metrics.register(diff_size)
    metrics.register(apply_success)
    metrics.register(apply_failure)
