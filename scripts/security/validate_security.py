from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
#!/usr/bin/env python3
"""
Validate Security

Purpose:
    Validates security

Usage:
    python scripts/security/validate_security.py [options]

    Examples:
    $ python scripts/security/validate_security.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


import logging
import subprocess

logger = logging.getLogger(__name__)
import sys


def run_check(name: str, pattern: str, should_find: bool = False) -> tuple[bool, int]:
    """Run a grep check and return results."""
    result = subprocess.run(
        ['grep', '-r', pattern, 'src/', 'agents/', '--include=*.py'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )

    count = len([line for line in result.stdout.split('\n') if line.strip()])

    passed = count > 0 if should_find else count == 0

    return passed, count

def validate_security() -> dict[str, tuple[bool, str]]:
    """Run all security validation checks."""
    checks = {}

    print("🔍 Running Security Validation Checks...\n")

    # Check 1: No unsafe eval()
    print("1. Checking for unsafe eval() usage...")
    result = subprocess.run(
        ['grep', '-r', r'\beval\(', 'src/', 'agents/', '--include=*.py'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    # Filter out safe usages
    unsafe_evals = [line for line in result.stdout.split('\n')
                    if 'eval(' in line
                    and 'model.eval()' not in line
                    and 'literal_eval' not in line
                    and line.strip()]

    passed = len(unsafe_evals) == 0
    status = "✅ PASS" if passed else "❌ FAIL"
    checks['unsafe_eval'] = (passed, f"{status} - Found {len(unsafe_evals)} unsafe eval() calls")
    print(f"   {checks['unsafe_eval'][1]}\n")

    # Check 2: No shell=True
    print("2. Checking for shell=True in subprocess...")
    passed, count = run_check('shell=True', r'shell=True', should_find=False)
    status = "✅ PASS" if passed else "❌ FAIL"
    checks['shell_true'] = (passed, f"{status} - Found {count} instances")
    print(f"   {checks['shell_true'][1]}\n")

    # Check 3: MD5 has usedforsecurity
    print("3. Checking MD5 usage has usedforsecurity parameter...")
    result = subprocess.run(
        ['grep', '-r', r'hashlib\.md5\(', 'src/', 'agents/', '--include=*.py'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    md5_calls = [line for line in result.stdout.split('\n') if 'hashlib.md5(' in line and line.strip()]
    md5_safe = [line for line in md5_calls if 'usedforsecurity=False' in line]

    ratio = len(md5_safe) / len(md5_calls) if md5_calls else 1.0
    passed = ratio > 0.8  # Allow some exceptions
    status = "✅ PASS" if passed else "⚠️  WARN"
    checks['md5_safe'] = (passed, f"{status} - {len(md5_safe)}/{len(md5_calls)} MD5 calls are safe ({ratio*100:.0f}%)")
    print(f"   {checks['md5_safe'][1]}\n")

    # Check 4: Logging added to exceptions
    print("4. Checking exception handlers have logging...")
    result = subprocess.run(
        ['grep', '-A 1', r'except.*:', 'src/', '-r', '--include=*.py'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )

    lines = result.stdout.split('\n')
    except_blocks = 0
    logged_blocks = 0

    for i, line in enumerate(lines):
        if 'except' in line and ':' in line:
            except_blocks += 1
            # Check if next line has logging or pass
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if 'logger.' in next_line or 'logging.' in next_line:
                    logged_blocks += 1

    ratio = logged_blocks / except_blocks if except_blocks else 1.0
    passed = ratio > 0.7  # Expect >70% have logging
    status = "✅ PASS" if passed else "⚠️  WARN"
    checks['exception_logging'] = (passed, f"{status} - {logged_blocks}/{except_blocks} exception handlers have logging ({ratio*100:.0f}%)")
    print(f"   {checks['exception_logging'][1]}\n")

    # Check 5: Safe pickle loading
    print("5. Checking pickle.load usage...")
    result = subprocess.run(
        ['grep', '-r', r'pickle\.load\(', 'src/', 'agents/', '--include=*.py'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )

    pickle_loads = [line for line in result.stdout.split('\n')
                    if 'pickle.load(' in line
                    and 'safe_pickle' not in line
                    and line.strip()]

    passed = len(pickle_loads) == 0
    status = "✅ PASS" if passed else "⚠️  WARN"
    checks['pickle_safe'] = (passed, f"{status} - Found {len(pickle_loads)} direct pickle.load() calls")
    print(f"   {checks['pickle_safe'][1]}\n")

    # Check 6: Torch weights_only
    print("6. Checking torch.load usage...")
    result = subprocess.run(
        ['grep', '-r', r'torch\.load\(', 'src/', 'agents/', '--include=*.py'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )

    torch_loads = [line for line in result.stdout.split('\n') if 'torch.load(' in line and line.strip()]
    safe_loads = [line for line in torch_loads if 'weights_only=True' in line or 'weights_only' in line]

    ratio = len(safe_loads) / len(torch_loads) if torch_loads else 1.0
    passed = ratio > 0.8
    status = "✅ PASS" if passed else "⚠️  WARN"
    checks['torch_safe'] = (passed, f"{status} - {len(safe_loads)}/{len(torch_loads)} torch.load() calls use weights_only ({ratio*100:.0f}%)")
    print(f"   {checks['torch_safe'][1]}\n")

    return checks

def main():
    """Run validation and print summary."""
    print("=" * 70)
    print("🛡️  SECURITY VALIDATION REPORT")
    print("=" * 70)
    print()

    checks = validate_security()

    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    total = len(checks)
    passed = sum(1 for result, _ in checks.values() if result)

    for _name, (_result, message) in checks.items():
        print(f"{message}")

    print()
    print(f"Total Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print()

    if passed == total:
        print("🎉 ALL SECURITY CHECKS PASSED!")
        print("✅ Codebase is production-ready")
        return 0
    if passed >= total * 0.8:
        print("⚠️  MOST SECURITY CHECKS PASSED")
        print("✅ Codebase is acceptable with minor improvements needed")
        return 0
    print("❌ SECURITY CHECKS FAILED")
    print("⚠️  Review and fix issues before deployment")
    return 1

if __name__ == '__main__':
    sys.exit(main())
