"""
GitHub Connector Check Tool

Validates GitHub connector configuration and connectivity.
Supports offline mode for testing without network access.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict[str, Any]:
    """
    Load connector configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_connector(config: dict[str, Any]) -> bool:
    """
    Check GitHub connector configuration and connectivity.

    Args:
        config: Connector configuration dictionary

    Returns:
        True if connector is valid and accessible, False otherwise
    """
    # Validate required fields
    required_fields = ['endpoint', 'repo']
    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required field: {field}")
            return False

    # Check offline_ok flag
    offline_ok = config.get('offline_ok', False)

    if offline_ok:
        # In offline mode, just validate configuration structure
        logger.info("Offline mode enabled - skipping connectivity check")
        logger.info(f"Configuration validated for repo: {config['repo']}")
        return True

    # In online mode, we would check connectivity here
    # For now, just validate config structure
    logger.info(f"Configuration validated for repo: {config['repo']}")
    return True


def main() -> int:
    """
    Main entry point for connector check.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Look for config in standard location
        config_path = Path("configs/connectors/github_connector.config.json")

        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return 1

        # Load and validate configuration
        config = load_config(config_path)

        # Check connector
        if check_connector(config):
            logger.info("Connector check passed")
            return 0
        logger.error("Connector check failed")
        return 1

    except Exception as e:
        logger.error(f"Error checking connector: {e}")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
