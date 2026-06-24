#!/usr/bin/env python3
"""
Base Requirement Validator Class

Provides common functionality for all requirement validators:
- JSON output serialization
- GitHub API integration
- Performance tracking
- Error handling
- Caching
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class ComplianceResult:
    """Standard result format for all requirement validators."""

    requirement_id: str           # "REQ-1", "REQ-2", etc.
    status: str                   # "pass", "fail", "warn"
    score: float                  # 0.0-1.0 (0=fail, 0.5=warn, 1.0=pass)
    reason: str                   # Detailed explanation
    remediation: list[str] = field(default_factory=list)  # Fix steps
    metadata: dict = field(default_factory=dict)  # Additional context
    elapsed_ms: float = 0.0       # Performance tracking

    def __post_init__(self):
        """Validate score range."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be 0.0-1.0, got {self.score}")
        if self.status not in ("pass", "fail", "warn"):
            raise ValueError(f"Status must be pass/fail/warn, got {self.status}")
        if self.score == 1.0 and self.status != "pass":
            raise ValueError("Score 1.0 must have status 'pass'")
        if self.score == 0.0 and self.status != "fail":
            raise ValueError("Score 0.0 must have status 'fail'")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class RequirementValidator:
    """Base class for all requirement validators."""

    def __init__(
        self,
        pr_number: str,
        repo: str = "Aries-Serpent/_codex_",
        timeout: int = 30,
    ):
        self.pr_number = pr_number
        self.repo = repo
        self.timeout = timeout
        self._start_time: Optional[float] = None

    @property
    def requirement_id(self) -> str:
        """Override in subclass: REQ-1, REQ-2, etc."""
        raise NotImplementedError("Subclass must define requirement_id")

    def validate(self) -> ComplianceResult:
        """Run the validation. Returns JSON-serializable result."""
        self._start_time = time.time()
        try:
            result = self._validate_impl()
        except Exception as exc:
            logger.exception(f"Validation failed for {self.requirement_id}")
            result = ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"Validation error: {exc}",
                remediation=[
                    "Check validator logs for details",
                    "Ensure GitHub API is accessible",
                ],
            )
        finally:
            elapsed = (time.time() - (self._start_time or time.time())) * 1000
            result.elapsed_ms = elapsed

        return result

    def _validate_impl(self) -> ComplianceResult:
        """Implement in subclass."""
        raise NotImplementedError("Subclass must implement _validate_impl")

    # --- GitHub API Helpers ---

    def _gh_api_call(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[dict] = None,
        jq: Optional[str] = None,
    ) -> str:
        """Make authenticated GitHub API call via gh CLI."""
        cmd = ["gh", "api", endpoint, "--method", method]
        if jq:
            cmd.extend(["--jq", jq])
        if data:
            cmd.append("--input=-")

        try:
            result = subprocess.run(
                cmd,
                input=json.dumps(data) if data else None,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"GitHub API call failed: {exc.stderr}")

    def _get_pr_details(self) -> dict:
        """Fetch PR details from GitHub."""
        output = self._gh_api_call(
            f"repos/{self.repo}/pulls/{self.pr_number}",
            jq=".",
        )
        return json.loads(output)

    def _get_pr_commits(self) -> list[dict]:
        """Fetch commits for the PR."""
        output = self._gh_api_call(
            f"repos/{self.repo}/pulls/{self.pr_number}/commits",
            jq=".",
        )
        return json.loads(output)

    def _get_pr_reviews(self) -> list[dict]:
        """Fetch reviews for the PR."""
        output = self._gh_api_call(
            f"repos/{self.repo}/pulls/{self.pr_number}/reviews",
            jq=".",
        )
        return json.loads(output)

    def _get_commit_details(self, sha: str) -> dict:
        """Fetch details for a specific commit."""
        output = self._gh_api_call(
            f"repos/{self.repo}/commits/{sha}",
            jq=".",
        )
        return json.loads(output)

    def _get_file_content(self, path: str, ref: str = "HEAD") -> Optional[str]:
        """Get file content from repository."""
        file_path = REPO_ROOT / path
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return None

    # --- Local File Helpers ---

    def _read_file(self, path: str) -> Optional[str]:
        """Read file from repo root."""
        file_path = REPO_ROOT / path
        try:
            return file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def _file_exists(self, path: str) -> bool:
        """Check if file exists in repo."""
        return (REPO_ROOT / path).exists()


def main():
    """Test the base class."""
    logging.basicConfig(level=logging.INFO)

    # Test ComplianceResult
    result = ComplianceResult(
        requirement_id="REQ-1",
        status="pass",
        score=1.0,
        reason="All checks passed",
        remediation=[],
        metadata={"test": True},
    )

    print("✅ ComplianceResult created successfully")
    print(result.to_json())

    return 0


if __name__ == "__main__":
    sys.exit(main())
