"""Checkpoint integrity validation with SHA256 checksums.

This module provides utilities for ensuring checkpoint integrity through
cryptographic hashing and validation.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

__all__ = ["CheckpointIntegrity", "add_integrity_hash", "validate_checkpoint"]


class CheckpointIntegrity:
    """Manages checkpoint integrity through SHA256 hashing.

    Attributes:
        checkpoint_path: Path to checkpoint file
        hash_path: Path to integrity hash file (.integrity.json)
    """

    def __init__(self, checkpoint_path: Path | str):
        """Initialize checkpoint integrity validator.

        Args:
            checkpoint_path: Path to checkpoint file
        """
        self.checkpoint_path = Path(checkpoint_path)
        self.hash_path = self.checkpoint_path.with_suffix(
            self.checkpoint_path.suffix + ".integrity.json"
        )

    def compute_hash(self) -> str:
        """Compute SHA256 hash of checkpoint file.

        Returns:
            Hexadecimal digest of checkpoint file

        Raises:
            FileNotFoundError: If checkpoint file doesn't exist
        """
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")

        sha256 = hashlib.sha256()

        with open(self.checkpoint_path, "rb") as f:
            # Read in chunks for memory efficiency
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def save_integrity(self, metadata: Optional[dict] = None) -> Path:
        """Compute and save integrity hash with optional metadata.

        Args:
            metadata: Optional dict with additional metadata

        Returns:
            Path to saved integrity file
        """
        checkpoint_hash = self.compute_hash()

        integrity_data = {
            "checkpoint_path": str(self.checkpoint_path.name),
            "sha256": checkpoint_hash,
            "file_size_bytes": self.checkpoint_path.stat().st_size,
        }

        if metadata:
            integrity_data["metadata"] = metadata

        with open(self.hash_path, "w", encoding="utf-8") as f:
            json.dump(integrity_data, f, indent=2, sort_keys=True)

        logger.info(f"Saved checkpoint integrity: {self.hash_path}")
        return self.hash_path

    def validate(self, strict: bool = True) -> bool:
        """Validate checkpoint integrity against saved hash.

        Args:
            strict: If True, raises exception on validation failure

        Returns:
            True if validation passes, False otherwise

        Raises:
            FileNotFoundError: If integrity file missing (strict mode only)
            ValueError: If hash mismatch (strict mode only)
        """
        if not self.hash_path.exists():
            msg = f"Integrity file not found: {self.hash_path}"
            if strict:
                raise FileNotFoundError(msg)
            logger.warning(msg)
            return False

        # Load saved hash
        with open(self.hash_path, encoding="utf-8") as f:
            integrity_data = json.load(f)

        saved_hash = integrity_data.get("sha256")
        if not saved_hash:
            msg = "Integrity file missing SHA256 hash"
            if strict:
                raise ValueError(msg)
            logger.warning(msg)
            return False

        # Compute current hash
        current_hash = self.compute_hash()

        # Compare hashes
        if current_hash != saved_hash:
            msg = (
                f"Checkpoint integrity validation failed!\n"
                f"  Expected: {saved_hash}\n"
                f"  Got:      {current_hash}\n"
                f"  Checkpoint may be corrupted: {self.checkpoint_path}"
            )
            if strict:
                raise ValueError(msg)
            logger.error(msg)
            return False

        logger.info(f"✓ Checkpoint integrity validated: {self.checkpoint_path}")
        return True

    def get_integrity_info(self) -> Optional[dict]:
        """Get integrity information if available.

        Returns:
            dict with integrity info, or None if not available
        """
        if not self.hash_path.exists():
            return None

        with open(self.hash_path, encoding="utf-8") as f:
            return json.load(f)


def validate_checkpoint(checkpoint_path: Path | str, strict: bool = True) -> bool:
    """Validate checkpoint integrity (convenience function).

    Args:
        checkpoint_path: Path to checkpoint file
        strict: If True, raises exception on validation failure

    Returns:
        True if validation passes
    """
    integrity = CheckpointIntegrity(checkpoint_path)
    return integrity.validate(strict=strict)


def add_integrity_hash(checkpoint_path: Path | str, metadata: Optional[dict] = None) -> Path:
    """Add integrity hash to checkpoint (convenience function).

    Args:
        checkpoint_path: Path to checkpoint file
        metadata: Optional metadata to include

    Returns:
        Path to integrity file
    """
    integrity = CheckpointIntegrity(checkpoint_path)
    return integrity.save_integrity(metadata=metadata)
