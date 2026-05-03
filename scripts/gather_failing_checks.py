#!/usr/bin/env python3
"""
Collect and report failing GitHub checks and artifacts for all commits in a Pull Request.

This script fetches commit history from a PR, identifies failing check runs,
collects downloadable artifacts, and generates a markdown report.

Usage:
    python scripts/gather_failing_checks.py --repo owner/repo --pr 3248 --output failing_checks.md

Environment:
    GITHUB_TOKEN: GitHub personal access token (required for API access)
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "collect_failing_checks.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class GitHubAPIClient:
    """Client for interacting with GitHub REST API."""

    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub API client.

        Args:
            token: GitHub personal access token. If None, reads from GITHUB_TOKEN env var.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable must be set")

        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[dict[str, Any]]:
        """Make an authenticated request to the GitHub API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            JSON response as dict, or None on error
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text[:500]}")
            return None

    def fetch_pr_commits(self, owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """Fetch all commits in a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of commit objects
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        logger.info(f"Fetching commits for PR #{pr_number}...")

        commits = []
        page = 1
        per_page = 100

        while True:
            params = {"page": page, "per_page": per_page}
            data = self._request("GET", endpoint, params=params)
            if not data:
                break

            commits.extend(data)
            logger.info(f"Fetched {len(data)} commits (page {page})")

            if len(data) < per_page:
                break
            page += 1

        logger.info(f"Total commits fetched: {len(commits)}")
        return commits

    def fetch_check_runs(self, owner: str, repo: str, sha: str) -> list[dict[str, Any]]:
        """Fetch check runs for a specific commit.

        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA

        Returns:
            List of check run objects
        """
        endpoint = f"/repos/{owner}/{repo}/commits/{sha}/check-runs"
        data = self._request("GET", endpoint)
        if not data or "check_runs" not in data:
            return []

        return data["check_runs"]

    def fetch_workflow_runs(self, owner: str, repo: str, sha: str) -> list[dict[str, Any]]:
        """Fetch workflow runs for a specific commit.

        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA

        Returns:
            List of workflow run objects
        """
        endpoint = f"/repos/{owner}/{repo}/actions/runs"
        params = {"head_sha": sha}
        data = self._request("GET", endpoint, params=params)
        if not data or "workflow_runs" not in data:
            return []

        return data["workflow_runs"]

    def fetch_workflow_artifacts(self, owner: str, repo: str, run_id: int) -> list[dict[str, Any]]:
        """Fetch artifacts for a specific workflow run.

        Args:
            owner: Repository owner
            repo: Repository name
            run_id: Workflow run ID

        Returns:
            List of artifact objects
        """
        endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
        data = self._request("GET", endpoint)
        if not data or "artifacts" not in data:
            return []

        return data["artifacts"]


def is_check_failing(check_run: dict[str, Any]) -> bool:
    """Determine if a check run is failing or non-successful.

    Args:
        check_run: Check run object from GitHub API

    Returns:
        True if check is failing, False otherwise
    """
    status = check_run.get("status", "")
    conclusion = check_run.get("conclusion", "")

    # Check is failing if:
    # - Not completed yet (status != 'completed')
    # - Completed with non-success conclusion
    failing_conclusions = ["failure", "timed_out", "cancelled", "action_required"]

    return (status != "completed") or (conclusion in failing_conclusions)


def process_commit(
    client: GitHubAPIClient,
    owner: str,
    repo: str,
    commit: dict[str, Any]
) -> Optional[tuple[str, list[str], list[tuple[str, str]]]]:
    """Process a single commit to extract failing checks and artifacts.

    Args:
        client: GitHub API client
        owner: Repository owner
        repo: Repository name
        commit: Commit object from GitHub API

    Returns:
        Tuple of (sha, failing_check_urls, artifacts) or None if no failures
    """
    sha = commit["sha"]
    short_sha = sha[:7]
    logger.info(f"Processing commit {short_sha}...")

    # Fetch check runs
    check_runs = client.fetch_check_runs(owner, repo, sha)
    failing_checks = []

    for check_run in check_runs:
        if is_check_failing(check_run):
            check_name = check_run.get("name", "Unknown")
            check_url = check_run.get("html_url", "")
            if check_url:
                failing_checks.append(check_url)
                logger.info(f"  Found failing check: {check_name}")

    # Fetch workflow runs and their artifacts
    artifacts_list = []
    workflow_runs = client.fetch_workflow_runs(owner, repo, sha)

    for run in workflow_runs:
        run_id = run.get("id")
        if run_id:
            artifacts = client.fetch_workflow_artifacts(owner, repo, run_id)
            for artifact in artifacts:
                artifact_name = artifact.get("name", "Unknown")
                artifact_url = artifact.get("archive_download_url", "")
                if artifact_url:
                    artifacts_list.append((artifact_name, artifact_url))
                    logger.info(f"  Found artifact: {artifact_name}")

    # Only include commit if there are failing checks or artifacts
    if failing_checks or artifacts_list:
        return (sha, failing_checks, artifacts_list)

    return None


def generate_markdown_report(
    owner: str,
    repo: str,
    pr_number: int,
    results: list[tuple[str, list[str], list[tuple[str, str]]]],
    output_path: Path
) -> None:
    """Generate markdown report with failing checks and artifacts.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        results: List of (sha, failing_checks, artifacts) tuples
        output_path: Output file path
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# [Investigation Request]: Failing Checks per Commit",
        f"> Generated: {timestamp}",
        f"> Pull Request: #{pr_number}",
        f"> Repository: {owner}/{repo}",
        "",
        "## Summary",
        "",
        f"This report contains failing check runs and artifacts for **{len(results)} commit(s)** in PR #{pr_number}.",
        "",
        "## Failing Checks and Artifacts",
        "",
        "| Commit SHA | Failing Check Workflows (links) | Artifacts (download links) |",
        "|------------|----------------------------------|----------------------------|"
    ]

    for sha, failing_checks, artifacts in results:
        short_sha = sha[:7]
        commit_url = f"https://github.com/{owner}/{repo}/commit/{sha}"
        commit_link = f"[`{short_sha}`]({commit_url})"

        # Format failing checks
        if failing_checks:
            check_links = "<br>".join([f"[Check Run]({url})" for url in failing_checks])
        else:
            check_links = "N/A"

        # Format artifacts (note: requires authentication)
        if artifacts:
            artifact_links = []
            for name, url in artifacts:
                artifact_links.append(f"[{name}]({url}) 🔒")
            artifact_str = "<br>".join(artifact_links)
        else:
            artifact_str = "N/A"

        lines.append(f"| {commit_link} | {check_links} | {artifact_str} |")

    lines.extend([
        "",
        "---",
        "",
        "**Note:** Artifact download links require authentication with a GitHub token that has access to this repository.",
        "",
        "**Generated by:** `scripts/gather_failing_checks.py`",
        f"**Last Updated:** {timestamp}",
    ])

    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"Report written to {output_path}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Collect failing GitHub checks and artifacts for a Pull Request"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository in format 'owner/repo' (e.g., 'Aries-Serpent/_codex_')"
    )
    parser.add_argument(
        "--pr",
        type=int,
        required=True,
        help="Pull request number"
    )
    parser.add_argument(
        "--output",
        default="failing_checks.md",
        help="Output markdown file path (default: failing_checks.md)"
    )

    args = parser.parse_args()

    # Parse owner/repo
    try:
        owner, repo = args.repo.split("/")
    except ValueError:
        logger.error(f"Invalid repo format: {args.repo}. Expected 'owner/repo'")
        sys.exit(1)

    output_path = Path(args.output)

    try:
        # Initialize API client
        logger.info("Initializing GitHub API client...")
        client = GitHubAPIClient()

        # Fetch PR commits
        commits = client.fetch_pr_commits(owner, repo, args.pr)
        if not commits:
            logger.warning(f"No commits found for PR #{args.pr}")
            # Still generate empty report
            generate_markdown_report(owner, repo, args.pr, [], output_path)
            return 0

        # Process each commit
        results = []
        for commit in commits:
            result = process_commit(client, owner, repo, commit)
            if result:
                results.append(result)

        # Generate report
        generate_markdown_report(owner, repo, args.pr, results, output_path)

        logger.info(f"Successfully processed {len(commits)} commits")
        logger.info(f"Found {len(results)} commits with failing checks or artifacts")
        return 0

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        # Still try to generate partial report if we have results
        if 'results' in locals():
            generate_markdown_report(owner, repo, args.pr, results, output_path)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
