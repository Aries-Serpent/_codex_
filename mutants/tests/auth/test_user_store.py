"""
Tests for UserStore and PasswordHasher.
"""

import pytest

from codex.auth.exceptions import InvalidCredentialsError
from codex.auth.user_store import PasswordHasher, User, UserStore


class TestPasswordHasher:
    """Tests for PasswordHasher."""

    def test_hash_returns_string(self):
        h = PasswordHasher()
        result = h.hash("MyP@ssword1")
        assert isinstance(result, str)
        assert ":" in result # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

    def test_verify_correct_password(self):
        h = PasswordHasher()
        stored = h.hash("correct-horse-battery")
        assert h.verify("correct-horse-battery", stored) is True

    def test_verify_wrong_password(self):
        h = PasswordHasher()
        stored = h.hash("correct-horse-battery")
        assert h.verify("wrong-password", stored) is False

    def test_unique_salts(self):
        h = PasswordHasher()
        h1 = h.hash("same-password")
        h2 = h.hash("same-password")
        assert h1 != h2, "h1 is not valid"

    def test_hash_empty_password_raises(self):
        h = PasswordHasher()
        with pytest.raises(ValueError, match="must not be empty"):
            h.hash("")

    def test_verify_malformed_hash(self):
        h = PasswordHasher()
        assert h.verify("anything", "not-a-valid-hash") is False

    def test_verify_empty_hash(self):
        h = PasswordHasher()
        assert h.verify("password", "") is False


class TestUser:
    """Tests for the User dataclass."""

    def test_has_role_true(self):
        user = User(
            user_id="u1",
            username="alice",
            email="alice@example.com",
            password_hash="x:y",
            roles=["user", "admin"],
        )
        assert user.has_role("admin") is True, "Condition must be true"

    def test_has_role_false(self):
        user = User(
            user_id="u1",
            username="alice",
            email="alice@example.com",
            password_hash="x:y",
        )
        assert user.has_role("admin") is False, "Condition must be true"

    def test_to_dict_omits_password_hash(self):
        user = User(
            user_id="u1",
            username="alice",
            email="alice@example.com",
            password_hash="secret-hash",
        )
        d = user.to_dict()
        assert "password_hash" not in d, "Condition must be true"
        assert d["username"] == "alice", "Condition must be true"
        assert d["email"] == "alice@example.com", "Condition must be true"

    def test_to_dict_contains_expected_keys(self):
        user = User(
            user_id="u1",
            username="alice",
            email="alice@example.com",
            password_hash="x:y",
        )
        d = user.to_dict()
        for key in (
            "user_id",
            "username",
            "email",
            "is_active",
            "roles",
            "created_at",
            "updated_at",
        ):
            assert key in d, "Condition must be true"

    def test_requires_identifier(self):
        with pytest.raises(ValueError, match="At least one identifier"):
            User(username="alice", email="alice@example.com", password_hash="x:y")

    def test_rejects_conflicting_identifiers(self):
        with pytest.raises(ValueError, match="must match"):
            User(
                user_id="u1",
                id="u2",
                username="alice",
                email="alice@example.com",
                password_hash="x:y",
            )


class TestUserStore:
    """Tests for UserStore CRUD and authentication."""

    # ------------------------------------------------------------------ #
    # create_user                                                          #
    # ------------------------------------------------------------------ #

    def test_create_user_success(self):
        store = UserStore()
        user = store.create_user("bob", "bob@example.com", "Str0ngPass!")
        assert user.username == "bob", "username is not valid"
        assert user.email == "bob@example.com", "email is not valid"
        assert user.is_active is True, "is_active is not valid"
        assert "user" in user.roles, "Condition must be true"

    def test_create_user_normalises_email(self):
        store = UserStore()
        user = store.create_user("carol", "Carol@Example.COM", "Str0ngPass!")
        assert user.email == "carol@example.com", "email is not valid"

    def test_create_user_custom_roles(self):
        store = UserStore()
        user = store.create_user("dave", "dave@example.com", "Str0ngPass!", roles=["admin"])
        assert user.roles == ["admin"], "roles is not valid"

    def test_create_user_duplicate_username_raises(self):
        store = UserStore()
        store.create_user("eve", "eve@example.com", "Str0ngPass!")
        with pytest.raises(ValueError, match="already taken"):
            store.create_user("eve", "eve2@example.com", "Str0ngPass!")

    def test_create_user_duplicate_email_raises(self):
        store = UserStore()
        store.create_user("frank", "frank@example.com", "Str0ngPass!")
        with pytest.raises(ValueError, match="already registered"):
            store.create_user("frank2", "frank@example.com", "Str0ngPass!")

    def test_create_user_empty_username_raises(self):
        store = UserStore()
        with pytest.raises(ValueError, match="must not be empty"):
            store.create_user("", "a@b.com", "Str0ngPass!")

    def test_create_user_weak_password_raises(self):
        store = UserStore()
        with pytest.raises(ValueError, match="8 characters"):
            store.create_user("grace", "grace@example.com", "short")

    # ------------------------------------------------------------------ #
    # lookup                                                               #
    # ------------------------------------------------------------------ #

    def test_find_by_username(self):
        store = UserStore()
        created = store.create_user("hank", "hank@example.com", "Str0ngPass!")
        found = store.find_by_username("hank")
        assert found is not None, "found must be initialized"
        assert found.user_id == created.user_id, "user_id is not valid"

    def test_find_by_username_missing(self):
        store = UserStore()
        assert store.find_by_username("nobody") is None, "st is not valid"

    def test_find_by_email(self):
        store = UserStore()
        created = store.create_user("iris", "iris@example.com", "Str0ngPass!")
        found = store.find_by_email("iris@example.com")
        assert found is not None, "found must be initialized"
        assert found.user_id == created.user_id, "user_id is not valid"

    def test_get_user(self):
        store = UserStore()
        created = store.create_user("jan", "jan@example.com", "Str0ngPass!")
        assert store.get_user(created.user_id) is created, "st is not valid"

    def test_get_user_missing(self):
        store = UserStore()
        assert store.get_user("nonexistent-id") is None, "st is not valid"

    # ------------------------------------------------------------------ #
    # deactivate / delete                                                  #
    # ------------------------------------------------------------------ #

    def test_deactivate_user(self):
        store = UserStore()
        user = store.create_user("ken", "ken@example.com", "Str0ngPass!")
        store.deactivate_user(user.user_id)
        assert store.get_user(user.user_id).is_active is False, "is_active is not valid"

    def test_list_users_excludes_inactive_by_default(self):
        store = UserStore()
        active_user = store.create_user("leo", "leo@example.com", "Str0ngPass!")
        inactive_user = store.create_user("mia", "mia@example.com", "Str0ngPass!")
        store.deactivate_user(inactive_user.user_id)
        users = store.list_users()
        ids = [u.user_id for u in users]
        assert active_user.user_id in ids, "Condition must be true"
        assert inactive_user.user_id not in ids, "Condition must be true"

    def test_list_users_includes_inactive_when_requested(self):
        store = UserStore()
        u = store.create_user("nat", "nat@example.com", "Str0ngPass!")
        store.deactivate_user(u.user_id)
        users = store.list_users(include_inactive=True)
        assert any(x.user_id == u.user_id for x in users), "user_id is not valid"

    def test_delete_user(self):
        store = UserStore()
        user = store.create_user("oliver", "oliver@example.com", "Str0ngPass!")
        store.delete_user(user.user_id)
        assert store.get_user(user.user_id) is None, "st is not valid"

    def test_delete_nonexistent_raises(self):
        store = UserStore()
        with pytest.raises(KeyError):
            store.delete_user("ghost")

    # ------------------------------------------------------------------ #
    # update_password                                                      #
    # ------------------------------------------------------------------ #

    def test_update_password(self):
        store = UserStore()
        user = store.create_user("pat", "pat@example.com", "OldPass123!")
        store.update_password(user.user_id, "NewPass456!")
        # Verify old password no longer works
        with pytest.raises(InvalidCredentialsError):
            store.authenticate("pat", "OldPass123!")
        # Verify new password works
        authenticated = store.authenticate("pat", "NewPass456!")
        assert authenticated.user_id == user.user_id, "user_id is not valid"

    # ------------------------------------------------------------------ #
    # authenticate                                                         #
    # ------------------------------------------------------------------ #

    def test_authenticate_by_username(self):
        store = UserStore()
        user = store.create_user("quinn", "quinn@example.com", "Str0ngPass!")
        result = store.authenticate("quinn", "Str0ngPass!")
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_authenticate_by_email(self):
        store = UserStore()
        user = store.create_user("rex", "rex@example.com", "Str0ngPass!")
        result = store.authenticate("rex@example.com", "Str0ngPass!")
        assert result.user_id == user.user_id, "Result must not be empty"

    def test_authenticate_wrong_password_raises(self):
        store = UserStore()
        store.create_user("sam", "sam@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            store.authenticate("sam", "WrongPass!!")

    def test_authenticate_unknown_user_raises(self):
        store = UserStore()
        with pytest.raises(InvalidCredentialsError):
            store.authenticate("nobody", "Str0ngPass!")

    def test_authenticate_preserves_password_whitespace(self):
        store = UserStore()
        password = "  Str0ngPass!  "
        user = store.create_user("uma", "uma@example.com", password)
        authenticated = store.authenticate("uma", password)
        assert authenticated.user_id == user.user_id, "user_id is not valid"

    def test_authenticate_inactive_user_raises(self):
        store = UserStore()
        user = store.create_user("tina", "tina@example.com", "Str0ngPass!")
        store.deactivate_user(user.user_id)
        with pytest.raises(InvalidCredentialsError):
            store.authenticate("tina", "Str0ngPass!")
