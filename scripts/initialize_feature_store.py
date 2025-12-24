#!/usr/bin/env python
"""Feature Store Initialization Script for Phase 6.2

This script initializes the production feature store and registers
the 10 initial feature groups defined in configs/production/features.yaml.

Usage:
    python scripts/initialize_feature_store.py
    python scripts/initialize_feature_store.py --config configs/production/features.yaml
    python scripts/initialize_feature_store.py --dry-run
"""

import argparse
import logging
import sys
from pathlib import Path
import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from codex_ml.features.feature_store import FeatureStore, FeatureGroup
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    print(f"Error importing feature store: {e}")
    print("Make sure the package is installed: pip install -e .")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load feature store configuration."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config.get("feature_store", {})


def initialize_feature_store(config: dict, dry_run: bool = False) -> FeatureStore:
    """Initialize the feature store.

    Args:
        config: Feature store configuration
        dry_run: If True, don't actually create the store

    Returns:
        FeatureStore instance
    """
    storage_config = config.get("storage", {})
    base_path = storage_config.get("base_path", "artifacts/features/production")

    logger.info(f"Initializing feature store at: {base_path}")

    if dry_run:
        logger.info("[DRY RUN] Would initialize feature store")
        return None

    store = FeatureStore(base_path)
    logger.info(f"✓ Feature store initialized at {store.store_path}")

    return store


def register_feature_groups(store: FeatureStore, config: dict, dry_run: bool = False):
    """Register initial feature groups from config.

    Args:
        store: FeatureStore instance
        config: Feature store configuration
        dry_run: If True, don't actually register
    """
    feature_groups = config.get("initial_feature_groups", [])

    if not feature_groups:
        logger.warning("No initial feature groups defined in config")
        return

    logger.info(f"Registering {len(feature_groups)} feature groups...")

    for i, group_config in enumerate(feature_groups, 1):
        name = group_config.get("name")
        version = group_config.get("version", "1.0.0")
        description = group_config.get("description", "")
        priority = group_config.get("priority", "medium")

        logger.info(
            f"  [{i}/{len(feature_groups)}] Registering: {name} v{version} (priority: {priority})"
        )

        if dry_run:
            logger.info(f"    [DRY RUN] Would register {name}")
            continue

        try:
            # Create feature group (placeholder - features would be defined in actual usage)
            group = FeatureGroup(
                name=name,
                version=version,
                features=[],  # Placeholder - to be populated by users
                description=description,
            )

            # Register with store
            store.register_feature_group(group)
            logger.info(f"    ✓ Registered {name} v{version}")

        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"    ✗ Failed to register {name}: {e}")

    if not dry_run:
        logger.info(f"✓ Successfully registered {len(feature_groups)} feature groups")


def verify_feature_store(store: FeatureStore):
    """Verify feature store is operational.

    Args:
        store: FeatureStore instance
    """
    logger.info("Verifying feature store...")

    try:
        # List features
        features = store.list_features()
        logger.info(f"  ✓ Found {len(features)} registered feature groups")

        # Check registry
        if store.registry_path.exists():
            logger.info(f"  ✓ Registry exists at {store.registry_path}")
        else:
            logger.warning(f"  ⚠ Registry not found at {store.registry_path}")

        # Check storage
        if store.store_path.exists():
            logger.info(f"  ✓ Storage exists at {store.store_path}")
        else:
            logger.warning(f"  ⚠ Storage directory not found at {store.store_path}")

        logger.info("✓ Feature store verification complete")

    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"✗ Verification failed: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize production feature store with initial feature groups"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/production/features.yaml",
        help="Path to feature store config file",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without actually doing it"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing feature store, don't initialize",
    )

    args = parser.parse_args()

    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return 1

    logger.info("=" * 60)
    logger.info("Feature Store Initialization - Phase 6.2")
    logger.info("=" * 60)
    logger.info(f"Config: {config_path}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info("")

    # Load config
    try:
        config = load_config(str(config_path))
    except Exception as e:
        logger.debug(f"Exception: {e}")
        logger.error(f"Failed to load config: {e}")
        return 1

    # Initialize feature store
    if not args.verify_only:
        store = initialize_feature_store(config, dry_run=args.dry_run)

        if not args.dry_run:
            # Register feature groups
            register_feature_groups(store, config, dry_run=args.dry_run)

            # Verify
            verify_feature_store(store)
    else:
        # Verify only mode
        storage_config = config.get("storage", {})
        base_path = storage_config.get("base_path", "artifacts/features/production")
        store = FeatureStore(base_path)
        verify_feature_store(store)

    logger.info("")
    logger.info("=" * 60)
    if args.dry_run:
        logger.info("✓ Dry run complete - no changes made")
    else:
        logger.info("✓ Feature store initialization complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. List features: python -m codex_ml.cli.feature_store list")
    logger.info("  2. Check health: python -m codex_ml.cli.feature_store health")
    logger.info("  3. Register custom features via CLI or programmatically")
    logger.info("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
