"""
Exceptions Module

This module provides functionality for exceptions.

Usage:
    from github.exceptions import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging
logger = logging.getLogger(__name__)
"""GitHub API exceptions."""

from typing import Optional
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


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""

    def xǁGitHubAPIErrorǁ__init____mutmut_orig(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def xǁGitHubAPIErrorǁ__init____mutmut_1(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(None)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def xǁGitHubAPIErrorǁ__init____mutmut_2(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = None
        self.status_code = status_code
        self.response_body = response_body

    def xǁGitHubAPIErrorǁ__init____mutmut_3(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = None
        self.response_body = response_body

    def xǁGitHubAPIErrorǁ__init____mutmut_4(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = None
    
    xǁGitHubAPIErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubAPIErrorǁ__init____mutmut_1': xǁGitHubAPIErrorǁ__init____mutmut_1, 
        'xǁGitHubAPIErrorǁ__init____mutmut_2': xǁGitHubAPIErrorǁ__init____mutmut_2, 
        'xǁGitHubAPIErrorǁ__init____mutmut_3': xǁGitHubAPIErrorǁ__init____mutmut_3, 
        'xǁGitHubAPIErrorǁ__init____mutmut_4': xǁGitHubAPIErrorǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubAPIErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁGitHubAPIErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁGitHubAPIErrorǁ__init____mutmut_orig)
    xǁGitHubAPIErrorǁ__init____mutmut_orig.__name__ = 'xǁGitHubAPIErrorǁ__init__'

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""

    def xǁRateLimitErrorǁ__init____mutmut_orig(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_1(
        self,
        message: str = "XXGitHub API rate limit exceededXX",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_2(
        self,
        message: str = "github api rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_3(
        self,
        message: str = "GITHUB API RATE LIMIT EXCEEDED",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_4(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 1,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_5(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(None, status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_6(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=None)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_7(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(status_code=403)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_8(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, )
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_9(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=404)
        self.reset_at = reset_at
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_10(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = None
        self.remaining = remaining

    def xǁRateLimitErrorǁ__init____mutmut_11(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_at: Optional[int] = None,
        remaining: int = 0,
    ):
        super().__init__(message, status_code=403)
        self.reset_at = reset_at
        self.remaining = None
    
    xǁRateLimitErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimitErrorǁ__init____mutmut_1': xǁRateLimitErrorǁ__init____mutmut_1, 
        'xǁRateLimitErrorǁ__init____mutmut_2': xǁRateLimitErrorǁ__init____mutmut_2, 
        'xǁRateLimitErrorǁ__init____mutmut_3': xǁRateLimitErrorǁ__init____mutmut_3, 
        'xǁRateLimitErrorǁ__init____mutmut_4': xǁRateLimitErrorǁ__init____mutmut_4, 
        'xǁRateLimitErrorǁ__init____mutmut_5': xǁRateLimitErrorǁ__init____mutmut_5, 
        'xǁRateLimitErrorǁ__init____mutmut_6': xǁRateLimitErrorǁ__init____mutmut_6, 
        'xǁRateLimitErrorǁ__init____mutmut_7': xǁRateLimitErrorǁ__init____mutmut_7, 
        'xǁRateLimitErrorǁ__init____mutmut_8': xǁRateLimitErrorǁ__init____mutmut_8, 
        'xǁRateLimitErrorǁ__init____mutmut_9': xǁRateLimitErrorǁ__init____mutmut_9, 
        'xǁRateLimitErrorǁ__init____mutmut_10': xǁRateLimitErrorǁ__init____mutmut_10, 
        'xǁRateLimitErrorǁ__init____mutmut_11': xǁRateLimitErrorǁ__init____mutmut_11
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimitErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRateLimitErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRateLimitErrorǁ__init____mutmut_orig)
    xǁRateLimitErrorǁ__init____mutmut_orig.__name__ = 'xǁRateLimitErrorǁ__init__'


class AuthenticationError(GitHubAPIError):
    """Raised when authentication fails."""

    def xǁAuthenticationErrorǁ__init____mutmut_orig(self, message: str = "GitHub authentication failed"):
        super().__init__(message, status_code=401)

    def xǁAuthenticationErrorǁ__init____mutmut_1(self, message: str = "XXGitHub authentication failedXX"):
        super().__init__(message, status_code=401)

    def xǁAuthenticationErrorǁ__init____mutmut_2(self, message: str = "github authentication failed"):
        super().__init__(message, status_code=401)

    def xǁAuthenticationErrorǁ__init____mutmut_3(self, message: str = "GITHUB AUTHENTICATION FAILED"):
        super().__init__(message, status_code=401)

    def xǁAuthenticationErrorǁ__init____mutmut_4(self, message: str = "GitHub authentication failed"):
        super().__init__(None, status_code=401)

    def xǁAuthenticationErrorǁ__init____mutmut_5(self, message: str = "GitHub authentication failed"):
        super().__init__(message, status_code=None)

    def xǁAuthenticationErrorǁ__init____mutmut_6(self, message: str = "GitHub authentication failed"):
        super().__init__(status_code=401)

    def xǁAuthenticationErrorǁ__init____mutmut_7(self, message: str = "GitHub authentication failed"):
        super().__init__(message, )

    def xǁAuthenticationErrorǁ__init____mutmut_8(self, message: str = "GitHub authentication failed"):
        super().__init__(message, status_code=402)
    
    xǁAuthenticationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthenticationErrorǁ__init____mutmut_1': xǁAuthenticationErrorǁ__init____mutmut_1, 
        'xǁAuthenticationErrorǁ__init____mutmut_2': xǁAuthenticationErrorǁ__init____mutmut_2, 
        'xǁAuthenticationErrorǁ__init____mutmut_3': xǁAuthenticationErrorǁ__init____mutmut_3, 
        'xǁAuthenticationErrorǁ__init____mutmut_4': xǁAuthenticationErrorǁ__init____mutmut_4, 
        'xǁAuthenticationErrorǁ__init____mutmut_5': xǁAuthenticationErrorǁ__init____mutmut_5, 
        'xǁAuthenticationErrorǁ__init____mutmut_6': xǁAuthenticationErrorǁ__init____mutmut_6, 
        'xǁAuthenticationErrorǁ__init____mutmut_7': xǁAuthenticationErrorǁ__init____mutmut_7, 
        'xǁAuthenticationErrorǁ__init____mutmut_8': xǁAuthenticationErrorǁ__init____mutmut_8
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthenticationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAuthenticationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAuthenticationErrorǁ__init____mutmut_orig)
    xǁAuthenticationErrorǁ__init____mutmut_orig.__name__ = 'xǁAuthenticationErrorǁ__init__'


class NotFoundError(GitHubAPIError):
    """Raised when a resource is not found."""

    def xǁNotFoundErrorǁ__init____mutmut_orig(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            status_code=404,
        )
        self.resource = resource
        self.identifier = identifier

    def xǁNotFoundErrorǁ__init____mutmut_1(self, resource: str, identifier: str):
        super().__init__(
            None,
            status_code=404,
        )
        self.resource = resource
        self.identifier = identifier

    def xǁNotFoundErrorǁ__init____mutmut_2(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            status_code=None,
        )
        self.resource = resource
        self.identifier = identifier

    def xǁNotFoundErrorǁ__init____mutmut_3(self, resource: str, identifier: str):
        super().__init__(
            status_code=404,
        )
        self.resource = resource
        self.identifier = identifier

    def xǁNotFoundErrorǁ__init____mutmut_4(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            )
        self.resource = resource
        self.identifier = identifier

    def xǁNotFoundErrorǁ__init____mutmut_5(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            status_code=405,
        )
        self.resource = resource
        self.identifier = identifier

    def xǁNotFoundErrorǁ__init____mutmut_6(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            status_code=404,
        )
        self.resource = None
        self.identifier = identifier

    def xǁNotFoundErrorǁ__init____mutmut_7(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            status_code=404,
        )
        self.resource = resource
        self.identifier = None
    
    xǁNotFoundErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNotFoundErrorǁ__init____mutmut_1': xǁNotFoundErrorǁ__init____mutmut_1, 
        'xǁNotFoundErrorǁ__init____mutmut_2': xǁNotFoundErrorǁ__init____mutmut_2, 
        'xǁNotFoundErrorǁ__init____mutmut_3': xǁNotFoundErrorǁ__init____mutmut_3, 
        'xǁNotFoundErrorǁ__init____mutmut_4': xǁNotFoundErrorǁ__init____mutmut_4, 
        'xǁNotFoundErrorǁ__init____mutmut_5': xǁNotFoundErrorǁ__init____mutmut_5, 
        'xǁNotFoundErrorǁ__init____mutmut_6': xǁNotFoundErrorǁ__init____mutmut_6, 
        'xǁNotFoundErrorǁ__init____mutmut_7': xǁNotFoundErrorǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNotFoundErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁNotFoundErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁNotFoundErrorǁ__init____mutmut_orig)
    xǁNotFoundErrorǁ__init____mutmut_orig.__name__ = 'xǁNotFoundErrorǁ__init__'


class WorkflowTriggerError(GitHubAPIError):
    """Raised when workflow trigger fails."""

    def xǁWorkflowTriggerErrorǁ__init____mutmut_orig(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            f"Failed to trigger workflow '{workflow}': {reason}",
            status_code=status_code,
        )
        self.workflow = workflow
        self.reason = reason

    def xǁWorkflowTriggerErrorǁ__init____mutmut_1(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            None,
            status_code=status_code,
        )
        self.workflow = workflow
        self.reason = reason

    def xǁWorkflowTriggerErrorǁ__init____mutmut_2(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            f"Failed to trigger workflow '{workflow}': {reason}",
            status_code=None,
        )
        self.workflow = workflow
        self.reason = reason

    def xǁWorkflowTriggerErrorǁ__init____mutmut_3(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            status_code=status_code,
        )
        self.workflow = workflow
        self.reason = reason

    def xǁWorkflowTriggerErrorǁ__init____mutmut_4(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            f"Failed to trigger workflow '{workflow}': {reason}",
            )
        self.workflow = workflow
        self.reason = reason

    def xǁWorkflowTriggerErrorǁ__init____mutmut_5(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            f"Failed to trigger workflow '{workflow}': {reason}",
            status_code=status_code,
        )
        self.workflow = None
        self.reason = reason

    def xǁWorkflowTriggerErrorǁ__init____mutmut_6(
        self,
        workflow: str,
        reason: str,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            f"Failed to trigger workflow '{workflow}': {reason}",
            status_code=status_code,
        )
        self.workflow = workflow
        self.reason = None
    
    xǁWorkflowTriggerErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWorkflowTriggerErrorǁ__init____mutmut_1': xǁWorkflowTriggerErrorǁ__init____mutmut_1, 
        'xǁWorkflowTriggerErrorǁ__init____mutmut_2': xǁWorkflowTriggerErrorǁ__init____mutmut_2, 
        'xǁWorkflowTriggerErrorǁ__init____mutmut_3': xǁWorkflowTriggerErrorǁ__init____mutmut_3, 
        'xǁWorkflowTriggerErrorǁ__init____mutmut_4': xǁWorkflowTriggerErrorǁ__init____mutmut_4, 
        'xǁWorkflowTriggerErrorǁ__init____mutmut_5': xǁWorkflowTriggerErrorǁ__init____mutmut_5, 
        'xǁWorkflowTriggerErrorǁ__init____mutmut_6': xǁWorkflowTriggerErrorǁ__init____mutmut_6
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWorkflowTriggerErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁWorkflowTriggerErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁWorkflowTriggerErrorǁ__init____mutmut_orig)
    xǁWorkflowTriggerErrorǁ__init____mutmut_orig.__name__ = 'xǁWorkflowTriggerErrorǁ__init__'


class ValidationError(GitHubAPIError):
    """Raised when request validation fails."""

    def xǁValidationErrorǁ__init____mutmut_orig(self, message: str, errors: Optional[list] = None):
        super().__init__(message, status_code=422)
        self.errors = errors or []

    def xǁValidationErrorǁ__init____mutmut_1(self, message: str, errors: Optional[list] = None):
        super().__init__(None, status_code=422)
        self.errors = errors or []

    def xǁValidationErrorǁ__init____mutmut_2(self, message: str, errors: Optional[list] = None):
        super().__init__(message, status_code=None)
        self.errors = errors or []

    def xǁValidationErrorǁ__init____mutmut_3(self, message: str, errors: Optional[list] = None):
        super().__init__(status_code=422)
        self.errors = errors or []

    def xǁValidationErrorǁ__init____mutmut_4(self, message: str, errors: Optional[list] = None):
        super().__init__(message, )
        self.errors = errors or []

    def xǁValidationErrorǁ__init____mutmut_5(self, message: str, errors: Optional[list] = None):
        super().__init__(message, status_code=423)
        self.errors = errors or []

    def xǁValidationErrorǁ__init____mutmut_6(self, message: str, errors: Optional[list] = None):
        super().__init__(message, status_code=422)
        self.errors = None

    def xǁValidationErrorǁ__init____mutmut_7(self, message: str, errors: Optional[list] = None):
        super().__init__(message, status_code=422)
        self.errors = errors and []
    
    xǁValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁValidationErrorǁ__init____mutmut_1': xǁValidationErrorǁ__init____mutmut_1, 
        'xǁValidationErrorǁ__init____mutmut_2': xǁValidationErrorǁ__init____mutmut_2, 
        'xǁValidationErrorǁ__init____mutmut_3': xǁValidationErrorǁ__init____mutmut_3, 
        'xǁValidationErrorǁ__init____mutmut_4': xǁValidationErrorǁ__init____mutmut_4, 
        'xǁValidationErrorǁ__init____mutmut_5': xǁValidationErrorǁ__init____mutmut_5, 
        'xǁValidationErrorǁ__init____mutmut_6': xǁValidationErrorǁ__init____mutmut_6, 
        'xǁValidationErrorǁ__init____mutmut_7': xǁValidationErrorǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁValidationErrorǁ__init____mutmut_orig)
    xǁValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁValidationErrorǁ__init__'
