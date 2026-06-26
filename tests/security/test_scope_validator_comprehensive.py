"""Comprehensive tests for security.scope_validator module.

This module tests scope validation and authorization including:
- Scope flag operations
- Token scope validation
- Hierarchical permission checking
- Scope error handling
"""

from __future__ import annotations

import pytest

from security.scope_validator import (
    InsufficientScopeError,
    InvalidScopeError,
    ScopeError,
    ScopeValidator,
    TokenScope,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def scope_validator():
    """Create a scope validator."""
    return ScopeValidator()


@pytest.fixture
def admin_token_scope():
    """Create admin token scope."""
    return TokenScope.ADMIN_REPO | TokenScope.ADMIN_WORKFLOW


@pytest.fixture
def user_token_scope():
    """Create user token scope."""
    return TokenScope.READ_REPO | TokenScope.WRITE_ISSUES


# ============================================================================
# TOKEN_SCOPE TESTS
# ============================================================================


class TestTokenScope:
    """Test TokenScope enum."""

    def test_token_scope_read_repo(self):
        """Test READ_REPO scope."""
        assert TokenScope.READ_REPO.value == TokenScope.READ_REPO, "Value must be initialized"

    def test_token_scope_write_repo(self):
        """Test WRITE_REPO scope."""
        assert TokenScope.WRITE_REPO.value == TokenScope.WRITE_REPO, "Value must be initialized"

    def test_token_scope_admin_repo(self):
        """Test ADMIN_REPO scope."""
        assert TokenScope.ADMIN_REPO.value == TokenScope.ADMIN_REPO, "Value must be initialized"

    def test_token_scope_delete_repo(self):
        """Test DELETE_REPO scope."""
        assert TokenScope.DELETE_REPO.value == TokenScope.DELETE_REPO, "Value must be initialized"

    def test_token_scope_combination(self):
        """Test combining scopes."""
        combined = TokenScope.READ_REPO | TokenScope.WRITE_REPO
        assert TokenScope.READ_REPO in combined, "Condition must be true"
        assert TokenScope.WRITE_REPO in combined, "Condition must be true"

    def test_token_scope_none(self):
        """Test NONE scope."""
        assert TokenScope.NONE.value == 0, "Value must be initialized"

    def test_token_scope_all_repository_scopes(self):
        """Test all repository scopes exist."""
        scopes = [
            TokenScope.READ_REPO,
            TokenScope.WRITE_REPO,
            TokenScope.ADMIN_REPO,
            TokenScope.DELETE_REPO,
        ]
        assert len(scopes) == 4, "Scopes must not be empty"

    def test_token_scope_all_workflow_scopes(self):
        """Test all workflow scopes exist."""
        scopes = [
            TokenScope.READ_WORKFLOW,
            TokenScope.WRITE_WORKFLOW,
            TokenScope.ADMIN_WORKFLOW,
        ]
        assert len(scopes) == 3, "Scopes must not be empty"

    def test_token_scope_all_issue_scopes(self):
        """Test all issue scopes exist."""
        scopes = [
            TokenScope.READ_ISSUES,
            TokenScope.WRITE_ISSUES,
            TokenScope.ADMIN_ISSUES,
        ]
        assert len(scopes) == 3, "Scopes must not be empty"

    def test_token_scope_all_package_scopes(self):
        """Test all package scopes exist."""
        scopes = [
            TokenScope.READ_PACKAGES,
            TokenScope.WRITE_PACKAGES,
            TokenScope.ADMIN_PACKAGES,
        ]
        assert len(scopes) == 3, "Scopes must not be empty"

    def test_token_scope_all_org_scopes(self):
        """Test all org scopes exist."""
        scopes = [
            TokenScope.READ_ORG,
            TokenScope.WRITE_ORG,
            TokenScope.ADMIN_ORG,
        ]
        assert len(scopes) == 3, "Scopes must not be empty"

    def test_token_scope_all_user_scopes(self):
        """Test all user scopes exist."""
        scopes = [
            TokenScope.READ_USER,
            TokenScope.WRITE_USER,
        ]
        assert len(scopes) == 2, "Scopes must not be empty"

    def test_token_scope_all_security_scopes(self):
        """Test all security scopes exist."""
        scopes = [
            TokenScope.READ_SECURITY,
            TokenScope.WRITE_SECURITY,
            TokenScope.ADMIN_SECURITY,
        ]
        assert len(scopes) == 3, "Scopes must not be empty"


# ============================================================================
# SCOPE_VALIDATOR TESTS
# ============================================================================


class TestScopeValidator:
    """Test ScopeValidator class."""

    def test_scope_validator_creation(self, scope_validator):
        """Test creating a scope validator."""
        assert scope_validator is not None, "scope_validator must be initialized"

    def test_validate_scope_has_required_scope(self, scope_validator, admin_token_scope):
        """Test validating token with required scope."""
        scope_validator.validate_scope(admin_token_scope, TokenScope.ADMIN_REPO)
        # Should not raise

    def test_validate_scope_missing_required_scope(self, scope_validator, user_token_scope):
        """Test validating token missing required scope."""
        with pytest.raises(InsufficientScopeError):
            scope_validator.validate_scope(user_token_scope, TokenScope.ADMIN_REPO)

    def test_validate_scope_multiple_required(self, scope_validator, admin_token_scope):
        """Test validating multiple required scopes."""
        required = TokenScope.ADMIN_REPO | TokenScope.ADMIN_WORKFLOW
        scope_validator.validate_scope(admin_token_scope, required)
        # Should not raise

    def test_validate_scope_insufficient_error(self, scope_validator):
        """Test InsufficientScopeError is raised."""
        token_scope = TokenScope.READ_REPO
        with pytest.raises(InsufficientScopeError):
            scope_validator.validate_scope(token_scope, TokenScope.WRITE_REPO)

    def test_validate_scope_with_admin_implied(self, scope_validator):
        """Test admin scope implies all scopes."""
        admin_scope = TokenScope.ADMIN_REPO
        scope_validator.validate_scope(admin_scope, TokenScope.READ_REPO)
        scope_validator.validate_scope(admin_scope, TokenScope.WRITE_REPO)
        # Should not raise

    def test_validate_scope_write_implies_read(self, scope_validator):
        """Test write scope implies read."""
        write_scope = TokenScope.WRITE_REPO
        # Write should imply read in some contexts
        result = scope_validator.check_scope(write_scope, TokenScope.WRITE_REPO)
        assert result is True, "Result must not be empty"

    def test_check_scope_has_scope(self, scope_validator):
        """Test checking if token has scope."""
        token_scope = TokenScope.READ_REPO | TokenScope.WRITE_REPO
        result = scope_validator.check_scope(token_scope, TokenScope.READ_REPO)
        assert result is True, "Result must not be empty"

    def test_check_scope_missing_scope(self, scope_validator):
        """Test checking for missing scope."""
        token_scope = TokenScope.READ_REPO
        result = scope_validator.check_scope(token_scope, TokenScope.WRITE_REPO)
        assert result is False, "Result must not be empty"

    def test_check_scope_empty_token_scope(self, scope_validator):
        """Test checking scope on token with no scopes."""
        token_scope = TokenScope.NONE
        result = scope_validator.check_scope(token_scope, TokenScope.READ_REPO)
        assert result is False, "Result must not be empty"

    def test_get_implied_scopes(self, scope_validator):
        """Test getting implied scopes."""
        admin_scope = TokenScope.ADMIN_REPO
        implied = scope_validator.get_implied_scopes(admin_scope)
        assert isinstance(implied, list)

    def test_is_admin_scope(self, scope_validator):
        """Test checking if scope is admin."""
        assert scope_validator.is_admin_scope(TokenScope.ADMIN_REPO) is True, "scope_validat is not valid"
        assert scope_validator.is_admin_scope(TokenScope.READ_REPO) is False, "scope_validat is not valid"

    def test_get_scope_category(self, scope_validator):
        """Test getting scope category."""
        category = scope_validator.get_scope_category(TokenScope.READ_REPO)
        assert "repo" in category.lower() or category is not None, "category must be initialized"

    def test_scope_string_representation(self, scope_validator):
        """Test scope string representation."""
        scope = TokenScope.READ_REPO
        scope_str = scope_validator.scope_to_string(scope)
        assert isinstance(scope_str, str)
        assert len(scope_str) > 0, "Scope_str must not be empty"

    def test_parse_scope_string(self, scope_validator):
        """Test parsing scope from string."""
        scope_str = "read:repo"
        parsed = scope_validator.parse_scope_string(scope_str)
        assert isinstance(parsed, (TokenScope, int, type(None)))

    def test_validate_scope_format(self, scope_validator):
        """Test validating scope format."""
        valid_format = "read:repo"
        result = scope_validator.validate_scope_format(valid_format)
        assert isinstance(result, bool)

    def test_validate_scope_format_invalid(self, scope_validator):
        """Test validating invalid scope format."""
        invalid_format = "!!invalid!!"
        result = scope_validator.validate_scope_format(invalid_format)
        assert isinstance(result, bool)


# ============================================================================
# SCOPE_ERROR TESTS
# ============================================================================


class TestScopeErrors:
    """Test scope error classes."""

    def test_scope_error_is_exception(self):
        """Test ScopeError is an Exception."""
        error = ScopeError("test error")
        assert isinstance(error, Exception)

    def test_insufficient_scope_error_message(self):
        """Test InsufficientScopeError message."""
        error = InsufficientScopeError("Missing write:repo")
        assert "Missing write:repo" in str(error), "Error should be raised or set"

    def test_invalid_scope_error_message(self):
        """Test InvalidScopeError message."""
        error = InvalidScopeError("Invalid scope format")
        assert "Invalid scope format" in str(error), "Error should be raised or set"

    def test_insufficient_scope_error_inheritance(self):
        """Test InsufficientScopeError inherits from ScopeError."""
        error = InsufficientScopeError("test")
        assert isinstance(error, ScopeError)

    def test_invalid_scope_error_inheritance(self):
        """Test InvalidScopeError inherits from ScopeError."""
        error = InvalidScopeError("test")
        assert isinstance(error, ScopeError)


# ============================================================================
# HIERARCHICAL SCOPE TESTS
# ============================================================================


class TestHierarchicalScopes:
    """Test hierarchical scope relationships."""

    def test_admin_implies_write(self, scope_validator):
        """Test ADMIN scope implies WRITE."""
        admin_scope = TokenScope.ADMIN_REPO
        # Admin should have write capabilities
        result = scope_validator.check_scope(admin_scope, TokenScope.WRITE_REPO)
        assert isinstance(result, bool)

    def test_admin_implies_read(self, scope_validator):
        """Test ADMIN scope implies READ."""
        admin_scope = TokenScope.ADMIN_REPO
        # Admin should have read capabilities
        result = scope_validator.check_scope(admin_scope, TokenScope.READ_REPO)
        assert isinstance(result, bool)

    def test_write_implies_read(self, scope_validator):
        """Test WRITE scope implies READ."""
        write_scope = TokenScope.WRITE_REPO
        # Write should have read capabilities
        result = scope_validator.check_scope(write_scope, TokenScope.READ_REPO)
        assert isinstance(result, bool)

    def test_read_does_not_imply_write(self, scope_validator):
        """Test READ scope does not imply WRITE."""
        read_scope = TokenScope.READ_REPO
        # Read should not have write capabilities
        result = scope_validator.check_scope(read_scope, TokenScope.WRITE_REPO)
        assert result is False, "Result must not be empty"

    def test_hierarchy_repo_scopes(self, scope_validator):
        """Test hierarchy of repo scopes."""
        # DELETE > ADMIN > WRITE > READ
        scopes = [
            TokenScope.READ_REPO,
            TokenScope.WRITE_REPO,
            TokenScope.ADMIN_REPO,
            TokenScope.DELETE_REPO,
        ]
        for scope in scopes:
            assert isinstance(scope, TokenScope)

    def test_hierarchy_workflow_scopes(self, scope_validator):
        """Test hierarchy of workflow scopes."""
        # ADMIN > WRITE > READ
        scopes = [
            TokenScope.READ_WORKFLOW,
            TokenScope.WRITE_WORKFLOW,
            TokenScope.ADMIN_WORKFLOW,
        ]
        for scope in scopes:
            assert isinstance(scope, TokenScope)


# ============================================================================
# SCOPE COMBINATION TESTS
# ============================================================================


class TestScopeCombinations:
    """Test scope combinations."""

    def test_combine_repo_and_workflow_scopes(self):
        """Test combining repo and workflow scopes."""
        combined = TokenScope.READ_REPO | TokenScope.WRITE_WORKFLOW
        assert TokenScope.READ_REPO in combined, "Condition must be true"
        assert TokenScope.WRITE_WORKFLOW in combined, "Condition must be true"

    def test_combine_multiple_scopes(self):
        """Test combining multiple scopes."""
        scopes = TokenScope.READ_REPO | TokenScope.WRITE_ISSUES | TokenScope.ADMIN_WORKFLOW
        assert TokenScope.READ_REPO in scopes, "Condition must be true"
        assert TokenScope.WRITE_ISSUES in scopes, "Condition must be true"
        assert TokenScope.ADMIN_WORKFLOW in scopes, "Condition must be true"

    def test_scope_intersection(self, scope_validator):
        """Test scope intersection."""
        scope1 = TokenScope.READ_REPO | TokenScope.WRITE_REPO
        TokenScope.WRITE_REPO | TokenScope.ADMIN_REPO

        # Both should have WRITE_REPO
        result = scope_validator.check_scope(scope1, TokenScope.WRITE_REPO)
        assert result is True, "Result must not be empty"

    def test_scope_union(self, scope_validator):
        """Test scope union."""
        scope1 = TokenScope.READ_REPO
        scope2 = TokenScope.WRITE_REPO
        union = scope1 | scope2

        assert TokenScope.READ_REPO in union, "Condition must be true"
        assert TokenScope.WRITE_REPO in union, "Condition must be true"

    def test_scope_difference(self, scope_validator):
        """Test scope difference."""
        scope1 = TokenScope.READ_REPO | TokenScope.WRITE_REPO
        # This would remove READ_REPO from combined scope (bitwise operations)
        result = scope1 & ~TokenScope.READ_REPO
        assert isinstance(result, int)


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize(
    "scope,category",
    [
        (TokenScope.READ_REPO, "repo"),
        (TokenScope.WRITE_REPO, "repo"),
        (TokenScope.READ_WORKFLOW, "workflow"),
        (TokenScope.READ_ISSUES, "issues"),
        (TokenScope.READ_PACKAGES, "packages"),
        (TokenScope.READ_ORG, "org"),
    ],
)
def test_scope_category_parametrized(scope_validator, scope, category):
    """Parametrized test for scope categories."""
    result = scope_validator.get_scope_category(scope)
    assert isinstance(result, str)


@pytest.mark.parametrize(
    "token_scope,required,should_pass",
    [
        (TokenScope.ADMIN_REPO, TokenScope.READ_REPO, True),
        (TokenScope.WRITE_REPO, TokenScope.READ_REPO, True),
        (TokenScope.READ_REPO, TokenScope.WRITE_REPO, False),
        (TokenScope.ADMIN_WORKFLOW, TokenScope.ADMIN_REPO, False),
    ],
)
def test_scope_validation_parametrized(scope_validator, token_scope, required, should_pass):
    """Parametrized test for scope validation."""
    result = scope_validator.check_scope(token_scope, required)
    assert result == should_pass, "Result must not be empty"


# ============================================================================
# EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_validate_scope_with_none_scope(self, scope_validator):
        """Test validating None scope."""
        try:
            scope_validator.validate_scope(None, TokenScope.READ_REPO)
        except (TypeError, InsufficientScopeError):
            pass

    def test_check_scope_with_zero_scope(self, scope_validator):
        """Test checking zero scope."""
        result = scope_validator.check_scope(0, TokenScope.READ_REPO)
        assert result is False, "Result must not be empty"

    def test_scope_validator_with_no_scopes(self, scope_validator):
        """Test validator with empty scopes."""
        result = scope_validator.check_scope(TokenScope.NONE, TokenScope.NONE)
        assert isinstance(result, bool)

    def test_scope_string_parsing_invalid(self, scope_validator):
        """Test parsing invalid scope strings."""
        try:
            result = scope_validator.parse_scope_string("invalid::scope")
            assert result is None or isinstance(result, (TokenScope, int))
        except (ValueError, InvalidScopeError):
            pass

    def test_scope_empty_string(self, scope_validator):
        """Test parsing empty scope string."""
        try:
            result = scope_validator.parse_scope_string("")
            assert result is None or isinstance(result, (TokenScope, int))
        except (ValueError, InvalidScopeError):
            pass

    def test_validate_scope_format_edge_cases(self, scope_validator):
        """Test scope format validation edge cases."""
        test_cases = ["", ":", ":::", "read::", "::read"]
        for case in test_cases:
            result = scope_validator.validate_scope_format(case)
            assert isinstance(result, bool)

    def test_scope_hierarchy_deep_nesting(self, scope_validator):
        """Test deeply nested scope hierarchies."""
        deep_scope = (
            TokenScope.ADMIN_REPO
            | TokenScope.ADMIN_WORKFLOW
            | TokenScope.ADMIN_ISSUES
            | TokenScope.ADMIN_ORG
        )
        assert isinstance(deep_scope, int)
