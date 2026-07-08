"""Tests for security.decorators and security.scope_validator.

Covers:
- TokenScope flag operations and from_string/from_list/to_strings
- ScopeValidator has_scope, has_any_scope, require_scope, require_any_scope, validate
- Context variable helpers: set/get/clear_scope_validator
- require_scope decorator: pass, fail, no-validator RuntimeError
- require_any_scope decorator: pass, fail, no-validator RuntimeError
- optional_scope decorator: pass-through with/without validator
- scope_metadata introspection helper
"""

from __future__ import annotations

import pytest

from security.decorators import (
    clear_scope_validator,
    get_scope_validator,
    optional_scope,
    require_any_scope,
    require_scope,
    scope_metadata,
    set_scope_validator,
)
from security.scope_validator import (
    InsufficientScopeError,
    InvalidScopeError,
    ScopeValidationResult,
    ScopeValidator,
    TokenScope,
)

# ---------------------------------------------------------------------------
# TokenScope — from_string
# ---------------------------------------------------------------------------


class TestTokenScopeFromString:
    def test_repo_shorthand(self) -> None:
        s = TokenScope.from_string("repo")
        assert s & TokenScope.READ_REPO, "Condition must be true"
        assert s & TokenScope.WRITE_REPO, "Condition must be true"

    def test_repo_read(self) -> None:
        s = TokenScope.from_string("repo:read")
        assert s & TokenScope.READ_REPO, "Condition must be true"
        assert not (s & TokenScope.WRITE_REPO), "Condition must be true"

    def test_repo_write_implies_read(self) -> None:
        s = TokenScope.from_string("repo:write")
        assert s & TokenScope.WRITE_REPO, "Condition must be true"
        assert s & TokenScope.READ_REPO, "Condition must be true"

    def test_repo_admin_implies_write_and_read(self) -> None:
        s = TokenScope.from_string("repo:admin")
        assert s & TokenScope.ADMIN_REPO, "Condition must be true"
        assert s & TokenScope.WRITE_REPO, "Condition must be true"
        assert s & TokenScope.READ_REPO, "Condition must be true"

    def test_workflow_read(self) -> None:
        s = TokenScope.from_string("workflow:read")
        assert s & TokenScope.READ_WORKFLOW, "Condition must be true"

    def test_issues_write(self) -> None:
        s = TokenScope.from_string("issues:write")
        assert s & TokenScope.WRITE_ISSUES, "Condition must be true"
        assert s & TokenScope.READ_ISSUES, "Condition must be true"

    def test_security_admin(self) -> None:
        s = TokenScope.from_string("security:admin")
        assert s & TokenScope.ADMIN_SECURITY, "Condition must be true"
        assert s & TokenScope.WRITE_SECURITY, "Condition must be true"
        assert s & TokenScope.READ_SECURITY, "Condition must be true"

    def test_user_write(self) -> None:
        s = TokenScope.from_string("user:write")
        assert s & TokenScope.WRITE_USER, "Condition must be true"
        assert s & TokenScope.READ_USER, "Condition must be true"

    def test_org_shorthand(self) -> None:
        s = TokenScope.from_string("org")
        assert s & TokenScope.READ_ORG, "Condition must be true"
        assert s & TokenScope.WRITE_ORG, "Condition must be true"

    def test_invalid_scope_raises(self) -> None:
        with pytest.raises(InvalidScopeError, match="Unknown scope"):
            TokenScope.from_string("nonexistent:scope")

    def test_whitespace_stripped(self) -> None:
        s = TokenScope.from_string("  repo:read  ")
        assert s & TokenScope.READ_REPO, "Condition must be true"

    def test_case_insensitive(self) -> None:
        s = TokenScope.from_string("REPO:READ")
        assert s & TokenScope.READ_REPO, "Condition must be true"


# ---------------------------------------------------------------------------
# TokenScope — from_list
# ---------------------------------------------------------------------------


class TestTokenScopeFromList:
    def test_empty_list_returns_none(self) -> None:
        s = TokenScope.from_list([])
        assert s == TokenScope.NONE, "s is not valid"

    def test_single_scope(self) -> None:
        s = TokenScope.from_list(["repo:read"])
        assert s & TokenScope.READ_REPO, "Condition must be true"

    def test_multiple_scopes_combined(self) -> None:
        s = TokenScope.from_list(["repo:read", "workflow:write"])
        assert s & TokenScope.READ_REPO, "Condition must be true"
        assert s & TokenScope.WRITE_WORKFLOW, "Condition must be true"
        assert s & TokenScope.READ_WORKFLOW, "Condition must be true"

    def test_invalid_in_list_raises(self) -> None:
        with pytest.raises(InvalidScopeError):
            TokenScope.from_list(["repo:read", "bogus"])


# ---------------------------------------------------------------------------
# TokenScope — to_strings / has
# ---------------------------------------------------------------------------


class TestTokenScopeToStrings:
    def test_read_repo_roundtrip(self) -> None:
        s = TokenScope.READ_REPO
        strings = s.to_strings()
        assert "repo:read" in strings, "Condition must be true"

    def test_none_scope_empty(self) -> None:
        assert TokenScope.NONE.to_strings() == set(), "Condition must be true"

    def test_has_all_required(self) -> None:
        s = TokenScope.READ_REPO | TokenScope.WRITE_REPO
        assert s.has(TokenScope.READ_REPO), "Condition must be true"
        assert s.has(TokenScope.WRITE_REPO), "Condition must be true"

    def test_has_missing_flag_false(self) -> None:
        s = TokenScope.READ_REPO
        assert not s.has(TokenScope.WRITE_REPO), "Condition must be true"


# ---------------------------------------------------------------------------
# ScopeValidator
# ---------------------------------------------------------------------------


class TestScopeValidator:
    def test_init_from_list(self) -> None:
        v = ScopeValidator(["repo:write"])
        assert v.has_scope(TokenScope.WRITE_REPO), "Condition must be true"

    def test_init_from_token_scope(self) -> None:
        v = ScopeValidator(TokenScope.READ_REPO)
        assert v.has_scope(TokenScope.READ_REPO), "Condition must be true"

    def test_has_scope_true(self) -> None:
        v = ScopeValidator(["repo:admin"])
        assert v.has_scope(TokenScope.READ_REPO), "Condition must be true"
        assert v.has_scope(TokenScope.WRITE_REPO), "Condition must be true"
        assert v.has_scope(TokenScope.ADMIN_REPO), "Condition must be true"

    def test_has_scope_false(self) -> None:
        v = ScopeValidator(["repo:read"])
        assert not v.has_scope(TokenScope.WRITE_REPO), "Condition must be true"

    def test_has_any_scope_first_match(self) -> None:
        v = ScopeValidator(["repo:read"])
        assert v.has_any_scope([TokenScope.READ_REPO, TokenScope.WRITE_WORKFLOW])

    def test_has_any_scope_no_match(self) -> None:
        v = ScopeValidator(["repo:read"])
        assert not v.has_any_scope([TokenScope.WRITE_REPO, TokenScope.WRITE_WORKFLOW])

    def test_require_scope_passes(self) -> None:
        v = ScopeValidator(["repo:write"])
        v.require_scope(TokenScope.READ_REPO)  # implied by write, no error

    def test_require_scope_raises(self) -> None:
        v = ScopeValidator(["repo:read"])
        with pytest.raises(InsufficientScopeError, match="Missing required scope"):
            v.require_scope(TokenScope.WRITE_REPO)

    def test_require_any_scope_passes(self) -> None:
        v = ScopeValidator(["workflow:write"])
        v.require_any_scope([TokenScope.WRITE_WORKFLOW, TokenScope.ADMIN_REPO])

    def test_require_any_scope_raises(self) -> None:
        v = ScopeValidator(["repo:read"])
        with pytest.raises(InsufficientScopeError, match="Need one of"):
            v.require_any_scope([TokenScope.WRITE_REPO, TokenScope.ADMIN_REPO])

    def test_validate_success(self) -> None:
        v = ScopeValidator(["repo:write"])
        result = v.validate(TokenScope.READ_REPO)
        assert isinstance(result, ScopeValidationResult)
        assert result.valid is True, "Result must not be empty"
        assert result.message == "Scope validation successful", "Result must not be empty"

    def test_validate_failure(self) -> None:
        v = ScopeValidator(["repo:read"])
        result = v.validate(TokenScope.WRITE_REPO)
        assert result.valid is False, "Result must not be empty"
        assert result.missing_scopes is not None, "missing_scopes must be initialized"
        assert "Missing scopes" in result.message, "Result must not be empty"

    def test_get_granted_scopes(self) -> None:
        v = ScopeValidator(["repo:read", "workflow:read"])
        scopes = v.get_granted_scopes()
        assert isinstance(scopes, set)
        assert "repo:read" in scopes, "Condition must be true"


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------


class TestContextHelpers:
    def setup_method(self) -> None:
        clear_scope_validator()

    def test_get_returns_none_initially(self) -> None:
        assert get_scope_validator() is None, "get_scope_validat is not valid"

    def test_set_and_get(self) -> None:
        v = ScopeValidator(["repo:read"])
        set_scope_validator(v)
        assert get_scope_validator() is v, "get_scope_validat is not valid"

    def test_clear_resets_to_none(self) -> None:
        v = ScopeValidator(["repo:read"])
        set_scope_validator(v)
        clear_scope_validator()
        assert get_scope_validator() is None, "get_scope_validat is not valid"

    def test_overwrite_validator(self) -> None:
        v1 = ScopeValidator(["repo:read"])
        v2 = ScopeValidator(["workflow:write"])
        set_scope_validator(v1)
        set_scope_validator(v2)
        assert get_scope_validator() is v2, "get_scope_validat is not valid"


# ---------------------------------------------------------------------------
# require_scope decorator
# ---------------------------------------------------------------------------


class TestRequireScopeDecorator:
    def setup_method(self) -> None:
        clear_scope_validator()

    def test_passes_with_sufficient_scope(self) -> None:
        v = ScopeValidator(["repo:write"])
        set_scope_validator(v)

        @require_scope("repo:read")
        def fn() -> str:
            return "ok"

        assert fn() == "ok", "Condition must be true"

    def test_raises_with_insufficient_scope(self) -> None:
        v = ScopeValidator(["repo:read"])
        set_scope_validator(v)

        @require_scope("repo:write")
        def fn() -> None:
            pass

        with pytest.raises(InsufficientScopeError):
            fn()

    def test_raises_runtime_error_no_validator(self) -> None:
        @require_scope("repo:read")
        def fn() -> None:
            pass

        with pytest.raises(RuntimeError, match="No scope validator"):
            fn()

    def test_preserves_function_name(self) -> None:
        @require_scope("repo:read")
        def my_special_fn() -> None:
            pass

        assert my_special_fn.__name__ == "my_special_fn", "__name__ is not valid"

    def test_stores_required_scopes_metadata(self) -> None:
        @require_scope("repo:write", "workflow:read")
        def fn() -> None:
            pass

        assert fn.__required_scopes__ == ("repo:write", "workflow:read")
        assert fn.__scope_protected__ is True, "__scope_protected__ is not valid"

    def test_passes_args_kwargs(self) -> None:
        v = ScopeValidator(["repo:write"])
        set_scope_validator(v)

        @require_scope("repo:read")
        def add(x: int, y: int) -> int:
            return x + y

        assert add(2, y=3) == 5

    def test_multiple_scopes_all_required(self) -> None:
        v = ScopeValidator(["repo:write"])
        set_scope_validator(v)

        @require_scope("repo:read", "repo:write")
        def fn() -> str:
            return "multi"

        assert fn() == "multi", "Condition must be true"

    def test_multiple_scopes_partial_fails(self) -> None:
        v = ScopeValidator(["repo:read"])
        set_scope_validator(v)

        @require_scope("repo:read", "workflow:write")
        def fn() -> None:
            pass

        with pytest.raises(InsufficientScopeError):
            fn()


# ---------------------------------------------------------------------------
# require_any_scope decorator
# ---------------------------------------------------------------------------


class TestRequireAnyScopeDecorator:
    def setup_method(self) -> None:
        clear_scope_validator()

    def test_passes_with_one_matching_scope(self) -> None:
        v = ScopeValidator(["repo:read"])
        set_scope_validator(v)

        @require_any_scope("repo:read", "workflow:write")
        def fn() -> str:
            return "any"

        assert fn() == "any", "Condition must be true"

    def test_raises_with_no_matching_scope(self) -> None:
        v = ScopeValidator(["issues:read"])
        set_scope_validator(v)

        @require_any_scope("repo:write", "workflow:write")
        def fn() -> None:
            pass

        with pytest.raises(InsufficientScopeError):
            fn()

    def test_raises_runtime_error_no_validator(self) -> None:
        @require_any_scope("repo:read")
        def fn() -> None:
            pass

        with pytest.raises(RuntimeError, match="No scope validator"):
            fn()

    def test_stores_any_metadata(self) -> None:
        @require_any_scope("repo:read", "workflow:read")
        def fn() -> None:
            pass

        assert fn.__scope_any__ is True, "__scope_any__ is not valid"
        assert fn.__scope_protected__ is True, "__scope_protected__ is not valid"


# ---------------------------------------------------------------------------
# optional_scope decorator
# ---------------------------------------------------------------------------


class TestOptionalScopeDecorator:
    def setup_method(self) -> None:
        clear_scope_validator()

    def test_executes_without_validator(self) -> None:
        @optional_scope("repo:write")
        def fn() -> str:
            return "no validator"

        assert fn() == "no validator", "Condition must be true"

    def test_executes_with_validator_and_scope(self) -> None:
        v = ScopeValidator(["repo:write"])
        set_scope_validator(v)

        @optional_scope("repo:write")
        def fn() -> str:
            return "has scope"

        assert fn() == "has scope", "Condition must be true"

    def test_executes_with_validator_missing_scope(self) -> None:
        v = ScopeValidator(["repo:read"])
        set_scope_validator(v)

        @optional_scope("repo:write")
        def fn() -> str:
            return "no write but ok"

        assert fn() == "no write but ok", "Condition must be true"

    def test_stores_optional_metadata(self) -> None:
        @optional_scope("repo:write")
        def fn() -> None:
            pass

        assert fn.__scope_optional__ is True, "__scope_optional__ is not valid"
        assert fn.__optional_scopes__ == ("repo:write",)


# ---------------------------------------------------------------------------
# scope_metadata helper
# ---------------------------------------------------------------------------


class TestScopeMetadata:
    def test_undecorated_function(self) -> None:
        def plain() -> None:
            pass

        meta = scope_metadata(plain)
        assert meta["protected"] is False, "Condition must be true"
        assert meta["optional"] is False, "Condition must be true"
        assert meta["required"] == [], "Condition must be true"
        assert meta["any"] is False, "Condition must be true"

    def test_require_scope_metadata(self) -> None:
        @require_scope("repo:write")
        def fn() -> None:
            pass

        meta = scope_metadata(fn)
        assert meta["protected"] is True, "Condition must be true"
        assert meta["required"] == ("repo:write",)
        assert meta["any"] is False, "Condition must be true"
        assert meta["optional"] is False, "Condition must be true"

    def test_require_any_scope_metadata(self) -> None:
        @require_any_scope("repo:read", "workflow:read")
        def fn() -> None:
            pass

        meta = scope_metadata(fn)
        assert meta["any"] is True, "Condition must be true"
        assert meta["protected"] is True, "Condition must be true"

    def test_optional_scope_metadata(self) -> None:
        @optional_scope("repo:read")
        def fn() -> None:
            pass

        meta = scope_metadata(fn)
        assert meta["optional"] is True, "Condition must be true"
        assert meta["protected"] is False, "Condition must be true"
