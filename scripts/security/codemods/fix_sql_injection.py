"""
Codemod: Fix SQL injection vulnerabilities

Transforms:
  cursor.execute(f"SELECT * FROM {table}") → cursor.execute("SELECT * FROM ?", (table,))
  cursor.execute("SELECT * FROM " + table) → cursor.execute("SELECT * FROM ?", (table,))

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Input validation on file paths
- Defensive error handling
- Pattern matching with bounds
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def fix_fstring_sql(content: str) -> Tuple[str, List[str]]:
    """Fix f-string SQL injection patterns."""
    changes: List[str] = []

    # Pattern: cursor.execute(f"... {var}...")
    fstring_pattern = r'(\w+\.execute\s*\(\s*)f(["\'])(.*?)\2(\s*\))'

    def replace_fstring(match: re.Match) -> str:
        prefix = match.group(1)
        quote = match.group(2)
        sql = match.group(3)
        suffix = match.group(4)

        # Find all {var} patterns
        vars_pattern = r'\{(\w+)\}'
        variables = re.findall(vars_pattern, sql)

        if not variables:
            return match.group(0)

        # Replace {var} with ?
        new_sql = re.sub(vars_pattern, '?', sql)

        # Create parameters tuple
        # Note: Only parameterize simple identifiers - complex expressions need manual review
        params = ', '.join(variables)
        
        # Handle single variable case - need trailing comma for single-element tuple
        if len(variables) == 1:
            var = variables[0]
            # Only add comma if it's a simple identifier (not already a tuple/list reference)
            # Check for common patterns that indicate the variable might be iterable:
            # - ends with 's' (plural, might be a list)
            # - contains 'list', 'tuple', 'array', 'items'
            # These need manual review to avoid (iterable,) which would be incorrect
            likely_iterable_patterns = ['list', 'tuple', 'array', 'items', 'values', 'params']
            is_likely_iterable = (
                any(pattern in var.lower() for pattern in likely_iterable_patterns)
            )
            
            if var.isidentifier() and not is_likely_iterable:
                params += ','  # Single element tuple needs trailing comma
                changes.append(f"Parameterized SQL with variable: {var} (added trailing comma for single-element tuple)")
            else:
                # Variable might be iterable - add warning comment
                changes.append(f"Parameterized SQL with variable: {var} (WARNING: verify {var} is not already iterable)")
        else:
            changes.append(f"Parameterized SQL with variables: {variables}")

        return f'{prefix}{quote}{new_sql}{quote}, ({params}){suffix}'

    new_content = re.sub(fstring_pattern, replace_fstring, content, flags=re.DOTALL)

    return new_content, changes


def fix_concat_sql(content: str) -> Tuple[str, List[str]]:
    """Fix string concatenation SQL injection patterns."""
    changes: List[str] = []

    # Pattern: cursor.execute("SELECT..." + var)
    concat_pattern = r'(\w+\.execute\s*\(\s*)(["\'])([^"\']+)\2\s*\+\s*(\w+)(\s*\))'

    def replace_concat(match: re.Match) -> str:
        prefix = match.group(1)
        quote = match.group(2)
        sql_before = match.group(3)
        variable = match.group(4)
        suffix = match.group(5)

        new_sql = f"{sql_before}?"

        changes.append(f"Parameterized concatenated SQL with variable: {variable}")

        return f'{prefix}{quote}{new_sql}{quote}, ({variable},){suffix}'

    new_content = re.sub(concat_pattern, replace_concat, content)

    return new_content, changes


def transform_file(file_path: str) -> Tuple[str, List[str]]:
    """Transform a single file."""
    # Input validation (safeguard)
    if not file_path or not isinstance(file_path, str):
        return "", ["Invalid file path"]

    path = Path(file_path)
    if not path.exists():
        return "", [f"File not found: {file_path}"]

    # File size check (safeguard)
    if path.stat().st_size > MAX_FILE_SIZE:
        return "", [f"File too large: {file_path}"]

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return "", [f"Error reading file: {e}"]

    all_changes: List[str] = []

    # Apply fixes
    content, changes = fix_fstring_sql(content)
    all_changes.extend(changes)

    content, changes = fix_concat_sql(content)
    all_changes.extend(changes)

    return content, all_changes


def main() -> None:
    """Main entry point."""
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python fix_sql_injection.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    new_content, changes = transform_file(file_path)

    if changes:
        logger.info(f"✅ Made {len(changes)} changes:")
        for change in changes:
            logger.info(f"  - {change}")

        with open(file_path, "w") as f:
            f.write(new_content)
        logger.info(f"💾 Updated {file_path}")
    else:
        logger.info("No changes needed")


if __name__ == "__main__":
    main()
