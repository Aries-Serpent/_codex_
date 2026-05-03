#!/usr/bin/env python3
"""Fix Phase 26 test files by removing unused variables/imports and adding proper skip markers."""

import re
from pathlib import Path


def fix_test_file(filepath: Path) -> tuple[int, list[str]]:
    """Fix a single test file. Returns (num_changes, list_of_changes)."""
    with open(filepath) as f:
        content = f.read()

    original_content = content
    changes = []

    # Remove unused imports
    unused_imports = [
        (r'^from pathlib import Path\n', r'', 'test_cli_edge_cases_phase26.py'),
        (r'^from unittest\.mock import patch, Mock\n', r'from unittest.mock import patch\n', 'test_context_agent_edge_cases_phase26.py'),
        (r'^from unittest\.mock import Mock\n', r'', 'test_context_agent_edge_cases_phase26.py'),
        (r'^import pytest\n', r'', 'test_utils_edge_cases_phase26.py'),
        (r'^import os\n', r'', 'test_utils_edge_cases_phase26.py'),
        (r'^from unittest\.mock import patch, Mock\n', r'from unittest.mock import patch\n', 'test_data_config_edge_cases_phase26.py'),
    ]

    for pattern, replacement, target_file in unused_imports:
        if filepath.name == target_file and re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            changes.append(f"Removed unused import: {pattern.strip()}")

    # Fix placeholder tests by adding assertions and skip markers
    # Pattern: function with pass statement and unused variables

    # Replace standalone pass statements with pytest.skip
    pass_pattern = r'(\s+)(# .*\n\s+)pass\n'
    matches = list(re.finditer(pass_pattern, content))
    for match in reversed(matches):  # Process in reverse to maintain positions
        indent = match.group(1)
        comment_line = match.group(2)
        # Add pytest.skip after the comment
        replacement = f'{comment_line}{indent}pytest.skip("Test not fully implemented - placeholder for edge case coverage")\n'
        content = content[:match.start()] + replacement + content[match.end():]
        changes.append("Added pytest.skip to placeholder test")

    # Remove or use unused variables with basic assertions
    unused_vars = [
        (r'(\s+)initial_size = len\(.*?\)\n\s+# .*\n\s+pass',
         r'\1# Skipping - test not fully implemented\n\1pytest.skip("Test not fully implemented")'),
        (r'(\s+)slow_action = lambda: time\.sleep\(100\)\n\s+# .*\n\s+pass',
         r'\1# Skipping - test not fully implemented\n\1pytest.skip("Test not fully implemented")'),
        (r'(\s+)(incomplete_config|invalid_ranges|config2|invalid_schema|empty_config|child_config|config) = .*?\n(\s+# .*\n)?(\s+pass|\s+$)',
         r'\1# Variable created but test not fully implemented\n\1pytest.skip("Test not fully implemented")'),
    ]

    for pattern, replacement in unused_vars:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append("Fixed unused variable with skip marker")

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return (len(changes), changes)

    return (0, [])

def main():
    """Fix all Phase 26 test files."""
    # Get repository root dynamically
    repo_root = Path(__file__).resolve().parents[1]  # scripts is one level down from root
    test_dir = repo_root / "tests"
    phase26_files = list(test_dir.rglob("*phase26*.py"))

    print(f"Found {len(phase26_files)} Phase 26 test files")
    total_changes = 0

    for filepath in sorted(phase26_files):
        num_changes, changes = fix_test_file(filepath)
        if num_changes > 0:
            print(f"\n{filepath.name}: {num_changes} changes")
            for change in changes[:5]:  # Show first 5 changes
                print(f"  - {change}")
            if len(changes) > 5:
                print(f"  ... and {len(changes) - 5} more")
            total_changes += num_changes

    print(f"\nTotal: {total_changes} changes across {len(phase26_files)} files")

if __name__ == "__main__":
    main()
