#!/usr/bin/env python
"""
Migrate legacy config directories to unified structure.

Usage:
    python scripts/migrate_configs.py --dry-run
    python scripts/migrate_configs.py --execute
"""
import argparse
import shutil
from pathlib import Path
import yaml


LEGACY_DIRS = ["config", "conf"]
TARGET_DIR = Path("configs")


def find_legacy_configs() -> list:
    """Find all legacy config directories and files."""
    legacy = []

    for dir_name in LEGACY_DIRS:
        legacy_dir = Path(dir_name)
        if legacy_dir.exists() and legacy_dir.is_dir():
            for yaml_file in legacy_dir.rglob("*.yaml"):
                legacy.append(yaml_file)
            for yml_file in legacy_dir.rglob("*.yml"):
                legacy.append(yml_file)

    return legacy


def determine_target_path(source: Path) -> Path:
    """Determine target path for a config file."""
    # Map legacy paths to new structure
    name = source.stem

    # Check if it's a base config
    if "base" in str(source) or name in ["training", "model", "data"]:
        return TARGET_DIR / "base" / source.name

    # Check if it's production
    if "prod" in str(source):
        return TARGET_DIR / "production" / source.name

    # Check if it's development/minimal
    if "minimal" in str(source) or "dev" in str(source):
        return TARGET_DIR / "development" / source.name

    # Check if it's experiment
    if "experiment" in str(source) or "sweep" in str(source):
        return TARGET_DIR / "experiments" / source.name

    # Check if it's evaluation
    if "eval" in str(source):
        return TARGET_DIR / "evaluation" / source.name

    # Default to base
    return TARGET_DIR / "base" / source.name


def migrate_file(source: Path, target: Path, dry_run: bool = True) -> None:
    """Migrate a single config file."""
    if dry_run:
        print(f"  [DRY RUN] {source} -> {target}")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            print(f"  [SKIP] {target} already exists")
        else:
            shutil.copy2(source, target)
            print(f"  [MIGRATED] {source} -> {target}")


def create_hydra_config(dry_run: bool = True) -> None:
    """Create main Hydra config if not exists."""
    hydra_config = TARGET_DIR / "hydra" / "config.yaml"

    if hydra_config.exists():
        print(f"  [SKIP] {hydra_config} already exists")
        return

    config_content = {
        "defaults": [
            "base/training",
            "base/model",
            "base/data",
            "_self_",
        ],
        "hydra": {
            "searchpath": ["pkg://configs", "file://configs"],
            "run": {
                "dir": "outputs/${now:%Y-%m-%d}/${now:%H-%M-%S}",
            },
            "sweep": {
                "dir": "multirun/${now:%Y-%m-%d}/${now:%H-%M-%S}",
                "subdir": "${hydra.job.num}",
            },
        },
        "env": "development",
    }

    if dry_run:
        print(f"  [DRY RUN] Would create {hydra_config}")
    else:
        hydra_config.parent.mkdir(parents=True, exist_ok=True)
        with open(hydra_config, "w") as f:
            yaml.dump(config_content, f, default_flow_style=False, sort_keys=False)
        print(f"  [CREATED] {hydra_config}")


def create_init_file(dry_run: bool = True) -> None:
    """Create __init__.py to make configs a package."""
    init_file = TARGET_DIR / "__init__.py"

    if init_file.exists():
        print(f"  [SKIP] {init_file} already exists")
        return

    content = '''"""
Unified configuration package for Codex ML.

This package contains all configuration files organized by purpose:
- base/: Base configurations and defaults
- production/: Production overrides
- development/: Development overrides
- experiments/: Experiment-specific configs
- hydra/: Hydra-specific configurations
"""
'''

    if dry_run:
        print(f"  [DRY RUN] Would create {init_file}")
    else:
        with open(init_file, "w") as f:
            f.write(content)
        print(f"  [CREATED] {init_file}")


def main():
    parser = argparse.ArgumentParser(description="Migrate configs")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--execute", action="store_true", help="Execute migration")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Specify --dry-run or --execute")
        return

    dry_run = args.dry_run

    print("=" * 70)
    print("CONFIG CONSOLIDATION MIGRATION")
    print("=" * 70)

    print("\n1. Finding legacy configs...")
    legacy_files = find_legacy_configs()
    print(f"   Found {len(legacy_files)} config files in legacy directories")

    if legacy_files:
        print("\n2. Migrating files...")
        for source in legacy_files:
            target = determine_target_path(source)
            migrate_file(source, target, dry_run)
    else:
        print("\n2. No legacy files to migrate")

    print("\n3. Creating __init__.py...")
    create_init_file(dry_run)

    print("\n4. Creating Hydra config...")
    create_hydra_config(dry_run)

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE!")
    print("=" * 70)

    if dry_run:
        print("\nRun with --execute to apply changes")
    else:
        print("\nMigration applied successfully!")
        print("\nNext steps:")
        print("  1. Review the migrated configs")
        print("  2. Update any import paths in your code")
        print("  3. Test with: python -m codex_ml.config")
        print("  4. Consider removing legacy directories once verified")


if __name__ == "__main__":
    main()
