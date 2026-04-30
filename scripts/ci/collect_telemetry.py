#!/usr/bin/env python3
"""
CI Telemetry Collection Script

Collects workflow runs, jobs, and artifacts from GitHub Actions.
Maps failures to 16 pattern categories for automated analysis.

Usage:
    python scripts/ci/collect_telemetry.py --owner Aries-Serpent --repo _codex_ --branch main --days 7
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

import requests


class TelemetryCollector:
    """Collects and analyzes CI telemetry data."""

    # Pattern keywords for automatic classification.
    # Ordered by specificity — more specific patterns should appear first.
    # Each failure is matched against run name + job names (case-insensitive).
    PATTERN_KEYWORDS = {
        # ── High-frequency CI patterns ───────────────────────────────────────
        "coverage-timeout": [
            "coverage", "pytest-cov", "coverage report", "coverage-with-timeout",
            "sharded coverage", "coverage shard",
        ],
        "auto-fix": [
            "auto-fix", "detect-and-fix", "detect ci issues", "auto fix",
            "fix-pr", "auto_fix", "autofix", "common issues",
        ],
        "pre-merge-cascade": [
            "pre-merge", "final-checks", "merge validation", "pre-merge-validation",
            "pre_merge",
        ],
        # ── Workflow-cascade / concurrency patterns ───────────────────────────
        "workflow-cascade": [
            "workflow-analytics", "workflow analytics", "cognitive-brain",
            "cognitive brain", "cascade", "art_workflow",
        ],
        # ── Integration-branch direct-session guard (REQ-11) ──────────────────
        # MUST be checked BEFORE auth-delegation: agent-auth-delegation.yml run
        # name contains "delegation" which otherwise matches auth-delegation first.
        # Fires when a Copilot session is attempted directly on 0D_base_.
        # Non-fixable by auto-heal; escalates with redirect instructions.
        "integration-branch-direct-session": [
            "req-11", "req11", "integration branch", "integration-branch",
            "staging gate", "direct session on integration",
            "direct-session", "0d_base", "0D_base_",
        ],
        # ── Auth / delegation patterns ────────────────────────────────────────
        "auth-delegation": [
            "agent-auth", "delegation", "token-probe", "token probe",
            "auth-compliance", "auth-mfa", "auth-secret", "auth-security",
            "auth-token", "auth-tests", "agent token",
        ],
        # ── Self-healing / watchdog patterns ─────────────────────────────────
        "self-healing": [
            "self-heal", "self_healing", "self healing", "session-watchdog",
            "watchdog",
            # S172 cascade root-cause signature: .venv_ci/bin/pip absent on cache miss
            "iterative-self-healing-ci",
            "self-heal(iter-",
        ],
        # ── Security / scanning patterns ─────────────────────────────────────
        "security-scan": [
            "codeql", "security", "dependabot", "vulnerability",
            "secret-scan", "secret scan", "scan-trivy", "sbom",
            "code-scanning",
            # GitHub Advanced Security: dependency graph submission
            "dependency submission", "dependency-submission",
            "automatic dependency", "component-detection",
        ],
        # ── Build / container patterns ────────────────────────────────────────
        "docker-build": [
            "docker", "build-image", "container", "push_image",
            "buildx", "qemu",
        ],
        # ── Test infrastructure ───────────────────────────────────────────────
        "test-infrastructure": [
            "resilient", "validation-suite", "test-runner", "pytest",
            "validate_test", "test_structure", "audit-qa",
        ],
        # ── Documentation / link validation ───────────────────────────────────
        "documentation": [
            "docs", "documentation", "link-validator", "doc-freshness",
            "doc_refactor", "api-documentation",
        ],
        # ── Cache management ──────────────────────────────────────────────────
        "cache": [
            "cache-pruning", "cache-warmup", "cache-cleanup",
            "cache management", "cache-management",
        ],
        # ── Cognitive brain / AI patterns ─────────────────────────────────────
        "cognitive-brain": [
            "cognitive", "quantum", "agent-brain", "brain-analysis",
            "cognitive_brain", "cognitive-action", "cognitive-analysis",
        ],
        # ── CI health / triage ────────────────────────────────────────────────
        "ci-health": [
            "health-monitor", "health check", "ci-health", "batch-ci-triage",
            "batch_ci", "batch_triage", "ci_triage",
        ],
        # ── Deployment / release ──────────────────────────────────────────────
        "deployment": [
            "deploy", "release", "publish", "pypi", "pages",
        ],
        # ── Lint / formatting ─────────────────────────────────────────────────
        "lint": [
            "lint", "ruff", "black", "isort", "pre-commit", "format",
            "auto-update-configs", "actionlint", "compliance-audit",
            "workflow compliance",
        ],
        # ── Filesystem / directory ────────────────────────────────────────────
        "filesystem-deadlock": [
            "root-org", "file-validation", "directory", "filesystem",
            "flatten-repo", "root_organizer",
        ],
        # ── Type-checking / mypy anti-regression ─────────────────────────────
        "type-check": [
            "mypy", "type-check", "type check", "anti-regression",
            "mypy-baseline", "mypy baseline", "type-error",
        ],
        # ── Policy / compliance gates ─────────────────────────────────────────
        "policy-gate": [
            "deferral", "language-gate", "deferral-language", "policy-check",
            "deferral language", "deferral gate",
        ],
        # ── Branch / rebase gates ─────────────────────────────────────────────
        "rebase-gate": [
            "rebase", "branch-rebase", "rebase-gate", "behind base",
            "branch rebase", "req-10",
        ],
        # ── Copilot coding-agent runs ─────────────────────────────────────────
        "copilot-agent": [
            "copilot coding", "swe-agent", "copilot-swe", "coding agent",
        ],
        # ── P4.5: New classifiers — drive unknown bucket from ~60% → <30% ────
        # DATETIME_001: offset-aware vs offset-naive mixing (common after Python 3.11+)
        "datetime-error": [
            "offset-aware", "offset-naive", "cannot mix", "tzinfo",
            "astimezone", "utcnow", "timezone-aware",
        ],
        # BUILD_001: pyproject.toml SPDX license-expression incompatibility
        "build-config": [
            "license-expression", "spdx", "pyproject.toml",
            "configuration error", "license must be string",
        ],
        # PKG_001: PEP 621 / setuptools dynamic metadata issues
        "packaging": [
            "pep 621", "pep621", "setuptools", "dynamic",
            "requires-python", "build-backend", "flit_core",
        ],
        # SESSION_INJECTOR: Copilot PR session injection / context briefing workflows
        "session-injector": [
            "session-inject", "session injector", "copilot-pr-session",
            "inject cognitive", "cognitive brain context", "pr-session",
            "session_inject", "brain context",
        ],
        # SMOKE_TEST_001: Docker smoke-test / health-check failures (registry denial,
        # image-not-found, health endpoint timeout) — distinct from generic docker-build
        "docker-smoke-test": [
            "smoke-test", "smoke test", "health check", "health-check",
            "/api/health", "registry denied", "denied", "not found in manifest",
            "load=true", "unable to find image",
        ],
        # CODESPACES_001: Codespaces prebuild failures
        "codespaces": [
            "codespaces", "prebuild", "devcontainer", "prebuilds",
            "create template", "codespace",
        ],
        # EMBEDDING_001: Embedding / RAG index rebuild failures
        "embedding-rebuild": [
            "embedding", "index rebuild", "rag-index", "rag index",
            "vector store", "faiss", "embedding-rebuild",
        ],
        # CODECOV_001: Codecov upload fails with "Token required because branch is protected"
        "codecov-token": [
            "codecov", "codecov-action", "token required", "protected branch",
            "upload queued", "coverage upload", "codecov upload",
        ],
        # ACCOUNTABILITY_001: AGENT_ACCOUNTABILITY_REPORT.md not updated in last commit
        "accountability-report": [
            "accountability report", "agent_accountability", "req-4", "req4",
            "accountability", "report updated in last commit",
        ],
        # AUTOSTASH_001: git pull --rebase without --autostash causes "unstaged changes" abort
        "autostash-race": [
            "autostash", "unstaged changes", "cannot pull with rebase",
            "rebase race", "session_wrapup", "session-done push",
            "fetch first", "rebase abort",
        ],
        # PUSH_RACE_001: concurrent push race (non-fast-forward rejection) when multiple
        # self-heal jobs or sweep jobs attempt to push to the same branch simultaneously.
        "push-race": [
            "non-fast-forward", "push rejected", "failed to push",
            "concurrent push", "push failed after", "updates were rejected",
            "push race", "fetch first",
        ],
    }

    def __init__(self, owner: str, repo: str, token: str):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def collect_workflow_runs(
        self, branch: str, days: int = 7, max_pages: int = 10
    ) -> List[Dict]:
        """Collect workflow runs from specified branch.

        Args:
            branch: Branch name to analyze
            days: Number of days to look back
            max_pages: Maximum number of pages to fetch

        Returns:
            List of workflow run dictionaries
        """
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs"
        params = {"branch": branch, "per_page": 100, "created": f">={since}"}

        runs = []
        page = 1
        while page <= max_pages:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            runs.extend(data["workflow_runs"])

            if len(data["workflow_runs"]) < 100:
                break
            page += 1

        return runs

    def collect_job_details(self, run_id: int) -> List[Dict]:
        """Collect job details for a workflow run.

        Args:
            run_id: Workflow run ID

        Returns:
            List of job dictionaries
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/jobs"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()["jobs"]

    def collect_artifacts(self, run_id: int) -> List[Dict]:
        """Collect artifacts for a workflow run.

        Args:
            run_id: Workflow run ID

        Returns:
            List of artifact dictionaries
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/artifacts"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()["artifacts"]

    def classify_failure(self, run: Dict, jobs: List[Dict]) -> str:
        """Classify failure into one of 5 patterns.

        Args:
            run: Workflow run dictionary
            jobs: List of job dictionaries

        Returns:
            Pattern name or "unknown"
        """
        run_name = run["name"].lower()
        job_names = " ".join([j["name"].lower() for j in jobs])
        # Also include step names from all jobs — catches REQ-11 step names like
        # "REQ-11: Integration-branch direct-session guard" which contain the
        # keywords that distinguish integration-branch-direct-session from
        # auth-delegation when the workflow is agent-auth-delegation.yml.
        step_names = " ".join(
            s["name"].lower()
            for j in jobs
            for s in j.get("steps", [])
        )
        search_text = f"{run_name} {job_names} {step_names}"

        for pattern, keywords in self.PATTERN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in search_text:
                    return pattern

        return "unknown"

    def generate_report(
        self, branch: str, days: int = 7, output: str = "telemetry_report.json"
    ) -> Dict:
        """Generate comprehensive telemetry report.

        Args:
            branch: Branch to analyze
            days: Days to look back
            output: Output file path

        Returns:
            Telemetry data dictionary
        """
        print(f"Collecting workflow runs from {branch} (last {days} days)...")
        runs = self.collect_workflow_runs(branch, days)

        # Filter to failed runs
        failed_runs = [
            r for r in runs if r["conclusion"] in ["failure", "cancelled", "timed_out"]
        ]
        print(f"Found {len(failed_runs)} failed runs out of {len(runs)} total")

        telemetry_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "repository": f"{self.owner}/{self.repo}",
            "branch": branch,
            "days_analyzed": days,
            "summary": {
                "total_runs": len(runs),
                "failed_runs": len(failed_runs),
                "failure_rate": len(failed_runs) / len(runs) if runs else 0,
            },
            "pattern_distribution": {},
            "failed_runs": [],
        }

        # Collect details for each failed run
        for i, run in enumerate(failed_runs, 1):
            print(
                f"  Processing run {i}/{len(failed_runs)}: {run['id']} - {run['name']}"
            )

            try:
                jobs = self.collect_job_details(run["id"])
                artifacts = self.collect_artifacts(run["id"])
                pattern = self.classify_failure(run, jobs)

                # Update pattern distribution
                telemetry_data["pattern_distribution"][pattern] = (
                    telemetry_data["pattern_distribution"].get(pattern, 0) + 1
                )

                telemetry_data["failed_runs"].append(
                    {
                        "run_id": run["id"],
                        "run_name": run["name"],
                        "run_html_url": run["html_url"],
                        "conclusion": run["conclusion"],
                        "created_at": run["created_at"],
                        "pattern": pattern,
                        "jobs": [
                            {
                                "job_id": j["id"],
                                "job_name": j["name"],
                                "job_html_url": j["html_url"],
                                "status": j["status"],
                                "conclusion": j["conclusion"],
                            }
                            for j in jobs
                        ],
                        "artifacts": [
                            {
                                "artifact_id": a["id"],
                                "artifact_name": a["name"],
                                "size_bytes": a["size_in_bytes"],
                                "expired": a["expired"],
                            }
                            for a in artifacts
                        ],
                    }
                )
            except requests.RequestException as e:
                print(f"  Warning: Failed to collect details for run {run['id']}: {e}")
                continue

        # Write report
        # Run cascade analysis and embed results so ci-health-monitor can
        # suppress false-positive threshold alerts when a self-healing cascade
        # accounts for the majority of failures (issue #3669).
        cascade_analysis = self.analyze_multi_job_cascade(telemetry_data)
        telemetry_data["cascade_analysis"] = cascade_analysis

        with open(output, "w") as f:
            json.dump(telemetry_data, f, indent=2)

        print(f"\nTelemetry report written to {output}")
        print("\nPattern Distribution:")
        for pattern, count in sorted(
            telemetry_data["pattern_distribution"].items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / len(failed_runs)) * 100 if failed_runs else 0
            print(f"  {pattern}: {count} ({percentage:.1f}%)")

        return telemetry_data

    def analyze_multi_job_cascade(self, telemetry_data: Dict) -> Dict:
        """Identify self-healing cascade patterns across multiple jobs in a workflow run.

        A cascade occurs when the dominant failure pattern is 'self-healing', meaning
        the Iterative Self-Healing CI workflow itself is failing (rather than it
        successfully healing other workflows).  This helper computes:

        - cascade_detected: bool — True when 'self-healing' > 50% of all failures
        - cascade_rate:     float — fraction of failures that are self-healing
        - root_cause:       str   — human-readable root cause explanation
        - recommended_action: str — what to do to remediate

        Used by ci-health-alert-agent.md Phase 2 pattern classification.
        """
        distribution = telemetry_data.get("pattern_distribution", {})
        total_failures = sum(distribution.values())
        if total_failures == 0:
            return {
                "cascade_detected": False,
                "cascade_rate": 0.0,
                "self_healing_count": 0,
                "total_failures": 0,
                "root_cause": "No failures to analyze",
                "recommended_action": "none",
                "pattern_distribution": distribution,
            }

        self_healing_count = distribution.get("self-healing", 0)
        cascade_rate = self_healing_count / total_failures

        cascade_detected = cascade_rate > 0.50
        if cascade_detected:
            root_cause = (
                f"Self-healing cascade: {self_healing_count}/{total_failures} failures "
                f"({cascade_rate*100:.1f}%) are from Iterative Self-Healing CI runs. "
                "Most likely root cause: stale or missing .venv_ci virtualenv on cache "
                "miss, leaving .venv_ci/bin/pip absent or invalid "
                "(SELF_HEALING_001 sub-scenario A). Fixed in S172 by recreating the "
                "venv with 'python3 -m venv .venv_ci' and installing via '.venv_ci/bin/pip'."
            )
            recommended_action = (
                "1. Verify iterative-self-healing-ci.yml recreates the venv with "
                "'python3 -m venv .venv_ci' and installs via '.venv_ci/bin/pip' "
                "(NOT a system-pip fallback). "
                "2. Check CODEX_CACHE_VERSION — a version bump busts the L3 venv cache. "
                "3. Monitor for 7 days post-fix; failure rate should drop to <1%."
            )
        else:
            root_cause = (
                f"No cascade detected: self-healing failures at {cascade_rate*100:.1f}% "
                f"of total ({self_healing_count}/{total_failures})."
            )
            top_pattern = max(distribution, key=distribution.get) if distribution else "unknown"
            top_count = distribution.get(top_pattern, 0)
            recommended_action = (
                f"Investigate top failure pattern: '{top_pattern}' ({top_count} occurrences). "
                f"See '.codex/patterns/ci_failure_patterns.yaml' for pattern fix guidance. "
                f"Run: python scripts/ci/collect_telemetry.py --classify-run <RUN_ID> "
                f"--owner Aries-Serpent --repo _codex_"
            )

        return {
            "cascade_detected": cascade_detected,
            "cascade_rate": round(cascade_rate, 4),
            "self_healing_count": self_healing_count,
            "total_failures": total_failures,
            "root_cause": root_cause,
            "recommended_action": recommended_action,
            "pattern_distribution": distribution,
        }


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Collect CI telemetry data from GitHub Actions"
    )
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--branch", default="main", help="Branch to analyze")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument(
        "--output", default="telemetry_report.json", help="Output file path"
    )
    parser.add_argument(
        "--token", help="GitHub token (or use GITHUB_TOKEN/CODEX_MASTER_KEY env var)"
    )
    parser.add_argument(
        "--classify-run",
        metavar="RUN_ID",
        help=(
            "Classify a single workflow run by ID and print the pattern name to stdout. "
            "Always exits 0; prints 'unknown' to stdout on API failure to preserve the "
            "workflow's || echo 'unknown' contract. "
            "Used by iterative-self-healing-ci.yml to label failures."
        ),
    )

    args = parser.parse_args()

    token = (
        args.token
        or os.getenv("GITHUB_TOKEN")
        or os.getenv("CODEX_MASTER_KEY")
        or os.getenv("CODEX_BACKUP_KEY")
    )
    if not token:
        print(
            "Error: GitHub token required (--token or GITHUB_TOKEN/CODEX_MASTER_KEY env var)"
        )
        sys.exit(1)

    # Single-run classification mode — used by iterative-self-healing-ci.yml.
    # Fetch run + jobs, classify, and print just the pattern name so the
    # workflow can capture it via $(…) without needing a full report.
    if args.classify_run:
        try:
            collector = TelemetryCollector(args.owner, args.repo, token)
            run_id = int(args.classify_run)
            run_url = f"{collector.base_url}/repos/{collector.owner}/{collector.repo}/actions/runs/{run_id}"
            run_resp = requests.get(run_url, headers=collector.headers, timeout=30)
            run_resp.raise_for_status()
            run = run_resp.json()
            jobs = collector.collect_job_details(run_id)
            pattern = collector.classify_failure(run, jobs)
            print(pattern)
        except Exception as e:
            print(f"classify-run error: {e}", file=sys.stderr)
            print("unknown")
        return

    try:
        collector = TelemetryCollector(args.owner, args.repo, token)
        collector.generate_report(args.branch, args.days, args.output)
        print("\n✓ Telemetry collection completed successfully")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
