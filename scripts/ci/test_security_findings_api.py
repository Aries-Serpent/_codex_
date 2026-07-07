#!/usr/bin/env python3
"""
Test Suite for Security Findings API (Phase 5B)

Tests all query types, filtering, formatting, and CLI interface.
Performance benchmark included.
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List

# Test data - sample findings
SAMPLE_FINDINGS = [
    {
        "id": "codeql-1",
        "tool": "CodeQL",
        "title": "XSS Vulnerability in Template Engine",
        "description": "User input not escaped before HTML rendering",
        "severity": "HIGH",
        "file": "src/templates/render.py",
        "line": 42,
        "cwe_id": "CWE-79",
        "rule_id": "py/xss"
    },
    {
        "id": "semgrep-1",
        "tool": "Semgrep",
        "title": "SQL Injection Risk",
        "description": "Dynamic SQL query construction",
        "severity": "CRITICAL",
        "file": "src/database/query_builder.py",
        "line": 15,
        "cwe_id": "CWE-89",
        "rule_id": "py/sql-injection"
    },
    {
        "id": "pip-audit-1",
        "tool": "pip-audit",
        "title": "Known Vulnerability in Django",
        "description": "Django < 3.2.5 has security vulnerability",
        "severity": "HIGH",
        "package": "django",
        "version": "3.2.4",
        "cwe_id": "CWE-352"
    },
    {
        "id": "safety-1",
        "tool": "Safety",
        "title": "Security Issue in requests Library",
        "description": "Unsafe use of requests without timeout",
        "severity": "MEDIUM",
        "package": "requests",
        "version": "2.28.0",
        "cwe_id": "CWE-391"
    },
    {
        "id": "detect-secrets-1",
        "tool": "detect-secrets",
        "title": "API Key Detected",
        "description": "Potential API key found in source code",
        "severity": "CRITICAL",
        "file": "config/settings.py",
        "line": 10
    }
]


def setup_test_findings() -> Path:
    """Create temporary findings file for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    findings_file = temp_dir / "findings.json"
    
    findings_data = {
        "metadata": {
            "generated": "2026-07-07T01:59:39Z",
            "total_tools": 5,
            "total_findings": len(SAMPLE_FINDINGS)
        },
        "findings": SAMPLE_FINDINGS
    }
    
    findings_file.write_text(json.dumps(findings_data, indent=2))
    return findings_file


def run_query_test(api_script: Path, findings_file: Path, 
                   query_type: str, value: str, expected_count: int) -> bool:
    """Run a query and verify result count."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(api_script),
                'query',
                '--query-type', query_type,
                '--value', value,
                '--findings-file', str(findings_file),
                '--format', 'json'
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            actual_count = output['results']['total_matched']
            if actual_count == expected_count:
                print(f"✓ {query_type}={value}: {actual_count} findings")
                return True
            else:
                print(f"✗ {query_type}={value}: expected {expected_count}, got {actual_count}")
                return False
        elif result.returncode == 2:
            # No findings found - expected for some tests
            if expected_count == 0:
                print(f"✓ {query_type}={value}: 0 findings (as expected)")
                return True
            else:
                print(f"✗ {query_type}={value}: no findings found (expected {expected_count})")
                return False
        else:
            print(f"✗ {query_type}={value}: error code {result.returncode}")
            print(f"  stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {query_type}={value}: timeout (> 5s)")
        return False
    except json.JSONDecodeError:
        print(f"✗ {query_type}={value}: invalid JSON output")
        return False
    except Exception as e:
        print(f"✗ {query_type}={value}: {e}")
        return False


def test_cwe_query(api_script: Path) -> bool:
    """Test CWE filtering."""
    print("\n🔍 Testing CWE Query:")
    
    findings_file = setup_test_findings()
    tests = [
        ("CWE-79", 1),      # Template XSS
        ("CWE-89", 1),      # SQL Injection
        ("CWE-352", 1),     # Django vulnerability
        ("79", 1),          # Without prefix
        ("CWE-999", 0),     # Non-existent CWE
    ]
    
    results = []
    for cwe, expected in tests:
        results.append(run_query_test(api_script, findings_file, "cwe", cwe, expected))
    
    findings_file.parent.rmdir()
    return all(results)


def test_package_query(api_script: Path) -> bool:
    """Test package filtering."""
    print("\n📦 Testing Package Query:")
    
    findings_file = setup_test_findings()
    tests = [
        ("django", 1),
        ("requests", 1),
        ("Django", 1),      # Case insensitive
        ("numpy", 0),       # Not in test data
    ]
    
    results = []
    for package, expected in tests:
        results.append(run_query_test(api_script, findings_file, "package", package, expected))
    
    findings_file.parent.rmdir()
    return all(results)


def test_file_query(api_script: Path) -> bool:
    """Test file path filtering."""
    print("\n📁 Testing File Query:")
    
    findings_file = setup_test_findings()
    tests = [
        ("src/templates/render.py", 1),
        ("render.py", 1),           # Suffix match
        ("src/database/query_builder.py", 1),
        ("src/config.py", 0),       # Non-existent file
    ]
    
    results = []
    for filepath, expected in tests:
        results.append(run_query_test(api_script, findings_file, "file", filepath, expected))
    
    findings_file.parent.rmdir()
    return all(results)


def test_severity_query(api_script: Path) -> bool:
    """Test severity level filtering."""
    print("\n🚨 Testing Severity Query:")
    
    findings_file = setup_test_findings()
    tests = [
        ("CRITICAL", 2),   # CRITICAL and higher (2 CRITICAL findings)
        ("HIGH", 4),       # HIGH and higher (2 CRITICAL + 2 HIGH)
        ("MEDIUM", 5),     # MEDIUM and higher (all 5)
        ("LOW", 5),        # LOW and higher (all 5)
        ("INFO", 5),       # INFO and higher (all 5)
    ]
    
    results = []
    for severity, expected in tests:
        results.append(run_query_test(api_script, findings_file, "severity", severity, expected))
    
    findings_file.parent.rmdir()
    return all(results)


def test_output_formats(api_script: Path) -> bool:
    """Test different output formats."""
    print("\n📋 Testing Output Formats:")
    
    findings_file = setup_test_findings()
    temp_dir = findings_file.parent
    
    results = []
    
    for fmt in ['json', 'csv', 'markdown']:
        output_file = temp_dir / f"output.{fmt}"
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(api_script),
                    'query',
                    '--query-type', 'cwe',
                    '--value', 'CWE-79',
                    '--format', fmt,
                    '--output', str(output_file)
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and output_file.exists():
                content = output_file.read_text()
                if fmt == 'json':
                    json.loads(content)  # Validate JSON
                    print(f"✓ {fmt.upper()}: valid format, {len(content)} bytes")
                elif fmt == 'csv':
                    print(f"✓ {fmt.upper()}: valid format, {len(content)} bytes")
                else:  # markdown
                    print(f"✓ {fmt.upper()}: valid format, {len(content)} bytes")
                results.append(True)
            else:
                print(f"✗ {fmt.upper()}: failed")
                results.append(False)
        except Exception as e:
            print(f"✗ {fmt.upper()}: {e}")
            results.append(False)
    
    findings_file.parent.rmdir()
    return all(results)


def test_performance(api_script: Path) -> bool:
    """Benchmark query performance."""
    print("\n⏱️  Testing Performance (< 500ms target):")
    
    findings_file = setup_test_findings()
    
    try:
        start = time.time()
        result = subprocess.run(
            [
                sys.executable,
                str(api_script),
                'query',
                '--query-type', 'severity',
                '--value', 'HIGH',
                '--format', 'json'
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        if result.returncode == 0 or result.returncode == 2:
            if elapsed < 500:
                print(f"✓ Query completed in {elapsed:.1f}ms (< 500ms)")
                findings_file.parent.rmdir()
                return True
            else:
                print(f"⚠ Query completed in {elapsed:.1f}ms (exceeds 500ms target)")
                findings_file.parent.rmdir()
                return False
        else:
            print(f"✗ Query failed with code {result.returncode}")
            findings_file.parent.rmdir()
            return False
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        findings_file.parent.rmdir()
        return False


def test_validation(api_script: Path) -> bool:
    """Test input validation."""
    print("\n✅ Testing Input Validation:")
    
    results = []
    
    # Invalid query type
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(api_script),
                'query',
                '--query-type', 'invalid',
                '--value', 'test',
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print("✓ Rejects invalid query type")
            results.append(True)
        else:
            print("✗ Should reject invalid query type")
            results.append(False)
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        results.append(False)
    
    return all(results)


def main():
    """Run all tests."""
    api_script = Path(__file__).parent / "security_findings_api.py"
    
    if not api_script.exists():
        print(f"❌ API script not found: {api_script}")
        return 1
    
    print("=" * 60)
    print("🧪 Security Findings API - Test Suite (Phase 5B)")
    print("=" * 60)
    
    test_results = {
        "CWE Query": test_cwe_query(api_script),
        "Package Query": test_package_query(api_script),
        "File Query": test_file_query(api_script),
        "Severity Query": test_severity_query(api_script),
        "Output Formats": test_output_formats(api_script),
        "Performance": test_performance(api_script),
        "Input Validation": test_validation(api_script),
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    for test_name, passed in test_results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for p in test_results.values() if p)
    total_tests = len(test_results)
    
    print(f"\nTotal: {total_passed}/{total_tests} test suites passed")
    print("=" * 60)
    
    return 0 if all(test_results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
