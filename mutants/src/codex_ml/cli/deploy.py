"""Dry-run deployment validation for reasoning pods."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def _load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _load_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_deploy_dry_run(
    *, config_path: Path, dry_run: bool, run_metadata_dir: Path
) -> dict[str, Any]:
    """Validate rollout ring compatibility without touching live infrastructure."""

    if not dry_run:
        raise RuntimeError(
            "Only --dry-run deployments are permitted for reasoning pods in this ring."
        )

    deploy_cfg = _load_yaml_file(config_path)

    pod_section = deploy_cfg.get("pod", {}) if isinstance(deploy_cfg, dict) else {}
    pod_ring = None
    if isinstance(pod_section, dict):
        pod_ring = pod_section.get("ring") or pod_section.get("rollout_ring")
    if not pod_ring:
        pod_ring = deploy_cfg.get("rollout_ring") if isinstance(deploy_cfg, dict) else None

    if not pod_ring:
        raise RuntimeError(
            "Deployment config missing rollout_ring. Declare pod.rollout_ring or rollout_ring."
        )

    run_meta_path = run_metadata_dir / "run_metadata.json"
    if not run_meta_path.exists():
        raise RuntimeError(
            f"run_metadata.json not found in {run_metadata_dir}. Run training before deploy."
        )

    run_metadata = _load_json_file(run_meta_path)
    rollout_ring = None
    if isinstance(run_metadata, dict):
        rollout_ring = run_metadata.get("rollout_ring") or run_metadata.get("metadata", {}).get(
            "rollout_ring"
        )
        if rollout_ring is None:
            control = run_metadata.get("control_surface")
            if isinstance(control, dict):
                rollout_ring = control.get("rollout_ring")

    if not rollout_ring:
        raise RuntimeError(
            "Training metadata missing rollout_ring. Set metadata.rollout_ring in the config."
        )

    if pod_ring and rollout_ring != pod_ring:
        raise RuntimeError(f"rollout ring mismatch: training={rollout_ring} deploy={pod_ring}")

    summary: dict[str, Any] = {
        "status": "validated",
        "dry_run_only": True,
        "rollout_ring": rollout_ring,
        "pod_ring": pod_ring,
        "config": str(config_path),
    }

    if isinstance(deploy_cfg, dict):
        if "image" in deploy_cfg:
            summary["image"] = deploy_cfg["image"]
        if "resources" in deploy_cfg:
            summary["resources"] = deploy_cfg["resources"]
        if isinstance(pod_section, dict):
            for key in ("image", "resources"):
                if key in pod_section:
                    summary[key] = pod_section[key]

    summary["notes"] = "Offline dry-run only; no infrastructure changes were made."
    return summary
