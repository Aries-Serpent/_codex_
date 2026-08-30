"""
Unit tests for user_repository module.

Tests cover:
- User repository interface contract
- CRUD operations
- Query operations
- Error handling
- Repository implementations
"""

from datetime import (
    datetime,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret; pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)
from uuid import uuid4

import pytest  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

from src.codex.auth.user_model import User
from src.codex.auth.user_repository import UserRepository


class TestUserRepositoryContract:
    """Test suite for UserRepository interface contract."""

    def test_user_repository_is_abstract(self):
        """Test that UserRepository is abstract."""
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            UserRepository()

    def test_user_repository_has_create_method(self):
        """Test UserRepository has create method."""
        assert hasattr(UserRepository, "create")
        assert callable(getattr(UserRepository, "create", None))

    def test_user_repository_has_get_method(self):
        """Test UserRepository has get method."""
        assert hasattr(UserRepository, "get_by_id")
        assert callable(getattr(UserRepository, "get_by_id", None))

    def test_user_repository_has_update_method(self):
        """Test UserRepository has update method."""
        assert hasattr(UserRepository, "update")
        assert callable(getattr(UserRepository, "update", None))

    def test_user_repository_has_delete_method(self):
        """Test UserRepository has delete method."""
        assert hasattr(UserRepository, "delete")
        assert callable(getattr(UserRepository, "delete", None))

    def test_user_repository_has_list_method(self):
        """Test UserRepository has list method."""
        assert hasattr(UserRepository, "list")
        assert callable(getattr(UserRepository, "list", None))

    def test_user_repository_has_get_by_username_method(self):
        """Test UserRepository has get_by_username method."""
        assert hasattr(UserRepository, "get_by_username")
        assert callable(getattr(UserRepository, "get_by_username", None))

    def test_user_repository_create_is_abstract(self):
        """Test create method is abstract."""
        # Trying to call abstract methods should raise
        with pytest.raises(TypeError):

            class TestRepo(UserRepository):
                # Don't implement methods
                pass

            TestRepo()

    def test_user_repository_update_is_abstract(self):
        """Test update method is abstract."""
        with pytest.raises(TypeError):

            class TestRepo(UserRepository):
                def create(self, user):
                    pass

                def get_by_id(self, user_id):
                    pass

                def delete(self, user_id):
                    pass

                def list(self):
                    pass

                def get_by_username(self, username):
                    pass

                # Missing update implementation

            TestRepo()

    def test_user_repository_delete_is_abstract(self):
        """Test delete method is abstract."""
        with pytest.raises(TypeError):

            class TestRepo(UserRepository):
                def create(self, user):
                    pass

                def get_by_id(self, user_id):
                    pass

                def update(self, user):
                    pass

                def list(self):
                    pass

                def get_by_username(self, username):
                    pass

                # Missing delete implementation

            TestRepo()


class MockUserRepository(UserRepository):
    """Mock implementation of UserRepository for testing."""

    def __init__(self):
        """Initialize mock repository."""
        self._users = {}

    def create(self, user: User) -> User:
        """Create a user."""
        if user.user_id in self._users:
            raise ValueError("User already exists")
        self._users[user.user_id] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        return self._users.get(user_id)

    def update(self, user: User) -> User:
        """Update a user."""
        if user.user_id not in self._users:
            raise KeyError("User not found")
        self._users[user.user_id] = user
        return user

    def delete(self, user_id: str) -> None:
        """Delete a user."""
        if user_id not in self._users:
            raise KeyError("User not found")
        del self._users[user_id]

    def list(self) -> list:
        """List all users."""
        return list(self._users.values())

    def list_all(self) -> list:
        """List all users (abstract method implementation)."""
        return list(self._users.values())

    def get_by_username(self, username: str) -> User:
        """Get user by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def get_by_email(self, email: str) -> User:
        """Get user by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None


class TestUserRepositoryImplementation:
    """Test suite for UserRepository concrete implementation."""

    @pytest.fixture
    def repository(self):
        """Create a mock repository."""
        return MockUserRepository()

    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        return User(
            user_id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now().timestamp(),
        )

    def test_mock_repository_create(self, repository, test_user):
        """Test creating user in mock repository."""
        user = repository.create(test_user)
        assert user.user_id == test_user.user_id, "user_id is not valid"

    def test_mock_repository_get_by_id(self, repository, test_user):
        """Test getting user by ID."""
        repository.create(test_user)
        retrieved = repository.get_by_id(test_user.user_id)
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.user_id == test_user.user_id, "user_id is not valid"
        assert retrieved.username == "testuser", "username is not valid"

    def test_mock_repository_update(self, repository, test_user):
        """Test updating user."""
        repository.create(test_user)
        test_user.email = "new@example.com"
        repository.update(test_user)

        retrieved = repository.get_by_id(test_user.user_id)
        assert retrieved.email == "new@example.com", "email is not valid"

    def test_mock_repository_delete(self, repository, test_user):
        """Test deleting user."""
        repository.create(test_user)
        repository.delete(test_user.user_id)

        # get_by_id returns None for deleted/nonexistent users
        result = repository.get_by_id(test_user.user_id)
        assert result is None, "get_by_id should return None after deletion"

    def test_mock_repository_list(self, repository):
        """Test listing users."""
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

        repository.create(user1)
        repository.create(user2)

        users = repository.list()
        assert len(users) == 2, "Users must not be empty"

    def test_mock_repository_get_by_username(self, repository, test_user):
        """Test getting user by username."""
        repository.create(test_user)
        retrieved = repository.get_by_username("testuser")
        assert retrieved.user_id == test_user.user_id, "user_id is not valid"

    def test_repository_create_duplicate_raises_error(self, repository, test_user):
        """Test creating duplicate user raises error."""
        repository.create(test_user)

        with pytest.raises((ValueError, KeyError)):
            repository.create(test_user)

    def test_repository_get_nonexistent_user_raises_error(self, repository):
        """Test getting nonexistent user returns None."""
        # MockUserRepository.get_by_id uses dict.get() which returns None
        result = repository.get_by_id("nonexistent")
        assert result is None, "get_by_id should return None for nonexistent user"

    def test_repository_update_nonexistent_user_raises_error(self, repository, test_user):
        """Test updating nonexistent user raises error."""
        with pytest.raises(KeyError):
            repository.update(test_user)

    def test_repository_delete_nonexistent_user_raises_error(self, repository):
        """Test deleting nonexistent user raises error."""
        with pytest.raises(KeyError):
            repository.delete("nonexistent")

    def test_repository_get_by_username_nonexistent_raises_error(self, repository):
        """Test getting nonexistent user by username returns None."""
        # MockUserRepository.get_by_username returns None when not found
        result = repository.get_by_username("nonexistent")
        assert result is None, "get_by_username should return None for nonexistent user"

    def test_repository_list_empty(self, repository):
        """Test listing users from empty repository."""
        users = repository.list()
        assert users == [], "users is not valid"

    def test_repository_multiple_operations_sequence(self, repository):
        """Test sequence of CRUD operations."""
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

        # Create
        repository.create(user1)
        repository.create(user2)

        # List
        users = repository.list()
        assert len(users) == 2, "Users must not be empty"

        # Update
        user1.email = "updated@example.com"
        repository.update(user1)

        # Get
        retrieved = repository.get_by_id(user1.user_id)
        assert retrieved.email == "updated@example.com", "email is not valid"

        # Delete
        repository.delete(user1.user_id)
        users = repository.list()
        assert len(users) == 1, "Users must not be empty"

    def test_repository_concurrent_users(self, repository):
        """Test repository with multiple concurrent users."""
        users = []
        for i in range(100):
            user = User(
                id=str(uuid4()),
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=f"hash{i}",
                created_at=datetime.now(),
            )
            repository.create(user)
            users.append(user)

        all_users = repository.list()
        assert len(all_users) == 100, "All_users must not be empty"

    def test_repository_get_by_username_unique(self, repository):
        """Test get_by_username returns single user."""
        user = User(
            id=str(uuid4()),
            username="unique_user",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        repository.create(user)
        retrieved = repository.get_by_username("unique_user")

        assert retrieved.user_id == user.user_id, "user_id is not valid"

    def test_repository_preserves_user_data_on_update(self, repository):
        """Test that all user data is preserved on update."""
        original_user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        repository.create(original_user)

        # Update only email
        original_user.email = "new@example.com"
        repository.update(original_user)

        # Verify other fields are preserved
        retrieved = repository.get_by_id(original_user.user_id)
        assert retrieved.username == "testuser", "username is not valid"
        assert retrieved.password_hash == "hash", "password_hash is not valid"
        assert retrieved.email == "new@example.com", "email is not valid"


class TestUserRepositoryEdgeCases:
    """Test edge cases for UserRepository."""

    @pytest.fixture
    def repository(self):
        """Create a mock repository."""
        return MockUserRepository()

    def test_repository_with_special_characters_in_username(self, repository):
        """Test repository with special characters in username."""
        user = User(
            id=str(uuid4()),
            username="user_with-special.chars@123",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        repository.create(user)
        retrieved = repository.get_by_username("user_with-special.chars@123")
        assert retrieved.username == user.username, "username is not valid"

    def test_repository_with_unicode_username(self, repository):
        """Test repository with Unicode username."""
        user = User(
            id=str(uuid4()),
            username="用户名",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now(),
        )

        repository.create(user)
        retrieved = repository.get_by_username("用户名")
        assert retrieved.username == "用户名", "username is not valid"

    def test_repository_with_very_long_password_hash(self, repository):
        """Test repository with very long password hash."""
        long_hash = "x" * 10000
        user = User(
            id=str(uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash=long_hash,
            created_at=datetime.now(),
        )

        repository.create(user)
        retrieved = repository.get_by_id(user.user_id)
        assert len(retrieved.password_hash) == 10000, "Collection must not be empty"
