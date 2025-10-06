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
import logging
import hashlib
import inspect
import io
import json
import pickle
import platform
import random
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Dict,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Union,
)

# Prefer provenance utilities when available
try:
    from codex_ml.utils.provenance import (
        environment_summary as _prov_env_summary,  # type: ignore
    )
except Exception:  # pragma: no cover - provenance optional
    _prov_env_summary = None  # type: ignore[assignment]

from codex_ml.utils.seeding import set_reproducible
from .checkpoint_event import maybe_emit_checkpoint_saved_event

logger = logging.getLogger(__name__)

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


class StateDictProvider(Protocol):
    def state_dict(self) -> Mapping[str, Any]: ...

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any: ...


@dataclass
class ModuleStateDictProvider(StateDictProvider):
    module: Any | None

    def state_dict(self) -> Mapping[str, Any]:
        if self.module is None:
            return {}
        state_fn = getattr(self.module, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())  # type: ignore[arg-type]
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.module is None:
            return None
        loader = getattr(self.module, "load_state_dict", None)
        if not callable(loader):
            return None
        try:
            return loader(state_dict, strict=strict)
        except TypeError:
            return loader(state_dict)


@dataclass
class OptimizerStateDictProvider(StateDictProvider):
    optimizer: Any | None

    def state_dict(self) -> Mapping[str, Any]:
        if self.optimizer is None:
            return {}
        state_fn = getattr(self.optimizer, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())  # type: ignore[arg-type]
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.optimizer is None:
            return None
        loader = getattr(self.optimizer, "load_state_dict", None)
        if callable(loader):
            return loader(state_dict)
        return None


@dataclass
class SchedulerStateDictProvider(StateDictProvider):
    scheduler: Any | None

    def state_dict(self) -> Mapping[str, Any]:
        if self.scheduler is None:
            return {}
        state_fn = getattr(self.scheduler, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())  # type: ignore[arg-type]
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.scheduler is None:
            return None
        loader = getattr(self.scheduler, "load_state_dict", None)
        if callable(loader):
            try:
                return loader(state_dict)
            except Exception:
                return None
        return None


@dataclass
class GradScalerStateDictProvider(StateDictProvider):
    scaler: Any | None

    def state_dict(self) -> Mapping[str, Any]:
        if self.scaler is None:
            return {}
        state_fn = getattr(self.scaler, "state_dict", None)
        if callable(state_fn):
            result = state_fn()
            if isinstance(result, Mapping):
                return dict(result)
            if hasattr(result, "items"):
                return dict(result.items())  # type: ignore[arg-type]
        return {}

    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> Any:
        if self.scaler is None:
            return None
        loader = getattr(self.scaler, "load_state_dict", None)
        if callable(loader):
            return loader(state_dict)
        return None


StateMapping = Union[Mapping[str, Any], MutableMapping[str, Any]]


class CheckpointLoadError(RuntimeError):
    """Raised when checkpoint serialization or deserialization fails."""


SaveFormat = Literal["auto", "torch", "pickle"]


def _resolve_format(value: str | None) -> SaveFormat:
    fmt = (value or "auto").lower()
    if fmt not in {"auto", "torch", "pickle"}:
        raise ValueError(f"unsupported checkpoint format: {value}")
    return fmt  # type: ignore[return-value]


def _pickle_dump(path: Path, payload: Mapping[str, Any]) -> None:
    with path.open("wb") as fh:
        pickle.dump(dict(payload), fh, protocol=pickle.HIGHEST_PROTOCOL)


def _torch_dump(path: Path, payload: Mapping[str, Any]) -> None:
    if not TORCH_AVAILABLE:
        raise CheckpointLoadError("torch checkpoint format requested but torch is not available")
    save_kwargs: dict[str, Any] = {}
    try:
        signature = inspect.signature(torch.save)
    except (TypeError, ValueError):  # pragma: no cover - signature may fail on older torch
        signature = None  # type: ignore[assignment]
    if signature and "_use_new_zipfile_serialization" in signature.parameters:
        save_kwargs["_use_new_zipfile_serialization"] = True
    torch.save(dict(payload), path, **save_kwargs)


def _save_payload(path: Path, payload: Mapping[str, Any], *, fmt: SaveFormat) -> None:
    errors: list[BaseException] = []
    if fmt in {"auto", "torch"}:
        try:
            _torch_dump(path, payload)
            return
        except Exception as exc:  # pragma: no cover - torch optional
            errors.append(exc)
            if fmt == "torch":
                raise CheckpointLoadError(f"failed to save torch checkpoint: {exc}") from exc
            fmt = "pickle"
    if fmt == "pickle" or (fmt == "auto" and not TORCH_AVAILABLE):
        try:
            _pickle_dump(path, payload)
            return
        except Exception as exc:
            errors.append(exc)
            raise CheckpointLoadError(f"failed to save checkpoint via pickle: {exc}") from exc
    if errors:
        raise CheckpointLoadError(
            f"failed to save checkpoint; errors encountered: {[type(e).__name__ for e in errors]}"
        )


def _load_payload(path: Path, *, map_location: str | None, fmt: SaveFormat) -> Any:
    errors: list[BaseException] = []
    if fmt in {"auto", "torch"} and TORCH_AVAILABLE:
        try:
            kwargs: dict[str, Any] = {}
            if map_location is not None:
                kwargs["map_location"] = map_location
            if "weights_only" in inspect.signature(torch.load).parameters:
                kwargs["weights_only"] = False
            return torch.load(path, **kwargs)
        except Exception as exc:  # pragma: no cover - torch optional
            errors.append(exc)
            if fmt == "torch":
                raise CheckpointLoadError(f"failed to load torch checkpoint: {exc}") from exc
    if fmt == "torch" and not TORCH_AVAILABLE:
        raise CheckpointLoadError("torch checkpoint format requested but torch is not available")
    try:
        with path.open("rb") as fh:
            return pickle.load(fh)
    except Exception as exc:
        errors.append(exc)
        raise CheckpointLoadError(f"failed to load checkpoint via pickle: {exc}") from exc


def _standardize_state(state: Mapping[str, Any]) -> Dict[str, Any]:
    payload = dict(state)
    if "model_state_dict" not in payload and "model" in payload:
        payload["model_state_dict"] = payload["model"]
    if "optimizer_state_dict" not in payload and "optimizer" in payload:
        payload["optimizer_state_dict"] = payload["optimizer"]
    if "scheduler_state_dict" not in payload and "scheduler" in payload:
        payload["scheduler_state_dict"] = payload["scheduler"]
    if payload.get("extra") is None:
        payload["extra"] = {}
    payload.setdefault("epoch", payload.get("step") or payload.get("epoch"))
    return payload


def _load_into_target(target: Any, state_dict: Mapping[str, Any], *, strict: bool = True) -> None:
    loader = getattr(target, "load_state_dict", None)
    if not callable(loader):
        return
    try:
        loader(state_dict, strict=strict)
    except TypeError:
        loader(state_dict)


def _snapshot_state(source: Any | StateMapping | None) -> Optional[Dict[str, Any]]:
    if source is None:
        return None
    if isinstance(source, Mapping):
        return dict(source)
    if hasattr(source, "state_dict") and callable(source.state_dict):  # type: ignore[attr-defined]
        result = source.state_dict()
        if isinstance(result, Mapping):
            return dict(result)
        return dict(result.items()) if hasattr(result, "items") else dict(result)
    return None


def load_checkpoint(
    path: str | Path, map_location: str | None = "cpu", *, format: str | None = None
) -> Any:
    """Load a checkpoint payload returning the raw serialized state."""

    p = Path(path)
    try:
        return _load_payload(p, map_location=map_location, fmt=_resolve_format(format))
    except CheckpointLoadError:
        raise
    except Exception as exc:  # pragma: no cover - fallback path
        raise CheckpointLoadError(f"failed to load checkpoint from {p}: {exc}") from exc


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
    except Exception as exc:
        logger.info(
            "checkpointing._safe_git_commit: provenance hook failed: %s", exc, exc_info=True
        )
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
                torch.version.cuda
                if hasattr(torch, "version") and torch.cuda.is_available()
                else None  # type: ignore[attr-defined]
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
    except Exception as exc:
        logger.info(
            "checkpointing._safe_environment_summary: provenance summary failed: %s",
            exc,
            exc_info=True,
        )
    # Fallback to minimal snapshot
    return _minimal_env_summary()


def save_checkpoint(
    path: str | Path,
    model: StateDictProvider | None,
    optimizer: Any | StateMapping | None,
    scheduler: Any | StateMapping | None,
    epoch: int,
    extra: Mapping[str, Any] | None = None,
    *,
    format: str | None = None,
) -> None:
    """Save a training checkpoint using ``torch`` when available, ``pickle`` otherwise."""

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    env = _safe_environment_summary()
    payload_extra = dict(extra or {})
    payload_extra.setdefault("system", env)
    if env.get("git_commit"):
        payload_extra.setdefault("git_commit", env["git_commit"])

    state: Dict[str, Any] = {
        "model_state_dict": _snapshot_state(model),
        "optimizer_state_dict": _snapshot_state(optimizer),
        "scheduler_state_dict": _snapshot_state(scheduler),
        "epoch": int(epoch),
        "extra": payload_extra,
    }
    if state["model_state_dict"] is not None:
        state["model"] = state["model_state_dict"]
    if state["optimizer_state_dict"] is not None:
        state["optimizer"] = state["optimizer_state_dict"]
    if state["scheduler_state_dict"] is not None:
        state["scheduler"] = state["scheduler_state_dict"]

    save_format = _resolve_format(format)
    try:
        _save_payload(p, state, fmt=save_format)
    except Exception as exc:  # pragma: no cover - save failures are rare
        raise CheckpointLoadError(f"failed to save checkpoint to {p}: {exc}") from exc

    _write_checksum_manifest(p)

    try:
        sidecar = {"epoch": epoch, "git_commit": env.get("git_commit"), "system": env}
        p.with_suffix(".meta.json").write_text(
            json.dumps(sidecar, indent=2, sort_keys=True), encoding="utf-8"
        )
    except Exception as exc:  # pragma: no cover - metadata best effort
        logger.info(
            "save_checkpoint: unable to write metadata sidecar for %s: %s", p, exc, exc_info=True
        )

    try:
        h = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        maybe_emit_checkpoint_saved_event(
            str(p), sha256=h.hexdigest(), num_bytes=p.stat().st_size, extra={"epoch": epoch}
        )
    except Exception as exc:  # pragma: no cover - telemetry best effort
        logger.info(
            "save_checkpoint: telemetry emission skipped for %s due to %s", p, exc, exc_info=True
        )


def load_training_checkpoint(
    path: str | Path,
    model: Any | None = None,
    optimizer: Any | None = None,
    scheduler: Any | None = None,
    map_location: str = "cpu",
    *,
    strict: bool = True,
    format: str | None = None,
) -> Dict[str, Any]:
    """Load a training checkpoint and optionally restore state into live objects."""

    p = Path(path)
    if not p.exists():
        raise CheckpointLoadError(f"checkpoint does not exist: {p}")

    try:
        _verify_checksum_manifest(p.parent)
    except RuntimeError as exc:
        raise CheckpointLoadError(str(exc)) from exc
    except Exception as exc:  # pragma: no cover - checksum verify is best-effort
        logger.info(
            "load_training_checkpoint: checksum verification skipped for %s: %s",
            p,
            exc,
            exc_info=True,
        )

    try:
        raw = _load_payload(p, map_location=map_location, fmt=_resolve_format(format))
    except CheckpointLoadError:
        raise
    except Exception as exc:  # pragma: no cover - fallback path
        raise CheckpointLoadError(f"failed to load checkpoint from {p}: {exc}") from exc

    if not isinstance(raw, Mapping):
        raise CheckpointLoadError(
            f"checkpoint at {p} is not a mapping payload (found {type(raw).__name__})"
        )

    data = _standardize_state(raw)
    if data.get("model_state_dict") is not None:
        data.setdefault("model", data["model_state_dict"])
    if data.get("optimizer_state_dict") is not None:
        data.setdefault("optimizer", data["optimizer_state_dict"])
    if data.get("scheduler_state_dict") is not None:
        data.setdefault("scheduler", data["scheduler_state_dict"])

    if data.get("epoch") is not None:
        try:
            data["epoch"] = int(data["epoch"])
        except (TypeError, ValueError) as exc:  # pragma: no cover - fallback to raw value
            logger.info(
                "load_training_checkpoint: epoch value %r could not be coerced to int: %s",
                data.get("epoch"),
                exc,
            )

    if model is not None and data.get("model_state_dict") is not None:
        try:
            _load_into_target(model, data["model_state_dict"], strict=strict)
        except Exception as exc:  # pragma: no cover - strict mismatches
            raise CheckpointLoadError(f"failed to load model state: {exc}") from exc
    if optimizer is not None and data.get("optimizer_state_dict") is not None:
        try:
            _load_into_target(optimizer, data["optimizer_state_dict"], strict=True)
        except Exception as exc:  # pragma: no cover - optimizer mismatch
            raise CheckpointLoadError(f"failed to load optimizer state: {exc}") from exc
    if scheduler is not None and data.get("scheduler_state_dict") is not None:
        try:
            _load_into_target(scheduler, data["scheduler_state_dict"], strict=True)
        except Exception as exc:  # pragma: no cover - scheduler load is best effort
            logger.info(
                "load_training_checkpoint: scheduler state not restored: %s", exc, exc_info=True
            )

    if not isinstance(data.get("extra"), dict):
        data["extra"] = dict(data.get("extra") or {})

    return data


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


def set_seed(
    seed: int,
    out_dir: Optional[Path | str] = None,
    *,
    deterministic: bool | None = None,
) -> Dict[str, int]:
    """Set RNG seeds across libraries and optionally persist seeds.json."""
    if deterministic is None:
        set_reproducible(seed)
    else:
        set_reproducible(seed, deterministic=deterministic)
    seeds: Dict[str, int] = {"python": seed}
    if NUMPY_AVAILABLE:
        seeds["numpy"] = seed
    if TORCH_AVAILABLE:
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

    def load_latest(
        self,
        model: Any | None = None,
        optimizer: Any | None = None,
        scheduler: Any | None = None,
        *,
        search_path: Path | None = None,
        strict: bool = True,
    ) -> Dict[str, Any]:
        """Resume from the most recent checkpoint available.

        Parameters
        ----------
        model, optimizer, scheduler:
            Optional PyTorch objects that will receive the restored
            state_dicts when provided.
        search_path:
            Optional directory to search instead of :attr:`root`. When the
            directory already points to a concrete checkpoint (i.e. contains
            ``state.pt``/``state.pkl``) it is used directly.
        strict:
            When ``True`` (default) a :class:`FileNotFoundError` is raised if
            no checkpoints are discovered.  When ``False`` an empty payload is
            returned instead.

        Returns
        -------
        Dict[str, Any]
            The metadata returned from :meth:`resume_from` with the resolved
            checkpoint ``path`` included.
        """

        def _has_state(directory: Path) -> bool:
            return (directory / "state.pt").exists() or (directory / "state.pkl").exists()

        root = Path(search_path) if search_path is not None else self.root
        if root.is_file():
            root = root.parent

        candidates: list[Path] = []
        seen: set[str] = set()

        def _register(candidate: Path | None) -> None:
            if candidate is None:
                return
            try:
                resolved = str(candidate.resolve())
            except Exception:
                resolved = str(candidate)
            if resolved in seen:
                return
            if not candidate.exists():
                return
            seen.add(resolved)
            candidates.append(candidate)

        if root.is_dir() and _has_state(root):
            _register(root)

        marker = root / "last"
        if marker.exists():
            marker_path: Path | None = None
            if marker.is_symlink():
                with contextlib.suppress(Exception):
                    marker_path = marker.resolve(strict=False)
            else:
                try:
                    marker_value = marker.read_text(encoding="utf-8").strip()
                except IsADirectoryError:
                    with contextlib.suppress(Exception):
                        marker_path = marker.resolve(strict=False)
                except Exception:
                    marker_value = ""
                else:
                    if marker_value:
                        candidate = Path(marker_value)
                        if not candidate.is_absolute():
                            try:
                                candidate = (root / candidate).resolve(strict=False)
                            except Exception:
                                candidate = root / candidate
                        marker_path = candidate
            if marker_path is not None:
                _register(marker_path)

        for candidate in sorted(
            [p for p in root.glob("epoch-*") if p.is_dir()],
            key=lambda p: int(p.name.split("-")[-1]),
            reverse=True,
        ):
            _register(candidate)

        if not candidates:
            if strict:
                raise FileNotFoundError(f"no checkpoints found under: {root}")
            return {"meta": {}, "state": False, "path": None}

        for candidate in candidates:
            if _has_state(candidate):
                info = self.resume_from(
                    candidate,
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                )
                info["path"] = str(candidate)
                return info

        if strict:
            raise FileNotFoundError(f"no checkpoint state files found under: {root}")
        return {"meta": {}, "state": False, "path": None}

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
    "CheckpointLoadError",
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
    "ModuleStateDictProvider",
    "OptimizerStateDictProvider",
    "SchedulerStateDictProvider",
    "GradScalerStateDictProvider",
]
