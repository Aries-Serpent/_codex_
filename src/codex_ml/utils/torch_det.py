def seed_worker(worker_id):
    try:
        import random

        import numpy as np

        import torch

        worker_seed = torch.initial_seed() % 2**32
        np.random.seed(worker_seed)
        random.seed(worker_seed)
    except Exception:
        # Torch/NumPy not available or seeding failed
        pass
