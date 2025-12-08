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
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    import torch  # type: ignore

    # Check if torch actually has the functionality we need
    TORCH_AVAILABLE = hasattr(torch, "manual_seed")
except (ImportError, AttributeError):
    # AttributeError can occur from sitecustomize.py
    torch = None  # type: ignore
    TORCH_AVAILABLE = False


@dataclass
class SeedState:
    """Captured seed state for reproducibility."""

    seed: int
    python_hash_seed: str
    numpy_seed: Optional[int] = None
    torch_seed: Optional[int] = None
    cuda_seed: Optional[int] = None
    cudnn_deterministic: bool = False
    cudnn_benchmark: bool = True


class SeedManager:
    """
    Manage seeds for reproducible experiments.

    Usage:
        seed_mgr = SeedManager(seed=42, deterministic=True)
        seed_mgr.set_all_seeds()

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

    def set_all_seeds(self) -> SeedState:
        """Set all random seeds for reproducibility."""
        # Python random
        random.seed(self.seed)

        # Python hash seed (must be set before interpreter starts ideally)
        python_hash = os.environ.get("PYTHONHASHSEED", str(self.seed))
        os.environ["PYTHONHASHSEED"] = python_hash

        state = SeedState(
            seed=self.seed,
            python_hash_seed=python_hash,
        )

        # NumPy
        if NUMPY_AVAILABLE:
            # Use modern API for better behavior in multi-threaded contexts
            _ = np.random.default_rng(self.seed)  # Creates RNG instance
            # Also set global seed for legacy code compatibility
            np.random.seed(self.seed)
            state.numpy_seed = self.seed
        elif self.warn_on_missing:
            logger.warning("NumPy not available - seed not set")

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
                    torch.use_deterministic_algorithms(True)
            else:
                state.cudnn_deterministic = False
                state.cudnn_benchmark = True

        elif self.warn_on_missing:
            logger.warning("PyTorch not available - seed not set")

        self._state = state
        logger.info(f"Seeds set: {self.seed} (deterministic={self.deterministic})")

        return state

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
            env_info["torch_version"] = torch.__version__
            env_info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                env_info["cuda_version"] = torch.version.cuda

        env_str = json.dumps(env_info, sort_keys=True)
        return hashlib.sha256(env_str.encode()).hexdigest()[:16]


def set_seed(seed: int = 42, deterministic: bool = False) -> SeedState:
    """Convenience function to set all seeds."""
    manager = SeedManager(seed, deterministic)
    return manager.set_all_seeds()


__all__ = ["SeedManager", "SeedState", "set_seed"]
