"""Scope Validation Library for Token Authorization.

This module provides centralized scope validation for token-based authorization,
supporting hierarchical scope checking and fine-grained access control.

Part of PS-05 Enhancement: Scope Validation Library - Priority 4
"""

from __future__ import annotations

import logging
from enum import Flag, auto
from typing import Set, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class ScopeError(Exception):
    """Base exception for scope validation errors."""
    pass


class InsufficientScopeError(ScopeError):
    """Raised when token lacks required scope."""
    pass


class InvalidScopeError(ScopeError):
    """Raised when scope format is invalid."""
    pass


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
    def from_list(cls, scopes: List[str]) -> TokenScope:
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
    
    def xǁTokenScopeǁto_strings__mutmut_orig(self) -> Set[str]:
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
    
    def xǁTokenScopeǁto_strings__mutmut_1(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = None
        
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
    
    def xǁTokenScopeǁto_strings__mutmut_2(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self | TokenScope.READ_REPO:
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
    
    def xǁTokenScopeǁto_strings__mutmut_3(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add(None)
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
    
    def xǁTokenScopeǁto_strings__mutmut_4(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add("XXrepo:readXX")
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
    
    def xǁTokenScopeǁto_strings__mutmut_5(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add("REPO:READ")
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
    
    def xǁTokenScopeǁto_strings__mutmut_6(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add("repo:read")
        if self | TokenScope.WRITE_REPO:
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
    
    def xǁTokenScopeǁto_strings__mutmut_7(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add("repo:read")
        if self & TokenScope.WRITE_REPO:
            scopes.add(None)
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
    
    def xǁTokenScopeǁto_strings__mutmut_8(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add("repo:read")
        if self & TokenScope.WRITE_REPO:
            scopes.add("XXrepo:writeXX")
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
    
    def xǁTokenScopeǁto_strings__mutmut_9(self) -> Set[str]:
        """Convert scope flags to string representation.
        
        Returns:
            Set of scope strings
        """
        scopes = set()
        
        # Map flags back to strings (simplified form)
        if self & TokenScope.READ_REPO:
            scopes.add("repo:read")
        if self & TokenScope.WRITE_REPO:
            scopes.add("REPO:WRITE")
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
    
    def xǁTokenScopeǁto_strings__mutmut_10(self) -> Set[str]:
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
        if self | TokenScope.ADMIN_REPO:
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
    
    def xǁTokenScopeǁto_strings__mutmut_11(self) -> Set[str]:
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
            scopes.add(None)
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
    
    def xǁTokenScopeǁto_strings__mutmut_12(self) -> Set[str]:
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
            scopes.add("XXrepo:adminXX")
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
    
    def xǁTokenScopeǁto_strings__mutmut_13(self) -> Set[str]:
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
            scopes.add("REPO:ADMIN")
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
    
    def xǁTokenScopeǁto_strings__mutmut_14(self) -> Set[str]:
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
        if self | TokenScope.DELETE_REPO:
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
    
    def xǁTokenScopeǁto_strings__mutmut_15(self) -> Set[str]:
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
            scopes.add(None)
        
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
    
    def xǁTokenScopeǁto_strings__mutmut_16(self) -> Set[str]:
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
            scopes.add("XXrepo:deleteXX")
        
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
    
    def xǁTokenScopeǁto_strings__mutmut_17(self) -> Set[str]:
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
            scopes.add("REPO:DELETE")
        
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
    
    def xǁTokenScopeǁto_strings__mutmut_18(self) -> Set[str]:
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
        
        if self | TokenScope.READ_WORKFLOW:
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
    
    def xǁTokenScopeǁto_strings__mutmut_19(self) -> Set[str]:
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
            scopes.add(None)
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
    
    def xǁTokenScopeǁto_strings__mutmut_20(self) -> Set[str]:
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
            scopes.add("XXworkflow:readXX")
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
    
    def xǁTokenScopeǁto_strings__mutmut_21(self) -> Set[str]:
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
            scopes.add("WORKFLOW:READ")
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
    
    def xǁTokenScopeǁto_strings__mutmut_22(self) -> Set[str]:
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
        if self | TokenScope.WRITE_WORKFLOW:
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
    
    def xǁTokenScopeǁto_strings__mutmut_23(self) -> Set[str]:
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
            scopes.add(None)
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
    
    def xǁTokenScopeǁto_strings__mutmut_24(self) -> Set[str]:
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
            scopes.add("XXworkflow:writeXX")
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
    
    def xǁTokenScopeǁto_strings__mutmut_25(self) -> Set[str]:
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
            scopes.add("WORKFLOW:WRITE")
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
    
    def xǁTokenScopeǁto_strings__mutmut_26(self) -> Set[str]:
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
        if self | TokenScope.ADMIN_WORKFLOW:
            scopes.add("workflow:admin")
        
        if self & TokenScope.READ_ISSUES:
            scopes.add("issues:read")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_27(self) -> Set[str]:
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
            scopes.add(None)
        
        if self & TokenScope.READ_ISSUES:
            scopes.add("issues:read")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_28(self) -> Set[str]:
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
            scopes.add("XXworkflow:adminXX")
        
        if self & TokenScope.READ_ISSUES:
            scopes.add("issues:read")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_29(self) -> Set[str]:
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
            scopes.add("WORKFLOW:ADMIN")
        
        if self & TokenScope.READ_ISSUES:
            scopes.add("issues:read")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_30(self) -> Set[str]:
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
        
        if self | TokenScope.READ_ISSUES:
            scopes.add("issues:read")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_31(self) -> Set[str]:
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
            scopes.add(None)
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_32(self) -> Set[str]:
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
            scopes.add("XXissues:readXX")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_33(self) -> Set[str]:
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
            scopes.add("ISSUES:READ")
        if self & TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_34(self) -> Set[str]:
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
        if self | TokenScope.WRITE_ISSUES:
            scopes.add("issues:write")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_35(self) -> Set[str]:
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
            scopes.add(None)
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_36(self) -> Set[str]:
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
            scopes.add("XXissues:writeXX")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_37(self) -> Set[str]:
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
            scopes.add("ISSUES:WRITE")
        if self & TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_38(self) -> Set[str]:
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
        if self | TokenScope.ADMIN_ISSUES:
            scopes.add("issues:admin")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_39(self) -> Set[str]:
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
            scopes.add(None)
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_40(self) -> Set[str]:
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
            scopes.add("XXissues:adminXX")
        
        # Add more as needed...
        
        return scopes
    
    def xǁTokenScopeǁto_strings__mutmut_41(self) -> Set[str]:
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
            scopes.add("ISSUES:ADMIN")
        
        # Add more as needed...
        
        return scopes
    
    xǁTokenScopeǁto_strings__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenScopeǁto_strings__mutmut_1': xǁTokenScopeǁto_strings__mutmut_1, 
        'xǁTokenScopeǁto_strings__mutmut_2': xǁTokenScopeǁto_strings__mutmut_2, 
        'xǁTokenScopeǁto_strings__mutmut_3': xǁTokenScopeǁto_strings__mutmut_3, 
        'xǁTokenScopeǁto_strings__mutmut_4': xǁTokenScopeǁto_strings__mutmut_4, 
        'xǁTokenScopeǁto_strings__mutmut_5': xǁTokenScopeǁto_strings__mutmut_5, 
        'xǁTokenScopeǁto_strings__mutmut_6': xǁTokenScopeǁto_strings__mutmut_6, 
        'xǁTokenScopeǁto_strings__mutmut_7': xǁTokenScopeǁto_strings__mutmut_7, 
        'xǁTokenScopeǁto_strings__mutmut_8': xǁTokenScopeǁto_strings__mutmut_8, 
        'xǁTokenScopeǁto_strings__mutmut_9': xǁTokenScopeǁto_strings__mutmut_9, 
        'xǁTokenScopeǁto_strings__mutmut_10': xǁTokenScopeǁto_strings__mutmut_10, 
        'xǁTokenScopeǁto_strings__mutmut_11': xǁTokenScopeǁto_strings__mutmut_11, 
        'xǁTokenScopeǁto_strings__mutmut_12': xǁTokenScopeǁto_strings__mutmut_12, 
        'xǁTokenScopeǁto_strings__mutmut_13': xǁTokenScopeǁto_strings__mutmut_13, 
        'xǁTokenScopeǁto_strings__mutmut_14': xǁTokenScopeǁto_strings__mutmut_14, 
        'xǁTokenScopeǁto_strings__mutmut_15': xǁTokenScopeǁto_strings__mutmut_15, 
        'xǁTokenScopeǁto_strings__mutmut_16': xǁTokenScopeǁto_strings__mutmut_16, 
        'xǁTokenScopeǁto_strings__mutmut_17': xǁTokenScopeǁto_strings__mutmut_17, 
        'xǁTokenScopeǁto_strings__mutmut_18': xǁTokenScopeǁto_strings__mutmut_18, 
        'xǁTokenScopeǁto_strings__mutmut_19': xǁTokenScopeǁto_strings__mutmut_19, 
        'xǁTokenScopeǁto_strings__mutmut_20': xǁTokenScopeǁto_strings__mutmut_20, 
        'xǁTokenScopeǁto_strings__mutmut_21': xǁTokenScopeǁto_strings__mutmut_21, 
        'xǁTokenScopeǁto_strings__mutmut_22': xǁTokenScopeǁto_strings__mutmut_22, 
        'xǁTokenScopeǁto_strings__mutmut_23': xǁTokenScopeǁto_strings__mutmut_23, 
        'xǁTokenScopeǁto_strings__mutmut_24': xǁTokenScopeǁto_strings__mutmut_24, 
        'xǁTokenScopeǁto_strings__mutmut_25': xǁTokenScopeǁto_strings__mutmut_25, 
        'xǁTokenScopeǁto_strings__mutmut_26': xǁTokenScopeǁto_strings__mutmut_26, 
        'xǁTokenScopeǁto_strings__mutmut_27': xǁTokenScopeǁto_strings__mutmut_27, 
        'xǁTokenScopeǁto_strings__mutmut_28': xǁTokenScopeǁto_strings__mutmut_28, 
        'xǁTokenScopeǁto_strings__mutmut_29': xǁTokenScopeǁto_strings__mutmut_29, 
        'xǁTokenScopeǁto_strings__mutmut_30': xǁTokenScopeǁto_strings__mutmut_30, 
        'xǁTokenScopeǁto_strings__mutmut_31': xǁTokenScopeǁto_strings__mutmut_31, 
        'xǁTokenScopeǁto_strings__mutmut_32': xǁTokenScopeǁto_strings__mutmut_32, 
        'xǁTokenScopeǁto_strings__mutmut_33': xǁTokenScopeǁto_strings__mutmut_33, 
        'xǁTokenScopeǁto_strings__mutmut_34': xǁTokenScopeǁto_strings__mutmut_34, 
        'xǁTokenScopeǁto_strings__mutmut_35': xǁTokenScopeǁto_strings__mutmut_35, 
        'xǁTokenScopeǁto_strings__mutmut_36': xǁTokenScopeǁto_strings__mutmut_36, 
        'xǁTokenScopeǁto_strings__mutmut_37': xǁTokenScopeǁto_strings__mutmut_37, 
        'xǁTokenScopeǁto_strings__mutmut_38': xǁTokenScopeǁto_strings__mutmut_38, 
        'xǁTokenScopeǁto_strings__mutmut_39': xǁTokenScopeǁto_strings__mutmut_39, 
        'xǁTokenScopeǁto_strings__mutmut_40': xǁTokenScopeǁto_strings__mutmut_40, 
        'xǁTokenScopeǁto_strings__mutmut_41': xǁTokenScopeǁto_strings__mutmut_41
    }
    
    def to_strings(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenScopeǁto_strings__mutmut_orig"), object.__getattribute__(self, "xǁTokenScopeǁto_strings__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_strings.__signature__ = _mutmut_signature(xǁTokenScopeǁto_strings__mutmut_orig)
    xǁTokenScopeǁto_strings__mutmut_orig.__name__ = 'xǁTokenScopeǁto_strings'
    
    def xǁTokenScopeǁhas__mutmut_orig(self, required: TokenScope) -> bool:
        """Check if this scope includes required permissions.
        
        Args:
            required: Required scope flags
            
        Returns:
            True if all required flags are present
        """
        return bool(self & required == required)
    
    def xǁTokenScopeǁhas__mutmut_1(self, required: TokenScope) -> bool:
        """Check if this scope includes required permissions.
        
        Args:
            required: Required scope flags
            
        Returns:
            True if all required flags are present
        """
        return bool(None)
    
    def xǁTokenScopeǁhas__mutmut_2(self, required: TokenScope) -> bool:
        """Check if this scope includes required permissions.
        
        Args:
            required: Required scope flags
            
        Returns:
            True if all required flags are present
        """
        return bool(self | required == required)
    
    def xǁTokenScopeǁhas__mutmut_3(self, required: TokenScope) -> bool:
        """Check if this scope includes required permissions.
        
        Args:
            required: Required scope flags
            
        Returns:
            True if all required flags are present
        """
        return bool(self & required != required)
    
    xǁTokenScopeǁhas__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenScopeǁhas__mutmut_1': xǁTokenScopeǁhas__mutmut_1, 
        'xǁTokenScopeǁhas__mutmut_2': xǁTokenScopeǁhas__mutmut_2, 
        'xǁTokenScopeǁhas__mutmut_3': xǁTokenScopeǁhas__mutmut_3
    }
    
    def has(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenScopeǁhas__mutmut_orig"), object.__getattribute__(self, "xǁTokenScopeǁhas__mutmut_mutants"), args, kwargs, self)
        return result 
    
    has.__signature__ = _mutmut_signature(xǁTokenScopeǁhas__mutmut_orig)
    xǁTokenScopeǁhas__mutmut_orig.__name__ = 'xǁTokenScopeǁhas'


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
    
    def xǁScopeValidatorǁ__init____mutmut_orig(self, token_scopes: List[str] | TokenScope):
        """Initialize validator with token scopes.
        
        Args:
            token_scopes: List of scope strings or TokenScope flags
        """
        if isinstance(token_scopes, TokenScope):
            self.scopes = token_scopes
        else:
            self.scopes = TokenScope.from_list(token_scopes)
        
        logger.debug(f"ScopeValidator initialized with: {self.scopes.to_strings()}")
    
    def xǁScopeValidatorǁ__init____mutmut_1(self, token_scopes: List[str] | TokenScope):
        """Initialize validator with token scopes.
        
        Args:
            token_scopes: List of scope strings or TokenScope flags
        """
        if isinstance(token_scopes, TokenScope):
            self.scopes = None
        else:
            self.scopes = TokenScope.from_list(token_scopes)
        
        logger.debug(f"ScopeValidator initialized with: {self.scopes.to_strings()}")
    
    def xǁScopeValidatorǁ__init____mutmut_2(self, token_scopes: List[str] | TokenScope):
        """Initialize validator with token scopes.
        
        Args:
            token_scopes: List of scope strings or TokenScope flags
        """
        if isinstance(token_scopes, TokenScope):
            self.scopes = token_scopes
        else:
            self.scopes = None
        
        logger.debug(f"ScopeValidator initialized with: {self.scopes.to_strings()}")
    
    def xǁScopeValidatorǁ__init____mutmut_3(self, token_scopes: List[str] | TokenScope):
        """Initialize validator with token scopes.
        
        Args:
            token_scopes: List of scope strings or TokenScope flags
        """
        if isinstance(token_scopes, TokenScope):
            self.scopes = token_scopes
        else:
            self.scopes = TokenScope.from_list(None)
        
        logger.debug(f"ScopeValidator initialized with: {self.scopes.to_strings()}")
    
    def xǁScopeValidatorǁ__init____mutmut_4(self, token_scopes: List[str] | TokenScope):
        """Initialize validator with token scopes.
        
        Args:
            token_scopes: List of scope strings or TokenScope flags
        """
        if isinstance(token_scopes, TokenScope):
            self.scopes = token_scopes
        else:
            self.scopes = TokenScope.from_list(token_scopes)
        
        logger.debug(None)
    
    xǁScopeValidatorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁScopeValidatorǁ__init____mutmut_1': xǁScopeValidatorǁ__init____mutmut_1, 
        'xǁScopeValidatorǁ__init____mutmut_2': xǁScopeValidatorǁ__init____mutmut_2, 
        'xǁScopeValidatorǁ__init____mutmut_3': xǁScopeValidatorǁ__init____mutmut_3, 
        'xǁScopeValidatorǁ__init____mutmut_4': xǁScopeValidatorǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁScopeValidatorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁScopeValidatorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁScopeValidatorǁ__init____mutmut_orig)
    xǁScopeValidatorǁ__init____mutmut_orig.__name__ = 'xǁScopeValidatorǁ__init__'
    
    def xǁScopeValidatorǁhas_scope__mutmut_orig(self, required: TokenScope) -> bool:
        """Check if token has required scope.
        
        Args:
            required: Required scope flags
            
        Returns:
            True if token has all required scopes
        """
        return self.scopes.has(required)
    
    def xǁScopeValidatorǁhas_scope__mutmut_1(self, required: TokenScope) -> bool:
        """Check if token has required scope.
        
        Args:
            required: Required scope flags
            
        Returns:
            True if token has all required scopes
        """
        return self.scopes.has(None)
    
    xǁScopeValidatorǁhas_scope__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁScopeValidatorǁhas_scope__mutmut_1': xǁScopeValidatorǁhas_scope__mutmut_1
    }
    
    def has_scope(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁScopeValidatorǁhas_scope__mutmut_orig"), object.__getattribute__(self, "xǁScopeValidatorǁhas_scope__mutmut_mutants"), args, kwargs, self)
        return result 
    
    has_scope.__signature__ = _mutmut_signature(xǁScopeValidatorǁhas_scope__mutmut_orig)
    xǁScopeValidatorǁhas_scope__mutmut_orig.__name__ = 'xǁScopeValidatorǁhas_scope'
    
    def xǁScopeValidatorǁhas_any_scope__mutmut_orig(self, required_scopes: List[TokenScope]) -> bool:
        """Check if token has any of the required scopes.
        
        Args:
            required_scopes: List of acceptable scope flags
            
        Returns:
            True if token has at least one of the required scopes
        """
        return any(self.has_scope(scope) for scope in required_scopes)
    
    def xǁScopeValidatorǁhas_any_scope__mutmut_1(self, required_scopes: List[TokenScope]) -> bool:
        """Check if token has any of the required scopes.
        
        Args:
            required_scopes: List of acceptable scope flags
            
        Returns:
            True if token has at least one of the required scopes
        """
        return any(None)
    
    def xǁScopeValidatorǁhas_any_scope__mutmut_2(self, required_scopes: List[TokenScope]) -> bool:
        """Check if token has any of the required scopes.
        
        Args:
            required_scopes: List of acceptable scope flags
            
        Returns:
            True if token has at least one of the required scopes
        """
        return any(self.has_scope(None) for scope in required_scopes)
    
    xǁScopeValidatorǁhas_any_scope__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁScopeValidatorǁhas_any_scope__mutmut_1': xǁScopeValidatorǁhas_any_scope__mutmut_1, 
        'xǁScopeValidatorǁhas_any_scope__mutmut_2': xǁScopeValidatorǁhas_any_scope__mutmut_2
    }
    
    def has_any_scope(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁScopeValidatorǁhas_any_scope__mutmut_orig"), object.__getattribute__(self, "xǁScopeValidatorǁhas_any_scope__mutmut_mutants"), args, kwargs, self)
        return result 
    
    has_any_scope.__signature__ = _mutmut_signature(xǁScopeValidatorǁhas_any_scope__mutmut_orig)
    xǁScopeValidatorǁhas_any_scope__mutmut_orig.__name__ = 'xǁScopeValidatorǁhas_any_scope'
    
    def xǁScopeValidatorǁrequire_scope__mutmut_orig(self, required: TokenScope) -> None:
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
    
    def xǁScopeValidatorǁrequire_scope__mutmut_1(self, required: TokenScope) -> None:
        """Require specific scope, raising exception if not present.
        
        Args:
            required: Required scope flags
            
        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if self.has_scope(required):
            missing = required & ~self.scopes
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Required: {required.to_strings()}, "
                f"Granted: {self.scopes.to_strings()}, "
                f"Missing: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_scope__mutmut_2(self, required: TokenScope) -> None:
        """Require specific scope, raising exception if not present.
        
        Args:
            required: Required scope flags
            
        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if not self.has_scope(None):
            missing = required & ~self.scopes
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Required: {required.to_strings()}, "
                f"Granted: {self.scopes.to_strings()}, "
                f"Missing: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_scope__mutmut_3(self, required: TokenScope) -> None:
        """Require specific scope, raising exception if not present.
        
        Args:
            required: Required scope flags
            
        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if not self.has_scope(required):
            missing = None
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Required: {required.to_strings()}, "
                f"Granted: {self.scopes.to_strings()}, "
                f"Missing: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_scope__mutmut_4(self, required: TokenScope) -> None:
        """Require specific scope, raising exception if not present.
        
        Args:
            required: Required scope flags
            
        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if not self.has_scope(required):
            missing = required | ~self.scopes
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Required: {required.to_strings()}, "
                f"Granted: {self.scopes.to_strings()}, "
                f"Missing: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_scope__mutmut_5(self, required: TokenScope) -> None:
        """Require specific scope, raising exception if not present.
        
        Args:
            required: Required scope flags
            
        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if not self.has_scope(required):
            missing = required & self.scopes
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Required: {required.to_strings()}, "
                f"Granted: {self.scopes.to_strings()}, "
                f"Missing: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_scope__mutmut_6(self, required: TokenScope) -> None:
        """Require specific scope, raising exception if not present.
        
        Args:
            required: Required scope flags
            
        Raises:
            InsufficientScopeError: If token lacks required scope
        """
        if not self.has_scope(required):
            missing = required & ~self.scopes
            raise InsufficientScopeError(
                None
            )
    
    xǁScopeValidatorǁrequire_scope__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁScopeValidatorǁrequire_scope__mutmut_1': xǁScopeValidatorǁrequire_scope__mutmut_1, 
        'xǁScopeValidatorǁrequire_scope__mutmut_2': xǁScopeValidatorǁrequire_scope__mutmut_2, 
        'xǁScopeValidatorǁrequire_scope__mutmut_3': xǁScopeValidatorǁrequire_scope__mutmut_3, 
        'xǁScopeValidatorǁrequire_scope__mutmut_4': xǁScopeValidatorǁrequire_scope__mutmut_4, 
        'xǁScopeValidatorǁrequire_scope__mutmut_5': xǁScopeValidatorǁrequire_scope__mutmut_5, 
        'xǁScopeValidatorǁrequire_scope__mutmut_6': xǁScopeValidatorǁrequire_scope__mutmut_6
    }
    
    def require_scope(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁScopeValidatorǁrequire_scope__mutmut_orig"), object.__getattribute__(self, "xǁScopeValidatorǁrequire_scope__mutmut_mutants"), args, kwargs, self)
        return result 
    
    require_scope.__signature__ = _mutmut_signature(xǁScopeValidatorǁrequire_scope__mutmut_orig)
    xǁScopeValidatorǁrequire_scope__mutmut_orig.__name__ = 'xǁScopeValidatorǁrequire_scope'
    
    def xǁScopeValidatorǁrequire_any_scope__mutmut_orig(self, required_scopes: List[TokenScope]) -> None:
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
    
    def xǁScopeValidatorǁrequire_any_scope__mutmut_1(self, required_scopes: List[TokenScope]) -> None:
        """Require at least one of the specified scopes.
        
        Args:
            required_scopes: List of acceptable scope flags
            
        Raises:
            InsufficientScopeError: If token lacks all required scopes
        """
        if self.has_any_scope(required_scopes):
            required_strings = [scope.to_strings() for scope in required_scopes]
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Need one of: {required_strings}, "
                f"Granted: {self.scopes.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_any_scope__mutmut_2(self, required_scopes: List[TokenScope]) -> None:
        """Require at least one of the specified scopes.
        
        Args:
            required_scopes: List of acceptable scope flags
            
        Raises:
            InsufficientScopeError: If token lacks all required scopes
        """
        if not self.has_any_scope(None):
            required_strings = [scope.to_strings() for scope in required_scopes]
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Need one of: {required_strings}, "
                f"Granted: {self.scopes.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_any_scope__mutmut_3(self, required_scopes: List[TokenScope]) -> None:
        """Require at least one of the specified scopes.
        
        Args:
            required_scopes: List of acceptable scope flags
            
        Raises:
            InsufficientScopeError: If token lacks all required scopes
        """
        if not self.has_any_scope(required_scopes):
            required_strings = None
            raise InsufficientScopeError(
                f"Missing required scope. "
                f"Need one of: {required_strings}, "
                f"Granted: {self.scopes.to_strings()}"
            )
    
    def xǁScopeValidatorǁrequire_any_scope__mutmut_4(self, required_scopes: List[TokenScope]) -> None:
        """Require at least one of the specified scopes.
        
        Args:
            required_scopes: List of acceptable scope flags
            
        Raises:
            InsufficientScopeError: If token lacks all required scopes
        """
        if not self.has_any_scope(required_scopes):
            required_strings = [scope.to_strings() for scope in required_scopes]
            raise InsufficientScopeError(
                None
            )
    
    xǁScopeValidatorǁrequire_any_scope__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁScopeValidatorǁrequire_any_scope__mutmut_1': xǁScopeValidatorǁrequire_any_scope__mutmut_1, 
        'xǁScopeValidatorǁrequire_any_scope__mutmut_2': xǁScopeValidatorǁrequire_any_scope__mutmut_2, 
        'xǁScopeValidatorǁrequire_any_scope__mutmut_3': xǁScopeValidatorǁrequire_any_scope__mutmut_3, 
        'xǁScopeValidatorǁrequire_any_scope__mutmut_4': xǁScopeValidatorǁrequire_any_scope__mutmut_4
    }
    
    def require_any_scope(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁScopeValidatorǁrequire_any_scope__mutmut_orig"), object.__getattribute__(self, "xǁScopeValidatorǁrequire_any_scope__mutmut_mutants"), args, kwargs, self)
        return result 
    
    require_any_scope.__signature__ = _mutmut_signature(xǁScopeValidatorǁrequire_any_scope__mutmut_orig)
    xǁScopeValidatorǁrequire_any_scope__mutmut_orig.__name__ = 'xǁScopeValidatorǁrequire_any_scope'
    
    def xǁScopeValidatorǁvalidate__mutmut_orig(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_1(self, required: TokenScope) -> ScopeValidationResult:
        """Validate scope and return detailed result.
        
        Args:
            required: Required scope flags
            
        Returns:
            ScopeValidationResult with validation details
        """
        has_scope = None
        
        if has_scope:
            return ScopeValidationResult(
                valid=True,
                granted_scopes=self.scopes,
                required_scopes=required,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_2(self, required: TokenScope) -> ScopeValidationResult:
        """Validate scope and return detailed result.
        
        Args:
            required: Required scope flags
            
        Returns:
            ScopeValidationResult with validation details
        """
        has_scope = self.has_scope(None)
        
        if has_scope:
            return ScopeValidationResult(
                valid=True,
                granted_scopes=self.scopes,
                required_scopes=required,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_3(self, required: TokenScope) -> ScopeValidationResult:
        """Validate scope and return detailed result.
        
        Args:
            required: Required scope flags
            
        Returns:
            ScopeValidationResult with validation details
        """
        has_scope = self.has_scope(required)
        
        if has_scope:
            return ScopeValidationResult(
                valid=None,
                granted_scopes=self.scopes,
                required_scopes=required,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_4(self, required: TokenScope) -> ScopeValidationResult:
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
                granted_scopes=None,
                required_scopes=required,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_5(self, required: TokenScope) -> ScopeValidationResult:
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
                required_scopes=None,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_6(self, required: TokenScope) -> ScopeValidationResult:
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
                message=None
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_7(self, required: TokenScope) -> ScopeValidationResult:
        """Validate scope and return detailed result.
        
        Args:
            required: Required scope flags
            
        Returns:
            ScopeValidationResult with validation details
        """
        has_scope = self.has_scope(required)
        
        if has_scope:
            return ScopeValidationResult(
                granted_scopes=self.scopes,
                required_scopes=required,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_8(self, required: TokenScope) -> ScopeValidationResult:
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
                required_scopes=required,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_9(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_10(self, required: TokenScope) -> ScopeValidationResult:
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
                )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_11(self, required: TokenScope) -> ScopeValidationResult:
        """Validate scope and return detailed result.
        
        Args:
            required: Required scope flags
            
        Returns:
            ScopeValidationResult with validation details
        """
        has_scope = self.has_scope(required)
        
        if has_scope:
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_12(self, required: TokenScope) -> ScopeValidationResult:
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
                message="XXScope validation successfulXX"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_13(self, required: TokenScope) -> ScopeValidationResult:
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
                message="scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_14(self, required: TokenScope) -> ScopeValidationResult:
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
                message="SCOPE VALIDATION SUCCESSFUL"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_15(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = None
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_16(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required | ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_17(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_18(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=None,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_19(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=None,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_20(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=None,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_21(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=None,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_22(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=None
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_23(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_24(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_25(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_26(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    def xǁScopeValidatorǁvalidate__mutmut_27(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=False,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                )
    
    def xǁScopeValidatorǁvalidate__mutmut_28(self, required: TokenScope) -> ScopeValidationResult:
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
                message="Scope validation successful"
            )
        else:
            missing = required & ~self.scopes
            return ScopeValidationResult(
                valid=True,
                granted_scopes=self.scopes,
                required_scopes=required,
                missing_scopes=missing,
                message=f"Missing scopes: {missing.to_strings()}"
            )
    
    xǁScopeValidatorǁvalidate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁScopeValidatorǁvalidate__mutmut_1': xǁScopeValidatorǁvalidate__mutmut_1, 
        'xǁScopeValidatorǁvalidate__mutmut_2': xǁScopeValidatorǁvalidate__mutmut_2, 
        'xǁScopeValidatorǁvalidate__mutmut_3': xǁScopeValidatorǁvalidate__mutmut_3, 
        'xǁScopeValidatorǁvalidate__mutmut_4': xǁScopeValidatorǁvalidate__mutmut_4, 
        'xǁScopeValidatorǁvalidate__mutmut_5': xǁScopeValidatorǁvalidate__mutmut_5, 
        'xǁScopeValidatorǁvalidate__mutmut_6': xǁScopeValidatorǁvalidate__mutmut_6, 
        'xǁScopeValidatorǁvalidate__mutmut_7': xǁScopeValidatorǁvalidate__mutmut_7, 
        'xǁScopeValidatorǁvalidate__mutmut_8': xǁScopeValidatorǁvalidate__mutmut_8, 
        'xǁScopeValidatorǁvalidate__mutmut_9': xǁScopeValidatorǁvalidate__mutmut_9, 
        'xǁScopeValidatorǁvalidate__mutmut_10': xǁScopeValidatorǁvalidate__mutmut_10, 
        'xǁScopeValidatorǁvalidate__mutmut_11': xǁScopeValidatorǁvalidate__mutmut_11, 
        'xǁScopeValidatorǁvalidate__mutmut_12': xǁScopeValidatorǁvalidate__mutmut_12, 
        'xǁScopeValidatorǁvalidate__mutmut_13': xǁScopeValidatorǁvalidate__mutmut_13, 
        'xǁScopeValidatorǁvalidate__mutmut_14': xǁScopeValidatorǁvalidate__mutmut_14, 
        'xǁScopeValidatorǁvalidate__mutmut_15': xǁScopeValidatorǁvalidate__mutmut_15, 
        'xǁScopeValidatorǁvalidate__mutmut_16': xǁScopeValidatorǁvalidate__mutmut_16, 
        'xǁScopeValidatorǁvalidate__mutmut_17': xǁScopeValidatorǁvalidate__mutmut_17, 
        'xǁScopeValidatorǁvalidate__mutmut_18': xǁScopeValidatorǁvalidate__mutmut_18, 
        'xǁScopeValidatorǁvalidate__mutmut_19': xǁScopeValidatorǁvalidate__mutmut_19, 
        'xǁScopeValidatorǁvalidate__mutmut_20': xǁScopeValidatorǁvalidate__mutmut_20, 
        'xǁScopeValidatorǁvalidate__mutmut_21': xǁScopeValidatorǁvalidate__mutmut_21, 
        'xǁScopeValidatorǁvalidate__mutmut_22': xǁScopeValidatorǁvalidate__mutmut_22, 
        'xǁScopeValidatorǁvalidate__mutmut_23': xǁScopeValidatorǁvalidate__mutmut_23, 
        'xǁScopeValidatorǁvalidate__mutmut_24': xǁScopeValidatorǁvalidate__mutmut_24, 
        'xǁScopeValidatorǁvalidate__mutmut_25': xǁScopeValidatorǁvalidate__mutmut_25, 
        'xǁScopeValidatorǁvalidate__mutmut_26': xǁScopeValidatorǁvalidate__mutmut_26, 
        'xǁScopeValidatorǁvalidate__mutmut_27': xǁScopeValidatorǁvalidate__mutmut_27, 
        'xǁScopeValidatorǁvalidate__mutmut_28': xǁScopeValidatorǁvalidate__mutmut_28
    }
    
    def validate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁScopeValidatorǁvalidate__mutmut_orig"), object.__getattribute__(self, "xǁScopeValidatorǁvalidate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate.__signature__ = _mutmut_signature(xǁScopeValidatorǁvalidate__mutmut_orig)
    xǁScopeValidatorǁvalidate__mutmut_orig.__name__ = 'xǁScopeValidatorǁvalidate'
    
    def get_granted_scopes(self) -> Set[str]:
        """Get set of granted scope strings.
        
        Returns:
            Set of scope strings
        """
        return self.scopes.to_strings()
