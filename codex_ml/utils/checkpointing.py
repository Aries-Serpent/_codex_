# BEGIN: CODEX_CKPT_RNG_SEED
from __future__ import annotations

import json
import random
from pathlib import Path


def set_seed(seed: int) -> None:
    try:
        import numpy as np

        np.random.seed(seed)
    except Exception:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
    random.seed(seed)

    # Persist seed for reproducibility
    try:
        path = Path(".codex")
        path.mkdir(exist_ok=True)
        (path / "seeds.json").write_text(json.dumps({"seed": seed}), encoding="utf-8")
    except Exception:
        pass


def save_rng(path: Path) -> None:
    state = {}
    try:
        import numpy as np

        state["numpy"] = np.random.get_state()[1][:].tolist()
    except Exception:
        pass
    try:
        import torch

        state["torch"] = torch.get_rng_state().tolist()
        if torch.cuda.is_available():
            state["torch_cuda"] = torch.cuda.get_rng_state().tolist()
    except Exception:
        pass
    state["python"] = random.getstate()[1][:] if hasattr(random.getstate(), "__iter__") else None
    (path / "rng.json").write_text(json.dumps(state), encoding="utf-8")


def load_rng(path: Path) -> None:
    f = path / "rng.json"
    if not f.exists():
        return
    try:
        state = json.loads(f.read_text(encoding="utf-8"))
        import random as pyrand

        import numpy as np
        import torch

        if "numpy" in state:
            np.random.seed(state["numpy"][0] if state["numpy"] else 0)
        if "torch" in state:
            torch.set_rng_state(torch.tensor(state["torch"], dtype=torch.uint8))
        if "torch_cuda" in state and torch.cuda.is_available():
            torch.cuda.set_rng_state(torch.tensor(state["torch_cuda"], dtype=torch.uint8))
        if "python" in state and state["python"] is not None:
            pyrand.setstate((3, tuple(state["python"]), None))
    except Exception:
        pass


def verify_shapes(model, checkpoint_state: dict) -> None:
    try:
        missing, unexpected = model.load_state_dict(checkpoint_state, strict=False)
        if missing or unexpected:
            raise RuntimeError(f"Shape/state mismatch: missing={missing}, unexpected={unexpected}")
    except Exception as e:
        raise RuntimeError(f"Failed verifying shapes: {e}")


def log_seed(path: Path, seed: int) -> None:
    (path / "seeds.json").write_text(json.dumps({"seed": seed}), encoding="utf-8")


# END: CODEX_CKPT_RNG_SEED
