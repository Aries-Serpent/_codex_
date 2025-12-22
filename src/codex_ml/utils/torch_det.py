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
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        # Torch/NumPy not available or seeding failed
        pass
