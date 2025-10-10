import pytest

from src.security import SecurityError, rate_limiter


def test_rate_limiter_enforcement() -> None:
    timeline = iter([0.0, 0.1, 0.2, 0.3])

    def fake_clock() -> float:
        return next(timeline)

    @rate_limiter(calls=3, period=1.0, clock=fake_clock)
    def guarded() -> None:
        return None

    guarded()
    guarded()
    guarded()
    with pytest.raises(SecurityError):
        guarded()
