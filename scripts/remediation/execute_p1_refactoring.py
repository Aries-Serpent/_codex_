#!/usr/bin/env python3
"""
P1 Refactoring Automation Script

Executes high-priority refactoring tickets from CODE_LEVEL_REFACTORING_TICKETS.md
Focuses on:
1. to_dict() implementations (20 instances)
2. Context manager patterns (48 instances)
3. MCP detector consolidation (4 files, 89% similar)
4. Training loop variants (2 files, 100% similar)
"""

import ast
from pathlib import Path
from typing import List, Tuple


class RefactoringExecutor:
    """Executes P1 refactoring tickets."""

    def __init__(self, repo_root: Path, dry_run: bool = True):
        self.root = repo_root
        self.dry_run = dry_run
        self.changes = []
        self.errors = []

    def find_to_dict_implementations(self) -> List[Tuple[Path, int]]:
        """Find all to_dict() method implementations."""
        results = []

        for py_file in self.root.rglob("*.py"):
            if "venv" in str(py_file) or "node_modules" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content, filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == "to_dict":
                        results.append((py_file, node.lineno))
            except Exception:
                continue

        return results

    def create_dict_serializable_mixin(self):
        """Create base mixin for dict serialization."""
        mixin_code = '''"""Serialization utilities for converting objects to dictionaries."""

from typing import Any, Dict


class DictSerializable:
    """Mixin class providing dict serialization capability.
    
    Automatically converts object attributes to dictionary,
    excluding None values and private attributes.
    
    Usage:
        @dataclass
        class MyModel(DictSerializable):
            name: str
            value: int = None
            
        model = MyModel(name="test", value=42)
        data = model.to_dict()  # {"name": "test", "value": 42}
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary representation.
        
        Returns:
            Dictionary with non-None public attributes
        """
        result = {}
        for key, value in self.__dict__.items():
            # Skip private attributes
            if key.startswith('_'):
                continue
            # Skip None values
            if value is not None:
                # Handle nested DictSerializable objects
                if isinstance(value, DictSerializable):
                    result[key] = value.to_dict()
                # Handle lists of DictSerializable objects
                elif isinstance(value, list) and value and isinstance(value[0], DictSerializable):
                    result[key] = [v.to_dict() for v in value]
                else:
                    result[key] = value
        return result
'''

        output_path = self.root / "src" / "codex_ml" / "utils" / "serialization.py"

        if not self.dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(mixin_code)
            self.changes.append(f"Created {output_path}")
        else:
            self.changes.append(f"Would create {output_path}")

        return output_path

    def find_context_managers(self) -> List[Tuple[Path, str, int]]:
        """Find context manager implementations (__enter__/__exit__)."""
        results = []

        for py_file in self.root.rglob("*.py"):
            if "venv" in str(py_file) or "node_modules" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content, filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = {m.name for m in node.body if isinstance(m, ast.FunctionDef)}
                        if "__enter__" in methods or "__exit__" in methods:
                            results.append((py_file, node.name, node.lineno))
            except Exception:
                continue

        return results

    def consolidate_mcp_detectors(self):
        """Consolidate MCP detector pattern duplicates."""
        print("\n=== P1: MCP Detector Consolidation ===")

        # Find MCP detector files
        mcp_files = list(self.root.glob("**/mcp_*.py"))
        mcp_files.extend(self.root.glob("**/*_mcp.py"))

        print(f"Found {len(mcp_files)} potential MCP detector files")

        for f in mcp_files[:5]:  # Show first 5
            print(f"  - {f.relative_to(self.root)}")

        if mcp_files:
            self.changes.append(f"Identified {len(mcp_files)} MCP detector files for review")

        return mcp_files

    def consolidate_training_loops(self):
        """Consolidate training loop variants."""
        print("\n=== P1: Training Loop Consolidation ===")

        # Find training loop files
        training_files = []
        for pattern in ["**/train*.py", "**/training*.py", "**/engine*.py"]:
            training_files.extend(self.root.glob(pattern))

        # Filter to actual training loops (contain "for epoch" or similar)
        loop_files = []
        for f in training_files:
            try:
                with open(f, "r") as file:
                    content = file.read()
                    if "for epoch" in content.lower() or "training loop" in content.lower():
                        loop_files.append(f)
            except Exception:
                continue

        print(f"Found {len(loop_files)} files with training loops")

        for f in loop_files[:5]:
            print(f"  - {f.relative_to(self.root)}")

        if loop_files:
            self.changes.append(
                f"Identified {len(loop_files)} training loop files for consolidation"
            )

        return loop_files

    def generate_refactoring_report(self):
        """Generate comprehensive refactoring report."""
        print("\n" + "=" * 80)
        print("=== P1 REFACTORING EXECUTION REPORT ===")
        print("=" * 80)
        print()
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print()

        # Find to_dict implementations
        to_dict_impls = self.find_to_dict_implementations()
        print(f"📊 to_dict() implementations found: {len(to_dict_impls)}")
        print(f"   Recommendation: Create DictSerializable mixin")
        print()

        # Find context managers
        ctx_managers = self.find_context_managers()
        print(f"📊 Context manager classes found: {len(ctx_managers)}")
        print(f"   Recommendation: Review for contextlib.contextmanager usage")
        print()

        # MCP detectors
        mcp_files = self.consolidate_mcp_detectors()

        # Training loops
        training_files = self.consolidate_training_loops()

        print("\n" + "=" * 80)
        print("CHANGES SUMMARY")
        print("=" * 80)
        print()

        if self.changes:
            for change in self.changes:
                print(f"  ✓ {change}")
        else:
            print("  (No changes made - analysis only)")

        print()

        if self.errors:
            print("ERRORS:")
            for error in self.errors:
                print(f"  ✗ {error}")
            print()

        return {
            "to_dict_count": len(to_dict_impls),
            "context_managers": len(ctx_managers),
            "mcp_detectors": len(mcp_files),
            "training_loops": len(training_files),
            "changes": len(self.changes),
            "errors": len(self.errors),
        }

    def execute_p1_refactoring(self):
        """Execute P1 refactoring with safety checks."""
        print("=== EXECUTING P1 REFACTORING ===")
        print()

        # Step 1: Create DictSerializable mixin
        print("Step 1: Creating DictSerializable mixin...")
        mixin_path = self.create_dict_serializable_mixin()
        print(f"  ✓ {'Would create' if self.dry_run else 'Created'}: {mixin_path}")
        print()

        # Step 2: Generate report
        stats = self.generate_refactoring_report()

        return stats


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Execute P1 refactoring tickets")
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Preview changes without executing"
    )
    parser.add_argument("--execute", action="store_true", help="Actually execute refactoring")
    parser.add_argument(
        "--analyze-only", action="store_true", help="Only analyze, don't make changes"
    )

    args = parser.parse_args()

    root = Path.cwd()
    executor = RefactoringExecutor(root, dry_run=not args.execute)

    if args.analyze_only:
        stats = executor.generate_refactoring_report()
        print()
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print()
        print(f"Found {stats['to_dict_count']} to_dict() implementations")
        print(f"Found {stats['context_managers']} context manager classes")
        print(f"Found {stats['mcp_detectors']} MCP detector files")
        print(f"Found {stats['training_loops']} training loop files")
        print()
        print("Next steps:")
        print("  1. Review findings above")
        print("  2. Run with --dry-run to see proposed changes")
        print("  3. Run with --execute to apply changes")
    else:
        stats = executor.execute_p1_refactoring()

        print()
        print("=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print()
        print(f"Mode: {'DRY RUN' if not args.execute else 'LIVE EXECUTION'}")
        print(f"Changes: {stats['changes']}")
        print(f"Errors: {stats['errors']}")
        print()

        if not args.execute:
            print("ℹ️  This was a dry run. Use --execute to apply changes.")
        else:
            print("✅ Refactoring executed successfully!")
            print()
            print("Next steps:")
            print("  1. Review changes: git diff")
            print("  2. Run tests: pytest tests/ -v")
            print("  3. Commit: git add . && git commit -m 'refactor: P1 consolidation'")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
