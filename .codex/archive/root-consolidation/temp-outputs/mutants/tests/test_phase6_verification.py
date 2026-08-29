#!/usr/bin/env python3
"""
Phase 6 Direct Testing - Verification of deliverables

Tests:
1. Workflow YAML validity
2. Formatter CLI functionality
3. Output format validation
4. Edge cases handling
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


def run_test(name: str, condition: bool, details: str = "") -> bool:
    """Print test result."""
    status = "✅" if condition else "❌"
    print(f"{status} {name}")
    if details and not condition:
        print(f"   └─ {details}")
    return condition

def main():
    print("\n" + "="*70)
    print("PHASE 6 DELIVERABLE VERIFICATION")
    print("="*70 + "\n")
    
    all_passed = True
    
    # Test 1: Workflow file exists and is valid YAML
    print("📋 Test Suite 1: Workflow Validation")
    workflow_path = Path(".github/workflows/security-pr-enhancement.yml")
    all_passed &= run_test(
        "Workflow file exists",
        workflow_path.exists(),
        f"File not found: {workflow_path}"
    )
    
    if workflow_path.exists():
        try:
            with open(workflow_path) as f:
                workflow = yaml.safe_load(f)
            
            all_passed &= run_test(
                "Workflow YAML is valid",
                isinstance(workflow, dict),
                "Failed to parse YAML"
            )
            
            all_passed &= run_test(
                "Workflow has name",
                workflow.get('name') == 'Security PR Enhancement',
                f"Unexpected name: {workflow.get('name')}"
            )
            
            jobs = workflow.get('jobs', {})
            all_passed &= run_test(
                "Has 'enhance-pr-security' job",
                'enhance-pr-security' in jobs,
                "Job not found in workflow"
            )
            
            all_passed &= run_test(
                "Has 'validate-findings-json' job",
                'validate-findings-json' in jobs,
                "Job not found in workflow"
            )
            
            steps = jobs.get('enhance-pr-security', {}).get('steps', [])
            all_passed &= run_test(
                "Has Python setup step",
                any('setup-python' in str(step).lower() for step in steps),
                "Python setup not found"
            )
            
            all_passed &= run_test(
                "Has findings generation step",
                any('findings' in str(step).lower() for step in steps),
                "Findings generation not found"
            )
            
        except yaml.YAMLError as e:
            all_passed &= run_test("Parse workflow YAML", False, str(e))
    
    # Test 2: Formatter module existence and basic functionality
    print("\n📋 Test Suite 2: Formatter Module")
    formatter_path = Path("scripts/ci/security_pr_formatter.py")
    all_passed &= run_test(
        "Formatter script exists",
        formatter_path.exists(),
        f"File not found: {formatter_path}"
    )
    
    if formatter_path.exists():
        # Test help
        result = subprocess.run(
            ["python", str(formatter_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        all_passed &= run_test(
            "Formatter --help works",
            result.returncode == 0,
            f"Exit code: {result.returncode}"
        )
        
        # Test generate command
        result = subprocess.run(
            ["python", str(formatter_path), "generate", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        all_passed &= run_test(
            "Formatter generate subcommand exists",
            result.returncode == 0,
            f"Exit code: {result.returncode}"
        )
    
    # Test 3: Findings JSON file
    print("\n📋 Test Suite 3: Findings JSON")
    findings_path = Path(".codex/security-findings-comprehensive.json")
    all_passed &= run_test(
        "Findings JSON exists",
        findings_path.exists(),
        f"File not found: {findings_path}"
    )
    
    if findings_path.exists():
        try:
            with open(findings_path) as f:
                data = json.load(f)
            
            all_passed &= run_test(
                "Findings JSON is valid",
                isinstance(data, dict),
                "Invalid JSON structure"
            )
            
            all_passed &= run_test(
                "Has 'findings' key",
                'findings' in data,
                "Missing 'findings' key"
            )
            
            all_passed &= run_test(
                "Has 'metadata' key",
                'metadata' in data,
                "Missing 'metadata' key"
            )
            
            findings = data.get('findings', [])
            all_passed &= run_test(
                "Has test findings",
                len(findings) > 0,
                f"Expected > 0 findings, got {len(findings)}"
            )
            
            if findings:
                first = findings[0]
                required_keys = ['cwe', 'severity', 'description', 'file_path', 'tool', 'fix_recommendation']
                all_passed &= run_test(
                    "Finding has required keys",
                    all(k in first for k in required_keys),
                    f"Missing keys: {[k for k in required_keys if k not in first]}"
                )
                
                all_passed &= run_test(
                    "Finding severity is valid",
                    first.get('severity') in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'],
                    f"Invalid severity: {first.get('severity')}"
                )
        
        except json.JSONDecodeError as e:
            all_passed &= run_test("Parse findings JSON", False, str(e))
    
    # Test 4: Formatter execution
    print("\n📋 Test Suite 4: Formatter Execution")
    if formatter_path.exists() and findings_path.exists():
        result = subprocess.run(
            ["python", str(formatter_path), "generate",
             "--findings", str(findings_path),
             "--limit", "3"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        all_passed &= run_test(
            "Formatter generates output",
            result.returncode == 0 and len(result.stdout) > 0,
            f"Exit: {result.returncode}, Output length: {len(result.stdout)}"
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            all_passed &= run_test(
                "Output contains summary",
                "Summary" in output,
                "Missing summary section"
            )
            
            all_passed &= run_test(
                "Output contains severity distribution",
                "Severity Distribution" in output or "Severity" in output,
                "Missing severity distribution"
            )
            
            all_passed &= run_test(
                "Output contains severity emojis",
                any(emoji in output for emoji in ['🔴', '🟠', '🟡', '🟢', '🔵']),
                "Missing severity emojis"
            )
            
            all_passed &= run_test(
                "Output contains agent recommendations",
                "@" in output,  # Agent mentions with @
                "Missing agent recommendations"
            )
    
    # Test 5: Output to file
    print("\n📋 Test Suite 5: File Output")
    if formatter_path.exists() and findings_path.exists():
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as tmp:
            output_path = Path(tmp.name)
        try:
            result = subprocess.run(
                ["python", str(formatter_path), "generate",
                 "--findings", str(findings_path),
                 "--output", str(output_path),
                 "--limit", "2"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            all_passed &= run_test(
                "Formatter creates output file",
                result.returncode == 0 and output_path.exists(),
                f"Exit: {result.returncode}, File exists: {output_path.exists()}"
            )
            
            if output_path.exists():
                with open(output_path) as f:
                    content = f.read()
                
                all_passed &= run_test(
                    "Output file has content",
                    len(content) > 100,
                    f"File too small: {len(content)} bytes"
                )
                
                all_passed &= run_test(
                    "Output file is markdown",
                    "##" in content or "|" in content,
                    "Not valid markdown"
                )
        finally:
            # Clean up tempfile
            if output_path.exists():
                output_path.unlink()
    
    # Summary
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Phase 6 deliverables are valid")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Review issues above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
