#!/usr/bin/env python3
"""Token utility adoption validator for PHASE 4.2 of CODEX_MASTER_KEY campaign.

This validator scans all Python scripts to verify correct adoption of the
_token_resolver utility and detect remaining anti-patterns.

VALIDATION RULES:
1. Rule 1: All scripts using elevated operations MUST import get_token
2. Rule 2: No inline token patterns allowed (direct CODEX_MASTER_KEY access)
3. Rule 3: All PR/variable/workflow operations MUST use get_token_scope validation
4. Rule 4: Token values never logged (validate log patterns)

Exit Codes:
    0 = All scripts compliant (≥95% adoption)
    1 = Violations found (anti-patterns detected)
    2 = Error during scanning

Example:
    $ python validate_token_utility_adoption.py --check-only
    $ python validate_token_utility_adoption.py --json-output /tmp/report.json --verbose
    $ python validate_token_utility_adoption.py --show-violations
"""

import argparse
import ast
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
from typing import Dict, List, Optional, Set, Tuple

# Add parent directory to path for CI execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ViolationDetail:
    """Represents a single validation violation."""

    rule_id: str  # Rule 1, Rule 2, Rule 3, Rule 4
    rule_name: str
    line_number: int
    line_content: str
    severity: str  # critical, high, medium


@dataclass
class ScriptAnalysis:
    """Analysis result for a single Python script."""

    file_path: str
    script_name: str
    is_compliant: bool
    has_token_resolver_import: bool
    violations: List[ViolationDetail] = field(default_factory=list)
    anti_patterns_found: Set[str] = field(default_factory=set)
    uses_elevated_operations: bool = False
    compliance_score: float = 1.0  # 1.0 = 100% compliant

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "script_name": self.script_name,
            "is_compliant": self.is_compliant,
            "has_token_resolver_import": self.has_token_resolver_import,
            "uses_elevated_operations": self.uses_elevated_operations,
            "compliance_score": round(self.compliance_score, 3),
            "violations": [asdict(v) for v in self.violations],
            "anti_patterns_found": list(self.anti_patterns_found),
        }


@dataclass
class AdoptionReport:
    """Overall adoption report."""

    total_scripts_scanned: int
    compliant_scripts: int
    non_compliant_scripts: int
    scripts_with_violations: int
    adoption_percentage: float
    target_percentage: float
    meets_target: bool
    violations_by_rule: Dict[str, int] = field(default_factory=dict)
    anti_patterns_summary: Dict[str, int] = field(default_factory=dict)
    timestamp: str = ""
    script_analyses: List[ScriptAnalysis] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_scripts_scanned": self.total_scripts_scanned,
            "compliant_scripts": self.compliant_scripts,
            "non_compliant_scripts": self.non_compliant_scripts,
            "scripts_with_violations": self.scripts_with_violations,
            "adoption_percentage": round(self.adoption_percentage, 2),
            "target_percentage": self.target_percentage,
            "meets_target": self.meets_target,
            "violations_by_rule": self.violations_by_rule,
            "anti_patterns_summary": self.anti_patterns_summary,
            "timestamp": self.timestamp,
            "script_analyses": [s.to_dict() for s in self.script_analyses],
        }


class TokenAdoptionValidator:
    """Validator for token utility adoption across all Python scripts."""

    # Anti-patterns to detect
    INLINE_TOKEN_PATTERNS = [
        'get_token(required_elevated=True)[0]',
        'get_token(required_elevated=True)[0]',
        'get_token(required_elevated=True)[0]',
        'get_token(required_elevated=True)[0]',
        'get_token(required_elevated=True)[0]',
        'get_token(required_elevated=True)[0]',
        'CODEX_MASTER_KEY',
        "CODEX_MASTER_KEY",
    ]

    # Elevated operation keywords that indicate need for get_token
    ELEVATED_OPERATIONS = [
        "workflow",
        "actions:write",
        "security_events",
        "admin",
        "deploy",
        "pull_request_write",
        "workflow_dispatch",
    ]

    def __init__(self, verbose: bool = False):
        """Initialize validator.

        Args:
            verbose: Enable verbose logging.
        """
        self.verbose = verbose
        self.findings: Dict[str, ScriptAnalysis] = {}
        if verbose:
            logger.setLevel(logging.DEBUG)

    def find_python_scripts(
        self, root_dir: str = REPO_ROOT
    ) -> List[str]:
        """Find all Python scripts in the repository.

        Args:
            root_dir: Root directory to search.

        Returns:
            List of absolute paths to Python scripts.
        """
        scripts = []
        root_path = Path(root_dir)

        # Exclude common non-relevant directories
        exclude_dirs = {
            "__pycache__",
            ".git",
            "venv",
            "env",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "site-packages",
        }

        for py_file in root_path.rglob("*.py"):
            # Skip if in excluded directories
            if any(ex in py_file.parts for ex in exclude_dirs):
                continue
            scripts.append(str(py_file))

        return sorted(scripts)

    def parse_script(self, file_path: str) -> Tuple[Optional[ast.Module], str]:
        """Parse Python script into AST.

        Args:
            file_path: Path to Python script.

        Returns:
            Tuple of (AST module, file content) or (None, content) if parse fails.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            tree = ast.parse(content)
            return tree, content
        except (SyntaxError, ValueError) as e:
            if self.verbose:
                logger.debug(f"Failed to parse {file_path}: {e}")
            return None, ""

    def check_has_token_resolver_import(self, tree: Optional[ast.Module]) -> bool:
        """Check if script imports from _token_resolver.

        Args:
            tree: AST module to check.

        Returns:
            True if _token_resolver is imported.
        """
        if tree is None:
            return False

        for node in ast.walk(tree):
            # Check 'from X import Y' statements
            if isinstance(node, ast.ImportFrom):
                if node.module and "_token_resolver" in node.module:
                    return True
            # Check 'import X' statements
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "_token_resolver" in alias.name:
                        return True

        return False

    def check_uses_elevated_operations(
        self, tree: Optional[ast.Module], content: str
    ) -> bool:
        """Check if script uses elevated operations.

        Args:
            tree: AST module to check.
            content: Raw file content.

        Returns:
            True if elevated operations detected.
        """
        if tree is None:
            return False

        # Check content for elevated operation keywords
        content_lower = content.lower()
        for operation in self.ELEVATED_OPERATIONS:
            if operation in content_lower:
                return True

        return False

    def find_inline_token_patterns(self, content: str) -> Set[str]:
        """Find inline token access patterns in content.

        Args:
            content: Raw file content.

        Returns:
            Set of found anti-patterns.
        """
        found_patterns = set()

        for pattern in self.INLINE_TOKEN_PATTERNS:
            if pattern in content:
                found_patterns.add(pattern)

        # Also check for direct environment variable access patterns
        if 'os.environ.get("CODEX' in content or 'os.environ["CODEX' in content:
            found_patterns.add("os.environ.get/set for CODEX keys")

        if "os.getenv" in content and "CODEX" in content:
            found_patterns.add("os.getenv for CODEX keys")

        return found_patterns

    def check_token_logging(self, content: str) -> bool:
        """Check if token values are being logged.

        Args:
            content: Raw file content.

        Returns:
            True if potential token logging found.
        """
        # Look for patterns like logging the token value itself
        suspicious_patterns = [
            "logger.debug(token",
            "logger.info(token",
            "logging.debug(token",
            "logging.info(token",
            'print(f".*token',
            'f".*{token',
            "print(token)",
        ]

        for pattern in suspicious_patterns:
            if pattern in content:
                return True

        return False

    def check_scope_validation(
        self, tree: Optional[ast.Module], content: str
    ) -> bool:
        """Check if script uses token scope validation.

        Args:
            tree: AST module to check.
            content: Raw file content.

        Returns:
            True if scope validation is used.
        """
        if tree is None:
            return False

        # Check for get_token_scope or validate_token_scope usage
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if "scope" in node.func.id.lower():
                        return True

        # Fallback to content checking
        return "get_token_scope" in content or "validate_token_scope" in content

    def analyze_script(self, file_path: str) -> ScriptAnalysis:
        """Analyze a single Python script.

        Args:
            file_path: Path to Python script.

        Returns:
            ScriptAnalysis with findings.
        """
        script_name = os.path.basename(file_path)
        tree, content = self.parse_script(file_path)

        analysis = ScriptAnalysis(
            file_path=file_path,
            script_name=script_name,
            is_compliant=True,
            has_token_resolver_import=self.check_has_token_resolver_import(tree),
            uses_elevated_operations=self.check_uses_elevated_operations(tree, content),
        )

        # Rule 1: All scripts using elevated operations MUST import get_token
        if (
            analysis.uses_elevated_operations
            and not analysis.has_token_resolver_import
        ):
            violation = ViolationDetail(
                rule_id="Rule 1",
                rule_name="Elevated ops without token resolver import",
                line_number=1,
                line_content="Script uses elevated operations but doesn't import get_token",
                severity="critical",
            )
            analysis.violations.append(violation)
            analysis.is_compliant = False
            analysis.compliance_score = 0.0

        # Rule 2: No inline token patterns allowed
        inline_patterns = self.find_inline_token_patterns(content)
        if inline_patterns:
            for line_num, line in enumerate(content.split("\n"), 1):
                for pattern in inline_patterns:
                    if pattern in line:
                        violation = ViolationDetail(
                            rule_id="Rule 2",
                            rule_name="Inline token pattern detected",
                            line_number=line_num,
                            line_content=line.strip(),
                            severity="critical",
                        )
                        analysis.violations.append(violation)
                        analysis.is_compliant = False
                        analysis.anti_patterns_found.add(pattern)

            analysis.compliance_score *= 0.0

        # Rule 3: Token operations should use scope validation
        if (
            analysis.uses_elevated_operations
            and analysis.has_token_resolver_import
            and not self.check_scope_validation(tree, content)
        ):
            violation = ViolationDetail(
                rule_id="Rule 3",
                rule_name="Missing scope validation for elevated token operations",
                line_number=1,
                line_content="Script uses elevated token operations but lacks scope validation",
                severity="high",
            )
            analysis.violations.append(violation)
            analysis.compliance_score *= 0.7

        # Rule 4: Token values never logged
        if self.check_token_logging(content):
            for line_num, line in enumerate(content.split("\n"), 1):
                if "token" in line.lower() and any(
                    x in line for x in ["logger", "logging", "print("]
                ):
                    violation = ViolationDetail(
                        rule_id="Rule 4",
                        rule_name="Token value may be logged",
                        line_number=line_num,
                        line_content=line.strip(),
                        severity="high",
                    )
                    analysis.violations.append(violation)
                    analysis.compliance_score *= 0.8

        return analysis

    def scan_all_scripts(
        self, max_scripts: Optional[int] = None
    ) -> List[ScriptAnalysis]:
        """Scan all Python scripts in repository.

        Args:
            max_scripts: Maximum number of scripts to scan (for testing).

        Returns:
            List of ScriptAnalysis results.
        """
        scripts = self.find_python_scripts()
        if max_scripts:
            scripts = scripts[:max_scripts]

        analyses = []
        for i, script_path in enumerate(scripts, 1):
            if self.verbose and i % 100 == 0:
                logger.debug(f"Scanned {i}/{len(scripts)} scripts...")

            analysis = self.analyze_script(script_path)
            analyses.append(analysis)
            self.findings[script_path] = analysis

        return analyses

    def generate_report(
        self, analyses: List[ScriptAnalysis], target_percentage: float = 95.0
    ) -> AdoptionReport:
        """Generate adoption report from analyses.

        Args:
            analyses: List of script analyses.
            target_percentage: Target adoption percentage.

        Returns:
            AdoptionReport with metrics.
        """
        from datetime import datetime

        total = len(analyses)
        compliant = sum(1 for a in analyses if a.is_compliant)
        non_compliant = total - compliant
        with_violations = sum(1 for a in analyses if a.violations)

        adoption_pct = (compliant / total * 100) if total > 0 else 0

        # Aggregate violations by rule
        violations_by_rule: Dict[str, int] = {}
        anti_patterns_summary: Dict[str, int] = {}

        for analysis in analyses:
            for violation in analysis.violations:
                violations_by_rule[violation.rule_id] = (
                    violations_by_rule.get(violation.rule_id, 0) + 1
                )
            for pattern in analysis.anti_patterns_found:
                anti_patterns_summary[pattern] = (
                    anti_patterns_summary.get(pattern, 0) + 1
                )

        report = AdoptionReport(
            total_scripts_scanned=total,
            compliant_scripts=compliant,
            non_compliant_scripts=non_compliant,
            scripts_with_violations=with_violations,
            adoption_percentage=adoption_pct,
            target_percentage=target_percentage,
            meets_target=adoption_pct >= target_percentage,
            violations_by_rule=violations_by_rule,
            anti_patterns_summary=anti_patterns_summary,
            timestamp=datetime.now().isoformat(),
            script_analyses=analyses,
        )

        return report

    def print_report(self, report: AdoptionReport, show_violations: bool = False):
        """Print formatted adoption report.

        Args:
            report: AdoptionReport to print.
            show_violations: Whether to show individual violations.
        """
        print("\n" + "=" * 80)
        print("TOKEN UTILITY ADOPTION REPORT - PHASE 4.2")
        print("=" * 80)
        print(f"\nTimestamp: {report.timestamp}")
        print(f"\nTotal scripts scanned: {report.total_scripts_scanned}")
        print(f"Compliant scripts: {report.compliant_scripts}")
        print(f"Non-compliant scripts: {report.non_compliant_scripts}")
        print(f"Scripts with violations: {report.scripts_with_violations}")
        print(
            f"\nAdoption Rate: {report.adoption_percentage:.2f}% (Target: {report.target_percentage}%)"
        )
        print(f"Target Met: {'✅ YES' if report.meets_target else '❌ NO'}")

        print("\nViolations by Rule:")
        for rule_id in sorted(report.violations_by_rule.keys()):
            count = report.violations_by_rule[rule_id]
            print(f"  {rule_id}: {count} violations")

        if report.anti_patterns_summary:
            print("\nAnti-Patterns Found:")
            for pattern, count in sorted(
                report.anti_patterns_summary.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  {pattern}: {count} occurrences")

        if show_violations:
            print("\n" + "-" * 80)
            print("DETAILED VIOLATIONS")
            print("-" * 80)

            for analysis in report.script_analyses:
                if analysis.violations:
                    print(f"\n📄 {analysis.script_name}")
                    print(f"   Path: {analysis.file_path}")
                    print(f"   Compliance: {analysis.compliance_score:.1%}")
                    for violation in analysis.violations:
                        print(f"   - {violation.rule_id} ({violation.severity})")
                        print(f"     Line {violation.line_number}: {violation.line_content}")

        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate token utility adoption across all scripts"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Check compliance without detailed output",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        help="Output JSON report to specified file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--show-violations",
        action="store_true",
        help="Show detailed violations in output",
    )
    parser.add_argument(
        "--target",
        type=float,
        default=95.0,
        help="Target adoption percentage (default: 95)",
    )
    parser.add_argument(
        "--max-scripts",
        type=int,
        help="Maximum scripts to scan (for testing)",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=REPO_ROOT,
        help="Root directory to scan",
    )

    args = parser.parse_args()

    # Create validator
    validator = TokenAdoptionValidator(verbose=args.verbose)

    # Scan scripts
    print("🔍 Scanning Python scripts for token utility adoption...")
    analyses = validator.scan_all_scripts(max_scripts=args.max_scripts)

    # Generate report
    report = validator.generate_report(analyses, target_percentage=args.target)

    # Print report
    if not args.check_only:
        validator.print_report(report, show_violations=args.show_violations)

    # Output JSON if requested
    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"✅ JSON report written to: {args.json_output}")

    # Determine exit code
    if report.meets_target:
        exit_code = 0
        print("✅ Token utility adoption meets target!")
    else:
        exit_code = 1
        print("❌ Token utility adoption below target!")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
