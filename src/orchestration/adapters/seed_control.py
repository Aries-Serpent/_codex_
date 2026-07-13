"""Seed Control System — Deterministic seed propagation across RNG systems.

Propagates a single seed to all random number generation systems
(random, numpy, torch) for fully deterministic execution.

SECURITY NOTE: Uses Python's `random` module for deterministic seeding,
not for cryptographic purposes. For cryptographic randomness, use
`secrets` or `os.urandom()`. This module is safe for:
  - Testing and validation
  - Reproducible machine learning experiments
  - Deterministic simulation environments
NOT suitable for:
  - Cryptographic key generation
  - Security token generation
  - Anything requiring cryptographic randomness
"""

import random  # noqa: S311  # Used for deterministic testing, not cryptography
from typing import Optional

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class SeedControlError(Exception):
    """Raised when seed control operations fail."""

    pass


class SeedControlSystem:
    """Manages deterministic seed propagation across all RNG systems."""

    MIN_SEED = 0
    MAX_SEED = 2**31 - 1

    @classmethod
    def validate_seed(cls, seed: int) -> bool:
        """Validate that seed is in valid range.

        Args:
            seed: Integer seed to validate

        Returns:
            True if seed is valid

        Raises:
            SeedControlError: If seed is invalid
        """
        if not isinstance(seed, int):
            raise SeedControlError(f"Seed must be integer, got {type(seed)}")

        if seed < cls.MIN_SEED or seed > cls.MAX_SEED:
            raise SeedControlError(
                f"Seed must be in range [{cls.MIN_SEED}, {cls.MAX_SEED}], "
                f"got {seed}"
            )

        return True

    @classmethod
    def set_seed(cls, seed: int, numpy_enabled: bool = True) -> None:
        """Set seed for all available RNG systems.

        Args:
            seed: Integer seed (0 to 2^31-1)
            numpy_enabled: Whether to set numpy seed (default: True)

        Raises:
            SeedControlError: If seed is invalid or setting fails
        """
        cls.validate_seed(seed)

        try:
            # Set Python random seed
            random.seed(seed)

            # Set numpy seed if available
            if numpy_enabled and HAS_NUMPY:
                np.random.seed(seed)
                # Also set numpy's new Generator API
                try:
                    np.random.default_rng(seed)
                except Exception:  # pragma: no cover  # noqa: B110
                    # Ignore failures for numpy Generator API (optional optimization)
                    pass

            # Set PyTorch seeds if available
            if HAS_TORCH:
                torch.manual_seed(seed)
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                # Disable benchmark to ensure reproducibility
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False

        except Exception as e:
            raise SeedControlError(f"Failed to set seed: {e}")

    @classmethod
    def get_seed_documentation(cls, seed: int) -> dict:
        """Get documentation for seed used in lane manifest.

        Args:
            seed: The seed value

        Returns:
            Dictionary with seed metadata for manifest
        """
        return {
            "seed": seed,
            "range": [cls.MIN_SEED, cls.MAX_SEED],
            "systems": {
                "random": True,
                "numpy": HAS_NUMPY,
                "torch": HAS_TORCH,
            },
        }


def set_deterministic_seed(seed: int) -> None:
    """Convenience function to set deterministic seed globally.

    Args:
        seed: Integer seed (0 to 2^31-1)

    Raises:
        SeedControlError: If seed is invalid
    """
    SeedControlSystem.set_seed(seed)
