"""
Reproducibility seed management for deterministic training.

Ensures:
- Python random seed
- NumPy random seed
- PyTorch random seed (CPU + CUDA)
- CuDNN determinism (optional, affects performance)
- Environment capture for reproduction
"""

import hashlib
import json
import logging
import os
import random
import sys
from dataclasses import asdict, dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    np = None
    NUMPY_AVAILABLE = False

try:
    import torch

    # Check if torch actually has the functionality we need
    TORCH_AVAILABLE = hasattr(torch, "manual_seed")
except (ImportError, AttributeError):
    # AttributeError can occur from sitecustomize.py
    torch = None  # type: ignore[assignment]
    TORCH_AVAILABLE = False


@dataclass
class SeedState:
    """Captured seed state for reproducibility."""

    seed: int
    python_hash_seed: str
    numpy_seed: Optional[int] = None
    numpy_rng_available: bool = False
    torch_seed: Optional[int] = None
    cuda_seed: Optional[int] = None
    cudnn_deterministic: bool = False
    cudnn_benchmark: bool = True


class SeedManager:
    """
    Manage seeds for reproducible experiments.

    Usage:
        seed_mgr = SeedManager(seed=42, deterministic=True)
        state = seed_mgr.set_all_seeds()

        # Use the NumPy RNG for reproducible operations (recommended)
        rng = seed_mgr.get_rng()
        if rng is not None:
            random_data = rng.standard_normal(100)

        # At end of training
        seed_mgr.save_state("seed_state.json")
    """

    def __init__(
        self,
        seed: int = 42,
        deterministic: bool = False,
        warn_on_missing: bool = True,
    ):
        """
        Initialize seed manager.

        Args:
            seed: Base seed value
            deterministic: Enable CuDNN determinism (slower but reproducible)
            warn_on_missing: Warn if libraries not available
        """
        self.seed = seed
        self.deterministic = deterministic
        self.warn_on_missing = warn_on_missing
        self._state: Optional[SeedState] = None
        self._rng: Optional[object] = None

    def set_all_seeds(self) -> SeedState:
        """Set seeds for all supported frameworks.

        Note:
            PYTHONHASHSEED must be set BEFORE interpreter startup to be effective.
            Setting it via os.environ after startup has NO effect on hash randomization.

        Returns:
            SeedState object containing all seed values and flags
        """
        # Python random
        random.seed(self.seed)

        # Warn about PYTHONHASHSEED limitation (don't set it, just warn)
        if "PYTHONHASHSEED" not in os.environ:
            logger.warning(
                "PYTHONHASHSEED was not set before interpreter startup. "
                "For reproducible Python hash randomization, set it BEFORE running: "
                "PYTHONHASHSEED=%d python your_script.py",
                self.seed,
            )
        # Note: We intentionally do NOT set os.environ["PYTHONHASHSEED"] here
        # because it has no effect after interpreter startup.

        python_hash = os.environ.get("PYTHONHASHSEED", str(self.seed))
        state = SeedState(
            seed=self.seed,
            python_hash_seed=python_hash,
        )

        # NumPy
        if NUMPY_AVAILABLE:
            # Legacy API for backward compatibility
            np.random.seed(self.seed)
            # Note: For modern Generator-based code, use get_rng() method
            state.numpy_seed = self.seed
            state.numpy_rng_available = True
        elif self.warn_on_missing:
            logger.warning("NumPy not available - seed not set")

        # Store RNG for later use (not discarded)
        self._rng = self.get_rng()

        # PyTorch
        if TORCH_AVAILABLE:
            torch.manual_seed(self.seed)
            state.torch_seed = self.seed

            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(self.seed)
                state.cuda_seed = self.seed

            # CuDNN determinism
            if self.deterministic:
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
                state.cudnn_deterministic = True
                state.cudnn_benchmark = False

                # PyTorch 1.8+ deterministic algorithms
                if hasattr(torch, "use_deterministic_algorithms"):
                    try:
                        torch.use_deterministic_algorithms(True)
                    except RuntimeError as e:
                        type(e).__name__
                        logger.debug("RuntimeError: <ERROR_TYPE>")
                        logger.warning(
                            f"torch.use_deterministic_algorithms(True) failed: {e}. "
                            "Some operations may not be fully deterministic."
                        )
            else:
                state.cudnn_deterministic = False
                state.cudnn_benchmark = True

        elif self.warn_on_missing:
            logger.warning("PyTorch not available - seed not set")

        self._state = state
        logger.info(f"Seeds set: {self.seed} (deterministic={self.deterministic})")

        return state

    def get_rng(self) -> Any:
        """Get a reproducible NumPy Generator instance.

        Returns:
            np.random.Generator if NumPy available, else None
        """
        if NUMPY_AVAILABLE:
            return np.random.default_rng(self.seed)
        return None

    def save_state(self, path: str) -> None:
        """Save seed state to JSON file."""
        if self._state is None:
            raise RuntimeError("No seed state - call set_all_seeds() first")

        with open(path, "w") as f:
            json.dump(asdict(self._state), f, indent=2)

    @classmethod
    def load_state(cls, path: str) -> "SeedManager":
        """Load and apply seed state from file."""
        with open(path) as f:
            data = json.load(f)

        manager = cls(
            seed=data["seed"],
            deterministic=data.get("cudnn_deterministic", False),
        )
        manager.set_all_seeds()
        return manager

    def get_environment_hash(self) -> str:
        """Get hash of current environment for reproducibility tracking."""
        env_info = {
            "seed": self.seed,
            "python_version": sys.version,
        }

        if NUMPY_AVAILABLE:
            env_info["numpy_version"] = np.__version__
        if TORCH_AVAILABLE:
            env_info["torch_version"] = getattr(torch, "__version__", "unknown")
            cuda = getattr(torch, "cuda", None)
            cuda_available = bool(
                cuda is not None
                and callable(getattr(cuda, "is_available", None))
                and cuda.is_available()
            )
            env_info["cuda_available"] = cuda_available
            if cuda_available:
                env_info["cuda_version"] = getattr(getattr(torch, "version", None), "cuda", None)

        env_str = json.dumps(env_info, sort_keys=True, default=str)
        return hashlib.sha256(env_str.encode()).hexdigest()[:16]


def set_seed(seed: int = 42, deterministic: bool = False) -> SeedState:
    """Convenience function to set all seeds."""
    manager = SeedManager(seed, deterministic)
    return manager.set_all_seeds()


__all__ = ["SeedManager", "SeedState", "set_seed"]
