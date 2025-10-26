"""Load lightweight training configuration without requiring Hydra."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

try:  # pragma: no cover - omegaconf optional
    from omegaconf import OmegaConf
except Exception:  # pragma: no cover - fallback stub
    OmegaConf = None  # type: ignore[assignment]

_DEFAULT_CFG: dict[str, Any] = {
    "training": {
        "model_name": "sshleifer/tiny-gpt2",
        "texts": ["hello codex"],
        "epochs": 1,
        "batch_size": 2,
        "lr": 5e-4,
        "grad_accum": 1,
        "log_every": 10,
        "checkpoint_dir": "checkpoints",
    }
}


def _apply_overrides(cfg: MutableMapping[str, Any], overrides: Sequence[str] | None) -> None:
    if not overrides:
        return
    for item in overrides:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        target = cfg
        parts = key.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})  # type: ignore[assignment]
        target[parts[-1]] = _coerce_scalar(value)


def _coerce_scalar(raw: str) -> Any:
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def load_training_cfg(
    path: str | Path | None = None,
    *,
    allow_fallback: bool = False,
    overrides: Sequence[str] | None = None,
) -> Any:
    """Load a training configuration, returning an OmegaConf object when available."""

    data: MutableMapping[str, Any] = {}
    if path:
        file_path = Path(path)
        if file_path.exists():
            if file_path.suffix.lower() in {".yml", ".yaml"}:
                from codex_ml.utils.yaml_support import safe_load

                content = safe_load(file_path.read_text(encoding="utf-8"))
                if isinstance(content, Mapping):
                    data.update(content)
            else:
                import json

                data.update(json.loads(file_path.read_text(encoding="utf-8")))
    if not data and allow_fallback:
        data.update(_DEFAULT_CFG)
    _apply_overrides(data, overrides)
    if OmegaConf is not None:
        return OmegaConf.create(data)
    return data


__all__ = ["load_training_cfg"]
