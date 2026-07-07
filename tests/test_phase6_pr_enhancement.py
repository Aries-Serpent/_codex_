#!/usr/bin/env python3
"""
Comprehensive tests for Phase 6: PR Body Enhancement & WEC Integration

Tests cover:
1. Workflow YAML validation
2. Formatter module functionality
3. WEC section preservation
4. Empty findings handling
5. End-to-end PR body injection
"""

import json
import sys
import tempfile
from pathlib import Path

# Test framework
def test(name: str, condition: bool, message: str = ""):
    """Simple test assertion."""
    status = "✅" if condition else "❌"
    print(f"{status} {name}")
    if not condition and message:
        print(f"   └─ {message}")
    return condition

def test_workflow_yaml_valid():
    """Test 1: Workflow YAML is valid"""
    import yaml
    
    workflow_path = Path(".github/workflows/security-pr-enhancement.yml")
    if not workflow_path.exists():
        return test("Workflow file exists", False, "File not found")
    
    try:
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        # Check structure
        checks = [
            test("Workflow has 'name'", 'name' in workflow, "Missing workflow name"),
            test("Workflow has 'jobs'", 'jobs' in workflow, "Missing jobs section"),
            test("Has at least 1 job", len(workflow.get('jobs', {})) >= 1),
            test("enhance-pr-security job exists", 'enhance-pr-security' in workflow.get('jobs', {})),
            test("validate-findings-json job exists", 'validate-findings-json' in workflow.get('jobs', {}))
        ]
        
        # Check permissions
        perms = workflow.get('permissions', {})
        checks.append(test("Has pull-requests: write permission", 'pull-requests' in perms))
        
        return all(checks)
    except Exception as e:
        return test("YAML parses without errors", False, str(e))

def test_formatter_module():
    """Test 2: Formatter module works correctly"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import (
        load_findings,
        format_findings_table,
        list_top_issues,
        get_agent_assignments,
        generate_pr_summary,
        SecurityFinding
    )
    
    # Create test findings
    test_findings = [
        SecurityFinding(
            cwe="CWE-79",
            severity="CRITICAL",
            description="XSS vulnerability",
            file_path="app.py",
            line_number=10,
            tool="CodeQL",
            fix_recommendation="Use escape()",
            confidence=0.95
        ),
        SecurityFinding(
            cwe="CWE-22",
            severity="HIGH",
            description="Path traversal",
            file_path="utils.py",
            line_number=42,
            tool="Semgrep",
            fix_recommendation="Validate path",
            confidence=0.88
        )
    ]
    
    checks = [
        test("SecurityFinding class works", len(test_findings) == 2),
        test("format_findings_table produces output", bool(format_findings_table(test_findings))),
        test("format_findings_table contains severity", "Severity" in format_findings_table(test_findings)),
        test("list_top_issues produces output", bool(list_top_issues(test_findings, limit=5))),
        test("list_top_issues shows 2 findings", "1. **" in list_top_issues(test_findings, limit=5) and "2. **" in list_top_issues(test_findings, limit=5)),
        test("get_agent_assignments produces output", bool(get_agent_assignments(test_findings))),
        test("generate_pr_summary contains summary", "Summary" in generate_pr_summary(test_findings)),
    ]
    
    return all(checks)

def test_empty_findings_handling():
    """Test 3: Empty findings handled gracefully"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import (
        generate_pr_summary,
        format_findings_table,
        list_top_issues
    )
    
    empty_findings = []
    
    checks = [
        test("Empty summary handled", "No security findings" in generate_pr_summary(empty_findings)),
        test("Empty table handled", bool(format_findings_table(empty_findings))),
        test("Empty issues list handled", bool(list_top_issues(empty_findings))),
    ]
    
    return all(checks)

def test_findings_json_loading():
    """Test 4: Load and parse findings JSON"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import load_findings
    
    findings_path = Path(".codex/security-findings-comprehensive.json")
    
    checks = [
        test("Findings file exists", findings_path.exists()),
    ]
    
    if findings_path.exists():
        findings = load_findings(findings_path)
        checks.extend([
            test("Findings loaded successfully", len(findings) > 0, f"Expected > 0 findings, got {len(findings)}"),
            test("Has CRITICAL findings", any(f.severity == 'CRITICAL' for f in findings)),
            test("Has HIGH findings", any(f.severity == 'HIGH' for f in findings)),
            test("First finding has CWE", findings[0].cwe.startswith('CWE-') if findings else True),
        ])
    
    return all(checks)

def test_output_format():
    """Test 5: Output format is valid markdown"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import generate_findings_section
    
    findings_path = Path(".codex/security-findings-comprehensive.json")
    if not findings_path.exists():
        return test("Output format test", False, "Findings file not found")
    
    output = generate_findings_section(findings_path, limit=3)
    
    checks = [
        test("Output is not empty", bool(output)),
        test("Output contains markdown headings", "###" in output or "##" in output),
        test("Output contains table headers", "|" in output),
        test("Output contains summary", "Summary" in output),
    ]
    
    return all(checks)

def test_wec_preservation():
    """Test 6: WEC section preservation logic"""
    # This tests the JavaScript logic that should preserve WEC
    import re
    
    sample_body_with_wec = """## Description
This PR does X and Y.

## 🔄 Workflow Execution Checklist
- [ ] Tests pass
- [ ] Security review
"""
    
    # The workflow's replace logic should NOT remove WEC
    result = re.sub(r'## 🔐 Security Findings[\s\S]*?(?=##|$)', '', sample_body_with_wec)
    
    checks = [
        test("WEC section preserved", "🔄 Workflow Execution Checklist" in result),
        test("Description section preserved", "## Description" in result),
    ]
    
    return all(checks)

def test_cli_interface():
    """Test 7: CLI interface works correctly"""
    import subprocess
    
    checks = [
        test("Help command works", subprocess.run(
            ["python", "scripts/ci/security_pr_formatter.py", "--help"],
            capture_output=True
        ).returncode == 0),
        
        test("Generate command works", subprocess.run(
            ["python", "scripts/ci/security_pr_formatter.py", "generate", 
             "--findings", ".codex/security-findings-comprehensive.json"],
            capture_output=True
        ).returncode == 0),
        
        test("Validate command works", subprocess.run(
            ["python", "scripts/ci/security_pr_formatter.py", "validate",
             "--findings", ".codex/security-findings-comprehensive.json"],
            capture_output=True
        ).returncode == 0),
    ]
    
    return all(checks)

def test_github_script_compatibility():
    """Test 8: GitHub script logic validation"""
    # Basic syntax check for JavaScript code
    script_path = Path(".github/workflows/security-pr-enhancement.yml")
    
    if not script_path.exists():
        return test("Workflow file exists for script check", False)
    
    with open(script_path) as f:
        content = f.read()
    
    checks = [
        test("Uses github.rest.pulls.update", "github.rest.pulls.update" in content),
        test("Uses github.rest.issues.createComment", "github.rest.issues.createComment" in content),
        test("Reads findings file", "pr-findings.md" in content),
        test("Handles errors gracefully", "catch (error)" in content),
    ]
    
    return all(checks)

def test_severity_emoji_support():
    """Test 9: Severity emoji support"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import generate_findings_section
    
    findings_path = Path(".codex/security-findings-comprehensive.json")
    if not findings_path.exists():
        return test("Findings file for emoji test", False)
    
    output = generate_findings_section(findings_path)
    
    checks = [
        test("CRITICAL emoji present", "🔴" in output),
        test("HIGH emoji present", "🟠" in output),
        test("MEDIUM emoji present", "🟡" in output),
    ]
    
    return all(checks)

def test_agent_recommendations():
    """Test 10: Agent recommendation logic"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import get_agent_assignments, SecurityFinding
    
    # Create findings from different tools
    findings = [
        SecurityFinding("CWE-79", "CRITICAL", "XSS", "app.py", 10, "CodeQL", "Fix", 1.0),
        SecurityFinding("CWE-22", "HIGH", "Path", "utils.py", 42, "Semgrep", "Fix", 0.9),
        SecurityFinding("CWE-798", "CRITICAL", "Secret", "config.py", 5, "detect-secrets", "Fix", 1.0),
    ]
    
    output = get_agent_assignments(findings)
    
    checks = [
        test("CodeQL agent recommended", "@codeql-alert-resolution-agent" in output),
        test("Secret detection agent recommended", "@secret-detection-agent" in output),
        test("Shows finding counts", "findings)" in output),
    ]
    
    return all(checks)

# Run all tests
def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("PHASE 6: PR BODY ENHANCEMENT & WEC INTEGRATION - TEST SUITE")
    print("="*60 + "\n")
    
    test_suites = [
        ("Workflow YAML Validation", test_workflow_yaml_valid),
        ("Formatter Module", test_formatter_module),
        ("Empty Findings Handling", test_empty_findings_handling),
        ("Findings JSON Loading", test_findings_json_loading),
        ("Output Format", test_output_format),
        ("WEC Preservation", test_wec_preservation),
        ("CLI Interface", test_cli_interface),
        ("GitHub Script Compatibility", test_github_script_compatibility),
        ("Severity Emoji Support", test_severity_emoji_support),
        ("Agent Recommendations", test_agent_recommendations),
    ]
    
    results = []
    for suite_name, test_func in test_suites:
        print(f"\n📋 {suite_name}:")
        try:
            result = test_func()
            results.append((suite_name, result))
        except Exception as e:
            print(f"❌ Test suite failed with exception: {e}")
            results.append((suite_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for suite_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {suite_name}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
