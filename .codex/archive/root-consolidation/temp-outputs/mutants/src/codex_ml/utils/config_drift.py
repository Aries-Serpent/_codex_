"""Configuration drift detection for reproducible training.

This module provides utilities for detecting configuration changes that could
affect training reproducibility.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = ["ConfigDrift", "detect_config_drift", "embed_config_hash"]


class ConfigDrift:
    """Detects and tracks configuration drift.

    Configuration drift occurs when training config changes between runs,
    potentially affecting reproducibility.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize config drift detector.

        Args:
            config: Configuration dictionary to track
        """
        self.config = config
        self._hash: Optional[str] = None

    def compute_hash(self) -> str:
        """Compute SHA256 hash of configuration.

        Returns:
            Hexadecimal digest of config
        """
        if self._hash is not None:
            return self._hash

        # Serialize config to JSON with sorted keys for deterministic hashing
        config_json = json.dumps(self.config, sort_keys=True, separators=(",", ":"))
        self._hash = hashlib.sha256(config_json.encode("utf-8")).hexdigest()
        return self._hash

    def save_baseline(self, path: Path | str) -> Path:
        """Save configuration baseline for future comparison.

        Args:
            path: Path where baseline will be saved

        Returns:
            Path to saved baseline file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        baseline = {
            "config": self.config,
            "config_hash": self.compute_hash(),
            "baseline_version": "1.0",
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, sort_keys=True)

        logger.info(f"Saved config baseline: {path}")
        return path

    @classmethod
    def load_baseline(cls, path: Path | str) -> ConfigDrift:
        """Load configuration baseline from file.

        Args:
            path: Path to baseline file

        Returns:
            ConfigDrift instance with loaded config

        Raises:
            FileNotFoundError: If baseline file doesn't exist
            ValueError: If baseline format is invalid
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Baseline not found: {path}")

        with open(path, encoding="utf-8") as f:
            baseline = json.load(f)

        if "config" not in baseline:
            raise ValueError("Invalid baseline format: missing 'config' key")

        return cls(baseline["config"])

    def compare(self, other: ConfigDrift) -> dict[str, list[str]]:
        """Compare this config with another for drift.

        Args:
            other: Another ConfigDrift instance to compare against

        Returns:
            dict with keys 'added', 'removed', 'modified' listing changed keys
        """
        result: dict[str, list[str]] = {"added": [], "removed": [], "modified": []}

        this_keys = set(self.config.keys())
        other_keys = set(other.config.keys())

        # Find added and removed keys
        result["added"] = sorted(this_keys - other_keys)
        result["removed"] = sorted(other_keys - this_keys)

        # Find modified values
        common_keys = this_keys & other_keys
        for key in sorted(common_keys):
            if self.config[key] != other.config[key]:
                result["modified"].append(key)

        return result

    def has_drift(self, baseline_path: Path | str) -> bool:
        """Check if config has drifted from baseline.

        Args:
            baseline_path: Path to baseline file

        Returns:
            True if drift detected, False otherwise
        """
        try:
            baseline = self.load_baseline(baseline_path)
            diff = self.compare(baseline)
            return bool(diff["added"] or diff["removed"] or diff["modified"])
        except FileNotFoundError as e:
            type(e).__name__
            logger.debug("FileNotFoundError: <ERROR_TYPE>")
            logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)
            logger.warning(f"Baseline not found: {baseline_path}")
            return False

    def validate_against_baseline(self, baseline_path: Path | str, strict: bool = False) -> bool:
        """Validate config against baseline, optionally raising on drift.

        Args:
            baseline_path: Path to baseline file
            strict: If True, raises ValueError on drift detection

        Returns:
            True if no drift, False if drift detected

        Raises:
            ValueError: If drift detected and strict=True
        """
        baseline = self.load_baseline(baseline_path)
        diff = self.compare(baseline)

        has_drift = bool(diff["added"] or diff["removed"] or diff["modified"])

        if has_drift:
            msg = (
                f"Configuration drift detected:\n"
                f"  Added: {diff['added']}\n"
                f"  Removed: {diff['removed']}\n"
                f"  Modified: {diff['modified']}"
            )

            if strict:
                raise ValueError(msg)

            logger.warning(msg)
            return False

        logger.info("✓ No configuration drift detected")
        return True


def detect_config_drift(
    current_config: dict[str, Any], baseline_path: Path | str, strict: bool = False
) -> bool:
    """Detect configuration drift (convenience function).

    Args:
        current_config: Current configuration dict
        baseline_path: Path to baseline config file
        strict: If True, raises exception on drift

    Returns:
        True if no drift, False if drift detected
    """
    drift = ConfigDrift(current_config)
    return drift.validate_against_baseline(baseline_path, strict=strict)


def embed_config_hash(config: dict[str, Any], checkpoint_data: dict[str, Any]) -> dict[str, Any]:
    """Embed config hash in checkpoint metadata (convenience function).

    Args:
        config: Configuration dict to hash
        checkpoint_data: Checkpoint data dict to modify

    Returns:
        Modified checkpoint data with embedded config hash
    """
    drift = ConfigDrift(config)

    if "metadata" not in checkpoint_data:
        checkpoint_data["metadata"] = {}

    checkpoint_data["metadata"]["config_hash"] = drift.compute_hash()
    checkpoint_data["metadata"]["config"] = config

    return checkpoint_data
