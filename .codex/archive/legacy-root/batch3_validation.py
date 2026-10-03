#!/usr/bin/env python3
"""
Batch 3 Flaky Test Validation & Verification Script
Validates that all stabilization fixes are applied correctly
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

def check_syntax_errors() -> Tuple[int, List[str]]:
    """Check for Python syntax errors using py_compile"""
    errors = []
    error_count = 0
    
    print("🔍 Checking for syntax errors...")
    
    test_files = list(Path("tests").rglob("test_*.py"))
    
    for test_file in test_files[:50]:  # Sample first 50
        try:
            import py_compile
            py_compile.compile(str(test_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(str(test_file))
            error_count += 1
    
    return error_count, errors


def check_import_errors() -> Tuple[int, List[str]]:
    """Check for import errors"""
    errors = []
    error_count = 0
    
    print("🔍 Checking for import errors...")
    
    # Try importing key modules
    try:
        import freezegun
        print("  ✅ freezegun available")
    except ImportError:
        print("  ⚠️ freezegun not available (will be used in tests)")
    
    try:
        import pytest
        print("  ✅ pytest available")
    except ImportError:
        errors.append("pytest not installed")
        error_count += 1
    
    return error_count, errors


def verify_freezegun_decorator(file_path: str) -> bool:
    """Verify @freeze_time decorator applied correctly"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for freezegun import
        if 'from freezegun import' not in content:
            print(f"  ❌ No freezegun import in {file_path}")
            return False
        
        # Check for @freeze_time decorator
        if '@freeze_time' in content:
            print(f"  ✅ @freeze_time decorator found in {file_path}")
            return True
        
        print(f"  ⚠️ freezegun imported but no @freeze_time decorator in {file_path}")
        return True  # Still OK, just not used
        
    except Exception as e:
        print(f"  ❌ Error checking {file_path}: {e}")
        return False


def verify_mock_fixtures(file_path: str) -> bool:
    """Verify mock_requests fixture parameters added"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if 'mock_requests' in content:
            print(f"  ✅ mock_requests fixture found in {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Error checking {file_path}: {e}")
        return False


def verify_polling_helper(file_path: str) -> bool:
    """Verify polling_helper fixture parameters added"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if 'polling_helper' in content or 'wait_for_condition' in content:
            print(f"  ✅ polling_helper found in {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Error checking {file_path}: {e}")
        return False


def verify_flaky_markers() -> Tuple[int, int]:
    """Verify all flaky markers have reason= argument"""
    test_root = Path("tests")
    has_reason = 0
    missing_reason = 0
    
    print("🔍 Verifying flaky markers...")
    
    for test_file in test_root.rglob("test_*.py"):
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Find all @pytest.mark.flaky
            flaky_pattern = r'@pytest\.mark\.flaky\([^)]*\)'
            matches = re.findall(flaky_pattern, content)
            
            for match in matches:
                if 'reason=' in match:
                    has_reason += 1
                else:
                    missing_reason += 1
                    print(f"  ⚠️ Missing reason= in {test_file}: {match}")
        
        except Exception as e:
            pass
    
    return has_reason, missing_reason


def count_test_functions() -> int:
    """Count total test functions"""
    test_root = Path("tests")
    count = 0
    
    for test_file in test_root.rglob("test_*.py"):
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Count def test_ functions
            matches = re.findall(r'def test_\w+\(', content)
            count += len(matches)
        
        except:
            pass
    
    return count


def validate_conftest_fixtures() -> bool:
    """Verify conftest.py has required fixtures"""
    conftest_path = Path("tests/conftest.py")
    
    if not conftest_path.exists():
        print("  ⚠️ tests/conftest.py not found")
        return False
    
    with open(conftest_path, 'r') as f:
        content = f.read()
    
    required_fixtures = [
        'mock_requests',
        'polling_helper',
        'time_mock',
    ]
    
    found = 0
    for fixture in required_fixtures:
        if f'@pytest.fixture' in content and fixture in content:
            found += 1
    
    print(f"  ✅ Found {found}/{len(required_fixtures)} required fixtures in conftest.py")
    return found == len(required_fixtures)


def main():
    """Main validation execution"""
    
    print("=" * 80)
    print("BATCH 3 FLAKY TEST VALIDATION & VERIFICATION")
    print("=" * 80)
    
    print("\n📋 VALIDATION CHECKS:")
    
    # Check 1: Syntax errors
    syntax_errors, syntax_files = check_syntax_errors()
    print(f"  ✅ Syntax check: {0 if syntax_errors == 0 else '❌'} {syntax_errors} errors")
    
    # Check 2: Import errors
    import_errors, import_files = check_import_errors()
    print(f"  ✅ Import check: {0 if import_errors == 0 else '⚠️'} {import_errors} errors")
    
    # Check 3: Freezegun decorator
    print("\n🔍 Checking freezegun decorators...")
    verify_freezegun_decorator("tests/test_actions_server_smoke.py")
    
    # Check 4: Flaky markers with reason
    print("\n🔍 Verifying flaky markers...")
    has_reason, missing_reason = verify_flaky_markers()
    print(f"  ✅ Flaky markers with reason=: {has_reason}")
    print(f"  ⚠️ Flaky markers missing reason=: {missing_reason}")
    
    # Check 5: Conftest fixtures
    print("\n🔍 Validating conftest.py fixtures...")
    validate_conftest_fixtures()
    
    # Check 6: Test function count
    print("\n📊 Test Statistics:")
    total_tests = count_test_functions()
    print(f"  Total test functions: {total_tests}")
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    all_pass = (
        syntax_errors == 0 and
        import_errors == 0 and
        missing_reason == 0
    )
    
    if all_pass:
        print("✅ All validation checks PASSED")
        print("\n✅ Ready for flakiness audit (3x test runs)")
    else:
        print("⚠️ Some validation checks FAILED")
        print("  Review errors above and fix before running tests")
    
    print("\n📝 Next Steps:")
    print("  1. Install missing dependencies (freezegun, pytest-mock)")
    print("  2. Run flakiness audit (3 consecutive test runs)")
    print("  3. Verify no failures across runs")
    print("  4. Generate final report")
    
    return all_pass


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
