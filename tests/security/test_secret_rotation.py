import pytest

from src.security import SecretRotationPolicy, SecretRotationState, SecurityError, rotate_secret


def test_secret_rotation_policy_enforced() -> None:
    policy = SecretRotationPolicy(min_entropy_bits=32.0, max_age_seconds=10)
    state = SecretRotationState(identifier="service", last_rotated=0)
    secret = rotate_secret(state, policy=policy)
    assert len(secret) == 32
    with pytest.raises(SecurityError):
        rotate_secret(state, policy=policy)
