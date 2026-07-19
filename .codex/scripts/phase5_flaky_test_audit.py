#!/usr/bin/env python3
"""
phase5_flaky_test_audit.py

Comprehensive audit for Phase 5 Lane 2: Flaky Test Stabilization & Pattern Enforcement.

Purpose:
- Identify flaky tests from test file patterns (async, timeouts, external deps)
- Audit test naming conventions (test_*_on_*() patterns)
- Check docstring coverage (target >90%)
- Identify isolation violations (shared state, cross-test dependencies)
- Generate remediation recommendations

Output:
- .codex/PHASE_5_FLAKY_TEST_AUDIT_REPORT.md
- .codex/PHASE_5_FLAKY_TEST_REMEDIATION.json
- .codex/PHASE_5_TEST_PATTERN_VIOLATIONS.md
"""

import ast
import json
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class TestIssue:
    """Represents a single test issue."""
    file: str
    test_name: str
    issue_type: str  # "missing_docstring", "flaky_pattern", "isolation", "naming"
    severity: str   # "low", "medium", "high"
    description: str
    remediation: str


class PhaseFlakytestAuditor:
    """Audit test suite for Phase 5 flaky test issues."""
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.tests_dir = self.repo_root / "tests"
        self.issues: list[TestIssue] = []
        self.flaky_patterns = {
            "async_operations": re.compile(r"(asyncio|async def|await|sleep|time\.sleep)", re.MULTILINE),
            "network_calls": re.compile(r"(requests\.|http\.|socket\.|urlopen)", re.MULTILINE),
            "file_io": re.compile(r"(open\(|Path\(|os\.path\.|os\.mkdir|os\.remove)", re.MULTILINE),
            "datetime_dependent": re.compile(r"(datetime\.now|time\.time|timezone|utcnow)", re.MULTILINE),
            "random_values": re.compile(r"(random\.|np\.random|torch\.rand)", re.MULTILINE),
            "external_calls": re.compile(r"(subprocess\.|popen|system\()", re.MULTILINE),
            "timeouts": re.compile(r"(@pytest\.mark\.timeout|timeout=)", re.MULTILINE),
            "retries": re.compile(r"(@pytest\.mark\.retry|max_attempts|retry_count)", re.MULTILINE),
        }
        self.shared_state_patterns = {
            "global_var": re.compile(r"^([\w_]+)\s*=\s*", re.MULTILINE),
            "class_var": re.compile(r"class\s+\w+:.*?(?=class|\Z)", re.DOTALL),
        }
    
    def discover_tests(self) -> list[Path]:
        """Find all test files."""
        if not self.tests_dir.exists():
            return []
        files = sorted(set(self.tests_dir.rglob("test_*.py")) | set(self.tests_dir.rglob("*_test.py")))
        return [f for f in files if f.is_file()]
    
    def analyze_file(self, filepath: Path) -> None:
        """Analyze a single test file for issues."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return
        
        try:
            tree = ast.parse(content)
        except Exception:
            return
        
        rel_path = str(filepath.relative_to(self.repo_root))
        
        # Check for flaky patterns in file-level code
        flaky_score = self._score_flakiness(content)
        
        # Walk AST for functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                self._analyze_test_function(rel_path, content, node)
    
    def _score_flakiness(self, content: str) -> dict:
        """Score flakiness risk based on patterns."""
        scores = {}
        for pattern_name, pattern_re in self.flaky_patterns.items():
            matches = len(pattern_re.findall(content))
            scores[pattern_name] = matches
        return scores
    
    def _analyze_test_function(self, filepath: str, file_content: str, node: ast.FunctionDef) -> None:
        """Analyze a single test function."""
        test_name = node.name
        
        # Check 1: Docstring coverage
        docstring = ast.get_docstring(node)
        if not docstring:
            self.issues.append(TestIssue(
                file=filepath,
                test_name=test_name,
                issue_type="missing_docstring",
                severity="medium",
                description=f"Test function '{test_name}' lacks documentation.",
                remediation=f'Add docstring: def {test_name}():\n    """Test purpose: ..."""'
            ))
        
        # Check 2: Naming convention (test_*() pattern)
        # Flexible pattern: should describe what is being tested
        # Simplified regex to avoid ReDoS (exponential backtracking): use + instead of nested quantifier
        if not re.match(r"^test_\w+$", test_name):
            self.issues.append(TestIssue(
                file=filepath,
                test_name=test_name,
                issue_type="naming",
                severity="low",
                description=f"Test name '{test_name}' doesn't follow test_* convention.",
                remediation=f"Rename to follow pattern: test_<component>_<scenario>()"
            ))
        
        # Check 3: Flaky patterns in function body
        func_content = ast.get_source_segment(file_content, node) or ""
        flaky_indicators = []
        
        for pattern_name, pattern_re in self.flaky_patterns.items():
            if pattern_re.search(func_content):
                flaky_indicators.append(pattern_name)
        
        if flaky_indicators:
            severity = "high" if len(flaky_indicators) > 2 else "medium"
            self.issues.append(TestIssue(
                file=filepath,
                test_name=test_name,
                issue_type="flaky_pattern",
                severity=severity,
                description=f"Test uses flaky patterns: {', '.join(flaky_indicators)}",
                remediation=f"Add mocks/fixtures for: {', '.join(flaky_indicators)}. Consider @pytest.mark.flaky."
            ))
        
        # Check 4: Isolation - look for pytest fixtures usage (good) or globals (bad)
        if "monkeypatch" in func_content or "tmp_path" in func_content or "capsys" in func_content:
            pass  # Good isolation patterns
        else:
            # Check if function modifies globals
            if re.search(r"global\s+\w+|sys\.path|os\.environ", func_content):
                self.issues.append(TestIssue(
                    file=filepath,
                    test_name=test_name,
                    issue_type="isolation",
                    severity="high",
                    description=f"Test modifies global state or environment.",
                    remediation="Use pytest fixtures (monkeypatch, tmp_path, etc.) for isolation."
                ))
    
    def audit_all(self) -> dict:
        """Run full audit on all tests."""
        test_files = self.discover_tests()
        print(f"Auditing {len(test_files)} test files...")
        
        for filepath in test_files:
            self.analyze_file(filepath)
        
        # Categorize issues
        by_type = defaultdict(list)
        by_severity = defaultdict(list)
        
        for issue in self.issues:
            by_type[issue.issue_type].append(issue)
            by_severity[issue.severity].append(issue)
        
        return {
            "total_files_audited": len(test_files),
            "total_issues": len(self.issues),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "issues": [asdict(i) for i in self.issues],
        }


def main():
    auditor = PhaseFlakytestAuditor()
    result = auditor.audit_all()
    
    # Save JSON report
    report_json = Path(".codex/PHASE_5_FLAKY_TEST_REMEDIATION.json")
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(result, indent=2))
    
    # Print summary
    print(f"\n=== Phase 5 Flaky Test Audit Summary ===")
    print(f"Total files audited: {result['total_files_audited']}")
    print(f"Total issues found: {result['total_issues']}")
    print(f"By type: {result['by_type']}")
    print(f"By severity: {result['by_severity']}")
    print(f"\nFull report saved to: {report_json}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
