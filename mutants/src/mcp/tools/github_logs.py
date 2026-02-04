"""MCP tool for fetching GitHub Actions logs.

Provides Model Context Protocol (MCP) tool interface for fetching logs
from GitHub Actions workflows, jobs, and check runs.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

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


class FetchCheckRunLogsInput(BaseModel):
    """Input schema for fetch_check_run_logs tool."""

    owner: str = Field(..., description="Repository owner (e.g., 'Aries-Serpent')")
    repo: str = Field(..., description="Repository name (e.g., '_codex_')")
    check_run_id: int = Field(..., description="Check run ID to fetch logs for")


class FetchJobLogsInput(BaseModel):
    """Input schema for fetch_job_logs tool."""

    owner: str = Field(..., description="Repository owner (e.g., 'Aries-Serpent')")
    repo: str = Field(..., description="Repository name (e.g., '_codex_')")
    job_id: int = Field(..., description="Job ID to fetch logs for")


class ListCheckRunsInput(BaseModel):
    """Input schema for list_check_runs tool."""

    owner: str = Field(..., description="Repository owner (e.g., 'Aries-Serpent')")
    repo: str = Field(..., description="Repository name (e.g., '_codex_')")
    ref: str = Field(..., description="Git reference (commit SHA, branch, or tag)")
    status: Optional[str] = Field(None, description="Filter by status (queued, in_progress, completed)")
    check_name: Optional[str] = Field(None, description="Filter by check run name")


def _get_github_client():
    """Get GitHub client instance."""
    from src.services.github.client import GitHubClientSync
    return GitHubClientSync()


def x_fetch_check_run_logs__mutmut_orig(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_1(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = None
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_2(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = None
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_3(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = None
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_4(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            None,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_5(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            None,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_6(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            None
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_7(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_8(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_9(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_10(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = None
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_11(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            None,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_12(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            None,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_13(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            None
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_14(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_15(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_16(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_17(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "XXsuccessXX": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_18(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "SUCCESS": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_19(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": False,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_20(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "XXcheck_run_idXX": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_21(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "CHECK_RUN_ID": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_22(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "XXownerXX": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_23(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "OWNER": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_24(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "XXrepoXX": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_25(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "REPO": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_26(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "XXcheck_runXX": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_27(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "CHECK_RUN": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_28(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "XXidXX": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_29(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "ID": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_30(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "XXnameXX": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_31(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "NAME": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_32(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "XXstatusXX": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_33(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "STATUS": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_34(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "XXconclusionXX": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_35(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "CONCLUSION": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_36(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "XXhtml_urlXX": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_37(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "HTML_URL": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_38(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "XXstarted_atXX": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_39(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "STARTED_AT": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_40(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "XXcompleted_atXX": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_41(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "COMPLETED_AT": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_42(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "XXlogsXX": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_43(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "LOGS": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_44(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(None, exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_45(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=None)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_46(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_47(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", )
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_48(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=False)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_49(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "XXsuccessXX": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_50(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "SUCCESS": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_51(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": True,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_52(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "XXerrorXX": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_53(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "ERROR": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_54(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(None),
            "error_type": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_55(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "XXerror_typeXX": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_56(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "ERROR_TYPE": type(e).__name__,
        }


def x_fetch_check_run_logs__mutmut_57(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions check run.
    
    This MCP tool fetches logs from a specific GitHub Actions check run by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - check_run_id: Check run ID
    
    Returns:
        Dictionary containing check run details and logs.
    
    Example:
        ```python
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchCheckRunLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch check run details
        check_run = client.get_check_run(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        # Fetch logs
        logs = client.get_check_run_logs(
            input_data.owner,
            input_data.repo,
            input_data.check_run_id
        )
        
        return {
            "success": True,
            "check_run_id": input_data.check_run_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "check_run": {
                "id": check_run.id,
                "name": check_run.name,
                "status": check_run.status,
                "conclusion": check_run.conclusion,
                "html_url": check_run.html_url,
                "started_at": check_run.started_at.isoformat() if check_run.started_at else None,
                "completed_at": check_run.completed_at.isoformat() if check_run.completed_at else None,
            },
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch check run logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(None).__name__,
        }

x_fetch_check_run_logs__mutmut_mutants : ClassVar[MutantDict] = {
'x_fetch_check_run_logs__mutmut_1': x_fetch_check_run_logs__mutmut_1, 
    'x_fetch_check_run_logs__mutmut_2': x_fetch_check_run_logs__mutmut_2, 
    'x_fetch_check_run_logs__mutmut_3': x_fetch_check_run_logs__mutmut_3, 
    'x_fetch_check_run_logs__mutmut_4': x_fetch_check_run_logs__mutmut_4, 
    'x_fetch_check_run_logs__mutmut_5': x_fetch_check_run_logs__mutmut_5, 
    'x_fetch_check_run_logs__mutmut_6': x_fetch_check_run_logs__mutmut_6, 
    'x_fetch_check_run_logs__mutmut_7': x_fetch_check_run_logs__mutmut_7, 
    'x_fetch_check_run_logs__mutmut_8': x_fetch_check_run_logs__mutmut_8, 
    'x_fetch_check_run_logs__mutmut_9': x_fetch_check_run_logs__mutmut_9, 
    'x_fetch_check_run_logs__mutmut_10': x_fetch_check_run_logs__mutmut_10, 
    'x_fetch_check_run_logs__mutmut_11': x_fetch_check_run_logs__mutmut_11, 
    'x_fetch_check_run_logs__mutmut_12': x_fetch_check_run_logs__mutmut_12, 
    'x_fetch_check_run_logs__mutmut_13': x_fetch_check_run_logs__mutmut_13, 
    'x_fetch_check_run_logs__mutmut_14': x_fetch_check_run_logs__mutmut_14, 
    'x_fetch_check_run_logs__mutmut_15': x_fetch_check_run_logs__mutmut_15, 
    'x_fetch_check_run_logs__mutmut_16': x_fetch_check_run_logs__mutmut_16, 
    'x_fetch_check_run_logs__mutmut_17': x_fetch_check_run_logs__mutmut_17, 
    'x_fetch_check_run_logs__mutmut_18': x_fetch_check_run_logs__mutmut_18, 
    'x_fetch_check_run_logs__mutmut_19': x_fetch_check_run_logs__mutmut_19, 
    'x_fetch_check_run_logs__mutmut_20': x_fetch_check_run_logs__mutmut_20, 
    'x_fetch_check_run_logs__mutmut_21': x_fetch_check_run_logs__mutmut_21, 
    'x_fetch_check_run_logs__mutmut_22': x_fetch_check_run_logs__mutmut_22, 
    'x_fetch_check_run_logs__mutmut_23': x_fetch_check_run_logs__mutmut_23, 
    'x_fetch_check_run_logs__mutmut_24': x_fetch_check_run_logs__mutmut_24, 
    'x_fetch_check_run_logs__mutmut_25': x_fetch_check_run_logs__mutmut_25, 
    'x_fetch_check_run_logs__mutmut_26': x_fetch_check_run_logs__mutmut_26, 
    'x_fetch_check_run_logs__mutmut_27': x_fetch_check_run_logs__mutmut_27, 
    'x_fetch_check_run_logs__mutmut_28': x_fetch_check_run_logs__mutmut_28, 
    'x_fetch_check_run_logs__mutmut_29': x_fetch_check_run_logs__mutmut_29, 
    'x_fetch_check_run_logs__mutmut_30': x_fetch_check_run_logs__mutmut_30, 
    'x_fetch_check_run_logs__mutmut_31': x_fetch_check_run_logs__mutmut_31, 
    'x_fetch_check_run_logs__mutmut_32': x_fetch_check_run_logs__mutmut_32, 
    'x_fetch_check_run_logs__mutmut_33': x_fetch_check_run_logs__mutmut_33, 
    'x_fetch_check_run_logs__mutmut_34': x_fetch_check_run_logs__mutmut_34, 
    'x_fetch_check_run_logs__mutmut_35': x_fetch_check_run_logs__mutmut_35, 
    'x_fetch_check_run_logs__mutmut_36': x_fetch_check_run_logs__mutmut_36, 
    'x_fetch_check_run_logs__mutmut_37': x_fetch_check_run_logs__mutmut_37, 
    'x_fetch_check_run_logs__mutmut_38': x_fetch_check_run_logs__mutmut_38, 
    'x_fetch_check_run_logs__mutmut_39': x_fetch_check_run_logs__mutmut_39, 
    'x_fetch_check_run_logs__mutmut_40': x_fetch_check_run_logs__mutmut_40, 
    'x_fetch_check_run_logs__mutmut_41': x_fetch_check_run_logs__mutmut_41, 
    'x_fetch_check_run_logs__mutmut_42': x_fetch_check_run_logs__mutmut_42, 
    'x_fetch_check_run_logs__mutmut_43': x_fetch_check_run_logs__mutmut_43, 
    'x_fetch_check_run_logs__mutmut_44': x_fetch_check_run_logs__mutmut_44, 
    'x_fetch_check_run_logs__mutmut_45': x_fetch_check_run_logs__mutmut_45, 
    'x_fetch_check_run_logs__mutmut_46': x_fetch_check_run_logs__mutmut_46, 
    'x_fetch_check_run_logs__mutmut_47': x_fetch_check_run_logs__mutmut_47, 
    'x_fetch_check_run_logs__mutmut_48': x_fetch_check_run_logs__mutmut_48, 
    'x_fetch_check_run_logs__mutmut_49': x_fetch_check_run_logs__mutmut_49, 
    'x_fetch_check_run_logs__mutmut_50': x_fetch_check_run_logs__mutmut_50, 
    'x_fetch_check_run_logs__mutmut_51': x_fetch_check_run_logs__mutmut_51, 
    'x_fetch_check_run_logs__mutmut_52': x_fetch_check_run_logs__mutmut_52, 
    'x_fetch_check_run_logs__mutmut_53': x_fetch_check_run_logs__mutmut_53, 
    'x_fetch_check_run_logs__mutmut_54': x_fetch_check_run_logs__mutmut_54, 
    'x_fetch_check_run_logs__mutmut_55': x_fetch_check_run_logs__mutmut_55, 
    'x_fetch_check_run_logs__mutmut_56': x_fetch_check_run_logs__mutmut_56, 
    'x_fetch_check_run_logs__mutmut_57': x_fetch_check_run_logs__mutmut_57
}

def fetch_check_run_logs(*args, **kwargs):
    result = _mutmut_trampoline(x_fetch_check_run_logs__mutmut_orig, x_fetch_check_run_logs__mutmut_mutants, args, kwargs)
    return result 

fetch_check_run_logs.__signature__ = _mutmut_signature(x_fetch_check_run_logs__mutmut_orig)
x_fetch_check_run_logs__mutmut_orig.__name__ = 'x_fetch_check_run_logs'


def x_fetch_job_logs__mutmut_orig(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_1(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = None
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_2(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = None
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_3(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = None
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_4(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            None,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_5(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            None,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_6(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            None
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_7(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_8(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_9(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_10(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "XXsuccessXX": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_11(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "SUCCESS": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_12(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": False,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_13(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "XXjob_idXX": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_14(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "JOB_ID": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_15(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "XXownerXX": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_16(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "OWNER": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_17(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "XXrepoXX": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_18(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "REPO": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_19(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "XXlogsXX": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_20(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "LOGS": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_21(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(None, exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_22(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=None)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_23(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_24(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", )
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_25(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=False)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_26(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "XXsuccessXX": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_27(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "SUCCESS": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_28(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": True,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_29(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "XXerrorXX": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_30(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "ERROR": str(e),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_31(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(None),
            "error_type": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_32(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "XXerror_typeXX": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_33(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "ERROR_TYPE": type(e).__name__,
        }


def x_fetch_job_logs__mutmut_34(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch logs from a GitHub Actions workflow job.
    
    This MCP tool fetches logs from a specific GitHub Actions job by ID.
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - job_id: Job ID
    
    Returns:
        Dictionary containing job logs.
    
    Example:
        ```python
        result = fetch_job_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "job_id": 12345678
        })
        print(result["logs"])
        ```
    """
    try:
        # Validate input
        input_data = FetchJobLogsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        # Fetch logs
        logs = client.get_job_logs(
            input_data.owner,
            input_data.repo,
            input_data.job_id
        )
        
        return {
            "success": True,
            "job_id": input_data.job_id,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "logs": logs,
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch job logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(None).__name__,
        }

x_fetch_job_logs__mutmut_mutants : ClassVar[MutantDict] = {
'x_fetch_job_logs__mutmut_1': x_fetch_job_logs__mutmut_1, 
    'x_fetch_job_logs__mutmut_2': x_fetch_job_logs__mutmut_2, 
    'x_fetch_job_logs__mutmut_3': x_fetch_job_logs__mutmut_3, 
    'x_fetch_job_logs__mutmut_4': x_fetch_job_logs__mutmut_4, 
    'x_fetch_job_logs__mutmut_5': x_fetch_job_logs__mutmut_5, 
    'x_fetch_job_logs__mutmut_6': x_fetch_job_logs__mutmut_6, 
    'x_fetch_job_logs__mutmut_7': x_fetch_job_logs__mutmut_7, 
    'x_fetch_job_logs__mutmut_8': x_fetch_job_logs__mutmut_8, 
    'x_fetch_job_logs__mutmut_9': x_fetch_job_logs__mutmut_9, 
    'x_fetch_job_logs__mutmut_10': x_fetch_job_logs__mutmut_10, 
    'x_fetch_job_logs__mutmut_11': x_fetch_job_logs__mutmut_11, 
    'x_fetch_job_logs__mutmut_12': x_fetch_job_logs__mutmut_12, 
    'x_fetch_job_logs__mutmut_13': x_fetch_job_logs__mutmut_13, 
    'x_fetch_job_logs__mutmut_14': x_fetch_job_logs__mutmut_14, 
    'x_fetch_job_logs__mutmut_15': x_fetch_job_logs__mutmut_15, 
    'x_fetch_job_logs__mutmut_16': x_fetch_job_logs__mutmut_16, 
    'x_fetch_job_logs__mutmut_17': x_fetch_job_logs__mutmut_17, 
    'x_fetch_job_logs__mutmut_18': x_fetch_job_logs__mutmut_18, 
    'x_fetch_job_logs__mutmut_19': x_fetch_job_logs__mutmut_19, 
    'x_fetch_job_logs__mutmut_20': x_fetch_job_logs__mutmut_20, 
    'x_fetch_job_logs__mutmut_21': x_fetch_job_logs__mutmut_21, 
    'x_fetch_job_logs__mutmut_22': x_fetch_job_logs__mutmut_22, 
    'x_fetch_job_logs__mutmut_23': x_fetch_job_logs__mutmut_23, 
    'x_fetch_job_logs__mutmut_24': x_fetch_job_logs__mutmut_24, 
    'x_fetch_job_logs__mutmut_25': x_fetch_job_logs__mutmut_25, 
    'x_fetch_job_logs__mutmut_26': x_fetch_job_logs__mutmut_26, 
    'x_fetch_job_logs__mutmut_27': x_fetch_job_logs__mutmut_27, 
    'x_fetch_job_logs__mutmut_28': x_fetch_job_logs__mutmut_28, 
    'x_fetch_job_logs__mutmut_29': x_fetch_job_logs__mutmut_29, 
    'x_fetch_job_logs__mutmut_30': x_fetch_job_logs__mutmut_30, 
    'x_fetch_job_logs__mutmut_31': x_fetch_job_logs__mutmut_31, 
    'x_fetch_job_logs__mutmut_32': x_fetch_job_logs__mutmut_32, 
    'x_fetch_job_logs__mutmut_33': x_fetch_job_logs__mutmut_33, 
    'x_fetch_job_logs__mutmut_34': x_fetch_job_logs__mutmut_34
}

def fetch_job_logs(*args, **kwargs):
    result = _mutmut_trampoline(x_fetch_job_logs__mutmut_orig, x_fetch_job_logs__mutmut_mutants, args, kwargs)
    return result 

fetch_job_logs.__signature__ = _mutmut_signature(x_fetch_job_logs__mutmut_orig)
x_fetch_job_logs__mutmut_orig.__name__ = 'x_fetch_job_logs'


def x_list_check_runs__mutmut_orig(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_1(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = None
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_2(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = None
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_3(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_4(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(None) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_5(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = None
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_6(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            None,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_7(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            None,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_8(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            None,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_9(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=None,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_10(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=None
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_11(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_12(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_13(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_14(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_15(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_16(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = None
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_17(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "XXidXX": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_18(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "ID": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_19(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "XXnameXX": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_20(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "NAME": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_21(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "XXstatusXX": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_22(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "STATUS": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_23(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "XXconclusionXX": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_24(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "CONCLUSION": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_25(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "XXhtml_urlXX": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_26(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "HTML_URL": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_27(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "XXstarted_atXX": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_28(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "STARTED_AT": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_29(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "XXcompleted_atXX": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_30(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "COMPLETED_AT": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_31(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "XXsuccessXX": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_32(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "SUCCESS": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_33(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": False,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_34(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "XXownerXX": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_35(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "OWNER": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_36(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "XXrepoXX": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_37(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "REPO": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_38(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "XXrefXX": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_39(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "REF": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_40(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "XXtotal_countXX": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_41(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "TOTAL_COUNT": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_42(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "XXcheck_runsXX": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_43(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "CHECK_RUNS": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_44(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(None, exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_45(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=None)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_46(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_47(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", )
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_48(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=False)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_49(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "XXsuccessXX": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_50(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "SUCCESS": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_51(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": True,
            "error": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_52(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "XXerrorXX": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_53(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "ERROR": str(e),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_54(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(None),
            "error_type": type(e).__name__,
        }


def x_list_check_runs__mutmut_55(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "XXerror_typeXX": type(e).__name__,
        }


def x_list_check_runs__mutmut_56(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "ERROR_TYPE": type(e).__name__,
        }


def x_list_check_runs__mutmut_57(params: dict[str, Any]) -> dict[str, Any]:
    """List check runs for a git reference.
    
    This MCP tool lists check runs for a specific git reference (commit, branch, or tag).
    
    Args:
        params: Dictionary containing:
            - owner: Repository owner
            - repo: Repository name
            - ref: Git reference (commit SHA, branch, or tag)
            - status: Optional status filter
            - check_name: Optional check name filter
    
    Returns:
        Dictionary containing list of check runs.
    
    Example:
        ```python
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed"
        })
        for run in result["check_runs"]:
            print(f"{run['id']}: {run['name']} - {run['conclusion']}")
        ```
    """
    try:
        # Validate input
        input_data = ListCheckRunsInput(**params)
        
        # Get client
        client = _get_github_client()
        
        from src.services.github.types import CheckRunStatus
        status_enum = CheckRunStatus(input_data.status) if input_data.status else None
        
        # Fetch check runs
        check_runs = client.list_check_runs_for_ref(
            input_data.owner,
            input_data.repo,
            input_data.ref,
            check_name=input_data.check_name,
            status=status_enum
        )
        
        # Convert to serializable format
        check_runs_list = [
            {
                "id": run.id,
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "html_url": run.html_url,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            }
            for run in check_runs
        ]
        
        return {
            "success": True,
            "owner": input_data.owner,
            "repo": input_data.repo,
            "ref": input_data.ref,
            "total_count": len(check_runs_list),
            "check_runs": check_runs_list,
        }
        
    except Exception as e:
        logger.error(f"Failed to list check runs: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(None).__name__,
        }

x_list_check_runs__mutmut_mutants : ClassVar[MutantDict] = {
'x_list_check_runs__mutmut_1': x_list_check_runs__mutmut_1, 
    'x_list_check_runs__mutmut_2': x_list_check_runs__mutmut_2, 
    'x_list_check_runs__mutmut_3': x_list_check_runs__mutmut_3, 
    'x_list_check_runs__mutmut_4': x_list_check_runs__mutmut_4, 
    'x_list_check_runs__mutmut_5': x_list_check_runs__mutmut_5, 
    'x_list_check_runs__mutmut_6': x_list_check_runs__mutmut_6, 
    'x_list_check_runs__mutmut_7': x_list_check_runs__mutmut_7, 
    'x_list_check_runs__mutmut_8': x_list_check_runs__mutmut_8, 
    'x_list_check_runs__mutmut_9': x_list_check_runs__mutmut_9, 
    'x_list_check_runs__mutmut_10': x_list_check_runs__mutmut_10, 
    'x_list_check_runs__mutmut_11': x_list_check_runs__mutmut_11, 
    'x_list_check_runs__mutmut_12': x_list_check_runs__mutmut_12, 
    'x_list_check_runs__mutmut_13': x_list_check_runs__mutmut_13, 
    'x_list_check_runs__mutmut_14': x_list_check_runs__mutmut_14, 
    'x_list_check_runs__mutmut_15': x_list_check_runs__mutmut_15, 
    'x_list_check_runs__mutmut_16': x_list_check_runs__mutmut_16, 
    'x_list_check_runs__mutmut_17': x_list_check_runs__mutmut_17, 
    'x_list_check_runs__mutmut_18': x_list_check_runs__mutmut_18, 
    'x_list_check_runs__mutmut_19': x_list_check_runs__mutmut_19, 
    'x_list_check_runs__mutmut_20': x_list_check_runs__mutmut_20, 
    'x_list_check_runs__mutmut_21': x_list_check_runs__mutmut_21, 
    'x_list_check_runs__mutmut_22': x_list_check_runs__mutmut_22, 
    'x_list_check_runs__mutmut_23': x_list_check_runs__mutmut_23, 
    'x_list_check_runs__mutmut_24': x_list_check_runs__mutmut_24, 
    'x_list_check_runs__mutmut_25': x_list_check_runs__mutmut_25, 
    'x_list_check_runs__mutmut_26': x_list_check_runs__mutmut_26, 
    'x_list_check_runs__mutmut_27': x_list_check_runs__mutmut_27, 
    'x_list_check_runs__mutmut_28': x_list_check_runs__mutmut_28, 
    'x_list_check_runs__mutmut_29': x_list_check_runs__mutmut_29, 
    'x_list_check_runs__mutmut_30': x_list_check_runs__mutmut_30, 
    'x_list_check_runs__mutmut_31': x_list_check_runs__mutmut_31, 
    'x_list_check_runs__mutmut_32': x_list_check_runs__mutmut_32, 
    'x_list_check_runs__mutmut_33': x_list_check_runs__mutmut_33, 
    'x_list_check_runs__mutmut_34': x_list_check_runs__mutmut_34, 
    'x_list_check_runs__mutmut_35': x_list_check_runs__mutmut_35, 
    'x_list_check_runs__mutmut_36': x_list_check_runs__mutmut_36, 
    'x_list_check_runs__mutmut_37': x_list_check_runs__mutmut_37, 
    'x_list_check_runs__mutmut_38': x_list_check_runs__mutmut_38, 
    'x_list_check_runs__mutmut_39': x_list_check_runs__mutmut_39, 
    'x_list_check_runs__mutmut_40': x_list_check_runs__mutmut_40, 
    'x_list_check_runs__mutmut_41': x_list_check_runs__mutmut_41, 
    'x_list_check_runs__mutmut_42': x_list_check_runs__mutmut_42, 
    'x_list_check_runs__mutmut_43': x_list_check_runs__mutmut_43, 
    'x_list_check_runs__mutmut_44': x_list_check_runs__mutmut_44, 
    'x_list_check_runs__mutmut_45': x_list_check_runs__mutmut_45, 
    'x_list_check_runs__mutmut_46': x_list_check_runs__mutmut_46, 
    'x_list_check_runs__mutmut_47': x_list_check_runs__mutmut_47, 
    'x_list_check_runs__mutmut_48': x_list_check_runs__mutmut_48, 
    'x_list_check_runs__mutmut_49': x_list_check_runs__mutmut_49, 
    'x_list_check_runs__mutmut_50': x_list_check_runs__mutmut_50, 
    'x_list_check_runs__mutmut_51': x_list_check_runs__mutmut_51, 
    'x_list_check_runs__mutmut_52': x_list_check_runs__mutmut_52, 
    'x_list_check_runs__mutmut_53': x_list_check_runs__mutmut_53, 
    'x_list_check_runs__mutmut_54': x_list_check_runs__mutmut_54, 
    'x_list_check_runs__mutmut_55': x_list_check_runs__mutmut_55, 
    'x_list_check_runs__mutmut_56': x_list_check_runs__mutmut_56, 
    'x_list_check_runs__mutmut_57': x_list_check_runs__mutmut_57
}

def list_check_runs(*args, **kwargs):
    result = _mutmut_trampoline(x_list_check_runs__mutmut_orig, x_list_check_runs__mutmut_mutants, args, kwargs)
    return result 

list_check_runs.__signature__ = _mutmut_signature(x_list_check_runs__mutmut_orig)
x_list_check_runs__mutmut_orig.__name__ = 'x_list_check_runs'


# MCP tool registry metadata
GITHUB_LOGS_TOOLS = {
    "fetch_check_run_logs": {
        "function": fetch_check_run_logs,
        "schema": FetchCheckRunLogsInput.schema(),
        "description": "Fetch logs from a GitHub Actions check run by ID",
        "name": "fetch_check_run_logs",
    },
    "fetch_job_logs": {
        "function": fetch_job_logs,
        "schema": FetchJobLogsInput.schema(),
        "description": "Fetch logs from a GitHub Actions workflow job by ID",
        "name": "fetch_job_logs",
    },
    "list_check_runs": {
        "function": list_check_runs,
        "schema": ListCheckRunsInput.schema(),
        "description": "List check runs for a git reference (commit, branch, or tag)",
        "name": "list_check_runs",
    },
}
