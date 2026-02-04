"""GitHub API Client implementation.

Provides async-friendly wrapper around GitHub REST API for workflow operations.
Includes retry logic, rate limit handling, and typed responses.
"""

import asyncio
import logging
logger = logging.getLogger(__name__)
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional, Union

import httpx

from .exceptions import (
    AuthenticationError,
    GitHubAPIError,
    NotFoundError,
    RateLimitError,
    WorkflowTriggerError,
)
from .types import (
    ArtifactInfo,
    CheckRun,
    CheckRunStatus,
    ListArtifactsResponse,
    ListCheckRunsResponse,
    ListWorkflowJobsResponse,
    ListWorkflowRunsResponse,
    RateLimitInfo,
    RunStatus,
    WorkflowInfo,
    WorkflowJob,
    WorkflowRun,
)
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


class GitHubClient:
    """GitHub API client for workflow operations.

    Provides typed, async-friendly methods for:
    - Listing and triggering workflows
    - Monitoring workflow runs
    - Retrieving job logs and artifacts
    - Rate limit handling with exponential backoff

    Example:
        ```python
        client = GitHubClient()
        
        # list workflows
        workflows = await client.list_workflows("owner", "repo")
        
        # Trigger a workflow
        run_id = await client.trigger_workflow(
            "owner", "repo", "ci.yml",
            ref="main",
            inputs={"environment": "staging"}
        )
        
        # Monitor status
        run = await client.get_workflow_run("owner", "repo", run_id)
        print(f"Status: {run.status}, Conclusion: {run.conclusion}")
        ```
    """

    DEFAULT_BASE_URL = "https://api.github.com"
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 2.0

    def xǁGitHubClientǁ__init____mutmut_orig(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_1(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = None
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_2(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token and os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_3(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get(None, "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_4(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", None)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_5(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_6(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_7(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("XXGITHUB_TOKENXX", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_8(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("github_token", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_9(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "XXXX")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_10(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = None
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_11(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip(None)
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_12(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.lstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_13(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip("XX/XX")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_14(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = None
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_15(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = None
        self._rate_limit: Optional[RateLimitInfo] = None

    def xǁGitHubClientǁ__init____mutmut_16(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token or app token.
                   Defaults to GITHUB_TOKEN environment variable.
            base_url: GitHub API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = ""
    
    xǁGitHubClientǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁ__init____mutmut_1': xǁGitHubClientǁ__init____mutmut_1, 
        'xǁGitHubClientǁ__init____mutmut_2': xǁGitHubClientǁ__init____mutmut_2, 
        'xǁGitHubClientǁ__init____mutmut_3': xǁGitHubClientǁ__init____mutmut_3, 
        'xǁGitHubClientǁ__init____mutmut_4': xǁGitHubClientǁ__init____mutmut_4, 
        'xǁGitHubClientǁ__init____mutmut_5': xǁGitHubClientǁ__init____mutmut_5, 
        'xǁGitHubClientǁ__init____mutmut_6': xǁGitHubClientǁ__init____mutmut_6, 
        'xǁGitHubClientǁ__init____mutmut_7': xǁGitHubClientǁ__init____mutmut_7, 
        'xǁGitHubClientǁ__init____mutmut_8': xǁGitHubClientǁ__init____mutmut_8, 
        'xǁGitHubClientǁ__init____mutmut_9': xǁGitHubClientǁ__init____mutmut_9, 
        'xǁGitHubClientǁ__init____mutmut_10': xǁGitHubClientǁ__init____mutmut_10, 
        'xǁGitHubClientǁ__init____mutmut_11': xǁGitHubClientǁ__init____mutmut_11, 
        'xǁGitHubClientǁ__init____mutmut_12': xǁGitHubClientǁ__init____mutmut_12, 
        'xǁGitHubClientǁ__init____mutmut_13': xǁGitHubClientǁ__init____mutmut_13, 
        'xǁGitHubClientǁ__init____mutmut_14': xǁGitHubClientǁ__init____mutmut_14, 
        'xǁGitHubClientǁ__init____mutmut_15': xǁGitHubClientǁ__init____mutmut_15, 
        'xǁGitHubClientǁ__init____mutmut_16': xǁGitHubClientǁ__init____mutmut_16
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁGitHubClientǁ__init____mutmut_orig)
    xǁGitHubClientǁ__init____mutmut_orig.__name__ = 'xǁGitHubClientǁ__init__'

    def xǁGitHubClientǁ_get_headers__mutmut_orig(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_1(self) -> dict[str, str]:
        """Get request headers."""
        headers = None
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_2(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "XXAcceptXX": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_3(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_4(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "ACCEPT": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_5(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "XXapplication/vnd.github+jsonXX",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_6(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "APPLICATION/VND.GITHUB+JSON",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_7(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "XXX-GitHub-Api-VersionXX": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_8(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "x-github-api-version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_9(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GITHUB-API-VERSION": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_10(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "XX2022-11-28XX",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_11(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = None
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_12(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["XXAuthorizationXX"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_13(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["authorization"] = f"Bearer {self.token}"
        return headers

    def xǁGitHubClientǁ_get_headers__mutmut_14(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["AUTHORIZATION"] = f"Bearer {self.token}"
        return headers
    
    xǁGitHubClientǁ_get_headers__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁ_get_headers__mutmut_1': xǁGitHubClientǁ_get_headers__mutmut_1, 
        'xǁGitHubClientǁ_get_headers__mutmut_2': xǁGitHubClientǁ_get_headers__mutmut_2, 
        'xǁGitHubClientǁ_get_headers__mutmut_3': xǁGitHubClientǁ_get_headers__mutmut_3, 
        'xǁGitHubClientǁ_get_headers__mutmut_4': xǁGitHubClientǁ_get_headers__mutmut_4, 
        'xǁGitHubClientǁ_get_headers__mutmut_5': xǁGitHubClientǁ_get_headers__mutmut_5, 
        'xǁGitHubClientǁ_get_headers__mutmut_6': xǁGitHubClientǁ_get_headers__mutmut_6, 
        'xǁGitHubClientǁ_get_headers__mutmut_7': xǁGitHubClientǁ_get_headers__mutmut_7, 
        'xǁGitHubClientǁ_get_headers__mutmut_8': xǁGitHubClientǁ_get_headers__mutmut_8, 
        'xǁGitHubClientǁ_get_headers__mutmut_9': xǁGitHubClientǁ_get_headers__mutmut_9, 
        'xǁGitHubClientǁ_get_headers__mutmut_10': xǁGitHubClientǁ_get_headers__mutmut_10, 
        'xǁGitHubClientǁ_get_headers__mutmut_11': xǁGitHubClientǁ_get_headers__mutmut_11, 
        'xǁGitHubClientǁ_get_headers__mutmut_12': xǁGitHubClientǁ_get_headers__mutmut_12, 
        'xǁGitHubClientǁ_get_headers__mutmut_13': xǁGitHubClientǁ_get_headers__mutmut_13, 
        'xǁGitHubClientǁ_get_headers__mutmut_14': xǁGitHubClientǁ_get_headers__mutmut_14
    }
    
    def _get_headers(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁ_get_headers__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁ_get_headers__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_headers.__signature__ = _mutmut_signature(xǁGitHubClientǁ_get_headers__mutmut_orig)
    xǁGitHubClientǁ_get_headers__mutmut_orig.__name__ = 'xǁGitHubClientǁ_get_headers'

    def xǁGitHubClientǁ_create_client__mutmut_orig(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=self.timeout,
        )

    def xǁGitHubClientǁ_create_client__mutmut_1(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            base_url=None,
            headers=self._get_headers(),
            timeout=self.timeout,
        )

    def xǁGitHubClientǁ_create_client__mutmut_2(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=None,
            timeout=self.timeout,
        )

    def xǁGitHubClientǁ_create_client__mutmut_3(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=None,
        )

    def xǁGitHubClientǁ_create_client__mutmut_4(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            headers=self._get_headers(),
            timeout=self.timeout,
        )

    def xǁGitHubClientǁ_create_client__mutmut_5(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def xǁGitHubClientǁ_create_client__mutmut_6(self) -> httpx.AsyncClient:
        """Create async HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            )
    
    xǁGitHubClientǁ_create_client__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁ_create_client__mutmut_1': xǁGitHubClientǁ_create_client__mutmut_1, 
        'xǁGitHubClientǁ_create_client__mutmut_2': xǁGitHubClientǁ_create_client__mutmut_2, 
        'xǁGitHubClientǁ_create_client__mutmut_3': xǁGitHubClientǁ_create_client__mutmut_3, 
        'xǁGitHubClientǁ_create_client__mutmut_4': xǁGitHubClientǁ_create_client__mutmut_4, 
        'xǁGitHubClientǁ_create_client__mutmut_5': xǁGitHubClientǁ_create_client__mutmut_5, 
        'xǁGitHubClientǁ_create_client__mutmut_6': xǁGitHubClientǁ_create_client__mutmut_6
    }
    
    def _create_client(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁ_create_client__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁ_create_client__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _create_client.__signature__ = _mutmut_signature(xǁGitHubClientǁ_create_client__mutmut_orig)
    xǁGitHubClientǁ_create_client__mutmut_orig.__name__ = 'xǁGitHubClientǁ_create_client'

    def xǁGitHubClientǁ_update_rate_limit__mutmut_orig(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_1(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = None
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_2(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(None)
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_3(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get(None, 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_4(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", None))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_5(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get(0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_6(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", ))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_7(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("XXx-ratelimit-limitXX", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_8(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("X-RATELIMIT-LIMIT", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_9(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 1))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_10(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = None
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_11(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(None)
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_12(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get(None, 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_13(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", None))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_14(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get(0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_15(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", ))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_16(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("XXx-ratelimit-remainingXX", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_17(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("X-RATELIMIT-REMAINING", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_18(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 1))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_19(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = None
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_20(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(None)
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_21(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get(None, 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_22(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", None))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_23(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get(0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_24(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", ))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_25(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("XXx-ratelimit-resetXX", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_26(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("X-RATELIMIT-RESET", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_27(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 1))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_28(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = None

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_29(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(None)

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_30(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get(None, 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_31(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", None))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_32(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get(0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_33(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", ))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_34(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("XXx-ratelimit-usedXX", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_35(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("X-RATELIMIT-USED", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_36(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 1))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_37(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit >= 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_38(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 1:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_39(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = None
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_40(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=None,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_41(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=None,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_42(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=None,
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_43(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=None,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_44(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_45(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_46(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_47(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_48(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(None, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_49(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=None),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_50(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_51(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, ),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = None
            return

    def xǁGitHubClientǁ_update_rate_limit__mutmut_52(self, headers: httpx.Headers) -> None:
        """Update rate limit info from response headers."""
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset_ts = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))

            if limit > 0:
                self._rate_limit = RateLimitInfo(
                    limit=limit,
                    remaining=remaining,
                    reset=datetime.fromtimestamp(reset_ts, tz=timezone.utc),
                    used=used,
                )
        except (ValueError, TypeError):
            # Ignore malformed rate limit headers - rate limiting will be unavailable
            # but the API request can still proceed. This is not a critical error.
            self._rate_limit = ""
            return
    
    xǁGitHubClientǁ_update_rate_limit__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁ_update_rate_limit__mutmut_1': xǁGitHubClientǁ_update_rate_limit__mutmut_1, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_2': xǁGitHubClientǁ_update_rate_limit__mutmut_2, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_3': xǁGitHubClientǁ_update_rate_limit__mutmut_3, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_4': xǁGitHubClientǁ_update_rate_limit__mutmut_4, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_5': xǁGitHubClientǁ_update_rate_limit__mutmut_5, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_6': xǁGitHubClientǁ_update_rate_limit__mutmut_6, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_7': xǁGitHubClientǁ_update_rate_limit__mutmut_7, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_8': xǁGitHubClientǁ_update_rate_limit__mutmut_8, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_9': xǁGitHubClientǁ_update_rate_limit__mutmut_9, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_10': xǁGitHubClientǁ_update_rate_limit__mutmut_10, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_11': xǁGitHubClientǁ_update_rate_limit__mutmut_11, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_12': xǁGitHubClientǁ_update_rate_limit__mutmut_12, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_13': xǁGitHubClientǁ_update_rate_limit__mutmut_13, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_14': xǁGitHubClientǁ_update_rate_limit__mutmut_14, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_15': xǁGitHubClientǁ_update_rate_limit__mutmut_15, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_16': xǁGitHubClientǁ_update_rate_limit__mutmut_16, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_17': xǁGitHubClientǁ_update_rate_limit__mutmut_17, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_18': xǁGitHubClientǁ_update_rate_limit__mutmut_18, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_19': xǁGitHubClientǁ_update_rate_limit__mutmut_19, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_20': xǁGitHubClientǁ_update_rate_limit__mutmut_20, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_21': xǁGitHubClientǁ_update_rate_limit__mutmut_21, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_22': xǁGitHubClientǁ_update_rate_limit__mutmut_22, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_23': xǁGitHubClientǁ_update_rate_limit__mutmut_23, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_24': xǁGitHubClientǁ_update_rate_limit__mutmut_24, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_25': xǁGitHubClientǁ_update_rate_limit__mutmut_25, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_26': xǁGitHubClientǁ_update_rate_limit__mutmut_26, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_27': xǁGitHubClientǁ_update_rate_limit__mutmut_27, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_28': xǁGitHubClientǁ_update_rate_limit__mutmut_28, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_29': xǁGitHubClientǁ_update_rate_limit__mutmut_29, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_30': xǁGitHubClientǁ_update_rate_limit__mutmut_30, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_31': xǁGitHubClientǁ_update_rate_limit__mutmut_31, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_32': xǁGitHubClientǁ_update_rate_limit__mutmut_32, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_33': xǁGitHubClientǁ_update_rate_limit__mutmut_33, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_34': xǁGitHubClientǁ_update_rate_limit__mutmut_34, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_35': xǁGitHubClientǁ_update_rate_limit__mutmut_35, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_36': xǁGitHubClientǁ_update_rate_limit__mutmut_36, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_37': xǁGitHubClientǁ_update_rate_limit__mutmut_37, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_38': xǁGitHubClientǁ_update_rate_limit__mutmut_38, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_39': xǁGitHubClientǁ_update_rate_limit__mutmut_39, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_40': xǁGitHubClientǁ_update_rate_limit__mutmut_40, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_41': xǁGitHubClientǁ_update_rate_limit__mutmut_41, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_42': xǁGitHubClientǁ_update_rate_limit__mutmut_42, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_43': xǁGitHubClientǁ_update_rate_limit__mutmut_43, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_44': xǁGitHubClientǁ_update_rate_limit__mutmut_44, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_45': xǁGitHubClientǁ_update_rate_limit__mutmut_45, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_46': xǁGitHubClientǁ_update_rate_limit__mutmut_46, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_47': xǁGitHubClientǁ_update_rate_limit__mutmut_47, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_48': xǁGitHubClientǁ_update_rate_limit__mutmut_48, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_49': xǁGitHubClientǁ_update_rate_limit__mutmut_49, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_50': xǁGitHubClientǁ_update_rate_limit__mutmut_50, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_51': xǁGitHubClientǁ_update_rate_limit__mutmut_51, 
        'xǁGitHubClientǁ_update_rate_limit__mutmut_52': xǁGitHubClientǁ_update_rate_limit__mutmut_52
    }
    
    def _update_rate_limit(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁ_update_rate_limit__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁ_update_rate_limit__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _update_rate_limit.__signature__ = _mutmut_signature(xǁGitHubClientǁ_update_rate_limit__mutmut_orig)
    xǁGitHubClientǁ_update_rate_limit__mutmut_orig.__name__ = 'xǁGitHubClientǁ_update_rate_limit'

    async def xǁGitHubClientǁ_request__mutmut_orig(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_1(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 1,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_2(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = None
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_3(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    None,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_4(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    None,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_5(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=None,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_6(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=None,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_7(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_8(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_9(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_10(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_11(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(None)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_12(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code != 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_13(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 404:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_14(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "XXrate limitXX" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_15(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "RATE LIMIT" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_16(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" not in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_17(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.upper():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_18(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = None
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_19(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            None
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_20(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get(None, 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_21(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", None)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_22(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get(0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_23(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", )
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_24(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("XXx-ratelimit-resetXX", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_25(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("X-RATELIMIT-RESET", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_26(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 1)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_27(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=None,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_28(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=None,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_29(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_30(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_31(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=1,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_32(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code != 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_33(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 402:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_34(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code != 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_35(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 405:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_36(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError(None, path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_37(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", None)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_38(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError(path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_39(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", )

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_40(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("XXresourceXX", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_41(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("RESOURCE", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_42(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code > 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_43(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 401:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_44(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=None,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_45(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=None,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_46(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=None,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_47(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_48(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_49(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_50(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count <= self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_51(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = None
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_52(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE * retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_53(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(None)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_54(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        None, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_55(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, None, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_56(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, None, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_57(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, None, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_58(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, None
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_59(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_60(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, json, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_61(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, params, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_62(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, retry_count + 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_63(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_64(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count - 1
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_65(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 2
                    )
                raise GitHubAPIError(f"Request failed: {e}")

    async def xǁGitHubClientǁ_request__mutmut_66(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make API request with retry logic.

        Args:
            method: HTTP method.
            path: API path.
            json: JSON body.
            params: Query parameters.
            retry_count: Current retry attempt.

        Returns:
            HTTP response.

        Raises:
            GitHubAPIError: On API errors.
            RateLimitError: When rate limit exceeded.
            AuthenticationError: On auth failure.
        """
        async with self._create_client() as client:
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                self._update_rate_limit(response.headers)

                # Handle rate limiting
                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        reset_at = int(
                            response.headers.get("x-ratelimit-reset", 0)
                        )
                        raise RateLimitError(
                            reset_at=reset_at,
                            remaining=0,
                        )

                # Handle auth errors
                if response.status_code == 401:
                    raise AuthenticationError()

                # Handle not found
                if response.status_code == 404:
                    raise NotFoundError("resource", path)

                # Handle other errors
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        message=response.text,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                return response

            except httpx.RequestError as e:
                if retry_count < self.max_retries:
                    wait_time = self.RETRY_BACKOFF_BASE ** retry_count
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, path, json, params, retry_count + 1
                    )
                raise GitHubAPIError(None)
    
    xǁGitHubClientǁ_request__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁ_request__mutmut_1': xǁGitHubClientǁ_request__mutmut_1, 
        'xǁGitHubClientǁ_request__mutmut_2': xǁGitHubClientǁ_request__mutmut_2, 
        'xǁGitHubClientǁ_request__mutmut_3': xǁGitHubClientǁ_request__mutmut_3, 
        'xǁGitHubClientǁ_request__mutmut_4': xǁGitHubClientǁ_request__mutmut_4, 
        'xǁGitHubClientǁ_request__mutmut_5': xǁGitHubClientǁ_request__mutmut_5, 
        'xǁGitHubClientǁ_request__mutmut_6': xǁGitHubClientǁ_request__mutmut_6, 
        'xǁGitHubClientǁ_request__mutmut_7': xǁGitHubClientǁ_request__mutmut_7, 
        'xǁGitHubClientǁ_request__mutmut_8': xǁGitHubClientǁ_request__mutmut_8, 
        'xǁGitHubClientǁ_request__mutmut_9': xǁGitHubClientǁ_request__mutmut_9, 
        'xǁGitHubClientǁ_request__mutmut_10': xǁGitHubClientǁ_request__mutmut_10, 
        'xǁGitHubClientǁ_request__mutmut_11': xǁGitHubClientǁ_request__mutmut_11, 
        'xǁGitHubClientǁ_request__mutmut_12': xǁGitHubClientǁ_request__mutmut_12, 
        'xǁGitHubClientǁ_request__mutmut_13': xǁGitHubClientǁ_request__mutmut_13, 
        'xǁGitHubClientǁ_request__mutmut_14': xǁGitHubClientǁ_request__mutmut_14, 
        'xǁGitHubClientǁ_request__mutmut_15': xǁGitHubClientǁ_request__mutmut_15, 
        'xǁGitHubClientǁ_request__mutmut_16': xǁGitHubClientǁ_request__mutmut_16, 
        'xǁGitHubClientǁ_request__mutmut_17': xǁGitHubClientǁ_request__mutmut_17, 
        'xǁGitHubClientǁ_request__mutmut_18': xǁGitHubClientǁ_request__mutmut_18, 
        'xǁGitHubClientǁ_request__mutmut_19': xǁGitHubClientǁ_request__mutmut_19, 
        'xǁGitHubClientǁ_request__mutmut_20': xǁGitHubClientǁ_request__mutmut_20, 
        'xǁGitHubClientǁ_request__mutmut_21': xǁGitHubClientǁ_request__mutmut_21, 
        'xǁGitHubClientǁ_request__mutmut_22': xǁGitHubClientǁ_request__mutmut_22, 
        'xǁGitHubClientǁ_request__mutmut_23': xǁGitHubClientǁ_request__mutmut_23, 
        'xǁGitHubClientǁ_request__mutmut_24': xǁGitHubClientǁ_request__mutmut_24, 
        'xǁGitHubClientǁ_request__mutmut_25': xǁGitHubClientǁ_request__mutmut_25, 
        'xǁGitHubClientǁ_request__mutmut_26': xǁGitHubClientǁ_request__mutmut_26, 
        'xǁGitHubClientǁ_request__mutmut_27': xǁGitHubClientǁ_request__mutmut_27, 
        'xǁGitHubClientǁ_request__mutmut_28': xǁGitHubClientǁ_request__mutmut_28, 
        'xǁGitHubClientǁ_request__mutmut_29': xǁGitHubClientǁ_request__mutmut_29, 
        'xǁGitHubClientǁ_request__mutmut_30': xǁGitHubClientǁ_request__mutmut_30, 
        'xǁGitHubClientǁ_request__mutmut_31': xǁGitHubClientǁ_request__mutmut_31, 
        'xǁGitHubClientǁ_request__mutmut_32': xǁGitHubClientǁ_request__mutmut_32, 
        'xǁGitHubClientǁ_request__mutmut_33': xǁGitHubClientǁ_request__mutmut_33, 
        'xǁGitHubClientǁ_request__mutmut_34': xǁGitHubClientǁ_request__mutmut_34, 
        'xǁGitHubClientǁ_request__mutmut_35': xǁGitHubClientǁ_request__mutmut_35, 
        'xǁGitHubClientǁ_request__mutmut_36': xǁGitHubClientǁ_request__mutmut_36, 
        'xǁGitHubClientǁ_request__mutmut_37': xǁGitHubClientǁ_request__mutmut_37, 
        'xǁGitHubClientǁ_request__mutmut_38': xǁGitHubClientǁ_request__mutmut_38, 
        'xǁGitHubClientǁ_request__mutmut_39': xǁGitHubClientǁ_request__mutmut_39, 
        'xǁGitHubClientǁ_request__mutmut_40': xǁGitHubClientǁ_request__mutmut_40, 
        'xǁGitHubClientǁ_request__mutmut_41': xǁGitHubClientǁ_request__mutmut_41, 
        'xǁGitHubClientǁ_request__mutmut_42': xǁGitHubClientǁ_request__mutmut_42, 
        'xǁGitHubClientǁ_request__mutmut_43': xǁGitHubClientǁ_request__mutmut_43, 
        'xǁGitHubClientǁ_request__mutmut_44': xǁGitHubClientǁ_request__mutmut_44, 
        'xǁGitHubClientǁ_request__mutmut_45': xǁGitHubClientǁ_request__mutmut_45, 
        'xǁGitHubClientǁ_request__mutmut_46': xǁGitHubClientǁ_request__mutmut_46, 
        'xǁGitHubClientǁ_request__mutmut_47': xǁGitHubClientǁ_request__mutmut_47, 
        'xǁGitHubClientǁ_request__mutmut_48': xǁGitHubClientǁ_request__mutmut_48, 
        'xǁGitHubClientǁ_request__mutmut_49': xǁGitHubClientǁ_request__mutmut_49, 
        'xǁGitHubClientǁ_request__mutmut_50': xǁGitHubClientǁ_request__mutmut_50, 
        'xǁGitHubClientǁ_request__mutmut_51': xǁGitHubClientǁ_request__mutmut_51, 
        'xǁGitHubClientǁ_request__mutmut_52': xǁGitHubClientǁ_request__mutmut_52, 
        'xǁGitHubClientǁ_request__mutmut_53': xǁGitHubClientǁ_request__mutmut_53, 
        'xǁGitHubClientǁ_request__mutmut_54': xǁGitHubClientǁ_request__mutmut_54, 
        'xǁGitHubClientǁ_request__mutmut_55': xǁGitHubClientǁ_request__mutmut_55, 
        'xǁGitHubClientǁ_request__mutmut_56': xǁGitHubClientǁ_request__mutmut_56, 
        'xǁGitHubClientǁ_request__mutmut_57': xǁGitHubClientǁ_request__mutmut_57, 
        'xǁGitHubClientǁ_request__mutmut_58': xǁGitHubClientǁ_request__mutmut_58, 
        'xǁGitHubClientǁ_request__mutmut_59': xǁGitHubClientǁ_request__mutmut_59, 
        'xǁGitHubClientǁ_request__mutmut_60': xǁGitHubClientǁ_request__mutmut_60, 
        'xǁGitHubClientǁ_request__mutmut_61': xǁGitHubClientǁ_request__mutmut_61, 
        'xǁGitHubClientǁ_request__mutmut_62': xǁGitHubClientǁ_request__mutmut_62, 
        'xǁGitHubClientǁ_request__mutmut_63': xǁGitHubClientǁ_request__mutmut_63, 
        'xǁGitHubClientǁ_request__mutmut_64': xǁGitHubClientǁ_request__mutmut_64, 
        'xǁGitHubClientǁ_request__mutmut_65': xǁGitHubClientǁ_request__mutmut_65, 
        'xǁGitHubClientǁ_request__mutmut_66': xǁGitHubClientǁ_request__mutmut_66
    }
    
    def _request(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁ_request__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁ_request__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _request.__signature__ = _mutmut_signature(xǁGitHubClientǁ_request__mutmut_orig)
    xǁGitHubClientǁ_request__mutmut_orig.__name__ = 'xǁGitHubClientǁ_request'

    async def xǁGitHubClientǁ_get__mutmut_orig(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("GET", path, params=params)
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_1(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = None
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_2(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request(None, path, params=params)
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_3(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("GET", None, params=params)
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_4(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("GET", path, params=None)
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_5(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request(path, params=params)
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_6(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("GET", params=params)
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_7(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("GET", path, )
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_8(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("XXGETXX", path, params=params)
        return response.json()

    async def xǁGitHubClientǁ_get__mutmut_9(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        response = await self._request("get", path, params=params)
        return response.json()
    
    xǁGitHubClientǁ_get__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁ_get__mutmut_1': xǁGitHubClientǁ_get__mutmut_1, 
        'xǁGitHubClientǁ_get__mutmut_2': xǁGitHubClientǁ_get__mutmut_2, 
        'xǁGitHubClientǁ_get__mutmut_3': xǁGitHubClientǁ_get__mutmut_3, 
        'xǁGitHubClientǁ_get__mutmut_4': xǁGitHubClientǁ_get__mutmut_4, 
        'xǁGitHubClientǁ_get__mutmut_5': xǁGitHubClientǁ_get__mutmut_5, 
        'xǁGitHubClientǁ_get__mutmut_6': xǁGitHubClientǁ_get__mutmut_6, 
        'xǁGitHubClientǁ_get__mutmut_7': xǁGitHubClientǁ_get__mutmut_7, 
        'xǁGitHubClientǁ_get__mutmut_8': xǁGitHubClientǁ_get__mutmut_8, 
        'xǁGitHubClientǁ_get__mutmut_9': xǁGitHubClientǁ_get__mutmut_9
    }
    
    def _get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁ_get__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁ_get__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get.__signature__ = _mutmut_signature(xǁGitHubClientǁ_get__mutmut_orig)
    xǁGitHubClientǁ_get__mutmut_orig.__name__ = 'xǁGitHubClientǁ_get'

    async def xǁGitHubClientǁ_post__mutmut_orig(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", path, json=json)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_1(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = None
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_2(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request(None, path, json=json)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_3(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", None, json=json)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_4(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", path, json=None)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_5(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request(path, json=json)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_6(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", json=json)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_7(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", path, )
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_8(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("XXPOSTXX", path, json=json)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_9(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("post", path, json=json)
        if response.status_code == 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_10(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", path, json=json)
        if response.status_code != 204:
            return None
        return response.json()

    async def xǁGitHubClientǁ_post__mutmut_11(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Make POST request."""
        response = await self._request("POST", path, json=json)
        if response.status_code == 205:
            return None
        return response.json()
    
    xǁGitHubClientǁ_post__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁ_post__mutmut_1': xǁGitHubClientǁ_post__mutmut_1, 
        'xǁGitHubClientǁ_post__mutmut_2': xǁGitHubClientǁ_post__mutmut_2, 
        'xǁGitHubClientǁ_post__mutmut_3': xǁGitHubClientǁ_post__mutmut_3, 
        'xǁGitHubClientǁ_post__mutmut_4': xǁGitHubClientǁ_post__mutmut_4, 
        'xǁGitHubClientǁ_post__mutmut_5': xǁGitHubClientǁ_post__mutmut_5, 
        'xǁGitHubClientǁ_post__mutmut_6': xǁGitHubClientǁ_post__mutmut_6, 
        'xǁGitHubClientǁ_post__mutmut_7': xǁGitHubClientǁ_post__mutmut_7, 
        'xǁGitHubClientǁ_post__mutmut_8': xǁGitHubClientǁ_post__mutmut_8, 
        'xǁGitHubClientǁ_post__mutmut_9': xǁGitHubClientǁ_post__mutmut_9, 
        'xǁGitHubClientǁ_post__mutmut_10': xǁGitHubClientǁ_post__mutmut_10, 
        'xǁGitHubClientǁ_post__mutmut_11': xǁGitHubClientǁ_post__mutmut_11
    }
    
    def _post(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁ_post__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁ_post__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _post.__signature__ = _mutmut_signature(xǁGitHubClientǁ_post__mutmut_orig)
    xǁGitHubClientǁ_post__mutmut_orig.__name__ = 'xǁGitHubClientǁ_post'

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_orig(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_1(
        self,
        owner: str,
        repo: str,
        per_page: int = 31,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_2(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 2,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_3(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = None
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_4(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            None,
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_5(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params=None,
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_6(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_7(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_8(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"XXper_pageXX": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_9(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"PER_PAGE": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_10(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "XXpageXX": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_11(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "PAGE": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_12(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get(None, [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_13(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", None)]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_14(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get([])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_15(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("workflows", )]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_16(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("XXworkflowsXX", [])]

    # =========================================================================
    # Workflow Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflows__mutmut_17(
        self,
        owner: str,
        repo: str,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowInfo]:
        """list repository workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            list of workflow info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows",
            params={"per_page": per_page, "page": page},
        )
        return [WorkflowInfo(**w) for w in data.get("WORKFLOWS", [])]
    
    xǁGitHubClientǁlist_workflows__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁlist_workflows__mutmut_1': xǁGitHubClientǁlist_workflows__mutmut_1, 
        'xǁGitHubClientǁlist_workflows__mutmut_2': xǁGitHubClientǁlist_workflows__mutmut_2, 
        'xǁGitHubClientǁlist_workflows__mutmut_3': xǁGitHubClientǁlist_workflows__mutmut_3, 
        'xǁGitHubClientǁlist_workflows__mutmut_4': xǁGitHubClientǁlist_workflows__mutmut_4, 
        'xǁGitHubClientǁlist_workflows__mutmut_5': xǁGitHubClientǁlist_workflows__mutmut_5, 
        'xǁGitHubClientǁlist_workflows__mutmut_6': xǁGitHubClientǁlist_workflows__mutmut_6, 
        'xǁGitHubClientǁlist_workflows__mutmut_7': xǁGitHubClientǁlist_workflows__mutmut_7, 
        'xǁGitHubClientǁlist_workflows__mutmut_8': xǁGitHubClientǁlist_workflows__mutmut_8, 
        'xǁGitHubClientǁlist_workflows__mutmut_9': xǁGitHubClientǁlist_workflows__mutmut_9, 
        'xǁGitHubClientǁlist_workflows__mutmut_10': xǁGitHubClientǁlist_workflows__mutmut_10, 
        'xǁGitHubClientǁlist_workflows__mutmut_11': xǁGitHubClientǁlist_workflows__mutmut_11, 
        'xǁGitHubClientǁlist_workflows__mutmut_12': xǁGitHubClientǁlist_workflows__mutmut_12, 
        'xǁGitHubClientǁlist_workflows__mutmut_13': xǁGitHubClientǁlist_workflows__mutmut_13, 
        'xǁGitHubClientǁlist_workflows__mutmut_14': xǁGitHubClientǁlist_workflows__mutmut_14, 
        'xǁGitHubClientǁlist_workflows__mutmut_15': xǁGitHubClientǁlist_workflows__mutmut_15, 
        'xǁGitHubClientǁlist_workflows__mutmut_16': xǁGitHubClientǁlist_workflows__mutmut_16, 
        'xǁGitHubClientǁlist_workflows__mutmut_17': xǁGitHubClientǁlist_workflows__mutmut_17
    }
    
    def list_workflows(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁlist_workflows__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁlist_workflows__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflows.__signature__ = _mutmut_signature(xǁGitHubClientǁlist_workflows__mutmut_orig)
    xǁGitHubClientǁlist_workflows__mutmut_orig.__name__ = 'xǁGitHubClientǁlist_workflows'

    async def xǁGitHubClientǁget_workflow__mutmut_orig(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
    ) -> WorkflowInfo:
        """Get workflow by ID or filename.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename (e.g., "ci.yml").

        Returns:
            Workflow info object.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}"
        )
        return WorkflowInfo(**data)

    async def xǁGitHubClientǁget_workflow__mutmut_1(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
    ) -> WorkflowInfo:
        """Get workflow by ID or filename.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename (e.g., "ci.yml").

        Returns:
            Workflow info object.
        """
        data = None
        return WorkflowInfo(**data)

    async def xǁGitHubClientǁget_workflow__mutmut_2(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
    ) -> WorkflowInfo:
        """Get workflow by ID or filename.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename (e.g., "ci.yml").

        Returns:
            Workflow info object.
        """
        data = await self._get(
            None
        )
        return WorkflowInfo(**data)
    
    xǁGitHubClientǁget_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁget_workflow__mutmut_1': xǁGitHubClientǁget_workflow__mutmut_1, 
        'xǁGitHubClientǁget_workflow__mutmut_2': xǁGitHubClientǁget_workflow__mutmut_2
    }
    
    def get_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁget_workflow__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁget_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_workflow.__signature__ = _mutmut_signature(xǁGitHubClientǁget_workflow__mutmut_orig)
    xǁGitHubClientǁget_workflow__mutmut_orig.__name__ = 'xǁGitHubClientǁget_workflow'

    async def xǁGitHubClientǁtrigger_workflow__mutmut_orig(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_1(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "XXmainXX",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_2(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "MAIN",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_3(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                None,
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_4(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json=None,
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_5(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_6(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_7(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"XXrefXX": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_8(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"REF": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_9(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "XXinputsXX": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_10(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "INPUTS": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_11(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs and {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_12(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(None)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_13(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(3)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_14(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = None
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_15(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                None, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_16(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, None, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_17(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, None, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_18(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=None
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_19(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_20(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_21(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_22(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_23(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=2
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_24(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[1].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_25(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(None)
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_26(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=None,
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_27(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=None,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_28(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                status_code=None,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_29(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                reason=e.message,
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_30(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                status_code=e.status_code,
            )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_31(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(workflow_id),
                reason=e.message,
                )

    async def xǁGitHubClientǁtrigger_workflow__mutmut_32(
        self,
        owner: str,
        repo: str,
        workflow_id: Union[int, str],
        ref: str = "main",
        inputs: Optional[dict[str, Any]] = None,
    ) -> Optional[int]:
        """Trigger workflow via workflow_dispatch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Workflow ID or filename.
            ref: Git reference (branch/tag) to run on.
            inputs: Workflow input parameters.

        Returns:
            Run ID if available (may need to poll for it).

        Raises:
            WorkflowTriggerError: On trigger failure.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json={"ref": ref, "inputs": inputs or {}},
            )

            # GitHub returns 204 No Content on success
            # We need to poll for the run ID
            await asyncio.sleep(2)  # Brief wait for run to be created

            # Get most recent run for this workflow
            runs = await self.list_workflow_runs(
                owner, repo, workflow_id, per_page=1
            )
            if runs:
                return runs[0].id
            return None

        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            raise WorkflowTriggerError(
                workflow=str(None),
                reason=e.message,
                status_code=e.status_code,
            )
    
    xǁGitHubClientǁtrigger_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁtrigger_workflow__mutmut_1': xǁGitHubClientǁtrigger_workflow__mutmut_1, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_2': xǁGitHubClientǁtrigger_workflow__mutmut_2, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_3': xǁGitHubClientǁtrigger_workflow__mutmut_3, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_4': xǁGitHubClientǁtrigger_workflow__mutmut_4, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_5': xǁGitHubClientǁtrigger_workflow__mutmut_5, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_6': xǁGitHubClientǁtrigger_workflow__mutmut_6, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_7': xǁGitHubClientǁtrigger_workflow__mutmut_7, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_8': xǁGitHubClientǁtrigger_workflow__mutmut_8, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_9': xǁGitHubClientǁtrigger_workflow__mutmut_9, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_10': xǁGitHubClientǁtrigger_workflow__mutmut_10, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_11': xǁGitHubClientǁtrigger_workflow__mutmut_11, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_12': xǁGitHubClientǁtrigger_workflow__mutmut_12, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_13': xǁGitHubClientǁtrigger_workflow__mutmut_13, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_14': xǁGitHubClientǁtrigger_workflow__mutmut_14, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_15': xǁGitHubClientǁtrigger_workflow__mutmut_15, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_16': xǁGitHubClientǁtrigger_workflow__mutmut_16, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_17': xǁGitHubClientǁtrigger_workflow__mutmut_17, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_18': xǁGitHubClientǁtrigger_workflow__mutmut_18, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_19': xǁGitHubClientǁtrigger_workflow__mutmut_19, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_20': xǁGitHubClientǁtrigger_workflow__mutmut_20, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_21': xǁGitHubClientǁtrigger_workflow__mutmut_21, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_22': xǁGitHubClientǁtrigger_workflow__mutmut_22, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_23': xǁGitHubClientǁtrigger_workflow__mutmut_23, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_24': xǁGitHubClientǁtrigger_workflow__mutmut_24, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_25': xǁGitHubClientǁtrigger_workflow__mutmut_25, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_26': xǁGitHubClientǁtrigger_workflow__mutmut_26, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_27': xǁGitHubClientǁtrigger_workflow__mutmut_27, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_28': xǁGitHubClientǁtrigger_workflow__mutmut_28, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_29': xǁGitHubClientǁtrigger_workflow__mutmut_29, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_30': xǁGitHubClientǁtrigger_workflow__mutmut_30, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_31': xǁGitHubClientǁtrigger_workflow__mutmut_31, 
        'xǁGitHubClientǁtrigger_workflow__mutmut_32': xǁGitHubClientǁtrigger_workflow__mutmut_32
    }
    
    def trigger_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁtrigger_workflow__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁtrigger_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    trigger_workflow.__signature__ = _mutmut_signature(xǁGitHubClientǁtrigger_workflow__mutmut_orig)
    xǁGitHubClientǁtrigger_workflow__mutmut_orig.__name__ = 'xǁGitHubClientǁtrigger_workflow'

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_orig(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_1(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 31,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_2(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 2,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_3(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = None
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_4(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"XXper_pageXX": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_5(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"PER_PAGE": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_6(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "XXpageXX": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_7(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "PAGE": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_8(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = None
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_9(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["XXbranchXX"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_10(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["BRANCH"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_11(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = None
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_12(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["XXeventXX"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_13(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["EVENT"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_14(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = None

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_15(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["XXstatusXX"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_16(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["STATUS"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_17(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = None
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_18(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = None

        data = await self._get(path, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_19(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = None
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_20(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(None, params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_21(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=None)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_22(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(params=params)
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_23(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, )
        response = ListWorkflowRunsResponse(**data)
        return response.workflow_runs

    # =========================================================================
    # Workflow Run Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_runs__mutmut_24(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[Union[int, str]] = None,
        branch: Optional[str] = None,
        event: Optional[str] = None,
        status: Optional[RunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowRun]:
        """list workflow runs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workflow_id: Filter by workflow ID/filename.
            branch: Filter by branch.
            event: Filter by event type.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status.value

        if workflow_id:
            path = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            path = f"/repos/{owner}/{repo}/actions/runs"

        data = await self._get(path, params=params)
        response = None
        return response.workflow_runs
    
    xǁGitHubClientǁlist_workflow_runs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁlist_workflow_runs__mutmut_1': xǁGitHubClientǁlist_workflow_runs__mutmut_1, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_2': xǁGitHubClientǁlist_workflow_runs__mutmut_2, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_3': xǁGitHubClientǁlist_workflow_runs__mutmut_3, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_4': xǁGitHubClientǁlist_workflow_runs__mutmut_4, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_5': xǁGitHubClientǁlist_workflow_runs__mutmut_5, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_6': xǁGitHubClientǁlist_workflow_runs__mutmut_6, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_7': xǁGitHubClientǁlist_workflow_runs__mutmut_7, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_8': xǁGitHubClientǁlist_workflow_runs__mutmut_8, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_9': xǁGitHubClientǁlist_workflow_runs__mutmut_9, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_10': xǁGitHubClientǁlist_workflow_runs__mutmut_10, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_11': xǁGitHubClientǁlist_workflow_runs__mutmut_11, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_12': xǁGitHubClientǁlist_workflow_runs__mutmut_12, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_13': xǁGitHubClientǁlist_workflow_runs__mutmut_13, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_14': xǁGitHubClientǁlist_workflow_runs__mutmut_14, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_15': xǁGitHubClientǁlist_workflow_runs__mutmut_15, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_16': xǁGitHubClientǁlist_workflow_runs__mutmut_16, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_17': xǁGitHubClientǁlist_workflow_runs__mutmut_17, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_18': xǁGitHubClientǁlist_workflow_runs__mutmut_18, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_19': xǁGitHubClientǁlist_workflow_runs__mutmut_19, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_20': xǁGitHubClientǁlist_workflow_runs__mutmut_20, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_21': xǁGitHubClientǁlist_workflow_runs__mutmut_21, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_22': xǁGitHubClientǁlist_workflow_runs__mutmut_22, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_23': xǁGitHubClientǁlist_workflow_runs__mutmut_23, 
        'xǁGitHubClientǁlist_workflow_runs__mutmut_24': xǁGitHubClientǁlist_workflow_runs__mutmut_24
    }
    
    def list_workflow_runs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁlist_workflow_runs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁlist_workflow_runs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflow_runs.__signature__ = _mutmut_signature(xǁGitHubClientǁlist_workflow_runs__mutmut_orig)
    xǁGitHubClientǁlist_workflow_runs__mutmut_orig.__name__ = 'xǁGitHubClientǁlist_workflow_runs'

    async def xǁGitHubClientǁget_workflow_run__mutmut_orig(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> WorkflowRun:
        """Get workflow run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            Workflow run object.
        """
        data = await self._get(f"/repos/{owner}/{repo}/actions/runs/{run_id}")
        return WorkflowRun(**data)

    async def xǁGitHubClientǁget_workflow_run__mutmut_1(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> WorkflowRun:
        """Get workflow run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            Workflow run object.
        """
        data = None
        return WorkflowRun(**data)

    async def xǁGitHubClientǁget_workflow_run__mutmut_2(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> WorkflowRun:
        """Get workflow run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            Workflow run object.
        """
        data = await self._get(None)
        return WorkflowRun(**data)
    
    xǁGitHubClientǁget_workflow_run__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁget_workflow_run__mutmut_1': xǁGitHubClientǁget_workflow_run__mutmut_1, 
        'xǁGitHubClientǁget_workflow_run__mutmut_2': xǁGitHubClientǁget_workflow_run__mutmut_2
    }
    
    def get_workflow_run(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁget_workflow_run__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁget_workflow_run__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_workflow_run.__signature__ = _mutmut_signature(xǁGitHubClientǁget_workflow_run__mutmut_orig)
    xǁGitHubClientǁget_workflow_run__mutmut_orig.__name__ = 'xǁGitHubClientǁget_workflow_run'

    async def xǁGitHubClientǁwait_for_run__mutmut_orig(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_1(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 11.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_2(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3601.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_3(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = None
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_4(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while False:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_5(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = None
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_6(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(None, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_7(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, None, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_8(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, None)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_9(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_10(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_11(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, )
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_12(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = None
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_13(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() + start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_14(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_15(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    None
                )

            await asyncio.sleep(poll_interval)

    async def xǁGitHubClientǁwait_for_run__mutmut_16(
        self,
        owner: str,
        repo: str,
        run_id: int,
        poll_interval: float = 10.0,
        timeout: float = 3600.0,
    ) -> WorkflowRun:
        """Wait for workflow run to complete.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            poll_interval: Seconds between status checks.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed workflow run.

        Raises:
            TimeoutError: If run doesn't complete within timeout.
        """
        start_time = time.time()
        while True:
            run = await self.get_workflow_run(owner, repo, run_id)
            if run.is_completed:
                return run

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Workflow run {run_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(None)
    
    xǁGitHubClientǁwait_for_run__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁwait_for_run__mutmut_1': xǁGitHubClientǁwait_for_run__mutmut_1, 
        'xǁGitHubClientǁwait_for_run__mutmut_2': xǁGitHubClientǁwait_for_run__mutmut_2, 
        'xǁGitHubClientǁwait_for_run__mutmut_3': xǁGitHubClientǁwait_for_run__mutmut_3, 
        'xǁGitHubClientǁwait_for_run__mutmut_4': xǁGitHubClientǁwait_for_run__mutmut_4, 
        'xǁGitHubClientǁwait_for_run__mutmut_5': xǁGitHubClientǁwait_for_run__mutmut_5, 
        'xǁGitHubClientǁwait_for_run__mutmut_6': xǁGitHubClientǁwait_for_run__mutmut_6, 
        'xǁGitHubClientǁwait_for_run__mutmut_7': xǁGitHubClientǁwait_for_run__mutmut_7, 
        'xǁGitHubClientǁwait_for_run__mutmut_8': xǁGitHubClientǁwait_for_run__mutmut_8, 
        'xǁGitHubClientǁwait_for_run__mutmut_9': xǁGitHubClientǁwait_for_run__mutmut_9, 
        'xǁGitHubClientǁwait_for_run__mutmut_10': xǁGitHubClientǁwait_for_run__mutmut_10, 
        'xǁGitHubClientǁwait_for_run__mutmut_11': xǁGitHubClientǁwait_for_run__mutmut_11, 
        'xǁGitHubClientǁwait_for_run__mutmut_12': xǁGitHubClientǁwait_for_run__mutmut_12, 
        'xǁGitHubClientǁwait_for_run__mutmut_13': xǁGitHubClientǁwait_for_run__mutmut_13, 
        'xǁGitHubClientǁwait_for_run__mutmut_14': xǁGitHubClientǁwait_for_run__mutmut_14, 
        'xǁGitHubClientǁwait_for_run__mutmut_15': xǁGitHubClientǁwait_for_run__mutmut_15, 
        'xǁGitHubClientǁwait_for_run__mutmut_16': xǁGitHubClientǁwait_for_run__mutmut_16
    }
    
    def wait_for_run(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁwait_for_run__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁwait_for_run__mutmut_mutants"), args, kwargs, self)
        return result 
    
    wait_for_run.__signature__ = _mutmut_signature(xǁGitHubClientǁwait_for_run__mutmut_orig)
    xǁGitHubClientǁwait_for_run__mutmut_orig.__name__ = 'xǁGitHubClientǁwait_for_run'

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_orig(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_1(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                None
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_2(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return False
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_3(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(None)
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_4(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(None, exc_info=True)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_5(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=None)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_6(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(exc_info=True)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_7(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", )
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_8(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=False)
            return False

    async def xǁGitHubClientǁcancel_workflow_run__mutmut_9(
        self,
        owner: str,
        repo: str,
        run_id: int,
    ) -> bool:
        """Cancel a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.

        Returns:
            True if cancellation was accepted.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return True
    
    xǁGitHubClientǁcancel_workflow_run__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁcancel_workflow_run__mutmut_1': xǁGitHubClientǁcancel_workflow_run__mutmut_1, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_2': xǁGitHubClientǁcancel_workflow_run__mutmut_2, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_3': xǁGitHubClientǁcancel_workflow_run__mutmut_3, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_4': xǁGitHubClientǁcancel_workflow_run__mutmut_4, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_5': xǁGitHubClientǁcancel_workflow_run__mutmut_5, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_6': xǁGitHubClientǁcancel_workflow_run__mutmut_6, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_7': xǁGitHubClientǁcancel_workflow_run__mutmut_7, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_8': xǁGitHubClientǁcancel_workflow_run__mutmut_8, 
        'xǁGitHubClientǁcancel_workflow_run__mutmut_9': xǁGitHubClientǁcancel_workflow_run__mutmut_9
    }
    
    def cancel_workflow_run(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁcancel_workflow_run__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁcancel_workflow_run__mutmut_mutants"), args, kwargs, self)
        return result 
    
    cancel_workflow_run.__signature__ = _mutmut_signature(xǁGitHubClientǁcancel_workflow_run__mutmut_orig)
    xǁGitHubClientǁcancel_workflow_run__mutmut_orig.__name__ = 'xǁGitHubClientǁcancel_workflow_run'

    async def xǁGitHubClientǁrerun_workflow__mutmut_orig(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_1(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = True,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_2(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                None,
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_3(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json=None,
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_4(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_5(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_6(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"XXenable_debug_loggingXX": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_7(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"ENABLE_DEBUG_LOGGING": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_8(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return False
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_9(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(None)
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_10(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(None, exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_11(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=None)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_12(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(exc_info=True)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_13(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", )
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_14(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=False)
            return False

    async def xǁGitHubClientǁrerun_workflow__mutmut_15(
        self,
        owner: str,
        repo: str,
        run_id: int,
        enable_debug: bool = False,
    ) -> bool:
        """Re-run a workflow.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            enable_debug: Enable debug logging.

        Returns:
            True if re-run was triggered.
        """
        try:
            await self._post(
                f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
                json={"enable_debug_logging": enable_debug},
            )
            return True
        except GitHubAPIError as e:
            logger.debug(f"GitHubAPIError: {e}")
            logger.warning(f"GitHubAPIError: {e}", exc_info=True)
            return True
    
    xǁGitHubClientǁrerun_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁrerun_workflow__mutmut_1': xǁGitHubClientǁrerun_workflow__mutmut_1, 
        'xǁGitHubClientǁrerun_workflow__mutmut_2': xǁGitHubClientǁrerun_workflow__mutmut_2, 
        'xǁGitHubClientǁrerun_workflow__mutmut_3': xǁGitHubClientǁrerun_workflow__mutmut_3, 
        'xǁGitHubClientǁrerun_workflow__mutmut_4': xǁGitHubClientǁrerun_workflow__mutmut_4, 
        'xǁGitHubClientǁrerun_workflow__mutmut_5': xǁGitHubClientǁrerun_workflow__mutmut_5, 
        'xǁGitHubClientǁrerun_workflow__mutmut_6': xǁGitHubClientǁrerun_workflow__mutmut_6, 
        'xǁGitHubClientǁrerun_workflow__mutmut_7': xǁGitHubClientǁrerun_workflow__mutmut_7, 
        'xǁGitHubClientǁrerun_workflow__mutmut_8': xǁGitHubClientǁrerun_workflow__mutmut_8, 
        'xǁGitHubClientǁrerun_workflow__mutmut_9': xǁGitHubClientǁrerun_workflow__mutmut_9, 
        'xǁGitHubClientǁrerun_workflow__mutmut_10': xǁGitHubClientǁrerun_workflow__mutmut_10, 
        'xǁGitHubClientǁrerun_workflow__mutmut_11': xǁGitHubClientǁrerun_workflow__mutmut_11, 
        'xǁGitHubClientǁrerun_workflow__mutmut_12': xǁGitHubClientǁrerun_workflow__mutmut_12, 
        'xǁGitHubClientǁrerun_workflow__mutmut_13': xǁGitHubClientǁrerun_workflow__mutmut_13, 
        'xǁGitHubClientǁrerun_workflow__mutmut_14': xǁGitHubClientǁrerun_workflow__mutmut_14, 
        'xǁGitHubClientǁrerun_workflow__mutmut_15': xǁGitHubClientǁrerun_workflow__mutmut_15
    }
    
    def rerun_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁrerun_workflow__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁrerun_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    rerun_workflow.__signature__ = _mutmut_signature(xǁGitHubClientǁrerun_workflow__mutmut_orig)
    xǁGitHubClientǁrerun_workflow__mutmut_orig.__name__ = 'xǁGitHubClientǁrerun_workflow'

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_orig(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_1(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 31,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_2(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 2,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_3(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = None
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_4(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"XXper_pageXX": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_5(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"PER_PAGE": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_6(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "XXpageXX": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_7(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "PAGE": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_8(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = None

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_9(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["XXfilterXX"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_10(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["FILTER"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_11(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = None
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_12(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            None,
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_13(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=None,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_14(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            params=params,
        )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_15(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            )
        response = ListWorkflowJobsResponse(**data)
        return response.jobs

    # =========================================================================
    # Job Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_workflow_jobs__mutmut_16(
        self,
        owner: str,
        repo: str,
        run_id: int,
        filter_status: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[WorkflowJob]:
        """list jobs for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            filter_status: Filter by status (latest, all).
            per_page: Results per page.
            page: Page number.

        Returns:
            list of workflow jobs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if filter_status:
            params["filter"] = filter_status

        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
            params=params,
        )
        response = None
        return response.jobs
    
    xǁGitHubClientǁlist_workflow_jobs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁlist_workflow_jobs__mutmut_1': xǁGitHubClientǁlist_workflow_jobs__mutmut_1, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_2': xǁGitHubClientǁlist_workflow_jobs__mutmut_2, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_3': xǁGitHubClientǁlist_workflow_jobs__mutmut_3, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_4': xǁGitHubClientǁlist_workflow_jobs__mutmut_4, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_5': xǁGitHubClientǁlist_workflow_jobs__mutmut_5, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_6': xǁGitHubClientǁlist_workflow_jobs__mutmut_6, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_7': xǁGitHubClientǁlist_workflow_jobs__mutmut_7, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_8': xǁGitHubClientǁlist_workflow_jobs__mutmut_8, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_9': xǁGitHubClientǁlist_workflow_jobs__mutmut_9, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_10': xǁGitHubClientǁlist_workflow_jobs__mutmut_10, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_11': xǁGitHubClientǁlist_workflow_jobs__mutmut_11, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_12': xǁGitHubClientǁlist_workflow_jobs__mutmut_12, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_13': xǁGitHubClientǁlist_workflow_jobs__mutmut_13, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_14': xǁGitHubClientǁlist_workflow_jobs__mutmut_14, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_15': xǁGitHubClientǁlist_workflow_jobs__mutmut_15, 
        'xǁGitHubClientǁlist_workflow_jobs__mutmut_16': xǁGitHubClientǁlist_workflow_jobs__mutmut_16
    }
    
    def list_workflow_jobs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁlist_workflow_jobs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁlist_workflow_jobs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflow_jobs.__signature__ = _mutmut_signature(xǁGitHubClientǁlist_workflow_jobs__mutmut_orig)
    xǁGitHubClientǁlist_workflow_jobs__mutmut_orig.__name__ = 'xǁGitHubClientǁlist_workflow_jobs'

    async def xǁGitHubClientǁget_job_logs__mutmut_orig(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_1(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = None
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_2(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                None,
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_3(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=None,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_4(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_5(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_6(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=False,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_7(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(None)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_8(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code != 404:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_9(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 405:
                raise NotFoundError("job logs", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_10(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError(None, str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_11(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", None)

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_12(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError(str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_13(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", )

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_14(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("XXjob logsXX", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_15(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("JOB LOGS", str(job_id))

            return response.text

    async def xǁGitHubClientǁget_job_logs__mutmut_16(
        self,
        owner: str,
        repo: str,
        job_id: int,
    ) -> str:
        """Get job logs.

        Args:
            owner: Repository owner.
            repo: Repository name.
            job_id: Job ID.

        Returns:
            Job logs as string.
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("job logs", str(None))

            return response.text
    
    xǁGitHubClientǁget_job_logs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁget_job_logs__mutmut_1': xǁGitHubClientǁget_job_logs__mutmut_1, 
        'xǁGitHubClientǁget_job_logs__mutmut_2': xǁGitHubClientǁget_job_logs__mutmut_2, 
        'xǁGitHubClientǁget_job_logs__mutmut_3': xǁGitHubClientǁget_job_logs__mutmut_3, 
        'xǁGitHubClientǁget_job_logs__mutmut_4': xǁGitHubClientǁget_job_logs__mutmut_4, 
        'xǁGitHubClientǁget_job_logs__mutmut_5': xǁGitHubClientǁget_job_logs__mutmut_5, 
        'xǁGitHubClientǁget_job_logs__mutmut_6': xǁGitHubClientǁget_job_logs__mutmut_6, 
        'xǁGitHubClientǁget_job_logs__mutmut_7': xǁGitHubClientǁget_job_logs__mutmut_7, 
        'xǁGitHubClientǁget_job_logs__mutmut_8': xǁGitHubClientǁget_job_logs__mutmut_8, 
        'xǁGitHubClientǁget_job_logs__mutmut_9': xǁGitHubClientǁget_job_logs__mutmut_9, 
        'xǁGitHubClientǁget_job_logs__mutmut_10': xǁGitHubClientǁget_job_logs__mutmut_10, 
        'xǁGitHubClientǁget_job_logs__mutmut_11': xǁGitHubClientǁget_job_logs__mutmut_11, 
        'xǁGitHubClientǁget_job_logs__mutmut_12': xǁGitHubClientǁget_job_logs__mutmut_12, 
        'xǁGitHubClientǁget_job_logs__mutmut_13': xǁGitHubClientǁget_job_logs__mutmut_13, 
        'xǁGitHubClientǁget_job_logs__mutmut_14': xǁGitHubClientǁget_job_logs__mutmut_14, 
        'xǁGitHubClientǁget_job_logs__mutmut_15': xǁGitHubClientǁget_job_logs__mutmut_15, 
        'xǁGitHubClientǁget_job_logs__mutmut_16': xǁGitHubClientǁget_job_logs__mutmut_16
    }
    
    def get_job_logs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁget_job_logs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁget_job_logs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_job_logs.__signature__ = _mutmut_signature(xǁGitHubClientǁget_job_logs__mutmut_orig)
    xǁGitHubClientǁget_job_logs__mutmut_orig.__name__ = 'xǁGitHubClientǁget_job_logs'

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_orig(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"per_page": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_1(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 31,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"per_page": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_2(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 2,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"per_page": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_3(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = None
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_4(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            None,
            params={"per_page": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_5(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params=None,
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_6(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            params={"per_page": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_7(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_8(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"XXper_pageXX": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_9(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"PER_PAGE": per_page, "page": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_10(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"per_page": per_page, "XXpageXX": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_11(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"per_page": per_page, "PAGE": page},
        )
        response = ListArtifactsResponse(**data)
        return response.artifacts

    # =========================================================================
    # Artifact Operations
    # =========================================================================

    async def xǁGitHubClientǁlist_run_artifacts__mutmut_12(
        self,
        owner: str,
        repo: str,
        run_id: int,
        per_page: int = 30,
        page: int = 1,
    ) -> list[ArtifactInfo]:
        """list artifacts for a workflow run.

        Args:
            owner: Repository owner.
            repo: Repository name.
            run_id: Workflow run ID.
            per_page: Results per page.
            page: Page number.

        Returns:
            list of artifact info objects.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
            params={"per_page": per_page, "page": page},
        )
        response = None
        return response.artifacts
    
    xǁGitHubClientǁlist_run_artifacts__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁlist_run_artifacts__mutmut_1': xǁGitHubClientǁlist_run_artifacts__mutmut_1, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_2': xǁGitHubClientǁlist_run_artifacts__mutmut_2, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_3': xǁGitHubClientǁlist_run_artifacts__mutmut_3, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_4': xǁGitHubClientǁlist_run_artifacts__mutmut_4, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_5': xǁGitHubClientǁlist_run_artifacts__mutmut_5, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_6': xǁGitHubClientǁlist_run_artifacts__mutmut_6, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_7': xǁGitHubClientǁlist_run_artifacts__mutmut_7, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_8': xǁGitHubClientǁlist_run_artifacts__mutmut_8, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_9': xǁGitHubClientǁlist_run_artifacts__mutmut_9, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_10': xǁGitHubClientǁlist_run_artifacts__mutmut_10, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_11': xǁGitHubClientǁlist_run_artifacts__mutmut_11, 
        'xǁGitHubClientǁlist_run_artifacts__mutmut_12': xǁGitHubClientǁlist_run_artifacts__mutmut_12
    }
    
    def list_run_artifacts(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁlist_run_artifacts__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁlist_run_artifacts__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_run_artifacts.__signature__ = _mutmut_signature(xǁGitHubClientǁlist_run_artifacts__mutmut_orig)
    xǁGitHubClientǁlist_run_artifacts__mutmut_orig.__name__ = 'xǁGitHubClientǁlist_run_artifacts'

    async def xǁGitHubClientǁdownload_artifact__mutmut_orig(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_1(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = None
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_2(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                None,
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_3(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=None,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_4(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_5(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_6(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=False,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_7(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(None)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_8(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code != 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_9(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 405:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_10(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError(None, str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_11(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", None)

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_12(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError(str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_13(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", )

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_14(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("XXartifactXX", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_15(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("ARTIFACT", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_16(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(None))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_17(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code > 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_18(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 401:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_19(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message=None,
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_20(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    status_code=None,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_21(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_22(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="Failed to download artifact",
                    )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_23(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="XXFailed to download artifactXX",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_24(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="failed to download artifact",
                    status_code=response.status_code,
                )

            return response.content

    async def xǁGitHubClientǁdownload_artifact__mutmut_25(
        self,
        owner: str,
        repo: str,
        artifact_id: int,
    ) -> bytes:
        """Download an artifact.

        Args:
            owner: Repository owner.
            repo: Repository name.
            artifact_id: Artifact ID.

        Returns:
            Artifact content as bytes (zip archive).
        """
        async with self._create_client() as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip",
                follow_redirects=True,
            )
            self._update_rate_limit(response.headers)

            if response.status_code == 404:
                raise NotFoundError("artifact", str(artifact_id))

            if response.status_code >= 400:
                raise GitHubAPIError(
                    message="FAILED TO DOWNLOAD ARTIFACT",
                    status_code=response.status_code,
                )

            return response.content
    
    xǁGitHubClientǁdownload_artifact__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁdownload_artifact__mutmut_1': xǁGitHubClientǁdownload_artifact__mutmut_1, 
        'xǁGitHubClientǁdownload_artifact__mutmut_2': xǁGitHubClientǁdownload_artifact__mutmut_2, 
        'xǁGitHubClientǁdownload_artifact__mutmut_3': xǁGitHubClientǁdownload_artifact__mutmut_3, 
        'xǁGitHubClientǁdownload_artifact__mutmut_4': xǁGitHubClientǁdownload_artifact__mutmut_4, 
        'xǁGitHubClientǁdownload_artifact__mutmut_5': xǁGitHubClientǁdownload_artifact__mutmut_5, 
        'xǁGitHubClientǁdownload_artifact__mutmut_6': xǁGitHubClientǁdownload_artifact__mutmut_6, 
        'xǁGitHubClientǁdownload_artifact__mutmut_7': xǁGitHubClientǁdownload_artifact__mutmut_7, 
        'xǁGitHubClientǁdownload_artifact__mutmut_8': xǁGitHubClientǁdownload_artifact__mutmut_8, 
        'xǁGitHubClientǁdownload_artifact__mutmut_9': xǁGitHubClientǁdownload_artifact__mutmut_9, 
        'xǁGitHubClientǁdownload_artifact__mutmut_10': xǁGitHubClientǁdownload_artifact__mutmut_10, 
        'xǁGitHubClientǁdownload_artifact__mutmut_11': xǁGitHubClientǁdownload_artifact__mutmut_11, 
        'xǁGitHubClientǁdownload_artifact__mutmut_12': xǁGitHubClientǁdownload_artifact__mutmut_12, 
        'xǁGitHubClientǁdownload_artifact__mutmut_13': xǁGitHubClientǁdownload_artifact__mutmut_13, 
        'xǁGitHubClientǁdownload_artifact__mutmut_14': xǁGitHubClientǁdownload_artifact__mutmut_14, 
        'xǁGitHubClientǁdownload_artifact__mutmut_15': xǁGitHubClientǁdownload_artifact__mutmut_15, 
        'xǁGitHubClientǁdownload_artifact__mutmut_16': xǁGitHubClientǁdownload_artifact__mutmut_16, 
        'xǁGitHubClientǁdownload_artifact__mutmut_17': xǁGitHubClientǁdownload_artifact__mutmut_17, 
        'xǁGitHubClientǁdownload_artifact__mutmut_18': xǁGitHubClientǁdownload_artifact__mutmut_18, 
        'xǁGitHubClientǁdownload_artifact__mutmut_19': xǁGitHubClientǁdownload_artifact__mutmut_19, 
        'xǁGitHubClientǁdownload_artifact__mutmut_20': xǁGitHubClientǁdownload_artifact__mutmut_20, 
        'xǁGitHubClientǁdownload_artifact__mutmut_21': xǁGitHubClientǁdownload_artifact__mutmut_21, 
        'xǁGitHubClientǁdownload_artifact__mutmut_22': xǁGitHubClientǁdownload_artifact__mutmut_22, 
        'xǁGitHubClientǁdownload_artifact__mutmut_23': xǁGitHubClientǁdownload_artifact__mutmut_23, 
        'xǁGitHubClientǁdownload_artifact__mutmut_24': xǁGitHubClientǁdownload_artifact__mutmut_24, 
        'xǁGitHubClientǁdownload_artifact__mutmut_25': xǁGitHubClientǁdownload_artifact__mutmut_25
    }
    
    def download_artifact(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁdownload_artifact__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁdownload_artifact__mutmut_mutants"), args, kwargs, self)
        return result 
    
    download_artifact.__signature__ = _mutmut_signature(xǁGitHubClientǁdownload_artifact__mutmut_orig)
    xǁGitHubClientǁdownload_artifact__mutmut_orig.__name__ = 'xǁGitHubClientǁdownload_artifact'

    # =========================================================================
    # Check Run Operations
    # =========================================================================

    async def xǁGitHubClientǁget_check_run__mutmut_orig(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> CheckRun:
        """Get check run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run object.
        """
        data = await self._get(
            f"/repos/{owner}/{repo}/check-runs/{check_run_id}"
        )
        return CheckRun(**data)

    # =========================================================================
    # Check Run Operations
    # =========================================================================

    async def xǁGitHubClientǁget_check_run__mutmut_1(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> CheckRun:
        """Get check run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run object.
        """
        data = None
        return CheckRun(**data)

    # =========================================================================
    # Check Run Operations
    # =========================================================================

    async def xǁGitHubClientǁget_check_run__mutmut_2(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> CheckRun:
        """Get check run by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run object.
        """
        data = await self._get(
            None
        )
        return CheckRun(**data)
    
    xǁGitHubClientǁget_check_run__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁget_check_run__mutmut_1': xǁGitHubClientǁget_check_run__mutmut_1, 
        'xǁGitHubClientǁget_check_run__mutmut_2': xǁGitHubClientǁget_check_run__mutmut_2
    }
    
    def get_check_run(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁget_check_run__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁget_check_run__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_check_run.__signature__ = _mutmut_signature(xǁGitHubClientǁget_check_run__mutmut_orig)
    xǁGitHubClientǁget_check_run__mutmut_orig.__name__ = 'xǁGitHubClientǁget_check_run'

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_orig(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_1(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 31,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_2(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 2,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_3(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = None
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_4(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"XXper_pageXX": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_5(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"PER_PAGE": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_6(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "XXpageXX": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_7(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "PAGE": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_8(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = None
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_9(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["XXcheck_nameXX"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_10(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["CHECK_NAME"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_11(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = None

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_12(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["XXstatusXX"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_13(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["STATUS"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_14(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = None
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_15(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            None,
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_16(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=None,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_17(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            params=params,
        )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_18(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            )
        response = ListCheckRunsResponse(**data)
        return response.check_runs

    async def xǁGitHubClientǁlist_check_runs_for_ref__mutmut_19(
        self,
        owner: str,
        repo: str,
        ref: str,
        check_name: Optional[str] = None,
        status: Optional[CheckRunStatus] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[CheckRun]:
        """List check runs for a git reference.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (commit SHA, branch, or tag).
            check_name: Filter by check run name.
            status: Filter by status.
            per_page: Results per page.
            page: Page number.

        Returns:
            List of check runs.
        """
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if check_name:
            params["check_name"] = check_name
        if status:
            params["status"] = status.value

        data = await self._get(
            f"/repos/{owner}/{repo}/commits/{ref}/check-runs",
            params=params,
        )
        response = None
        return response.check_runs
    
    xǁGitHubClientǁlist_check_runs_for_ref__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_1': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_1, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_2': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_2, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_3': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_3, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_4': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_4, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_5': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_5, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_6': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_6, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_7': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_7, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_8': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_8, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_9': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_9, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_10': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_10, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_11': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_11, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_12': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_12, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_13': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_13, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_14': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_14, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_15': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_15, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_16': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_16, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_17': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_17, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_18': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_18, 
        'xǁGitHubClientǁlist_check_runs_for_ref__mutmut_19': xǁGitHubClientǁlist_check_runs_for_ref__mutmut_19
    }
    
    def list_check_runs_for_ref(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁlist_check_runs_for_ref__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁlist_check_runs_for_ref__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_check_runs_for_ref.__signature__ = _mutmut_signature(xǁGitHubClientǁlist_check_runs_for_ref__mutmut_orig)
    xǁGitHubClientǁlist_check_runs_for_ref__mutmut_orig.__name__ = 'xǁGitHubClientǁlist_check_runs_for_ref'

    async def xǁGitHubClientǁget_check_run_logs__mutmut_orig(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_1(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(None, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_2(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, None, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_3(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, None)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_4(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_5(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_6(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, )
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_7(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                None,
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_8(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                None
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_9(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_10(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "check run logs",
                )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_11(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "XXcheck run logsXX",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )

    async def xǁGitHubClientǁget_check_run_logs__mutmut_12(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
    ) -> str:
        """Get check run logs.

        Note: Check runs are associated with GitHub Actions jobs.
        This method fetches the logs for the underlying job.

        Args:
            owner: Repository owner.
            repo: Repository name.
            check_run_id: Check run ID.

        Returns:
            Check run logs as string.

        Raises:
            NotFoundError: If check run or logs not found.
            GitHubAPIError: On other API errors.
        """
        # Check runs don't have a direct logs endpoint, but if it's a GitHub Actions
        # check run, we need to find the associated job
        # For now, we'll try to get logs via the Actions job endpoint
        # The check_run_id is often the same as the job_id for Actions
        try:
            return await self.get_job_logs(owner, repo, check_run_id)
        except NotFoundError:
            # If direct job lookup fails, we need to find the job via workflow runs
            # This is a limitation of the GitHub API - check runs don't directly expose logs
            raise NotFoundError(
                "CHECK RUN LOGS",
                f"{check_run_id} (note: logs may only be available via associated workflow job)"
            )
    
    xǁGitHubClientǁget_check_run_logs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁget_check_run_logs__mutmut_1': xǁGitHubClientǁget_check_run_logs__mutmut_1, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_2': xǁGitHubClientǁget_check_run_logs__mutmut_2, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_3': xǁGitHubClientǁget_check_run_logs__mutmut_3, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_4': xǁGitHubClientǁget_check_run_logs__mutmut_4, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_5': xǁGitHubClientǁget_check_run_logs__mutmut_5, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_6': xǁGitHubClientǁget_check_run_logs__mutmut_6, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_7': xǁGitHubClientǁget_check_run_logs__mutmut_7, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_8': xǁGitHubClientǁget_check_run_logs__mutmut_8, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_9': xǁGitHubClientǁget_check_run_logs__mutmut_9, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_10': xǁGitHubClientǁget_check_run_logs__mutmut_10, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_11': xǁGitHubClientǁget_check_run_logs__mutmut_11, 
        'xǁGitHubClientǁget_check_run_logs__mutmut_12': xǁGitHubClientǁget_check_run_logs__mutmut_12
    }
    
    def get_check_run_logs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁget_check_run_logs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁget_check_run_logs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_check_run_logs.__signature__ = _mutmut_signature(xǁGitHubClientǁget_check_run_logs__mutmut_orig)
    xǁGitHubClientǁget_check_run_logs__mutmut_orig.__name__ = 'xǁGitHubClientǁget_check_run_logs'

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_orig(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_1(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = None
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_2(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get(None)
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_3(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("XX/rate_limitXX")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_4(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/RATE_LIMIT")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_5(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = None
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_6(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get(None, {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_7(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", None)
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_8(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get({})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_9(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", )
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_10(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get(None, {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_11(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", None).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_12(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get({}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_13(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", ).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_14(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("XXresourcesXX", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_15(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("RESOURCES", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_16(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("XXcoreXX", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_17(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("CORE", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_18(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=None,
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_19(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=None,
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_20(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=None,
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_21(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=None,
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_22(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_23(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_24(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_25(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_26(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get(None, 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_27(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", None),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_28(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get(0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_29(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", ),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_30(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("XXlimitXX", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_31(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("LIMIT", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_32(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 1),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_33(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get(None, 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_34(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", None),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_35(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get(0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_36(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", ),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_37(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("XXremainingXX", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_38(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("REMAINING", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_39(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 1),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_40(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                None, tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_41(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=None
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_42(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_43(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_44(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get(None, 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_45(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", None), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_46(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get(0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_47(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", ), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_48(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("XXresetXX", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_49(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("RESET", 0), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_50(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 1), tz=timezone.utc
            ),
            used=core.get("used", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_51(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get(None, 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_52(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", None),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_53(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get(0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_54(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", ),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_55(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("XXusedXX", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_56(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("USED", 0),
        )

    # =========================================================================
    # Rate Limit
    # =========================================================================

    async def xǁGitHubClientǁget_rate_limit__mutmut_57(self) -> RateLimitInfo:
        """Get current rate limit status.

        Returns:
            Rate limit info.
        """
        data = await self._get("/rate_limit")
        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 0),
            remaining=core.get("remaining", 0),
            reset=datetime.fromtimestamp(
                core.get("reset", 0), tz=timezone.utc
            ),
            used=core.get("used", 1),
        )
    
    xǁGitHubClientǁget_rate_limit__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientǁget_rate_limit__mutmut_1': xǁGitHubClientǁget_rate_limit__mutmut_1, 
        'xǁGitHubClientǁget_rate_limit__mutmut_2': xǁGitHubClientǁget_rate_limit__mutmut_2, 
        'xǁGitHubClientǁget_rate_limit__mutmut_3': xǁGitHubClientǁget_rate_limit__mutmut_3, 
        'xǁGitHubClientǁget_rate_limit__mutmut_4': xǁGitHubClientǁget_rate_limit__mutmut_4, 
        'xǁGitHubClientǁget_rate_limit__mutmut_5': xǁGitHubClientǁget_rate_limit__mutmut_5, 
        'xǁGitHubClientǁget_rate_limit__mutmut_6': xǁGitHubClientǁget_rate_limit__mutmut_6, 
        'xǁGitHubClientǁget_rate_limit__mutmut_7': xǁGitHubClientǁget_rate_limit__mutmut_7, 
        'xǁGitHubClientǁget_rate_limit__mutmut_8': xǁGitHubClientǁget_rate_limit__mutmut_8, 
        'xǁGitHubClientǁget_rate_limit__mutmut_9': xǁGitHubClientǁget_rate_limit__mutmut_9, 
        'xǁGitHubClientǁget_rate_limit__mutmut_10': xǁGitHubClientǁget_rate_limit__mutmut_10, 
        'xǁGitHubClientǁget_rate_limit__mutmut_11': xǁGitHubClientǁget_rate_limit__mutmut_11, 
        'xǁGitHubClientǁget_rate_limit__mutmut_12': xǁGitHubClientǁget_rate_limit__mutmut_12, 
        'xǁGitHubClientǁget_rate_limit__mutmut_13': xǁGitHubClientǁget_rate_limit__mutmut_13, 
        'xǁGitHubClientǁget_rate_limit__mutmut_14': xǁGitHubClientǁget_rate_limit__mutmut_14, 
        'xǁGitHubClientǁget_rate_limit__mutmut_15': xǁGitHubClientǁget_rate_limit__mutmut_15, 
        'xǁGitHubClientǁget_rate_limit__mutmut_16': xǁGitHubClientǁget_rate_limit__mutmut_16, 
        'xǁGitHubClientǁget_rate_limit__mutmut_17': xǁGitHubClientǁget_rate_limit__mutmut_17, 
        'xǁGitHubClientǁget_rate_limit__mutmut_18': xǁGitHubClientǁget_rate_limit__mutmut_18, 
        'xǁGitHubClientǁget_rate_limit__mutmut_19': xǁGitHubClientǁget_rate_limit__mutmut_19, 
        'xǁGitHubClientǁget_rate_limit__mutmut_20': xǁGitHubClientǁget_rate_limit__mutmut_20, 
        'xǁGitHubClientǁget_rate_limit__mutmut_21': xǁGitHubClientǁget_rate_limit__mutmut_21, 
        'xǁGitHubClientǁget_rate_limit__mutmut_22': xǁGitHubClientǁget_rate_limit__mutmut_22, 
        'xǁGitHubClientǁget_rate_limit__mutmut_23': xǁGitHubClientǁget_rate_limit__mutmut_23, 
        'xǁGitHubClientǁget_rate_limit__mutmut_24': xǁGitHubClientǁget_rate_limit__mutmut_24, 
        'xǁGitHubClientǁget_rate_limit__mutmut_25': xǁGitHubClientǁget_rate_limit__mutmut_25, 
        'xǁGitHubClientǁget_rate_limit__mutmut_26': xǁGitHubClientǁget_rate_limit__mutmut_26, 
        'xǁGitHubClientǁget_rate_limit__mutmut_27': xǁGitHubClientǁget_rate_limit__mutmut_27, 
        'xǁGitHubClientǁget_rate_limit__mutmut_28': xǁGitHubClientǁget_rate_limit__mutmut_28, 
        'xǁGitHubClientǁget_rate_limit__mutmut_29': xǁGitHubClientǁget_rate_limit__mutmut_29, 
        'xǁGitHubClientǁget_rate_limit__mutmut_30': xǁGitHubClientǁget_rate_limit__mutmut_30, 
        'xǁGitHubClientǁget_rate_limit__mutmut_31': xǁGitHubClientǁget_rate_limit__mutmut_31, 
        'xǁGitHubClientǁget_rate_limit__mutmut_32': xǁGitHubClientǁget_rate_limit__mutmut_32, 
        'xǁGitHubClientǁget_rate_limit__mutmut_33': xǁGitHubClientǁget_rate_limit__mutmut_33, 
        'xǁGitHubClientǁget_rate_limit__mutmut_34': xǁGitHubClientǁget_rate_limit__mutmut_34, 
        'xǁGitHubClientǁget_rate_limit__mutmut_35': xǁGitHubClientǁget_rate_limit__mutmut_35, 
        'xǁGitHubClientǁget_rate_limit__mutmut_36': xǁGitHubClientǁget_rate_limit__mutmut_36, 
        'xǁGitHubClientǁget_rate_limit__mutmut_37': xǁGitHubClientǁget_rate_limit__mutmut_37, 
        'xǁGitHubClientǁget_rate_limit__mutmut_38': xǁGitHubClientǁget_rate_limit__mutmut_38, 
        'xǁGitHubClientǁget_rate_limit__mutmut_39': xǁGitHubClientǁget_rate_limit__mutmut_39, 
        'xǁGitHubClientǁget_rate_limit__mutmut_40': xǁGitHubClientǁget_rate_limit__mutmut_40, 
        'xǁGitHubClientǁget_rate_limit__mutmut_41': xǁGitHubClientǁget_rate_limit__mutmut_41, 
        'xǁGitHubClientǁget_rate_limit__mutmut_42': xǁGitHubClientǁget_rate_limit__mutmut_42, 
        'xǁGitHubClientǁget_rate_limit__mutmut_43': xǁGitHubClientǁget_rate_limit__mutmut_43, 
        'xǁGitHubClientǁget_rate_limit__mutmut_44': xǁGitHubClientǁget_rate_limit__mutmut_44, 
        'xǁGitHubClientǁget_rate_limit__mutmut_45': xǁGitHubClientǁget_rate_limit__mutmut_45, 
        'xǁGitHubClientǁget_rate_limit__mutmut_46': xǁGitHubClientǁget_rate_limit__mutmut_46, 
        'xǁGitHubClientǁget_rate_limit__mutmut_47': xǁGitHubClientǁget_rate_limit__mutmut_47, 
        'xǁGitHubClientǁget_rate_limit__mutmut_48': xǁGitHubClientǁget_rate_limit__mutmut_48, 
        'xǁGitHubClientǁget_rate_limit__mutmut_49': xǁGitHubClientǁget_rate_limit__mutmut_49, 
        'xǁGitHubClientǁget_rate_limit__mutmut_50': xǁGitHubClientǁget_rate_limit__mutmut_50, 
        'xǁGitHubClientǁget_rate_limit__mutmut_51': xǁGitHubClientǁget_rate_limit__mutmut_51, 
        'xǁGitHubClientǁget_rate_limit__mutmut_52': xǁGitHubClientǁget_rate_limit__mutmut_52, 
        'xǁGitHubClientǁget_rate_limit__mutmut_53': xǁGitHubClientǁget_rate_limit__mutmut_53, 
        'xǁGitHubClientǁget_rate_limit__mutmut_54': xǁGitHubClientǁget_rate_limit__mutmut_54, 
        'xǁGitHubClientǁget_rate_limit__mutmut_55': xǁGitHubClientǁget_rate_limit__mutmut_55, 
        'xǁGitHubClientǁget_rate_limit__mutmut_56': xǁGitHubClientǁget_rate_limit__mutmut_56, 
        'xǁGitHubClientǁget_rate_limit__mutmut_57': xǁGitHubClientǁget_rate_limit__mutmut_57
    }
    
    def get_rate_limit(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientǁget_rate_limit__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientǁget_rate_limit__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_rate_limit.__signature__ = _mutmut_signature(xǁGitHubClientǁget_rate_limit__mutmut_orig)
    xǁGitHubClientǁget_rate_limit__mutmut_orig.__name__ = 'xǁGitHubClientǁget_rate_limit'

    @property
    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Get cached rate limit info from last request."""
        return self._rate_limit


# Synchronous wrapper for convenience
class GitHubClientSync:
    """Synchronous wrapper for GitHubClient.

    Use when async is not available or not needed.
    """

    def xǁGitHubClientSyncǁ__init____mutmut_orig(self, *args: Any, **kwargs: Any):
        self._async_client = GitHubClient(*args, **kwargs)

    def xǁGitHubClientSyncǁ__init____mutmut_1(self, *args: Any, **kwargs: Any):
        self._async_client = None

    def xǁGitHubClientSyncǁ__init____mutmut_2(self, *args: Any, **kwargs: Any):
        self._async_client = GitHubClient(**kwargs)

    def xǁGitHubClientSyncǁ__init____mutmut_3(self, *args: Any, **kwargs: Any):
        self._async_client = GitHubClient(*args, )
    
    xǁGitHubClientSyncǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁ__init____mutmut_1': xǁGitHubClientSyncǁ__init____mutmut_1, 
        'xǁGitHubClientSyncǁ__init____mutmut_2': xǁGitHubClientSyncǁ__init____mutmut_2, 
        'xǁGitHubClientSyncǁ__init____mutmut_3': xǁGitHubClientSyncǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁ__init____mutmut_orig)
    xǁGitHubClientSyncǁ__init____mutmut_orig.__name__ = 'xǁGitHubClientSyncǁ__init__'

    def xǁGitHubClientSyncǁ_run__mutmut_orig(self, coro: Any) -> Any:
        """Run coroutine synchronously."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def xǁGitHubClientSyncǁ_run__mutmut_1(self, coro: Any) -> Any:
        """Run coroutine synchronously."""
        return asyncio.get_event_loop().run_until_complete(None)
    
    xǁGitHubClientSyncǁ_run__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁ_run__mutmut_1': xǁGitHubClientSyncǁ_run__mutmut_1
    }
    
    def _run(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁ_run__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁ_run__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _run.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁ_run__mutmut_orig)
    xǁGitHubClientSyncǁ_run__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁ_run'

    def xǁGitHubClientSyncǁlist_workflows__mutmut_orig(self, *args: Any, **kwargs: Any) -> list[WorkflowInfo]:
        return self._run(self._async_client.list_workflows(*args, **kwargs))

    def xǁGitHubClientSyncǁlist_workflows__mutmut_1(self, *args: Any, **kwargs: Any) -> list[WorkflowInfo]:
        return self._run(None)

    def xǁGitHubClientSyncǁlist_workflows__mutmut_2(self, *args: Any, **kwargs: Any) -> list[WorkflowInfo]:
        return self._run(self._async_client.list_workflows(**kwargs))

    def xǁGitHubClientSyncǁlist_workflows__mutmut_3(self, *args: Any, **kwargs: Any) -> list[WorkflowInfo]:
        return self._run(self._async_client.list_workflows(*args, ))
    
    xǁGitHubClientSyncǁlist_workflows__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁlist_workflows__mutmut_1': xǁGitHubClientSyncǁlist_workflows__mutmut_1, 
        'xǁGitHubClientSyncǁlist_workflows__mutmut_2': xǁGitHubClientSyncǁlist_workflows__mutmut_2, 
        'xǁGitHubClientSyncǁlist_workflows__mutmut_3': xǁGitHubClientSyncǁlist_workflows__mutmut_3
    }
    
    def list_workflows(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁlist_workflows__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁlist_workflows__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflows.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁlist_workflows__mutmut_orig)
    xǁGitHubClientSyncǁlist_workflows__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁlist_workflows'

    def xǁGitHubClientSyncǁget_workflow__mutmut_orig(self, *args: Any, **kwargs: Any) -> WorkflowInfo:
        return self._run(self._async_client.get_workflow(*args, **kwargs))

    def xǁGitHubClientSyncǁget_workflow__mutmut_1(self, *args: Any, **kwargs: Any) -> WorkflowInfo:
        return self._run(None)

    def xǁGitHubClientSyncǁget_workflow__mutmut_2(self, *args: Any, **kwargs: Any) -> WorkflowInfo:
        return self._run(self._async_client.get_workflow(**kwargs))

    def xǁGitHubClientSyncǁget_workflow__mutmut_3(self, *args: Any, **kwargs: Any) -> WorkflowInfo:
        return self._run(self._async_client.get_workflow(*args, ))
    
    xǁGitHubClientSyncǁget_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁget_workflow__mutmut_1': xǁGitHubClientSyncǁget_workflow__mutmut_1, 
        'xǁGitHubClientSyncǁget_workflow__mutmut_2': xǁGitHubClientSyncǁget_workflow__mutmut_2, 
        'xǁGitHubClientSyncǁget_workflow__mutmut_3': xǁGitHubClientSyncǁget_workflow__mutmut_3
    }
    
    def get_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁget_workflow__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁget_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_workflow.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁget_workflow__mutmut_orig)
    xǁGitHubClientSyncǁget_workflow__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁget_workflow'

    def xǁGitHubClientSyncǁtrigger_workflow__mutmut_orig(self, *args: Any, **kwargs: Any) -> Optional[int]:
        return self._run(self._async_client.trigger_workflow(*args, **kwargs))

    def xǁGitHubClientSyncǁtrigger_workflow__mutmut_1(self, *args: Any, **kwargs: Any) -> Optional[int]:
        return self._run(None)

    def xǁGitHubClientSyncǁtrigger_workflow__mutmut_2(self, *args: Any, **kwargs: Any) -> Optional[int]:
        return self._run(self._async_client.trigger_workflow(**kwargs))

    def xǁGitHubClientSyncǁtrigger_workflow__mutmut_3(self, *args: Any, **kwargs: Any) -> Optional[int]:
        return self._run(self._async_client.trigger_workflow(*args, ))
    
    xǁGitHubClientSyncǁtrigger_workflow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁtrigger_workflow__mutmut_1': xǁGitHubClientSyncǁtrigger_workflow__mutmut_1, 
        'xǁGitHubClientSyncǁtrigger_workflow__mutmut_2': xǁGitHubClientSyncǁtrigger_workflow__mutmut_2, 
        'xǁGitHubClientSyncǁtrigger_workflow__mutmut_3': xǁGitHubClientSyncǁtrigger_workflow__mutmut_3
    }
    
    def trigger_workflow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁtrigger_workflow__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁtrigger_workflow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    trigger_workflow.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁtrigger_workflow__mutmut_orig)
    xǁGitHubClientSyncǁtrigger_workflow__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁtrigger_workflow'

    def xǁGitHubClientSyncǁlist_workflow_runs__mutmut_orig(
        self, *args: Any, **kwargs: Any
    ) -> list[WorkflowRun]:
        return self._run(
            self._async_client.list_workflow_runs(*args, **kwargs)
        )

    def xǁGitHubClientSyncǁlist_workflow_runs__mutmut_1(
        self, *args: Any, **kwargs: Any
    ) -> list[WorkflowRun]:
        return self._run(
            None
        )

    def xǁGitHubClientSyncǁlist_workflow_runs__mutmut_2(
        self, *args: Any, **kwargs: Any
    ) -> list[WorkflowRun]:
        return self._run(
            self._async_client.list_workflow_runs(**kwargs)
        )

    def xǁGitHubClientSyncǁlist_workflow_runs__mutmut_3(
        self, *args: Any, **kwargs: Any
    ) -> list[WorkflowRun]:
        return self._run(
            self._async_client.list_workflow_runs(*args, )
        )
    
    xǁGitHubClientSyncǁlist_workflow_runs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁlist_workflow_runs__mutmut_1': xǁGitHubClientSyncǁlist_workflow_runs__mutmut_1, 
        'xǁGitHubClientSyncǁlist_workflow_runs__mutmut_2': xǁGitHubClientSyncǁlist_workflow_runs__mutmut_2, 
        'xǁGitHubClientSyncǁlist_workflow_runs__mutmut_3': xǁGitHubClientSyncǁlist_workflow_runs__mutmut_3
    }
    
    def list_workflow_runs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁlist_workflow_runs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁlist_workflow_runs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflow_runs.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁlist_workflow_runs__mutmut_orig)
    xǁGitHubClientSyncǁlist_workflow_runs__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁlist_workflow_runs'

    def xǁGitHubClientSyncǁget_workflow_run__mutmut_orig(self, *args: Any, **kwargs: Any) -> WorkflowRun:
        return self._run(self._async_client.get_workflow_run(*args, **kwargs))

    def xǁGitHubClientSyncǁget_workflow_run__mutmut_1(self, *args: Any, **kwargs: Any) -> WorkflowRun:
        return self._run(None)

    def xǁGitHubClientSyncǁget_workflow_run__mutmut_2(self, *args: Any, **kwargs: Any) -> WorkflowRun:
        return self._run(self._async_client.get_workflow_run(**kwargs))

    def xǁGitHubClientSyncǁget_workflow_run__mutmut_3(self, *args: Any, **kwargs: Any) -> WorkflowRun:
        return self._run(self._async_client.get_workflow_run(*args, ))
    
    xǁGitHubClientSyncǁget_workflow_run__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁget_workflow_run__mutmut_1': xǁGitHubClientSyncǁget_workflow_run__mutmut_1, 
        'xǁGitHubClientSyncǁget_workflow_run__mutmut_2': xǁGitHubClientSyncǁget_workflow_run__mutmut_2, 
        'xǁGitHubClientSyncǁget_workflow_run__mutmut_3': xǁGitHubClientSyncǁget_workflow_run__mutmut_3
    }
    
    def get_workflow_run(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁget_workflow_run__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁget_workflow_run__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_workflow_run.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁget_workflow_run__mutmut_orig)
    xǁGitHubClientSyncǁget_workflow_run__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁget_workflow_run'

    def xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_orig(self, *args: Any, **kwargs: Any) -> list[WorkflowJob]:
        return self._run(
            self._async_client.list_workflow_jobs(*args, **kwargs)
        )

    def xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_1(self, *args: Any, **kwargs: Any) -> list[WorkflowJob]:
        return self._run(
            None
        )

    def xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_2(self, *args: Any, **kwargs: Any) -> list[WorkflowJob]:
        return self._run(
            self._async_client.list_workflow_jobs(**kwargs)
        )

    def xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_3(self, *args: Any, **kwargs: Any) -> list[WorkflowJob]:
        return self._run(
            self._async_client.list_workflow_jobs(*args, )
        )
    
    xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_1': xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_1, 
        'xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_2': xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_2, 
        'xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_3': xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_3
    }
    
    def list_workflow_jobs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_workflow_jobs.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_orig)
    xǁGitHubClientSyncǁlist_workflow_jobs__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁlist_workflow_jobs'

    def xǁGitHubClientSyncǁget_job_logs__mutmut_orig(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_job_logs(*args, **kwargs))

    def xǁGitHubClientSyncǁget_job_logs__mutmut_1(self, *args: Any, **kwargs: Any) -> str:
        return self._run(None)

    def xǁGitHubClientSyncǁget_job_logs__mutmut_2(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_job_logs(**kwargs))

    def xǁGitHubClientSyncǁget_job_logs__mutmut_3(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_job_logs(*args, ))
    
    xǁGitHubClientSyncǁget_job_logs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁget_job_logs__mutmut_1': xǁGitHubClientSyncǁget_job_logs__mutmut_1, 
        'xǁGitHubClientSyncǁget_job_logs__mutmut_2': xǁGitHubClientSyncǁget_job_logs__mutmut_2, 
        'xǁGitHubClientSyncǁget_job_logs__mutmut_3': xǁGitHubClientSyncǁget_job_logs__mutmut_3
    }
    
    def get_job_logs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁget_job_logs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁget_job_logs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_job_logs.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁget_job_logs__mutmut_orig)
    xǁGitHubClientSyncǁget_job_logs__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁget_job_logs'

    def xǁGitHubClientSyncǁlist_run_artifacts__mutmut_orig(
        self, *args: Any, **kwargs: Any
    ) -> list[ArtifactInfo]:
        return self._run(
            self._async_client.list_run_artifacts(*args, **kwargs)
        )

    def xǁGitHubClientSyncǁlist_run_artifacts__mutmut_1(
        self, *args: Any, **kwargs: Any
    ) -> list[ArtifactInfo]:
        return self._run(
            None
        )

    def xǁGitHubClientSyncǁlist_run_artifacts__mutmut_2(
        self, *args: Any, **kwargs: Any
    ) -> list[ArtifactInfo]:
        return self._run(
            self._async_client.list_run_artifacts(**kwargs)
        )

    def xǁGitHubClientSyncǁlist_run_artifacts__mutmut_3(
        self, *args: Any, **kwargs: Any
    ) -> list[ArtifactInfo]:
        return self._run(
            self._async_client.list_run_artifacts(*args, )
        )
    
    xǁGitHubClientSyncǁlist_run_artifacts__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁlist_run_artifacts__mutmut_1': xǁGitHubClientSyncǁlist_run_artifacts__mutmut_1, 
        'xǁGitHubClientSyncǁlist_run_artifacts__mutmut_2': xǁGitHubClientSyncǁlist_run_artifacts__mutmut_2, 
        'xǁGitHubClientSyncǁlist_run_artifacts__mutmut_3': xǁGitHubClientSyncǁlist_run_artifacts__mutmut_3
    }
    
    def list_run_artifacts(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁlist_run_artifacts__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁlist_run_artifacts__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_run_artifacts.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁlist_run_artifacts__mutmut_orig)
    xǁGitHubClientSyncǁlist_run_artifacts__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁlist_run_artifacts'

    def xǁGitHubClientSyncǁdownload_artifact__mutmut_orig(self, *args: Any, **kwargs: Any) -> bytes:
        return self._run(self._async_client.download_artifact(*args, **kwargs))

    def xǁGitHubClientSyncǁdownload_artifact__mutmut_1(self, *args: Any, **kwargs: Any) -> bytes:
        return self._run(None)

    def xǁGitHubClientSyncǁdownload_artifact__mutmut_2(self, *args: Any, **kwargs: Any) -> bytes:
        return self._run(self._async_client.download_artifact(**kwargs))

    def xǁGitHubClientSyncǁdownload_artifact__mutmut_3(self, *args: Any, **kwargs: Any) -> bytes:
        return self._run(self._async_client.download_artifact(*args, ))
    
    xǁGitHubClientSyncǁdownload_artifact__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁdownload_artifact__mutmut_1': xǁGitHubClientSyncǁdownload_artifact__mutmut_1, 
        'xǁGitHubClientSyncǁdownload_artifact__mutmut_2': xǁGitHubClientSyncǁdownload_artifact__mutmut_2, 
        'xǁGitHubClientSyncǁdownload_artifact__mutmut_3': xǁGitHubClientSyncǁdownload_artifact__mutmut_3
    }
    
    def download_artifact(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁdownload_artifact__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁdownload_artifact__mutmut_mutants"), args, kwargs, self)
        return result 
    
    download_artifact.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁdownload_artifact__mutmut_orig)
    xǁGitHubClientSyncǁdownload_artifact__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁdownload_artifact'

    def xǁGitHubClientSyncǁget_check_run__mutmut_orig(self, *args: Any, **kwargs: Any) -> CheckRun:
        return self._run(self._async_client.get_check_run(*args, **kwargs))

    def xǁGitHubClientSyncǁget_check_run__mutmut_1(self, *args: Any, **kwargs: Any) -> CheckRun:
        return self._run(None)

    def xǁGitHubClientSyncǁget_check_run__mutmut_2(self, *args: Any, **kwargs: Any) -> CheckRun:
        return self._run(self._async_client.get_check_run(**kwargs))

    def xǁGitHubClientSyncǁget_check_run__mutmut_3(self, *args: Any, **kwargs: Any) -> CheckRun:
        return self._run(self._async_client.get_check_run(*args, ))
    
    xǁGitHubClientSyncǁget_check_run__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁget_check_run__mutmut_1': xǁGitHubClientSyncǁget_check_run__mutmut_1, 
        'xǁGitHubClientSyncǁget_check_run__mutmut_2': xǁGitHubClientSyncǁget_check_run__mutmut_2, 
        'xǁGitHubClientSyncǁget_check_run__mutmut_3': xǁGitHubClientSyncǁget_check_run__mutmut_3
    }
    
    def get_check_run(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁget_check_run__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁget_check_run__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_check_run.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁget_check_run__mutmut_orig)
    xǁGitHubClientSyncǁget_check_run__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁget_check_run'

    def xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_orig(self, *args: Any, **kwargs: Any) -> list[CheckRun]:
        return self._run(self._async_client.list_check_runs_for_ref(*args, **kwargs))

    def xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_1(self, *args: Any, **kwargs: Any) -> list[CheckRun]:
        return self._run(None)

    def xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_2(self, *args: Any, **kwargs: Any) -> list[CheckRun]:
        return self._run(self._async_client.list_check_runs_for_ref(**kwargs))

    def xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_3(self, *args: Any, **kwargs: Any) -> list[CheckRun]:
        return self._run(self._async_client.list_check_runs_for_ref(*args, ))
    
    xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_1': xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_1, 
        'xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_2': xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_2, 
        'xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_3': xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_3
    }
    
    def list_check_runs_for_ref(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_check_runs_for_ref.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_orig)
    xǁGitHubClientSyncǁlist_check_runs_for_ref__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁlist_check_runs_for_ref'

    def xǁGitHubClientSyncǁget_check_run_logs__mutmut_orig(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_check_run_logs(*args, **kwargs))

    def xǁGitHubClientSyncǁget_check_run_logs__mutmut_1(self, *args: Any, **kwargs: Any) -> str:
        return self._run(None)

    def xǁGitHubClientSyncǁget_check_run_logs__mutmut_2(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_check_run_logs(**kwargs))

    def xǁGitHubClientSyncǁget_check_run_logs__mutmut_3(self, *args: Any, **kwargs: Any) -> str:
        return self._run(self._async_client.get_check_run_logs(*args, ))
    
    xǁGitHubClientSyncǁget_check_run_logs__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁget_check_run_logs__mutmut_1': xǁGitHubClientSyncǁget_check_run_logs__mutmut_1, 
        'xǁGitHubClientSyncǁget_check_run_logs__mutmut_2': xǁGitHubClientSyncǁget_check_run_logs__mutmut_2, 
        'xǁGitHubClientSyncǁget_check_run_logs__mutmut_3': xǁGitHubClientSyncǁget_check_run_logs__mutmut_3
    }
    
    def get_check_run_logs(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁget_check_run_logs__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁget_check_run_logs__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_check_run_logs.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁget_check_run_logs__mutmut_orig)
    xǁGitHubClientSyncǁget_check_run_logs__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁget_check_run_logs'

    def xǁGitHubClientSyncǁget_rate_limit__mutmut_orig(self, *args: Any, **kwargs: Any) -> RateLimitInfo:
        return self._run(self._async_client.get_rate_limit(*args, **kwargs))

    def xǁGitHubClientSyncǁget_rate_limit__mutmut_1(self, *args: Any, **kwargs: Any) -> RateLimitInfo:
        return self._run(None)

    def xǁGitHubClientSyncǁget_rate_limit__mutmut_2(self, *args: Any, **kwargs: Any) -> RateLimitInfo:
        return self._run(self._async_client.get_rate_limit(**kwargs))

    def xǁGitHubClientSyncǁget_rate_limit__mutmut_3(self, *args: Any, **kwargs: Any) -> RateLimitInfo:
        return self._run(self._async_client.get_rate_limit(*args, ))
    
    xǁGitHubClientSyncǁget_rate_limit__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁGitHubClientSyncǁget_rate_limit__mutmut_1': xǁGitHubClientSyncǁget_rate_limit__mutmut_1, 
        'xǁGitHubClientSyncǁget_rate_limit__mutmut_2': xǁGitHubClientSyncǁget_rate_limit__mutmut_2, 
        'xǁGitHubClientSyncǁget_rate_limit__mutmut_3': xǁGitHubClientSyncǁget_rate_limit__mutmut_3
    }
    
    def get_rate_limit(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁGitHubClientSyncǁget_rate_limit__mutmut_orig"), object.__getattribute__(self, "xǁGitHubClientSyncǁget_rate_limit__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_rate_limit.__signature__ = _mutmut_signature(xǁGitHubClientSyncǁget_rate_limit__mutmut_orig)
    xǁGitHubClientSyncǁget_rate_limit__mutmut_orig.__name__ = 'xǁGitHubClientSyncǁget_rate_limit'
