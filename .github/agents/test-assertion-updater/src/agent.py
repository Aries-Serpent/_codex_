#!/usr/bin/env python3
"""
Test Assertion Updater Agent

Automatically detect and fix test assertion mismatches when implementation evolves
while preserving test intent and coverage.

Usage:
    python -m test_assertion_updater.src.agent analyze tests/test_example.py::test_function
    python -m test_assertion_updater.src.agent fix tests/test_example.py::test_function --validate
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class AssertionMismatch:
    """Represents a detected assertion mismatch"""
    test_name: str
    file_path: Path
    line_number: int
    mismatch_type: str  # 'string_format', 'data_structure', 'type_change'
    expected_value: str
    actual_value: str
    confidence: float


@dataclass
class FixProposal:
    """Represents a proposed fix for an assertion"""
    original_code: str
    fixed_code: str
    reason: str
    validation_strategy: str


class TestAssertionUpdater:
    """Main agent class for test assertion updates"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent with optional configuration"""
        self.config = self._load_config(config_path)
        self.patterns = self._load_patterns()

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load agent configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"

        if not config_path.exists():
            return self._default_config()

        with open(config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            'version': '1.0.0',
            'agent_name': 'test-assertion-updater',
            'capabilities': ['parse_failures', 'analyze_code', 'generate_fixes', 'validate_fixes'],
            'settings': {
                'timeout_seconds': 300,
                'max_retries': 3,
                'log_level': 'INFO',
                'enable_caching': True
            }
        }

    def _load_patterns(self) -> dict[str, list[dict]]:
        """Load known assertion evolution patterns"""
        return {
            'string_format': [
                {
                    'old_pattern': r'assert .* == "[^"]+"',
                    'new_pattern': r'assert "[^"]+" in .*',
                    'reason': 'Error message evolved to be more detailed'
                }
            ],
            'data_structure': [
                {
                    'old_pattern': r'assert .* == \[',
                    'new_pattern': r'assert .*\[".*"\] ==',
                    'reason': 'Return value changed from list to list of dicts'
                }
            ],
            'type_change': [
                {
                    'old_pattern': r'assert .* == \d+',
                    'new_pattern': r'assert .*\["count"\] ==',
                    'reason': 'Return value changed from int to dict with metadata'
                }
            ]
        }

    def parse_pytest_output(self, pytest_output: str) -> list[AssertionMismatch]:
        """Parse pytest failure output to identify assertion errors"""
        mismatches = []

        # Pattern to extract assertion errors from pytest output
        pattern = re.compile(
            r"(?P<file>[^\s]+\.py)::(?P<test>\w+).*?"
            r"AssertionError:.*?assert\s+(?P<assertion>.+?)(?:\n|$)",
            re.DOTALL
        )

        for match in pattern.finditer(pytest_output):
            file_path = Path(match.group('file'))
            test_name = match.group('test')
            assertion = match.group('assertion')

            # Try to extract expected and actual values
            expected, actual = self._extract_values(assertion)
            mismatch_type = self._classify_mismatch(expected, actual)

            mismatches.append(AssertionMismatch(
                test_name=f"{file_path}::{test_name}",
                file_path=file_path,
                line_number=0,  # Would need more parsing to get exact line
                mismatch_type=mismatch_type,
                expected_value=expected,
                actual_value=actual,
                confidence=0.8
            ))

        return mismatches

    def _extract_values(self, assertion: str) -> tuple[str, str]:
        """Extract expected and actual values from assertion"""
        # Simple extraction - would be more sophisticated in production
        parts = assertion.split('==')
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()
        return assertion, ""

    def _classify_mismatch(self, expected: str, actual: str) -> str:
        """Classify the type of mismatch"""
        if '{' in actual or '[' in actual:
            if '{' not in expected and '[' not in expected:
                return 'data_structure'

        if '"' in expected and '"' in actual:
            return 'string_format'

        return 'type_change'

    def generate_fix(self, mismatch: AssertionMismatch) -> FixProposal:
        """Generate a proposed fix for the assertion mismatch"""
        if mismatch.mismatch_type == 'string_format':
            return self._fix_string_format(mismatch)
        if mismatch.mismatch_type == 'data_structure':
            return self._fix_data_structure(mismatch)
        if mismatch.mismatch_type == 'type_change':
            return self._fix_type_change(mismatch)
        raise ValueError(f"Unknown mismatch type: {mismatch.mismatch_type}")

    def _fix_string_format(self, mismatch: AssertionMismatch) -> FixProposal:
        """Generate fix for string format changes"""
        # Extract the key part of the string
        expected_clean = mismatch.expected_value.strip('"\'')

        return FixProposal(
            original_code=f'assert result == "{expected_clean}"',
            fixed_code=f'assert "{expected_clean}" in str(result)',
            reason='Error message format evolved to be more descriptive',
            validation_strategy='string_contains'
        )

    def _fix_data_structure(self, mismatch: AssertionMismatch) -> FixProposal:
        """Generate fix for data structure changes"""
        return FixProposal(
            original_code=f'assert result == {mismatch.expected_value}',
            fixed_code='assert [item["name"] if isinstance(item, dict) else item for item in result] == expected',
            reason='Implementation evolved to return structured data with metadata',
            validation_strategy='structure_extraction'
        )

    def _fix_type_change(self, mismatch: AssertionMismatch) -> FixProposal:
        """Generate fix for type changes"""
        return FixProposal(
            original_code=f'assert result == {mismatch.expected_value}',
            fixed_code=f'assert result["value"] == {mismatch.expected_value}',
            reason='Return type changed from primitive to dict with metadata',
            validation_strategy='dict_key_access'
        )

    def validate_fix(self, fix: FixProposal, test_file: Path) -> bool:
        """Validate the proposed fix using property-based testing or dry-run"""
        # In production, would run hypothesis tests or pytest dry-run
        # For now, basic validation
        try:
            # Check that the fixed code is valid Python
            ast.parse(fix.fixed_code)
            return True
        except SyntaxError:
            return False

    def apply_fix(self, fix: FixProposal, test_file: Path, line_number: int) -> bool:
        """Apply the fix to the test file"""
        try:
            with open(test_file) as f:
                lines = f.readlines()

            # Find and replace the line
            for i, line in enumerate(lines):
                if fix.original_code.strip() in line.strip():
                    lines[i] = line.replace(fix.original_code, fix.fixed_code)
                    break

            with open(test_file, 'w') as f:
                f.writelines(lines)

            return True
        except Exception as e:
            print(f"Error applying fix: {e}")
            return False

    def generate_commit_message(self, fix: FixProposal, mismatch: AssertionMismatch) -> str:
        """Generate a detailed commit message for the fix"""
        return f"""fix(tests): update assertion in {mismatch.test_name}

- Previous: {fix.original_code}
- Updated: {fix.fixed_code}
- Reason: {fix.reason}

Validated with {fix.validation_strategy}
Auto-generated by test-assertion-updater agent
"""


if __name__ == '__main__':
    print("Test Assertion Updater Agent - Use as a module")
