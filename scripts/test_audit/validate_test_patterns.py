#!/usr/bin/env python3
"""
Test Suite Pattern Validator
Identifies and reports test anti-patterns in real-time
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Dict

class TestPatternValidator:
    def __init__(self, test_dir: Path = Path("tests")):
        self.test_dir = test_dir
        self.findings = defaultdict(list)
    
    def validate_assertions(self, content: str, filepath: str) -> None:
        """Check for tests without assertions."""
        test_funcs = re.findall(
            r'def (test_\w+)\([^)]*\):\s*(.*?)(?=\n    def |\nclass |\Z)',
            content, re.DOTALL
        )
        
        for func_name, func_body in test_funcs:
            if not any(x in func_body for x in ["assert ", "yield", "raise ", "pytest.fail"]):
                self.findings["no_assertion"].append((filepath, func_name))
    
    def validate_mock_patterns(self, content: str, filepath: str) -> None:
        """Check for mock anti-patterns."""
        # Side effect list exhaustion
        if re.search(r'\.side_effect\s*=\s*\[', content):
            self.findings["side_effect_list"].append(filepath)
        
        # Potential serialization issues
        if "json.dumps" in content and "Mock" in content:
            self.findings["mock_serialization"].append(filepath)
    
    def validate_isolation(self, content: str, filepath: str) -> None:
        """Check for test isolation issues."""
        monkeypatch_count = len(re.findall(r'monkeypatch\.', content))
        if monkeypatch_count > 5:
            self.findings["isolation_risk"].append((filepath, monkeypatch_count))
    
    def validate_flakiness(self, content: str, filepath: str) -> None:
        """Check for flaky test patterns."""
        if re.search(r'time\.sleep\(|sleep\(', content):
            sleep_count = len(re.findall(r'time\.sleep\(|sleep\(', content))
            self.findings["flaky_sleep"].append((filepath, sleep_count))
    
    def validate_fixture_scope(self, content: str, filepath: str) -> None:
        """Check fixture scope issues."""
        if "@pytest.fixture" in content:
            fixture_count = len(re.findall(r'@pytest\.fixture', content))
            if fixture_count > 5:
                self.findings["high_fixture_count"].append((filepath, fixture_count))
    
    def run_validation(self) -> Dict[str, list]:
        """Run all validations on test files."""
        for py_file in self.test_dir.rglob("test_*.py"):
            try:
                content = py_file.read_text()
                relative_path = str(py_file.relative_to(self.test_dir))
                
                self.validate_assertions(content, relative_path)
                self.validate_mock_patterns(content, relative_path)
                self.validate_isolation(content, relative_path)
                self.validate_flakiness(content, relative_path)
                self.validate_fixture_scope(content, relative_path)
            except Exception as e:
                print(f"Warning: Could not process {py_file}: {e}", file=sys.stderr)
        
        return dict(self.findings)
    
    def report(self, findings: Dict[str, list]) -> str:
        """Generate report from findings."""
        report_lines = ["# Test Pattern Validation Report\n"]
        
        # Summary
        total_issues = sum(len(v) for v in findings.values())
        report_lines.append(f"**Total Issues Found**: {total_issues}\n")
        
        # Details by category
        categories = [
            ("no_assertion", "🔴 Tests Without Assertions"),
            ("isolation_risk", "🟠 Test Isolation Issues"),
            ("flaky_sleep", "🟠 Flaky Timing Patterns"),
            ("side_effect_list", "🟡 Mock Side-Effect Lists"),
            ("mock_serialization", "🟡 Mock Serialization"),
            ("high_fixture_count", "🟡 High Fixture Density"),
        ]
        
        for key, title in categories:
            if key in findings and findings[key]:
                report_lines.append(f"\n## {title}\n")
                report_lines.append(f"**Count**: {len(findings[key])}\n")
                
                # Show samples
                samples = findings[key][:5]
                for item in samples:
                    if isinstance(item, tuple):
                        report_lines.append(f"- {item[0]}: {item[1]}")
                    else:
                        report_lines.append(f"- {item}")
        
        return "\n".join(report_lines)

def main():
    validator = TestPatternValidator()
    findings = validator.run_validation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST PATTERN VALIDATION RESULTS")
    print("=" * 80)
    
    for category, items in findings.items():
        if items:
            print(f"\n{category}: {len(items)} issues")
    
    # Generate report
    report = validator.report(findings)
    print("\n" + report)
    
    # Return exit code based on severity
    critical_count = len(findings.get("no_assertion", [])) + len(findings.get("isolation_risk", []))
    
    if critical_count > 100:
        print("\n⚠️  Critical issues detected")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
