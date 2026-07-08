"""Scope Validation Library for Token Authorization.

This module provides centralized scope validation for token-based authorization,
supporting hierarchical scope checking and fine-grained access control.

Part of PS-05 Enhancement: Scope Validation Library - Priority 4
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Flag, auto
from typing import Optional

logger = logging.getLogger(__name__)


class ScopeError(Exception):
    """Base exception for scope validation errors."""


class InsufficientScopeError(ScopeError):
    """Raised when token lacks required scope."""


class InvalidScopeError(ScopeError):
    """Raised when scope format is invalid."""


class TokenScope(Flag):
    """Token scope flags with hierarchical permissions.

    Scopes follow a hierarchical model where broader scopes
    imply narrower ones:
    - ADMIN_* implies WRITE_* and READ_*
    - WRITE_* implies READ_*

    Examples:
        >>> scope = TokenScope.READ_REPO | TokenScope.WRITE_WORKFLOW
        >>> scope.has(TokenScope.READ_REPO)
        True
    """

    NONE = 0

    # Repository scopes
    READ_REPO = auto()
    WRITE_REPO = auto()
    ADMIN_REPO = auto()
    DELETE_REPO = auto()

    # Workflow scopes
    READ_WORKFLOW = auto()
    WRITE_WORKFLOW = auto()
    ADMIN_WORKFLOW = auto()

    # Issues scopes
    READ_ISSUES = auto()
    WRITE_ISSUES = auto()
    ADMIN_ISSUES = auto()

    # Packages scopes
    READ_PACKAGES = auto()
    WRITE_PACKAGES = auto()
    ADMIN_PACKAGES = auto()

    # Organization scopes
    READ_ORG = auto()
    WRITE_ORG = auto()
    ADMIN_ORG = auto()

    # User scopes
    READ_USER = auto()
    WRITE_USER = auto()

    # Security scopes
    READ_SECURITY = auto()
    WRITE_SECURITY = auto()
    ADMIN_SECURITY = auto()

    @classmethod
    def from_string(cls, scope: str) -> TokenScope:
        """Parse scope from string format.

        Supports formats:
        - "repo" -> READ_REPO | WRITE_REPO
        - "repo:read" -> READ_REPO
        - "repo:write" -> WRITE_REPO (implies READ_REPO)
        - "admin:repo" -> ADMIN_REPO (implies WRITE_REPO and READ_REPO)

        Args:
            scope: Scope string in format "resource:permission"

        Returns:
            TokenScope flags

        Raises:
            InvalidScopeError: If scope format is invalid
        """
        scope = scope.strip().lower()

        # Mapping of string scopes to flags
        scope_map = {
            # Repository
            "repo": cls.READ_REPO | cls.WRITE_REPO,
            "repo:read": cls.READ_REPO,
            "repo:write": cls.WRITE_REPO | cls.READ_REPO,
            "repo:admin": cls.ADMIN_REPO | cls.WRITE_REPO | cls.READ_REPO,
            "repo:delete": cls.DELETE_REPO | cls.ADMIN_REPO | cls.WRITE_REPO | cls.READ_REPO,
            # Workflow
            "workflow": cls.READ_WORKFLOW | cls.WRITE_WORKFLOW,
            "workflow:read": cls.READ_WORKFLOW,
            "workflow:write": cls.WRITE_WORKFLOW | cls.READ_WORKFLOW,
            "workflow:admin": cls.ADMIN_WORKFLOW | cls.WRITE_WORKFLOW | cls.READ_WORKFLOW,
            # Issues
            "issues": cls.READ_ISSUES | cls.WRITE_ISSUES,
            "issues:read": cls.READ_ISSUES,
            "issues:write": cls.WRITE_ISSUES | cls.READ_ISSUES,
            "issues:admin": cls.ADMIN_ISSUES | cls.WRITE_ISSUES | cls.READ_ISSUES,
            # Packages
            "packages": cls.READ_PACKAGES | cls.WRITE_PACKAGES,
            "packages:read": cls.READ_PACKAGES,
            "packages:write": cls.WRITE_PACKAGES | cls.READ_PACKAGES,
            "packages:admin": cls.ADMIN_PACKAGES | cls.WRITE_PACKAGES | cls.READ_PACKAGES,
            # Organization
            "org": cls.READ_ORG | cls.WRITE_ORG,
            "org:read": cls.READ_ORG,
            "org:write": cls.WRITE_ORG | cls.READ_ORG,
            "org:admin": cls.ADMIN_ORG | cls.WRITE_ORG | cls.READ_ORG,
            # User
            "user": cls.READ_USER | cls.WRITE_USER,
            "user:read": cls.READ_USER,
            "user:write": cls.WRITE_USER | cls.READ_USER,
            # Security
            "security": cls.READ_SECURITY | cls.WRITE_SECURITY,
            "security:read": cls.READ_SECURITY,
            "security:write": cls.WRITE_SECURITY | cls.READ_SECURITY,
            "security:admin": cls.ADMIN_SECURITY | cls.WRITE_SECURITY | cls.READ_SECURITY,
        }

        if scope not in scope_map:
            raise InvalidScopeError(f"Unknown scope: {scope}")

        return scope_map[scope]

    @classmethod
    def from_list(cls, scopes: list[str]) -> TokenScope:
        """Parse multiple scopes from list.

        Args:
            scopes: List of scope strings

        Returns:
            Combined TokenScope flags
        """
        result = cls.NONE
        for scope in scopes:
            result |= cls.from_string(scope)
        return result

    def to_strings(self) -> set[str]:
        """Convert scope flags to string representation.

        Returns:
            Set of scope strings
        """
        scopes = set()

        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add("repo:read")
        if self & TokenScope.WRITE_REPO:
            scopes.add("repo:write")
        if self & TokenScope.ADMIN_REPO:
            scopes.add("repo:admin")
        if self & TokenScope.DELETE_REPO:
            scopes.add("repo:delete")

        if self & TokenScope.READ_WORKFLOW:
            scopes.add("workflow:read")
        if self & TokenScope.WRITE_WORKFLOW:
            scopes.add("workflow:write")
        if self & TokenScope.ADMIN_WORKFLOW:
            scopes.add("workflow:admin")

        if self & TokenScope.READ_ISSUES:
            scopes.add("issues:read")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")

        # Add more as needed...

        return scopes

    def has(self, required: TokenScope) -> bool:
        """Check if this scope includes required permissions.

        Args:
            required: Required scope flags

        Returns:
            True if all required flags are present
        """
        return bool(self & required == required)


@dataclass
class ScopeValidationResult:
    """Result of scope validation."""

    valid: bool
    granted_scopes: TokenScope
    required_scopes: TokenScope
    missing_scopes: Optional[TokenScope] = None
    message: Optional[str] = None


class ScopeValidator:
    """Validates token scopes against required permissions.

    Example:
        >>> validator = ScopeValidator(["repo:write", "workflow:read"])
        >>> validator.require(TokenScope.READ_REPO)  # OK
        >>> validator.require(TokenScope.WRITE_WORKFLOW)  # Raises InsufficientScopeError
    """

    def __init__(self, token_scopes: list[str] | TokenScope):
        """Initialize validator with token scopes.

        Args:
            token_scopes: List of scope strings or TokenScope flags
        """
        if isinstance(token_scopes, TokenScope):
            self.scopes = token_scopes
        else:
            self.scopes = TokenScope.from_list(token_scopes)

        logger.debug(f"ScopeValidator initialized with: {self.scopes.to_strings()}")

    def has_scope(self, required: TokenScope) -> bool:
        """Check if token has required scope.

        Args:
            required: Required scope flags

        Returns:
            True if token has all required scopes
        """
        return self.scopes.has(required)

    def has_any_scope(self, required_scopes: list[TokenScope]) -> bool:
        """Check if token has any of the required scopes.

        Args:
            required_scopes: List of acceptable scope flags

        Returns:
            True if token has at least one of the required scopes
        """
        return any(self.has_scope(scope) for scope in required_scopes)

    def require_scope(self, required: TokenScope) -> None:
        """Require specific scope, raising exception if not present.

        Args:
            required: Required scope flags

        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if not self.has_scope(required):
            missing = required & ~self.scopes
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Required: {required.to_strings()}, "
                f"Granted: {self.scopes.to_strings()}, "
                f"Missing: {missing.to_strings()}"
            )

    def require_any_scope(self, required_scopes: list[TokenScope]) -> None:
        """Require at least one of the specified scopes.

        Args:
            required_scopes: List of acceptable scope flags

        Raises:
            InsufficientScopeError: If token lacks all required scopes
        """
        if not self.has_any_scope(required_scopes):
            required_strings = [scope.to_strings() for scope in required_scopes]
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Need one of: {required_strings}, "
                f"Granted: {self.scopes.to_strings()}"
            )

    def validate(self, required: TokenScope) -> ScopeValidationResult:
        """Validate scope and return detailed result.

        Args:
            required: Required scope flags

        Returns:
            ScopeValidationResult with validation details
        """
        has_scope = self.has_scope(required)

        if has_scope:
            return ScopeValidationResult(
                valid=True,
                granted_scopes=self.scopes,
                required_scopes=required,
                message="Scope validation successful",
            )
        missing = required & ~self.scopes
        return ScopeValidationResult(
            valid=False,
            granted_scopes=self.scopes,
            required_scopes=required,
            missing_scopes=missing,
            message=f"Missing scopes: {missing.to_strings()}",
        )

    def get_granted_scopes(self) -> set[str]:
        """Get set of granted scope strings.

        Returns:
            Set of scope strings
        """
        return self.scopes.to_strings()
