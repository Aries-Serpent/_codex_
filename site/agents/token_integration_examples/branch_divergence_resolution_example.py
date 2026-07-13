"""
Branch Divergence Resolution Agent - Token Integration Example

Demonstrates branch operation flow with multiple scope management.

Key Concepts:
- Level 2 (CODEX_BACKUP_TOKEN) token
- Scopes: repo, contents:write, pull_requests
- Multiple API operations requiring different permissions
- Conflict resolution workflow
- Concurrency handling
"""

import logging
import requests
from typing import Dict, List
from dataclasses import dataclass
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BranchDivergence:
    branch_a: str
    branch_b: str
    diverged_at_commit: str
    commits_behind: int
    commits_ahead: int
    conflicts: List[str]


class BranchDivergenceResolutionAgent:
    """Detect and resolve branch divergence."""
    
    def __init__(self):
        from scripts.ci._token_resolver import get_token, validate_scope
        
        self.token = get_token(required_elevated=True)
        if not self.token:
            self.token = get_token(required_elevated=False)
        
        validate_scope(self.token, ['repo', 'contents:write', 'pull_requests'])
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"token {self.token}"}
        )
    
    def detect_divergence(
        self,
        repo: str,
        branch_a: str,
        branch_b: str
    ) -> BranchDivergence:
        """Detect divergence between two branches."""
        
        # Get comparison
        url = f"https://api.github.com/repos/{repo}/compare/{branch_a}...{branch_b}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            divergence = BranchDivergence(
                branch_a=branch_a,
                branch_b=branch_b,
                diverged_at_commit=data['merge_base_commit']['sha'],
                commits_behind=data['behind_by'],
                commits_ahead=data['ahead_by'],
                conflicts=[f['filename'] for f in data.get('files', [])]
            )
            
            logger.info(
                "divergence_detected",
                extra={
                    "repo": repo,
                    "branch_a": branch_a,
                    "branch_b": branch_b,
                    "behind": divergence.commits_behind,
                    "ahead": divergence.commits_ahead
                }
            )
            
            return divergence
        
        except requests.HTTPError as e:
            logger.error(f"Failed to detect divergence: {e}")
            raise
    
    def resolve_branch_divergence(
        self,
        repo: str,
        source: str,
        target: str,
        strategy: str = "merge"
    ) -> Dict:
        """Resolve divergence using merge or rebase."""
        
        if strategy == "merge":
            return self._create_merge_pr(repo, source, target)
        elif strategy == "rebase":
            return self._create_rebase_pr(repo, source, target)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _create_merge_pr(self, repo: str, source: str, target: str) -> Dict:
        """Create PR to merge source into target."""
        url = f"https://api.github.com/repos/{repo}/pulls"
        
        body = f"""## Resolve Branch Divergence

Merge `{source}` into `{target}` to resolve divergence.

**Actions**:
- Integrates {source} changes
- Preserves merge history
- Allows conflict resolution review
"""
        
        try:
            response = self.session.post(
                url,
                json={
                    "title": f"Merge {source} → {target}",
                    "head": source,
                    "base": target,
                    "body": body
                },
                timeout=30
            )
            response.raise_for_status()
            
            pr = response.json()
            logger.info(
                "merge_pr_created",
                extra={"repo": repo, "pr": pr['number']}
            )
            
            return {"status": "success", "pr": pr['number'], "strategy": "merge"}
        
        except requests.HTTPError as e:
            logger.error(f"Failed to create merge PR: {e}")
            raise
    
    def _create_rebase_pr(self, repo: str, source: str, target: str) -> Dict:
        """Create PR to rebase source onto target."""
        url = f"https://api.github.com/repos/{repo}/pulls"
        
        body = f"""## Rebase {source} onto {target}

Rebase `{source}` onto latest `{target}` to resolve divergence.

**Actions**:
- Replays {source} commits on top of {target}
- Linearizes history
- May need conflict resolution
"""
        
        try:
            response = self.session.post(
                url,
                json={
                    "title": f"Rebase {source} onto {target}",
                    "head": source,
                    "base": target,
                    "body": body,
                    "draft": False
                },
                timeout=30
            )
            response.raise_for_status()
            
            pr = response.json()
            logger.info(
                "rebase_pr_created",
                extra={"repo": repo, "pr": pr['number']}
            )
            
            return {"status": "success", "pr": pr['number'], "strategy": "rebase"}
        
        except requests.HTTPError as e:
            logger.error(f"Failed to create rebase PR: {e}")
            raise
    
    def wait_for_conflict_resolution(
        self,
        repo: str,
        pr_number: int,
        max_wait_seconds: int = 3600
    ) -> bool:
        """Wait for PR conflicts to be resolved."""
        
        start_time = time.time()
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        
        while time.time() - start_time < max_wait_seconds:
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                pr = response.json()
                mergeable = pr.get('mergeable')
                
                if mergeable is None:
                    # Still computing
                    logger.info(f"PR #{pr_number} mergeability computing...")
                    time.sleep(10)
                    continue
                
                if mergeable:
                    logger.info(f"PR #{pr_number} conflicts resolved")
                    return True
                else:
                    logger.warning(f"PR #{pr_number} has unresolved conflicts")
                    return False
            
            except requests.HTTPError as e:
                logger.error(f"Error checking PR status: {e}")
                time.sleep(10)
        
        return False


if __name__ == "__main__":
    agent = BranchDivergenceResolutionAgent()
    
    # Detect divergence
    divergence = agent.detect_divergence(
        "owner/repo",
        "main",
        "staging"
    )
    
    print(f"Divergence: {divergence.commits_ahead} ahead, {divergence.commits_behind} behind")
    
    # Resolve if needed
    if divergence.commits_behind > 0:
        result = agent.resolve_branch_divergence(
            "owner/repo",
            "staging",
            "main",
            strategy="merge"
        )
        print(f"Resolution PR: #{result['pr']}")
