#!/usr/bin/env python3
"""
Fix from __future__ import placement in Python files.

This script ensures from __future__ imports are placed immediately after
the module docstring and before any other code or imports.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def extract_module_docstring(lines: list[str]) -> tuple[list[str], int]:
    """Extract the module docstring and return it with the end index."""
    docstring_lines = []
    i = 0

    # Skip shebang and encoding declarations
    while i < len(lines):
        line = lines[i]
        if line.startswith('#!') or line.startswith('# -*- coding') or line.startswith('# coding:') or line.strip() == '':
            docstring_lines.append(line)
            i += 1
        else:
            break

    # Check for module docstring
    if i < len(lines):
        line = lines[i].strip()
        if line.startswith('"""') or line.startswith("'''"):
            quote = '"""' if line.startswith('"""') else "'''"
            docstring_lines.append(lines[i])
            i += 1

            # Multi-line docstring
            if not line.endswith(quote) or line.count(quote) < 2:
                while i < len(lines):
                    docstring_lines.append(lines[i])
                    if quote in lines[i]:
                        i += 1
                        break
                    i += 1

    return docstring_lines, i


def fix_future_imports_file(filepath: Path) -> bool:
    """Fix from __future__ import placement in a single file."""
    try:
        content = filepath.read_text()
        lines = content.splitlines(keepends=True)

        # Check if file has from __future__ imports
        has_future = any('from __future__' in line for line in lines)
        if not has_future:
            return False

        # Extract module docstring
        docstring_lines, doc_end_idx = extract_module_docstring(lines)

        # Collect all from __future__ imports and their indices
        future_imports = []
        future_indices = []

        for i, line in enumerate(lines):
            if line.strip().startswith('from __future__'):
                future_imports.append(line)
                future_indices.append(i)

        # If no future imports after docstring, already correct
        if not future_imports:
            return False

        # Check if already correct (all future imports right after docstring)
        if future_indices[0] == doc_end_idx:
            # Check if consecutive
            is_consecutive = True
            for idx, fut_idx in enumerate(future_indices):
                if fut_idx != doc_end_idx + idx:
                    is_consecutive = False
                    break
            if is_consecutive:
                return False  # Already correct

        # Reconstruct file
        new_lines = []

        # 1. Add docstring
        new_lines.extend(docstring_lines)

        # 2. Add blank line after docstring if docstring exists and doesn't end with blank
        if docstring_lines and docstring_lines[-1].strip():
            new_lines.append('\n')

        # 3. Add all from __future__ imports
        for future_line in future_imports:
            if future_line not in new_lines:
                new_lines.append(future_line)

        # 4. Add blank line after future imports
        new_lines.append('\n')

        # 5. Add remaining code (excluding duplicate future imports)
        for i, line in enumerate(lines[doc_end_idx:], start=doc_end_idx):
            if i not in future_indices:
                new_lines.append(line)

        new_content = ''.join(new_lines)

        # Validate the new content can be parsed
        try:
            ast.parse(new_content)
        except SyntaxError as e:
            print(f"  ⚠️  Warning: Fixed {filepath} but still has syntax error: {e}")
            return False

        if new_content != content:
            filepath.write_text(new_content)
            return True
        return False

    except Exception as e:
        print(f"  ❌ Error fixing {filepath}: {e}", file=sys.stderr)
        return False


def main() -> int:
    """Main entry point."""
    repo_root = Path.cwd()
    scripts_dir = repo_root / 'scripts'

    if not scripts_dir.exists():
        print("Error: scripts/ directory not found", file=sys.stderr)
        return 1

    fixed_files = []
    error_files = []

    print("🔄 Fixing from __future__ import placement...\n")

    # List of known problematic files
    problem_files = [
        'scripts/archival/check_archival_compliance.py',
        'scripts/archive/select_and_compress.py',
        'scripts/archive/trend_aggregate.py',
        'scripts/archive/validate_prefixes.py',
        'scripts/audit/build_integrity_chain.py',
        'scripts/automation/sync_issues_to_report.py',
        'scripts/cognitive/har_ingest.py',
        'scripts/config/schema_validate.py',
        'scripts/content_filter/apply_filter.py',
        'scripts/env/export_env_snapshot.py',
        'scripts/env/print_env_info.py',
        'scripts/metrics/token_similarity.py',
        'scripts/multi_repo/federated_index.py',
        'scripts/packaging/build_solution.py',
        'scripts/remediation/list_shims.py',
        'scripts/remediation/refactor_imports.py',
        'scripts/security/cherry_pick_strategy.py',
        'scripts/security/classify_severity.py',
        'scripts/security/copy_ideal_versions.py',
        'scripts/security/resolve_merge_conflicts.py',
        'scripts/security/revert_overly_broad_replacements.py',
        'scripts/security/secret_context_correlate.py',
        'scripts/security/secret_entropy_scan.py',
        'scripts/space_traversal/status_update_report.py',
        'scripts/space_traversal/trend_db.py',
    ]

    for file_path_str in problem_files:
        filepath = repo_root / file_path_str
        if not filepath.exists():
            print(f"  ⚠️  Skipping (not found): {file_path_str}")
            continue

        try:
            if fix_future_imports_file(filepath):
                fixed_files.append(filepath)
                print(f"  ✅ Fixed: {filepath.relative_to(repo_root)}")
        except Exception as e:
            error_files.append(filepath)
            print(f"  ❌ Error: {filepath.relative_to(repo_root)}: {e}")

    print("\n📊 Summary:")
    print(f"  ✅ Fixed: {len(fixed_files)} files")
    if error_files:
        print(f"  ❌ Errors: {len(error_files)} files")

    # Validate all fixed files compile
    print("\n🔍 Validating fixed files...")
    validation_errors = []
    for filepath in fixed_files:
        try:
            with open(filepath) as f:
                ast.parse(f.read())
        except SyntaxError as e:
            validation_errors.append((filepath, e))
            print(f"  ❌ Validation failed: {filepath.relative_to(repo_root)}: {e}")

    if not validation_errors:
        print(f"  ✅ All {len(fixed_files)} files validated successfully")

    return 0 if not error_files and not validation_errors else 1


if __name__ == '__main__':
    sys.exit(main())
