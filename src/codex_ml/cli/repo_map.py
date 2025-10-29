"""Utilities for rendering repository maps for the Codex CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _json_sanitize(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, Mapping):
        return {str(k): _json_sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_json_sanitize(v) for v in obj]
    return obj


def _load_reasoning_baseline() -> Dict[str, Any]:
    cfg_path = _repo_root() / "configs" / "training" / "reasoning" / "baseline.yaml"
    if not cfg_path.exists():
        return {}
    with cfg_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _list_repo_entries(root: Path) -> Iterable[str]:
    for item in sorted(root.iterdir()):
        name = item.name
        if name.startswith("."):
            continue
        suffix = "/" if item.is_dir() else ""
        prefix = "[dir] " if item.is_dir() else " "
        yield f"{prefix}{name}{suffix}"


def _extract_control_surface(cfg: Mapping[str, Any]) -> Dict[str, Any]:
    control: Dict[str, Any] = {}

    trace_mode = cfg.get("trace_mode")
    training_section = cfg.get("training") if isinstance(cfg.get("training"), Mapping) else {}
    if not trace_mode and isinstance(training_section, Mapping):
        reasoning_section = training_section.get("reasoning")
        if isinstance(reasoning_section, Mapping):
            trace_mode = reasoning_section.get("trace_mode")
    if trace_mode:
        control["trace_mode"] = trace_mode

    curriculum_cfg = cfg.get("curriculum")
    if isinstance(curriculum_cfg, Mapping):
        preset = curriculum_cfg.get("preset") or curriculum_cfg.get("phase_schedule")
        if preset:
            control["curriculum.preset"] = preset

    evaluation_cfg = cfg.get("evaluation")
    if not isinstance(evaluation_cfg, Mapping) and isinstance(training_section, Mapping):
        evaluation_cfg = training_section.get("evaluation")
    if isinstance(evaluation_cfg, Mapping):
        preset = evaluation_cfg.get("preset")
        if preset:
            control["evaluation.preset"] = preset

    deployment_cfg = cfg.get("deployment")
    if isinstance(deployment_cfg, Mapping):
        preset = deployment_cfg.get("preset")
        if preset:
            control["deployment.preset"] = preset

    metadata_cfg = cfg.get("metadata")
    if isinstance(metadata_cfg, Mapping):
        ring = metadata_cfg.get("rollout_ring")
        if ring:
            control["metadata.rollout_ring"] = ring
        owner = metadata_cfg.get("owner")
        if owner:
            control["metadata.owner"] = owner

    return control


def render_repo_map(*, reasoning: bool = False) -> str:
    root = _repo_root()
    base_entries = list(_list_repo_entries(root))
    if not reasoning:
        return "\n".join(base_entries)

    cfg = _load_reasoning_baseline()
    control_surface = _extract_control_surface(cfg) if cfg else {}

    lines: list[str] = []
    lines.extend(base_entries)
    lines.append("")
    lines.append("reasoning_status:")
    if not control_surface:
        lines.append("  <no reasoning control surface detected>")
    else:
        for key, value in control_surface.items():
            value_str = _json_sanitize(value)
            lines.append(f"  {key}: {value_str}")

    return "\n".join(lines)
