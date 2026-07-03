"""
Determinism Bootstrap for Test Harness.

This module ensures deterministic behavior across all test runs by:
1. Setting fixed random seeds for Python, NumPy, PyTorch, TensorFlow
2. Configuring deterministic algorithms where available
3. Enforcing reproducible hash seeds via environment variables

Import this module early in test setup (e.g., in conftest.py) to ensure
all tests execute with deterministic behavior.
"""

import os
import random
import sys

from codex.logging.structured_logger import logger

# Set Python hash seed (should already be set via env, but enforce it)
os.environ.setdefault("PYTHONHASHSEED", "0")

# Set fixed random seed for Python's random module
random.seed(0)

# Try to set NumPy seed if available
try:
    import numpy as np

    np.random.seed(0)
    print("✓ NumPy determinism enabled (seed=0)", file=sys.stderr)
except ImportError:
    _ = None  # suppressed: no action needed

# Try to configure PyTorch determinism if available
try:
    import torch

    torch.manual_seed(0)
    # Use deterministic algorithms where possible
    torch.use_deterministic_algorithms(True, warn_only=True)
    # Set CUDA determinism if available
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(0)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    print("✓ PyTorch determinism enabled (seed=0)", file=sys.stderr)
except ImportError:
    # PyTorch not installed in this environment (expected in CPU-only test runs)
    pass
except AttributeError:
    # torch module is installed but torch.use_deterministic_algorithms or CUDA-specific attributes
    # (like torch.backends.cudnn) are unavailable in CPU-only or minimal PyTorch installations
    pass
except (IOError, OSError) as e:
    # Some PyTorch operations may not support deterministic mode
    logger.error(f"⚠ PyTorch determinism partially enabled: {e}")

# Try to configure TensorFlow determinism if available
try:
    import tensorflow as tf

    tf.random.set_seed(0)
    # Enable deterministic ops
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    print("✓ TensorFlow determinism enabled (seed=0)", file=sys.stderr)
except ImportError:
    _ = None  # suppressed: no action needed
except (IOError, OSError) as e:
    logger.error(f"⚠ TensorFlow determinism partially enabled: {e}")

print(
    "✓ Determinism bootstrap complete", file=sys.stderr
)  # intentional: diagnostic output on import via conftest
