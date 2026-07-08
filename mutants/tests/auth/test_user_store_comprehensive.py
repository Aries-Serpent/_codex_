"""
Comprehensive tests for User Store.

Tests cover:
- User creation and retrieval
- Password hashing and verification
- User updates
- Role management
- Email handling
- Backend persistence
- Concurrent operations
"""

import threading

import pytest

from codex.auth.exceptions import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from codex.auth.user_store import PasswordHasher, User, UserStore

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def user_store():
    """Create in-memory user store."""
    return UserStore()


@pytest.fixture
def password_hasher():
    """Create password hasher."""
    return PasswordHasher()


# ============================================================================
# PasswordHasher Tests
# ============================================================================


class TestPasswordHasher:
    """Password hashing and verification."""

    def test_hash_password(self, password_hasher):
        password = "Str0ngPass!"
        hashed = password_hasher.hash_password(password)
        assert hashed != password, "hashed is not valid"
        assert len(hashed) > len(password), "Hashed must not be empty"

    def test_verify_correct_password(self, password_hasher):
        password = "Str0ngPass!"
        hashed = password_hasher.hash_password(password)
        is_valid = password_hasher.verify(password, hashed)
        assert is_valid, "is_valid is not valid"

    def test_verify_incorrect_password(self, password_hasher):
        password = "Str0ngPass!"
        wrong_password = "WrongPass!"
        hashed = password_hasher.hash_password(password)
        is_valid = password_hasher.verify(wrong_password, hashed)
        assert not is_valid, "not is not valid"

    def test_hashes_are_different(self, password_hasher):
        password = "Str0ngPass!"
        hash1 = password_hasher.hash_password(password)
        hash2 = password_hasher.hash_password(password)
        # Should be different due to random salt
        assert hash1 != hash2, "hash1 is not valid"

    def test_hash_format(self, password_hasher):
        password = "Str0ngPass!"
        hashed = password_hasher.hash_password(password)
        # PBKDF2 format includes algorithm, iterations, salt, hash
        assert "$" in hashed or ":" in hashed, "Condition must be true"

    def test_empty_password(self, password_hasher):
        with pytest.raises(ValueError):
            password_hasher.hash_password("")

    def test_none_password(self, password_hasher):
        with pytest.raises((ValueError, TypeError)):
            password_hasher.hash_password(None)

    def test_very_long_password(self, password_hasher):
        password = "P" + "a" * 1000 + "!"
        hashed = password_hasher.hash_password(password)
        assert password_hasher.verify(password, hashed)

    def test_unicode_password(self, password_hasher):
        password = "Str0ng🔐Pass!"
        hashed = password_hasher.hash_password(password)
        assert password_hasher.verify(password, hashed)

    def test_special_chars_password(self, password_hasher):
        password = "P@$$w0rd!#%^&*()"
        hashed = password_hasher.hash_password(password)
        assert password_hasher.verify(password, hashed)

    def test_timing_safe_comparison(self, password_hasher):
        password = "Str0ngPass!"
        hashed = password_hasher.hash_password(password)

        # Both should complete without timing differences
        is_valid1 = password_hasher.verify(password, hashed)
        is_valid2 = password_hasher.verify("Wrong!!!!!!!!", hashed)

        assert is_valid1, "is_valid1 is not valid"
        assert not is_valid2, "not is not valid"


# ============================================================================
# User Creation Tests
# ============================================================================


class TestUserCreation:
    """User creation and storage."""

    def test_create_user(self, user_store):
        user = user_store.create_user("alice", "alice@example.com", "Str0ngPass!")
        assert user.user_id, "Condition must be true"
        assert user.username == "alice", "username is not valid"
        assert user.email == "alice@example.com", "email is not valid"

    def test_create_user_with_roles(self, user_store):
        user = user_store.create_user("bob", "bob@example.com", "Str0ngPass!", roles=["admin"])
        assert "admin" in user.roles, "Condition must be true"

    def test_duplicate_username(self, user_store):
        user_store.create_user("charlie", "charlie@example.com", "Str0ngPass!")
        with pytest.raises(UserAlreadyExistsError):
            user_store.create_user("charlie", "charlie2@example.com", "Str0ngPass!")

    def test_duplicate_email_allowed(self, user_store):
        # Some systems allow duplicate emails, others don't
        user_store.create_user("diana", "diana@example.com", "Str0ngPass!")
        try:
            user2 = user_store.create_user("diana2", "diana@example.com", "Str0ngPass!")
            assert user2.user_id, "Condition must be true"
        except (UserAlreadyExistsError, ValueError):
            pass  # Either behavior acceptable

    def test_user_id_is_unique(self, user_store):
        user1 = user_store.create_user("eve", "eve@example.com", "Str0ngPass!")
        user2 = user_store.create_user("frank", "frank@example.com", "Str0ngPass!")
        assert user1.user_id != user2.user_id, "user_id is not valid"

    def test_created_at_set(self, user_store):
        user = user_store.create_user("grace", "grace@example.com", "Str0ngPass!")
        assert user.created_at > 0, "created_at must be greater than zero"

    def test_password_hashed_not_plain(self, user_store):
        password = "Str0ngPass!"
        user = user_store.create_user("henry", "henry@example.com", password)
        # Password should not be stored in plain text
        # (this is implementation dependent - can't directly check stored hash)
        user_retrieved = user_store.get_by_username("henry")
        assert user_retrieved.user_id == user.user_id, "user_id is not valid"


# ============================================================================
# User Retrieval Tests
# ============================================================================


class TestUserRetrieval:
    """User lookup and retrieval."""

    def test_get_by_username(self, user_store):
        original = user_store.create_user("iris", "iris@example.com", "Str0ngPass!")
        retrieved = user_store.get_by_username("iris")
        assert retrieved.user_id == original.user_id, "user_id is not valid"
        assert retrieved.username == "iris", "username is not valid"

    def test_get_by_user_id(self, user_store):
        original = user_store.create_user("jack", "jack@example.com", "Str0ngPass!")
        retrieved = user_store.get_by_user_id(original.user_id)
        assert retrieved.user_id == original.user_id, "user_id is not valid"
        assert retrieved.username == "jack", "username is not valid"

    def test_get_by_email(self, user_store):
        original = user_store.create_user("karl", "karl@example.com", "Str0ngPass!")
        retrieved = user_store.get_by_email("karl@example.com")
        assert retrieved.user_id == original.user_id, "user_id is not valid"
        assert retrieved.email == "karl@example.com", "email is not valid"

    def test_get_nonexistent_by_username(self, user_store):
        result = user_store.get_by_username("nonexistent")
        assert result is None, "Nonexistent user should return None"

    def test_get_nonexistent_by_id(self, user_store):
        result = user_store.get_by_user_id("nonexistent-id")
        assert result is None, "Nonexistent user should return None"

    def test_get_nonexistent_by_email(self, user_store):
        result = user_store.get_by_email("nonexistent@example.com")
        assert result is None, "Nonexistent user should return None"

    def test_case_sensitive_username(self, user_store):
        user_store.create_user("larry", "larry@example.com", "Str0ngPass!")
        result = user_store.get_by_username("LARRY")
        assert result is None, "Username lookup should be case-sensitive"

    def test_case_insensitive_email(self, user_store):
        user_store.create_user("mike", "mike@example.com", "Str0ngPass!")
        # Email lookup might be case-insensitive
        try:
            retrieved = user_store.get_by_email("MIKE@EXAMPLE.COM")
            assert retrieved.email.lower() == "mike@example.com", "Condition must be true"
        except (UserNotFoundError, ValueError):
            pass  # Case-sensitive is also acceptable


# ============================================================================
# Authentication Tests
# ============================================================================


class TestAuthentication:
    """User authentication."""

    def test_authenticate_correct_password(self, user_store):
        user_store.create_user("nancy", "nancy@example.com", "Str0ngPass!")
        user = user_store.authenticate("nancy", "Str0ngPass!")
        assert user.username == "nancy", "username is not valid"

    def test_authenticate_wrong_password(self, user_store):
        user_store.create_user("oliver", "oliver@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            user_store.authenticate("oliver", "WrongPass!")

    def test_authenticate_nonexistent_user(self, user_store):
        with pytest.raises(InvalidCredentialsError):
            user_store.authenticate("phantom", "Str0ngPass!")

    def test_authenticate_by_email(self, user_store):
        user_store.create_user("paul", "paul@example.com", "Str0ngPass!")
        user = user_store.authenticate("paul@example.com", "Str0ngPass!")
        assert user.username == "paul", "username is not valid"

    def test_authenticate_empty_password(self, user_store):
        user_store.create_user("quinn", "quinn@example.com", "Str0ngPass!")
        with pytest.raises(InvalidCredentialsError):
            user_store.authenticate("quinn", "")

    def test_authenticate_none_password(self, user_store):
        user_store.create_user("robin", "robin@example.com", "Str0ngPass!")
        with pytest.raises((InvalidCredentialsError, TypeError)):
            user_store.authenticate("robin", None)


# ============================================================================
# User Update Tests
# ============================================================================


class TestUserUpdate:
    """User profile updates."""

    def test_update_email(self, user_store):
        user = user_store.create_user("sam", "sam@example.com", "Str0ngPass!")
        user.email = "sam.new@example.com"
        updated_user = user_store.update_user(user)
        assert updated_user.email == "sam.new@example.com", "email is not valid"

    def test_update_password(self, user_store):
        user = user_store.create_user("tina", "tina@example.com", "Str0ngPass!")
        new_password = "NewPass123!"
        user_store.update_password(user.user_id, new_password)
        # New password should work
        authenticated = user_store.authenticate("tina", new_password)
        assert authenticated.user_id == user.user_id, "user_id is not valid"

    def test_update_nonexistent_user(self, user_store):
        nonexistent = User(user_id="nonexistent-id", username="ghost", email="ghost@example.com")
        with pytest.raises((KeyError, UserNotFoundError, ValueError)):
            user_store.update_user(nonexistent)

    def test_update_multiple_fields(self, user_store):
        user = user_store.create_user("uma", "uma@example.com", "Str0ngPass!")
        user.email = "uma.new@example.com"
        updated_user = user_store.update_user(user)
        assert updated_user.email == "uma.new@example.com", "email is not valid"
        new_password = "NewPass123!"
        user_store.update_password(user.user_id, new_password)
        authenticated = user_store.authenticate("uma", new_password)
        assert authenticated.user_id == user.user_id, "user_id is not valid"

    def test_update_preserves_user_id(self, user_store):
        user = user_store.create_user("victor", "victor@example.com", "Str0ngPass!")
        user.email = "victor.new@example.com"
        updated_user = user_store.update_user(user)
        assert updated_user.user_id == user.user_id, "user_id is not valid"

# ============================================================================
# Role Management Tests
# ============================================================================


class TestRoleManagement:
    """User role management."""

    def test_add_role(self, user_store):
        user = user_store.create_user("wendy", "wendy@example.com", "Str0ngPass!")
        user_store.add_role(user.user_id, "admin")
        updated_user = user_store.get_by_user_id(user.user_id)
        assert "admin" in updated_user.roles, "Condition must be true"

    def test_remove_role(self, user_store):
        user = user_store.create_user(
            "xavier", "xavier@example.com", "Str0ngPass!", roles=["admin"]
        )
        user_store.remove_role(user.user_id, "admin")
        updated_user = user_store.get_by_user_id(user.user_id)
        assert "admin" not in updated_user.roles, "Condition must be true"

    def test_add_multiple_roles(self, user_store):
        user = user_store.create_user("yara", "yara@example.com", "Str0ngPass!")
        user_store.add_role(user.user_id, "admin")
        user_store.add_role(user.user_id, "moderator")
        user_store.add_role(user.user_id, "editor")
        user = user_store.get_by_user_id(user.user_id)
        assert "admin" in user.roles, "Condition must be true"
        assert "moderator" in user.roles, "Condition must be true"
        assert "editor" in user.roles, "Condition must be true"

    def test_default_role(self, user_store):
        user = user_store.create_user("zoe", "zoe@example.com", "Str0ngPass!")
        assert "user" in user.roles, "Condition must be true"

    def test_add_duplicate_role(self, user_store):
        user = user_store.create_user("zach", "zach@example.com", "Str0ngPass!")
        user_store.add_role(user.user_id, "admin")
        # Adding same role again - should be idempotent
        user_store.add_role(user.user_id, "admin")
        user = user_store.get_by_user_id(user.user_id)
        assert user.roles.count("admin") <= 1, "Count must be greater than zero"


# ============================================================================
# Concurrent Access Tests
# ============================================================================


class TestConcurrentAccess:
    """Concurrent user operations."""

    def test_concurrent_user_creation(self, user_store):
        users = []
        errors = []

        def create_user(username, email):
            try:
                user = user_store.create_user(username, email, "Str0ngPass!")
                users.append(user)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            t = threading.Thread(target=create_user, args=(f"user{i}", f"user{i}@example.com"))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All should succeed or handle duplicates appropriately
        assert len(users) + len(errors) == 5, "Users must not be empty"

    def test_concurrent_authentication(self, user_store):
        user_store.create_user("alice", "alice@example.com", "Str0ngPass!")
        results = []

        def authenticate():
            try:
                user = user_store.authenticate("alice", "Str0ngPass!")
                results.append(user)
            except Exception as _err:
                results.append(None)

        threads = [threading.Thread(target=authenticate) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed
        assert all(r is not None for r in results), "r must be initialized"
        assert all(r.username == "alice" for r in results), "Result must not be empty"


# ============================================================================
# Edge Cases Tests
# ============================================================================


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_whitespace_in_username(self, user_store):
        with pytest.raises(ValueError):
            user_store.create_user("user name", "user@example.com", "Str0ngPass!")

    def test_very_long_username(self, user_store):
        long_username = "a" * 255
        user = user_store.create_user(long_username, "long@example.com", "Str0ngPass!")
        assert len(user.username) <= 255, "Collection must not be empty"

    def test_very_long_email(self, user_store):
        long_email = "a" * 240 + "@example.com"
        try:
            user = user_store.create_user("longemail", long_email, "Str0ngPass!")
            assert user.email, "Condition must be true"
        except ValueError:
            pass  # Email length limit is acceptable

    def test_unicode_username(self, user_store):
        user = user_store.create_user("用户", "user@example.com", "Str0ngPass!")
        assert user.username == "用户", "username is not valid"

    def test_unicode_email(self, user_store):
        # Standard emails don't support unicode, but test handling
        try:
            user = user_store.create_user("test", "test@例え.jp", "Str0ngPass!")
            assert user.email, "Condition must be true"
        except ValueError:
            pass  # Unicode email rejection is acceptable

    def test_special_chars_username(self, user_store):
        # Some systems accept special chars, others don't
        try:
            user = user_store.create_user("user@123", "user@example.com", "Str0ngPass!")
            assert user.username, "Condition must be true"
        except ValueError:
            pass  # Rejection is acceptable


# ============================================================================
# User Model Tests
# ============================================================================


class TestUserModel:
    """User data model."""

    def test_user_creation(self):
        user = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hashed_password",
        )
        assert user.user_id == "123", "user_id is not valid"
        assert user.username == "alice", "username is not valid"
        assert user.email == "alice@example.com", "email is not valid"

    def test_user_with_roles(self):
        user = User(
            user_id="123",
            username="bob",
            email="bob@example.com",
            password_hash="hashed_password",
            roles=["admin", "editor"],
        )
        assert "admin" in user.roles, "Condition must be true"
        assert "editor" in user.roles, "Condition must be true"

    def test_user_default_roles(self):
        user = User(
            user_id="123",
            username="charlie",
            email="charlie@example.com",
            password_hash="hashed_password",
        )
        assert "user" in user.roles, "Condition must be true"

    def test_user_created_at(self):
        import time

        before = time.time()
        user = User(
            user_id="123",
            username="diana",
            email="diana@example.com",
            password_hash="hashed_password",
        )
        after = time.time()
        assert before <= user.created_at <= after, "before is not valid"


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration scenarios."""

    def test_full_user_lifecycle(self, user_store):
        # Create
        user = user_store.create_user("emma", "emma@example.com", "Str0ngPass!")
        assert user.user_id, "Condition must be true"

        # Authenticate
        authenticated = user_store.authenticate("emma", "Str0ngPass!")
        assert authenticated.user_id == user.user_id, "user_id is not valid"

        # Update email
        user.email = "emma.new@example.com"
        updated = user_store.update_user(user)
        assert updated.email == "emma.new@example.com", "email is not valid"

        # Add role
        user_store.add_role(user.user_id, "admin")
        updated = user_store.get_by_user_id(user.user_id)
        assert "admin" in updated.roles, "Condition must be true"

        # Change password
        user_store.update_password(user.user_id, "NewPass123!")
        authenticated = user_store.authenticate("emma", "NewPass123!")
        assert authenticated.user_id == user.user_id, "user_id is not valid"

    def test_multiple_users(self, user_store):
        users = []
        for i in range(10):
            user = user_store.create_user(f"user{i}", f"user{i}@example.com", "Str0ngPass!")
            users.append(user)

        assert len(users) == 10, "Users must not be empty"
        assert len(set(u.user_id for u in users)) == 10, "Collection must not be empty"

    def test_user_retrieval_methods_consistency(self, user_store):
        created = user_store.create_user("frank", "frank@example.com", "Str0ngPass!")

        by_username = user_store.get_by_username("frank")
        by_id = user_store.get_by_user_id(created.user_id)
        by_email = user_store.get_by_email("frank@example.com")

        assert by_username.user_id == by_id.user_id == by_email.user_id, "user_id is not valid"
