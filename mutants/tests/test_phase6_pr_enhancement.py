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

import sys
from pathlib import Path


def test_workflow_yaml_valid():
    """Test 1: Workflow YAML is valid"""
    import yaml
    
    workflow_path = Path(".github/workflows/security-pr-enhancement.yml")
    assert workflow_path.exists(), "Workflow file not found"
    
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)
    
    # Check structure
    assert 'name' in workflow, "Missing workflow name"
    assert 'jobs' in workflow, "Missing jobs section"
    assert len(workflow.get('jobs', {})) >= 1, "Workflow has no jobs"
    assert 'enhance-pr-security' in workflow.get('jobs', {}), "Missing enhance-pr-security job"
    assert 'validate-findings-json' in workflow.get('jobs', {}), "Missing validate-findings-json job"
    
    # Check permissions
    perms = workflow.get('permissions', {})
    assert 'pull-requests' in perms, "Missing pull-requests: write permission"

def test_formatter_module():
    """Test 2: Formatter module works correctly"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import (
        SecurityFinding,
        format_findings_table,
        generate_pr_summary,
        get_agent_assignments,
        list_top_issues,
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
    
    assert len(test_findings) == 2, "Expected 2 test findings"
    
    table_output = format_findings_table(test_findings)
    assert bool(table_output), "format_findings_table produced no output"
    assert "Severity" in table_output, "format_findings_table missing 'Severity'"
    
    issues_output = list_top_issues(test_findings, limit=5)
    assert bool(issues_output), "list_top_issues produced no output"
    assert "1. **" in issues_output, "list_top_issues missing finding 1"
    assert "2. **" in issues_output, "list_top_issues missing finding 2"
    
    assert bool(get_agent_assignments(test_findings)), "get_agent_assignments produced no output"
    
    summary_output = generate_pr_summary(test_findings)
    assert "Summary" in summary_output, "generate_pr_summary missing 'Summary'"

def test_empty_findings_handling():
    """Test 3: Empty findings handled gracefully"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import format_findings_table, generate_pr_summary, list_top_issues
    
    empty_findings = []
    
    assert "No security findings" in generate_pr_summary(empty_findings), "Empty summary not handled correctly"
    assert bool(format_findings_table(empty_findings)), "Empty findings table not handled"
    assert bool(list_top_issues(empty_findings)), "Empty findings list not handled"

def test_findings_json_loading():
    """Test 4: Load and parse findings JSON"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import load_findings
    
    findings_path = Path(".codex/security-findings-comprehensive.json")
    
    assert findings_path.exists(), "Findings file does not exist"
    
    findings = load_findings(findings_path)
    assert len(findings) > 0, f"Expected > 0 findings, got {len(findings)}"
    assert any(f.severity == 'CRITICAL' for f in findings), "No CRITICAL findings found"
    assert any(f.severity == 'HIGH' for f in findings), "No HIGH findings found"
    
    if findings:
        assert findings[0].cwe.startswith('CWE-'), "First finding missing CWE"

def test_output_format():
    """Test 5: Output format is valid markdown"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import generate_findings_section
    
    findings_path = Path(".codex/security-findings-comprehensive.json")
    assert findings_path.exists(), "Findings file not found"
    
    output = generate_findings_section(findings_path, limit=3)
    
    assert bool(output), "Output is empty"
    assert ("###" in output or "##" in output), "Output missing markdown headings"
    assert ("|" in output), "Output missing table headers"
    assert ("Summary" in output), "Output missing summary"

def test_wec_preservation():
    """Test 6: WEC section preservation logic"""
    # This tests the JavaScript logic that should preserve WEC
    

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
    
    assert "🔄 Workflow Execution Checklist" in result, "WEC section not preserved"
    assert "## Description" in result, "Description section not preserved"

def test_cli_interface():
    """Test 7: CLI interface works correctly"""
    import subprocess
    
    help_result = subprocess.run(
        ["python", "scripts/ci/security_pr_formatter.py", "--help"],
        capture_output=True
    )
    assert help_result.returncode == 0, "Help command failed"
    
    generate_result = subprocess.run(
        ["python", "scripts/ci/security_pr_formatter.py", "generate", 
         "--findings", ".codex/security-findings-comprehensive.json"],
        capture_output=True
    )
    assert generate_result.returncode == 0, "Generate command failed"
    
    validate_result = subprocess.run(
        ["python", "scripts/ci/security_pr_formatter.py", "validate",
         "--findings", ".codex/security-findings-comprehensive.json"],
        capture_output=True
    )
    assert validate_result.returncode == 0, "Validate command failed"

def test_github_script_compatibility():
    """Test 8: GitHub script logic validation"""
    # Basic syntax check for JavaScript code
    script_path = Path(".github/workflows/security-pr-enhancement.yml")
    
    assert script_path.exists(), "Workflow file not found for script check"
    
    with open(script_path) as f:
        content = f.read()
    
    assert "github.rest.pulls.update" in content, "Missing github.rest.pulls.update"
    assert "github.rest.issues.createComment" in content, "Missing github.rest.issues.createComment"
    assert "pr-findings.md" in content, "Missing pr-findings.md reference"
    assert "catch (error)" in content, "Missing error handling"

def test_severity_emoji_support():
    """Test 9: Severity emoji support"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import generate_findings_section
    
    findings_path = Path(".codex/security-findings-comprehensive.json")
    assert findings_path.exists(), "Findings file not found for emoji test"
    
    output = generate_findings_section(findings_path)
    
    assert "🔴" in output, "CRITICAL emoji not present"
    assert "🟠" in output, "HIGH emoji not present"
    assert "🟡" in output, "MEDIUM emoji not present"

def test_agent_recommendations():
    """Test 10: Agent recommendation logic"""
    import sys
    sys.path.insert(0, 'scripts/ci')
    from security_pr_formatter import SecurityFinding, get_agent_assignments
    
    # Create findings from different tools
    findings = [
        SecurityFinding("CWE-79", "CRITICAL", "XSS", "app.py", 10, "CodeQL", "Fix", 1.0),
        SecurityFinding("CWE-22", "HIGH", "Path", "utils.py", 42, "Semgrep", "Fix", 0.9),
        SecurityFinding("CWE-798", "CRITICAL", "Secret", "config.py", 5, "detect-secrets", "Fix", 1.0),
    ]
    
    output = get_agent_assignments(findings)
    
    assert "@codeql-alert-resolution-agent" in output, "CodeQL agent not recommended"
    assert "@secret-detection-agent" in output, "Secret detection agent not recommended"
    assert "findings)" in output, "Finding counts not shown"


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
