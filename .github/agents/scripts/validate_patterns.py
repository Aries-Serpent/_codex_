"""
Pattern Validation Tool

Validates secret detection patterns against known test cases
and suggests improvements for failing patterns.
"""

import sys
from pathlib import Path

# Add agents directory to path
AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from codex_reviewer.secret_patterns import SecretPatterns  # noqa: E402


class PatternValidator:
    """Validate secret detection patterns against test cases."""

    def __init__(self):
        """Initialize with comprehensive test cases."""
        self.test_cases = {
            "api_key": [
                ('API_KEY="sk_test_1234567890abcdefghij"', True, "Standard format"),
                ('apiKey: "abc123xyz789def456ghi"', True, "JSON format"),
                ('api-key = my_secret_key_12345678', True, "Hyphenated"),
                ('{"api_key": "1234567890abcdef1234"}', True, "JSON embedded"),
                ('regular text without keys', False, "No secret"),
                ('API_KEY=YOUR_API_KEY_HERE', False, "Placeholder"),
            ],
            "api_key_variants": [
                ('API_KEY = "sk_live_123456"', True, "Uppercase with spaces"),
                ('export API_KEY="test_key"', True, "Export statement"),
            ],
            "aws_access_key": [
                ('AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"', True, "Standard format"),
                ('aws_access_key_id="AKIAI44QH8DHBEXAMPLE"', True, "Lowercase"),
                ('not an aws key', False, "No secret"),
            ],
            "aws_secret_key": [
                ('AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"', True, "Standard"),
                ('aws_secret_access_key="1234567890abcdefghijklmnopqrstuvwxyz1234"', True, "Lowercase"),
            ],
            "github_token": [
                ('ghp_1234567890abcdefghijklmnopqrstuv', True, "Personal token"),
                ('gho_1234567890abcdefghijklmnopqrstuv', True, "OAuth token"),
                ('ghs_1234567890abcdefghijklmnopqrstuv', True, "Server token"),
                ('github_token = "ghp_abcdef123456"', False, "Too short"),
            ],
            "github_token_classic": [
                ('GITHUB_TOKEN="ghp_1234567890abcdefghijklmnopqrstuv1234"', True, "Classic format"),
                ('gh_token: github_pat_11AAAAAAA0123456789_abcdefghijklmnopqrstuvwxyz123', True, "PAT format"),
            ],
            "private_key": [
                ('-----BEGIN PRIVATE KEY-----', True, "Standard PEM"),
                ('-----BEGIN RSA PRIVATE KEY-----', True, "RSA PEM"),
                ('-----BEGIN EC PRIVATE KEY-----', True, "EC PEM"),
                ('not a private key', False, "No key"),
            ],
        }

    def validate_all_patterns(self) -> dict[str, list[tuple[str, bool, bool, str]]]:
        """
        Test all patterns against test cases.

        Returns:
            Dict mapping pattern names to test results:
            (test_string, expected, actual, description)
        """
        patterns = SecretPatterns.get_compiled_patterns()
        results = {}

        for pattern_name, test_cases in self.test_cases.items():
            if pattern_name not in patterns:
                print(f"⚠️  Pattern '{pattern_name}' not found in SecretPatterns")
                continue

            pattern = patterns[pattern_name]
            results[pattern_name] = []

            for test_string, expected, description in test_cases:
                match = bool(pattern.search(test_string))
                results[pattern_name].append((test_string, expected, match, description))

                if match != expected:
                    status = "❌"
                    print(f"{status} Pattern '{pattern_name}' failed on: {description}")
                    print(f"   Test: {test_string}")
                    print(f"   Expected: {expected}, Got: {match}")
                else:
                    print(f"✅ Pattern '{pattern_name}' passed: {description}")

        return results

    def generate_report(self, results: dict[str, list[tuple[str, bool, bool, str]]]) -> None:
        """Generate summary report of validation results."""
        print("\n" + "=" * 70)
        print("📊 PATTERN VALIDATION SUMMARY")
        print("=" * 70)

        total_patterns = len(results)
        total_tests = sum(len(tests) for tests in results.values())
        total_passed = sum(
            sum(1 for _, expected, actual, _ in tests if expected == actual)
            for tests in results.values()
        )

        print(f"\nPatterns Tested: {total_patterns}")
        print(f"Total Test Cases: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_tests - total_passed}")
        print(f"Success Rate: {(total_passed / total_tests * 100):.1f}%")

        print("\n" + "-" * 70)
        print("PER-PATTERN RESULTS")
        print("-" * 70)

        for pattern_name, tests in results.items():
            passed = sum(1 for _, expected, actual, _ in tests if expected == actual)
            total = len(tests)
            status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"

            print(f"\n{status} {pattern_name}: {passed}/{total} passed")

            # Show failing tests
            failed_tests = [
                (test_str, expected, actual, desc)
                for test_str, expected, actual, desc in tests
                if expected != actual
            ]

            if failed_tests:
                print("   Failed tests:")
                for test_str, expected, actual, desc in failed_tests:
                    print(f"   - {desc}: expected={expected}, got={actual}")
                    print(f"     Test: {test_str[:60]}...")

    def suggest_pattern_fixes(self, results: dict[str, list[tuple]]) -> None:
        """Suggest improvements for failing patterns."""
        print("\n" + "=" * 70)
        print("💡 SUGGESTED PATTERN FIXES")
        print("=" * 70)

        fixes = {
            "api_key": r'(?i)(?:api[_\-]?key|apikey)["\']?\s*[:=]\s*["\']?([A-Za-z0-9+/=_\-]{16,})["\']?',
            "aws_secret_key": r'(?i)aws[_\-]?secret[_\-]?(?:access[_\-]?)?key\s*[:=]\s*["\']?([A-Za-z0-9+/=]{40})["\']?',
            "github_token_classic": r'(?i)(?:github[_\-]?token|gh[_\-]?token)\s*[:=]\s*["\']?(ghp_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{36,})["\']?',
        }

        for pattern_name, tests in results.items():
            failed = sum(1 for _, expected, actual, _ in tests if expected != actual)

            if failed > 0 and pattern_name in fixes:
                print(f"\n🔧 {pattern_name}:")
                print(f"   Current issues: {failed} test(s) failing")
                print("   Suggested pattern:")
                print(f"   {fixes[pattern_name]}")


def main():
    """Run pattern validation."""
    print("🔍 Validating Secret Detection Patterns\n")

    validator = PatternValidator()
    results = validator.validate_all_patterns()
    validator.generate_report(results)
    validator.suggest_pattern_fixes(results)

    # Determine exit code
    all_passed = all(
        expected == actual
        for tests in results.values()
        for _, expected, actual, _ in tests
    )

    if all_passed:
        print("\n" + "=" * 70)
        print("✅ ALL PATTERNS VALIDATED SUCCESSFULLY")
        print("=" * 70)
        return 0
    print("\n" + "=" * 70)
    print("❌ SOME PATTERNS FAILED VALIDATION")
    print("=" * 70)
    return 1


if __name__ == "__main__":
    sys.exit(main())
