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
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import pickle
import platform
import random
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Prefer provenance utilities when available
try:
    from codex_ml.utils.provenance import (
        environment_summary as _prov_env_summary,  # type: ignore
    )
except Exception:  # pragma: no cover - provenance optional
    _prov_env_summary = None  # type: ignore[assignment]

try:
    from codex_ml.utils.provenance import (
        _git_commit as _prov_git_commit,  # type: ignore
    )
except Exception:  # pragma: no cover - provenance optional
    _prov_git_commit = None  # type: ignore[assignment]

try:  # pragma: no cover - optional codex_digest dependency
    from codex_digest.error_capture import log_error as capture_error
except Exception:  # pragma: no cover - fallback no-op

    def capture_error(
        step_no: str,
        step_desc: str,
        msg: str,
        ctx: str,
        *,
        errors_path: Path | None = None,
    ) -> str:
        return ""


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

from .checkpoint_event import maybe_emit_checkpoint_saved_event


def load_checkpoint(path: str | Path, map_location: str | None = "cpu") -> Any:
    """Load a checkpoint file in a PyTorch-compatible way.

    PyTorch 2.6 introduced ``weights_only=True`` as the default for
    ``torch.load`` which breaks older pickled checkpoints.  This wrapper
    disables the flag when supported while remaining compatible with older
    torch versions that lack the ``weights_only`` parameter.
    """

    import inspect

    import torch

    kwargs = {"map_location": map_location}
    if "weights_only" in inspect.signature(torch.load).parameters:
        kwargs["weights_only"] = False
    return torch.load(path, **kwargs)


def _write_checksum_manifest(path: Path) -> None:
    """Write SHA256 checksum and size for path into checksums.json."""
    meta = {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }
    (path.parent / "checksums.json").write_text(json.dumps(meta), encoding="utf-8")


def _verify_checksum_manifest(directory: Path) -> None:
    """Verify checksum manifest in directory if present."""
    manifest = directory / "checksums.json"
    if not manifest.exists():
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    target = directory / data.get("file", "")
    if not target.exists():
        raise RuntimeError("checkpoint file missing during checksum verify")
    sha = hashlib.sha256(target.read_bytes()).hexdigest()
    if sha != data.get("sha256") or target.stat().st_size != data.get("bytes"):
        raise RuntimeError("checkpoint checksum mismatch")


def _fallback_git_commit() -> Optional[str]:
    """Return current Git commit hash if available (fallback to subprocess)."""
    try:
        repo_root = Path(__file__).resolve().parents[3]
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
        ).strip()
    except Exception:
        return None


def _safe_git_commit() -> Optional[str]:
    """Try provenance _git_commit then fallback to subprocess."""
    try:
        if callable(_prov_git_commit):  # type: ignore[truthy-bool]
            return _prov_git_commit()  # type: ignore[misc]
    except Exception:
        pass
    return _fallback_git_commit()


def _minimal_env_summary() -> Dict[str, Optional[str]]:
    """Collect minimal environment information (lightweight, no heavy deps)."""
    info: Dict[str, Optional[str]] = {
        "python": sys.version,
        "platform": platform.platform(),
    }
    if TORCH_AVAILABLE:
        try:
            info["torch"] = getattr(torch, "__version__", None)
            info["cuda"] = (
                torch.version.cuda if hasattr(torch, "version") and torch.cuda.is_available() else None  # type: ignore[attr-defined]
            )
        except Exception:
            info["torch"] = (
                getattr(torch, "__version__", None) if hasattr(torch, "__version__") else None
            )
    if NUMPY_AVAILABLE:
        try:
            info["numpy"] = getattr(np, "__version__", None)
        except Exception:
            info["numpy"] = None
    gc = _safe_git_commit()
    if gc:
        info["git_commit"] = gc
    return info


def _safe_environment_summary() -> Dict[str, Any]:
    """Attempt to collect rich environment summary; fallback to minimal if needed."""
    try:
        if callable(_prov_env_summary):  # type: ignore[truthy-bool]
            env = _prov_env_summary()  # type: ignore[misc]
            if isinstance(env, dict):
                # Ensure git_commit present if known
                gc = env.get("git_commit") or _safe_git_commit()
                if gc:
                    env.setdefault("git_commit", gc)
                return env
    except Exception:
        pass
    # Fallback to minimal snapshot
    return _minimal_env_summary()


def save_checkpoint(
    path: str, model, optimizer, scheduler, epoch: int, extra: Dict[str, Any] | None = None
) -> None:
    """Save PyTorch checkpoint with integrity and provenance information."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not TORCH_AVAILABLE:
        raise RuntimeError("torch is required to save checkpoints")
    env = _safe_environment_summary()
    payload_extra = dict(extra or {})
    # Provide rich environment summary and git commit for reproducibility
    payload_extra.setdefault("system", env)
    if env.get("git_commit"):
        payload_extra.setdefault("git_commit", env["git_commit"])
    torch.save(
        {
            "model": model.state_dict() if model is not None else None,
            "optimizer": optimizer.state_dict() if optimizer else None,
            "scheduler": scheduler.state_dict() if scheduler else None,
            "epoch": epoch,
            "extra": payload_extra,
        },
        p,
    )
    # Write integrity and provenance metadata
    _write_checksum_manifest(p)
    # Persist provenance alongside the checkpoint for reproducibility (best effort)
    try:
        sidecar = {"epoch": epoch, "git_commit": env.get("git_commit"), "system": env}
        p.with_suffix(".meta.json").write_text(
            json.dumps(sidecar, indent=2, sort_keys=True), encoding="utf-8"
        )
    except Exception:
        pass
    # Emit JSON event for log scrapers (opt-in, never raises)
    try:
        h = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        maybe_emit_checkpoint_saved_event(
            str(p), sha256=h.hexdigest(), num_bytes=p.stat().st_size, extra={"epoch": epoch}
        )
    except Exception:
        pass


def load_training_checkpoint(
    path: str,
    model=None,
    optimizer=None,
    scheduler=None,
    map_location: str = "cpu",
) -> tuple[int | None, Dict[str, Any]]:
    """Load a checkpoint produced by :func:`save_checkpoint`.

    This higher-level helper restores state into the provided ``model``,
    ``optimizer`` and ``scheduler`` objects when present and returns the saved
    epoch and extra metadata.
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("torch is required to load checkpoints")
    p = Path(path)
    # Best-effort integrity verification
    with contextlib.suppress(Exception):
        _verify_checksum_manifest(p.parent)
    data: Dict[str, Any] = load_checkpoint(p, map_location=map_location)
    if model is not None and data.get("model") is not None:
        with contextlib.suppress(Exception):
            model.load_state_dict(data["model"])
    if optimizer is not None and data.get("optimizer") is not None:
        with contextlib.suppress(Exception):
            optimizer.load_state_dict(data["optimizer"])
    if scheduler is not None and data.get("scheduler") is not None:
        with contextlib.suppress(Exception):
            scheduler.load_state_dict(data["scheduler"])
    return data.get("epoch"), data.get("extra", {})


def verify_ckpt_integrity(path: str) -> None:
    """Verify checkpoint integrity using checksums.json when present."""
    p = Path(path)
    meta_p = p.parent / "checksums.json"
    if not meta_p.exists():
        return
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta.get("file") != p.name:
        return
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if sha != meta.get("sha256"):
        raise RuntimeError(f"Checkpoint checksum mismatch for {p.name}")


def build_payload_bytes(
    model: Any,
    optimizer: Any | None = None,
    scheduler: Any | None = None,
    scaler: Any | None = None,
    *,
    rng_state: bool = False,
) -> bytes:
    """Serialize training state to bytes for atomic checkpoint writes."""
    if not TORCH_AVAILABLE:  # pragma: no cover - torch optional
        raise RuntimeError("torch is required to build checkpoint payloads")
    state: Dict[str, Any] = {
        "model": model.state_dict() if model is not None else None,
        "optimizer": optimizer.state_dict() if optimizer is not None else None,
        "scheduler": (
            scheduler.state_dict()
            if scheduler is not None and hasattr(scheduler, "state_dict")
            else None
        ),
    }
    if scaler is not None and hasattr(scaler, "state_dict"):
        state["scaler"] = scaler.state_dict()
    if rng_state:
        state["rng"] = _rng_dump()
    buf = io.BytesIO()
    torch.save(state, buf)
    return buf.getvalue()


def load_payload(
    path: str,
    model: Any,
    optimizer: Any | None = None,
    scheduler: Any | None = None,
    scaler: Any | None = None,
) -> Dict[str, Any]:
    """Load training state from path into provided objects."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("torch is required to load checkpoints")
    state: Dict[str, Any] = load_checkpoint(path, map_location="cpu")
    if model is not None and state.get("model") is not None:
        model.load_state_dict(state["model"])
    if optimizer is not None and state.get("optimizer"):
        optimizer.load_state_dict(state["optimizer"])
    if scheduler is not None and state.get("scheduler"):
        with contextlib.suppress(Exception):
            scheduler.load_state_dict(state["scheduler"])
    if scaler is not None and state.get("scaler"):
        with contextlib.suppress(Exception):
            scaler.load_state_dict(state["scaler"])
    if state.get("rng"):
        _rng_load(state["rng"])
    return state


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rng_dump() -> Dict[str, Any]:
    py_state = random.getstate()
    state: Dict[str, Any] = {"python": [py_state[0], list(py_state[1]), py_state[2]]}
    if NUMPY_AVAILABLE:  # pragma: no branch
        np_state = np.random.get_state()  # type: ignore[no-untyped-call]
        state["numpy"] = [
            np_state[0],  # type: ignore[index]
            np_state[1].tolist(),  # type: ignore[index]
            np_state[2],  # type: ignore[index]
            np_state[3],  # type: ignore[index]
            np_state[4],  # type: ignore[index]
        ]
    if TORCH_AVAILABLE:
        state["torch"] = {"cpu": torch.random.get_rng_state().tolist()}
        if hasattr(torch, "cuda") and torch.cuda.is_available():  # pragma: no cover - cuda optional
            state["torch"]["cuda"] = [s.tolist() for s in torch.cuda.get_rng_state_all()]
    return state


def _rng_load(state: Dict[str, Any]) -> None:
    if "python" in state:
        py_state = state["python"]
        random.setstate((py_state[0], tuple(py_state[1]), py_state[2]))
    if NUMPY_AVAILABLE and "numpy" in state:
        np_state = state["numpy"]
        np.random.set_state(
            (
                np_state[0],
                np.array(np_state[1], dtype=np.uint32),
                np_state[2],
                np_state[3],
                np_state[4],
            )
        )
    if TORCH_AVAILABLE and "torch" in state:
        torch.random.set_rng_state(torch.tensor(state["torch"]["cpu"], dtype=torch.uint8))
        if (
            "cuda" in state["torch"] and hasattr(torch, "cuda") and torch.cuda.is_available()
        ):  # pragma: no cover
            torch.cuda.set_rng_state_all(
                [torch.tensor(s, dtype=torch.uint8) for s in state["torch"]["cuda"]]
            )


def dump_rng_state() -> Dict[str, Any]:
    """Public wrapper around internal RNG snapshot."""
    return _rng_dump()


def load_rng_state(state: Dict[str, Any]) -> None:
    """Restore RNG state saved by dump_rng_state."""
    _rng_load(state)


def set_seed(seed: int, out_dir: Optional[Path | str] = None) -> Dict[str, int]:
    """Set RNG seeds across libraries and optionally persist seeds.json."""
    random.seed(seed)
    seeds: Dict[str, int] = {"python": seed}
    if NUMPY_AVAILABLE:
        np.random.seed(seed)
        seeds["numpy"] = seed
    if TORCH_AVAILABLE:
        torch.manual_seed(seed)
        if hasattr(torch, "cuda") and torch.cuda.is_available():  # pragma: no cover - cuda optional
            torch.cuda.manual_seed_all(seed)
        seeds["torch"] = seed
    if out_dir is not None:
        path = Path(out_dir) / "seeds.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(path, seeds)
    return seeds


def save_ckpt(state: Dict[str, Any], path: str) -> None:
    """Legacy checkpoint saver for state dicts with checksum metadata."""
    if not TORCH_AVAILABLE:
        raise RuntimeError("torch is required to save checkpoints")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    torch.save(state, p)
    _write_checksum_manifest(p)


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

        env = _safe_environment_summary()
        _write_json(
            ep_dir / "meta.json",
            {"epoch": epoch, "metrics": metrics or {}, "git_commit": env.get("git_commit")},
        )
        _write_json(ep_dir / "rng.json", _rng_dump())
        _write_json(ep_dir / "system.json", env)
        if config is not None:
            try:  # prefer YAML
                import yaml  # type: ignore[import-untyped]

                (ep_dir / "config.yaml").write_text(yaml.dump(config), encoding="utf-8")
            except Exception:
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

        if tokenizer is not None:  # pragma: no cover
            with contextlib.suppress(Exception):
                if hasattr(tokenizer, "save_pretrained"):
                    tokenizer.save_pretrained(str(ep_dir / "tokenizer"))
                else:
                    with open(ep_dir / "tokenizer.pkl", "wb") as fh:
                        pickle.dump(tokenizer, fh)

        state_file = ep_dir / ("state.pt" if (ep_dir / "state.pt").exists() else "state.pkl")
        _write_checksum_manifest(state_file)

        # last marker
        (self.root / "last").write_text(str(ep_dir), encoding="utf-8")

        # best tracking
        if metrics:
            best_file = self.root / "best.json"
            best: list[Dict[str, Any]] = []
            if best_file.exists():
                best = _read_json(best_file).get("items", [])
            entry = {"epoch": epoch, "metrics": metrics or {}, "path": str(ep_dir)}
            best.append(entry)

            def keyfn(x: Dict[str, Any]) -> tuple:
                m = x.get("metrics", {})
                if "val_loss" in m:
                    return (0, m["val_loss"])  # lower is better
                if "score" in m:
                    return (1, -m["score"])  # higher is better
                return (2, -x["epoch"])  # fallback to latest

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
        if not path.exists():  # pragma: no cover
            raise FileNotFoundError(f"resume path not found: {path}")

        _verify_checksum_manifest(path)
        state = None
        if (path / "state.pt").exists() and TORCH_AVAILABLE:
            state = load_checkpoint(path / "state.pt", map_location="cpu")
            if model is not None and state.get("model") is not None:
                self._verify_state_dict(model.state_dict(), state["model"])
                model.load_state_dict(state["model"])
            if optimizer is not None and state.get("optimizer") is not None:
                try:
                    optimizer.load_state_dict(state["optimizer"])
                except Exception as exc:  # pragma: no cover
                    raise ValueError(f"optimizer state load failed: {exc}") from exc
            if scheduler is not None and state.get("scheduler") is not None:
                with contextlib.suppress(Exception):
                    scheduler.load_state_dict(state["scheduler"])
        elif (path / "state.pkl").exists():  # pragma: no cover
            with open(path / "state.pkl", "rb") as fh:
                state = pickle.load(fh)
            if (
                model is not None
                and hasattr(model, "load_state_dict")
                and state.get("model") is not None
            ):
                with contextlib.suppress(Exception):
                    model.load_state_dict(state["model"])
        else:  # pragma: no cover
            raise RuntimeError(f"no compatible state file found under: {path}")

        rng_path = path / "rng.json"
        if rng_path.exists():
            try:
                rng_state = _read_json(rng_path)
                _rng_load(rng_state)
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"failed to restore RNG state: {exc}") from exc

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
    def _verify_state_dict(
        self, model_sd: Dict[str, Any], loaded_sd: Dict[str, Any]
    ) -> None:  # pragma: no cover
        missing, unexpected, mismatched = [], [], []
        for k, v in model_sd.items():
            if k not in loaded_sd:
                missing.append(k)
            else:
                lv = loaded_sd[k]
                if (
                    hasattr(v, "shape")
                    and hasattr(lv, "shape")
                    and tuple(v.shape) != tuple(lv.shape)
                ):
                    mismatched.append((k, tuple(v.shape), tuple(lv.shape)))
        for k in loaded_sd.keys():
            if k not in model_sd:
                unexpected.append(k)
        if missing or unexpected or mismatched:
            msgs = []
            if missing:
                msgs.append(f"missing: {missing[:10]}{' ...' if len(missing) > 10 else ''}")
            if unexpected:
                msgs.append(
                    f"unexpected: {unexpected[:10]}{' ...' if len(unexpected) > 10 else ''}"
                )
            if mismatched:
                sample = [(k, exp, lv) for (k, exp, lv) in mismatched[:5]]
                msgs.append(f"mismatched: {sample}{' ...' if len(mismatched) > 5 else ''}")
            raise ValueError("state_dict verification failed: " + "; ".join(msgs))


__all__ = [
    "CheckpointManager",
    "save_checkpoint",
    "save_ckpt",
    "load_checkpoint",
    "load_training_checkpoint",
    "verify_ckpt_integrity",
    "build_payload_bytes",
    "load_payload",
    "dump_rng_state",
    "load_rng_state",
    "set_seed",
]
