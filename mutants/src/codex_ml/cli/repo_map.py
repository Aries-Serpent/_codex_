"""
Repo Map Module

This module provides functionality for repo map.

Usage:
    from cli.repo_map import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import ModuleType
from typing import Any, Optional

yaml: ModuleType | None
try:  # pragma: no cover - optional dependency path
    import yaml as _yaml_module

    yaml = _yaml_module
except (IOError, OSError):  # pragma: no cover - PyYAML not installed in minimal envs
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[3]


def _list_top_level(repo_root: Path) -> list[str]:
    entries: list[str] = []
    for item in sorted(repo_root.iterdir()):
        name = item.name
        if name.startswith("."):
            continue
        if item.is_dir():
            entries.append(f"[dir] {name}/")
        else:
            entries.append(f" {name}")
    return entries


def _list_key_files(repo_root: Path) -> list[str]:
    candidates = ["README.md", "docs/README_ROOT.md", "pyproject.toml"]
    results: list[str] = []
    for relative in candidates:
        path = repo_root / relative
        if path.exists():
            results.append(relative)
    return results


def _load_yaml(path: Path) -> Optional[Mapping[str, Any]]:
    if yaml is None:
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (IOError, OSError):  # pragma: no cover - best effort parse
        return None
    if isinstance(data, Mapping):
        return data
    return None


def _extract_scalars_from_text(path: Path, keys: Sequence[str]) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        type(e).__name__
        logger.debug("OSError: <ERROR_TYPE>")
        logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
        return {}
    results: dict[str, str] = {}
    for key in keys:
        pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+)$", re.MULTILINE)
        match = pattern.search(content)
        if match:
            value = match.group(1).strip().strip("'\"")
            results[key] = value
    return results


def _collect_reasoning_sections(
    repo_root: Path,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Collect reasoning control-surface entries.

    Returns a tuple of ``(summary, sections)`` where ``summary`` maps dotted
    control-surface keys (``trace_mode``, ``curriculum.preset`` and friends) to
    repository sources, while ``sections`` retains the category groupings used by
    ``--include`` filters.
    """

    summary: dict[str, list[str]] = {}
    sections: dict[str, list[str]] = {}

    def _add_entry(
        *,
        section_key: str,
        summary_key: Optional[str],
        rel_path: str,
        value: str,
    ) -> None:
        sections.setdefault(section_key, []).append(f"{rel_path} -> {value}")
        if summary_key:
            summary.setdefault(summary_key, []).append(f"{rel_path} -> {value}")

    training_cfg = repo_root / "configs" / "training" / "reasoning" / "baseline.yaml"
    if training_cfg.exists():
        data = _load_yaml(training_cfg)
        trace_mode = None
        curriculum = None
        evaluation = None
        metadata_ring = None
        if data:
            trace_mode = data.get("trace_mode") or data.get("training", {}).get(
                "reasoning", {}
            ).get("trace_mode")
            curriculum = data.get("curriculum", {}).get("preset") or data.get("curriculum", {}).get(
                "phase_schedule"
            )
            evaluation = data.get("evaluation", {}).get("preset")
            metadata_ring = data.get("metadata", {}).get("rollout_ring") or data.get(
                "training", {}
            ).get("metadata", {}).get("rollout_ring")
        else:
            extracted = _extract_scalars_from_text(
                training_cfg, ["trace_mode", "rollout_ring", "preset"]
            )
            trace_mode = extracted.get("trace_mode")
            metadata_ring = extracted.get("rollout_ring")
            # `preset` may appear multiple times; assume first occurrence is curriculum.
            preset_value = extracted.get("preset")
            if preset_value:
                curriculum = preset_value

        rel_path = str(training_cfg.relative_to(repo_root))
        if trace_mode:
            _add_entry(
                section_key="trace_mode",
                summary_key="trace_mode",
                rel_path=rel_path,
                value=str(trace_mode),
            )
        if curriculum:
            _add_entry(
                section_key="curriculum",
                summary_key="curriculum.preset",
                rel_path=rel_path,
                value=str(curriculum),
            )
        if evaluation:
            _add_entry(
                section_key="evaluation",
                summary_key="evaluation.preset",
                rel_path=rel_path,
                value=str(evaluation),
            )
        if metadata_ring:
            _add_entry(
                section_key="rollout_ring",
                summary_key="metadata.rollout_ring",
                rel_path=rel_path,
                value=str(metadata_ring),
            )

    deploy_cfg = repo_root / "configs" / "deploy" / "reasoning_pod.yaml"
    if deploy_cfg.exists():
        data = _load_yaml(deploy_cfg)
        ring = None
        trace = None
        curriculum_phase = None
        eval_preset = None
        if data:
            ring = data.get("rollout_ring")
            env = data.get("pod", {}).get("env", [])
            if isinstance(env, list):
                for entry in env:
                    if not isinstance(entry, Mapping):
                        continue
                    name = entry.get("name")
                    value = entry.get("value")
                    if name == "CODEX_TRACE_MODE":
                        trace = value
                    elif name == "CODEX_CURRICULUM_PHASE":
                        curriculum_phase = value
                    elif name == "CODEX_EVAL_PRESET":
                        eval_preset = value
        else:
            scalars = _extract_scalars_from_text(
                deploy_cfg,
                [
                    "rollout_ring",
                    "CODEX_TRACE_MODE",
                    "CODEX_CURRICULUM_PHASE",
                    "CODEX_EVAL_PRESET",
                ],
            )
            ring = scalars.get("rollout_ring")
            trace = scalars.get("CODEX_TRACE_MODE")
            curriculum_phase = scalars.get("CODEX_CURRICULUM_PHASE")
            eval_preset = scalars.get("CODEX_EVAL_PRESET")

        rel_path = str(deploy_cfg.relative_to(repo_root))
        if ring:
            _add_entry(
                section_key="rollout_ring",
                summary_key="deployment.rollout_ring",
                rel_path=rel_path,
                value=str(ring),
            )
        if trace:
            _add_entry(
                section_key="trace_mode",
                summary_key="trace_mode",
                rel_path=rel_path,
                value=str(trace),
            )
        if curriculum_phase:
            _add_entry(
                section_key="curriculum",
                summary_key="curriculum.phase",
                rel_path=rel_path,
                value=str(curriculum_phase),
            )
        if eval_preset:
            _add_entry(
                section_key="evaluation",
                summary_key="evaluation.preset",
                rel_path=rel_path,
                value=str(eval_preset),
            )

    return summary, sections


def _format_reasoning_summary(summary: Mapping[str, Sequence[str]]) -> list[str]:
    """Format the reasoning summary block for display."""

    ordered_keys = [
        "trace_mode",
        "curriculum.preset",
        "curriculum.phase",
        "evaluation.preset",
        "metadata.rollout_ring",
        "deployment.rollout_ring",
    ]
    lines: list[str] = []

    def _append_block(key: str) -> None:
        values = summary.get(key)
        if not values:
            return
        if not lines:
            lines.append("reasoning_status:")
        lines.append(f"  {key}:")
        for entry in values:
            lines.append(f"    - {entry}")

    for ordered_key in ordered_keys:
        _append_block(ordered_key)

    for key in summary:
        if key in ordered_keys:
            continue
        _append_block(key)

    return lines


def render_repo_map(*, reasoning: bool = False, include: Optional[Sequence[str]] = None) -> str:
    """Render repository metadata with optional reasoning overlays."""

    top_level = _list_top_level(REPO_ROOT)
    extras: dict[str, list[str]] = {"key_files": _list_key_files(REPO_ROOT)}
    reasoning_status_block: list[str] = []

    if reasoning:
        summary, reasoning_sections = _collect_reasoning_sections(REPO_ROOT)
        extras.update(reasoning_sections)
        reasoning_status_block = _format_reasoning_summary(summary)

    sections: list[tuple[str, list[str]]] = []
    if include:
        for key in include:
            if key == "top_level":
                sections.append(("top_level", top_level))
            elif key == "reasoning_status" and reasoning_status_block:
                sections.append(("reasoning_status", reasoning_status_block))
            elif key in extras:
                sections.append((key, extras[key]))
    else:
        sections.append(("top_level", top_level))
        if reasoning:
            if reasoning_status_block:
                sections.append(("reasoning_status", reasoning_status_block))
            if extras.get("key_files"):
                sections.append(("key_files", extras["key_files"]))
            for key, values in extras.items():
                if key == "key_files":
                    continue
                if values:
                    sections.append((key, values))

    if not sections:
        return ""

    lines: list[str] = []
    first = True
    for key, values in sections:
        if not values:
            continue
        if first and key == "top_level" and not include and not reasoning:
            lines.extend(values)
        elif key == "reasoning_status":
            if not first:
                lines.append("")
            lines.extend(values)
        else:
            if not first:
                lines.append("")
            title = key.replace("_", " ").title()
            lines.append(f"# {title}")
            for entry in values:
                lines.append(entry)
        first = False

    return "\n".join(lines)


__all__ = ["render_repo_map"]
