def set_reproducible(seed: int = 42) -> None:
    """Best-effort reproducibility settings.

    Seeds Python, NumPy and torch (when available) and enables deterministic
    algorithms where supported. cuDNN benchmarking is disabled and a default
    ``CUBLAS_WORKSPACE_CONFIG`` is set when absent.
    """
    import os
    import random

    import numpy as np

    try:
        import torch
    except Exception:  # pragma: no cover - torch missing
        torch = None

    random.seed(seed)
    np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:  # pragma: no cover - older torch
            pass
        try:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        except Exception:  # pragma: no cover - no cudnn
            pass
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")
