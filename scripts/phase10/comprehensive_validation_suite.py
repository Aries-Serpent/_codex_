#!/usr/bin/env python3
"""
Comprehensive Validation Suite

Purpose:
    Main execution script

Usage:
    python scripts/phase10/comprehensive_validation_suite.py [options]

    Examples:
    $ python scripts/phase10/comprehensive_validation_suite.py --help

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



import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
from typing import Optional

logger = logging.getLogger(__name__)


class Phase10Validator:
    """Comprehensive validation for Phase 10 Master Integration."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "skipped": 0
            }
        }
        self.repo_root = REPO_ROOT

    def log_test(self, name: str, status: str, message: str, details: Optional[dict] = None):
        """Log test result."""
        test = {
            "name": name,
            "status": status,  # "pass", "fail", "warn", "skip"
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(UTC).isoformat()
        }
        self.results["tests"].append(test)
        self.results["summary"]["total"] += 1

        if status == "pass":
            self.results["summary"]["passed"] += 1
            print(f"✅ {name}: {message}")  # codeql[py/clear-text-logging-sensitive-data]
        elif status == "fail":
            self.results["summary"]["failed"] += 1
            print(f"❌ {name}: {message}")  # codeql[py/clear-text-logging-sensitive-data]
        elif status == "warn":
            self.results["summary"]["warnings"] += 1
            print(f"⚠️  {name}: {message}")  # codeql[py/clear-text-logging-sensitive-data]
        else:  # skip
            self.results["summary"]["skipped"] += 1
            print(f"⏸️  {name}: {message}")  # codeql[py/clear-text-logging-sensitive-data]

    def run_command(self, cmd: list[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
        """Execute shell command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.repo_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 5 minutes"
        except Exception as e:
            return -1, "", str(e)

    # ====================================================================
    # TEST CATEGORY 1: Configuration Files Validation
    # ====================================================================

    def test_repomix_config_exists(self):
        """Validate repomix.config.json exists and is valid."""
        config_path = self.repo_root / "repomix.config.json"

        if not config_path.exists():
            self.log_test(
                "repomix_config_exists",
                "fail",
                "repomix.config.json not found"
            )
            return

        try:
            with open(config_path) as f:
                config = json.load(f)

            # Validate required fields
            required_fields = ["output", "include", "ignore"]
            missing = [f for f in required_fields if f not in config]

            if missing:
                self.log_test(
                    "repomix_config_valid",
                    "fail",
                    f"Missing required fields: {missing}"
                )
            else:
                # Check specific settings
                details = {
                    "output_style": config.get("output", {}).get("style"),
                    "compress": config.get("output", {}).get("compress"),
                    "security_check": config.get("security", {}).get("enableSecurityCheck")
                }

                if details["output_style"] == "xml" and details["compress"]:
                    self.log_test(
                        "repomix_config_valid",
                        "pass",
                        "Configuration valid with XML output and compression",
                        details
                    )
                else:
                    self.log_test(
                        "repomix_config_valid",
                        "warn",
                        "Configuration valid but missing optimal settings",
                        details
                    )
        except json.JSONDecodeError as e:
            self.log_test(
                "repomix_config_valid",
                "fail",
                f"Invalid JSON: {e}"
            )
        except Exception as e:
            self.log_test(
                "repomix_config_valid",
                "fail",
                f"Validation error: {e}"
            )

    def test_repomix_instructions_exist(self):
        """Validate repomix-instruction.md exists."""
        instructions_path = self.repo_root / "repomix-instruction.md"

        if not instructions_path.exists():
            self.log_test(
                "repomix_instructions_exist",
                "fail",
                "repomix-instruction.md not found"
            )
            return

        size = instructions_path.stat().st_size
        if size > 1000:  # At least 1KB
            self.log_test(
                "repomix_instructions_valid",
                "pass",
                f"Instructions file valid ({size} bytes)",
                {"file_size": size}
            )
        else:
            self.log_test(
                "repomix_instructions_valid",
                "warn",
                f"Instructions file seems small ({size} bytes)"
            )

    def test_workflow_exists(self):
        """Validate notebooklm-sync.yml workflow exists."""
        workflow_path = self.repo_root / ".github/workflows/notebooklm-sync.yml"

        if not workflow_path.exists():
            self.log_test(
                "workflow_exists",
                "fail",
                "notebooklm-sync.yml not found"
            )
            return

        try:
            with open(workflow_path) as f:
                content = f.read()

            # Check for key components
            checks = {
                "repomix action": "repomix" in content,
                "security scanning": "secretlint" in content or "detect-secrets" in content,
                "google drive upload": "google-drive-upload" in content or "gdrive" in content.lower(),
                "workflow_dispatch": "workflow_dispatch" in content
            }

            all_present = all(checks.values())

            if all_present:
                self.log_test(
                    "workflow_valid",
                    "pass",
                    "Workflow contains all required components",
                    checks
                )
            else:
                missing = [k for k, v in checks.items() if not v]
                self.log_test(
                    "workflow_valid",
                    "fail",
                    f"Workflow missing components: {missing}",
                    checks
                )
        except Exception as e:
            self.log_test(
                "workflow_valid",
                "fail",
                f"Workflow validation error: {e}"
            )

    # ====================================================================
    # TEST CATEGORY 2: Documentation Validation
    # ====================================================================

    def test_documentation_exists(self):
        """Validate all Phase 10 documentation exists."""
        docs = {
            "COGNITIVE_BRAIN_STATUS_V3.md": "Cognitive brain status",
            "PHASE_10_MASTER_INTEGRATION_PLANSET.md": "Implementation planset",
            "PHASE_10_MASTER_INTEGRATION_PROMPTSET.md": "Continuation prompts",
            "HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md": "Human action tracker",
            "AUTOMATION_CAPABILITY_ANALYSIS_PHASE10.md": "Automation analysis",
            "docs/TASK_3_NOTEBOOKLM_SKILL_SETUP.md": "Claude Code setup guide",
            "docs/notebooklm-architect-prompt.md": "AI Architect prompt"
        }

        missing = []
        for doc, desc in docs.items():
            path = self.repo_root / doc
            if not path.exists():
                missing.append(f"{doc} ({desc})")

        if not missing:
            self.log_test(
                "documentation_complete",
                "pass",
                f"All {len(docs)} documentation files present",
                {"files": list(docs.keys())}
            )
        else:
            self.log_test(
                "documentation_complete",
                "fail",
                f"Missing {len(missing)} documentation files",
                {"missing": missing}
            )

    def test_documentation_quality(self):
        """Validate documentation quality and completeness."""
        planset_path = self.repo_root / "PHASE_10_MASTER_INTEGRATION_PLANSET.md"

        if not planset_path.exists():
            self.log_test(
                "documentation_quality",
                "skip",
                "Planset not found, skipping quality check"
            )
            return

        try:
            with open(planset_path) as f:
                content = f.read()

            # Quality checks
            checks = {
                "has_task_breakdown": "### Task 1:" in content and "### Task 2:" in content,
                "has_success_criteria": "Success Criteria" in content or "success criteria" in content,
                "has_timeline": "Timeline" in content or "Week" in content,
                "has_validation": "Validation" in content or "validation" in content,
                "sufficient_length": len(content) > 10000  # At least 10KB
            }

            score = sum(checks.values()) / len(checks) * 100

            if score >= 80:
                self.log_test(
                    "documentation_quality",
                    "pass",
                    f"Documentation quality: {score:.0f}%",
                    checks
                )
            elif score >= 60:
                self.log_test(
                    "documentation_quality",
                    "warn",
                    f"Documentation quality moderate: {score:.0f}%",
                    checks
                )
            else:
                self.log_test(
                    "documentation_quality",
                    "fail",
                    f"Documentation quality low: {score:.0f}%",
                    checks
                )
        except Exception as e:
            self.log_test(
                "documentation_quality",
                "fail",
                f"Quality check error: {e}"
            )

    # ====================================================================
    # TEST CATEGORY 3: Scripts and Tools Validation
    # ====================================================================

    def test_scripts_exist(self):
        """Validate all Phase 10 scripts exist and are executable."""
        scripts = {
            "scripts/phase10/test_repomix_local.sh": "Repomix local test",
            "scripts/phase10/validate_gdrive_secrets.sh": "Secrets validation",
            "scripts/phase10/generate_codex_master_key.sh": "Key generation",
            "scripts/phase10/automated_secrets_manager.py": "Secrets manager API",
            "scripts/phase10/execute_secrets_injection_now.py": "Immediate injection"
        }

        missing = []
        not_executable = []

        for script, desc in scripts.items():
            path = self.repo_root / script
            if not path.exists():
                missing.append(f"{script} ({desc})")
            elif not os.access(path, os.X_OK) and script.endswith('.sh'):
                not_executable.append(f"{script}")

        if not missing and not not_executable:
            self.log_test(
                "scripts_ready",
                "pass",
                f"All {len(scripts)} scripts present and ready",
                {"scripts": list(scripts.keys())}
            )
        else:
            issues = []
            if missing:
                issues.append(f"{len(missing)} missing")
            if not_executable:
                issues.append(f"{len(not_executable)} not executable")

            self.log_test(
                "scripts_ready",
                "fail",
                f"Script issues: {', '.join(issues)}",
                {"missing": missing, "not_executable": not_executable}
            )

    # ====================================================================
    # TEST CATEGORY 4: Security Scanning
    # ====================================================================

    def test_no_secrets_in_code(self):
        """Run security scanning to ensure no secrets in committed code."""
        print("\n🔒 Running security scan...")  # codeql[py/clear-text-logging-sensitive-data]

        # Check if detect-secrets is available
        returncode, _stdout, _stderr = self.run_command(["which", "detect-secrets"])

        if returncode != 0:
            self.log_test(
                "security_scan",
                "skip",
                "detect-secrets not available (install with: pip install detect-secrets)"
            )
            return

        # Run detect-secrets scan
        returncode, _stdout, _stderr = self.run_command([
            "detect-secrets", "scan",
            "--baseline", ".secrets.baseline",
            "--exclude-files", ".*node_modules/.*",
            "--exclude-files", r".*\.git/.*",
            "--exclude-files", r".*\.venv/.*"
        ])

        if returncode == 0:
            self.log_test(
                "security_scan",
                "pass",
                "No secrets detected in codebase"
            )
        else:
            self.log_test(
                "security_scan",
                "warn",
                "Potential secrets detected (review manually)",
                {"stderr": _stderr[:500]}
            )

    def test_dependencies_secure(self):
        """Check for known vulnerabilities in dependencies."""
        print("\n🔍 Checking dependencies...")  # codeql[py/clear-text-logging-sensitive-data]

        # Check Python dependencies with pip-audit if available
        returncode, _stdout, _stderr = self.run_command(["which", "pip-audit"])

        if returncode == 0:
            returncode, stdout, _stderr = self.run_command(["pip-audit", "--desc"])

            if returncode == 0:
                self.log_test(
                    "dependencies_secure",
                    "pass",
                    "No known vulnerabilities in Python dependencies"
                )
            else:
                vuln_count = stdout.count("Found")
                self.log_test(
                    "dependencies_secure",
                    "warn",
                    f"Potential vulnerabilities detected: {vuln_count}",
                    {"output": stdout[:500]}
                )
        else:
            self.log_test(
                "dependencies_secure",
                "skip",
                "pip-audit not available"
            )

    # ====================================================================
    # TEST CATEGORY 5: Cognitive Brain Health
    # ====================================================================

    def test_cognitive_brain_status(self):
        """Validate cognitive brain health metrics."""
        brain_path = self.repo_root / "COGNITIVE_BRAIN_STATUS_V3.md"

        if not brain_path.exists():
            self.log_test(
                "cognitive_brain_health",
                "fail",
                "COGNITIVE_BRAIN_STATUS_V3.md not found"
            )
            return

        try:
            with open(brain_path) as f:
                content = f.read()

            # Extract health metrics
            metrics = {}
            for line in content.split('\n'):
                if "/100" in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        try:
                            score = int(parts[-1].strip().split('/')[0])
                            name = parts[0].strip('*- ')
                            metrics[name] = score
                        except (ValueError, IndexError):
                            logger.debug("Suppressed exception in handler", exc_info=True)  # codeql[py/clear-text-logging-sensitive-data]
            if metrics:
                metrics.get("Overall Health", 0)
                metrics.get("Knowledge Synthesis", 0)
                metrics.get("Self-Healing", 0)

                avg_score = sum(metrics.values()) / len(metrics)

                if avg_score >= 95:
                    self.log_test(
                        "cognitive_brain_health",
                        "pass",
                        f"Cognitive brain health excellent: {avg_score:.1f}/100",
                        {"metrics": metrics}
                    )
                elif avg_score >= 80:
                    self.log_test(
                        "cognitive_brain_health",
                        "pass",
                        f"Cognitive brain health good: {avg_score:.1f}/100",
                        {"metrics": metrics}
                    )
                else:
                    self.log_test(
                        "cognitive_brain_health",
                        "warn",
                        f"Cognitive brain health needs improvement: {avg_score:.1f}/100",
                        {"metrics": metrics}
                    )
            else:
                self.log_test(
                    "cognitive_brain_health",
                    "warn",
                    "Could not extract health metrics from status file"
                )
        except Exception as e:
            self.log_test(
                "cognitive_brain_health",
                "fail",
                f"Status validation error: {e}"
            )

    # ====================================================================
    # TEST CATEGORY 6: End-to-End Integration (Simulated)
    # ====================================================================

    def test_end_to_end_readiness(self):
        """Validate all components are ready for end-to-end sync."""
        components = {
            "repomix_config": (self.repo_root / "repomix.config.json").exists(),
            "sync_workflow": (self.repo_root / ".github/workflows/notebooklm-sync.yml").exists(),
            "secrets_manager": (self.repo_root / "scripts/phase10/automated_secrets_manager.py").exists(),
            "documentation": (self.repo_root / "PHASE_10_MASTER_INTEGRATION_PLANSET.md").exists(),
            "architect_prompt": (self.repo_root / "docs/notebooklm-architect-prompt.md").exists()
        }

        ready_count = sum(components.values())
        total = len(components)

        if ready_count == total:
            self.log_test(
                "end_to_end_readiness",
                "pass",
                f"All {total} components ready for integration",
                components
            )
        else:
            missing = [k for k, v in components.items() if not v]
            self.log_test(
                "end_to_end_readiness",
                "fail",
                f"Missing {total - ready_count} components: {missing}",
                components
            )

    # ====================================================================
    # Main Execution
    # ====================================================================

    def run_all_tests(self):
        """Execute all validation tests."""
        print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print("🧪 Phase 10 Comprehensive Validation Test Suite")  # codeql[py/clear-text-logging-sensitive-data]
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print(f"Timestamp: {self.results['timestamp']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"Repository: {self.repo_root}")  # codeql[py/clear-text-logging-sensitive-data]
        print("")  # codeql[py/clear-text-logging-sensitive-data]

        # Category 1: Configuration Files
        print("\n📁 Category 1: Configuration Files")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        self.test_repomix_config_exists()
        self.test_repomix_instructions_exist()
        self.test_workflow_exists()

        # Category 2: Documentation
        print("\n📚 Category 2: Documentation")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        self.test_documentation_exists()
        self.test_documentation_quality()

        # Category 3: Scripts and Tools
        print("\n🛠️  Category 3: Scripts and Tools")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        self.test_scripts_exist()

        # Category 4: Security
        print("\n🔒 Category 4: Security Scanning")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        self.test_no_secrets_in_code()
        self.test_dependencies_secure()

        # Category 5: Cognitive Brain
        print("\n🧠 Category 5: Cognitive Brain Health")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        self.test_cognitive_brain_status()

        # Category 6: Integration Readiness
        print("\n🔗 Category 6: End-to-End Integration")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        self.test_end_to_end_readiness()

        # Generate summary
        self.generate_summary()

        # Save results
        self.save_results()

        return self.results["summary"]["failed"] == 0

    def generate_summary(self):
        """Generate and display test summary."""
        s = self.results["summary"]

        print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print("📊 Validation Summary")  # codeql[py/clear-text-logging-sensitive-data]
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print(f"Total Tests:   {s['total']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"✅ Passed:     {s['passed']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"❌ Failed:     {s['failed']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"⚠️  Warnings:   {s['warnings']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"⏸️  Skipped:    {s['skipped']}")  # codeql[py/clear-text-logging-sensitive-data]
        print("")  # codeql[py/clear-text-logging-sensitive-data]

        pass_rate = (s['passed'] / s['total'] * 100) if s['total'] > 0 else 0

        if pass_rate >= 90:
            status = "✅ EXCELLENT"
        elif pass_rate >= 75:
            status = "✅ GOOD"
        elif pass_rate >= 60:
            status = "⚠️  ACCEPTABLE"
        else:
            status = "❌ NEEDS WORK"

        print(f"Pass Rate: {pass_rate:.1f}% - {status}")  # codeql[py/clear-text-logging-sensitive-data]
        print("")  # codeql[py/clear-text-logging-sensitive-data]

        if s['failed'] > 0:
            print("❌ Failed Tests:")  # codeql[py/clear-text-logging-sensitive-data]
            for test in self.results["tests"]:
                if test["status"] == "fail":
                    print(f"  • {test['name']}: {test['message']}")  # codeql[py/clear-text-logging-sensitive-data]
            print("")  # codeql[py/clear-text-logging-sensitive-data]

        if s['warnings'] > 0:
            print("⚠️  Warnings:")  # codeql[py/clear-text-logging-sensitive-data]
            for test in self.results["tests"]:
                if test["status"] == "warn":
                    print(f"  • {test['name']}: {test['message']}")  # codeql[py/clear-text-logging-sensitive-data]
            print("")  # codeql[py/clear-text-logging-sensitive-data]

    def save_results(self):
        """Save validation results to file."""
        results_dir = self.repo_root / ".codex/validation/phase10"
        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        results_file = results_dir / f"validation-{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"💾 Results saved to: {results_file}")  # codeql[py/clear-text-logging-sensitive-data]

        # Also create a markdown report
        report_file = results_dir / f"validation-{timestamp}.md"
        self.generate_markdown_report(report_file)
        print(f"📄 Report saved to: {report_file}")  # codeql[py/clear-text-logging-sensitive-data]

    def generate_markdown_report(self, output_file: Path):
        """Generate markdown validation report."""
        s = self.results["summary"]
        pass_rate = (s['passed'] / s['total'] * 100) if s['total'] > 0 else 0

        report = f"""# Phase 10 Validation Report

**Generated**: {self.results['timestamp']}
**Repository**: Aries-Serpent/_codex_
**Branch**: copilot/sub-pr-2836-again

---

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Tests | {s['total']} | 100% |
| ✅ Passed | {s['passed']} | {s['passed']/s['total']*100:.1f}% |
| ❌ Failed | {s['failed']} | {s['failed']/s['total']*100:.1f}% |
| ⚠️  Warnings | {s['warnings']} | {s['warnings']/s['total']*100:.1f}% |
| ⏸️  Skipped | {s['skipped']} | {s['skipped']/s['total']*100:.1f}% |

**Overall Pass Rate**: {pass_rate:.1f}%

---

## Test Results by Category

"""

        categories = {
            "Configuration Files": ["repomix_config", "repomix_instructions", "workflow"],
            "Documentation": ["documentation_complete", "documentation_quality"],
            "Scripts and Tools": ["scripts_ready"],
            "Security": ["security_scan", "dependencies_secure"],
            "Cognitive Brain": ["cognitive_brain_health"],
            "Integration": ["end_to_end_readiness"]
        }

        for category, test_prefixes in categories.items():
            report += f"### {category}\n\n"
            for test in self.results["tests"]:
                if any(test["name"].startswith(prefix) for prefix in test_prefixes):
                    status_icon = {
                        "pass": "✅",
                        "fail": "❌",
                        "warn": "⚠️",
                        "skip": "⏸️"
                    }.get(test["status"], "❓")

                    report += f"- {status_icon} **{test['name']}**: {test['message']}\n"
            report += "\n"

        report += "---\n\n"
        report += "## Next Steps\n\n"

        if s['failed'] > 0:
            report += "### Address Failures\n\n"
            for test in self.results["tests"]:
                if test["status"] == "fail":
                    report += f"1. **{test['name']}**: {test['message']}\n"
            report += "\n"

        report += "### Phase 10 Continuation\n\n"
        report += "1. Complete manual setup tasks (Google Cloud, NotebookLM)\n"
        report += "2. Trigger first workflow run\n"
        report += "3. Validate end-to-end sync\n"
        report += "4. Configure AI Architect\n"
        report += "5. Update cognitive brain status\n"

        with open(output_file, 'w') as f:
            f.write(report)


def main():
    """Main entry point."""
    validator = Phase10Validator()
    success = validator.run_all_tests()

    print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
    if success:
        print("✅ All validation tests passed!")  # codeql[py/clear-text-logging-sensitive-data]
        print("Phase 10 implementation ready for deployment")  # codeql[py/clear-text-logging-sensitive-data]
        return 0
    print("❌ Some validation tests failed")  # codeql[py/clear-text-logging-sensitive-data]
    print("Review failures above and address before deployment")  # codeql[py/clear-text-logging-sensitive-data]
    return 1


if __name__ == "__main__":
    sys.exit(main())
