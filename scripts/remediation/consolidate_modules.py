#!/usr/bin/env python3
"""
import logging
logger = logging.getLogger(__name__)
Python Module Consolidation Script

Consolidates duplicate Python modules by:
1. Removing scripts/analysis/ (keeping tools/dupinv/)
2. Updating all imports
3. Cleaning up references
"""

from pathlib import Path
import re


class ModuleConsolidator:
    """Consolidates duplicate Python modules."""

    def __init__(self, root: Path, dry_run: bool = True):
        self.root = root
        self.dry_run = dry_run
        self.changes = []

    def find_import_references(self, old_module: str) -> list:
        """Find all files importing the old module using safe Python pathlib."""
        try:
            files_with_refs = []

            # Use pathlib to safely search for Python files
            for py_file in self.root.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        if old_module in content:
                            files_with_refs.append(py_file)
                except (IOError, UnicodeDecodeError):
                    continue

            return files_with_refs
        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Error finding references: {e}")
            return []

    def update_imports_in_file(self, file_path: Path, old_module: str, new_module: str):
        """Update imports in a single file."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            original_content = content

            # Pattern 1: from old_module import ...
            content = re.sub(rf"from {re.escape(old_module)}", f"from {new_module}", content)

            # Pattern 2: import old_module
            content = re.sub(
                rf"import {re.escape(old_module)}(?!\w)", f"import {new_module}", content
            )

            if content != original_content:
                if not self.dry_run:
                    with open(file_path, "w") as f:
                        f.write(content)
                    self.changes.append(f"Updated imports in {file_path}")
                else:
                    self.changes.append(f"Would update imports in {file_path}")
                return True
            return False
        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Error updating {file_path}: {e}")
            return False

    def consolidate_scripts_analysis(self):
        """Consolidate scripts/analysis → tools/dupinv."""
        print("=== Consolidating scripts/analysis → tools/dupinv ===")
        print()

        old_module = "scripts.analysis"
        new_module = "tools.dupinv"

        # Step 1: Find all references
        print("Step 1: Finding references...")
        refs = self.find_import_references(old_module)
        print(f"Found {len(refs)} files importing {old_module}")
        for ref in refs[:10]:
            print(f"  - {ref}")
        if len(refs) > 10:
            print(f"  ... and {len(refs) - 10} more")
        print()

        # Step 2: Update imports
        print("Step 2: Updating imports...")
        updated = 0
        for ref in refs:
            if self.update_imports_in_file(ref, old_module, new_module):
                updated += 1
        print(f"Updated {updated} files")
        print()

        # Step 3: Remove old directory
        print("Step 3: Removing scripts/analysis/...")
        old_dir = self.root / "scripts" / "analysis"
        if old_dir.exists():
            if not self.dry_run:
                import shutil

                shutil.rmtree(old_dir)
                self.changes.append(f"Removed {old_dir}")
                print(f"✓ Removed {old_dir}")
            else:
                self.changes.append(f"Would remove {old_dir}")
                print(f"Would remove {old_dir}")
        else:
            print(f"Directory {old_dir} doesn't exist")
        print()

    def consolidate_revert_or_restore(self):
        """Remove tools/revert_or_restore(other).py."""
        print("=== Consolidating revert_or_restore ===")
        print()

        other_file = self.root / "tools" / "revert_or_restore(other).py"
        if other_file.exists():
            if not self.dry_run:
                other_file.unlink()
                self.changes.append(f"Removed {other_file}")
                print(f"✓ Removed {other_file}")
            else:
                self.changes.append(f"Would remove {other_file}")
                print(f"Would remove {other_file}")
        else:
            print(f"File {other_file} doesn't exist")
        print()

    def consolidate_package_main(self):
        """Consolidate _package_main.py."""
        print("=== Investigating _package_main.py ===")
        print()

        root_file = self.root / "codex_ml" / "_package_main.py"
        src_file = self.root / "src" / "codex_ml" / "_package_main.py"

        if root_file.exists() and src_file.exists():
            # Compare
            with open(root_file) as f1, open(src_file) as f2:
                if f1.read() == f2.read():
                    print("Files are identical")
                    if not self.dry_run:
                        root_file.unlink()
                        self.changes.append(f"Removed {root_file} (keeping src/ version)")
                        print(f"✓ Removed {root_file}")
                    else:
                        self.changes.append(f"Would remove {root_file}")
                        print(f"Would remove {root_file}")
                else:
                    print("⚠ Files differ - manual review needed")
                    self.changes.append(f"Manual review: {root_file} vs {src_file}")
        else:
            print(f"One or both files don't exist:")
            print(f"  {root_file.exists()}: {root_file}")
            print(f"  {src_file.exists()}: {src_file}")
        print()

    def report(self):
        """Generate report."""
        print("\n" + "=" * 80)
        print("=== MODULE CONSOLIDATION REPORT ===")
        print("=" * 80)
        print()
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Changes: {len(self.changes)}")
        print()

        for change in self.changes:
            prefix = "→" if self.dry_run else "✓"
            print(f"  {prefix} {change}")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Consolidate duplicate Python modules")
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Show what would be done"
    )
    parser.add_argument("--execute", action="store_true", help="Actually perform consolidation")

    args = parser.parse_args()

    root = Path.cwd()
    consolidator = ModuleConsolidator(root, dry_run=not args.execute)

    # Run consolidations
    consolidator.consolidate_scripts_analysis()
    consolidator.consolidate_revert_or_restore()
    consolidator.consolidate_package_main()

    # Report
    consolidator.report()

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
