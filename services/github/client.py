"""GitHub service client module."""
from typing import Optional, Dict, Any, List
from .exceptions import GitHubServiceException

class GitHubClient:
    """Client for GitHub API interactions."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub client."""
        self.token = token
    
    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information."""
        if not self.token:
            raise GitHubServiceException("Authentication token required")
        return {
            "owner": owner,
            "repo": repo,
            "url": f"https://github.com/{owner}/{repo}",
        }
    
    def list_issues(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List issues in a repository."""
        if not self.token:
            raise GitHubServiceException("Authentication token required")
        return []

__all__ = ["GitHubClient"]
