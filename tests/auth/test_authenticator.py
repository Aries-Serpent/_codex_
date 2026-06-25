"""
Tests for the high-level Authenticator service.
"""

import pytest

from codex.auth.authenticator import Authenticator, LoginResult
from codex.auth.exceptions import (
    InvalidCredentialsError,
    MFARequiredError,
    MFAVerificationError,
)
from codex.auth.mfa_provider import MFAProvider
from codex.auth.token_manager import TokenManager, TokenType
from codex.auth.user_store import UserStore

# ---------------------------------------------------------------------------
# Helpers # pragma: allowlist secret
# ---------------------------------------------------------------------------


def _make_auth(with_mfa: bool = False) -> Authenticator:
    store = UserStore()
    tokens = TokenManager(secret_key="test-secret-key-for-authenticator")
    mfa = MFAProvider() if with_mfa else None
    return Authenticator(user_store=store, token_manager=tokens, mfa_provider=mfa)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestRegister:

    def test_register_returns_user(self):
        auth = _make_auth()
        user = auth.register("alice", "alice@example.com", "Str0ngPass!")
        assert user.username == "alice"
        assert user.email == "alice@example.com"

    def test_register_custom_roles(self):
        auth = _make_auth()
        user = auth.register("bob", "bob@example.com", "Str0ngPass!", roles=["admin"])
        assert "admin" in user.roles

    def test_register_duplicate_username_raises(self):
        auth = _make_auth()
        auth.register("carol", "carol@example.com", "Str0ngPass!")
        with pytest.raises(ValueError, match="already taken"):
            auth.register("carol", "carol2@example.com", "Str0ngPass!")

    def test_register_weak_password_raises(self):
        auth = _make_auth()
        with pytest.raises(ValueError):
            auth.register("dave", "dave@example.com", "short")


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestTokenManager:

    def test_zero_timeout_override_is_preserved(self):
        manager = TokenManager(
            secret_key="test-secret-key",
            access_token_timeout=0,
            refresh_token_timeout=0,
            session_token_timeout=0,
        )
        assert manager._access_token_expiry == 0
        assert manager._refresh_token_expiry == 0
        assert manager._session_token_expiry == 0


class TestLogin:

    def test_login_returns_login_result(self):
        auth = _make_auth()
        auth.register("eve", "eve@example.com", "Str0ngPass!")
        result = auth.login("eve", "Str0ngPass!")
        assert isinstance(result, LoginResult)
        assert result.username == "eve"
        assert result.access_token
        assert result.refresh_token
        assert result.session_token
        assert result.session_id

    def test_login_by_email(self):
        auth = _make_auth()
        auth.register("frank", "frank@example.com", "Str0ngPass!")
        result = auth.login("frank@example.com", "Str0ngPass!")
        assert result.username == "frank"

    def test_login_wrong_password_raises(self):
        auth = _make_auth()
        auth.register("grace", "grace@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            auth.login("grace", "WrongPass!!")

    def test_login_unknown_user_raises(self):
        auth = _make_auth()
        with pytest.raises(InvalidCredentialsError):
            auth.login("nobody", "Str0ngPass!")

    def test_login_result_contains_roles(self):
        auth = _make_auth()
        auth.register("hank", "hank@example.com", "Str0ngPass!", roles=["admin", "user"])
        result = auth.login("hank", "Str0ngPass!")
        assert "admin" in result.roles

    def test_login_tokens_are_valid(self):
        auth = _make_auth()
        tokens = auth._tokens
        auth.register("iris", "iris@example.com", "Str0ngPass!")
        result = auth.login("iris", "Str0ngPass!")
        # Access token
        claims = tokens.validate_token(result.access_token, TokenType.ACCESS)
        assert claims.sub == result.user_id
        # Session token
        claims_s = tokens.validate_token(result.session_token, TokenType.SESSION)
        assert claims_s.sub == result.user_id

    def test_login_records_ip_and_user_agent(self):
        auth = _make_auth()
        tokens = auth._tokens
        auth.register("jan", "jan@example.com", "Str0ngPass!")
        result = auth.login("jan", "Str0ngPass!", ip_address="10.0.0.1", user_agent="TestUA/1.0")
        session = tokens.get_session(result.session_id)
        assert session.ip_address == "10.0.0.1"
        assert session.user_agent == "TestUA/1.0"


# ---------------------------------------------------------------------------
# MFA-enabled login
# ---------------------------------------------------------------------------


class TestLoginWithMFA:

    def test_mfa_required_raises_when_no_code(self):
        auth = _make_auth(with_mfa=True)
        auth.register("ken", "ken@example.com", "Str0ngPass!")
        user = auth._store.find_by_username("ken")
        auth._mfa.generate_totp_secret(user.user_id)

        with pytest.raises(MFARequiredError):
            auth.login("ken", "Str0ngPass!")

    def test_mfa_wrong_code_raises(self):
        auth = _make_auth(with_mfa=True)
        auth.register("leo", "leo@example.com", "Str0ngPass!")
        user = auth._store.find_by_username("leo")
        auth._mfa.generate_totp_secret(user.user_id)

        with pytest.raises(MFAVerificationError):
            auth.login("leo", "Str0ngPass!", totp_code="000000")

    def test_mfa_not_enrolled_skipped(self):
        auth = _make_auth(with_mfa=True)
        auth.register("mia", "mia@example.com", "Str0ngPass!")
        # MFA provider present but user not enrolled → no MFA prompt
        result = auth.login("mia", "Str0ngPass!")
        assert result.mfa_verified is False


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


class TestLogout:

    def test_logout_revokes_session(self):
        auth = _make_auth()
        auth.register("nat", "nat@example.com", "Str0ngPass!")
        result = auth.login("nat", "Str0ngPass!")
        assert auth.logout(result.session_token) is True
        assert auth._tokens.get_session(result.session_id) is None

    def test_logout_invalid_token_returns_false(self):
        auth = _make_auth()
        assert auth.logout("not-a-valid-token") is False

    def test_logout_all_revokes_all_sessions(self):
        auth = _make_auth()
        auth.register("oliver", "oliver@example.com", "Str0ngPass!")
        r1 = auth.login("oliver", "Str0ngPass!", ip_address="1.1.1.1")
        r2 = auth.login("oliver", "Str0ngPass!", ip_address="2.2.2.2")
        count = auth.logout_all(r1.user_id)
        assert count == 2
        assert auth._tokens.get_session(r1.session_id) is None
        assert auth._tokens.get_session(r2.session_id) is None


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------


class TestRefresh:

    def test_refresh_returns_new_access_token(self):
        auth = _make_auth()
        auth.register("pat", "pat@example.com", "Str0ngPass!")
        result = auth.login("pat", "Str0ngPass!")
        new_token = auth.refresh(result.refresh_token)
        assert new_token
        assert new_token != result.access_token

    def test_refresh_invalid_token_raises(self):
        auth = _make_auth()
        with pytest.raises(ValueError):
            auth.refresh("invalid-refresh-token")


# ---------------------------------------------------------------------------
# Password management
# ---------------------------------------------------------------------------


class TestPasswordManagement:

    def test_change_password_works(self):
        auth = _make_auth()
        user = auth.register("quinn", "quinn@example.com", "OldPass123!")
        auth.change_password(user.user_id, "OldPass123!", "NewPass456!")
        result = auth.login("quinn", "NewPass456!")
        assert result.username == "quinn"

    def test_change_password_wrong_current_raises(self):
        auth = _make_auth()
        user = auth.register("rex", "rex@example.com", "OldPass123!")
        with pytest.raises(InvalidCredentialsError):
            auth.change_password(user.user_id, "WrongOld!!", "NewPass456!")

    def test_change_password_revokes_sessions_by_default(self):
        auth = _make_auth()
        user = auth.register("sam", "sam@example.com", "OldPass123!")
        result = auth.login("sam", "OldPass123!")
        auth.change_password(user.user_id, "OldPass123!", "NewPass456!")
        assert auth._tokens.get_session(result.session_id) is None

    def test_change_password_keep_sessions(self):
        auth = _make_auth()
        user = auth.register("tina", "tina@example.com", "OldPass123!")
        result = auth.login("tina", "OldPass123!")
        auth.change_password(user.user_id, "OldPass123!", "NewPass456!", revoke_sessions=False)
        assert auth._tokens.get_session(result.session_id) is not None

    def test_admin_reset_password(self):
        auth = _make_auth()
        user = auth.register("uma", "uma@example.com", "OldPass123!")
        auth.admin_reset_password(user.user_id, "AdminNew456!")
        result = auth.login("uma", "AdminNew456!")
        assert result.username == "uma"

    def test_admin_reset_unknown_user_raises(self):
        auth = _make_auth()
        with pytest.raises(KeyError):
            auth.admin_reset_password("ghost-id", "SomePass123!")
