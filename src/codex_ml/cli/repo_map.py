"""Repository mapping helpers for the Codex CLI."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Dict, List

try:  # pragma: no cover - optional dependency path
    import yaml  # type: ignore
except Exception:  # pragma: no cover - PyYAML not installed in minimal envs
    yaml = None  # type: ignore

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


def _load_yaml(path: Path) -> Mapping[str, Any] | None:
    if yaml is None:
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except Exception:  # pragma: no cover - best effort parse
        return None
    if isinstance(data, Mapping):
        return data
    return None


def _extract_scalars_from_text(path: Path, keys: Sequence[str]) -> Dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    results: Dict[str, str] = {}
    for key in keys:
        pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+)$", re.MULTILINE)
        match = pattern.search(content)
        if match:
            value = match.group(1).strip().strip("'\"")
            results[key] = value
    return results


def _collect_reasoning_sections(repo_root: Path) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}

    training_cfg = repo_root / "configs" / "training" / "reasoning" / "baseline.yaml"
    if training_cfg.exists():
        data = _load_yaml(training_cfg)
        trace_mode = None
        curriculum = None
        evaluation = None
        metadata_ring = None
        if data:
            trace_mode = (
                data.get("trace_mode")
                or data.get("training", {})
                .get("reasoning", {})
                .get("trace_mode")
            )
            curriculum = (
                data.get("curriculum", {}).get("preset")
                or data.get("curriculum", {}).get("phase_schedule")
            )
            evaluation = data.get("evaluation", {}).get("preset")
            metadata_ring = (
                data.get("metadata", {}).get("rollout_ring")
                or data.get("training", {})
                .get("metadata", {})
                .get("rollout_ring")
            )
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
            sections.setdefault("trace_mode", []).append(f"{rel_path} -> {trace_mode}")
        if curriculum:
            sections.setdefault("curriculum", []).append(f"{rel_path} -> {curriculum}")
        if evaluation:
            sections.setdefault("evaluation", []).append(f"{rel_path} -> {evaluation}")
        if metadata_ring:
            sections.setdefault("rollout_ring", []).append(
                f"{rel_path} -> {metadata_ring}"
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
                deploy_cfg, ["rollout_ring", "CODEX_TRACE_MODE", "CODEX_CURRICULUM_PHASE", "CODEX_EVAL_PRESET"]
            )
            ring = scalars.get("rollout_ring")
            trace = scalars.get("CODEX_TRACE_MODE")
            curriculum_phase = scalars.get("CODEX_CURRICULUM_PHASE")
            eval_preset = scalars.get("CODEX_EVAL_PRESET")

        rel_path = str(deploy_cfg.relative_to(repo_root))
        if ring:
            sections.setdefault("rollout_ring", []).append(f"{rel_path} -> {ring}")
        if trace:
            sections.setdefault("trace_mode", []).append(f"{rel_path} -> {trace}")
        if curriculum_phase:
            sections.setdefault("curriculum", []).append(
                f"{rel_path} -> {curriculum_phase}"
            )
        if eval_preset:
            sections.setdefault("evaluation", []).append(
                f"{rel_path} -> {eval_preset}"
            )

    return sections


def render_repo_map(
    *, reasoning: bool = False, include: Sequence[str] | None = None
) -> str:
    """Render repository metadata with optional reasoning overlays."""

    top_level = _list_top_level(REPO_ROOT)
    extras: Dict[str, List[str]] = {"key_files": _list_key_files(REPO_ROOT)}

    if reasoning:
        extras.update(_collect_reasoning_sections(REPO_ROOT))

    sections: List[tuple[str, List[str]]] = []
    if include:
        for key in include:
            if key == "top_level":
                sections.append(("top_level", top_level))
            elif key in extras:
                sections.append((key, extras[key]))
    else:
        sections.append(("top_level", top_level))
        if reasoning:
            if extras.get("key_files"):
                sections.append(("key_files", extras["key_files"]))
            for key, values in extras.items():
                if key == "key_files":
                    continue
                if values:
                    sections.append((key, values))

    if not sections:
        return ""

    lines: List[str] = []
    first = True
    for key, values in sections:
        if not values:
            continue
        if first and key == "top_level" and not include and not reasoning:
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
