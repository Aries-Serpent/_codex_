#!/usr/bin/env python3
"""
Audit Runner

Purpose:
    Runs audit_runner

Usage:
    python scripts/space_traversal/audit_runner.py [options]

    Examples:
    $ python scripts/space_traversal/audit_runner.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

"""
Audit Runner - Orchestrates security audits across the codebase
"""

import argparse
import importlib.util
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

EXIT_MISSING_ARTIFACTS = 2
EXIT_SCORE_REGRESSION = 3
EXIT_LOW_MATURITY = 4
EXIT_MISSING_DETECTOR = 5

_audit_spec = importlib.util.find_spec("scripts.space_traversal.security_audit")
_deps_spec = importlib.util.find_spec("scripts.space_traversal.dependency_scanner")
_quality_spec = importlib.util.find_spec("scripts.space_traversal.code_quality_checker")
_vuln_spec = importlib.util.find_spec("scripts.space_traversal.vulnerability_db")

if _audit_spec:
    from .security_audit import SecurityAuditor
else:
    SecurityAuditor = None

if _deps_spec:
    from .dependency_scanner import DependencyScanner
else:
    DependencyScanner = None

if _quality_spec:
    from .code_quality_checker import CodeQualityChecker
else:
    CodeQualityChecker = None

if _vuln_spec:
    from .vulnerability_db import VulnerabilityDatabase
else:
    VulnerabilityDatabase = None

if importlib.util.find_spec("yaml"):
    import yaml
else:
    yaml = None


class AuditRunner:
    """Main orchestrator for security audits"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the audit runner

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.auditor = SecurityAuditor(self.config) if SecurityAuditor else None
        self.dep_scanner = DependencyScanner(self.config) if DependencyScanner else None
        self.quality_checker = CodeQualityChecker(self.config) if CodeQualityChecker else None
        self.vuln_db = VulnerabilityDatabase(self.config) if VulnerabilityDatabase else None
        
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        try:
            if config_path and config_path.exists():
                if yaml and config_path.suffix in [".yml", ".yaml"]:
                    with open(config_path, encoding="utf-8") as f:
                        return yaml.safe_load(f)
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error("Failed to load config from %s: %s", config_path, e)

        # Return default configuration
        return {
            "scan_paths": ["src", "scripts"],
            "exclude_paths": [".git", "__pycache__", "venv"],
            "severity_threshold": "medium",
            "output_format": "json",
        }

    def run_full_audit(self, target_path: Path) -> Dict[str, Any]:
        """
        Run complete security audit suite

        Args:
            target_path: Root path to audit

        Returns:
            Dictionary containing audit results
        """
        logger.info("Starting full audit of %s", target_path)
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "target": str(target_path),
            "audits": {},
        }

        if self.auditor:
            try:
                logger.info("Running security audit...")
                results["audits"]["security"] = self.auditor.scan(target_path)
            except Exception as e:
                logger.error("Security audit failed: %s", e)
                results["audits"]["security"] = {"error": str(e)}

        if self.dep_scanner:
            try:
                logger.info("Scanning dependencies...")
                results["audits"]["dependencies"] = self.dep_scanner.scan(target_path)
            except Exception as e:
                logger.error("Dependency scan failed: %s", e)
                results["audits"]["dependencies"] = {"error": str(e)}

        if self.quality_checker:
            try:
                logger.info("Checking code quality...")
                results["audits"]["quality"] = self.quality_checker.check(target_path)
            except Exception as e:
                logger.error("Quality check failed: %s", e)
                results["audits"]["quality"] = {"error": str(e)}

        if self.vuln_db:
            try:
                logger.info("Checking vulnerability database...")
                results["audits"]["vulnerabilities"] = self.vuln_db.check(target_path)
            except Exception as e:
                logger.error("Vulnerability check failed: %s", e)
                results["audits"]["vulnerabilities"] = {"error": str(e)}

        results["summary"] = self._generate_summary(results["audits"])

        logger.info("Audit complete")
        return results

    def _generate_summary(self, audits: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from audit results"""
        summary = {
            "total_issues": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        try:
            for audit_results in audits.values():
                if isinstance(audit_results, dict) and "issues" in audit_results:
                    for issue in audit_results["issues"]:
                        summary["total_issues"] += 1
                        severity = issue.get("severity", "info").lower()
                        if severity in summary:
                            summary[severity] += 1
        except Exception as e:
            logger.error("Failed to generate summary: %s", e)

        return summary

    def save_results(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save audit results to file"""
        try:
            output_format = self.config.get("output_format", "json")

            if output_format == "yaml" and yaml:
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(results, f, default_flow_style=False)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)

            logger.info("Results saved to %s", output_path)
        except Exception as e:
            logger.error("Failed to save results: %s", e)
            raise


def main() -> None:
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Run security audits")
    parser.add_argument("target", type=Path, nargs="?", help="Target path to audit")
    parser.add_argument("--config", type=Path, help="Configuration file")
    parser.add_argument("--output", type=Path, help="Output file path")

    args = parser.parse_args()

    if args.target is None:
        print("Target path is required", file=sys.stderr)
        sys.exit(2)

    try:
        runner = AuditRunner(args.config)
        results = runner.run_full_audit(args.target)

        if args.output:
            runner.save_results(results, args.output)
        else:
            print(json.dumps(results, indent=2))

    except Exception as e:
        logger.error("Audit failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
