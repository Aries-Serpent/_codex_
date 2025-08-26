from typing import Sequence, Tuple, List
import numpy as np

def train_val_test_split(dataset: Sequence, val_frac: float = 0.1, test_frac: float = 0.1, seed: int = 42) -> Tuple[List, List, List]:
    assert 0 <= val_frac < 1 and 0 <= test_frac < 1 and (val_frac + test_frac) < 1
    rng = np.random.default_rng(seed)
    idxs = np.arange(len(dataset))
    rng.shuffle(idxs)
    n = len(dataset)
    t = int(n * test_frac)
    v = int(n * val_frac)
    test_idx = idxs[:t]
    val_idx = idxs[t:t+v]
    train_idx = idxs[t+v:]
    to_list = lambda arr: [dataset[i] for i in arr.tolist()]
    return to_list(train_idx), to_list(val_idx), to_list(test_idx)
