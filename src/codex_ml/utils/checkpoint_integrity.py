"""Utilities for attaching integrity metadata to checkpoint artifacts.

The helpers in this module are intentionally lightweight so they can be used
from training scripts, offline verifiers, and tests without pulling in the
heavier checkpoint machinery.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

SNAPSHOT_EXCLUDE_KEYS: set[str] = {
    # Hydra / OmegaConf internals that should not leak into manifests.
    "_target_",
    "_recursive_",
    "_convert_",
    "_partial_",
    # Conventional key used to mark placeholder configuration sections.
    "unused",
}


def sha256_file(path: str | Path, *, chunk_size: int = 1 << 20) -> str:
    """Return the SHA256 digest for *path*.

    The function reads the file in chunks to avoid loading large files entirely
    into memory.
    """

    file_path = Path(path)
    if not file_path.exists():  # pragma: no cover - defensive guard
        raise FileNotFoundError(file_path)

    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def attach_integrity(
    checkpoint_path: str | Path,
    metadata: Mapping[str, Any] | None = None,
    *,
    manifest_path: str | Path | None = None,
    relative_to: str | Path | None = None,
) -> dict[str, Any]:
    """Attach integrity metadata to *checkpoint_path*.

    A ``.sha256`` sidecar is written next to the checkpoint and, when
    ``manifest_path`` is provided, the manifest is updated (creating it if
    required). The returned dictionary can be used by callers for further
    processing or assertions in tests.
    """

    ckpt_path = Path(checkpoint_path)
    if not ckpt_path.exists():  # pragma: no cover - defensive guard
        raise FileNotFoundError(ckpt_path)

    sha = sha256_file(ckpt_path)
    size = ckpt_path.stat().st_size

    # Write sidecar with trailing newline for CLI compatibility.
    sidecar = ckpt_path.with_suffix(ckpt_path.suffix + ".sha256")
    sidecar.write_text(f"{sha}\n", encoding="utf-8")

    entry: dict[str, Any] = {
        "sha256": sha,
        "size": size,
    }

    if metadata:
        entry["metadata"] = dict(metadata)

    base_path = Path(relative_to) if relative_to is not None else None
    if base_path is not None:
        try:
            entry["path"] = str(ckpt_path.resolve().relative_to(base_path.resolve()))
        except Exception:
            entry["path"] = str(ckpt_path)
    else:
        entry["path"] = str(ckpt_path)

    if manifest_path is not None:
        manifest = Path(manifest_path)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        items: list[dict[str, Any]]
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    items = list(data)
                elif isinstance(data, Mapping):
                    items = [dict(data)]
                else:  # pragma: no cover - defensive branch
                    items = []
            except Exception:  # pragma: no cover - tolerate malformed manifests
                items = []
        else:
            items = []
        items.append(entry)
        manifest.write_text(json.dumps(items, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return entry


def snapshot_config(config: Any, *, exclude_keys: Sequence[str] | None = None) -> dict[str, Any]:
    """Return a JSON-friendly snapshot of *config* suitable for manifests.

    ``config`` may be a standard mapping, a dataclass instance, or an OmegaConf
    ``DictConfig``. Complex objects are converted to strings, missing values
    (``"???"``) are dropped, and reserved keys such as ``"unused"`` are
    filtered out.
    """

    if config is None:
        return {}

    exclusions = SNAPSHOT_EXCLUDE_KEYS | set(exclude_keys or ())

    try:  # pragma: no cover - optional dependency
        from omegaconf import DictConfig, ListConfig, OmegaConf  # type: ignore
    except Exception:  # pragma: no cover - optional dependency absent
        omega_conf = None
        omega_conf_types: tuple[type[Any], ...] = ()
    else:
        omega_conf = OmegaConf
        omega_conf_types = (DictConfig, ListConfig)

    def _to_container(value: Any) -> Any:
        if omega_conf is not None and isinstance(value, omega_conf_types):
            try:
                return omega_conf.to_container(value, resolve=True)  # type: ignore[attr-defined]
            except Exception as error:  # pragma: no cover - optional dependency edge
                if error.__class__.__name__ != "MissingMandatoryValue":
                    raise
                return omega_conf.to_container(value, resolve=False)  # type: ignore[attr-defined]
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, Mapping):
            return {k: _to_container(v) for k, v in value.items()}
        if isinstance(value, list | tuple | set):
            return [_to_container(v) for v in value]
        return value

    def _prune(value: Any) -> Any:
        if isinstance(value, Mapping):
            result: dict[str, Any] = {}
            for key, inner in value.items():
                str_key = str(key)
                if str_key in exclusions:
                    continue
                cleaned = _prune(inner)
                if cleaned is None:
                    continue
                result[str_key] = cleaned
            return result
        if isinstance(value, list):
            cleaned_list = [item for item in (_prune(v) for v in value) if item is not None]
            return cleaned_list
        if isinstance(value, tuple):
            cleaned_tuple = tuple(item for item in (_prune(v) for v in value) if item is not None)
            return list(cleaned_tuple)
        if isinstance(value, set):
            cleaned_set = [
                item for item in (_prune(v) for v in sorted(value, key=str)) if item is not None
            ]
            return cleaned_set
        if value is None:
            return None
        if isinstance(value, str):
            if value == "???":
                return None
            return value
        if isinstance(value, int | float | bool):
            return value
        return str(value)

    container = _to_container(config)
    cleaned = _prune(container)
    if not isinstance(cleaned, Mapping):
        return {"value": cleaned}
    return dict(cleaned)


__all__ = ["attach_integrity", "sha256_file", "snapshot_config"]
