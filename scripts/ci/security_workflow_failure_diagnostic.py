#!/usr/bin/env python3
"""
Security Workflow Failure Diagnostics Generator

Purpose:
    Generates detailed diagnostic information when security-scanning-suite fails,
    including root cause analysis, partial findings (if available), and 
    recommendations for Copilot agent remediation.

Usage:
    python scripts/ci/security_workflow_failure_diagnostic.py \
      --run-id 12345 \
      --workflow-name "Security Scanning Suite" \
      --output .codex/security-workflow-failure-diagnostic.json

Environment Variables:
    GITHUB_REPOSITORY: Repository name (owner/repo)
    GITHUB_RUN_ID: GitHub Actions run ID
    GITHUB_SHA: Commit SHA
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FailedJob:
    """Information about a failed job"""
    job_name: str
    reason: str  # timeout, tool_crash, config_error, network_error, unknown
    error_message: Optional[str] = None
    logs_url: Optional[str] = None
    last_step_name: Optional[str] = None
    duration_minutes: Optional[float] = None


@dataclass
class PartialFindings:
    """Information about partial findings from successful scans"""
    available: bool = False
    artifact_path: Optional[str] = None
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


@dataclass
class DiagnosticReport:
    """Comprehensive diagnostic report"""
    workflow_failure: Dict[str, Any]
    failed_jobs: List[str]
    failed_job_details: Dict[str, Any] = field(default_factory=dict)
    partial_findings: PartialFindings = field(default_factory=PartialFindings)
    recommended_agent: str = "ci-failure-resolution-agent"
    escalation_required: bool = False
    remediation_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FailureDiagnostician:
    """Diagnoses security workflow failures"""

    def __init__(
        self,
        run_id: str,
        workflow_name: str,
        repository: str,
        server_url: str,
        commit_sha: str,
    ):
        self.run_id = run_id
        self.workflow_name = workflow_name
        self.repository = repository
        self.server_url = server_url
        self.commit_sha = commit_sha

    def generate_report(self) -> DiagnosticReport:
        """Generate comprehensive failure diagnostic"""
        logger.info(f"Generating failure diagnostic for run {self.run_id}")

        # Build base failure info
        workflow_failure = {
            "workflow_name": self.workflow_name,
            "run_id": self.run_id,
            "run_url": f"{self.server_url}/{self.repository}/actions/runs/{self.run_id}",
            "failure_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "head_sha": self.commit_sha,
            "repository": self.repository,
        }

        # Detect failed jobs (would be populated by workflow context in real execution)
        failed_jobs = self._detect_failed_jobs()
        failed_job_details = self._analyze_failed_jobs(failed_jobs)

        # Check for partial findings
        partial_findings = self._check_partial_findings()

        # Determine escalation
        escalation_required = len(failed_jobs) > 2 or any(
            detail.get("reason") == "timeout" for detail in failed_job_details.values()
        )

        # Generate remediation steps
        remediation_steps = self._generate_remediation_steps(failed_job_details)

        report = DiagnosticReport(
            workflow_failure=workflow_failure,
            failed_jobs=failed_jobs,
            failed_job_details=failed_job_details,
            partial_findings=partial_findings,
            recommended_agent="ci-failure-resolution-agent" if not escalation_required else "ci-emergency-response-agent",
            escalation_required=escalation_required,
            remediation_steps=remediation_steps,
            metadata={
                "diagnostic_version": "1.0",
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )

        return report

    def _detect_failed_jobs(self) -> List[str]:
        """Detect which jobs failed (placeholder for real implementation)"""
        # In real workflow execution, this would parse job status from GitHub API
        # For now, return empty list (would be populated by workflow context)
        failed_jobs = []
        return failed_jobs

    def _analyze_failed_jobs(self, failed_jobs: List[str]) -> Dict[str, Any]:
        """Analyze each failed job"""
        analysis = {}

        job_patterns = {
            "codeql-scan": {
                "common_reasons": ["timeout (60min limit)", "autobuild failure", "config error"],
                "recovery_steps": ["Check .github/codeql/codeql-config.yml", "Check autobuild logs", "Increase timeout"],
            },
            "semgrep": {
                "common_reasons": ["rule fetch timeout", "memory exhaustion", "invalid rule config"],
                "recovery_steps": ["Check Semgrep registry connectivity", "Check rule config", "Review memory usage"],
            },
            "dependency-scan": {
                "common_reasons": ["pip timeout", "safety network error", "invalid requirements"],
                "recovery_steps": ["Verify requirements.txt", "Check pip cache", "Retry with --no-cache"],
            },
            "secret-scan": {
                "common_reasons": ["detect-secrets baseline update", "permission issue", "invalid baseline"],
                "recovery_steps": ["Regenerate .secrets.baseline", "Check file permissions", "Update plugins"],
            },
        }

        for job_name in failed_jobs:
            pattern = job_patterns.get(job_name, {})
            analysis[job_name] = {
                "job_name": job_name,
                "reason": "unknown",
                "error_message": "Details would be fetched from workflow logs",
                "logs_url": f"{self.server_url}/{self.repository}/actions/runs/{self.run_id}",
                "suggested_recovery_steps": pattern.get("recovery_steps", []),
                "common_causes": pattern.get("common_reasons", []),
            }

        return analysis

    def _check_partial_findings(self) -> PartialFindings:
        """Check if partial findings are available from successful scans"""
        findings_path = Path(".codex/security-findings-comprehensive.json")
        
        partial = PartialFindings(available=False)

        if findings_path.exists():
            try:
                with open(findings_path, "r") as f:
                    findings_data = json.load(f)
                
                partial.available = True
                partial.artifact_path = str(findings_path)
                
                summary = findings_data.get("summary", {})
                partial.critical_count = summary.get("critical_count", 0)
                partial.high_count = summary.get("high_count", 0)
                partial.medium_count = summary.get("medium_count", 0)
                partial.low_count = summary.get("low_count", 0)
                
                logger.info(f"Partial findings available: {partial.critical_count} critical, {partial.high_count} high")
            except Exception as e:
                logger.warning(f"Could not parse partial findings: {e}")

        return partial

    def _generate_remediation_steps(self, failed_job_details: Dict[str, Any]) -> List[str]:
        """Generate recommended remediation steps"""
        steps = [
            "1. Review failed job logs in GitHub Actions",
            "2. Identify root cause from error messages",
            "3. Check for tool-specific configuration issues",
        ]

        if any("timeout" in str(v).lower() for v in failed_job_details.values()):
            steps.append("4. Consider increasing job timeout if scan is legitimate")

        if any("config" in str(v).lower() for v in failed_job_details.values()):
            steps.append("4. Verify scanning tool configuration files (.github/codeql/, semgrep/, etc.)")

        steps.extend([
            "5. Check partial findings (if available) for insights",
            "6. Run affected scan locally to reproduce issue",
            "7. Commit fix and re-run workflow",
        ])

        return steps

    def save_report(self, output_path: str) -> None:
        """Save diagnostic report as JSON"""
        report = self.generate_report()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        report_dict = {
            "workflow_failure": report.workflow_failure,
            "failed_jobs": report.failed_jobs,
            "failed_job_details": report.failed_job_details,
            "partial_findings": asdict(report.partial_findings),
            "recommended_agent": report.recommended_agent,
            "escalation_required": report.escalation_required,
            "remediation_steps": report.remediation_steps,
            "metadata": report.metadata,
        }

        with open(output_file, "w") as f:
            json.dump(report_dict, f, indent=2)

        logger.info(f"Diagnostic report saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate security workflow failure diagnostics"
    )
    parser.add_argument(
        "--run-id",
        default=os.getenv("GITHUB_RUN_ID", "unknown"),
        help="GitHub Actions run ID",
    )
    parser.add_argument(
        "--workflow-name",
        default="Security Scanning Suite",
        help="Workflow name",
    )
    parser.add_argument(
        "--repository",
        default=os.getenv("GITHUB_REPOSITORY", "unknown/repo"),
        help="Repository name (owner/repo)",
    )
    parser.add_argument(
        "--server-url",
        default=os.getenv("GITHUB_SERVER_URL", "https://github.com"),
        help="GitHub server URL",
    )
    parser.add_argument(
        "--commit-sha",
        default=os.getenv("GITHUB_SHA", "unknown"),
        help="Commit SHA",
    )
    parser.add_argument(
        "--output",
        default=".codex/security-workflow-failure-diagnostic.json",
        help="Output file path",
    )

    args = parser.parse_args()

    diagnostician = FailureDiagnostician(
        run_id=args.run_id,
        workflow_name=args.workflow_name,
        repository=args.repository,
        server_url=args.server_url,
        commit_sha=args.commit_sha,
    )

    try:
        diagnostician.save_report(args.output)
        logger.info("✅ Diagnostic generation complete")
        return 0
    except Exception as e:
        logger.error(f"❌ Diagnostic generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
