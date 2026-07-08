"""
Comprehensive Wave 2 tests for User Store module.

Tests cover:
- User creation and retrieval
- Password hashing and verification
- User updates and deletion
- Concurrent access
- Edge cases
"""

import pytest  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

from codex.auth.exceptions import InvalidCredentialsError
from codex.auth.user_model import PasswordHasher
from codex.auth.user_store import User, UserStore

# ============================================================================ # pragma: allowlist secret
# Fixtures
# ============================================================================


@pytest.fixture
def user_store():
    """Create a test user store."""
    return UserStore()


@pytest.fixture
def password_hasher():
    """Create a password hasher."""
    return PasswordHasher()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
    }


# ============================================================================
# User Creation Tests
# ============================================================================


class TestUserCreation:
    """Test user creation functionality."""

    def test_create_user_basic(self, user_store, test_user_data):
        """Test creating a basic user."""
        user = user_store.create_user(
            test_user_data["username"],
            test_user_data["email"],
            test_user_data["password"],
        )
        assert user.username == test_user_data["username"], "Data must not be empty"
        assert user.email == test_user_data["email"], "Data must not be empty"
        assert user.user_id is not None, "user_id must be initialized"

    def test_create_user_with_roles(self, user_store):
        """Test creating user with roles."""
        user = user_store.create_user(
            "admin",
            "admin@example.com",
            "AdminPass123!",
            roles=["admin", "moderator"],
        )
        assert "admin" in user.roles, "Condition must be true"
        assert "moderator" in user.roles, "Condition must be true"

    def test_create_user_default_roles(self, user_store):
        """Test that created user has default roles."""
        user = user_store.create_user(
            "alice",
            "alice@example.com",
            "Pass123!",
        )
        assert "user" in user.roles, "Condition must be true"

    def test_create_user_generates_unique_id(self, user_store):
        """Test that each user gets unique ID."""
        user1 = user_store.create_user("user1", "user1@example.com", "Pass123!")
        user2 = user_store.create_user("user2", "user2@example.com", "Pass123!")
        assert user1.user_id != user2.user_id, "user_id is not valid"

    def test_create_duplicate_username_raises_error(self, user_store):
        """Test that duplicate username raises error."""
        user_store.create_user("alice", "alice@example.com", "Pass123!")

        # Assert a specific exception is raised instead of the generic Exception class
        with pytest.raises(ValueError):
            user_store.create_user("alice", "alice2@example.com", "Pass123!")

    def test_create_user_password_hashing(self, user_store):
        """Test that password is hashed, not stored plaintext."""
        password = "PlainTextPassword123!"
        user = user_store.create_user("charlie", "charlie@example.com", password)

        # Password hash should not be the plaintext
        assert user.password_hash != password, "password_hash is not valid"


# ============================================================================
# User Retrieval Tests
# ============================================================================


class TestUserRetrieval:
    """Test user retrieval functionality."""

    def test_get_user_by_username(self, user_store):
        """Test retrieving user by username."""
        created = user_store.create_user("dave", "dave@example.com", "Pass123!")
        retrieved = user_store.get_user_by_username("dave")

        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.username == "dave", "username is not valid"
        assert retrieved.user_id == created.user_id, "user_id is not valid"

    def test_get_user_by_email(self, user_store):
        """Test retrieving user by email."""
        user_store.create_user("eve", "eve@example.com", "Pass123!")
        retrieved = user_store.get_user_by_email("eve@example.com")

        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.email == "eve@example.com", "email is not valid"

    def test_get_user_by_id(self, user_store):
        """Test retrieving user by ID."""
        created = user_store.create_user("frank", "frank@example.com", "Pass123!")
        retrieved = user_store.get_user_by_id(created.user_id)

        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.user_id == created.user_id, "user_id is not valid"

    def test_get_nonexistent_user_returns_none(self, user_store):
        """Test that nonexistent user returns None."""
        assert user_store.get_user_by_username("nonexistent") is None, "user_st is not valid"
        assert user_store.get_user_by_email("nonexistent@example.com") is None, "user_st is not valid"

    def test_get_all_users(self, user_store):
        """Test retrieving all users."""
        user_store.create_user("user1", "user1@example.com", "Pass123!")
        user_store.create_user("user2", "user2@example.com", "Pass123!")

        users = user_store.get_all_users()
        assert len(users) >= 2, "Users must not be empty"

    def test_get_users_by_role(self, user_store):
        """Test retrieving users by role."""
        user_store.create_user("admin1", "admin1@example.com", "Pass123!", roles=["admin"])
        user_store.create_user("user1", "user1@example.com", "Pass123!", roles=["user"])

        admins = user_store.get_users_by_role("admin")
        assert any(u.username == "admin1" for u in admins), "username is not valid"


# ============================================================================
# Password Verification Tests
# ============================================================================


class TestPasswordVerification:
    """Test password verification functionality."""

    def test_verify_correct_password(self, user_store):
        """Test verifying correct password."""
        password = "CorrectPassword123!"
        user_store.create_user("alice", "alice@example.com", password)

        # Verify with authenticate method
        verified_user = user_store.authenticate("alice", password)
        assert verified_user is not None, "verified_user must be initialized"
        assert verified_user.username == "alice", "Username must match"

    def test_verify_incorrect_password(self, user_store):
        """Test that incorrect password fails verification."""
        user_store.create_user("bob", "bob@example.com", "CorrectPass123!")

        # Try to authenticate with wrong password
        with pytest.raises(InvalidCredentialsError):
            user_store.authenticate("bob", "WrongPassword123!")

    def test_verify_null_password_fails(self, user_store):
        """Test that None password fails verification."""
        user_store.create_user("charlie", "charlie@example.com", "Pass123!")

        with pytest.raises((ValueError, TypeError, InvalidCredentialsError)):
            user_store.authenticate("charlie", None)

    def test_password_case_sensitivity(self, user_store):
        """Test that passwords are case-sensitive."""
        password = "SecurePass123!"
        user_store.create_user("dave", "dave@example.com", password)

        # Wrong case should fail
        with pytest.raises(InvalidCredentialsError):
            user_store.authenticate("dave", "securepass123!")


# ============================================================================
# User Update Tests
# ============================================================================


class TestUserUpdates:
    """Test user update functionality."""

    def test_update_user_email(self, user_store):
        """Test updating user email."""
        user = user_store.create_user("eve", "eve@example.com", "Pass123!")
        user.email = "eve_new@example.com"
        updated = user_store.update_user(user)

        assert updated.email == "eve_new@example.com", "email is not valid"

    def test_update_user_roles(self, user_store):
        """Test updating user roles."""
        user = user_store.create_user("frank", "frank@example.com", "Pass123!")
        user.roles = ["admin", "moderator"]
        updated = user_store.update_user(user)

        assert "admin" in updated.roles, "Condition must be true"

    def test_update_user_metadata(self, user_store):
        """Test updating user metadata."""
        user = user_store.create_user("grace", "grace@example.com", "Pass123!")
        user.metadata = {"department": "sales"}
        updated = user_store.update_user(user)

        assert updated.metadata.get("department") == "sales", "Data must not be empty"

    def test_update_nonexistent_user_raises_error(self, user_store):
        """Test updating nonexistent user raises error."""
        fake_user = User(
            user_id="fake_id",
            username="nonexistent",
            email="fake@example.com",
            password_hash="fake_hash",
        )

        with pytest.raises(Exception):
            user_store.update_user(fake_user)


# ============================================================================
# User Deletion Tests
# ============================================================================


class TestUserDeletion:
    """Test user deletion functionality."""

    def test_delete_user(self, user_store):
        """Test deleting a user."""
        user = user_store.create_user("henry", "henry@example.com", "Pass123!")
        user_store.delete_user(user.user_id)

        assert user_store.get_user_by_id(user.user_id) is None, "user_st is not valid"

    def test_delete_nonexistent_user_raises_error(self, user_store):
        """Test deleting nonexistent user raises error."""
        with pytest.raises(Exception):
            user_store.delete_user("nonexistent_id")

    def test_delete_user_by_username(self, user_store):
        """Test deleting user by username."""
        user_store.create_user("iris", "iris@example.com", "Pass123!")
        user_store.delete_user_by_username("iris")

        assert user_store.get_user_by_username("iris") is None, "user_st is not valid"


# ============================================================================
# Password Hashing Tests
# ============================================================================


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_creates_different_hash(self):
        """Test that password is hashed."""
        hasher = PasswordHasher()
        password = "TestPassword123!"
        hash1 = hasher.hash_password(password)

        assert hash1 != password, "hash1 is not valid"
        assert len(hash1) > len(password), "Hash1 must not be empty"

    def test_same_password_different_salts(self):
        """Test that same password with different salts produces different hashes."""
        hasher = PasswordHasher()
        password = "TestPassword123!"
        hash1 = hasher.hash_password(password)
        hash2 = hasher.hash_password(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2, "hash1 is not valid"

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        hasher = PasswordHasher()
        password = "TestPassword123!"
        hashed = hasher.hash_password(password)

        assert hasher.verify(password, hashed)

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        hasher = PasswordHasher()
        password = "TestPassword123!"
        hashed = hasher.hash_password(password)

        assert not hasher.verify("WrongPassword123!", hashed)

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        hasher = PasswordHasher()
        password = "TestPassword123!"
        hashed = hasher.hash_password(password)

        assert not hasher.verify("testpassword123!", hashed)


# ============================================================================
# Thread Safety Tests
# ============================================================================


class TestThreadSafety:
    """Test thread-safety of user store."""

    def test_concurrent_user_creation(self, user_store):
        """Test concurrent user creation."""
        import threading

        users_created = []

        def create_user(username):
            user = user_store.create_user(
                username,
                f"{username}@example.com",
                "Pass123!",
            )
            users_created.append(user)

        threads = []
        for i in range(5):
            t = threading.Thread(target=create_user, args=(f"thread_user_{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(users_created) == 5, "Users_created must not be empty"

    def test_concurrent_user_retrieval(self, user_store):
        """Test concurrent user retrieval."""
        import threading

        # Create some users
        for i in range(5):
            user_store.create_user(f"user_{i}", f"user_{i}@example.com", "Pass123!")

        results = []

        def get_user(username):
            user = user_store.get_user_by_username(username)
            results.append(user)

        threads = []
        for i in range(5):
            t = threading.Thread(target=get_user, args=(f"user_{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(results) == 5, "Results must not be empty"
        assert all(u is not None for u in results), "u must be initialized"


# ============================================================================
# Edge Cases Tests
# ============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_username_with_special_characters(self, user_store):
        """Test username with special characters."""
        user = user_store.create_user("user@domain.com", "user@example.com", "Pass123!")
        assert user.username == "user@domain.com", "username is not valid"

    def test_very_long_username(self, user_store):
        """Test very long username."""
        long_username = "a" * 255
        user = user_store.create_user(long_username, "test@example.com", "Pass123!")
        assert len(user.username) == 255, "Collection must not be empty"

    def test_email_with_plus_sign(self, user_store):
        """Test email with plus sign."""
        user = user_store.create_user("john", "john+tag@example.com", "Pass123!")
        assert user.email == "john+tag@example.com", "email is not valid"

    def test_very_strong_password(self, user_store):
        """Test very long/complex password."""
        long_password = "Xa" + "X" * 998 + "1!@#$%^&*()"
        user = user_store.create_user("jane", "jane@example.com", long_password)
        assert user.user_id is not None, "user_id must be initialized"

    def test_empty_roles_list(self, user_store):
        """Test creating user with empty roles list."""
        user = user_store.create_user(
            "kay",
            "kay@example.com",
            "Pass123!",
            roles=[],
        )
        # Should have default role
        assert len(user.roles) > 0, "Collection must not be empty"

    def test_user_with_many_roles(self, user_store):
        """Test user with many roles."""
        many_roles = [f"role_{i}" for i in range(100)]
        user = user_store.create_user(
            "liam",
            "liam@example.com",
            "Pass123!",
            roles=many_roles,
        )
        assert len(user.roles) >= 100, "Collection must not be empty"


# ============================================================================
# Integration Tests
# ============================================================================


class TestUserStoreIntegration:
    """Integration tests for user store."""

    def test_complete_user_lifecycle(self, user_store):
        """Test complete user lifecycle."""
        # Create user
        user = user_store.create_user("mia", "mia@example.com", "Pass123!")
        assert user is not None, "user must be initialized"

        # Retrieve user
        retrieved = user_store.get_user_by_username("mia")
        assert retrieved is not None, "retrieved must be initialized"

        # Update user
        retrieved.email = "mia_new@example.com"
        updated = user_store.update_user(retrieved)
        assert updated.email == "mia_new@example.com", "email is not valid"

        # Delete user
        user_store.delete_user(user.user_id)
        assert user_store.get_user_by_id(user.user_id) is None, "user_st is not valid"

    def test_multiple_users_management(self, user_store):
        """Test managing multiple users."""
        users = []
        for i in range(10):
            user = user_store.create_user(
                f"user_{i}",
                f"user_{i}@example.com",
                "Pass123!",
            )
            users.append(user)

        # Verify all created
        all_users = user_store.get_all_users()
        assert len(all_users) >= 10, "All_users must not be empty"

        # Update some
        for user in users[:5]:
            user.roles.append("premium")
            user_store.update_user(user)

        # Delete some
        for user in users[5:]:
            user_store.delete_user(user.user_id)

    def test_user_search_operations(self, user_store):
        """Test various user search operations."""
        # Create diverse users
        user_store.create_user("admin1", "admin1@example.com", "Pass123!", roles=["admin"])
        user_store.create_user("mod1", "mod1@example.com", "Pass123!", roles=["moderator"])
        user_store.create_user("user1", "user1@example.com", "Pass123!", roles=["user"])

        # Search operations
        all_users = user_store.get_all_users()
        assert len(all_users) >= 3, "All_users must not be empty"

        admins = user_store.get_users_by_role("admin")
        assert any(u.username == "admin1" for u in admins), "username is not valid"
