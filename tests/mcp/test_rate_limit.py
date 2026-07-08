"""Dedicated tests for :mod:`mcp.rate_limit`."""

from __future__ import annotations

from mcp.rate_limit import MCPRateLimiter


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def advance(self, delta: float) -> None:
        self.t += delta


def test_rate_limiter_tracks_tokens() -> None:
    clock = _Clock()
    limiter = MCPRateLimiter(rate=0.5, capacity=1, time_func=clock)

    assert limiter.allow("p", "tool") is True
    assert limiter.allow("p", "tool") is False
    clock.advance(3.0)
    assert limiter.allow("p", "tool") is True
