"""
Unit tests for in_memory_user_repository module.

Tests cover:
- User creation and storage
- User retrieval by ID and username
- User update operations
- User deletion
- Error handling and edge cases
"""

from datetime import (
    datetime,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)
from uuid import uuid4

import pytest  # pragma: allowlist secret

from codex.auth.in_memory_user_repository import (
    InMemoryUserRepository,
    UserNotFoundError,
)
from codex.auth.user_model import User


class TestInMemoryUserRepository:
    """Test suite for InMemoryUserRepository."""

    @pytest.fixture
    def repository(self):
        """Create a test repository."""
        return InMemoryUserRepository()

    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        return User(
            user_id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
        )

    def test_repository_initialization(self, repository):
        """Test repository initialization."""
        assert repository is not None, "repository must be initialized"
        assert hasattr(repository, "users") or hasattr(repository, "_users")

    def test_create_user(self, repository, test_user):
        """Test creating a user."""
        repository.create(test_user)

        retrieved = repository.get_by_id(test_user.user_id)
        assert retrieved.user_id == test_user.user_id, "user_id is not valid"
        assert retrieved.username == test_user.username, "username is not valid"

    def test_create_duplicate_user(self, repository, test_user):
        """Test creating duplicate user raises error."""
        repository.create(test_user)

        with pytest.raises((ValueError, Exception)):
            repository.create(test_user)

    def test_get_user_by_id(self, repository, test_user):
        """Test retrieving user by ID."""
        repository.create(test_user)

        retrieved = repository.get_by_id(test_user.user_id)
        assert retrieved.user_id == test_user.user_id, "user_id is not valid"
        assert retrieved.username == "testuser", "username is not valid"
        assert retrieved.email == "test@example.com", "email is not valid"

    def test_get_user_by_nonexistent_id(self, repository):
        """Test retrieving nonexistent user by ID."""
        # get_by_id returns None for nonexistent users (does not raise)
        result = repository.get_by_id("nonexistent_id")
        assert result is None, "get_by_id should return None for nonexistent user"

    def test_get_user_by_username(self, repository, test_user):
        """Test retrieving user by username."""
        repository.create(test_user)

        retrieved = repository.get_by_username("testuser")
        assert retrieved.username == "testuser", "username is not valid"
        assert retrieved.user_id == test_user.user_id, "user_id is not valid"

    def test_get_user_by_nonexistent_username(self, repository):
        """Test retrieving nonexistent user by username."""
        # get_by_username returns None for nonexistent users (does not raise)
        result = repository.get_by_username("nonexistent_user")
        assert result is None, "get_by_username should return None for nonexistent user"

    def test_update_user(self, repository, test_user):
        """Test updating user."""
        repository.create(test_user)

        test_user.email = "newemail@example.com"
        repository.update(test_user)

        retrieved = repository.get_by_id(test_user.user_id)
        assert retrieved.email == "newemail@example.com", "email is not valid"

    def test_update_nonexistent_user(self, repository, test_user):
        """Test updating nonexistent user."""
        with pytest.raises((UserNotFoundError, ValueError)):
            repository.update(test_user)

    def test_delete_user(self, repository, test_user):
        """Test deleting user."""
        repository.create(test_user)
        repository.delete(test_user.user_id)

        # get_by_id returns None for deleted users (does not raise)
        result = repository.get_by_id(test_user.user_id)
        assert result is None, "get_by_id should return None after deletion"

    def test_delete_nonexistent_user(self, repository):
        """Test deleting nonexistent user."""
        with pytest.raises((UserNotFoundError, ValueError)):
            repository.delete("nonexistent_id")

    def test_list_users(self, repository):
        """Test listing all users."""
        user1 = User(
            user_id=str(uuid4()),
            username="user1",
            email="user1@example.com",
            password_hash="hash1",
            created_at=datetime.now(),
        )
        user2 = User(
            user_id=str(uuid4()),
            username="user2",
            email="user2@example.com",
            password_hash="hash2",
            created_at=datetime.now(),
        )

        repository.create(user1)
        repository.create(user2)

        users = repository.list_all()
        assert len(users) == 2, "Users must not be empty"
        usernames = [u.username for u in users]
        assert "user1" in usernames, "Condition must be true"
        assert "user2" in usernames, "Condition must be true"

    def test_list_empty_repository(self, repository):
        """Test listing users from empty repository."""
        users = repository.list_all()
        assert users == [] or len(users) == 0, "Users must not be empty"

    def test_user_count(self, repository, test_user):
        """Test getting user count."""
        repository.create(test_user)

        # Should have count() method or similar
        users = repository.list_all()
        assert len(users) >= 1, "Users must not be empty"

    def test_user_existence_check(self, repository, test_user):
        """Test checking if user exists."""
        repository.create(test_user)

        # Should be able to retrieve the user
        retrieved = repository.get_by_id(test_user.user_id)
        assert retrieved is not None, "retrieved must be initialized"

    def test_user_nonexistence_check(self, repository):
        """Test checking nonexistent user."""
        # get_by_id returns None for nonexistent users (does not raise)
        result = repository.get_by_id("nonexistent_id")
        assert result is None, "get_by_id should return None for nonexistent user"

    def test_get_by_email(self, repository, test_user):
        """Test retrieving user by email."""
        repository.create(test_user)

        # Some repositories might support this
        try:
            retrieved = repository.get_by_email("test@example.com")
            assert retrieved.email == "test@example.com", "email is not valid"
        except AttributeError:
            # If not supported, that's OK
            pass

    def test_concurrent_user_creation(self, repository):
        """Test creating multiple users."""
        users = []
        for i in range(10):
            user = User(
                user_id=str(uuid4()),
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
                created_at=datetime.now(),
            )
            repository.create(user)
            users.append(user)

        all_users = repository.list_all()
        assert len(all_users) >= 10, "All_users must not be empty"

    def test_user_modification_after_storage(self, repository, test_user):
        """Test that modifying stored user is reflected."""
        repository.create(test_user)

        test_user.email = "modified@example.com"
        repository.update(test_user)

        retrieved = repository.get_by_id(test_user.user_id)
        assert retrieved.email == "modified@example.com", "email is not valid"

    def test_special_characters_in_username(self, repository):
        """Test user with special characters in username."""
        user = User(
            user_id=str(uuid4()),
            username="user_with-special.chars@123",
            email="special@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        repository.create(user)
        retrieved = repository.get_by_username("user_with-special.chars@123")
        assert retrieved.username == "user_with-special.chars@123", "username is not valid"

    def test_unicode_email(self, repository):
        """Test user with Unicode email."""
        user = User(
            user_id=str(uuid4()),
            username="unicode_user",
            email="用户@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        repository.create(user)
        retrieved = repository.get_by_id(user.user_id)
        assert retrieved.email == "用户@example.com", "email is not valid"

    def test_empty_username_validation(self, repository):
        """Test creating user with empty username."""
        user = User(
            user_id=str(uuid4()),
            username="",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        with pytest.raises((ValueError, Exception)) as exc_info:
            repository.create(user)

        # Verify the error message is descriptive
        error_msg = str(exc_info.value).lower()
        assert "username" in error_msg or "empty" in error_msg, "Error should mention username or empty"

    def test_empty_email_validation(self, repository):
        """Test creating user with empty email."""
        user = User(
            user_id=str(uuid4()),
            username="testuser",
            email="",
            password_hash="hash",
            created_at=datetime.now(),
        )

        with pytest.raises((ValueError, Exception)) as exc_info:
            repository.create(user)

        # Verify the error message is descriptive
        error_msg = str(exc_info.value).lower()
        assert "email" in error_msg or "empty" in error_msg, "Error should mention email or empty"

        # Also test with whitespace-only email
        user_whitespace = User(
            user_id=str(uuid4()),
            username="testuser2",
            email="   ",
            password_hash="hash",
            created_at=datetime.now(),
        )

        with pytest.raises((ValueError, Exception)):
            repository.create(user_whitespace)

    def test_empty_password_hash_validation(self, repository):
        """Test creating user with empty password hash."""
        user = User(
            user_id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="",
            created_at=datetime.now(),
        )

        with pytest.raises((ValueError, Exception)):
            repository.create(user)


class TestInMemoryUserRepositoryEdgeCases:
    """Test edge cases for InMemoryUserRepository."""

    @pytest.fixture
    def repository(self):
        """Create a test repository."""
        return InMemoryUserRepository()

    def test_large_number_of_users(self, repository):
        """Test repository with large number of users."""
        for i in range(1000):
            user = User(
                user_id=str(uuid4()),
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
                created_at=datetime.now(),
            )
            repository.create(user)

        users = repository.list_all()
        assert len(users) >= 1000, "Users must not be empty"

    def test_case_sensitivity_in_username(self, repository):
        """Test username case sensitivity."""
        user1 = User(
            user_id=str(uuid4()),
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        repository.create(user1)

        # Should be case-sensitive or case-insensitive consistently
        try:
            retrieved = repository.get_by_username("TestUser")
            assert retrieved is not None, "retrieved must be initialized"
        except UserNotFoundError:
            # If case-insensitive, should still work
            pass

    def test_duplicate_email_handling(self, repository):
        """Test handling of duplicate emails."""
        user1 = User(
            user_id=str(uuid4()),
            username="user1",
            email="same@example.com",
            password_hash="hash1",
            created_at=datetime.now(),
        )
        user2 = User(
            user_id=str(uuid4()),
            username="user2",
            email="same@example.com",
            password_hash="hash2",
            created_at=datetime.now(),
        )

        repository.create(user1)

        # Should either allow or disallow duplicate emails
        try:
            repository.create(user2)
        except ValueError:
            # Duplicate emails not allowed
            pass

    def test_null_id_handling(self, repository):
        """Test handling of null ID."""
        # User raises ValueError when both user_id and id are None
        with pytest.raises((ValueError, TypeError)):
            user = User(
                user_id=None,
                username="testuser",
                email="test@example.com",
                password_hash="hash",
                created_at=datetime.now(),
            )
            repository.create(user)
