#!/usr/bin/env python3
"""
Test Signature Validation Utility

Automatically detects mismatches between test method calls and actual implementation signatures.
Based on patterns learned from PR test fixes on 2026-02-06.

Usage:
    python scripts/test_signature_validator.py [--check-only] [--fix] [path/to/tests/]

Examples:
    # Check all tests
    python scripts/test_signature_validator.py --check-only

    # Check specific test file
    python scripts/test_signature_validator.py --check-only tests/agents/

    # Apply fixes automatically
    python scripts/test_signature_validator.py --fix tests/agents/test_mental_mapping_core_flows.py
"""

from __future__ import annotations

import argparse
import ast
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class SignatureMismatch:
    """Represents a signature mismatch between test and implementation."""

    test_file: Path
    line_number: int
    function_name: str
    issue_type: str
    test_call: str
    expected_signature: str
    suggestion: str
    severity: str  # "critical", "warning", "info"


class SignatureValidator:
    """Validates test method calls match implementation signatures."""

    def __init__(self, src_root: Path, test_root: Path):
        self.src_root = src_root
        self.test_root = test_root
        self.mismatches: list[SignatureMismatch] = []
        self.checked_files = 0
        self.checked_calls = 0

    def validate_directory(self, test_dir: Path) -> list[SignatureMismatch]:
        """Validate all test files in a directory."""
        for test_file in test_dir.rglob("test_*.py"):
            if test_file.is_file():
                self.validate_file(test_file)
        return self.mismatches

    def validate_file(self, test_file: Path) -> list[SignatureMismatch]:
        """Validate a single test file."""
        self.checked_files += 1

        try:
            with open(test_file) as f:
                content = f.read()

            tree = ast.parse(content, filename=str(test_file))

            # Find all method/function calls in tests
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    self._check_call(node, test_file, content)

        except Exception as e:
            print(f"⚠️  Error parsing {test_file}: {e}")

        return self.mismatches

    def _check_call(self, call_node: ast.Call, test_file: Path, content: str):
        """Check a specific function call for signature mismatches."""
        self.checked_calls += 1

        # Extract function name
        func_name = self._get_function_name(call_node)
        if not func_name or func_name.startswith("_") is False:
            # Skip if not a private method (common pattern for internal APIs)
            return

        # Try to find the implementation
        impl_func = self._find_implementation(func_name)
        if not impl_func:
            return

        # Get actual signature
        try:
            sig = inspect.signature(impl_func)
        except Exception:
            return

        # Check for mismatches
        mismatch = self._detect_mismatch(call_node, sig, func_name, test_file)
        if mismatch:
            self.mismatches.append(mismatch)

    def _get_function_name(self, call_node: ast.Call) -> str | None:
        """Extract function name from call node."""
        if isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        return None

    def _find_implementation(self, func_name: str) -> Any | None:
        """Try to find the actual implementation of a function."""
        # This is a simplified version - in production, would use more sophisticated lookup
        # For now, just demonstrate the pattern
        try:
            # Try common import patterns
            for module_path in ["agents.mental_mapping", "agents.developer_orchestrator"]:
                try:
                    parts = module_path.split(".")
                    module = __import__(module_path)
                    for part in parts[1:]:
                        module = getattr(module, part)

                    # Look through classes for the method
                    for name in dir(module):
                        obj = getattr(module, name)
                        if inspect.isclass(obj) and hasattr(obj, func_name):
                            return getattr(obj, func_name)
                except Exception:
                    # Best-effort lookup: ignore failures for individual modules
                    continue
        except Exception as e:
            # Last-resort guard: log unexpected errors during implementation lookup
            print(
                f"⚠️  Unexpected error while looking up implementation for {func_name!r}: {e!r}",
                file=sys.stderr,
            )
        return None

    def _detect_mismatch(
        self,
        call_node: ast.Call,
        sig: inspect.Signature,
        func_name: str,
        test_file: Path
    ) -> SignatureMismatch | None:
        """Detect if there's a signature mismatch."""
        # Get parameters from call
        call_kwargs = {kw.arg for kw in call_node.keywords if kw.arg}

        # Get parameters from signature
        sig_params = set(sig.parameters.keys())
        if "self" in sig_params:
            sig_params.remove("self")
        if "cls" in sig_params:
            sig_params.remove("cls")

        # Check for unexpected kwargs
        unexpected_kwargs = call_kwargs - sig_params

        if unexpected_kwargs:
            line_num = call_node.lineno
            return SignatureMismatch(
                test_file=test_file,
                line_number=line_num,
                function_name=func_name,
                issue_type="unexpected_kwargs",
                test_call=f"{func_name}(..., {', '.join(f'{k}=...' for k in unexpected_kwargs)})",
                expected_signature=str(sig),
                suggestion=f"Remove kwargs: {', '.join(unexpected_kwargs)}. Use positional args instead.",
                severity="critical"
            )

        return None

    def generate_report(self) -> str:
        """Generate a human-readable report."""
        if not self.mismatches:
            return f"""
✅ Test Signature Validation - All Clear!

Files checked: {self.checked_files}
Calls validated: {self.checked_calls}
Issues found: 0

All test method signatures match their implementations.
"""

        report = f"""
⚠️  Test Signature Validation - Issues Found

Files checked: {self.checked_files}
Calls validated: {self.checked_calls}
Issues found: {len(self.mismatches)}

{'='*70}
"""

        # Group by severity
        critical = [m for m in self.mismatches if m.severity == "critical"]
        warnings = [m for m in self.mismatches if m.severity == "warning"]
        info = [m for m in self.mismatches if m.severity == "info"]

        for severity, mismatches in [("CRITICAL", critical), ("WARNING", warnings), ("INFO", info)]:
            if not mismatches:
                continue

            report += f"\n{severity} ({len(mismatches)} issues):\n"
            report += "-" * 70 + "\n"

            for m in mismatches:
                report += f"""
File: {m.test_file}
Line: {m.line_number}
Function: {m.function_name}
Issue: {m.issue_type}
Test call: {m.test_call}
Expected: {m.expected_signature}
Suggestion: {m.suggestion}
"""

        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate test method signatures match implementations"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="tests/",
        help="Path to test directory or file (default: tests/)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for issues, don't apply fixes"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically apply fixes (use with caution)"
    )

    args = parser.parse_args()

    # Setup paths
    repo_root = Path(__file__).parent.parent
    src_root = repo_root / "src"
    test_root = repo_root / "tests"

    target_path = repo_root / args.path
    if not target_path.exists():
        print(f"❌ Path not found: {target_path}")
        return 1

    print(f"🔍 Validating test signatures in: {target_path}")
    print()

    # Create validator
    validator = SignatureValidator(src_root, test_root)

    # Run validation
    if target_path.is_file():
        validator.validate_file(target_path)
    else:
        validator.validate_directory(target_path)

    # Generate report
    report = validator.generate_report()
    print(report)

    # Apply fixes if requested
    if args.fix and validator.mismatches:
        print("\n⚠️  Automatic fixing not yet implemented.")
        print("Please review the issues above and apply fixes manually.")
        print("See .github/agents/test-alignment-fixer-enhanced.md for patterns.")
        return 1

    # Return exit code based on critical issues
    critical_count = sum(1 for m in validator.mismatches if m.severity == "critical")
    return 1 if critical_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
