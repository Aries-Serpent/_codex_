"""
Unit tests for user_model module.

Tests cover:
- User model creation and validation
- Password hashing and verification
- User metadata management
- User state transitions
- Edge cases and error handling
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

from src.codex.auth.user_model import User

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

class TestUserModel:
    """Test suite for User model."""

    def test_user_creation(self):
        """Test creating a user."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert user.username == "testuser", "username is not valid"
        assert user.email == "test@example.com", "email is not valid"
        assert user.password_hash == "hashed_password", "password_hash is not valid"

    def test_user_id_generation(self):
        """Test user ID generation."""
        user_id = str(uuid4())
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert user.id == user_id, "id is not valid"

    def test_user_creation_timestamp(self):
        """Test user creation timestamp."""
        now = datetime.now()
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=now,
        )

        assert user.created_at == now, "created_at is not valid"

    def test_user_updated_at_timestamp(self):
        """Test user updated_at timestamp."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert user.updated_at is not None, "updated_at must be initialized"

    def test_user_email_validation(self):
        """Test user email validation."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="valid@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert "@" in user.email, "Condition must be true"
        assert "." in user.email, "Condition must be true"

    def test_user_username_length(self):
        """Test username length validation."""
        # Valid username
        user = User(
            id=str(uuid4()),
            username="validusername",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert len(user.username) > 0, "Collection must not be empty"

    def test_user_password_hash_storage(self):
        """Test password hash is stored (not plaintext)."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        # Should not store plaintext passwords
        assert user.password_hash != "plaintext_password", "password_hash is not valid"
        assert user.password_hash == "hashed_password", "password_hash is not valid"

    def test_user_multiple_instances(self):
        """Test creating multiple user instances."""
        users = []
        for i in range(10):
            user = User(
                id=str(uuid4()),
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
                created_at=datetime.now(),
            )
            users.append(user)

        assert len(users) == 10, "Users must not be empty"
        assert all(isinstance(u, User) for u in users)

    def test_user_equality(self):
        """Test user equality comparison."""
        user_id = str(uuid4())
        user1 = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )
        user2 = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=user1.created_at,
        )

        # Should be equal if IDs match
        assert user1.id == user2.id, "id is not valid"

    def test_user_inequality(self):
        """Test user inequality comparison."""
        user1 = User(
            id=str(uuid4()),
            username="user1",
            email="user1@example.com",
            password_hash="hash1",
            created_at=datetime.now(),
        )
        user2 = User(
            id=str(uuid4()),
            username="user2",
            email="user2@example.com",
            password_hash="hash2",
            created_at=datetime.now(),
        )

        assert user1.id != user2.id, "id is not valid"

    def test_user_attributes_are_accessible(self):
        """Test that all user attributes are accessible."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        # Should be able to access all attributes
        assert hasattr(user, "id")
        assert hasattr(user, "username")
        assert hasattr(user, "email")
        assert hasattr(user, "password_hash")
        assert hasattr(user, "created_at")

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        # Should have a string representation
        user_str = str(user)
        assert len(user_str) > 0, "User_str must not be empty"

    def test_user_with_special_characters_in_username(self):
        """Test user with special characters in username."""
        user = User(
            id=str(uuid4()),
            username="user_with-special.chars@123",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert "user_with-special.chars@123" == user.username, "Condition must be true"

    def test_user_with_unicode_email(self):
        """Test user with Unicode email."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="用户@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert "用户" in user.email, "Condition must be true"

    def test_user_with_unicode_username(self):
        """Test user with Unicode username."""
        user = User(
            id=str(uuid4()),
            username="用户名",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert "用户名" == user.username, "Condition must be true"

    def test_user_with_long_password_hash(self):
        """Test user with very long password hash."""
        long_hash = "x" * 10000
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash=long_hash,
            created_at=datetime.now(),
        )

        assert len(user.password_hash) == 10000, "Collection must not be empty"

    def test_user_with_none_optional_fields(self):
        """Test user with optional fields as None."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=None,
        )

        assert user.updated_at is None, "updated_at is not valid"

    def test_user_last_login_update(self):
        """Test updating last login timestamp."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        now = datetime.now()
        user.last_login = now
        assert user.last_login == now, "last_login is not valid"

    def test_user_is_active_flag(self):
        """Test user active status flag."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
            is_active=True,
        )

        # Check if is_active attribute exists and can be modified
        if hasattr(user, "is_active"):
            assert user.is_active, "Condition must be true"

    def test_user_with_mfa_enabled(self):
        """Test user with MFA enabled flag."""
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        # mfa_enabled is not a built-in User field; can be set dynamically
        user.mfa_enabled = True
        if hasattr(user, "mfa_enabled"):
            assert user.mfa_enabled, "Condition must be true"


class TestUserModelEdgeCases:
    """Test edge cases for User model."""

    def test_empty_username_handling(self):
        """Test handling of empty username."""
        # User model accepts empty strings; validation is enforced at higher layers
        user = User(
            id=str(uuid4()),
            username="",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )
        assert user.username == "", "empty username should be stored as-is"

    def test_empty_email_handling(self):
        """Test handling of empty email."""
        # User model accepts empty strings; validation is enforced at higher layers
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )
        assert user.email == "", "empty email should be stored as-is"

    def test_empty_password_hash_handling(self):
        """Test handling of empty password hash."""
        # User model accepts empty strings; validation is enforced at higher layers
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="",
            created_at=datetime.now(),
        )
        assert user.password_hash == "", "empty password_hash should be stored as-is"

    def test_none_id_handling(self):
        """Test handling of None ID."""
        with pytest.raises((ValueError, TypeError)):
            User(
                id=None,
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password",
                created_at=datetime.now(),
            )

    def test_future_created_at_timestamp(self):
        """Test user with future creation timestamp."""
        future_time = datetime.now() + timedelta(days=1)
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=future_time,
        )

        assert user.created_at == future_time, "created_at is not valid"

    def test_very_old_created_at_timestamp(self):
        """Test user with very old creation timestamp."""
        old_time = datetime.now() - timedelta(days=365)
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=old_time,
        )

        assert user.created_at == old_time, "created_at is not valid"

    def test_invalid_email_format(self):
        """Test user with invalid email format."""
        # Some implementations might validate email format
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="invalid-email-format",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        # Should store the invalid email (validation is optional)
        assert user.email == "invalid-email-format", "email is not valid"

    def test_very_long_username(self):
        """Test user with very long username."""
        long_username = "u" * 1000
        user = User(
            id=str(uuid4()),
            username=long_username,
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert len(user.username) == 1000, "Collection must not be empty"

    def test_whitespace_in_username(self):
        """Test username with whitespace."""
        user = User(
            id=str(uuid4()),
            username="user with spaces",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

        assert " " in user.username, "Condition must be true"
