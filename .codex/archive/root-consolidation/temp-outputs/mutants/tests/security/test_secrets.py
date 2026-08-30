"""Smoke tests for security secret helpers to ensure entropy checks stay stable."""

from __future__ import annotations

import pytest

from security import secrets as sec


def test_secret_entropy_thresholds():
    assert not sec.check_secret_entropy("short"), "Condition must be true"
    assert sec.check_secret_entropy("Aa1!sufficient-secret"), "Condition must be true"


def test_rotate_secret_with_custom_policy():
    state = sec.SecretRotationState("demo", last_rotated=0)
    policy = sec.SecretRotationPolicy(min_entropy_bits=1.0, max_age_seconds=0, history_size=2)

    class DeterministicRandom:
        def choice(self, alphabet: str) -> str:  # pragma: no cover - trivial
            return alphabet[0]

    rotated = sec.rotate_secret(state, policy=policy, generator=DeterministicRandom())
    assert rotated, "rotated is not valid"
    assert rotated in state.history, "Condition must be true"


def test_detect_secret_reuse():
    with pytest.raises(sec.SecurityError):
        sec.assert_secret_not_reused("abc", ["abc", "def"])
