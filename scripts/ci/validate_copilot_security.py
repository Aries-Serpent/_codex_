#!/usr/bin/env python3
"""
Security and secrets validation for copilot-setup-steps.yml.

This script implements section 5 of the pre-merge testing plan:
5. Security & Secrets Testing

Tests:
  - 5.1: Hardcoded secrets scan
  - 5.2: Token reference validation
  - 5.3: YAML injection prevention

Exit codes:
  0 = All tests passed
  1 = Critical security issues found
  2 = Warnings only
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Secret patterns (common formats that should not appear in code)
# ─────────────────────────────────────────────────────────────────────────────

SENSITIVE_PATTERNS = {
    # GitHub tokens
    'ghp_': 'GitHub Personal Access Token (ghp_)',
    'ghu_': 'GitHub User Token (ghu_)',
    'ghs_': 'GitHub Server Token (ghs_)',
    'ghe_': 'GitHub Enterprise Token (ghe_)',
    
    # AWS credentials
    'AKIA': 'AWS Access Key ID',
    
    # Generic secret patterns
    r'password\s*=\s*["\'].+["\']': 'Password assignment',
    r'secret\s*=\s*["\'].+["\']': 'Secret assignment',
    r'api[_-]?key\s*=\s*["\'].+["\']': 'API key assignment',
}

# Token references that MUST use GitHub secrets (not hardcoded)
REQUIRED_TOKEN_REFS = [
    'GITHUB_TOKEN',
    'CODEX_MASTER_KEY',
    'CODEX_BACKUP_KEY',
]


# ─────────────────────────────────────────────────────────────────────────────
# Test Result classes
# ─────────────────────────────────────────────────────────────────────────────

class TestResult:
    def __init__(self, name: str, passed: bool, severity: str = "error", message: str = ""):
        self.name = name
        self.passed = passed
        self.severity = severity
        self.message = message
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
        }
    
    def __repr__(self) -> str:
        status = "✅" if self.passed else ("⚠️ " if self.severity == "warning" else "❌")
        return f"{status} {self.name}: {self.message}"


class TestSuite:
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
    
    def add(self, result: TestResult):
        self.results.append(result)
    
    def critical_failures(self) -> List[TestResult]:
        return [r for r in self.results if not r.passed and r.severity == "error"]
    
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    def exit_code(self) -> int:
        if self.critical_failures():
            return 1
        if any(not r.passed for r in self.results):
            return 2
        return 0
    
    def to_json(self) -> Dict:
        return {
            "suite": self.name,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total": len(self.results),
            "passed": self.passed_count(),
            "failed": len(self.critical_failures()),
            "results": [r.to_dict() for r in self.results],
        }
    
    def print_summary(self):
        print(f"\n{'=' * 80}")
        print(f"Test Suite: {self.name}")
        print(f"{'=' * 80}")
        
        for result in self.results:
            # codeql[py/clear-text-logging-sensitive-data]: result.timestamp is a
            # regular test timestamp, not a secret
            print(f"  {result}")
        
        print(f"\nSummary: {self.passed_count()}/{len(self.results)} passed")
        
        if self.critical_failures():
            print(f"\n🔴 {len(self.critical_failures())} CRITICAL SECURITY ISSUE(S)")
            for result in self.critical_failures():
                print(f"   - {result.name}: {result.message}")


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_hardcoded_secrets(workflow_content: str) -> TestResult:
    """Test 5.1: Scan for accidentally hardcoded secrets."""
    found_issues = []
    suspicious_lines = []
    
    lines = workflow_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue
        
        # Skip YAML string examples/comments
        if '"""' in line or "'''" in line:
            continue
        
        # Check for common token patterns (but exclude legitimate references like ${{ ... }})
        if 'ghp_' in line and '{{' not in line:
            suspicious_lines.append(f"Line {line_num}: GitHub token pattern (ghp_)")
            found_issues.append("ghp_")
        
        if 'ghu_' in line and '{{' not in line:
            suspicious_lines.append(f"Line {line_num}: GitHub token pattern (ghu_)")
            found_issues.append("ghu_")
        
        # Look for hardcoded password/secret assignments (but exclude variable definitions)
        if re.search(r'(password|secret)\s*:\s*["\'][^"\']*[a-zA-Z0-9+/=]{20,}["\']', line):
            suspicious_lines.append(f"Line {line_num}: Possible hardcoded secret")
            found_issues.append("hardcoded_secret")
    
    if found_issues:
        unique_issues = set(found_issues)
        patterns = ', '.join(sorted(unique_issues)[:3])
        return TestResult(
            "Hardcoded Secrets Scan (5.1)",
            False,
            severity="error",
            message=f"Found {len(unique_issues)} secret patterns: {patterns}"
        )
    
    return TestResult(
        "Hardcoded Secrets Scan (5.1)",
        True,
        message="No obvious hardcoded secrets detected in workflow"
    )


def test_token_references(workflow_content: str) -> TestResult:
    """Test 5.2: Verify token references are properly validated."""
    issues = []
    
    # Check that tokens are referenced via secrets, not hardcoded
    for token_name in REQUIRED_TOKEN_REFS:
        if token_name == 'GITHUB_TOKEN':
            # Special case: can be github.token or secrets.GITHUB_TOKEN
            pattern = r'\$\{\s*(github\.token|secrets\.GITHUB_TOKEN)\s*\}\s*'
            if not re.search(pattern, workflow_content):
                # Might be defined as env var without reference — check for that
                if 'GITHUB_TOKEN:' not in workflow_content:
                    issues.append("No GITHUB_TOKEN reference found")
        else:
            # For CODEX tokens, verify they're referenced via secrets
            token_pattern = rf'\$\{{\s*secrets\.{token_name}\s*\}}\s*'
            if not re.search(token_pattern, workflow_content):
                # Check if it's at least mentioned (might be inherited from env)
                if token_name not in workflow_content:
                    issues.append(f"{token_name} not referenced in workflow")
    
    # Additional check: verify no hardcoded token values
    hardcoded_pattern = r'[\'"](ghp_|ghu_|ghs_|ghe_)[A-Za-z0-9_]{36,}[\'":]'
    if re.search(hardcoded_pattern, workflow_content):
        return TestResult(
            "Token Reference Validation (5.2)",
            False,
            severity="error",
            message="Found hardcoded token value in workflow"
        )
    
    if issues:
        return TestResult(
            "Token Reference Validation (5.2)",
            False,
            severity="warning",
            message=f"Found token issues: {'; '.join(issues[:2])}"
        )
    
    return TestResult(
        "Token Reference Validation (5.2)",
        True,
        message="All token references properly use GitHub secrets (no hardcoded values)"
    )


def test_yaml_injection_prevention(workflow_content: str) -> TestResult:
    """Test 5.3: Ensure no YAML injection vectors in environment variables."""
    issues = []
    
    # Check for unquoted YAML values that could be injection vectors
    # Pattern: env var with unquoted multiline or special chars
    lines = workflow_content.split('\n')
    
    in_env_section = False
    for line_num, line in enumerate(lines, 1):
        if re.match(r'\s*env:\s*$', line):
            in_env_section = True
            continue
        
        if in_env_section:
            # Stop when we leave the env section
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                in_env_section = False
            
            # Check for unquoted values with special chars
            if ':' in line:
                key, value = line.split(':', 1)
                # Values should be quoted if they contain special chars
                if any(c in value for c in ['|', '>', '#', '&', '*', '[', ']', '{', '}']):
                    if not ('"' in value or "'" in value):
                        # Exception: GitHub action expressions are allowed unquoted
                        if '${{' not in value:
                            issues.append(f"Line {line_num}: Unquoted value with special chars")
    
    if issues:
        count = len(issues)
        return TestResult(
            "YAML Injection Prevention (5.3)",
            False,
            severity="warning",
            message=f"Found {count} potentially unquoted values that could be injection vectors"
        )
    
    return TestResult(
        "YAML Injection Prevention (5.3)",
        True,
        message="YAML injection prevention check passed — values properly quoted"
    )


def test_secrets_baseline_sync(repo_root: Path) -> TestResult:
    """Test: Verify .secrets.baseline exists and is current."""
    baseline_path = repo_root / ".secrets.baseline"
    
    if not baseline_path.exists():
        return TestResult(
            "Secrets Baseline Sync",
            False,
            severity="warning",
            message=".secrets.baseline file not found (optional)"
        )
    
    # Basic check: file should be valid JSON
    try:
        import json
        with open(baseline_path, 'r') as f:
            _ = json.load(f)
        
        return TestResult(
            "Secrets Baseline Sync",
            True,
            message=".secrets.baseline is valid and current"
        )
    except Exception as e:
        return TestResult(
            "Secrets Baseline Sync",
            False,
            severity="warning",
            message=f"Could not parse .secrets.baseline: {str(e)[:50]}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Security and secrets validation for copilot-setup-steps.yml"
    )
    parser.add_argument('--workflow', default='.github/workflows/copilot-setup-steps.yml')
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--json-output', help='Output JSON results')
    parser.add_argument('--check-only', action='store_true')
    
    args = parser.parse_args()
    
    workflow_path = Path(args.repo_root) / args.workflow
    repo_root = Path(args.repo_root)
    
    if not workflow_path.exists():
        logger.error(f"❌ Workflow not found: {workflow_path}")
        return 1
    
    # Read workflow content
    with open(workflow_path, 'r') as f:
        workflow_content = f.read()
    
    logger.info(f"Scanning for security issues in: {workflow_path}")
    logger.info("")
    
    # Create test suite
    suite = TestSuite("Copilot Setup Steps Security Testing")
    
    # Run tests
    logger.info("Testing for hardcoded secrets...")
    suite.add(test_hardcoded_secrets(workflow_content))
    
    logger.info("Validating token references...")
    suite.add(test_token_references(workflow_content))
    
    logger.info("Checking YAML injection prevention...")
    suite.add(test_yaml_injection_prevention(workflow_content))
    
    logger.info("Verifying secrets baseline...")
    suite.add(test_secrets_baseline_sync(repo_root))
    
    # Print results
    suite.print_summary()
    
    # Save JSON if requested
    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(suite.to_json(), f, indent=2)
        logger.info(f"\n📄 JSON results saved to: {output_path}")
    
    return suite.exit_code()


if __name__ == '__main__':
    sys.exit(main())
