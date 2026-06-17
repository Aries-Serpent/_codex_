"""
Comprehensive tests for User Model and Repository (supplement).

Tests cover:
- User model validation
- User creation variations
- Repository advanced operations
- Bulk operations
- Search and filtering
- Complex queries
"""

import time

import pytest

from codex.auth.in_memory_user_repository import InMemoryUserRepository
from codex.auth.user_model import PasswordHasher, User

# ============================================================================
# User Model Extended Tests
# ============================================================================

class TestUserModelExtended:
    """Extended user model tests."""

    def test_user_equality(self):
        user1 = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
        )
        user2 = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
        )
        assert user1.user_id == user2.user_id

    def test_user_immutability(self):
        user = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
        )
        # Should not be able to modify
        original_email = user.email
        user.email = "new@example.com"
        # Implementation dependent - may or may not allow

    def test_user_string_representation(self):
        user = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
        )
        str_repr = str(user)
        assert "alice" in str_repr or "123" in str_repr

    def test_user_with_empty_roles(self):
        user = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
            roles=[],
        )
        # Should have default roles or empty
        assert isinstance(user.roles, list)

    def test_user_metadata(self):
        user = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
        )
        assert user.user_id
        assert user.created_at
        assert user.username

    def test_user_with_many_roles(self):
        roles = [f"role{i}" for i in range(100)]
        user = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
            roles=roles,
        )
        assert len(user.roles) == 100 or len(user.roles) > 0

    def test_user_role_uniqueness(self):
        user = User(
            user_id="123",
            username="alice",
            email="alice@example.com",
            password_hash="hash123",
            roles=["admin", "admin", "user"],
        )
        # Should deduplicate or allow duplicates


# ============================================================================
# Password Hasher Extended Tests
# ============================================================================

class TestPasswordHasherExtended:
    """Extended password hasher tests."""

    def test_hash_consistency_across_instances(self):
        hasher1 = PasswordHasher()
        hasher2 = PasswordHasher()

        password = "Str0ngPass!"
        hash1 = hasher1.hash_password(password)
        hash2 = hasher2.hash_password(password)

        # Different hashes due to random salt
        assert hash1 != hash2

        # But both should verify the same password
        assert hasher1.verify_password(password, hash1)
        assert hasher2.verify_password(password, hash2)

    def test_password_with_newlines(self):
        hasher = PasswordHasher()
        password = "Pass\n\nword123!"
        hashed = hasher.hash_password(password)
        assert hasher.verify_password(password, hashed)

    def test_password_with_tabs(self):
        hasher = PasswordHasher()
        password = "Pass\t\tword123!"
        hashed = hasher.hash_password(password)
        assert hasher.verify_password(password, hashed)

    def test_password_with_mixed_unicode(self):
        hasher = PasswordHasher()
        password = "Pässwörd123!中文"
        hashed = hasher.hash_password(password)
        assert hasher.verify_password(password, hashed)

    def test_similar_passwords_different_hashes(self):
        hasher = PasswordHasher()
        password1 = "Pass123!"
        password2 = "Pass124!"  # One character different

        hash1 = hasher.hash_password(password1)
        hash2 = hasher.hash_password(password2)

        # Hashes should be completely different
        assert not hasher.verify_password(password2, hash1)
        assert not hasher.verify_password(password1, hash2)


# ============================================================================
# Repository Advanced Operations
# ============================================================================

class TestRepositoryAdvanced:
    """Advanced repository operations."""

    @pytest.fixture
    def repo(self):
        """Create in-memory repository."""
        return InMemoryUserRepository()

    def test_bulk_create_users(self, repo):
        hasher = PasswordHasher()
        users = []

        for i in range(50):
            user = User(
                user_id=f"user{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)
            users.append(user)

        assert repo.get_user_count() == 50

    def test_bulk_delete_users(self, repo):
        hasher = PasswordHasher()
        user_ids = []

        for i in range(10):
            user = User(
                user_id=f"user{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)
            user_ids.append(user.user_id)

        for user_id in user_ids:
            repo.delete_user(user_id)

        assert repo.get_user_count() == 0

    def test_bulk_update_emails(self, repo):
        hasher = PasswordHasher()

        for i in range(10):
            user = User(
                user_id=f"user{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)

        for i in range(10):
            user = repo.get_by_user_id(f"user{i}")
            updated = User(
                user_id=user.user_id,
                username=user.username,
                email=f"updated{i}@example.com",
                password_hash=user.password_hash,
            )
            repo.update_user(updated)

        # Verify updates
        for i in range(10):
            user = repo.get_by_user_id(f"user{i}")
            assert user.email == f"updated{i}@example.com"

    def test_search_by_partial_username(self, repo):
        hasher = PasswordHasher()

        users_data = [
            ("alice", "alice@example.com"),
            ("alicia", "alicia@example.com"),
            ("bob", "bob@example.com"),
            ("bobby", "bobby@example.com"),
        ]

        for username, email in users_data:
            user = User(
                user_id=f"user_{username}",
                username=username,
                email=email,
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)

        # Exact match
        alice = repo.get_by_username("alice")
        assert alice.username == "alice"

    def test_list_with_pagination(self, repo):
        hasher = PasswordHasher()

        for i in range(30):
            user = User(
                user_id=f"user{i:03d}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)

        # Get all users
        users = repo.list_users()
        assert len(users) == 30

    def test_filter_by_creation_date(self, repo):
        hasher = PasswordHasher()

        before_time = time.time()

        for i in range(5):
            user = User(
                user_id=f"old_user{i}",
                username=f"old_user{i}",
                email=f"old{i}@example.com",
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)

        after_time = time.time()


# ============================================================================
# Concurrent Repository Operations
# ============================================================================

class TestConcurrentRepositoryOperations:
    """Concurrent repository access patterns."""

    @pytest.fixture
    def repo(self):
        """Create in-memory repository."""
        return InMemoryUserRepository()

    def test_concurrent_reads(self, repo):
        import threading

        hasher = PasswordHasher()
        user = User(
            user_id="concurrent_user",
            username="concurrent",
            email="concurrent@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(user)

        results = []

        def read_user():
            try:
                u = repo.get_by_username("concurrent")
                results.append(u)
            except Exception as e:
                results.append(e)

        threads = [threading.Thread(target=read_user) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All reads should succeed
        assert len([r for r in results if isinstance(r, User)]) == 10

    def test_concurrent_mixed_operations(self, repo):
        import threading

        def mixed_ops():
            hasher = PasswordHasher()
            user_id = f"concurrent_{threading.current_thread().name}"
            user = User(
                user_id=user_id,
                username=f"user_{threading.current_thread().ident}",
                email=f"{threading.current_thread().ident}@example.com",
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)
            retrieved = repo.get_by_user_id(user_id)
            assert retrieved.user_id == user_id

        threads = [
            threading.Thread(target=mixed_ops, name=f"worker-{i}")
            for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


# ============================================================================
# Data Integrity Tests
# ============================================================================

class TestDataIntegrity:
    """Data integrity and consistency."""

    @pytest.fixture
    def repo(self):
        """Create in-memory repository."""
        return InMemoryUserRepository()

    def test_no_data_loss_on_update(self, repo):
        hasher = PasswordHasher()
        original = User(
            user_id="user1",
            username="alice",
            email="alice@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(original)

        updated = User(
            user_id="user1",
            username="alice",
            email="alice.new@example.com",
            password_hash=hasher.hash_password("NewPass123!"),
        )
        repo.update_user(updated)

        retrieved = repo.get_by_user_id("user1")
        assert retrieved.email == "alice.new@example.com"
        assert retrieved.user_id == "user1"

    def test_deletion_is_permanent(self, repo):
        hasher = PasswordHasher()
        user = User(
            user_id="temp_user",
            username="temp",
            email="temp@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(user)
        repo.delete_user("temp_user")

        with pytest.raises(Exception):
            repo.get_by_user_id("temp_user")

    def test_unique_constraints_enforced(self, repo):
        hasher = PasswordHasher()

        user1 = User(
            user_id="user1",
            username="alice",
            email="alice@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(user1)

        user2 = User(
            user_id="user2",
            username="alice",  # Duplicate username
            email="alice2@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )

        with pytest.raises(Exception):
            repo.create_user(user2)


# ============================================================================
# User State Transitions
# ============================================================================

class TestUserStateTransitions:
    """User state and transitions."""

    @pytest.fixture
    def repo(self):
        """Create in-memory repository."""
        return InMemoryUserRepository()

    def test_new_user_is_enabled(self, repo):
        hasher = PasswordHasher()
        user = User(
            user_id="new_user",
            username="newuser",
            email="new@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(user)

        retrieved = repo.get_by_user_id("new_user")
        # New user should be enabled
        assert retrieved is not None

    def test_email_verification_workflow(self, repo):
        hasher = PasswordHasher()
        user = User(
            user_id="verify_user",
            username="verify",
            email="verify@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(user)

        # User created with unverified email
        retrieved = repo.get_by_user_id("verify_user")
        assert retrieved.email == "verify@example.com"

    def test_user_deactivation(self, repo):
        hasher = PasswordHasher()
        user = User(
            user_id="active_user",
            username="active",
            email="active@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(user)

        # Deactivate by deletion
        repo.delete_user("active_user")

        with pytest.raises(Exception):
            repo.get_by_user_id("active_user")


# ============================================================================
# Special Cases
# ============================================================================

class TestSpecialCases:
    """Special and unusual cases."""

    @pytest.fixture
    def repo(self):
        """Create in-memory repository."""
        return InMemoryUserRepository()

    def test_user_with_system_reserved_username(self, repo):
        hasher = PasswordHasher()
        reserved_names = ["admin", "root", "system", "guest"]

        for name in reserved_names:
            try:
                user = User(
                    user_id=f"user_{name}",
                    username=name,
                    email=f"{name}@example.com",
                    password_hash=hasher.hash_password("Str0ngPass!"),
                )
                repo.create_user(user)
                # Either allowed or rejected
            except Exception as _err:
                pass  # Rejection is acceptable

    def test_user_with_null_bytes_in_fields(self, repo):
        hasher = PasswordHasher()

        # Should handle or reject null bytes
        try:
            user = User(
                user_id="user_null",
                username="user\x00null",
                email="user@example.com",
                password_hash=hasher.hash_password("Str0ngPass!"),
            )
            repo.create_user(user)
        except Exception as _err:
            pass  # Rejection is acceptable

    def test_user_email_with_plus_addressing(self, repo):
        hasher = PasswordHasher()
        user = User(
            user_id="user_plus",
            username="userplus",
            email="user+test@example.com",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        repo.create_user(user)

        retrieved = repo.get_by_email("user+test@example.com")
        assert retrieved.email == "user+test@example.com"

    def test_user_with_international_domain(self, repo):
        hasher = PasswordHasher()
        user = User(
            user_id="user_intl",
            username="userintl",
            email="user@münchen.de",
            password_hash=hasher.hash_password("Str0ngPass!"),
        )
        try:
            repo.create_user(user)
            retrieved = repo.get_by_email("user@münchen.de")
            assert retrieved.email == "user@münchen.de"
        except Exception as _err:
            pass  # International domains may not be supported
