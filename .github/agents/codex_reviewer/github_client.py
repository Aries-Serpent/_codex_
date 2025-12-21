"""
GitHub API Client for Review Operations

Provides integration with GitHub REST API for posting reviews,
managing comments, and interacting with pull requests.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    import urllib.request
    import urllib.parse
    import json as stdlib_json

logger = logging.getLogger(__name__)


@dataclass
class GitHubConfig:
    """GitHub API configuration."""
    token: Optional[str] = None
    base_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> "GitHubConfig":
        """Create configuration from environment variables."""
        return cls(
            token=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"),
            base_url=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
        )


class GitHubAPIClient:
    """
    GitHub API client for PR review operations.
    
    Handles authentication, request formatting, error handling,
    and retry logic for GitHub API interactions.
    """
    
    def __init__(self, config: Optional[GitHubConfig] = None):
        """
        Initialize GitHub API client.
        
        Args:
            config: GitHub configuration (defaults to environment-based config)
        """
        self.config = config or GitHubConfig.from_env()
        
        if not self.config.token:
            logger.warning("No GitHub token configured - API requests will fail")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodexQuantumReviewer/1.0",
        }
        
        if self.config.token:
            headers["Authorization"] = f"token {self.config.token}"
        
        return headers
    
    async def post_review(
        self,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Post a review to a pull request.
        
        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            body: Review body text (markdown)
            event: Review event type (APPROVE, REQUEST_CHANGES, COMMENT)
            comments: Optional inline comments
            
        Returns:
            GitHub API response
            
        Raises:
            Exception: If API request fails
        """
        url = f"{self.config.base_url}/repos/{repo}/pulls/{pr_number}/reviews"
        
        payload = {
            "body": body,
            "event": event,
        }
        
        if comments:
            payload["comments"] = comments
        
        logger.info(f"Posting {event} review to {repo}#{pr_number}")
        
        if HTTPX_AVAILABLE:
            return await self._post_with_httpx(url, payload)
        else:
            return await self._post_with_urllib(url, payload)
    
    async def _post_with_httpx(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Post request using httpx library."""
        async with httpx.AsyncClient() as client:
            for attempt in range(self.config.max_retries):
                try:
                    response = await client.post(
                        url,
                        json=payload,
                        headers=self._get_headers(),
                        timeout=self.config.timeout,
                    )
                    
                    response.raise_for_status()
                    return response.json()
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 422:
                        # Validation error - don't retry
                        logger.error(f"GitHub API validation error: {e.response.text}")
                        raise
                    
                    if attempt < self.config.max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request failed, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                        
                except Exception as e:
                    logger.error(f"Unexpected error posting review: {e}")
                    raise
    
    async def _post_with_urllib(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback: Post request using urllib (synchronous)."""
        import json
        
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=self._get_headers(),
            method='POST'
        )
        
        for attempt in range(self.config.max_retries):
            try:
                with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                    return json.loads(response.read().decode('utf-8'))
                    
            except urllib.error.HTTPError as e:
                if e.code == 422:
                    logger.error(f"GitHub API validation error: {e.read().decode()}")
                    raise
                
                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"Unexpected error posting review: {e}")
                raise
    
    async def add_comment(
        self,
        repo: str,
        pr_number: int,
        body: str,
    ) -> Dict[str, Any]:
        """
        Add a comment to a pull request.
        
        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            body: Comment body text (markdown)
            
        Returns:
            GitHub API response
        """
        url = f"{self.config.base_url}/repos/{repo}/issues/{pr_number}/comments"
        
        payload = {"body": body}
        
        logger.info(f"Adding comment to {repo}#{pr_number}")
        
        if HTTPX_AVAILABLE:
            return await self._post_with_httpx(url, payload)
        else:
            return await self._post_with_urllib(url, payload)
    
    async def get_pr_details(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request details.
        
        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            PR details from GitHub API
        """
        url = f"{self.config.base_url}/repos/{repo}/pulls/{pr_number}"
        
        headers = self._get_headers()
        
        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json()
        else:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                import json
                return json.loads(response.read().decode('utf-8'))
    
    async def get_pr_files(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get list of files changed in a pull request.
        
        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            List of changed files from GitHub API
        """
        url = f"{self.config.base_url}/repos/{repo}/pulls/{pr_number}/files"
        
        headers = self._get_headers()
        
        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json()
        else:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                import json
                return json.loads(response.read().decode('utf-8'))
    
    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """
        Get pull request diff.
        
        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            Unified diff string
        """
        url = f"{self.config.base_url}/repos/{repo}/pulls/{pr_number}"
        
        headers = self._get_headers()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=self.config.timeout)
                response.raise_for_status()
                return response.text
        else:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                return response.read().decode('utf-8')
