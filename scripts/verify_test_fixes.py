#!/usr/bin/env python3
"""
Self-healing test verification script.
Runs specific tests that were fixed and validates they pass.
Provides detailed diagnostics if failures persist.
"""
import subprocess
import sys


def run_test(test_path: str) -> tuple[bool, str]:
    """
    Run a specific test and capture result.

    Returns:
        (passed: bool, output: str)
    """
    cmd = [
        sys.executable, '-m', 'pytest',
        test_path,
        '-v',
        '--tb=short',
        '--no-header',
        '--no-summary',
        '-q'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return passed, output
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 60 seconds"
    except Exception as e:
        return False, f"Failed to run test: {e}"


def verify_scheduler_fixes() -> dict[str, bool]:
    """Verify scheduler registry tests pass."""
    print("\n🔍 Verifying Scheduler Registry Fixes...")

    tests = {
        "test_registry_lists_builtins": "tests/space_traversal/test_peft_comprehensive/test_scheduler_registry.py::test_registry_lists_builtins",
        "test_build_step_lr_and_step_once": "tests/space_traversal/test_peft_comprehensive/test_scheduler_registry.py::test_build_step_lr_and_step_once",
        "test_build_cosine_annealing_progression": "tests/space_traversal/test_peft_comprehensive/test_scheduler_registry.py::test_build_cosine_annealing_progression",
    }

    results = {}
    for name, path in tests.items():
        passed, output = run_test(path)
        results[name] = passed

        if passed:
            print(f"  ✅ {name} PASSED")
        else:
            print(f"  ❌ {name} FAILED")
            print(f"     Output: {output[:200]}")

    return results


def verify_security_fixes() -> dict[str, bool]:
    """Verify security validation tests pass."""
    print("\n🔍 Verifying Security Validation Fixes...")

    tests = {
        "test_xss_javascript_protocol": "tests/production/test_security_validation.py::test_xss_javascript_protocol",
        "test_input_sanitization_integer": "tests/production/test_security_validation.py::test_input_sanitization_integer",
        "test_xss_event_handler_injection": "tests/production/test_security_validation.py::test_xss_event_handler_injection",
        "test_xss_attribute_injection": "tests/production/test_security_validation.py::test_xss_attribute_injection",
        "test_input_sanitization_email": "tests/production/test_security_validation.py::test_input_sanitization_email",
    }

    results = {}
    for name, path in tests.items():
        passed, output = run_test(path)
        results[name] = passed

        if passed:
            print(f"  ✅ {name} PASSED")
        else:
            print(f"  ❌ {name} FAILED")
            print(f"     Output: {output[:200]}")

    return results


def check_imports() -> bool:
    """Verify sanitization module can be imported."""
    print("\n🔍 Verifying Module Imports...")

    try:
        import importlib.util
        spec = importlib.util.find_spec("codex.security.sanitization")
        if spec is None:
            raise ImportError("codex.security.sanitization module not found")
        print("  ✅ Sanitization module imports successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Failed to import sanitization module: {e}")
        return False


def run_quick_smoke_tests() -> bool:
    """Run quick inline smoke tests."""
    print("\n🔍 Running Quick Smoke Tests...")

    try:
        from codex.security.sanitization import sanitize_html, sanitize_integer

        # Test XSS sanitization
        xss_input = '<a href="javascript:alert(1)">Click</a>'
        sanitized = sanitize_html(xss_input)
        assert 'javascript:' not in sanitized, f"XSS not removed: {sanitized}"
        print("  ✅ XSS javascript: protocol removed")

        # Test event handler sanitization
        xss_input2 = '<img src="x" onerror="alert(1)">'
        sanitized2 = sanitize_html(xss_input2)
        assert 'onerror=' not in sanitized2, f"Event handler not removed: {sanitized2}"
        print("  ✅ XSS event handler removed")

        # Test integer sanitization
        result = sanitize_integer('42.7')
        assert result == 42, f"Expected 42, got {result}"
        print("  ✅ Integer sanitization handles floats")

        return True

    except Exception as e:
        print(f"  ❌ Smoke test failed: {e}")
        return False


def main():
    """Main verification workflow."""
    print("=" * 60)
    print("🔧 Self-Healing Test Verification")
    print("=" * 60)

    # Step 1: Check imports
    if not check_imports():
        print("\n❌ VERIFICATION FAILED: Cannot import required modules")
        sys.exit(1)

    # Step 2: Run smoke tests
    if not run_quick_smoke_tests():
        print("\n❌ VERIFICATION FAILED: Smoke tests failed")
        sys.exit(1)

    # Step 3: Run actual tests
    scheduler_results = verify_scheduler_fixes()
    security_results = verify_security_fixes()

    # Step 4: Analyze results
    all_results = {**scheduler_results, **security_results}
    passed = sum(1 for v in all_results.values() if v)
    failed = len(all_results) - passed

    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{len(all_results)} tests passed")
    print("=" * 60)

    if failed > 0:
        print(f"\n❌ VERIFICATION FAILED: {failed} test(s) still failing")
        print("\nFailing tests:")
        for name, result in all_results.items():
            if not result:
                print(f"  - {name}")
        sys.exit(1)
    else:
        print("\n✅ VERIFICATION PASSED: All fixes validated")
        sys.exit(0)


if __name__ == '__main__':
    main()
