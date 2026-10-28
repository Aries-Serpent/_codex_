"""Offline packaging helpers for deployable model artefacts."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import tarfile  # noqa: E402
import tempfile  # noqa: E402
from collections.abc import Iterable, Mapping  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402
from uuid import uuid4  # noqa: E402

from codex_ml.plugins.registry import Registry  # noqa: E402
from codex_ml.security.runtime import (  # noqa: E402
    load_secret,
    scan_prompt_for_unsafe_content,
)

deployment_registry = Registry("deployment")


def build_service_package(
    model_dir: str | Path,
    output_path: str | Path,
    *,
    metadata: Mapping[str, Any] | None = None,
    prompt: str | None = None,
    secret_names: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Materialise a tarball describing a deployable service package.

    The function is intentionally offline and side-effect free apart from writing
    the package artefact. It supports pluggable hooks via ``deployment_registry``
    to allow extensions (e.g., signing, additional manifests).
    """

    model_root = Path(model_dir).expanduser().resolve()
    if not model_root.exists():
        raise FileNotFoundError(model_root)

    if prompt:
        scan_prompt_for_unsafe_content(prompt)

    gathered_secrets: dict[str, str] = {}
    for name in secret_names or ():
        gathered_secrets[name] = load_secret(name)

    run_id = metadata.get("run_id") if isinstance(metadata, Mapping) else None
    run_id = str(run_id) if run_id else f"deploy-{uuid4().hex}"

    staging = Path(tempfile.mkdtemp(prefix="codex-package-"))
    manifest = {
        "run_id": run_id,
        "model_dir": str(model_root),
        "files": sorted(p.name for p in model_root.glob("*")),
        "metadata": dict(metadata or {}),
        # Secrets stored only as SHA256 hashes, not raw values  # noqa: E501
        "secrets": [
            hashlib.sha256(k.encode()).hexdigest()[:16] for k in gathered_secrets
        ],  # nosec - hashed identifiers only — no secret values stored
    }
    manifest_path = staging / "manifest.json"
    # Manifest stores only hashed secret identifiers
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )  # File contains only hashed secrets

    pointer_path = staging / "model_pointer.txt"
    pointer_path.write_text(str(model_root), encoding="utf-8")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_destination = output.with_suffix(output.suffix + ".manifest.json")
    with tarfile.open(output, "w:gz") as tar:
        tar.add(manifest_path, arcname="manifest.json")
        tar.add(pointer_path, arcname="model_pointer.txt")

    shutil.copyfile(manifest_path, manifest_destination)

    hook_results: dict[str, Any] = {}
    for name in deployment_registry.names():
        item = deployment_registry.get(name)
        if item is None:
            continue
        hook = item.obj
        if callable(hook):
            try:
                hook_results[name] = hook(output)
            except (
                ValueError,
                TypeError,
                RuntimeError,
            ) as exc:  # pragma: no cover - plugin specific
                hook_results[name] = f"error: {exc}"

    try:
        shutil.rmtree(staging)
    except (ValueError, TypeError, RuntimeError):  # pragma: no cover - best effort cleanup
        logger.debug("Suppressed exception in handler", exc_info=True)
    return {
        "run_id": run_id,
        "package": str(output),
        "manifest": str(manifest_destination),
        "hooks": hook_results,
    }


__all__ = ["build_service_package", "deployment_registry"]
