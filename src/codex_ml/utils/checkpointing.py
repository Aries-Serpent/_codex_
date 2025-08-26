"""Checkpointing & Resuming Utilities (PyTorch-first, framework-aware).

Standard layout:
  output/checkpoints/epoch-{n}/
    - state.pt (torch) or state.pkl (fallback)
    - meta.json (epoch, metrics)
    - config.yaml/json
    - rng.json
Symlinks/markers:
  output/checkpoints/last -> latest epoch dir
  output/checkpoints/best -> best snapshot(s) tracked in best.json

CLI flags to integrate in a trainer:
  --checkpoint-dir (default output/checkpoints)
  --resume-from PATH
  --keep-last N
  --keep-best K
"""

from __future__ import annotations

import contextlib
import json
import pickle
import random
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional torch dependency
    import torch

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - torch missing
TORCH_AVAILABLE = False

try:  # pragma: no cover - optional numpy dependency
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:  # pragma: no cover - numpy missing
NUMPY_AVAILABLE = False


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rng_dump() -> Dict[str, Any]:
    state: Dict[str, Any] = {"python": random.getstate()}
    if NUMPY_AVAILABLE:
        state["numpy"] = np.random.get_state()
    if TORCH_AVAILABLE:
        state["torch"] = {"cpu": torch.random.get_rng_state().tolist()}
        if torch.cuda.is_available():  # pragma: no cover - cuda optional
            state["torch"]["cuda"] = torch.cuda.get_rng_state_all()
    return state


def _rng_load(state: Dict[str, Any]) -> None:
    if "python" in state:
        random.setstate(tuple(state["python"]))
    if NUMPY_AVAILABLE and "numpy" in state:
        np.random.set_state(tuple(state["numpy"]))
    if TORCH_AVAILABLE and "torch" in state:
        torch.random.set_rng_state(torch.tensor(state["torch"]["cpu"]))
        if "cuda" in state["torch"] and torch.cuda.is_available():  # pragma: no cover - cuda optional
            torch.cuda.set_rng_state_all(state["torch"]["cuda"])


def set_seed(seed: int, out_dir: Optional[Path | str] = None) -> Dict[str, int]:
    """Set RNG seeds across libraries and optionally persist ``seeds.json``."""
    random.seed(seed)
    seeds: Dict[str, int] = {"python": seed}
    if NUMPY_AVAILABLE:
        np.random.seed(seed)
        seeds["numpy"] = seed
    if TORCH_AVAILABLE:
        torch.manual_seed(seed)
        if torch.cuda.is_available():  # pragma: no cover - cuda optional
            torch.cuda.manual_seed_all(seed)
        seeds["torch"] = seed
    if out_dir is not None:
        path = Path(out_dir) / "seeds.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(path, seeds)
    return seeds


class CheckpointManager:
    """Manage training checkpoints with retention and resume support."""

    def __init__(self, root: Path, keep_last: int = 5, keep_best: int = 1) -> None:
        self.root = Path(root)
        self.keep_last = int(keep_last)
        self.keep_best = int(keep_best)
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    def save(
        self,
        epoch: int,
        model: Any | None = None,
        optimizer: Any | None = None,
        scheduler: Any | None = None,
        tokenizer: Any | None = None,
        *,
        config: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Path:
        ep_dir = self.root / f"epoch-{epoch}"
        ep_dir.mkdir(parents=True, exist_ok=True)

        _write_json(ep_dir / "meta.json", {"epoch": epoch, "metrics": metrics or {}})
        _write_json(ep_dir / "rng.json", _rng_dump())
        if config is not None:
            try:  # prefer YAML
                import yaml

                (ep_dir / "config.yaml").write_text(yaml.dump(config), encoding="utf-8")
            except Exception:  # pragma: no cover - yaml missing
                _write_json(ep_dir / "config.json", config)

        state: Dict[str, Any] = {"model": None, "optimizer": None, "scheduler": None}
        if TORCH_AVAILABLE and model is not None:
            state["model"] = model.state_dict()
            if optimizer is not None:
                state["optimizer"] = optimizer.state_dict()
            if scheduler is not None and hasattr(scheduler, "state_dict"):
                state["scheduler"] = scheduler.state_dict()
            torch.save(state, ep_dir / "state.pt")
        else:  # pragma: no cover - fallback path
            state = {
                "model": getattr(model, "__dict__", None),
                "optimizer": getattr(optimizer, "state_dict", lambda: None)(),
                "scheduler": getattr(scheduler, "state_dict", lambda: None)(),
            }
            with open(ep_dir / "state.pkl", "wb") as fh:
                pickle.dump(state, fh)

        if tokenizer is not None:
            with contextlib.suppress(Exception):
                if hasattr(tokenizer, "save_pretrained"):
                    tokenizer.save_pretrained(str(ep_dir / "tokenizer"))
                else:
                    with open(ep_dir / "tokenizer.pkl", "wb") as fh:
                        pickle.dump(tokenizer, fh)

        # last marker
        (self.root / "last").write_text(str(ep_dir), encoding="utf-8")

        # best tracking
        if metrics:
            best_file = self.root / "best.json"
            best = []
            if best_file.exists():
                best = _read_json(best_file).get("items", [])
            entry = {"epoch": epoch, "metrics": metrics, "path": str(ep_dir)}
            best.append(entry)

            def keyfn(x: Dict[str, Any]) -> tuple:
                m = x.get("metrics", {})
                if "val_loss" in m:
                    return (0, m["val_loss"])  # lower better
                if "score" in m:
                    return (1, -m["score"])  # higher better
                return (2, -x["epoch"])  # latest

            best.sort(key=keyfn)
            _write_json(best_file, {"items": best[: max(1, self.keep_best)]})

        self.apply_retention()
        return ep_dir

    # ------------------------------------------------------------------
    # Resume
    # ------------------------------------------------------------------
    def resume_from(
        self,
        path: Path,
        model: Any | None = None,
        optimizer: Any | None = None,
        scheduler: Any | None = None,
    ) -> Dict[str, Any]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"resume path not found: {path}")

        state = None
        if (path / "state.pt").exists() and TORCH_AVAILABLE:
            state = torch.load(path / "state.pt", map_location="cpu")
            if model is not None and state.get("model") is not None:
                self._verify_state_dict(model.state_dict(), state["model"])
                model.load_state_dict(state["model"])
            if optimizer is not None and state.get("optimizer") is not None:
                try:
                    optimizer.load_state_dict(state["optimizer"])
                except Exception as exc:  # noqa: BLE001
                    raise ValueError(f"optimizer state load failed: {exc}") from exc
            if scheduler is not None and state.get("scheduler") is not None:
                with contextlib.suppress(Exception):
                    scheduler.load_state_dict(state["scheduler"])
        elif (path / "state.pkl").exists():  # pragma: no cover - fallback
            with open(path / "state.pkl", "rb") as fh:
                state = pickle.load(fh)
            if model is not None and hasattr(model, "load_state_dict") and state.get("model") is not None:
                with contextlib.suppress(Exception):
                    model.load_state_dict(state["model"])
        else:
            raise RuntimeError(f"no compatible state file found under: {path}")

        with contextlib.suppress(Exception):
            rng_state = _read_json(path / "rng.json")
            _rng_load(rng_state)

        meta = _read_json(path / "meta.json") if (path / "meta.json").exists() else {}
        return {"meta": meta, "state": bool(state)}

    # ------------------------------------------------------------------
    # Retention
    # ------------------------------------------------------------------
    def apply_retention(self) -> None:
        entries = [p for p in self.root.glob("epoch-*") if p.is_dir()]
        entries.sort(key=lambda p: int(p.name.split("-")[-1]), reverse=True)
        keep = {e.name for e in entries[: max(1, self.keep_last)]}
        best_file = self.root / "best.json"
        if best_file.exists():
            for item in _read_json(best_file).get("items", []):
                keep.add(Path(item["path"]).name)
        for e in entries:
            if e.name not in keep:
                with contextlib.suppress(Exception):
                    shutil.rmtree(e)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    def _verify_state_dict(self, model_sd: Dict[str, Any], loaded_sd: Dict[str, Any]) -> None:
        missing, unexpected, mismatched = [], [], []
        for k, v in model_sd.items():
            if k not in loaded_sd:
                missing.append(k)
            else:
                lv = loaded_sd[k]
                if hasattr(v, "shape") and hasattr(lv, "shape") and tuple(v.shape) != tuple(lv.shape):
                    mismatched.append((k, tuple(v.shape), tuple(lv.shape)))
        for k in loaded_sd.keys():
            if k not in model_sd:
                unexpected.append(k)
        if missing or unexpected or mismatched:
            msgs = []
            if missing:
                msgs.append(f"missing: {missing[:10]}{' ...' if len(missing) > 10 else ''}")
            if unexpected:
                msgs.append(f"unexpected: {unexpected[:10]}{' ...' if len(unexpected) > 10 else ''}")
            if mismatched:
                msgs.append(f"mismatched: {mismatched[:5]}{' ...' if len(mismatched) > 5 else ''}")
            raise ValueError("state_dict verification failed: " + "; ".join(msgs))


__all__ = ["CheckpointManager"]
