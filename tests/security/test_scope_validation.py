"""
Test Scope Validation

Tests for the scope validator library and decorators.
"""

import pytest

from security.scope_validator import (
    InsufficientScopeError,
    InvalidScopeError,
    ScopeValidator,
    TokenScope,
)
from security.decorators import (
    clear_scope_validator,
    optional_scope,
    require_any_scope,
    require_scope,
    scope_metadata,
    set_scope_validator,
)


class TestTokenScopeParsing:
    """Tests for TokenScope parsing."""

    def test_from_string_write_implies_read(self):
        """Test write scope implies read scope."""
        scope = TokenScope.from_string("repo:write")
        assert scope & TokenScope.READ_REPO
        assert scope & TokenScope.WRITE_REPO

    def test_from_string_admin_implies_write_read(self):
        """Test admin scope implies write and read."""
        scope = TokenScope.from_string("repo:admin")
        assert scope & TokenScope.READ_REPO
        assert scope & TokenScope.WRITE_REPO
        assert scope & TokenScope.ADMIN_REPO

    def test_from_string_invalid_scope(self):
        """Test invalid scope string raises error."""
        with pytest.raises(InvalidScopeError):
            TokenScope.from_string("invalid:scope")

    def test_from_list_multiple_scopes(self):
        """Test parsing list of scopes."""
        scopes = TokenScope.from_list(["repo:read", "workflow:write"])
        assert scopes & TokenScope.READ_REPO
        assert scopes & TokenScope.READ_WORKFLOW
        assert scopes & TokenScope.WRITE_WORKFLOW

    def test_has_scope(self):
        """Test scope checking with has()."""
        scope = TokenScope.from_list(["repo:write", "issues:read"])
        assert scope.has(TokenScope.READ_REPO)
        assert scope.has(TokenScope.WRITE_REPO)
        assert scope.has(TokenScope.READ_ISSUES)
        assert not scope.has(TokenScope.WRITE_ISSUES)

    def test_to_strings(self):
        """Test converting scopes back to strings."""
        scope = TokenScope.from_list(["repo:write", "workflow:read"])
        strings = scope.to_strings()
        assert "repo:read" in strings
        assert "repo:write" in strings
        assert "workflow:read" in strings


class TestScopeValidator:
    """Tests for ScopeValidator."""

    def test_init_with_flags(self):
        """Test initializing validator with TokenScope flags."""
        scope_flags = TokenScope.READ_REPO | TokenScope.WRITE_WORKFLOW
        validator = ScopeValidator(scope_flags)
        assert validator.has_scope(TokenScope.READ_REPO)
        assert validator.has_scope(TokenScope.WRITE_WORKFLOW)

    def test_has_scope_success(self):
        """Test has_scope returns True when scope present."""
        validator = ScopeValidator(["repo:write"])
        assert validator.has_scope(TokenScope.READ_REPO) is True
        assert validator.has_scope(TokenScope.WRITE_REPO) is True

    def test_has_scope_failure(self):
        """Test has_scope returns False when scope missing."""
        validator = ScopeValidator(["repo:read"])
        assert validator.has_scope(TokenScope.WRITE_REPO) is False

    def test_has_any_scope_success(self):
        """Test has_any_scope with at least one match."""
        validator = ScopeValidator(["repo:read"])
        assert validator.has_any_scope(
            [
                TokenScope.WRITE_REPO,
                TokenScope.READ_REPO,
            ]
        ) is True

    def test_has_any_scope_failure(self):
        """Test has_any_scope with no matches."""
        validator = ScopeValidator(["repo:read"])
        assert validator.has_any_scope(
            [
                TokenScope.WRITE_WORKFLOW,
                TokenScope.ADMIN_REPO,
            ]
        ) is False

    def test_require_scope_success(self):
        """Test require_scope passes with sufficient scope."""
        validator = ScopeValidator(["repo:write"])
        # Should not raise
        validator.require_scope(TokenScope.READ_REPO)
        validator.require_scope(TokenScope.WRITE_REPO)

    def test_require_scope_failure(self):
        """Test require_scope raises with insufficient scope."""
        validator = ScopeValidator(["repo:read"])
        with pytest.raises(InsufficientScopeError, match="Missing required scope"):
            validator.require_scope(TokenScope.WRITE_REPO)

    def test_require_any_scope_success(self):
        """Test require_any_scope with sufficient scope."""
        validator = ScopeValidator(["repo:read"])
        # Should not raise
        validator.require_any_scope(
            [
                TokenScope.WRITE_REPO,
                TokenScope.READ_REPO,
            ]
        )

    def test_require_any_scope_failure(self):
        """Test require_any_scope raises with insufficient scope."""
        validator = ScopeValidator(["repo:read"])
        with pytest.raises(InsufficientScopeError):
            validator.require_any_scope(
                [
                    TokenScope.WRITE_WORKFLOW,
                    TokenScope.ADMIN_REPO,
                ]
            )

    def test_validate_success(self):
        """Test validate returns success result."""
        validator = ScopeValidator(["repo:write"])
        result = validator.validate(TokenScope.READ_REPO)
        assert result.valid is True
        assert result.granted_scopes == validator.scopes
        assert result.required_scopes == TokenScope.READ_REPO
        assert result.missing_scopes is None

    def test_validate_failure(self):
        """Test validate returns failure result with details."""
        validator = ScopeValidator(["repo:read"])
        result = validator.validate(TokenScope.WRITE_REPO)
        assert result.valid is False
        assert result.missing_scopes is not None
        assert "Missing scopes" in result.message

    def test_get_granted_scopes(self):
        """Test getting granted scopes as strings."""
        validator = ScopeValidator(["repo:write", "workflow:read"])
        scopes = validator.get_granted_scopes()
        assert "repo:read" in scopes
        assert "repo:write" in scopes
        assert "workflow:read" in scopes


class TestScopeDecorators:
    """Tests for scope decorator functions."""

    def setup_method(self):
        """Clear scope validator before each test."""
        clear_scope_validator()

    def teardown_method(self):
        """Clear scope validator after each test."""
        clear_scope_validator()

    def test_require_scope_success(self):
        """Test require_scope decorator allows execution."""
        validator = ScopeValidator(["repo:write"])
        set_scope_validator(validator)

        @require_scope("repo:read")
        def protected_function():
            return "success"

        result = protected_function()
        assert result == "success"

    def test_require_scope_failure(self):
        """Test require_scope decorator blocks execution."""
        validator = ScopeValidator(["repo:read"])
        set_scope_validator(validator)

        @require_scope("repo:write")
        def protected_function():
            return "success"

        with pytest.raises(InsufficientScopeError):
            protected_function()

    def test_require_scope_no_validator(self):
        """Test require_scope raises without validator in context."""

        @require_scope("repo:read")
        def protected_function():
            return "success"

        with pytest.raises(RuntimeError, match="No scope validator found"):
            protected_function()

    def test_require_any_scope_success(self):
        """Test require_any_scope decorator with sufficient scope."""
        validator = ScopeValidator(["repo:read"])
        set_scope_validator(validator)

        @require_any_scope("repo:read", "repo:write")
        def protected_function():
            return "success"

        result = protected_function()
        assert result == "success"

    def test_require_any_scope_failure(self):
        """Test require_any_scope decorator blocks execution."""
        validator = ScopeValidator(["workflow:read"])
        set_scope_validator(validator)

        @require_any_scope("repo:read", "repo:write")
        def protected_function():
            return "success"

        with pytest.raises(InsufficientScopeError):
            protected_function()

    def test_optional_scope_with_validator(self):
        """Test optional_scope decorator with validator present."""
        validator = ScopeValidator(["repo:read"])
        set_scope_validator(validator)

        @optional_scope("repo:read")
        def optional_function():
            return "success"

        result = optional_function()
        assert result == "success"

    def test_optional_scope_without_validator(self):
        """Test optional_scope decorator without validator."""

        @optional_scope("repo:read")
        def optional_function():
            return "success"

        # Should not raise
        result = optional_function()
        assert result == "success"

    def test_decorator_metadata(self):
        """Test scope metadata extraction from decorated functions."""

        @require_scope("repo:write", "workflow:read")
        def protected_function():
            pass

        metadata = scope_metadata(protected_function)
        assert metadata["protected"] is True
        assert "repo:write" in metadata["required"]
        assert "workflow:read" in metadata["required"]
        assert metadata["any"] is False

    def test_decorator_preserves_function_name(self):
        """Test decorators preserve function metadata."""

        @require_scope("repo:read")
        def my_function():
            """My docstring."""

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."


class TestHierarchicalScopes:
    """Tests for hierarchical scope behavior."""

    def test_write_implies_read(self):
        """Test write scope automatically grants read."""
        validator = ScopeValidator(["repo:write"])

        # Write implies read
        validator.require_scope(TokenScope.READ_REPO)
        validator.require_scope(TokenScope.WRITE_REPO)

    def test_admin_implies_write_and_read(self):
        """Test admin scope automatically grants write and read."""
        validator = ScopeValidator(["repo:admin"])

        # Admin implies write and read
        validator.require_scope(TokenScope.READ_REPO)
        validator.require_scope(TokenScope.WRITE_REPO)
        validator.require_scope(TokenScope.ADMIN_REPO)

    def test_delete_implies_admin_write_read(self):
        """Test delete scope implies full hierarchy."""
        validator = ScopeValidator(["repo:delete"])

        # Delete implies entire hierarchy
        validator.require_scope(TokenScope.READ_REPO)
        validator.require_scope(TokenScope.WRITE_REPO)
        validator.require_scope(TokenScope.ADMIN_REPO)
        validator.require_scope(TokenScope.DELETE_REPO)

    def test_read_does_not_imply_write(self):
        """Test read scope does not grant write."""
        validator = ScopeValidator(["repo:read"])

        with pytest.raises(InsufficientScopeError):
            validator.require_scope(TokenScope.WRITE_REPO)
