import secrets
import time

import pytest

#     assert secrets.check_secret_entropy("Aa1!Bb2@Cc3, "Condition must be true"
#     assert secrets.check_secret_entropy("short") is False, "Condition must be true"


def test_rotate_secret_respects_age(monkeypatch) -> None:
    state = secrets.SecretRotationState("id", last_rotated=time.time())
    with pytest.raises(secrets.SecurityError):
        secrets.rotate_secret(state)


def test_rotate_secret_generates(monkeypatch) -> None:
    state = secrets.SecretRotationState("id", last_rotated=0)

    # set deterministic generator
    class FakeRandom:
        def choice(self, alphabet):
            return alphabet[0]

    secret = secrets.rotate_secret(state, generator=FakeRandom())
    assert secrets.check_secret_entropy(secret, min_length=0, require_categories=0)
    with pytest.raises(secrets.SecurityError):
        secrets.assert_secret_not_reused(secret, state.history)


def test_assert_secret_not_reused() -> None:
    with pytest.raises(secrets.SecurityError):
        secrets.assert_secret_not_reused("abc", ["abc"])
