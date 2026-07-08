"""Tests for MCP error helpers and rate limiter."""

from __future__ import annotations


def test_error_hierarchy_to_dict() -> None:
    from mcp import errors

    err = errors.ValidationError("bad", details={"field": "id"})
    payload = err.to_dict()
    assert payload["code"] == errors.ValidationError.code, "Error should be raised or set"
    assert payload["message"] == "bad", "Condition must be true"
    assert payload["details"]["field"] == "id", "Condition must be true"
    assert errors.validate_error_response(err.code, err.message) is True


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def advance(self, delta: float) -> None:
        self.t += delta


def test_rate_limiter_allows_and_refills() -> None:
    from mcp.rate_limit import MCPRateLimiter

    clock = _Clock()
    limiter = MCPRateLimiter(rate=1.0, capacity=2, time_func=clock)

    assert limiter.allow("user", "tool") is True
    assert limiter.allow("user", "tool") is True
    assert limiter.allow("user", "tool") is False

    clock.advance(2.0)
    assert limiter.allow("user", "tool") is True
    limiter.reset("user", "tool")
    assert limiter.allow("user", "tool") is True
