#!/usr/bin/env python3
"""
Aggregate Security Findings Report Generator

Purpose:
    Consolidates all security findings from multiple scanning tools (CodeQL, Semgrep,
    pip-audit, Safety, detect-secrets, SBOM) into a single authoritative JSON report
    with unified severity levels, deduplication, and agent assignment recommendations.

Usage:
    python scripts/ci/aggregate_security_findings.py \
      --artifacts-dir security-suite-artifacts \
      --output-json .codex/security-findings-comprehensive.json \
      --output-md security-findings-comprehensive.md \
      --repo-url https://github.com/Aries-Serpent/_codex_ \
      --run-id 12345 \
      --commit-sha abc123

Environment Variables:
    GITHUB_REPOSITORY: Repository name (owner/repo)
    GITHUB_RUN_ID: GitHub Actions run ID
    GITHUB_SHA: Commit SHA
    GITHUB_SERVER_URL: GitHub server URL

Exit Codes:
    0: Success
    1: Error
    2: No findings found
"""

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """Normalized finding record across all tools"""

    id: str
    tool: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    file: Optional[str] = None
    line: Optional[int] = None
    cwe_id: Optional[str] = None
    rule_id: Optional[str] = None
    package: Optional[str] = None
    version: Optional[str] = None
    remediation_url: Optional[str] = None
    sarif_location: Optional[str] = None
    status: str = "open"  # open, dismissed, fixed
    agent_assignee: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {
            "id": self.id,
            "tool": self.tool,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
        }
        if self.file:
            result["file"] = self.file
        if self.line:
            result["line"] = self.line
        if self.cwe_id:
            result["cwe_id"] = self.cwe_id
        if self.rule_id:
            result["rule_id"] = self.rule_id
        if self.package:
            result["package"] = self.package
        if self.version:
            result["version"] = self.version
        if self.remediation_url:
            result["remediation_url"] = self.remediation_url
        if self.sarif_location:
            result["sarif_location"] = self.sarif_location
        if self.status != "open":
            result["status"] = self.status
        if self.agent_assignee:
            result["agent_assignee"] = self.agent_assignee
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class ArtifactCatalog:
    """Discover security artifacts and validate scanner output contracts."""

    SCAN_ARTIFACTS = {
        "codeql": (
            "security-suite-codeql-python",
            "security-suite-codeql-javascript",
        ),
        "semgrep": ("security-suite-semgrep",),
        "containers": (
            "security-suite-container-0",
            "security-suite-container-1",
            "security-suite-container-2",
        ),
        "cve": (
            "security-suite-cve-python",
            "security-suite-cve-javascript",
            "security-suite-cve-rust",
        ),
        "dependency": ("security-suite-dependency",),
        "secrets": ("security-suite-secrets",),
        "sbom": ("security-suite-sbom",),
    }

    def __init__(self, artifacts_dir: Path, selected_scans: Optional[List[str]]):
        self.artifacts_dir = artifacts_dir
        self.selected_scans = self._resolve_selected_scans(selected_scans)
        self.scan_status = self._build_scan_status()

    def _resolve_selected_scans(self, selected_scans: Optional[List[str]]) -> set[str]:
        if selected_scans is not None:
            return {
                scan
                for scan in selected_scans
                if isinstance(scan, str) and scan in self.SCAN_ARTIFACTS
            }

        manifest = (
            self.artifacts_dir
            / "security-suite-lane-contract"
            / ".codex"
            / "contracts"
            / "lane-manifest.json"
        )
        if manifest.is_file():
            try:
                with manifest.open(encoding="utf-8") as handle:
                    metadata = json.load(handle)
                value = metadata.get("selected_scans", "") if isinstance(metadata, dict) else ""
                if isinstance(value, list):
                    return {
                        scan
                        for scan in value
                        if isinstance(scan, str) and scan in self.SCAN_ARTIFACTS
                    }
                if isinstance(value, str):
                    return {scan for scan in value.split(",") if scan in self.SCAN_ARTIFACTS}
            except (OSError, json.JSONDecodeError, AttributeError) as exc:
                logger.warning("Unable to read selected scans from lane manifest: %s", exc)

        return set(self.SCAN_ARTIFACTS)

    def _artifact_dirs(self, scan: str) -> List[Path]:
        expected = self.SCAN_ARTIFACTS[scan]
        if scan in {"containers", "cve"}:
            prefix = "security-suite-container-" if scan == "containers" else "security-suite-cve-"
            return sorted(path for path in self.artifacts_dir.glob(f"{prefix}*") if path.is_dir())
        return [
            self.artifacts_dir / name for name in expected if (self.artifacts_dir / name).is_dir()
        ]

    @staticmethod
    def _artifact_contract_succeeded(artifact_dir: Path) -> bool:
        artifact_root = artifact_dir.resolve()
        contracts = list(artifact_dir.rglob("output-contract-*.json"))
        if not contracts:
            return False

        for contract in contracts:
            try:
                with contract.open(encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, json.JSONDecodeError):
                return False
            if not isinstance(data, dict):
                return False
            if data.get("status") != "success":
                return False
            if data.get("scan_outcome", "success") != "success":
                return False
            required_outputs = data.get("required_outputs", [])
            if not isinstance(required_outputs, list) or not all(
                isinstance(output, str) for output in required_outputs
            ):
                return False
            for output in required_outputs:
                output_path = (artifact_dir / output).resolve()
                if not output_path.is_relative_to(artifact_root) or not output_path.exists():
                    return False
        return True

    def successful_artifacts(self, scan: str) -> List[Path]:
        return [
            artifact
            for artifact in self._artifact_dirs(scan)
            if self._artifact_contract_succeeded(artifact)
        ]

    def _build_scan_status(self) -> Dict[str, Dict[str, Any]]:
        results = {}
        for scan, expected in self.SCAN_ARTIFACTS.items():
            artifacts = self._artifact_dirs(scan)
            successful = [
                artifact for artifact in artifacts if self._artifact_contract_succeeded(artifact)
            ]
            selected = scan in self.selected_scans
            if not selected:
                status = "skipped"
            elif len(successful) == len(expected):
                status = "success"
            elif successful:
                status = "partial"
            else:
                status = "incomplete"
            results[scan] = {
                "selected": selected,
                "status": status,
                "expected_artifacts": len(expected),
                "available_artifacts": len(artifacts),
                "successful_artifacts": len(successful),
            }
        return results


class FindingsAggregator:
    """Main aggregator for security findings across all tools"""

    def __init__(
        self,
        artifacts_dir: str,
        repo_url: str,
        run_id: str,
        commit_sha: str,
        repository: str,
        selected_scans: Optional[List[str]] = None,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.repo_url = repo_url
        self.run_id = run_id
        self.commit_sha = commit_sha
        self.repository = repository
        self.findings: List[Finding] = []
        self.artifact_catalog = ArtifactCatalog(self.artifacts_dir, selected_scans)
        self.selected_scans = self.artifact_catalog.selected_scans
        self.scan_status = self.artifact_catalog.scan_status
        self.github_alert_inventory_status = {
            "selected": "codeql" in self.selected_scans,
            "status": ("incomplete" if "codeql" in self.selected_scans else "skipped"),
            "expected_artifacts": 1,
            "available_artifacts": 0,
            "successful_artifacts": 0,
            "alert_count": 0,
        }
        self.severity_map = {
            "critical": "CRITICAL",
            "error": "CRITICAL",
            "high": "HIGH",
            "warning": "MEDIUM",
            "medium": "MEDIUM",
            "note": "LOW",
            "low": "LOW",
            "info": "INFO",
        }

    def run(self) -> Dict[str, Any]:
        """Execute aggregation pipeline"""
        logger.info(f"Starting findings aggregation from {self.artifacts_dir}")

        # Parse findings from each tool
        self._parse_codeql_findings()
        self._parse_semgrep_findings()
        self._parse_container_findings()
        self._parse_cve_findings()
        self._parse_dependency_findings()
        self._parse_secret_findings()

        # Preserve each scanner's alert; identical locations from distinct tools
        # remain separate findings in the consolidated report.
        self._deduplicate_findings()

        # Normalize severity levels
        self._normalize_severity()

        # Generate agent assignments
        self._assign_agents()

        # Build comprehensive report
        report = self._build_report()

        logger.info(f"Aggregation complete: {len(self.findings)} unique findings")
        return report

    def _parse_sarif_artifact(self, artifact_dir: Path, tool_name: str) -> None:
        for sarif_file in artifact_dir.rglob("*.sarif"):
            try:
                with sarif_file.open(encoding="utf-8") as handle:
                    sarif_data = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                logger.error("Unable to parse SARIF file %s: %s", sarif_file, exc)
                continue

            for run in sarif_data.get("runs", []):
                rules = {
                    rule.get("id", "unknown"): rule
                    for rule in run.get("tool", {}).get("driver", {}).get("rules", [])
                }
                for index, result in enumerate(run.get("results", [])):
                    rule_id = result.get("ruleId", "unknown")
                    rule = rules.get(rule_id, {})
                    message = result.get("message", {}).get("text", rule_id)
                    properties = result.get("properties", {})
                    rule_properties = rule.get("properties", {})
                    severity = self._sarif_severity(
                        result.get("level"),
                        properties.get("security-severity")
                        or rule_properties.get("security-severity"),
                    )
                    location = (result.get("locations") or [{}])[0]
                    physical = location.get("physicalLocation", {})
                    file_path = physical.get("artifactLocation", {}).get("uri")
                    line = physical.get("region", {}).get("startLine")
                    details = rule.get("help", {}).get("text") or message
                    cwe_match = re.search(
                        r"CWE-\d+",
                        " ".join(
                            str(value)
                            for value in (
                                details,
                                rule_properties.get("tags", []),
                                properties.get("tags", []),
                            )
                        ),
                    )
                    fingerprint = (
                        result.get("fingerprints") or result.get("partialFingerprints") or {}
                    )
                    fingerprint_value = next(iter(fingerprint.values()), str(index))
                    source_path = sarif_file.relative_to(artifact_dir).as_posix()
                    finding_identity = "/".join(
                        (
                            tool_name,
                            artifact_dir.name,
                            source_path,
                            rule_id,
                            str(fingerprint_value),
                        )
                    )
                    finding_id = (
                        f"{tool_name.upper()}-"
                        f"{hashlib.sha256(finding_identity.encode()).hexdigest()[:20]}"
                    )
                    self.findings.append(
                        Finding(
                            id=finding_id,
                            tool=tool_name,
                            title=message,
                            description=details,
                            severity=severity,
                            file=file_path,
                            line=line,
                            cwe_id=cwe_match.group(0) if cwe_match else None,
                            rule_id=rule_id,
                            sarif_location=str(sarif_file),
                        )
                    )

    def _sarif_severity(self, level: Optional[str], score: Any) -> str:
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            numeric_score = None
        if numeric_score is not None:
            if numeric_score >= 9:
                return "CRITICAL"
            if numeric_score >= 7:
                return "HIGH"
            if numeric_score >= 4:
                return "MEDIUM"
            return "LOW"
        return self.severity_map.get(str(level or "note").lower(), "LOW")

    def _parse_codeql_findings(self) -> None:
        """Parse CodeQL SARIF artifacts"""
        logger.info("Parsing CodeQL findings...")
        for artifact in self.artifact_catalog.successful_artifacts("codeql"):
            self._parse_sarif_artifact(artifact, "codeql")
        _parse_github_code_scanning_inventory(self)

    def _parse_semgrep_findings(self) -> None:
        """Parse Semgrep JSON output"""
        logger.info("Parsing Semgrep findings...")
        for semgrep_dir in self.artifact_catalog.successful_artifacts("semgrep"):
            for json_file in semgrep_dir.rglob("semgrep-results.json"):
                try:
                    with json_file.open(encoding="utf-8") as handle:
                        semgrep_data = json.load(handle)
                except (OSError, json.JSONDecodeError) as exc:
                    logger.error("Unable to parse Semgrep results %s: %s", json_file, exc)
                    continue

                for index, result in enumerate(semgrep_data.get("results", [])):
                    extra = result.get("extra", {})
                    self.findings.append(
                        Finding(
                            id=f"SEMGREP-{result.get('check_id', 'unknown')}-{index}",
                            tool="semgrep",
                            title=result.get("check_id", "Semgrep Finding"),
                            description=extra.get("message", ""),
                            severity=self.severity_map.get(
                                extra.get("severity", "info").lower(), "INFO"
                            ),
                            file=result.get("path"),
                            line=result.get("start", {}).get("line"),
                            rule_id=result.get("check_id"),
                            remediation_url=extra.get("docs"),
                        )
                    )

    def _parse_container_findings(self) -> None:
        logger.info("Parsing container scanner SARIF findings...")
        for artifact in self.artifact_catalog.successful_artifacts("containers"):
            self._parse_sarif_artifact(artifact, "trivy")

    def _parse_dependency_findings(self) -> None:
        """Parse pip-audit and Safety JSON outputs from the successful dependency gate."""
        logger.info("Parsing dependency vulnerability findings...")
        for dep_dir in self.artifact_catalog.successful_artifacts("dependency"):
            for file_path in dep_dir.rglob("pip-audit.json"):
                self._parse_pip_audit(file_path, "pip-audit")
            for file_path in dep_dir.rglob("safety.json"):
                self._parse_safety(file_path)

    def _parse_cve_findings(self) -> None:
        logger.info("Parsing CVE ecosystem audit findings...")
        for cve_dir in self.artifact_catalog.successful_artifacts("cve"):
            for file_path in cve_dir.rglob("*-cve-audit.json"):
                if "python" in cve_dir.name:
                    self._parse_pip_audit(file_path, "pip-audit")
                elif "javascript" in cve_dir.name:
                    self._parse_npm_audit(file_path)
                elif "rust" in cve_dir.name:
                    self._parse_cargo_audit(file_path)

    def _parse_pip_audit(self, file_path: Path, tool: str) -> None:
        try:
            with file_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Unable to parse %s results %s: %s", tool, file_path, exc)
            return

        for dependency in data.get("dependencies", []):
            for vulnerability in dependency.get("vulns", []):
                vuln_id = vulnerability.get("id", "unknown")
                self.findings.append(
                    Finding(
                        id=f"{tool.upper()}-{dependency.get('name', 'unknown')}-{vuln_id}",
                        tool=tool,
                        title=f"Vulnerability in {dependency.get('name', 'unknown')}",
                        description=vulnerability.get("description", ""),
                        severity="CRITICAL",
                        package=dependency.get("name"),
                        version=dependency.get("installed_version"),
                        remediation_url=vulnerability.get("advisory_url"),
                        rule_id=vuln_id,
                    )
                )

    def _parse_safety(self, file_path: Path) -> None:
        try:
            with file_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Unable to parse Safety results %s: %s", file_path, exc)
            return

        vulnerabilities = (
            data.get("vulnerabilities", [])
            if isinstance(data, dict)
            else data if isinstance(data, list) else []
        )
        for index, vulnerability in enumerate(vulnerabilities):
            package = vulnerability.get("package_name") or vulnerability.get("name")
            vuln_id = (
                vulnerability.get("CVE")
                or vulnerability.get("vulnerability_id")
                or vulnerability.get("advisory")
                or str(index)
            )
            self.findings.append(
                Finding(
                    id=f"SAFETY-{package or 'unknown'}-{vuln_id}",
                    tool="safety",
                    title=f"Vulnerability in {package or 'unknown'}",
                    description=(
                        vulnerability.get("advisory") or vulnerability.get("description") or ""
                    ),
                    severity=self.severity_map.get(
                        str(vulnerability.get("severity", "high")).lower(), "HIGH"
                    ),
                    package=package,
                    version=(
                        vulnerability.get("analyzed_version")
                        or vulnerability.get("installed_version")
                    ),
                    remediation_url=vulnerability.get("more_info_url"),
                    rule_id=str(vuln_id),
                )
            )

    def _parse_npm_audit(self, file_path: Path) -> None:
        try:
            with file_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Unable to parse npm audit results %s: %s", file_path, exc)
            return

        for package, vulnerability in data.get("vulnerabilities", {}).items():
            advisories = [
                advisory for advisory in vulnerability.get("via", []) if isinstance(advisory, dict)
            ]
            if not advisories:
                advisories = [{}]
            for index, advisory in enumerate(advisories):
                vuln_id = advisory.get("cve") or advisory.get("source") or f"{package}-{index}"
                self.findings.append(
                    Finding(
                        id=f"NPM-{package}-{vuln_id}",
                        tool="npm-audit",
                        title=advisory.get("title") or f"Vulnerability in {package}",
                        description=advisory.get("url", ""),
                        severity=self.severity_map.get(
                            str(vulnerability.get("severity", "low")).lower(), "LOW"
                        ),
                        package=package,
                        version=vulnerability.get("range"),
                        remediation_url=advisory.get("url"),
                        rule_id=str(vuln_id),
                    )
                )

    def _parse_cargo_audit(self, file_path: Path) -> None:
        try:
            with file_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Unable to parse cargo audit results %s: %s", file_path, exc)
            return

        vulnerabilities = data.get("vulnerabilities", {}).get("list", [])
        for index, vulnerability in enumerate(vulnerabilities):
            advisory = vulnerability.get("advisory", {})
            package = vulnerability.get("package", {})
            vuln_id = advisory.get("id") or f"unknown-{index}"
            self.findings.append(
                Finding(
                    id=f"CARGO-{package.get('name', 'unknown')}-{vuln_id}",
                    tool="cargo-audit",
                    title=advisory.get("title")
                    or f"Vulnerability in {package.get('name', 'unknown')}",
                    description=advisory.get("description", ""),
                    severity=self.severity_map.get(
                        str(advisory.get("severity", "unknown")).lower(), "LOW"
                    ),
                    package=package.get("name"),
                    version=package.get("version"),
                    remediation_url=advisory.get("url"),
                    rule_id=vuln_id,
                )
            )

    def _parse_secret_findings(self) -> None:
        """Parse detect-secrets baseline

        Security Note: This processes .secrets.baseline which contains secret hashes.
        We extract only type and line metadata, not actual secret values, to findings.
        """
        logger.info("Parsing secret detection findings...")
        for secrets_dir in self.artifact_catalog.successful_artifacts("secrets"):
            for baseline_file in secrets_dir.rglob(".secrets.baseline"):
                try:
                    with baseline_file.open(encoding="utf-8") as handle:
                        baseline_data = json.load(handle)
                except (OSError, json.JSONDecodeError) as exc:
                    logger.error("Unable to parse secret baseline %s: %s", baseline_file, exc)
                    continue

                for file_path, secrets in baseline_data.get("results", {}).items():
                    for idx, secret in enumerate(secrets):
                        self.findings.append(
                            Finding(
                                id=f"SECRET-{file_path.replace('/', '_')}-{idx:03d}",
                                tool="detect-secrets",
                                title=f"Potential secret in {file_path}",
                                description=secret.get("type", "Unknown secret type"),
                                severity="CRITICAL",
                                file=file_path,
                                line=secret.get("line_number"),
                                status="flagged",
                                agent_assignee="secret-detection-agent",
                            )
                        )

    def _deduplicate_findings(self) -> None:
        """Remove duplicate finding records without collapsing distinct scanner alerts."""
        logger.info("Removing duplicate finding identifiers...")
        seen = {}
        unique_findings = []

        for finding in self.findings:
            dedup_key = (finding.tool, finding.id)
            if dedup_key not in seen:
                seen[dedup_key] = finding
                unique_findings.append(finding)

        self.findings = unique_findings
        logger.info("Retained %s scanner findings", len(self.findings))

    def _normalize_severity(self) -> None:
        """Ensure all severity levels are in standard format"""
        for finding in self.findings:
            finding.severity = self.severity_map.get(finding.severity.lower(), "LOW")

    def _assign_agents(self) -> None:
        """Assign agent responsibilities based on finding type"""
        for finding in self.findings:
            if finding.tool == "codeql":
                finding.agent_assignee = "codeql-alert-resolution-agent"
            elif finding.tool == "github-code-scanning":
                finding.agent_assignee = "codeql-alert-resolution-agent"
            elif finding.tool == "semgrep":
                finding.agent_assignee = "unified-security-scanner"
            elif finding.tool in {"pip-audit", "safety", "npm-audit", "cargo-audit"}:
                finding.agent_assignee = "dependency-security-review-agent"
            elif finding.tool == "trivy":
                finding.agent_assignee = "unified-security-scanner"
            elif finding.tool == "detect-secrets":
                finding.agent_assignee = "secret-detection-agent"

    def _build_report(self) -> Dict[str, Any]:
        """Build comprehensive findings report"""
        logger.info("Building comprehensive findings report...")

        # Group findings by severity
        findings_by_severity = defaultdict(list)
        for finding in self.findings:
            findings_by_severity[finding.severity].append(finding)

        # Group findings by tool
        findings_by_tool = defaultdict(list)
        for finding in self.findings:
            findings_by_tool[finding.tool].append(finding)

        # Count by severity
        severity_counts = {
            "CRITICAL": len(findings_by_severity.get("CRITICAL", [])),
            "HIGH": len(findings_by_severity.get("HIGH", [])),
            "MEDIUM": len(findings_by_severity.get("MEDIUM", [])),
            "LOW": len(findings_by_severity.get("LOW", [])),
            "INFO": len(findings_by_severity.get("INFO", [])),
        }

        # Agent assignment recommendations
        agent_assignments = defaultdict(int)
        for finding in self.findings:
            if finding.agent_assignee:
                agent_assignments[finding.agent_assignee] += 1

        failure_classification = (
            "blocked_by_critical_or_high_vulnerabilities"
            if severity_counts["CRITICAL"] > 0 or severity_counts["HIGH"] > 0
            else (
                "warning_only"
                if severity_counts["MEDIUM"] > 0 or severity_counts["LOW"] > 0
                else "clean"
            )
        )
        raw_evidence_artifacts = sorted(
            str(path) for path in self.artifacts_dir.rglob("*") if path.is_file()
        )

        # Build report structure
        report = {
            "scan_metadata": {
                "repository": self.repository,
                "commit": self.commit_sha,
                "run_id": self.run_id,
                "run_url": f"{self.repo_url}/actions/runs/{self.run_id}",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "security_tab_url": f"{self.repo_url}/security/code-scanning",
                "selected_scans": sorted(self.selected_scans),
            },
            "scan_status": {
                **self.scan_status,
                "github-code-scanning-alerts": self.github_alert_inventory_status,
            },
            "findings_by_severity": {
                severity: [f.to_dict() for f in findings_by_severity.get(severity, [])]
                for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
            },
            "findings_by_tool": {
                tool: [f.to_dict() for f in findings_by_tool.get(tool, [])]
                for tool in sorted(findings_by_tool.keys())
            },
            "finding_index": [f.to_dict() for f in self.findings],
            "severity_summary": severity_counts,
            "failure_classification": failure_classification,
            "raw_evidence_artifacts": raw_evidence_artifacts,
            "summary": {
                "total_findings": len(self.findings),
                "critical_count": severity_counts["CRITICAL"],
                "high_count": severity_counts["HIGH"],
                "medium_count": severity_counts["MEDIUM"],
                "low_count": severity_counts["LOW"],
                "info_count": severity_counts["INFO"],
                "remediable_findings": len([f for f in self.findings if f.status == "open"]),
                "auto_fixable_findings": len([f for f in self.findings if f.agent_assignee]),
                "requires_manual_review": len([f for f in self.findings if not f.agent_assignee]),
                "recommended_agent_handoffs": [
                    {"agent": agent, "findings_count": count}
                    for agent, count in sorted(
                        agent_assignments.items(), key=lambda x: x[1], reverse=True
                    )
                ],
                "severity_summary": severity_counts,
                "failure_classification": failure_classification,
                "raw_evidence_artifacts": raw_evidence_artifacts,
                "existing_code_scanning_alerts": self.github_alert_inventory_status["alert_count"],
            },
        }

        return report

    def save_json(self, output_path: str) -> None:
        """Save report as JSON"""
        ReportWriter.write_json(self.run(), output_path)

    def save_markdown(self, output_path: str) -> None:
        """Save report as Markdown"""
        ReportWriter.write_markdown(self.run(), output_path)


class ReportWriter:
    """Write complete security findings reports in supported formats."""

    @staticmethod
    def write_json(report: Dict[str, Any], output_path: str) -> None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)

    @staticmethod
    def write_markdown(report: Dict[str, Any], output_path: str) -> None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# 🔐 Security Findings Comprehensive Report",
            "",
            f"**Repository:** `{report['scan_metadata']['repository']}`",
            f"**Commit:** `{report['scan_metadata']['commit']}`",
            f"**Run:** [{report['scan_metadata']['run_id']}]({report['scan_metadata']['run_url']})",
            f"**Generated:** {report['scan_metadata']['timestamp']}",
            "",
            "## Scan Status",
            "",
            "| Scan | Selected | Status | Successful artifacts | Expected artifacts |",
            "|---|---:|---|---:|---:|",
        ]
        for scan, status in report.get("scan_status", {}).items():
            lines.append(
                f"| {scan} | {status['selected']} | {status['status']} | "
                f"{status['successful_artifacts']} | {status['expected_artifacts']} |"
            )
        lines.extend(
            [
                "",
                "## Summary",
                "",
                f"- **Total Findings:** {report['summary']['total_findings']}",
                f"- **Critical:** {report['summary']['critical_count']}",
                f"- **High:** {report['summary']['high_count']}",
                f"- **Medium:** {report['summary']['medium_count']}",
                f"- **Low:** {report['summary']['low_count']}",
                "",
                "## Findings by Severity",
                "",
            ]
        )
        for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
            findings = report["findings_by_severity"].get(severity, [])
            if not findings:
                continue
            lines.extend([f"### {severity} ({len(findings)})", ""])
            for finding in findings:
                lines.append(f"- **{finding['title']}** ({finding['tool']})")
                lines.append(f"  - File: `{finding.get('file', 'N/A')}`")
                lines.append(f"  - Description: {finding.get('description', 'N/A')}")
                if finding.get("agent_assignee"):
                    lines.append(f"  - Assigned to: `{finding['agent_assignee']}`")
            lines.append("")
        lines.extend(["## Recommended Agent Handoffs", ""])
        for handoff in report["summary"]["recommended_agent_handoffs"]:
            lines.append(f"- `{handoff['agent']}`: {handoff['findings_count']} findings")
        lines.extend(
            [
                "",
                "[View full security report](reports/security-findings-comprehensive.json)",
            ]
        )
        output_file.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def write_csv_exports(
        report: Dict[str, Any],
        inventory_path: str,
        priority_path: str,
        family_path: str,
    ) -> None:
        findings = report.get("finding_index", [])
        inventory_file = Path(inventory_path)
        inventory_file.parent.mkdir(parents=True, exist_ok=True)
        with inventory_file.open("w", newline="", encoding="utf-8") as handle:
            fields = [
                "alert_id",
                "tool",
                "rule_id",
                "severity",
                "file_path",
                "start_line",
                "end_line",
                "commit_sha",
                "run_id",
            ]
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for finding in findings:
                writer.writerow(
                    {
                        "alert_id": finding.get("id", ""),
                        "tool": finding.get("tool", ""),
                        "rule_id": finding.get("rule_id", ""),
                        "severity": finding.get("severity", ""),
                        "file_path": finding.get("file", ""),
                        "start_line": finding.get("line", ""),
                        "end_line": "",
                        "commit_sha": report.get("scan_metadata", {}).get("commit", ""),
                        "run_id": report.get("scan_metadata", {}).get("run_id", ""),
                    }
                )

        severity_priority = {
            "CRITICAL": 100,
            "HIGH": 75,
            "MEDIUM": 50,
            "LOW": 25,
            "INFO": 0,
        }
        priority_file = Path(priority_path)
        priority_file.parent.mkdir(parents=True, exist_ok=True)
        with priority_file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["family_id", "priority_score", "severity", "reachable"],
            )
            writer.writeheader()
            for finding in findings:
                writer.writerow(
                    {
                        "family_id": (
                            f"{finding.get('tool', 'unknown')}:"
                            f"{finding.get('rule_id') or 'unknown'}"
                        ),
                        "priority_score": severity_priority.get(finding.get("severity", "LOW"), 0),
                        "severity": finding.get("severity", "LOW"),
                        "reachable": "unknown",
                    }
                )

        family_counts = Counter(
            (
                finding.get("tool", "unknown"),
                finding.get("rule_id") or "unknown",
            )
            for finding in findings
        )
        family_file = Path(family_path)
        family_file.parent.mkdir(parents=True, exist_ok=True)
        with family_file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["family_id", "rule_id", "count"])
            writer.writeheader()
            for (tool, rule_id), count in sorted(family_counts.items()):
                writer.writerow(
                    {
                        "family_id": f"{tool}:{rule_id}",
                        "rule_id": rule_id,
                        "count": count,
                    }
                )


def _parse_github_code_scanning_inventory(
    aggregator: FindingsAggregator,
) -> None:
    """Add the complete open GHAS alert inventory as a separately identified source."""
    status = aggregator.github_alert_inventory_status
    if not status["selected"]:
        return

    artifact_dir = aggregator.artifacts_dir / "security-suite-codeql-alerts"
    status["available_artifacts"] = int(artifact_dir.is_dir())
    if not artifact_dir.is_dir():
        return
    if not ArtifactCatalog._artifact_contract_succeeded(artifact_dir):
        return

    try:
        with (artifact_dir / "api_inventory_raw.json").open(encoding="utf-8") as handle:
            alerts = json.load(handle)
        with (artifact_dir / "api_inventory_summary.json").open(encoding="utf-8") as handle:
            summary = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Unable to read GitHub code-scanning inventory: %s", exc)
        return

    if (
        not isinstance(alerts, list)
        or not isinstance(summary, dict)
        or summary.get("total") != len(alerts)
    ):
        logger.error("GitHub code-scanning inventory failed count validation")
        return

    status["status"] = "success"
    status["successful_artifacts"] = 1
    status["alert_count"] = len(alerts)
    for alert in alerts:
        if not isinstance(alert, dict):
            continue
        rule = alert.get("rule") or {}
        instance = alert.get("most_recent_instance") or {}
        location = instance.get("location") or {}
        rule_id = str(rule.get("id") or "unknown")
        alert_number = alert.get("number")
        if alert_number is None:
            continue
        severity = rule.get("security_severity_level") or rule.get("severity") or "unknown"
        aggregator.findings.append(
            Finding(
                id=f"GHAS-{alert_number}",
                tool="github-code-scanning",
                title=rule.get("name") or rule.get("description") or rule_id,
                description=rule.get("description", ""),
                severity=aggregator.severity_map.get(str(severity).lower(), "LOW"),
                file=location.get("path"),
                line=location.get("start_line"),
                rule_id=rule_id,
                remediation_url=alert.get("html_url"),
                status=str(alert.get("state") or "open"),
                agent_assignee="codeql-alert-resolution-agent",
                metadata={
                    "alert_number": alert_number,
                    "tool": (alert.get("tool") or {}).get("name", "unknown"),
                    "ref": instance.get("ref"),
                    "commit_sha": instance.get("commit_sha"),
                },
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate security findings from all scanning tools"
    )
    parser.add_argument(
        "--artifacts-dir",
        default="security-suite-artifacts",
        help="Directory containing security-suite-* artifacts",
    )
    parser.add_argument(
        "--output-json",
        default=".codex/security-findings-comprehensive.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--output-md",
        default="security-findings-comprehensive.md",
        help="Output Markdown file path",
    )
    parser.add_argument(
        "--repo-url",
        default=os.getenv("GITHUB_SERVER_URL", "https://github.com")
        + "/"
        + os.getenv("GITHUB_REPOSITORY", "unknown/repo"),
        help="Repository URL",
    )
    parser.add_argument(
        "--run-id",
        default=os.getenv("GITHUB_RUN_ID", "unknown"),
        help="GitHub Actions run ID",
    )
    parser.add_argument(
        "--commit-sha",
        default=os.getenv("GITHUB_SHA", "unknown"),
        help="Commit SHA",
    )
    parser.add_argument(
        "--repository",
        default=os.getenv("GITHUB_REPOSITORY", "unknown/repo"),
        help="Repository name (owner/repo)",
    )
    parser.add_argument("--output-csv", help="Optional normalized alert inventory CSV")
    parser.add_argument("--output-priority-csv", help="Optional alert priority queue CSV")
    parser.add_argument("--output-family-csv", help="Optional alert family index CSV")

    args = parser.parse_args()
    csv_options = (
        args.output_csv,
        args.output_priority_csv,
        args.output_family_csv,
    )
    if any(csv_options) and not all(csv_options):
        parser.error(
            "--output-csv, --output-priority-csv, and --output-family-csv "
            "must be provided together"
        )

    # Create aggregator and generate reports
    aggregator = FindingsAggregator(
        artifacts_dir=args.artifacts_dir,
        repo_url=args.repo_url,
        run_id=args.run_id,
        commit_sha=args.commit_sha,
        repository=args.repository,
    )

    try:
        report = aggregator.run()
        ReportWriter.write_json(report, args.output_json)
        ReportWriter.write_markdown(report, args.output_md)
        if args.output_csv and args.output_priority_csv and args.output_family_csv:
            ReportWriter.write_csv_exports(
                report,
                args.output_csv,
                args.output_priority_csv,
                args.output_family_csv,
            )
        logger.info("✅ Aggregation complete")
        return 0
    except Exception as e:
        logger.error(f"❌ Aggregation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
