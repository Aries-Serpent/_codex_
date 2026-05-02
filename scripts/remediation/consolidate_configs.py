#!/usr/bin/env python3
"""
Consolidate Configs

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/remediation/consolidate_configs.py [options]

    Examples:
    $ python scripts/remediation/consolidate_configs.py --help

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



import shutil
import sys
from pathlib import Path

# Configuration consolidation map
# Format: (source_path, target_path, action)
# Actions: 'remove_source', 'keep_both_update_shim', 'merge'
CONSOLIDATION_MAP = [
    # Flat conf/ → Hierarchical conf/
    ("conf/minimal_train.yaml", "conf/training/minimal.yaml", "keep_both_update_shim"),
    ("conf/config.yaml", "conf/training/config.yaml", "keep_both_update_shim"),
    ("conf/minimal_eval.yaml", "conf/eval/minimal.yaml", "keep_both_update_shim"),
    # configs/ → config/ (singular)
    ("configs/defaults.yaml", "config/defaults.yaml", "remove_source"),
    ("configs/base/defaults.yaml", "config/defaults.yaml", "remove_source"),
    # Duplicate locations (keep canonical)
    ("configs/development/minimal.yaml", "conf/training/minimal.yaml", "remove_source"),
    ("configs/base/local.yaml", "conf/data/local.yaml", "remove_source"),
    ("configs/experiments/default.yaml", "conf/experiment/default.yaml", "remove_source"),
    ("configs/experiments/sweep.yaml", "conf/experiment/sweep.yaml", "remove_source"),
    ("configs/experiments/basic.yaml", "conf/experiment/basic.yaml", "remove_source"),
    # SBOM config
    ("config/sample-sbom-config.yaml", "config/sbom/sample.yaml", "remove_source"),
    # Safety config
    ("src/codex_ml/safety/default_policy.yaml", "config/safety/policy.yaml", "remove_source"),
]


class ConfigConsolidator:
    """Consolidates duplicate configuration files."""

    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root = root_path
        self.dry_run = dry_run
        self.actions_taken = []
        self.errors = []

    def verify_files_exist(self):
        """Verify source and target files exist."""
        print("=== Verifying Files ===")
        for source, target, action in CONSOLIDATION_MAP:
            src_path = self.root / source
            tgt_path = self.root / target

            src_exists = src_path.exists()
            tgt_exists = tgt_path.exists()

            status = "✓" if src_exists else "✗"
            print(f"{status} {source} (source)")

            if action != "remove_source" or not tgt_exists:
                status = "✓" if tgt_exists else "⚠"
                print(f"  {status} {target} (target)")
            print()

    def compare_files(self, src: Path, tgt: Path) -> bool:
        """Compare two files for differences."""
        if not src.exists() or not tgt.exists():
            return False

        with open(src, "r") as f1, open(tgt, "r") as f2:
            return f1.read() == f2.read()

    def consolidate(self):
        """Execute consolidation."""
        print("=== Consolidation Plan ===")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print()

        for source, target, action in CONSOLIDATION_MAP:
            src_path = self.root / source
            tgt_path = self.root / target

            if not src_path.exists():
                print(f"⊘ SKIP: {source} (does not exist)")
                continue

            print(f"→ {source}")
            print(f"  Action: {action}")
            print(f"  Target: {target}")

            if action == "remove_source":
                if tgt_path.exists():
                    # Compare before removing
                    if self.compare_files(src_path, tgt_path):
                        print("  Status: Identical - safe to remove source")
                        if not self.dry_run:
                            src_path.unlink()
                            self.actions_taken.append(f"Removed {source}")
                    else:
                        print("  ⚠ WARNING: Files differ! Manual review needed.")
                        self.errors.append(f"Difference: {source} ≠ {target}")
                else:
                    print(f"  ⚠ WARNING: Target {target} doesn't exist!")
                    if not self.dry_run:
                        tgt_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, tgt_path)
                        src_path.unlink()
                        self.actions_taken.append(f"Moved {source} → {target}")

            elif action == "keep_both_update_shim":
                print("  Status: Keep both, add to SHIM inventory")
                self.actions_taken.append(f"Track in SHIM: {source} ↔ {target}")

            elif action == "merge":
                print("  Status: Requires manual merge")
                self.errors.append(f"Manual merge needed: {source} + {target}")

            print()

        return len(self.errors) == 0

    def generate_shim_entries(self):
        """Generate SHIM inventory entries for configs to keep."""
        print("=== SHIM Inventory Entries ===")
        print()

        entries = []
        for source, target, action in CONSOLIDATION_MAP:
            if action == "keep_both_update_shim":
                target_stem = Path(target).stem
                entry = f"""
  - module: config.{target_stem}
    legacy_path: "{source}"
    canonical_path: "{target}"
    owner: ml-platform
    status: migration
    rationale: "Migrating from flat conf/ to hierarchical conf/{{training,data,experiment}}/"
    deprecation_date: "2026-03-01"
    whitelist_duplicates:
      - "{source}"
    notes: "Legacy flat structure being replaced by hierarchical. Both kept during migration period."
"""
                entries.append(entry)
                print(entry)

        return entries

    def generate_migration_guide(self):
        """Generate migration guide for developers."""
        print("=== Migration Guide ===")
        print()
        print("## Configuration File Consolidation")
        print()
        print("### Old → New Paths")
        print()

        for source, target, action in CONSOLIDATION_MAP:
            if action in ["remove_source", "keep_both_update_shim"]:
                print(f"- `{source}` → `{target}`")

        print()
        print("### Code Updates Needed")
        print()
        print("```python")
        print("# Old imports")
        print("# from omegaconf import OmegaConf")
        print("# config = OmegaConf.load('conf/minimal_train.yaml')")
        print()
        print("# New imports")
        print("# config = OmegaConf.load('conf/training/minimal.yaml')")
        print("```")
        print()
        print("### Search and Replace")
        print()
        print("```bash")
        for source, target, action in CONSOLIDATION_MAP:
            if action == "remove_source":
                print(f"find . -name '*.py' -exec sed -i 's|{source}|{target}|g' {{}} \\;")
        print("```")

    def report(self):
        """Generate final report."""
        print("\n" + "=" * 80)
        print("=== CONSOLIDATION REPORT ===")
        print("=" * 80)
        print()
        print(f"Actions taken: {len(self.actions_taken)}")
        for action in self.actions_taken:
            print(f"  ✓ {action}")
        print()

        if self.errors:
            print(f"Errors/Warnings: {len(self.errors)}")
            for error in self.errors:
                print(f"  ⚠ {error}")
            print()
            return False
        print("✓ No errors")
        return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Consolidate duplicate configuration files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done without making changes",
    )
    parser.add_argument("--execute", action="store_true", help="Actually perform the consolidation")
    parser.add_argument("--verify-only", action="store_true", help="Only verify files exist")
    parser.add_argument(
        "--generate-shim", action="store_true", help="Generate SHIM inventory entries"
    )
    parser.add_argument("--generate-guide", action="store_true", help="Generate migration guide")

    args = parser.parse_args()

    root = Path.cwd()
    consolidator = ConfigConsolidator(root, dry_run=not args.execute)

    if args.verify_only:
        consolidator.verify_files_exist()
        return 0

    if args.generate_shim:
        consolidator.generate_shim_entries()
        return 0

    if args.generate_guide:
        consolidator.generate_migration_guide()
        return 0

    # Run consolidation
    consolidator.verify_files_exist()
    success = consolidator.consolidate()

    if args.execute:
        consolidator.generate_shim_entries()

    consolidator.generate_migration_guide()
    consolidator.report()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
