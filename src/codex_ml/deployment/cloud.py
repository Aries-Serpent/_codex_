"""Offline-friendly cloud deployment utilities."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from codex_ml.monitoring.health import record_health_event

__all__ = ["provision_stack"]

_STATUS_DEFERRED = "deferred"
_DEFAULT_PROJECT = "codex-offline"


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _resolve_output_dir(output_dir: str | Path | None) -> Path | None:
    if output_dir is None:
        return None
    return Path(output_dir).expanduser().resolve()


def provision_stack(
    *,
    project: str | None = None,
    output_dir: str | Path | None = None,
    dry_run: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a structured status block describing offline provisioning results."""

    details: Dict[str, Any] = {
        "status": _STATUS_DEFERRED,
        "reason": "Cloud deployment is disabled for offline Codex runs.",
        "project": project or _DEFAULT_PROJECT,
        "dry_run": dry_run,
        "timestamp": _timestamp(),
    }
    resolved_dir = _resolve_output_dir(output_dir)
    if resolved_dir is not None:
        details["output_dir"] = str(resolved_dir)
    if metadata:
        details["metadata"] = metadata

    if dry_run:
        record_health_event(
            "deployment.cloud",
            "dry_run",
            details=details,
        )
        return details

    target_dir = resolved_dir or (Path.cwd() / "deployments" / details["project"])
    sandbox_dir = target_dir / "sandbox"
    manifest_path = target_dir / "manifest.json"

    target_dir.mkdir(parents=True, exist_ok=True)
    sandbox_dir.mkdir(parents=True, exist_ok=True)

    manifest_payload = {
        "project": details["project"],
        "created_at": details["timestamp"],
        "sandbox": str(sandbox_dir),
        "metadata": metadata or {},
    }
    manifest_path.write_text(
        json.dumps(manifest_payload, indent=2, sort_keys=True), encoding="utf-8"
    )

    readme_path = sandbox_dir / "README.txt"
    if not readme_path.exists():
        readme_path.write_text(
            "Offline sandbox created for Codex deployment. Add packaging artefacts here.",
            encoding="utf-8",
        )

    details.update(
        {
            "output_dir": str(target_dir),
            "manifest": str(manifest_path),
            "sandbox_root": str(sandbox_dir),
        }
    )
    record_health_event(
        "deployment.cloud",
        "materialised",
        details=details,
    )
    return details
