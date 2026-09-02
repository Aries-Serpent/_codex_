"""
Torch Det Module

This module provides functionality for torch det.

Usage:
    from utils.torch_det import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging

logger = logging.getLogger(__name__)


def seed_worker(worker_id):
    try:
        import random

        import numpy as np
        import torch

        worker_seed = torch.initial_seed() % 2**32
        np.random.seed(worker_seed)
        random.seed(worker_seed)
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        # Torch/NumPy not available or seeding failed
